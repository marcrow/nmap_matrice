# Pivot Machines: cards with what the rebound adds

Status: done
Blocked by: 05
Spec: ../spec.md

## What

Rewrite the Pivot Machines tab as cards (spec "Pivot Machine cards"): one explanation at the top (dark on white, not exhaustive); per Machine its name, Zone tags, bypass count; a Cytoscape diagram In (Source Zones → the Interface they reach, ports) and Out (each other Interface → its Zone, red dashed when bypass, amber dashed otherwise, as in the prototype: the user keeps amber for the rebound); the In table; the Out table listing every other Zone with, per Source Zone landing there, the Interfaces the rebound adds compared with what it reaches directly. Bypass cards first; a Machine whose rebound adds nothing folded to one line.

Reference: branch `prototype/report-readability`, `html.py` `_pivots_html`, `_pivots_tab`; `mermaid.py` `mermaid_pivot` (the Mermaid shape to port).

## Acceptance

- demo: fw-01 shows 2 bypasses (dmz → users, admin → audit), backup-01 leads to servers (+1) and admin (+3)
- the gain computation has tests (bypass, nothing new, partial)

## Comments

**2026-11-05, done.** The gain is computed in `analysis.py` (`rebounds` → `Rebound(into, through, others, gain)`, `Rebound.bypass`), the cards in `html.py` `_pivots_html` (sorted bypasses first, then gain; a Machine whose rebound adds nothing is folded and drawn when unfolded), the explanation and the rebound legend in `_pivots_tab`. Diagram (`_pivot_graph`, Cytoscape, same code as Per target): the Machine frame in the centre, "Source Zones" frame on the left (one card per Source Zone, links to the Interfaces its Sources reach, ports merged with the worst Flow Policy mark), "its other Zones" frame on the right (one card per rebound, dashed amber, red when bypass, "+n not reached directly" / "bypass, all of it" / "nothing new"); frames pinned to their side by the diagram (`D.sides`). Card nodes accept `sub`, `note`, `noteCol` and `tip`; rebound links are kept by the Port Group filter (`keep`). The Mermaid `mermaid_pivot` of the prototype is not ported (no Mermaid in the report from ticket 08). Checked headless on the demo: fw-01 "2 bypass" (into audit from admin and dmz, into users from dmz), backup-01 → servers +1, admin +3. Test: `test_rebound_gain_bypass_nothing_new_and_partial`.
