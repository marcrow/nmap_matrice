# Scans page: "Update the inventory" line

Status: done
Blocked by: 02, 03
Spec: ../spec.md

## What

On `/scans`, one line "N resolved names · M IPs not in the inventory. Update the inventory →", shown only when there is something to propose; the link opens `/inventory` with the panel unfolded. Counts as the panel computes them (fills + replacements, not conflicts nor skips).

## Acceptance

- shown after dropping the demo Scans on an inventory with empty names; gone once the names are applied

## Comments

2026-11-06 done: `#sline` inside step 2 (not at the top of the page as in the prototype: step 1 is long, the line must sit where the Scans are dropped); refreshed after an upload or an exclude. Checked: "31 resolved name(s) · 1 IP(s) not in the inventory · 1 conflict(s) to settle", link opens the panel.
