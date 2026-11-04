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

2026-11-04 verdicts, round 2:
- **Kit nav: C (section header)**: the cleanest, every piece of information visible.
- **Scan Profiles**: the round-2 editor duplicates the scan-building screen. Wanted instead: Auditor Kit › Scan Profiles **lists every profile with its details and a short description** of what it is for (to apply it well); building / adjusting a scan happens on the Scans page; when a profile is modified there and differs from the saved one, offer **"Save as a new profile version"**. Accepted cost: an optional `description` column in `scan_profiles.csv`.
- **Port Groups**: good, autocompletion works (UDP needs `udp:` typed first: acceptable). Fix: the first column has no title; the "Mission" badges are not aligned with the others. Nice to have: see *which* rules and profiles use a group, not only how many (without digging too far).
- **Port Labels**: much better, works well. Wanted: sort on the first column (shipped / Mission / replaces), like port and product.
- **Overview tutorial**: wanted far more visual: diagrams (use the palette's amber, never used so far) explaining the steps and why the tool is useful: step back over many rules and server answers (visual matrix instead of grepping text files), visual report, optimised nmap commands built with port search, every machine tested from several Sources without relaunching because something was forgotten, retests and visual comparison of Scans, diagrams in reports, collaboration on the scan method (kits), inventory by copy-paste. It must make people want to use the tool.
- New idea, out of scope: estimate the duration of a Scan (best / worst / expected) → `.scratch/scan-time-estimate/spec.md`.

2026-11-04 round 3 (same file; the Kit nav switch is gone, C is kept):
- **Scans** is now a real screen: ① **Build the scan**: pick a profile of the kit (its description shown), adjust ports (port search with "+ label this port") and the main options, see the command for a Source; a profile that differs from the saved one shows a **"Modified from broad"** bar listing the changes (+ports, −ports, options) with **Save as a new profile version…** (name `broad-v2` and a description "Variant of broad: …" prefilled; `broad` stays as it was), **Update broad** (warns when Scans were already imported with the previous version) and **Discard**; scripts for the modified profile cannot be downloaded until it is saved (Scans are tracked by profile name). ② **Run it from each Source**: Sources × profiles, ✓ when a Scan is in, a script button otherwise.
- **Auditor Kit › Scan Profiles** is a catalogue: name, **what it is for** (description, edited in place), ports (folded chips), options, Scans imported, and Open in Scans / Duplicate / Delete (inline confirmation) / + New profile. Implies an optional 4th column `description` in `scan_profiles.csv`.
- **Port Groups / Port Labels**: the first column is titled "source" and sorts (shipped, replaces, Mission); badges aligned (an app.css class collided); "used by" lists the profiles by name and the rules on hover.
- **Overview tutorial**, visual, with the palette's amber: a dark hero with a Zone graph (allowed / Finding / undeclared), the work process as six illustrated steps, "Without SegOWL" (a terminal full of greps) next to "With SegOWL" (the Zone matrix), several Sources fanning out over the whole inventory, a retest compared cell by cell, eight benefit cards (paste the inventory, build the right nmap command, nothing forgotten, same method on every audit, step back over the data, Findings not noise, retest and compare, a report that travels), then the numbered steps.

2026-11-04 verdicts, round 3, on the tutorial (the rest of round 3 had no remark):
- Audience: pentesters and auditors who know nmap, not beginners.
- The full-width hero card is liked, but its diagram did not show what the tool really draws, and was not pretty. There are two views: per Zone and per Source.
- The message is: the tool brings **rigour**, **visibility** and **quality of restitution**.
- Work process: Define the inventory → Select your Auditor Kit → Configure (optional: tune the profile) → Run on the Sources → Define the Flow Policy (optional) → matrices and diagrams, exportable per client / target selection, to put into a pentest report (the point is less the tool's own report than dropping its matrices into the pentest report). "Scripts" as a step meant nothing.
- Step by step comes too late: right after the work process, then a separate part on the advantages.
- Terminal: drop `ls | wc -l`; the interesting part is the grep and the questions that follow (which are really not allowed? any in T0? did I run every grep, find every Finding?). Matrix, several Sources, retest: good.
- Benefits: drop "paste the inventory" (an internal convenience); keep the nmap command (essential), nothing forgotten, same method (+ customise and improve it), step back over the data; the report card should say the diagrams go straight into a pentest or audit report.

Round 4 (tutorial only): hero for pentesters ("Rigour in the scans. Visibility on the flows. Quality in the report.", three pillars) with the report's **two views drawn as the report draws them** (Zone view: pastel Zone pills, edges coloured by Flow Policy status, admin ports in bold red, dashed "reachable"; Source view: dark hexagon Source, targets grouped in tinted Zone frames, multi-Interface Machine highlighted), switchable; the 6-step process (optional steps dashed) followed at once by the step-by-step; then "Why SegOWL": grep vs matrix, several Sources, retest, seven benefit cards.
