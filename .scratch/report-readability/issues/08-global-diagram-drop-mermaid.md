# Global zone diagram in Cytoscape, Mermaid out of the report

Status: done
Blocked by: 05, 06, 07
Spec: ../spec.md

## What

Draw the Global view zone → zone diagram in Cytoscape with the shared look, then remove `mermaid.min.js` from the report (about 3.3 MB less) and its loading code from `report.js`. The `.mmd` text exports written by `cli.py` (`segmentation.mmd`, per Source) stay: they need no JS and auditors paste them in documents.

## Acceptance

- `report.html` contains no Mermaid code and every diagram still renders offline
- the `.mmd` files are still written and their tests pass

## Comments

**2026-11-05, done.** Global view: `html.py` `_zone_graph` (one node per Zone with its Interface count, one link per Zone pair passing, each open port with the worst Flow Policy status it has between the two Zones) drawn by `report_graph.js` `drawZones`: Zones on a circle (Cytoscape `circle`, sorted, deterministic), bezier edges (the two edges of a pair bend apart, a loop inside a Zone points outwards), ports in a tag past the middle of the edge towards its target (admin bold, denied red; never onto the target), reachable / alive pairs as a dashed edge with their count; hover an edge for its pairs, Reset layout and Export PNG as elsewhere; Port Group filter applied. Mermaid is out of the report: `segowl/assets/mermaid.min.js` deleted (only the report used it), `_mermaid_script`, `_diagram` and the CDN fallback removed from `html.py`, the Mermaid code removed from `report.js` (`renderVisible` now only draws the Cytoscape diagrams). `cli.py` still writes `segmentation.mmd` and `mermaid/<ip>.mmd` (snapshot tests unchanged). The demo `report.html` went from 4.3 MB to 1.3 MB. README, `CODING_STANDARDS.md` and `segowl/__init__.py` no longer mention the Mermaid bundle. Checked headless, standalone and in the app (1366×768); `.gcy` min-height 560 px so a laptop keeps legible text (the page scrolls). Test: `test_report_has_the_seven_big_tabs_and_loads_nothing_from_the_network` also asserts no Mermaid in the report.
