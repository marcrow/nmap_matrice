"""Self-check : python3 test_seg_matrix.py"""
import os
import tempfile

from seg_matrix import (ALIVE, BLOCK, NODATA, REACH, aggregate_zones, build_matrix, classify,
                        load_inventory, target_exposure, write_html)

assert classify({"state": "up", "ports": [], "ignored": []}, pn=False).verdict == ALIVE
assert classify({"state": "up", "ports": [], "ignored": []}, pn=True).verdict == NODATA
assert classify({"state": "up", "ports": [(22, "tcp", "closed")], "ignored": []}, pn=False).verdict == REACH
assert classify({"state": "down", "ports": [], "ignored": []}, pn=False).verdict == BLOCK
assert classify({"state": "up", "ports": [(161, "udp", "open|filtered")], "ignored": []}, pn=True).verdict == BLOCK

with tempfile.TemporaryDirectory() as d:
    inv_path = os.path.join(d, "inv.csv")
    open(inv_path, "w").write("10.0.0.1;prod;vm;app\n10.9.0.1;T0;vm;app\n10.0.0.2;prod;vm;\n")
    inv = load_inventory(inv_path)
    # scan launched from the secondary interface: the primary interface is Self
    scan = os.path.join(d, "10.9.0.1.gnmap")
    open(scan, "w").write("Host: 10.0.0.1 ()\tPorts: 22/open/tcp//ssh///\n"
                          "Host: 10.0.0.2 ()\tPorts: 22/open/tcp//ssh///\n")
    matrix, *_ = build_matrix(inv, {"10.9.0.1": scan})
    assert set(matrix["10.9.0.1"]) == {"10.0.0.2"}, matrix

    # report.html: mermaid bundle inlined without breaking the <script> tag, ignored scan listed
    doc = open(write_html(matrix, inv, aggregate_zones(matrix, inv), target_exposure(matrix, inv),
                          [], [], ["scan_bidon"], d), encoding="utf-8").read()
    assert doc.count("</script>") == 2 and "scan_bidon.*" in doc
    assert 'value="Z_prod" onchange="refilter(this)"' in doc   # zone filter, per-source tab

    open(inv_path, "a").write("10.0.0.2;T0;vm;dup\n")
    try:
        load_inventory(inv_path)
        raise AssertionError("duplicate IP accepted")
    except SystemExit:
        pass
print("ok")
