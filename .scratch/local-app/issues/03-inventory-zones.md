# Inventory and Zones editors, client import/export

Status: done
Blocked by: 02
Spec: ../spec.md

## What

Inventory grid and Zones page as validated in 01. Optional `zones.csv` (web UI only). Zone and Machine rename propagate to `inventory.csv` and `flow_policy.csv`; delete only when unused. Import Zone list from another inventory. Client zip export/import (inventory + flow policy) with parse-error preview; whole-Mission zip.

## Acceptance

- renaming a Zone used in inventory and policy rewrites both; the CLI report is unchanged apart from the name
- a Mission without `zones.csv` works identically in CLI and app
- duplicate IP flagged inline and refused on save

## Comments

2026-11-03 done.
- **Files:** `segowl/mission_files.py` (CSV read/write/rename/validation, reusing the CLI's `load_inventory`), `Mission` editor methods and JSON routes in `segowl/app.py`, page assets `segowl/assets/{inventory.html,app_inventory.js,app_mission.js,app.css}`, vendored Tabulator 6.7.1 (MIT, `TABULATOR-LICENSE`).
- **Saving:** autosave, 1 s after the last change, checked against the file fingerprints. Duplicate or invalid IPs block the save with an inline status.
- **Renames:** a Zone rename comes from the sidebar; a Machine rename comes from editing a name shared by other Interfaces or referenced by the Flow Policy, through an inline banner. Both flush the pending save, then rewrite every file at once.
- **Paste:** Excel-style, anchored at the active cell; rows are added as needed and a header line is skipped.
- **Client import/export:** on the Mission page. Import is a dry run first, then an inline "Replace".
- **Security:** POSTs require an `X-SegOWL` header (CSRF), the Host header is checked when there is no login (DNS rebinding), and Tabulator is the only third-party asset.
- **Not done:** Zone descriptions cannot be edited in the UI yet (zones.csv keeps them); add an editor when it's asked for.
