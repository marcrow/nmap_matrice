# App Overview: same palette and legend wording as the report

Status: done
Blocked by: 03, 05
Spec: ../spec.md

## What

The app Overview (`overview.html`) takes the report's palette (Zone and Machine colours without red / amber / green, Flow Policy colours with icons) and the legend wording of tickets 03 and 05. The static tutorial SVGs (`segowl/assets/tutorial/`) and the README follow if their Zone colours changed.

## Acceptance

- no Zone or Machine is drawn red, amber or green anywhere in the app, the report or the README

## Comments

**2026-11-05, done.** Overview (`overview.html`): legend in the report's wording (line + icon per Flow Policy status, slate dashed "reachable, no open port", "port numbers: bold = admin port, red = denied by the Flow Policy"); `app.css` gets the `.pg` icons. Tutorial SVGs, shown by the Overview and the README: `zone-view.svg` and `source-view.svg` take the report's Zone palette in the order the report assigns it (Zones sorted by name), slate dashed reachable edges, admin ports bold and only denied ports red, dc-01 (a Machine) in the first Machine hue, the Source in navy; `several-sources.svg` rows take the same Zone hues. `zone-matrix.svg` and `retest.svg` only use the Flow Policy colours on cells: unchanged. Beyond the ticket, the Inventory and Flow Policy editors (`app_inventory.js`, `app_policy.js`) coloured their Zone chips from a hashed list holding red, green and orange: they now use the report's hues (dark tone, white text) in Zone name order, so a Zone has the same hue in the app and in the report. README: legend line and Port Group paragraph reworded. Checked headless in the app (1366 wide): Overview, Inventory, Flow Policy; no old Zone colour left in `segowl/` (grep).
