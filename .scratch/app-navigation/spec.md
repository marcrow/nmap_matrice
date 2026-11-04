# App navigation: Overview, Auditor Kit tab, Port Groups and Port Labels editors

Status: ready-for-agent

Vocabulary: `GLOSSARY.md` (Mission, Auditor Kit, Port Group, Port Label, Scan Profile, Source…). Decisions: `docs/adr/0003` (Mission folder is the only state), `docs/adr/0004` (stdlib server). Builds on `.scratch/local-app/`.

## Goal

The app grew one page per ticket; its menu mixes the client's data with the auditor's tooling and does not follow the course of an audit. Reorganise it so that a newcomer understands the work process and an experienced auditor reaches every screen in one or two clicks, and make the whole Auditor Kit editable from the UI (Port Groups and Port Labels have no editor today: they are hand-edited CSV files).

UX is a requirement, as in `local-app`: screens are prototyped and validated before being built.

## Decisions taken (2026-11-04, with the user)

- **Two kinds of screens.** The client's data stays in the Mission and never travels (inventory and Zones, Scans, Flow Policy, Report). The auditor's tooling is exactly the content of an Auditor Kit (Scan Profiles, Port Groups, Port Labels) plus kit management; it travels from Mission to Mission.
- **Main menu in audit order:** Overview · Inventory & Zones · Auditor Kit · Scans · Flow Policy · Report. Flow Policy comes after Scans because deciding is easier once flows are observed (bootstrap); it can still be filled at any time.
- **One Auditor Kit tab** with sub-tabs: Scan Profiles · Port Groups · Port Labels · Kits (today's Kits page: diff, pick files, save, zip, kit folders). The tab edits **this Mission's copies** (`mission/port_groups.csv`, …), never a kit folder: edit in the Mission, then save as a kit.
- **Overview replaces the Mission page and is the landing page** (today: Report). Per step, its state and the next thing to do; the client exchange (client zip, whole Mission zip) moves there; below, a presentation / tutorial of the work process.
- **"+ label this port"** shortcut in the Scan Profiles port search, for a port without a Port Label (approved).
- Old URLs (`/mission`, `/profiles`, `/kits`) redirect to their new place.

## Screens

### Overview

- One line per step, in menu order, with a status (✓ done, ◐ in progress, ○ not started, ⚠ problem) and a link to the next action. Examples:
  - Inventory: N Interfaces, M Zones; ⚠ Interfaces without Zone, duplicate IP (what the inventory editor flags).
  - Auditor Kit: N Scan Profiles, N Port Groups / Port Labels added by the Mission; "same as kit X" when the Mission's files match a known kit byte for byte (computed, nothing stored: ADR-0003).
  - Scans: Sources with every Scan Profile done / Sources; "3 to go → download scripts".
  - Flow Policy: N rules, N undecided, N refused by the report.
  - Report: N Findings, N undeclared flows, or the generation error.
- Client exchange block (moved from the Mission page).
- Presentation / tutorial: what SegOWL measures, then the work process step by step (prepare the inventory, possibly from the client's zip → pick a kit → add Sources and download their scripts → run them on each Source → drop the results → decide the Flow Policy from observed flows → read and share the report), with links to each screen. Collapsible; folded state remembered per browser (localStorage, a per-viewer convenience).

### Auditor Kit tab

- Sub-navigation always visible; a line under it recalls that the tab edits this Mission's copies, and which known kit they match, if any.
- **Scan Profiles**: today's editor, plus "+ label this port" in the port search.
- **Port Groups**: grid `group;ports`. Shipped groups shown greyed; editing one creates the Mission's group of the same name, which overrides it (today's semantics of `load_port_groups`); "reset to shipped" deletes the override. Port syntax validated inline (same rules as the Flow Policy). Rename rewrites `flow_policy.csv` and `scan_profiles.csv` at once (like Zone rename); delete only when unused ("used by 3 rules, 2 Scan Profiles"). Shows each group's port count.
- **Port Labels**: grid `port;product;tags;vendor;cleartext` (format of the shipped file; vendor and cleartext optional). Shipped labels greyed and read-only; several services may share a port (a row is keyed by port + product). Completing a shipped label creates a Mission row with the same port + product that **replaces** it instead of adding a duplicate (`load_labels` merges by port + product). Tags picked from the fixed vocabulary; cleartext `yes` / `no` / empty; port syntax validated inline. Filter by text, tag, vendor, "Mission rows only".
- **Kits**: today's page.

## Non-goals

Editing a kit folder in place (edit the Mission, then save as kit); a Port Labels editor for the shipped file (it is maintained in the repo, ticket 07 of `local-app`); roles, permissions; mobile layout.

## Open questions (for the prototype)

- Where the tag vocabulary lives so the editor and the shipped file share one source (today: a comment block in `segowl/defaults/port_labels.csv`).
- Overview: does a Source count as done when every Scan Profile has its Scan, or when it has at least one Scan?
- Does the tutorial stay on the Overview once the Mission is under way, or move behind a "How it works" link?

## Plan

| # | Ticket | Blocked by |
|---|---|---|
| 01 | Prototype: menu, Overview + tutorial, Auditor Kit tab, Port Groups and Port Labels grids, "+ label this port" | – |
| 02 | Navigation shell and Auditor Kit tab (move Scan Profiles and Kits, redirects) | 01 |
| 03 | Overview page (step states, client exchange, tutorial) | 02 |
| 04 | Port Groups editor (override, rename everywhere, delete when unused) | 02 |
| 05 | Port Labels editor, merge by port + product, "+ label this port" | 02, Port Label metadata (vendor, cleartext) committed |
