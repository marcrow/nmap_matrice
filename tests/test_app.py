import io
import re
import shutil
import threading
import urllib.error
import urllib.parse
import urllib.request
import xml.dom.minidom
import zipfile
from pathlib import Path

import pytest

from segowl import kits
from segowl.app import Conflict, Mission, add_user, fingerprint, make_server, save_file
from segowl.inventory import load_inventory
from segowl.policy import load_policy
from segowl.port_groups import load_port_groups

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


# ---------------------------------------------------------------- ticket 04: Scan Profiles and Scans
def test_profile_with_client_data_options_is_refused(mission):
    for opts in ("-sS --exclude 10.0.0.1", "-iL hosts.txt", "-oX out.xml", "--open"):
        with pytest.raises(ValueError, match="refused"):
            mission.save_profiles({"fp": "", "profiles": [{"name": "p", "ports": "22", "options": opts}]})
    assert not mission.file("scan_profiles.csv").exists()


def test_script_targets_skip_every_interface_of_the_source_machine(mission):
    with open(mission.file("inventory.csv"), "a") as fh:
        fh.write("172.31.252.1;admin;laptop;auditor;;\n")  # second Interface of the Source's Machine
    mission.save_profiles(
        {"fp": "", "profiles": [{"name": "mix", "ports": "top:100,@admin,udp:161", "options": "-sS -Pn"}]}
    )
    script = mission.script("172.31.250.1", "mix")
    assert "172.31.252.1" not in script and "\n172.31.250.1\n" not in script and "\n172.31.250.10\n" in script
    # top ports and explicit ports are two Scans (nmap would intersect them), UDP only with the explicit ones
    assert "--top-ports 100 -iL" in script and "-oA scans/172.31.250.1/mix-top100" in script
    assert (
        "-sS -Pn -sU -p" in script and "U:161,623" in script and "-oA scans/172.31.250.1/mix-ports" in script
    )


def test_uploaded_scan_completes_its_profile_and_feeds_the_report(mission, tmp_path):
    mission.save_profiles({"fp": "", "profiles": [{"name": "late", "ports": "22", "options": "-sT -Pn"}]})
    xml = next((MISSION / "scans" / "172.31.250.1").glob("*.xml")).read_bytes()
    mission.add_source("172.31.250.10")
    assert mission.scans()["sources"][1]["files"] == []
    mission.upload("172.31.250.10", "late.xml", io.BytesIO(xml), len(xml))
    src = next(s for s in mission.scans()["sources"] if s["ip"] == "172.31.250.10")
    assert src["files"] == [{"name": "late.xml", "excluded": False}]
    mission.refresh()
    assert "2 source(s)" in mission.lines[0]
    mission.move_scan("172.31.250.10", "late.xml", exclude=True)
    mission.refresh()
    assert "1 source(s)" in mission.lines[0]
    with pytest.raises(ValueError):
        mission.upload("../etc", "x.xml", io.BytesIO(b""), 0)


# ---------------------------------------------------------------- ticket 05: Flow Policy editor
def test_rule_on_an_unknown_zone_is_flagged_and_not_saved(mission):
    d = mission.policy()
    bad = {"src": "nowhere", "dst": "dmz", "ports": "@nope", "action": "allow", "comment": ""}
    rules = d["rules"] + [bad]
    r = mission.save_policy({"fp": d["fp"], "rules": rules})
    assert r["errors"][:2] == ["", ""]
    assert "nowhere" in r["errors"][2] and "neither a Zone nor a Machine" in r["errors"][2]
    assert mission.text("flow_policy.csv").count("\n") == 4  # unchanged


def test_bootstrap_from_observed_flows_then_save_loads_in_the_cli(mission):
    d = mission.policy()
    assert d["observed"]["audit;dmz"]  # the fixture Source sees open ports in dmz
    drafts = [  # what the editor's bootstrap adds: one undecided rule per observed Zone pair
        {"src": k.split(";")[0], "dst": k.split(";")[1], "ports": v, "action": "", "comment": "observed"}
        for k, v in d["observed"].items()
    ]
    r = mission.save_policy({"fp": d["fp"], "rules": d["rules"] + drafts})
    assert not any(r["errors"])
    assert "# keep me" in mission.text("flow_policy.csv")
    inv = load_inventory(str(mission.file("inventory.csv")))
    rules = load_policy(str(mission.file("flow_policy.csv")), inv, load_port_groups(None))
    assert len(rules) == 2  # undecided drafts are skipped by the CLI, not refused
    mission.refresh()
    assert not mission.error


def test_observed_flows_survive_a_policy_the_cli_refuses(mission):
    mission.file("flow_policy.csv").write_text("src;dst;ports;action;comment\nghost;dmz;22;allow;\n")
    d = mission.policy()
    assert d["errors"] == ["'ghost' is neither a Zone nor a Machine of the inventory"]
    assert d["observed"]["audit;data"] == "5432"


def test_policy_page_loads_with_a_broken_inventory_and_mixed_case_actions(mission):
    mission.file("flow_policy.csv").write_text("src;dst;ports;action;comment\ndmz;data;5432;DENY;\n")
    assert mission.policy()["rules"][0]["action"] == "deny"
    mission.file("inventory.csv").write_text("ip;zone;type;name\nnot-an-ip;dmz;vm;x\n")
    d = mission.policy()
    assert d["observed"] == {} and d["errors"][0]


# ---------------------------------------------------------------- ticket 06: Auditor Kits
def test_saved_kit_holds_only_the_three_config_files(mission, tmp_path):
    mission.file("scan_profiles.csv").write_text("name;ports;options\nquick;@admin;-sT -Pn\n")
    mission.file("port_labels.csv").write_text("port;product;tags\n9392;Veeam console;backup\n")
    kit_dir = tmp_path / "my-kits"
    kits.save_kit(mission.path, [kit_dir], kit_dir, "acme")
    assert sorted(p.name for p in (kit_dir / "acme").iterdir()) == ["port_labels.csv", "scan_profiles.csv"]


def test_shipped_kits_cannot_be_overwritten(mission, tmp_path):
    shipped = kits.list_kits([])
    assert shipped and all(k["shipped"] for k in shipped)
    for write in (
        lambda: kits.save_kit(mission.path, [kits.SHIPPED], kits.SHIPPED, shipped[0]["name"], overwrite=True),
        lambda: kits.import_zip(kits.export_zip(kits.SHIPPED / shipped[0]["name"]), [], kits.SHIPPED, "x"),
    ):
        with pytest.raises(ValueError, match="read-only"):
            write()


def test_applying_a_kit_then_exporting_it_round_trips(mission, tmp_path):
    src = tmp_path / "kits" / "src"
    src.mkdir(parents=True)
    (src / "scan_profiles.csv").write_bytes(b"name;ports;options\r\nweb;@web,udp:161;-sT -Pn\r\n")
    (src / "port_groups.csv").write_bytes("group;ports\nweb;80,443,8443\n# é\n".encode())
    dirs = [tmp_path / "kits"]
    preview = kits.apply_kit(mission.path, dirs, dirs[0], "src", dry=True)
    assert preview["diff"]["scan_profiles.csv"]["added"] == [["web", "@web,udp:161;-sT -Pn"]]
    assert not mission.file("scan_profiles.csv").exists()  # a preview writes nothing
    kits.apply_kit(mission.path, dirs, dirs[0], "src")
    kits.save_kit(mission.path, dirs, dirs[0], "again")
    with zipfile.ZipFile(io.BytesIO(kits.export_zip(dirs[0] / "again"))) as zf:
        assert {n: zf.read(n) for n in zf.namelist()} == {p.name: p.read_bytes() for p in src.iterdir()}


def test_kits_never_land_in_the_shipped_folder_or_a_mission(mission, tmp_path):
    segowl_dir = kits.SHIPPED.parent
    nested = kits.SHIPPED / "segmentation"
    for dirs, kit_dir, name in (([segowl_dir], segowl_dir, "kits"), ([nested], nested, "x")):
        with pytest.raises(ValueError, match="read-only"):
            kits.save_kit(mission.path, dirs, kit_dir, name, overwrite=True)
    with pytest.raises(ValueError, match="Mission"):
        kits.save_kit(mission.path, [tmp_path], tmp_path, "mission", overwrite=True)
    with pytest.raises(ValueError, match="no kit"):
        kits.export_zip(kits.kit_path([tmp_path], tmp_path, "nothing", write=False))


def test_apply_refuses_what_changed_since_the_preview(mission):
    shipped = kits.list_kits([])[0]
    ref = {"dir": shipped["dir"], "name": shipped["name"]}
    preview = mission.kit_action("preview", ref)
    assert preview["diff"]["scan_profiles.csv"]["status"] == "new"
    mission.file("port_groups.csv").write_text("group;ports\nweb;80\n")  # edited meanwhile
    with pytest.raises(Conflict):
        mission.kit_action("apply", {**ref, "fp": preview["fp"], "files": ["scan_profiles.csv"]})
    again = mission.kit_action("preview", ref)
    mission.kit_action("apply", {**ref, "fp": again["fp"], "files": ["scan_profiles.csv"]})
    assert mission.text("port_groups.csv") == "group;ports\nweb;80\n"  # not in the shipped kit: kept
    assert mission.text("scan_profiles.csv")


def test_apply_takes_only_the_chosen_kit_files_and_keeps_the_others(mission, tmp_path):
    kit = tmp_path / "kits" / "k"
    kit.mkdir(parents=True)
    (kit / "port_groups.csv").write_text("group;ports\nweb;80,443\nmgmt;22\n")
    (kit / "scan_profiles.csv").write_text("name;ports;options\nweb;@web;-sT -Pn\n")
    mine_groups = "group;ports\nweb;80\nlegacy;23\n"
    mission.file("port_groups.csv").write_text(mine_groups)
    mission.file("port_labels.csv").write_text("port;product;tags\n1;x;y\n")  # not in the kit
    dirs = [tmp_path / "kits"]
    preview = kits.apply_kit(mission.path, dirs, dirs[0], "k", dry=True)
    assert preview["diff"]["port_groups.csv"] == {
        "status": "changed",
        "added": [["mgmt", "22"]],
        "removed": [["legacy", "23"]],
        "changed": [["web", "80", "80,443"]],
    }
    assert preview["diff"]["port_labels.csv"] == {"status": "absent"}
    kits.apply_kit(mission.path, dirs, dirs[0], "k", files=["scan_profiles.csv"])
    assert mission.text("scan_profiles.csv") == (kit / "scan_profiles.csv").read_text()
    assert mission.text("port_groups.csv") == mine_groups  # not chosen
    assert mission.text("port_labels.csv") == "port;product;tags\n1;x;y\n"  # not in the kit


def test_kit_profiles_are_checked_against_the_groups_the_mission_will_have(mission, tmp_path):
    kit = tmp_path / "kits" / "k"
    kit.mkdir(parents=True)
    (kit / "scan_profiles.csv").write_text("name;ports;options\nops;@ops;-sT -Pn\n")
    (kit / "port_groups.csv").write_text("group;ports\nother;80\n")
    dirs = [tmp_path / "kits"]
    mission.file("port_groups.csv").write_text("group;ports\nops;22\n")  # @ops only exists in the Mission
    only_profiles = kits.apply_kit(mission.path, dirs, dirs[0], "k", files=["scan_profiles.csv"], dry=True)
    assert only_profiles["errors"] == []
    both = kits.apply_kit(mission.path, dirs, dirs[0], "k", dry=True)  # the kit's groups would drop @ops
    assert "unknown Port Group" in both["errors"][0]
    with pytest.raises(ValueError, match="unknown Port Group"):
        kits.apply_kit(mission.path, dirs, dirs[0], "k")
    assert mission.text("port_groups.csv") == "group;ports\nops;22\n"


def test_shipped_port_labels_are_valid_and_searchable(tmp_path):
    from segowl import scan_profiles as sp
    from segowl.ports import parse_port_set

    header = (sp.DEFAULTS / "port_labels.csv").read_text(encoding="utf-8")
    vocab = set(re.findall(r"^#   (\S+) ", header.split("# Tags")[1], re.M))
    labels = sp.load_labels()
    assert len(labels) > 400 and "risky" in vocab
    for port, product, tags, _vendor, clear in labels:
        parse_port_set(port)  # raises on a bad token
        assert product and set(tags.split(",")) <= vocab, (port, product, tags)
        assert clear in ("yes", "no", ""), (port, product, clear)
    assert len({(p, prod) for p, prod, *_ in labels}) == len(labels), "duplicate port+product"

    old = tmp_path / "port_labels.csv"  # a 3-column Mission file still loads, and adds to the shipped rows
    old.write_text("port;product;tags\n9392;Veeam console;backup\n")
    mine = sp.load_labels(old)
    assert mine[-1] == ("9392", "Veeam console", "backup", "", "")

    hits = sp.search_ports("cleartext", {}, labels)
    assert hits[0]["src"] == "tag" and "23" in hits[0]["many"] and "22" not in hits[0]["many"]
    assert any(h["key"] == "445" for h in sp.search_ports("microsoft", {}, labels))


def test_old_urls_redirect_and_every_screen_is_linked_from_every_page(served):
    base, _ = served
    cookie = fetch(base + "/login", {"login": "alice", "password": "s3cret"})[1]["Set-Cookie"].split(";")[0]
    for old, new in {
        "/mission": "/",
        "/profiles": "/kit/profiles",
        "/kits": "/kit/kits",
        "/kit": "/kit/profiles",
    }.items():
        status, headers, _ = fetch(base + old, cookie=cookie)
        assert (status, headers["Location"]) == (303, new), old
    screens = [
        "/",
        "/inventory",
        "/kit/profiles",
        "/kit/groups",
        "/kit/labels",
        "/kit/kits",
        "/scans",
        "/policy",
        "/report",
    ]
    for url in screens:
        status, _, body = fetch(base + url, cookie=cookie)
        assert status == 200, url
        assert all(f'href="{s}"' in body for s in screens), url


def test_kit_tab_says_which_known_kit_the_mission_copies(mission, tmp_path):
    mission = Mission(mission.path, tmp_path / "cfg")
    assert mission.kit_match() == "no kit file: shipped defaults"
    shutil.copy(kits.SHIPPED / "segmentation" / "scan_profiles.csv", mission.path)
    assert mission.kit_match() == "same as kit segmentation"
    (mission.path / "port_groups.csv").write_text("group;ports\nops;22\n")
    assert mission.kit_match() == "Scan Profiles same as kit segmentation"
    mine = tmp_path / "kits" / "k"  # holds a port_groups.csv the Mission lacks: not the same
    mine.mkdir(parents=True)
    (mine / "scan_profiles.csv").write_text("name;ports;options\nquick;22;\n")
    (mine / "port_groups.csv").write_text("group;ports\nops;23\n")
    kits.write_dirs(tmp_path / "cfg", [str(mine.parent)])
    (mission.path / "port_groups.csv").unlink()
    (mission.path / "scan_profiles.csv").write_text("name;ports;options\nquick;22;\n")
    assert mission.kit_match() == "Scan Profiles same as kit k"
    with open(mission.path / "scan_profiles.csv", "a") as f:
        f.write("extra;22;\n")
    assert mission.kit_match() == "matches no known kit"


def test_mission_group_replaces_the_shipped_one_until_reset(mission):
    g = mission.port_groups()
    assert "22" in g["shipped"]["admin"] and g["mission"] == {}
    mission.save_groups({"fp": g["fp"]["port_groups.csv"], "groups": [{"name": "admin", "ports": "2222"}]})
    assert mission.preview({"ports": "@admin"})["commands"][0]["cmd"].count("-p T:2222")
    load_port_groups(str(mission.path / "port_groups.csv"))  # the CLI reads it
    fp = mission.port_groups()["fp"]["port_groups.csv"]
    mission.save_groups({"fp": fp, "groups": []})  # Reset to shipped
    assert "-p T:2222" not in mission.preview({"ports": "@admin"})["commands"][0]["cmd"]


def test_group_files_never_hold_a_group_reference(mission):
    fp = mission.port_groups()["fp"]["port_groups.csv"]
    with pytest.raises(ValueError, match="@web"):
        mission.save_groups({"fp": fp, "groups": [{"name": "mine", "ports": "22,@web"}]})


def test_renaming_a_group_rewrites_rules_and_profiles(mission):
    (mission.path / "port_groups.csv").write_text("group;ports\nops;22,8443\n")
    (mission.path / "scan_profiles.csv").write_text("name;ports;options\nq;@ops,@web;-Pn\nr;443;\n")
    (mission.path / "flow_policy.csv").write_text("src;dst;ports;action;comment\n*;app-01;@ops,80;allow;x\n")
    g = mission.port_groups()
    assert g["used"]["ops"] == {"rules": ["* → app-01  @ops,80  allow"], "profiles": ["q"]}
    with pytest.raises(ValueError, match="shipped"):
        mission.rename_group("web", "www", g["fp"])
    out = mission.rename_group("ops", "mgmt", g["fp"])
    assert "1 Flow Policy rule(s) and 1 Scan Profile(s)" in out["message"]
    assert mission.text("flow_policy.csv") == "src;dst;ports;action;comment\n*;app-01;@mgmt,80;allow;x\n"
    assert mission.text("scan_profiles.csv") == "name;ports;options\nq;@mgmt,@web;-Pn\nr;443;\n"
    groups = load_port_groups(str(mission.path / "port_groups.csv"))
    load_policy(
        str(mission.path / "flow_policy.csv"), load_inventory(str(mission.path / "inventory.csv")), groups
    )
    with pytest.raises(ValueError, match=r"@mgmt is used by 1 Flow Policy rule\(s\), Scan Profile q"):
        mission.save_groups({"fp": out["fp"]["port_groups.csv"], "groups": []})


def test_port_search_completes_a_partly_typed_port():
    from segowl import scan_profiles as sp

    labels = sp.load_labels()
    keys = [h["key"] for h in sp.search_ports("338", {}, labels)]
    assert "3389" in keys and keys[0] == "338"  # as typed first, then the ports it starts
    assert "udp:161" in [h["key"] for h in sp.search_ports("udp:16", {}, labels)]
    assert "161" not in [h["key"] for h in sp.search_ports("udp:16", {}, labels)]


def test_a_mission_label_completes_the_shipped_one_instead_of_duplicating_it(mission):
    from segowl import scan_profiles as sp

    shipped = next(r for r in mission.labels()["shipped"] if r[0] == "3389")
    row = [shipped[0], shipped[1], "admin,My Tag", "Microsoft", "no"]
    mission.save_labels({"fp": mission.labels()["fp"], "labels": [row]})
    hits = [h for h in sp.search_ports("3389", {}, sp.load_labels(mission.file("port_labels.csv")))]
    same = [h for h in hits if h["key"] == "3389" and h["label"].startswith(shipped[1])]
    assert len(same) == 1 and same[0]["tags"] == "admin,my-tag"  # tags normalised on save
    with pytest.raises(ValueError, match="already ships: use Complete"):
        mission.add_label(["udp:161", next(r for r in mission.labels()["shipped"] if r[0] == "udp:161")[1]])


def test_two_products_on_one_port_stay_two_labels(mission):
    mission.add_label(["8443", "Acme console", "admin", "", "yes"])
    mission.add_label(["8443", "Other thing", "", "", ""])
    assert [r[1] for r in mission.labels()["mission"]] == ["Acme console", "Other thing"]
    with pytest.raises(ValueError, match="already in this Mission"):
        mission.add_label(["8443", "acme console"])
    with pytest.raises(ValueError, match="port"):
        mission.add_label(["99999", "Nope"])


def test_a_hand_written_three_column_label_file_is_rewritten_without_loss(mission):
    (mission.path / "port_labels.csv").write_text(
        "# my notes\nport;product;tags\n9392;Veeam console;backup\n"
    )
    data = mission.labels()
    assert data["mission"] == [["9392", "Veeam console", "backup", "", ""]]
    mission.save_labels({"fp": data["fp"], "labels": data["mission"]})
    assert mission.text("port_labels.csv") == (
        "port;product;tags;vendor;cleartext\n# my notes\n9392;Veeam console;backup;;\n"
    )


def test_profile_descriptions_are_optional_and_never_invented(mission):
    three = "name;ports;options\nbroad;22;-Pn\nr;443;\n"
    (mission.path / "scan_profiles.csv").write_text(three)
    d = mission.profiles()
    assert [(p["name"], p["description"], p["imported"]) for p in d["profiles"]] == [
        ("broad", "", 1),
        ("r", "", 0),
    ]
    fp = mission.save_profiles({"fp": d["fp"], "profiles": d["profiles"]})
    assert mission.text("scan_profiles.csv") == three  # still 3 columns: nothing typed, nothing added
    d["profiles"][0]["description"] = "First pass; from every Source"
    mission.save_profiles({"fp": fp, "profiles": d["profiles"]})
    assert mission.text("scan_profiles.csv") == (
        'name;ports;options;description\nbroad;22;-Pn;"First pass; from every Source"\nr;443;;\n'
    )
    assert mission.profiles()["profiles"][0]["description"] == "First pass; from every Source"


def test_a_kit_profile_description_shows_in_the_diff(mission, tmp_path):
    kit = tmp_path / "kits" / "k"
    kit.mkdir(parents=True)
    (kit / "scan_profiles.csv").write_text("name;ports;options;description\nq;22;-Pn;quick look\n")
    dirs = [tmp_path / "kits"]
    out = kits.apply_kit(mission.path, dirs, dirs[0], "k", dry=True)
    assert out["diff"]["scan_profiles.csv"]["added"] == [["q", "22;-Pn;quick look"]]


def test_tutorial_diagrams_stand_alone_and_are_served(served):
    files = sorted((Path(__file__).parents[1] / "segowl" / "assets" / "tutorial").glob("*.svg"))
    assert {"zone-view.svg", "source-view.svg", "work-process.svg", "zone-matrix.svg"} <= {
        f.name for f in files
    }
    for f in files:
        svg = f.read_text(encoding="utf-8")
        xml.dom.minidom.parseString(svg)  # well-formed: an <img> shows nothing otherwise
        assert "<script" not in svg and "@import" not in svg and " class=" not in svg, f.name
        assert set(re.findall(r'href="([^"]*)"|url\(([^)]*)\)', svg)) <= {
            ("", u) for u in re.findall(r"url\((#[^)]*)\)", svg)
        }
        assert f.name.startswith("benefit-") or '<rect x="-12" y="-12"' in svg  # own white background
    base, _ = served
    cookie = fetch(base + "/login", {"login": "alice", "password": "s3cret"})[1]["Set-Cookie"].split(";")[0]
    status, headers, body = fetch(base + "/static/tutorial/zone-view.svg", cookie=cookie)
    assert (status, headers["Content-Type"]) == (200, "image/svg+xml") and body.startswith("<svg")
    assert fetch(base + "/static/tutorial/../app.py", cookie=cookie)[0] == 404


def test_an_empty_mission_starts_with_the_inventory(tmp_path):
    from segowl.app import ensure_skeleton

    ensure_skeleton(tmp_path / "m")
    ov = Mission(tmp_path / "m", tmp_path / "cfg").overview()
    assert [s["state"] for s in ov["steps"]] == ["todo"] * 5
    assert ov["next"] == "inventory"


def test_a_broken_input_file_is_the_next_step_with_the_clis_message(served):
    base, path = served
    (path / "flow_policy.csv").write_text("src;dst;ports;action;comment\nnowhere;*;22;deny;x\n")
    ov = Mission(path, path.parent / "cfg").overview()
    pol = next(s for s in ov["steps"] if s["key"] == "policy")
    assert pol["state"] == "warn" and "nowhere" in pol["problem"] and ov["next"] == "policy"
    (path / "inventory.csv").write_text("ip;zone;type;name\n10.0.0.1;a;;\n10.0.0.1;b;;\n")
    ov = Mission(path, path.parent / "cfg").overview()
    inv = ov["steps"][0]
    assert inv["state"] == "warn" and "10.0.0.1" in inv["problem"] and ov["next"] == "inventory"
    cookie = fetch(base + "/login", {"login": "alice", "password": "s3cret"})[1]["Set-Cookie"].split(";")[0]
    status, _, body = fetch(base + "/", cookie=cookie)
    assert status == 200 and "10.0.0.1" in body and "Rigour in the scans" in body


def test_same_as_kit_means_byte_for_byte(mission, tmp_path):
    mission = Mission(mission.path, tmp_path / "cfg")
    shipped = (kits.SHIPPED / "segmentation" / "scan_profiles.csv").read_bytes()
    (mission.path / "scan_profiles.csv").write_bytes(shipped.replace(b"\n", b"\r\n"))
    assert mission.kit_match() == "matches no known kit"
    (mission.path / "scan_profiles.csv").write_bytes(shipped)
    kit = next(s for s in mission.overview()["steps"] if s["key"] == "kit")
    assert "same as kit segmentation" in kit["summary"]
