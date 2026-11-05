# Per source diagram in Cytoscape.js

Status: ready-for-agent
Blocked by: 02
Spec: ../spec.md

## What

Replace the Per source Mermaid diagram by Cytoscape.js (ADR-0005), from the validated POC `prototype_report/cytoscape_poc/` (branch `prototype/report-readability`, `page.html`, `build.py`, `vendor/`): Cytoscape 3.34.4 vendored and inlined (licence header kept), no fcose. Python emits the graph as JSON; the layout code lives in a report asset.

- Layout presets: **Zones facing the Source** (default), Zones on both sides, Zones around the Source; right-angle edges; deterministic.
- Zone arrangement: right-click on a Zone frame offers one column, two columns, one row, two rows, auto; the same choice for every Zone in the options panel; auto = the density rule of the spec.
- Nodes: white cards (name, IP, ports with bold admin / red denied, Flow Policy icon); "reachable" / "alive" labels; Source as a navy card with a cyan bar. Options: ports in the nodes (default) or on the edges, one edge per Interface (default) or per Zone, Machine colour bar (on), dotted Machine links (off), Zone checkboxes. Hover: tooltip and cyan ring on the Machine's other Interfaces. Reset layout, Export PNG (`cy.png({full:true, scale:2})`).
- Palette: Zone and Machine colours without red / amber / green, in `render/common.py` so the app follows. **The POC's Zone tints are too close to tell apart** (user, 2026-11-05): the Zones must be distinguishable at a glance. Give each Zone a distinct, validated hue on its border and title (a coloured title band or chip, like the matrix zone chips), keep the fill pale; run the dataviz validator on the border colours (`node validate_palette.js "<hex,...>" --mode light`) and fix every FAIL; with more Zones than passing hues, the title still names the Zone.
- The Port Group filter applies (the diagram shows only the group's OPEN flows).

## Acceptance

- the demo's three Sources each fit a 1600×1100 window readable without zoom, no edge under a node, same layout on every reload
- the 5 demo Zones are told apart by colour alone (validator passes on their border colours)
- jump-dmz shows its Findings at once (red edges, ✕, red 443)
- right-click on servers → "one row" redraws only that Zone's arrangement
- works offline, standalone and inside the app; the report grows by about 0.8 MB at most
