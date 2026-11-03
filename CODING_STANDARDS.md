# Coding standards

Rules for review that no automated check enforces. Ruff, the test suite and the snapshots in
`tests/fixtures/snapshots/` cover the rest (`uv run pytest`).

- **Verdicts mean the same thing in every view.** Each Verdict is defined in `GLOSSARY.md`. A
  change to `verdict.py` or `analysis.py` treats every Verdict the same way in the Markdown, CSV,
  Mermaid and HTML views. When the snapshots change, the diff explains why in the commit.
- **Port semantics live twice: `seg_matrix/ports.py` and `inRanges` in `seg_matrix/assets/report.js`.**
  A change to the port label format (`22`, `udp:161`) or to range matching lands in both.
- **The report runs offline.** `report.html` inlines its scripts, `mermaid.min.js` included; the CDN is
  only a fallback when the bundle is missing (the target machine has no internet access).
