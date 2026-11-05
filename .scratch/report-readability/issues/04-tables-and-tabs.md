# Tables (search + sort), Target details, Flow Policy counters, Scans and Anomalies

Status: ready-for-agent
Blocked by: 02
Spec: ../spec.md

## What

- Every report table gets one search field above it and sorts on a header click (again: reverse; numbers sort as numbers; an unfolded detail row moves with its row). Plain JS in `report.js`; tables stay real `<table>`s. No per-column filters.
- Flow Policy tab: counters as tiles (Findings, undeclared, rules) linking to their table; the big tab carries the counts.
- Target details (Per source): a row unfolds into the state each Scan saw per port (conflicts visible) and the Port Label.
- Scans tab holds Scans, Conflicts, Coverage and the former Anomalies tab. "Sources without scan" lists only declared Sources (a `scans/<ip>/` folder) without a Scan, computed in the analysis (the prototype hack in `cli.py` `DECLARED_EMPTY` does not go to master).

Reference: branch `prototype/report-readability`, `report.js` `filterRows`, `sortBy`, `toggleMore`; `html.py` `_filter_box`, `_port_detail`, `_source_table_html`, policy tab tiles.

## Acceptance

- on the demo, searching "ilo" in any table keeps only matching rows; sorting by a port column orders 22 before 443
- a Mission with an empty `scans/10.0.0.9/` folder lists 10.0.0.9 under Sources without scan; an inventory Interface with no folder is not listed
- `tests/` cover the declared-Sources rule
