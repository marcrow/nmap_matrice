# Pivot Machines: cards with what the rebound adds

Status: ready-for-agent
Blocked by: 05
Spec: ../spec.md

## What

Rewrite the Pivot Machines tab as cards (spec "Pivot Machine cards"): one explanation at the top (dark on white, not exhaustive); per Machine its name, Zone tags, bypass count; a Cytoscape diagram In (Source Zones → the Interface they reach, ports) and Out (each other Interface → its Zone, red dashed when bypass, amber dashed otherwise, as in the prototype: the user keeps amber for the rebound); the In table; the Out table listing every other Zone with, per Source Zone landing there, the Interfaces the rebound adds compared with what it reaches directly. Bypass cards first; a Machine whose rebound adds nothing folded to one line.

Reference: branch `prototype/report-readability`, `html.py` `_pivots_html`, `_pivots_tab`; `mermaid.py` `mermaid_pivot` (the Mermaid shape to port).

## Acceptance

- demo: fw-01 shows 2 bypasses (dmz → users, admin → audit), backup-01 leads to servers (+1) and admin (+3)
- the gain computation has tests (bypass, nothing new, partial)
