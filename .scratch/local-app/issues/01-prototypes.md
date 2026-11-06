# Prototypes of the three tedious screens

Status: done
Blocked by: –
Spec: ../spec.md

## What

Throwaway HTML mockups (`/prototype`) with the validated palette and logo, offline (vendored Tabulator 6.7.1): Inventory + Zones (2000-row grid, paste from LibreOffice, autocomplete, bulk edit, CIDR add, Zone rename), Scan Profile editor (port search, option controls, live command preview), Flow Policy grid (dynamic dropdowns). Fake data only.

## Acceptance

- the user clicks through and validates each screen
- Tabulator keyboard/paste feel judged against a spreadsheet; if it disappoints, retry with Jspreadsheet CE 5.0.4

## Comments

2026-11-03: prototype at `prototype_app/index.html` (open by double-click, offline). Bottom bar / `?screen=inventory|profile|policy&v=A|B` switches:
- Inventory A spreadsheet + Zone sidebar · B paste→map columns→Zone board (drag Machines)
- Scan Profile A two-column builder · B command line with palette
- Flow Policy A rule grid · B Zone×Zone matrix, click to decide, observed flows shown
Awaiting the user's verdict (or a mix: "sidebar from A, wizard from B").

2026-11-03 round 2, after the user's feedback on variant A:
- Inventory: one click edits; dragging selects; Ctrl+click adds non-adjacent blocks; typing over a selection fills every cell; an Excel-style fill handle extends series (vm-01 → vm-02, IPs); Ctrl+D copies down; "+ Column" uses an inline field instead of an alert; the Zone sidebar is labelled as a filter; the "set Zone" select is gone, since type-to-fill replaces it.
- Scan Profile: Port Groups as checkboxes, a top-ports control, separate TCP and UDP controls, -Pn always visible, an NSE picker, about 50 searchable options, and two commands when top + explicit ports are combined.
- Flow Policy: the dropdown is grouped into Any / Zones / Machines.

2026-11-03 verdicts:
- Inventory: **A** (spreadsheet + Zone sidebar, with the round-2 changes).
- Scan Profile: **A plus the B command line on top**, two-way synced. The palette suggests top ports, ports, options, NSE scripts and refused flags.
- Flow Policy: **B** (Zone × Zone matrix + exceptions panel). No prompt()/alert: the "Only… then deny the rest" choice, the per-cell rules and the machine exceptions are inline forms. Sticky headers for large matrices. Open question: readability with many Zones.
- No browser alerts or prompts anywhere in the real app.
- Prototype kept on branch `prototype/local-app` (`prototype_app/index.html`), out of the main line.
