# Report chrome: big tabs, sticky Port Group bar, section cards

Status: ready-for-agent
Blocked by: –
Spec: ../spec.md

## What

One `report.html`, two chromes (spec "One report.html, two chromes"). Seven big tabs in the Auditor Kit style (title, count, one-line description) in this order: Global view · Flow Policy · Pivot Machines · Per source · Per target · Scans · Diff, sticky with the Port Group bar under them. The tab is kept in the URL hash. Inside the app (`window.self !== window.top`) the report hides its own header; on its own it keeps a plain header. Port Group as chips (`all ports` then one per group, a dropdown beyond about 8), framed in brand amber with "This filter applies to every tab", an amber underline while a group is active. Every top-level section is a white card with its title; full width (no max width). Checkboxes, buttons and selects take the app styles. No Print button. The report palette uses the app variables (`app.css` `:root`).

Reference: branch `prototype/report-readability`, `segowl/render/html.py` `_tabs`, `write_html`, `_group_filter`; `segowl/assets/report.css` (`.rhead`, `.rtop`, `.bigtabs`, `.groupsel`, `.sec`); `report.js` `showTab`, embed detection, `pickGroup`.

## Acceptance

- `report.html` opened as a file and inside `/report` of the app: one header each time, the seven big tabs with their counts, the hash reopens the same tab
- the Port Group chips filter every tab and stay visible while scrolling
- no external request (offline constraint)
