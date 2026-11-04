# App navigation: Overview, Auditor Kit tab, Port Groups and Port Labels editors

Status: ready-for-agent

Vocabulary: `GLOSSARY.md` (Mission, Auditor Kit, Port Group, Port Label, Scan Profile, Source…). Decisions: `docs/adr/0003` (Mission folder is the only state), `docs/adr/0004` (stdlib server). Builds on `.scratch/local-app/`. Validated prototype: branch `prototype/app-navigation`, `prototype_nav/index.html` (four rounds, verdicts in `issues/01-prototype.md`): it is the reference for layout and behaviour.

## Goal

The app grew one page per ticket; its menu mixes the client's data with the auditor's tooling and does not follow the course of an audit. Reorganise it so that the work process is obvious and an experienced auditor reaches every screen in one or two clicks, make the whole Auditor Kit editable from the UI (Port Groups and Port Labels are hand-edited CSV files today), and present the tool to its audience.

Audience: pentesters and auditors who know nmap. The message: SegOWL brings **rigour** (the same optimised nmap from every Source, against the whole inventory), **visibility** (one view per Zone and per Source instead of thousands of nmap answers) and **quality of restitution** (matrices and diagrams per client and target selection, dropped into the pentest or audit report).

## Decisions (2026-11-04, with the user)

- **Two kinds of screens.** The client's data stays in the Mission and never travels (inventory and Zones, Scans, Flow Policy, Report). The auditor's tooling is exactly the content of an Auditor Kit (Scan Profiles, Port Groups, Port Labels) plus kit management; it travels from Mission to Mission.
- **Main menu in audit order:** Overview · Inventory & Zones · Auditor Kit · Scans · Flow Policy · Report. Flow Policy after Scans: deciding is easier once flows are observed; it can still be filled at any time.
- **Auditor Kit navigation: "section header"** (prototype variant C; sub-tabs under the menu were missed, a sidebar ate width): "Auditor Kit ▾" in the main menu opens a dropdown of its four screens with a one-line description each; the page opens with a sticky header of four large tabs (name, count, description: Scan Profiles · Port Groups · Port Labels · Kits) and a line recalling that the tab edits **this Mission's copies** (never a kit folder) and which known kit they match.
- **Scan building lives on the Scans page**; Auditor Kit › Scan Profiles is the kit's **catalogue**. A profile modified while building a scan offers **"Save as a new profile version"**.
- **Overview replaces the Mission page and is the landing page**: step states (checklist, not pipeline), client exchange, then a visual presentation of the tool.
- Old URLs (`/mission`, `/profiles`, `/kits`) redirect to their new place.

## Screens

### Overview

- **Checklist**, one row per step in menu order: status (✓ done, ◐ in progress, ○ not started, ! problem), summary, next action. The highlighted next step is the first one with a problem (it blocks the report), else the first one not done. States are computed from the Mission folder, nothing is stored (ADR-0003):
  - Inventory: N Interfaces, M Zones; problems the inventory editor flags (Interface without Zone, duplicate IP).
  - Auditor Kit: N Scan Profiles, Mission Port Groups / Port Labels; "same as kit X" when the Mission's files match a known kit byte for byte.
  - Scans: Sources with at least one Scan imported / Sources ("3 to go → download the scripts").
  - Flow Policy: N rules, N undecided, the CLI's message for a rule it refuses.
  - Report: N Findings, N undeclared flows, or the generation error.
- Client exchange block (moved from the Mission page).
- **Presentation**, always shown below (never in the way, no folding), visual, using the palette's amber:
  - hero card across the page: the message (rigour, visibility, restitution) and the report's **two views drawn as the report draws them** (Zone view: pastel Zone pills, edges coloured by Flow Policy status, admin ports in bold red, dashed "reachable"; Source view: dark hexagon Source, targets grouped in tinted Zone frames), switchable;
  - the work process in six illustrated steps: Define the inventory (IP and Zone; type and Machine name optional, names could later come from the Scans' DNS resolution, see `.scratch/inventory-names-from-scans/`) → Select your Auditor Kit → Configure (optional) → Run on the Sources → Define the Flow Policy (optional) → Matrices & diagrams; then the same six steps in words, with links;
  - "Why SegOWL": the grep you would run without it and the questions it leaves open, next to the Zone matrix; several Sources, one method; a retest compared cell by cell; benefit cards (build the right nmap command, nothing forgotten, your method shared and improved, step back over the data, Findings not noise, retest and compare, straight into your report).
- The diagrams are **static SVG files** (inline styles, own white background, system fonts, no script), served by the app and reused as is in `README.md` (`<img src=…>`): one source for both.

### Scans

1. **Build the scan**: pick a Scan Profile of the kit (its description shown), adjust ports (port search, "+ label this port" for a port without a Port Label) and options, see the command for a Source. When the profile differs from the saved one, a bar lists the changes (+ports, −ports, options) and offers **Save as a new profile version…** (name `<profile>-v2` and description "Variant of …" prefilled; the original stays as it was), **Update `<profile>`** (warns when Scans were already imported with the previous version) and **Discard**. Scripts of a modified profile cannot be downloaded until it is saved: Scans are tracked by profile name.
2. **Run it from each Source**: today's Sources × profiles grid (✓ when a Scan is in, script download, drop zone, exclude).

### Auditor Kit tab

- **Scan Profiles**: catalogue: name, **what it is for** (description, edited in place), ports (folded chips), options, Scans imported; Open in Scans, Duplicate, Delete (inline confirmation), + New profile (opens the builder). `scan_profiles.csv` gains an optional 4th column `description` (a 3-column file still loads; kits diff it like any column).
- **Port Groups**: grid `group;ports`. Shipped groups greyed; editing one's ports creates the Mission's group of the same name, which replaces it (today's semantics of `load_port_groups`); "Reset to shipped" removes it. Ports cell: chips, folded beyond 10 ("+N more"); editor with autocompletion like the port search (port number or product → Port Labels and IANA, `udp:` ports, the UDP twin of a typed port, `@group` **inserts a copy of that group's ports**: no nesting, no format change); syntax validated inline. Rename (Mission groups only) rewrites `flow_policy.csv` and `scan_profiles.csv` at once; delete only when unused. "Used by": the profiles by name, the rules on hover. First column "source" (shipped / replaces / Mission), sortable.
- **Port Labels**: grid `port;product;tags;vendor;cleartext` (format of the shipped file; vendor and cleartext optional). Shipped labels greyed, read-only, with **Complete**: copies the label into the Mission, where it **replaces** the shipped one (same port + product: `load_labels` merges by that key instead of appending). Several services may share a port. **"+ New label" opens a form** (port with autocompletion, product, tags, vendor, cleartext); an existing port + product is refused with the way out ("already ships: use Complete on it"). Tags: see below. Cleartext `yes` / `no` / empty. Filters: text, tag, vendor, Mission rows only. First column "source", sortable.
- **Kits**: today's page (diff, pick files, save, zip, kit folders).

### Tag vocabulary

No vocabulary file and no generated list: the vocabulary is **derived from the data**. The editor suggests the union of the tags in use (shipped labels + the Mission's rows), computed on load. A new tag is accepted as typed; the editor marks it "new" (dashed) and, when it is close to an existing one (case, plural, small edit distance), suggests that one. On save, tags are normalised (lower case, trimmed, inner spaces → `-`). The comment block of the shipped file stays human documentation; the tool does not read it. A kit stays self-contained: its `port_labels.csv` carries its own tags.

Rejected: a central vocabulary file (overhead, blocks adding a tag from the UI, a dependency between two files in kits and exports); a script listing the tags in use into comments (generated text in a hand-maintained file).

## Non-goals

Editing a kit folder in place (edit the Mission, then save as kit); a Port Labels editor for the shipped file (maintained in the repo, ticket 07 of `local-app`); Port Groups referencing other groups (`@group` only inserts a copy); roles, permissions; mobile layout. Out of scope, traced: inventory names from the Scans' DNS resolution (`.scratch/inventory-names-from-scans/`), Scan duration estimate (`.scratch/scan-time-estimate/`).

## Plan

| # | Ticket | Blocked by |
|---|---|---|
| 01 | Prototype (done, four rounds) | – |
| 02 | Navigation shell and Auditor Kit tab (section header, redirects) | 01 |
| 03 | Overview page (checklist, client exchange, presentation) | 02, 07 |
| 04 | Port Groups editor | 02 |
| 05 | Port Labels editor, merge by port + product, "+ label this port" | 02, Port Label metadata (vendor, cleartext) committed |
| 06 | Scan builder on Scans, Scan Profiles catalogue, profile description | 02 |
| 07 | Presentation diagrams as static SVG files, reused in README | 01 |
