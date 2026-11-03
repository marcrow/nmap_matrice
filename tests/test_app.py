import shutil
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

from segowl.app import Conflict, Mission, add_user, fingerprint, make_server, save_file

MISSION = Path(__file__).parent / "fixtures" / "mission"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


@pytest.fixture
def served(tmp_path):
    mission = tmp_path / "mission"
    shutil.copytree(MISSION, mission)
    config = tmp_path / "config"
    add_user(config / "users", "alice", "s3cret")
    server = make_server(str(mission), port=0, config=config)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}", mission
    server.shutdown()


def fetch(url, data=None, cookie=None):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode() if data else None)
    if cookie:
        req.add_header("Cookie", cookie)
    try:
        r = urllib.request.build_opener(NoRedirect).open(req)
    except urllib.error.HTTPError as e:
        r = e
    return r.status, dict(r.headers), r.read().decode()


def test_login_is_required_and_checked(served):
    base, _ = served
    assert fetch(base + "/report")[1]["Location"] == "/login"
    assert fetch(base + "/login", {"login": "alice", "password": "nope"})[0] == 401
    status, headers, _ = fetch(base + "/login", {"login": "alice", "password": "s3cret"})
    cookie = headers["Set-Cookie"].split(";")[0]
    assert status == 303 and "HttpOnly" in headers["Set-Cookie"]
    status, _, body = fetch(base + "/report/report.html", cookie=cookie)
    assert status == 200 and "<html" in body  # the report was generated from the Mission on first request
    assert fetch(base + "/report/../inventory.csv", cookie=cookie)[0] == 404


def test_network_address_needs_a_users_file(tmp_path):
    with pytest.raises(SystemExit, match="without authentication"):
        make_server(str(tmp_path / "m"), host="0.0.0.0", port=0, config=tmp_path / "empty")


def test_save_refuses_a_file_changed_since_load(tmp_path):
    f = tmp_path / "inventory.csv"
    f.write_text("v1")
    loaded = fingerprint(f)
    f.write_text("v2 from another auditor")
    with pytest.raises(Conflict):
        save_file(f, "v3", loaded)
    assert f.read_text() == "v2 from another auditor"
    assert save_file(f, "v3", fingerprint(f)) == fingerprint(f)


# ---------------------------------------------------------------- ticket 03: inventory and Zones


@pytest.fixture
def mission(tmp_path):
    m = tmp_path / "mission"
    shutil.copytree(MISSION, m)
    (m / "flow_policy.csv").write_text(
        "src;dst;ports;action;comment\n# keep me\ndmz;data;5432;deny;db\n*;app-01;*;allow;\n"
    )
    return Mission(m)


def test_zone_and_machine_renames_rewrite_inventory_and_policy(mission):
    before = mission.inventory()
    r = mission.rename("zone", "data", "T1-data", before["fp"])
    r = mission.rename("machine", "app-01", "web-01", r["fp"])
    inv, pol = mission.text("inventory.csv"), mission.text("flow_policy.csv")
    assert "T1-data;container;db-01" in inv and ";data;" not in inv
    assert "dmz;T1-data;5432;deny;db" in pol and "*;web-01;*;allow;" in pol and "# keep me" in pol
    with pytest.raises(Conflict):  # stale fingerprints: nothing is rewritten
        mission.rename("zone", "dmz", "x", before["fp"])
    assert "dmz;" in mission.text("inventory.csv")


def test_saving_without_zones_file_keeps_the_mission_cli_identical(mission):
    d = mission.inventory()
    mission.save_inventory(d)
    assert not mission.file("zones.csv").exists()  # every Zone is used and undescribed
    assert mission.text("inventory.csv") == (MISSION / "inventory.csv").read_text()
    d = mission.inventory()
    mission.save_inventory({**d, "zones": [{"name": "backup", "desc": ""}]})  # an empty Zone needs zones.csv
    assert mission.text("zones.csv") == "zone;description\nbackup;\n"


def test_duplicate_ip_is_refused_on_save(mission):
    d = mission.inventory()
    d["rows"].append(dict(d["rows"][0]))
    with pytest.raises(ValueError, match="Duplicate IP"):
        mission.save_inventory(d)
    assert mission.text("inventory.csv") == (MISSION / "inventory.csv").read_text()


def test_client_zip_round_trip(mission, tmp_path):
    blob = mission.client_zip()
    other = Mission(tmp_path / "other")
    other.path.mkdir()
    assert other.import_client(blob, apply=False) == {
        "report": {"inventory.csv": "5 Interface(s)", "flow_policy.csv": "2 rule(s)"},
        "ok": True,
        "applied": False,
    }
    assert not other.file("inventory.csv").exists()
    assert other.import_client(blob, apply=True)["applied"]
    assert other.text("flow_policy.csv") == mission.text("flow_policy.csv")
