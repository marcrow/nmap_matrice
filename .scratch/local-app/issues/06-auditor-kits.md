# Auditor Kits

Status: done
Blocked by: 04
Spec: ../spec.md

## What

Kits = folders with `port_groups.csv`, `scan_profiles.csv`, `port_labels.csv`. Sources: shipped `segowl/kits/<name>/` (read-only) + `~/.config/segowl/kit_dirs` edited from the Kits page. Save Mission config as kit, apply kit (replace, with preview), import/export zip. At least one shipped default kit.

## Acceptance

- a saved kit contains only the three files (no inventory, policy, scans)
- shipped kits cannot be overwritten from the UI
- applying a kit then exporting it round-trips identically

## Comments

2026-11-04: `segowl/kits.py`, page Kits. Decisions:
- A kit folder's sub-folders are kits (a cloned repo holds several kits); a folder that is itself a kit is not listed.
- ~~Applying replaces all three Mission files~~ (changed 2026-11-04, user's decision): applying shows a row-level
  diff per file (rows keyed by group / profile name / port + product: added, dropped, changed) and the auditor ticks
  the kit files to apply; a file the kit lacks or left unticked stays as it is. The resulting config is validated as
  a whole (a profile may rely on the Mission's groups, or need the kit's), live as boxes are ticked. Importing a zip
  opens its diff with the Mission straight away. The apply is refused if the Mission or the kit changed since the
  preview. Round-trip: the files applied come back byte-identical when the Mission is saved as a kit and exported.
- Writes are refused inside `segowl/kits/` (shipped, read-only, symlinks resolved) and into a folder holding an
  `inventory.csv` (a Mission). Kit zips: only the three files are read, Scan Profiles and Port Groups validated.
- Shipped kit `segmentation`: three Scan Profiles (broad, full-tcp, connect) on the default Port Groups.
- Port Labels are not scanned for client data (spec: "no content scan").
