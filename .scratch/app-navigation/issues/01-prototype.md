# Prototype: menu, Overview, Auditor Kit tab, Port Groups and Port Labels grids

Status: ready-for-agent
Blocked by: –
Spec: ../spec.md

## What

Throwaway clickable HTML mockup, offline, validated palette and logo, vendored Tabulator 6.7.1, fake data only, kept off the main line (branch `prototype/app-navigation`), like ticket 01 of `local-app`:

- the new main menu and the Auditor Kit sub-tabs;
- Overview: step states with next actions for an empty, a half-done and a finished Mission (switcher), client exchange block, tutorial of the work process (collapsible);
- Port Groups grid: shipped vs Mission rows, override, reset, rename everywhere, delete when unused;
- Port Labels grid with vendor and cleartext, two services on one port, completing a shipped label, tag picker, filters;
- Scan Profiles port search with "+ label this port".

Where a choice is open (spec, "Open questions"), offer two variants with the switcher.

## Acceptance

- the user clicks through every screen and gives a verdict per screen
- no browser alert / prompt / confirm anywhere
- the verdicts and the answers to the open questions are recorded in this ticket's Comments
