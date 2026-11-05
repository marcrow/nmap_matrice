import csv
import json
import re
import shutil
from pathlib import Path

import pytest

from segowl.analysis import aggregate_zones, analyze, build_matrix, pivot_machines, rebounds, restrict
from segowl.cli import main
from segowl.inventory import Host, load_inventory
from segowl.nmap import HostRecord, Scan, discover_declared, discover_excluded, discover_scans, parse_scan
from segowl.policy import load_policy
from segowl.port_groups import load_port_groups
from segowl.ports import in_port_set
from segowl.render.common import zone_cell
from segowl.render.exports import write_observed_zone_flows
from segowl.render.html import _nmap_ports, write_html
from segowl.render.mermaid import mermaid_zone, zid
from segowl.verdict import ALIVE, BLOCK, NODATA, OPEN, REACH, Cell, classify

MISSION = Path(__file__).parent / "fixtures" / "mission"
SRC = "172.31.250.1"  # the fixtures' Source (see fixtures/generate.sh)


def rec(state="up", ports=()):
    return HostRecord(state=state, ports=list(ports))


@pytest.mark.parametrize(
    "record, pn, verdict",
    [
        (rec(), False, ALIVE),
        (rec(), True, NODATA),
        (rec(ports=[(22, "tcp", "closed")]), False, REACH),
        (rec(state="down"), False, BLOCK),
        (rec(ports=[(161, "udp", "open|filtered")]), True, BLOCK),  # no reply is not an open port
        (rec(ports=[(22, "tcp", "filtered")]), False, ALIVE),  # answers discovery, every port filtered
        (rec(ports=[(22, "tcp", "filtered")]), True, BLOCK),
        (HostRecord(state="up", ignored=[("unfiltered", 1000)]), True, REACH),  # -sA: the flow passes
    ],
)
def test_classify(record, pn, verdict):
    assert classify(record, pn).verdict == verdict


@pytest.fixture
def inventory_file(tmp_path):
    path = tmp_path / "inv.csv"
    path.write_text("10.0.0.1;prod;vm;app\n10.9.0.1;T0;vm;app\n10.0.0.2;prod;vm;\n")
    return path


def test_self_is_excluded_and_report_renders(tmp_path, inventory_file):
    inv = load_inventory(str(inventory_file))
    # scan launched from the secondary interface: the primary interface is Self
    scan = tmp_path / "10.9.0.1.gnmap"
    scan.write_text(
        "Host: 10.0.0.1 ()\tPorts: 22/open/tcp//ssh///\nHost: 10.0.0.2 ()\tPorts: 22/open/tcp//ssh///\n"
    )
    a = analyze(inv, {"10.9.0.1": [parse_scan(str(scan), "10.9.0.1")]}, ["bogus_scan"])
    assert set(a.matrix["10.9.0.1"]) == {"10.0.0.2"}

    report = write_html(a, str(tmp_path))
    doc = open(report, encoding="utf-8").read()
    # mermaid bundle inlined without breaking the <script> tag, ignored scan listed
    assert doc.count("<script") == doc.count("</script>") and '<li class="warn">bogus_scan</li>' in doc
    graph = json.loads(
        re.search(r'<div class="graph"><script type="application/json">(.*?)</script>', doc)[1]
    )
    assert graph["center"]["ip"] == "10.9.0.1" and [n["ip"] for n in graph["nodes"]] == ["10.0.0.2"]


def test_duplicate_ip_is_rejected(inventory_file):
    with inventory_file.open("a") as fh:
        fh.write("10.0.0.2;T0;vm;dup\n")
    with pytest.raises(SystemExit):
        load_inventory(str(inventory_file))


def test_discovery_keeps_one_format_per_scan():
    files = discover_scans(str(MISSION / "scans"))
    names = [Path(p).name for p in files[SRC]]
    assert names == ["after_fix.xml", "broad.xml", "targeted.xml", "udp.xml"]  # broad.gnmap shadowed by xml


def test_source_view_merges_scans_and_tracks_coverage():
    inv = load_inventory(str(MISSION / "inventory.csv"))
    scans = {SRC: [parse_scan(p, SRC) for p in discover_scans(str(MISSION / "scans"))[SRC]]}
    app = build_matrix(inv, scans)[0][SRC]["172.31.250.10"]

    assert app.verdict == OPEN
    assert {(6379, "tcp"), (8443, "tcp")} <= set(app.open_ports)  # extra ports from the targeted follow-up
    # 22 open in the broad sweep, closed after the fix: the most permissive wins and the conflict is kept
    assert (22, "tcp") in app.open_ports
    assert app.conflicts[(22, "tcp")] == {f"{SRC}/broad.xml": "open", f"{SRC}/after_fix.xml": "closed"}
    assert app.is_tested(5432) is True
    assert app.is_tested(2000) is False  # never tested, which is not the same as unseen
    assert app.is_tested(161, "udp") is True

    legacy = parse_scan(str(MISSION / "scans" / SRC / "broad.gnmap"), SRC)
    cell = build_matrix(inv, {SRC: [legacy]})[0][SRC]["172.31.250.10"]
    assert cell.is_tested(2000) is None  # gnmap: Coverage unknown, never asserted untested


def test_udp_verdicts():
    inv = load_inventory(str(MISSION / "inventory.csv"))
    udp = parse_scan(str(MISSION / "scans" / SRC / "udp.xml"), SRC)
    row = build_matrix(inv, {SRC: [udp]})[0][SRC]
    assert row["172.31.250.10"].open_ports == [(161, "udp")]
    assert row["172.31.250.20"].verdict == REACH  # ICMP port unreachable = closed


def test_inventory_free_columns(tmp_path):
    path = tmp_path / "inv.csv"
    path.write_text("ip;zone;type;name;owner;;\n10.0.0.1;prod;vm;app;alice;;\n")
    assert load_inventory(str(path))["10.0.0.1"].extra == {"owner": "alice"}
    path.write_text("10.0.0.1;prod;vm;app;alice\n")
    with pytest.raises(SystemExit, match="no header"):
        load_inventory(str(path))


def test_port_groups_override_and_filter(tmp_path):
    override = tmp_path / "port_groups.csv"
    override.write_text("group;ports\nadmin;22,udp:161\n")
    groups = load_port_groups(str(override))
    assert groups["admin"] == {"tcp": [(22, 22)], "udp": [(161, 161)]}  # mission file replaces the default
    assert "db" in groups  # other defaults kept

    inv = load_inventory(str(MISSION / "inventory.csv"))
    scans = {SRC: [parse_scan(p, SRC) for p in discover_scans(str(MISSION / "scans"))[SRC]]}
    admin = restrict(build_matrix(inv, scans)[0], lambda p: in_port_set(p, groups["admin"]))
    assert admin[SRC]["172.31.250.10"].open_ports == [(22, "tcp"), (161, "udp")]
    assert admin[SRC]["172.31.250.20"].verdict == NODATA  # 5432 is not an admin port


def test_pivot_machine(tmp_path):
    inv_path = tmp_path / "inv.csv"
    inv_path.write_text(
        "10.0.1.5;dmz;vm;bastion\n10.9.0.5;T0;vm;bastion\n10.1.0.9;user;ws;pc\n10.0.1.6;dmz;vm;web\n"
    )
    inv = load_inventory(str(inv_path))
    scan = tmp_path / "10.1.0.9.gnmap"
    scan.write_text(
        "Host: 10.0.1.5 ()\tPorts: 22/open/tcp//ssh///\nHost: 10.0.1.6 ()\tPorts: 80/open/tcp//http///\n"
    )
    a = analyze(inv, {"10.1.0.9": [parse_scan(str(scan), "10.1.0.9")]}, [])
    assert a.pivots == {"bastion": [("10.1.0.9", "10.0.1.5", [(22, "tcp")])]}  # web spans one zone only


def test_asymmetry_needs_both_directions_tested(tmp_path):
    inv_path = tmp_path / "inv.csv"
    inv_path.write_text("10.0.0.1;user;ws;pc\n10.0.0.2;srv;vm;srv\n10.0.0.3;srv;vm;other\n")
    inv = load_inventory(str(inv_path))
    xml = (
        '<nmaprun args="nmap -Pn -p 22"><scaninfo type="syn" protocol="tcp" services="{ports}"/>'
        '<host><status state="up"/><address addr="{dst}" addrtype="ipv4"/><ports>'
        '<port protocol="tcp" portid="22"><state state="{state}"/></port></ports></host></nmaprun>'
    )
    scans = {}
    for src, dst, state, ports in [
        ("10.0.0.1", "10.0.0.2", "open", "22"),
        ("10.0.0.2", "10.0.0.1", "filtered", "22"),  # reverse blocked, same port tested: asymmetric
        ("10.0.0.3", "10.0.0.1", "filtered", "22"),
    ]:
        path = tmp_path / f"{src}-{dst}.xml"
        path.write_text(xml.format(dst=dst, state=state, ports=ports))
        scans.setdefault(src, []).append(parse_scan(str(path), src))
    a = analyze(inv, scans, [])
    assert a.asymmetries == [("10.0.0.1", "10.0.0.2")]  # 10.0.0.1 never scanned 10.0.0.3: not reported


def test_scan_row_is_one_scan_alone():
    inv = load_inventory(str(MISSION / "inventory.csv"))
    scans = {SRC: [parse_scan(p, SRC) for p in discover_scans(str(MISSION / "scans"))[SRC]]}
    a = analyze(inv, scans, [])
    after_fix = next(sc for sc in a.scans[SRC] if sc.name.endswith("after_fix.xml"))
    row = a.scan_row(after_fix)
    assert set(row) == {"172.31.250.10"}  # the only target of that Scan
    assert row["172.31.250.10"].open_ports == [] and row["172.31.250.10"].is_tested(22)


def _policy_case(tmp_path):
    inv_path = tmp_path / "inv.csv"
    inv_path.write_text("10.1.0.9;user;ws;pc\n10.0.1.6;dmz;vm;web\n10.0.1.7;dmz;vm;dc-01\n")
    inv = load_inventory(str(inv_path))
    scan = tmp_path / "10.1.0.9.gnmap"
    scan.write_text(
        "Host: 10.0.1.6 ()\tPorts: 22/open/tcp//ssh///, 443/open/tcp//https///\n"
        "Host: 10.0.1.7 ()\tPorts: 22/open/tcp//ssh///\n"
    )
    return inv, {"10.1.0.9": [parse_scan(str(scan), "10.1.0.9")]}


def test_flow_policy_precedence(tmp_path):
    inv, scans = _policy_case(tmp_path)
    policy_path = tmp_path / "flow_policy.csv"
    policy_path.write_text(
        "src;dst;ports;action;comment\n"
        "user;dmz;443;allow;web only\n"
        "user;dmz;*;deny;\n"
        "user;dc-01;*;allow;the machine rule beats the zone rule\n"
        "user;dmz;8080;;no decision yet: skipped\n"
    )
    policy = load_policy(str(policy_path), inv, load_port_groups())
    a = analyze(inv, scans, [], policy=policy)
    assert [(s, d, p, r.line) for s, d, p, r in a.findings] == [("10.1.0.9", "10.0.1.6", (22, "tcp"), 3)]
    assert a.flow_status("10.1.0.9", "10.0.1.6", (443, "tcp")) == "allow"
    assert a.flow_status("10.1.0.9", "10.0.1.7", (22, "tcp")) == "allow"
    assert a.undeclared == []


def test_no_policy_no_findings(tmp_path):
    inv, scans = _policy_case(tmp_path)
    a = analyze(inv, scans, [])
    assert a.findings == [] and a.pair_status(a.matrix) == {}


def test_zone_flow_export_bootstraps_a_policy(tmp_path):
    inv, scans = _policy_case(tmp_path)
    exported = write_observed_zone_flows(analyze(inv, scans, []), str(tmp_path))
    rows = list(csv.reader(open(exported, encoding="utf-8-sig"), delimiter=";"))
    assert rows[0] == ["src", "dst", "ports", "action", "comment"]
    assert [r[:3] for r in rows[1:]] == [["user", "dmz", "22"], ["user", "dmz", "443"]]

    for r in rows[1:]:
        r[3] = "deny" if r[2] == "22" else "allow"  # the auditor fills the action column
    policy_path = tmp_path / "flow_policy.csv"
    with open(policy_path, "w", newline="", encoding="utf-8") as fh:
        csv.writer(fh, delimiter=";").writerows(rows)
    a = analyze(inv, scans, [], policy=load_policy(str(policy_path), inv, load_port_groups()))
    assert len(a.findings) == 2  # 22 to web and to dc-01


def test_excluding_a_scan_removes_its_conflict(tmp_path):
    scans_dir = tmp_path / "scans"
    shutil.copytree(MISSION / "scans", scans_dir)
    (scans_dir / SRC / "excluded").mkdir()
    shutil.move(scans_dir / SRC / "after_fix.xml", scans_dir / SRC / "excluded" / "after_fix.xml")

    files = discover_scans(str(scans_dir))
    assert "after_fix.xml" not in [Path(p).name for p in files[SRC]]
    assert [Path(p).name for p in discover_excluded(str(scans_dir))[SRC]] == ["after_fix.xml"]
    inv = load_inventory(str(MISSION / "inventory.csv"))
    a = analyze(inv, {SRC: [parse_scan(p, SRC) for p in files[SRC]]}, [])
    assert a.matrix[SRC]["172.31.250.10"].conflicts == {}


def test_zone_matrix_keeps_alive_and_unseen_apart():
    inv = {ip: Host(ip, z, "vm", "") for ip, z in [("10.0.0.1", "A"), ("10.0.1.1", "B"), ("10.0.2.1", "C")]}
    matrix = {"10.0.0.1": {"10.0.1.1": Cell(ALIVE), "10.0.2.1": Cell()}}
    agg = aggregate_zones(matrix, inv)
    assert zone_cell(agg[("A", "B")])[1].startswith("~")
    assert zone_cell(agg[("A", "C")])[1] == "."
    assert "Z_A" in mermaid_zone(agg, inv).split("flowchart", 1)[1].split("Z_B")[0]  # an edge A -> B


def test_mermaid_ids_do_not_collide():
    assert len({zid("DMZ-1"), zid("DMZ 1"), zid("DMZ_1"), zid("DMZ.1")}) == 4


def test_inventory_rejects_a_non_ip(tmp_path):
    path = tmp_path / "inv.csv"
    path.write_text("<img src=x>;prod;vm;app\n")
    with pytest.raises(SystemExit):
        load_inventory(str(path))


def test_legacy_and_folder_scans_of_a_source_have_distinct_names(tmp_path):
    names = {Scan(str(p), SRC).name for p in (tmp_path / f"{SRC}.xml", tmp_path / SRC / f"{SRC}.xml")}
    assert len(names) == 2


def test_excluded_paths_are_relative_to_the_source_folder(tmp_path):
    for sub in ("archive/old", "excluded"):
        (tmp_path / SRC / sub).mkdir(parents=True)
        (tmp_path / SRC / sub / "a.xml").write_text("")
    assert discover_excluded(str(tmp_path))[SRC] == ["archive/old/a.xml", "excluded/a.xml"]


def test_missing_port_groups_file_is_an_error_with_a_mission(tmp_path, monkeypatch):
    argv = ["segowl", str(MISSION), "-o", str(tmp_path), "--port-groups", str(tmp_path / "typo.csv")]
    monkeypatch.setattr("sys.argv", argv)
    with pytest.raises(SystemExit, match="Port Groups file not found"):
        main()


def test_sources_without_scan_are_the_declared_folders_only(tmp_path):
    """A scans/<ip>/ folder declares a Source: empty, it is a gap; an Interface with no folder is none."""
    scans = tmp_path / "scans"
    shutil.copytree(MISSION / "scans", scans)
    (scans / "172.31.250.20").mkdir()  # declared, no Scan yet
    inv = load_inventory(str(MISSION / "inventory.csv"))
    files = discover_scans(str(scans))
    a = analyze(
        inv, {SRC: [parse_scan(p, SRC) for p in files[SRC]]}, [], declared=discover_declared(str(scans))
    )
    assert a.missing == ["172.31.250.20"]  # 172.31.250.10 and .30: no folder, not listed


def test_nmap_ports_lists_tcp_plainly_and_prefixes_protocols_when_mixed():
    assert _nmap_ports([(443, "tcp"), (22, "tcp"), (22, "tcp")]) == "22,443"
    assert _nmap_ports([(53, "udp"), (22, "tcp"), (161, "udp")]) == "T:22,U:53,161"
    assert _nmap_ports([]) == ""


def test_rebound_gain_bypass_nothing_new_and_partial():
    """From zone A, a Source reaches the Machine m OPEN on its B Interface; m also sits in C, D and E."""
    hosts = [("10.0.0.1", "A", ""), ("10.0.1.9", "B", "m"), ("10.0.2.9", "C", "m"), ("10.0.3.9", "D", "m")]
    hosts += [("10.0.4.9", "E", "m"), ("10.0.2.1", "C", ""), ("10.0.2.2", "C", ""), ("10.0.3.1", "D", "")]
    hosts += [("10.0.4.1", "E", "")]
    inv = {ip: Host(ip, z, "vm", name) for ip, z, name in hosts}
    opened = {"10.0.1.9", "10.0.2.1", "10.0.4.1"}  # m on B, one of C's two, all of E's one
    matrix = {"10.0.0.1": {ip: Cell(OPEN, [(22, "tcp")]) if ip in opened else Cell() for ip in inv}}
    hits = pivot_machines(matrix, inv)["m"]
    by_zone = {r.into: r for r in rebounds(matrix, inv, "m", hits)}
    assert set(by_zone) == {"C", "D", "E"}  # B is where the Source lands: no rebound into it
    assert by_zone["C"].gain["A"] == ["10.0.2.2"] and not by_zone["C"].bypass("A")  # partial: +1 of 2
    assert by_zone["D"].gain["A"] == ["10.0.3.1"] and by_zone["D"].bypass("A")  # adds everything
    assert by_zone["E"].gain["A"] == [] and not by_zone["E"].bypass("A")  # nothing new
