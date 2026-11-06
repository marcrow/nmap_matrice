# Tables (search + sort), Target details, Flow Policy counters, Scans and Anomalies

Status: done
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

## Comments

**2026-11-05, done.** Search and sort: `report.js` `enhanceTables` adds the search field and the header sort to every non-matrix table with 2 rows or more (the Python `_filter_box` calls are gone, one place instead of each table; the Diff tables are enhanced after each run); `filterRows` and `sortBy` keep a `tr.more` detail with its row; numbers and IPs sort numerically (`localeCompare` numeric). Flow Policy: `_policy_tab` counter tiles (click scrolls to Findings, undeclared, Rules), each table in its own section card. Target details: `_source_table_html(src, a)` unfolds `_port_detail` (state per Scan, disputed states in amber, Port Labels from `Analysis.labels`, the Mission's `port_labels.csv` over the shipped ones, passed by `cli.run`). Declared Sources: `nmap.discover_declared` (the `scans/<ip>/` folders), `analyze(declared=…)`, `Analysis.missing = declared − scanned`; `build_matrix` no longer returns `missing`; a declared folder outside the inventory is listed as such. Checked headless on the demo: "ilo" keeps ilo-01, ilo-02, 10.40.0.23; sorting the Findings by port gives 22 before 443. Test: `test_sources_without_scan_are_the_declared_folders_only`.
