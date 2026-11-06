# Local app: a web UI around the Mission folder

Status: done (tickets 01-06); ticket 07 waits on a human with vendor logins

Vocabulary: `GLOSSARY.md` (Mission, Scan Profile, Auditor Kit, Port Label…). Decisions: `docs/adr/0003` (Mission folder is the only state), `docs/adr/0004` (stdlib server, file auth).

## Goal

Save the auditor time on the tedious preparation work (inventory, Zones, port lists) and make every Source scanned the same way, then show the existing report live. UX is a requirement, not polish: screens are prototyped and validated before being built.

Non-goals: launching nmap from the app (scans run by hand on each Source), deleting Scans, roles/permissions, git integration, PowerShell export, port popularity statistics.

## Constraints

- Offline: no CDN, no external fonts; vendored assets only (Tabulator 6.7.1 js+css, MIT, like `mermaid.min.js`).
- Zero runtime Python dependency: `http.server.ThreadingHTTPServer`, `ssl`, `hashlib.scrypt` (ADR-0004).
- Plain files only (ADR-0003). Every file the app adds is optional: hand-editing and the CLI keep working without it.
- Validated visual identity (palette #0B1F33 / #00C8FF / #65E3FF / #FFB020 / #6B7C93 / #E6EDF5, owl logo).
- `nmap-services` is never shipped nor read (NPSL). Port reference = IANA registry extract (CC0) + our `port_labels.csv`.

## Launch and server

- `segowl serve <mission_dir>`: one Mission per launch, creates the folder skeleton if missing.
- Server config dir `~/.config/segowl/` (`--config DIR`): `users` (`login:scrypt-hash`, written by `segowl user add <login>`), `kit_dirs` (one path per line, edited from the Kits page).
- No `users` file → bind `127.0.0.1` only. With it → `--host` allowed, `--cert/--key` enable HTTPS. All users equal.
- Concurrent edits: a save is refused if the file changed since it was loaded (fingerprint), "modified by someone else, reload".
- Navigation: Mission · Inventory · Zones · Flow Policy · Scan Profiles · Scans · Kits · Report. The report is today's `report.html`, regenerated on every change.

## Mission folder additions (all optional)

```
mission/
  zones.csv            zone;description   only for the web UI (empty Zones, descriptions); CLI ignores it
  scan_profiles.csv    name;ports;options
  port_labels.csv      port;product;tags  mission additions to the shipped labels
```

Zones = those of `inventory.csv` ∪ `zones.csv`.

## Editors

- **Inventory**: spreadsheet-like grid (Tabulator): Tab/Enter/arrows, multi-row paste from Excel/LibreOffice, autocomplete of zone/type/name, bulk edit of selected rows, add rows from a CIDR range, inline validation (duplicate IP, empty Zone), free columns as normal columns. CSV upload/download kept.
- **Zones**: quick creation; rename rewrites `inventory.csv` and `flow_policy.csv` at once (same for Machine rename); delete only when unused ("used by 12 Interfaces, 3 rules"); import the Zone list (not the Interfaces) from another `inventory.csv`.
- **Scan Profile**: left, port search (Port Groups first, then Port Labels incl. tags, then IANA) with one-click add, chosen ports as tcp/udp chips with counts; right, data-type-appropriate controls for common options + option search + an "other options" field, live preview of the command for a sample Source, warnings (slow UDP…). `ports` uses the Flow Policy syntax plus `top:N` (`@admin,8443,udp:161,top:1000`). Any nmap option is allowed except a deny list: `-iL --exclude --excludefile -S -D --proxies --dns-servers --script-args` (client data), `-oA -oX -oN -oG` (output managed by SegOWL), `--open` (hides REACHABLE).
- **Flow Policy**: rule grid with dynamic dropdowns (Zones, Machines, Port Groups), inline validation, "bootstrap from observed flows" (reuses `observed_zone_flows.csv`).

## Scans

- A Source is a folder `scans/<ip>/` (an inventory IP); "Add Source" creates it empty (decided in ticket 04).

- Export per Source: one `.sh` script per Source and Scan Profile, plus the raw command to copy. Targets = all inventory Interfaces minus Self; output `-oA scans/<src_ip>/<profile>`.
- Progress grid Source × Scan Profile, ✓ when `scans/<src_ip>/<profile>.xml` exists (file presence only).
- Drag-and-drop XML files onto a Source row → stored in `scans/<src_ip>/`. Exclude / re-include = move to/from `excluded/`. No deletion.

## Auditor Kits

- A kit = folder with `port_groups.csv`, `scan_profiles.csv`, `port_labels.csv`. No client data, by construction (no targets, option deny list); no content scan.
- Sources: shipped kits `segowl/kits/<name>/` (read-only) + folders listed in `kit_dirs` (e.g. a cloned private repo, updated with `git pull` by the user).
- Actions: save the Mission's config as a kit (into a chosen kit dir), apply a kit to the Mission (row-level diff, then the auditor picks which kit files replace the Mission's; a file the kit lacks or left unpicked is untouched), import/export a kit as zip.
- Client export: zip of `inventory.csv` + `flow_policy.csv`; import replaces them after a parse-error preview. Plus "zip the whole Mission".

## Port reference

- Shipped: `segowl/defaults/iana_ports.csv` (trimmed IANA extract: name, port, proto, description; refreshed by hand per release) and `segowl/defaults/port_labels.csv` (demo, fairly complete: Veeam, iLO, iDRAC/IPMI, ESXi/vCenter, Proxmox, Fortinet, RDP…).
- Port Labels are descriptive only: tags help search, they filter nothing (Port Groups do).

## Plan

| # | Ticket | Blocked by |
|---|---|---|
| 01 | Prototypes: Inventory+Zones, Scan Profile, Flow Policy | – |
| 02 | Server: serve, auth, HTTPS, report served/regenerated, optimistic save | 01 |
| 03 | Inventory and Zones editors, client import/export | 02 |
| 04 | Port reference, Scan Profile editor, export scripts, Scans progress/upload | 03 |
| 05 | Flow Policy editor | 03 |
| 06 | Auditor Kits | 04 |
| 07 | Demo `port_labels.csv` (agent research) | – |
