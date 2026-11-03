# Inventory and Zones editors, client import/export

Status: needs-triage
Blocked by: 02
Spec: ../spec.md

## What

Inventory grid and Zones page as validated in 01. Optional `zones.csv` (web UI only). Zone and Machine rename propagate to `inventory.csv` and `flow_policy.csv`; delete only when unused. Import Zone list from another inventory. Client zip export/import (inventory + flow policy) with parse-error preview; whole-Mission zip.

## Acceptance

- renaming a Zone used in inventory and policy rewrites both; the CLI report is unchanged apart from the name
- a Mission without `zones.csv` works identically in CLI and app
- duplicate IP flagged inline and refused on save
