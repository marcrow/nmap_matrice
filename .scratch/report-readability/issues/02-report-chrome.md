# Report chrome: big tabs, sticky Port Group bar, section cards

Status: done
Blocked by: –
Spec: ../spec.md

## What

One `report.html`, two chromes (spec "One report.html, two chromes"). Seven big tabs in the Auditor Kit style (title, count, one-line description) in this order: Global view · Flow Policy · Pivot Machines · Per source · Per target · Scans · Diff, sticky with the Port Group bar under them. The tab is kept in the URL hash. Inside the app (`window.self !== window.top`) the report hides its own header; on its own it keeps a plain header. Port Group as chips (`all ports` then one per group, a dropdown beyond about 8), framed in brand amber with "This filter applies to every tab", an amber underline while a group is active. Every top-level section is a white card with its title; full width (no max width). Checkboxes, buttons and selects take the app styles. No Print button. The report palette uses the app variables (`app.css` `:root`).

Reference: branch `prototype/report-readability`, `segowl/render/html.py` `_tabs`, `write_html`, `_group_filter`; `segowl/assets/report.css` (`.rhead`, `.rtop`, `.bigtabs`, `.groupsel`, `.sec`); `report.js` `showTab`, embed detection, `pickGroup`.

## Acceptance

- `report.html` opened as a file and inside `/report` of the app: one header each time, the seven big tabs with their counts, the hash reopens the same tab
- the Port Group chips filter every tab and stay visible while scrolling
- no external request (offline constraint)

## Comments

**2026-11-05, done.** `render/html.py` `_tabs` (seven big tabs with counts and description), `_sec` (white card per section), `_group_filter` (chips, a `<select>` beyond 8 groups), `write_html` (plain header `.rhead`, sticky `.rtop`). The palette is `app.css` `:root`, prepended to `report.css` at generation (one source). `report.js`: `showTab` keeps the tab in the hash, `pickGroup`; the embed class is set by an inline script right after `<body>` (no header flash in the app). Pivot Machines and Per target hold the former Global view sections until tickets 06 and 07; Scans holds the former Anomalies tab. Checked headless on the demo, standalone (`#scans` reopens Scans) and in `/report` of the app (no own header). Test: `test_report_has_the_seven_big_tabs_and_loads_nothing_from_the_network`.
