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

**2026-11-06, third pass (user feedback).**

The user's points:
- at some zoom levels, bold text goes blurry;
- the gaps between columns are too wide: they should depend on that column's ports, and ports should wrap after a set length;
- try round Zones.

Done:
- **Sharp text**: Cytoscape keeps a bitmap of each node per zoom level (a power of 2) and builds a level by shrinking the one above. After a zoom in and out, the card text (SVG images) goes soft. The renderer's texture caches are now off (`crisp`, a patch on Cytoscape 3.34 private API, guarded): every node is drawn from its SVG at the current zoom.
- **Spacing and wrapping**:
  - each line is as wide as its widest node;
  - the gap before a line holds only that line's port tags;
  - tags beside a node wrap at 100 px.
- **Round Zone** ("circle" in the right-click menu and in Options):
  - a rounded frame, the nodes on the half away from the Source, one per height (one per column above or below);
  - edges come in at right angles through the empty half and cross nothing;
  - a parent node cannot be an ellipse in Cytoscape, so the frame is a rounded rectangle (`corner-radius`) kept whole by `min-width` / `min-height` with a bias.
- **Frame-style bug**: the frame style is set when the side is chosen, no longer while every side is being tried. The last side tried used to win.

**2026-11-06, fourth pass (user feedback).**

The user's points:
- the round Zone is too far from its nodes and takes too much room; the user prefers a "cloud" inside a contour that follows it;
- some texts are still a little blurry;
- "one per Zone" should switch the ports into the nodes;
- Pivot: "Leads to" ended up on the left, but it must stay on the right, with "Reached from" on the left.

Done:
- **Round Zone ("circle")**:
  - the square's staggered lines inside a frame rounded to an oval;
  - margin = 0.22 of the short side, so the corner nodes stay inside;
  - the half-moon version and its `min-width` bias are gone.
- **Blur**: the label caches are off as well (Zone and Machine titles, "+3" on edges). A test showed that Chrome redraws an SVG image at the size it is drawn, so cards drawn directly are sharp at any intrinsic size.
- **Options**: "one per Zone" sets the ports "in the nodes"; "on the edges" sets "one per Interface". The panels show the change.
- **Pivot sides**:
  - a diagram's own sides (`D.sides`) now always hold, whatever the arrangement; before, "one row" / "two rows" dropped them and the layout could swap them;
  - the Zone checkboxes follow the pinned sides (Reached from first);
  - checked headless: every arrangement, every Pivot Machine of demo and mission-lab.

**2026-11-06, fifth pass (user feedback).**

The user asked:
- to keep the half moon as a shape of its own;
- for icons on the Layout choice and in Zone arrangement, as in the right-click menu.

Done:
- **Half moon** (`arc`, `arcBlock`):
  - the nodes on an arc bulging away from the Source, one per height (one per column above or below);
  - an oval frame around the arc only, not a whole circle;
  - edges at right angles, crossing no node;
  - as long as one row / one column.
- **`FREE`**: the arrangements that fit on any side (auto, square, circle, half moon).
- **Layout and Zone arrangement**: icon tiles (`tiles`), like the right-click menu:
  - Layout: the Source in navy, with the Zone frames facing it, on both sides, or around it;
  - `syncPanels` marks the current tile in every diagram.
- Checked headless: every tile clicked, Pivot sides with every arrangement, the sweep on demo and mission-lab.
