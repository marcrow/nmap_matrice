import shutil
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

from segowl.app import Conflict, add_user, fingerprint, make_server, save_file

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
