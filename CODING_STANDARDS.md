# Coding standards

Rules for review that no automated check enforces. Ruff, the test suite and the snapshots in
`tests/fixtures/snapshots/` cover the rest (`uv run pytest`).

- **Verdicts mean the same thing in every view.** Each Verdict is defined in `GLOSSARY.md`. A
  change to `verdict.py` or `analysis.py` treats every Verdict the same way in the Markdown, CSV,
  Mermaid and HTML views. When the snapshots change, the diff explains why in the commit.
- **Port semantics live in `segowl/ports.py`, mirrored by `inRanges` in `segowl/assets/report.js` and by
  `tokOk` in `segowl/assets/app_ports.js`** (the app's inline check; the server re-checks with `ports.py`).
  A change to the port label format (`22`, `udp:161`) or to range matching lands in all three.
- **The report runs offline.** `report.html` inlines its scripts, `cytoscape.min.js` included, and loads
  nothing from the network (the target machine has no internet access).
