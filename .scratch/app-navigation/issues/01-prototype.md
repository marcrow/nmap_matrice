# Prototype: menu, Overview, Auditor Kit tab, Port Groups and Port Labels grids

Status: needs-info
Blocked by: –
Spec: ../spec.md

## What

Throwaway clickable HTML mockup, offline, validated palette and logo, vendored Tabulator 6.7.1, fake data only, kept off the main line (branch `prototype/app-navigation`), like ticket 01 of `local-app`:

- the new main menu and the Auditor Kit sub-tabs;
- Overview: step states with next actions for an empty, a half-done and a finished Mission (switcher), client exchange block, tutorial of the work process (collapsible);
- Port Groups grid: shipped vs Mission rows, override, reset, rename everywhere, delete when unused;
- Port Labels grid with vendor and cleartext, two services on one port, completing a shipped label, tag picker, filters;
- Scan Profiles port search with "+ label this port".

The spec's questions are answered (tag vocabulary derived from the data, Source done at one Scan, tutorial always below the Overview's states); where a layout choice is still open, offer two variants with the switcher.

## Acceptance

- the user clicks through every screen and gives a verdict per screen
- no browser alert / prompt / confirm anywhere
- the verdicts and the answers to the open questions are recorded in this ticket's Comments

## Comments

2026-11-04: prototype on branch `prototype/app-navigation`, checked out in the worktree `../nmap_matrice-proto-nav`: open `prototype_nav/index.html` by double-click (offline). The bottom bar switches:
- **Overview**: A checklist (one row per step) · B pipeline (one card per step). Mission state: empty / in progress / done / broken. The next step is the first one with a problem (⚠ blocks the report), else the first one not done. Client exchange and the "How SegOWL works" tutorial sit below, always shown.
- **Kit nav**: A sub-tabs under the main menu · B sidebar inside the page. A banner recalls that the tab edits this Mission's copies and which kit they match.
- **Scan Profiles**: the search shows "+ label this port" for a port without a Port Label (try 8291, 12345, 4840): inline form, tags with suggestions, the label then appears marked Mission.
- **Port Groups**: shipped rows grey; editing a shipped group's ports replaces it in the Mission ("Reset to shipped"); rename (Mission groups only) reports the rules and profiles rewritten; Delete disabled while used, saying by what; invalid ports in red.
- **Port Labels**: shipped rows grey with "Complete" (copies into the Mission, replaces the shipped one by port + product); three services on 443; tags derived from the data with suggestions, "did you mean", new tags dashed; vendor list with free text; cleartext yes / no / unknown; filters by text, tag, vendor, Mission rows only.
- Inventory, Scans, Flow Policy, Report and Kits are placeholders (unchanged screens).

Awaiting the user's verdict per screen (Overview A/B, Kit nav A/B, the three editors, the tutorial text).
