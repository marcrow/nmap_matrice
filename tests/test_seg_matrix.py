import pytest

from seg_matrix.analysis import aggregate_zones, build_matrix, target_exposure
from seg_matrix.inventory import load_inventory
from seg_matrix.render.html import write_html
from seg_matrix.verdict import ALIVE, BLOCK, NODATA, REACH, classify


def rec(state="up", ports=()):
    return {"state": state, "ports": list(ports), "ignored": []}


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
    matrix, *_ = build_matrix(inv, {"10.9.0.1": str(scan)})
    assert set(matrix["10.9.0.1"]) == {"10.0.0.2"}

    agg, exp = aggregate_zones(matrix, inv), target_exposure(matrix, inv)
    report = write_html(matrix, inv, agg, exp, [], [], ["bogus_scan"], str(tmp_path))
    doc = open(report, encoding="utf-8").read()
    # mermaid bundle inlined without breaking the <script> tag, ignored scan listed
    assert doc.count("</script>") == 2 and "bogus_scan.*" in doc
    assert 'value="Z_prod" onchange="refilter(this)"' in doc  # zone filter, per-source tab


def test_duplicate_ip_is_rejected(inventory_file):
    with inventory_file.open("a") as fh:
        fh.write("10.0.0.2;T0;vm;dup\n")
    with pytest.raises(SystemExit):
        load_inventory(str(inventory_file))
