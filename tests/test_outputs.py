"""Generated outputs: snapshots of every text view, and escaping of inventory text in the HTML.

Intended change to a view: `UPDATE_SNAPSHOTS=1 uv run pytest`, then review the snapshot diff.
"""

import os
from pathlib import Path

from segowl.analysis import analyze
from segowl.cli import main
from segowl.inventory import load_inventory
from segowl.nmap import parse_scan
from segowl.render.html import write_html

MISSION = Path(__file__).parent / "fixtures" / "mission"
SNAPSHOTS = Path(__file__).parent / "fixtures" / "snapshots"


def _texts(root: Path) -> dict[Path, str]:
    return {
        p.relative_to(root): p.read_text(encoding="utf-8")
        for p in root.rglob("*")
        if p.is_file() and p.name != "report.html"  # HTML: covered by the escaping test, bundles mermaid
    }


def test_text_views_match_snapshots(tmp_path, monkeypatch, capsys):  # capsys: silences the CLI
    monkeypatch.setattr("sys.argv", ["segowl", str(MISSION), "-o", str(tmp_path)])
    main()
    produced = _texts(tmp_path)
    if os.environ.get("UPDATE_SNAPSHOTS"):
        for rel, text in produced.items():
            (SNAPSHOTS / rel).parent.mkdir(parents=True, exist_ok=True)
            (SNAPSHOTS / rel).write_text(text, encoding="utf-8")
    expected = _texts(SNAPSHOTS)
    assert produced.keys() == expected.keys()
    for rel, text in produced.items():
        assert text == expected[rel], f"{rel} changed (UPDATE_SNAPSHOTS=1 if intended)"


def test_inventory_text_is_escaped_in_the_report(tmp_path):
    bad = "<x>"
    inv_path = tmp_path / "inv.csv"
    inv_path.write_text(f"ip;zone;type;name;owner\n10.0.0.1;{bad};{bad};{bad};{bad}\n10.0.0.2;b{bad};vm;;\n")
    inv = load_inventory(str(inv_path))
    scan = tmp_path / "10.0.0.1.gnmap"
    scan.write_text("Host: 10.0.0.2 ()\tPorts: 22/open/tcp//ssh///\n")
    a = analyze(inv, {"10.0.0.1": [parse_scan(str(scan), "10.0.0.1")]}, [])
    doc = open(write_html(a, str(tmp_path)), encoding="utf-8").read()
    assert bad not in doc
