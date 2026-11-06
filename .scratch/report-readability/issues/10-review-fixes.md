# Review fixes after trying the report on mission-lab

Status: done
Blocked by: 05, 07, 08
Spec: ../spec.md

## What

User feedback, 2026-11-06, after ticket 09:

- Zone palette: the orchid reads as red / pink, and 5 hues are not enough.
- Pivot Machines:
  - the "Zones facing the Source" and "Zones on both sides" layouts change nothing, and "Zones around the Source" swaps In and Out;
  - with several Interfaces the edges tangle;
  - a rebound that adds nothing looks like one that adds;
  - the count of Interfaces newly reached is no longer on the edge (it was in the Mermaid prototype);
  - "bypass" in red is unclear;
  - "its other Zones" is not pretty.
- Right-click works only on a Zone frame's background, and not on the Machine in the centre.
- Clicks sometimes land off the pointer.
- The Zone arrangement does not start on auto.

## Comments

**2026-11-06, done.**

- **Zone palette** (`common.py` `ZONE_COLORS`, and the app editors): 8 hues, dark and light variants, no red, amber or green. Measured on all pairs: OKLab ×100 ≥ 15.4 in normal vision, ≥ 8.7 for deutan / protan readers. Beyond 8 Zones the hues repeat. The app Zone chips now use the pale fill, the hue and the dark text, like the report.
- **Pivot diagram**:
  - frames are now "Reached from" and "Rebound into", and each card has its Zone's colour bar;
  - a Source Zone reaching several Interfaces has one edge to the Machine ("reaches n of its Interfaces"); the detail is in the hover and the In table;
  - Out edges carry "+n" (amber dashed), "bypass +n" (amber, thick) or nothing (grey dotted, the rebound adds nothing);
  - red is no longer used: a rebound is not a Flow Policy decision;
  - the `.byp` badge is amber.
- **Machine centre** (Pivot and Per target):
  - nodes are ordered by the mean rank of the Interfaces they link to, so fewer edges cross;
  - edges leaving one Interface start apart;
  - the Layout menu only offers the layouts that change the diagram (none on Pivot, where the sides are pinned);
  - right-click on the Machine puts its Interfaces in a row (Zones above and below) or back in a column.
- **Right-click** on any node of a Zone arranges that Zone.
- **Click offset**: the diagram re-reads its box (`cy.resize()`) when the pointer comes in.
- **Zone arrangement** is no longer remembered: every load starts on auto.
- Test: `test_rebound_gain_bypass_nothing_new_and_partial` also checks the diagram edges.
- Checked headless on demo and mission-lab: every tab, every diagram, a right-click and a Port Group switch, no JS error.

**2026-11-06, second pass (user feedback).**

The user's points:
- one edge per Source Zone to the Machine loses which Interface and which ports;
- the Options radios show nothing checked;
- in "one per Zone" mode the Out arrows point at the Machine and only link to the Machine;
- "Rebound into" should read like "gives access to";
- two rows with ports on the edges overlap the previous row;
- the right-click menu should look like Windows 11 snap layouts (icons; auto, one / two columns, one / two rows, a square, maybe a circle);
- a square for the Machine's Interfaces.

Done:
- **Reached from**: one card per Interface reached, listing each Source Zone with its Flow Policy icon and ports (ports in a column). The card has one edge to its Interface, in the Interfaces' order, so no edges cross.
- **Out frame**: renamed "Leads to".
- **"One per Zone" edges**: one per Zone *and* centre end (each Interface of a Machine), with the link's own direction. Out edges leave the Machine.
- **Options radios**: their names are per diagram (one shared name made every diagram's radios one group, so only one was checked). `syncPanels` keeps every panel showing the current options.
- **Zone arrangement**:
  - new "square" (⌈√n⌉ lines, either side);
  - between lines, room for the far line's port tags.
- **Right-click menu**: icon tiles (snap layouts). Zone: auto, one / two columns, one / two rows, square. Machine: one column, one row.

Not done, open:
- **A square of Interfaces for the Machine**: with Zones on both sides, the edges of the inner Interfaces would cross the outer ones.
- **Round Zone frames**: a bonus.
