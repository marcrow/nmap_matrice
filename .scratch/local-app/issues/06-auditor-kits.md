# Auditor Kits

Status: needs-triage
Blocked by: 04
Spec: ../spec.md

## What

Kits = folders with `port_groups.csv`, `scan_profiles.csv`, `port_labels.csv`. Sources: shipped `segowl/kits/<name>/` (read-only) + `~/.config/segowl/kit_dirs` edited from the Kits page. Save Mission config as kit, apply kit (replace, with preview), import/export zip. At least one shipped default kit.

## Acceptance

- a saved kit contains only the three files (no inventory, policy, scans)
- shipped kits cannot be overwritten from the UI
- applying a kit then exporting it round-trips identically
