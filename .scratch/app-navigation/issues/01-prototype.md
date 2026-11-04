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

2026-11-04 verdicts, round 1 (user's walkthrough):
- **Overview: A, checklist.** Clearer than the pipeline here: errors show at once, and more information fits without overflowing the screen.
- **Kit nav: neither.** Sub-tabs under the menu are not readable: one does not see there are sub-tabs, they get missed. The sidebar is visible but eats useful width on data-heavy screens (acceptable on a large screen, a pity on a small one). → round 2 proposes other layouts.
- **Scan Profiles:** must create, duplicate (clone the current profile to modify it) and delete profiles, and save the profile being built "as a new profile" from the command/generation panel. Note: the built editor (local-app 04) already has + New / Duplicate / Delete; the prototype only mocked the port search, so round 2 shows the real toolbar plus "Save as new profile" next to the command.
- **Port Groups:** creating a group works (the `@` is added by itself), Reset to shipped and Delete are good, the table view is fine. Missing: port autocomplete in the ports cell (Port Labels, IANA, `udp:` ports). Wanted: a more visual list, long port lists collapsed / expanded. Asked: could a group contain other groups? (see round 2)
- **Port Labels:** good overall, creating a tag works. "+ Label" is confusing: it adds a blank row and switches the filter; the user created two rows without meaning to. → round 2: an explicit new-label form.
- **Kits:** the prototype's summary hid the diff and the "save this Mission as a kit" form (both built in local-app 06): round 2 shows them.
- New idea, out of scope: fill inventory names from the names resolved in the Scans → `.scratch/inventory-names-from-scans/spec.md`.

2026-11-04 round 2 (same file; the Overview switch is gone, A is kept):
- **Kit nav**, two new layouts, default C:
  - **C · section header**: "Auditor Kit ▾" in the main menu opens a dropdown of the four screens with a one-line description each; on the page, a sticky header with four large tabs (name, count, description) and the "this Mission's copies / same as kit X" line. Visible, costs no width.
  - **D · group in menu**: no second level at all; the main menu carries the four screens inside a framed "AUDITOR KIT" group (9 entries, one click each).
  - A (tabs) and B (sidebar) are kept for comparison.
- **Scan Profiles**: the real toolbar (profile select, name, + New, Duplicate, Delete with an inline confirmation) and **Save as new profile…** under the command preview (inline name field; the current profile stays as it was).
- **Port Groups**: the ports cell autocompletes like the Scan Profiles search: a port number or a product (`338` → 3389 RDP, `winbox`), `udp:` ports (`udp:16` → udp:161 SNMP), the UDP twin of a typed port, and `@group`, which **inserts a copy of that group's ports**. Enter on a typed port keeps it as typed, arrows pick a suggestion, `,` moves to the next port. Ports show as chips; a list longer than 10 is folded ("+7 more ▾" / "show less ▴"). Double-click or click to edit.
- **Groups inside groups**, the user's question: round 2 only inserts a copy (`@web` → its ports), which needs no change to `port_groups.csv` or the CLI. A live reference (`@web` kept in the file) would mean: the CLI parser resolving references and refusing cycles; overriding a shipped group silently changing every group that includes it (wanted or not); a kit whose group includes another group it does not carry. Open question for the verdict: is the copy enough?
- **Port Labels**: "+ New label" opens an explicit form above the grid (port with autocomplete, product, tags, vendor, cleartext; Enter adds, Esc cancels); no blank row any more. A port + product that already exists is refused with the way out ("already ships: use Complete on it"); the new row is scrolled to and highlighted.
- **Kits**: shows what is built: "Apply to this Mission…" opens the diff with the file picker; "Save this Mission as a kit" with name and folder; "Import a kit zip" opens its diff right after.
