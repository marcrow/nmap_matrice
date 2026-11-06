# Scans page: "Update the inventory" line

Status: ready-for-agent
Blocked by: 02, 03
Spec: ../spec.md

## What

On `/scans`, one line "N resolved names · M IPs not in the inventory. Update the inventory →", shown only when there is something to propose; the link opens `/inventory` with the panel unfolded. Counts as the panel computes them (fills + replacements, not conflicts nor skips).

## Acceptance

- shown after dropping the demo Scans on an inventory with empty names; gone once the names are applied

## Comments
