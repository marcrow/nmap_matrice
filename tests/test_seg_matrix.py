from pathlib import Path

import pytest

from seg_matrix.analysis import analyze, build_matrix, restrict
from seg_matrix.inventory import load_inventory
from seg_matrix.nmap import HostRecord, discover_scans, parse_scan
from seg_matrix.port_groups import load_port_groups
from seg_matrix.ports import in_port_set
from seg_matrix.render.html import write_html
from seg_matrix.verdict import ALIVE, BLOCK, NODATA, OPEN, REACH, classify

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
    assert doc.count("</script>") == 2 and '<li class="warn">bogus_scan</li>' in doc
    assert 'value="Z_prod" onchange="refilter(this)"' in doc  # zone filter, per-source tab


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
