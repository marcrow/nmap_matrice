# Prototype: report chrome, palette, matrices, legends, Pivot Machines, Per target

Status: done
Blocked by: –
Spec: ../spec.md

## What

Throwaway prototype on the real renderers, generated on the demo Mission (`demo/`: 3 Sources, 41 Interfaces, 10 Findings), kept off the main line (branch `prototype/report-readability`, worktree `../nmap_matrice-proto-report`). Shows every decision of the spec so the user can judge it on real data before tickets are sliced.

## Acceptance

- the user clicks through every tab, standalone and inside the app, and picks a cell variant
- the verdicts are recorded in this ticket's Comments

## Comments

2026-11-05: prototype ready. Open `../nmap_matrice-proto-report/prototype_report/report.html` (standalone) or `in_app.html` (inside a mock of the app) by double-click. The bottom bar switches:
- **Cells A · shaded tiles (verdict first)**: tile = ordinal navy scale (OPEN darkest → BLOCKED near white, UNSEEN hatched); the Flow Policy is a round badge ✕ / ? / ✓ plus a bottom bar in red / amber / green. Admin ports bold (underlined amber on dark tiles).
- **Cells B · status tiles (Flow Policy first)**: neutral tiles tinted by the Flow Policy (red / amber / green) with the same badge; the verdict is a navy dot in the corner.
- **standalone / inside the app**: the same `report.html`; inside the app it drops its own header.

Also shown: seven big tabs with counts (Global, Flow Policy, Pivot Machines, Per source, Per target, Scans, Diff), sticky with the Port Group filter and a Print / PDF button (draws every diagram, unfolds every detail, one section per page); one legend per view; ports in edge labels red when denied, bold when admin; edges without a Flow Policy orange (cross-zone) / grey (same zone); Flow Policy counters as tiles linking to their table; per-column filters on every table; one diagram per Pivot Machine with the detail folded; Per target (search by name, IP or zone, diagram of the Sources reaching it, table); Target details rows that unfold per port (state per Scan, Port Label); Anomalies inside Scans, Sources without scan = declared Sources only.

Not in the prototype: the app Overview palette (follows the validated variant), Mermaid theme beyond the label background.

Awaiting the user's verdict.

2026-11-05 verdicts, round 1:
- **Cells: B** (status tiles). A is far too heavy: too much colour. Defect: every port of an OPEN cell is bold (B's CSS bolds the whole cell), so one admin port no longer stands out; the diagrams get it right.
- **BLOCKED and UNSEEN look the same** in the legend and the cells.
- **Big tabs inside the app: good.** Flow Policy counter tiles: liked.
- **Per-column filters: a regression.** Wanted instead: one search field per table, and sort by clicking a column header (again: reverse order). No autocompletion in the filters either.
- **Pivot Machines: hard to read.** It is unclear what the diagram means and why a Machine "leads to" a Zone (e.g. monitor-01, which has no Scan: it spans admin and servers in the inventory). "one hop onward" says little; the idea is a rebound: whoever holds this Machine reaches its other Zones. Needs a real explanation.
- **Width:** the 1500px cap leaves an empty strip on the right, not even centred; diagrams must use the full width.
- **Per source:** fine; Zone frames get very tall (a small group at the top, another at the bottom: Mermaid layout); firewalls on the same row is fine. Export SVG / PNG are too far on the right.
- **Per target misses the Machine:** searching fw-01 gives one Interface, never the Machine as a whole. And the old Exposure per target overview is lost: wanted back as a big table, folded, searchable.
- **Print / PDF: the rendering is ugly, remove the button** rather than ship it.
- **Port Group selector not visible enough.** More generally, important elements do not stand out and sections are not delimited well (better than before, still blended).

2026-11-05 round 2 (same files, the cell switch is gone, B is kept; answers to the round-2 questions all "yes", plus: a Pivot card must show *why* the Machine leads into each Zone, the out side, not only the in side):
- **Cells**: neutral tiles tinted by the Flow Policy with its icon, navy dot for the verdict; only admin ports bold; BLOCKED filled grey ×, UNSEEN empty dashed –.
- **Pivot Machines**: a plain sentence (its Interfaces, which Source Zones reach it OPEN, the rebound); diagram In (Source Zone → Interface reached, ports) and Out (other Interface → its Zone, red dashed if bypass, amber otherwise); two tables: *In: who reaches it* and *Out: where it leads* (through which Interface, same segment as which Interfaces, if the Machine is a Source what it was seen reaching, compared with the direct path: "bypass for dmz" or "audit already reaches 5 / 8 directly"). Cards with a bypass first; a Machine every Source Zone already reaches in each of its Zones (fw-01) is folded to one line. On the demo there is no bypass: every rebound leads into a Zone the Source Zone already reaches.
- **Per target per Machine**: search by name, IP or Zone; a Machine frame with all its Interfaces; table with an Interface column. Folded **All targets** table (target × Source) above, searchable and sortable.
- **Tables**: one search field each, sort by clicking a header (again: reverse).
- **Port Group chips** on their own row under the big tabs, framed in cyan; while a group is active the bar gets a cyan underline.
- **Sections as white cards**, full width, Print removed, Export SVG / PNG next to the Zone filters.
- **Per source**: without the dotted links between a Machine's Interfaces, the Zone frames no longer stretch (the Machine colour still marks multi-Interface Machines); the diagram is a tall single column on a large Source.

2026-11-05 verdicts, round 2:
- **Tables: validated** (one search field, sort on header click).
- **Port Group chips: better.** Defect: they do not filter Per target (Per source works).
- **Per source: worse than before.** Without the dotted links, Mermaid stacks the Zone frames in one column next to the Source: very tall diagrams that must be scrolled. The older side-by-side frames were preferred, even with some tall frames. Idea raised: the Source in the centre, Zones around it (mind map), if it stays readable.
- **Per target**: fw-01 gets hard to read, acceptable. Wanted: per Machine, the open ports of each Interface merged across Sources, with which Source sees what (a diff of what shows from where).
- **Pivot cards: the sentence is not readable and not useful**; keep the Machine name. The diagram with all its Interfaces is what makes it clear. In / Out: fine. The tab hint is grey text on light blue: too low contrast. "compared with the direct path" not understood. backup-01 now only leads to admin while round 1 showed more: the round 2 rule drops a Zone that every Source Zone already reaches on the Machine itself (servers, reached on 10.30.0.70 by admin and audit).
- **Host matrix legend incomplete**: the hatched tiles (same Machine) and the filled × tiles are not in the legend, the Flow Policy tints are not shown as tiles, and the `o` / `~` marks in the cells are not explained.
- **Machine**: today one inventory name = one Machine. In reality the same name may be two machines, and one machine may carry two names (one per network). Keep this rule for now, but say it in the glossary.

Round 3 answers, all "yes": Per source and Per target with the Source on top and the Zone frames side by side, Interfaces on several columns inside a frame (back to the older layout if not better); Pivot card = Machine name, diagram, In table, Out table listing every other Zone with what the rebound adds per Source Zone ("+3: ilo-02, …", "nothing new", bypass in red), one explanation at the top of the tab in dark text on white; matrix legend tiles drawn exactly like the cells, hatched = same Machine, `o` / `~` replaced by words; Per target: per Interface, open ports × Sources (open / blocked / not tested) with the Port Label, total for the Machine; Port Group filter applies to Per target; Machine = inventory name (glossary updated, with the warning). Plus: the Port Group bar in the brand amber, with "This filter applies to every tab". Machine identity guessing traced in `.scratch/machine-identity/`.

2026-11-05 round 3 (same files):
- **Per source / Per target**: top-down, the Source(s) on top, Zone frames side by side, a frame's Interfaces in columns of 6. The auditor's diagram fits one screen (scaled down: small text on 38 targets). fw-01 in Per target reads much better (Sources above, its 5 Interfaces below).
- **Pivot cards**: name + Zone tags + bypass count; diagram; In; Out lists every other Zone with, per Source Zone, the Interfaces the rebound adds ("+4: bastion-01, …", "nothing new, already reaches all 6", "bypass +9, all of it"). A Machine where the rebound adds nothing is folded. The explanation sits once at the top, dark on white, with the not-exhaustive warning. On the demo fw-01 now shows 2 bypasses (dmz reaches its users Interface, a Finding, and reaches no workstation directly) and backup-01 leads to servers again (+1) and admin (+3).
- **Matrix legend**: every item is a tile drawn like a cell (dot, mark, tint, icon), plus same Machine (hatched) and Scans disagree; `o` / `~` now read `closed` / `ping`.
- **Per target**: per Interface, open ports × Sources (open with its Flow Policy icon / not open / not tested) and the Port Label; open-port total for the Machine in the title; the Port Group filters the diagram, the tables and these rows.
- **Port Group bar** in brand amber, "This filter applies to every tab."

Awaiting the user's verdict on round 3.

2026-11-05 verdicts, round 3:
- **Pivot cards: liked**, especially the per-line gain. Readability still suffers as soon as there are many Machines and links (Mermaid); no filter on Pivot Machines.
- **Top-down layout (Source / target on top): rejected**, back to the original Per source layout (Zone frames side by side, dotted links between a Machine's Interfaces). The recurring problem is Mermaid itself: a research on other graph libraries (offline, compound Zones, more flexible) is running, see `../graph-library.md`; a POC may follow, else Mermaid as before.
- **Bug**: the matrix tiles jump when leaving "all ports" (the filter rewrote the cells).
- **Legends: better**; the sample port numbers in the tiles were confusing.
- **Per target**: the per-Interface tables are nice, and nicer than they looked on fw-01 (many Interfaces, few ports). Wanted: copy the open ports of an Interface, merged across Sources, with a button, to rescan just those.

Round 3b (same files): original Per source / Per target layout back; the Port Group filter now filters inside the port text (icon, bold admin ports and tile kept, column widths frozen); legend tiles read "ports" instead of sample numbers, diagram legend "port numbers on the arrows: bold = admin, red = denied"; a **Copy its open ports** button per Interface and **Copy all the Machine's open ports** (nmap -p format: `22,443`, or `T:22,U:53` with UDP).

2026-11-05 round 3b verdict: "plutôt bien, globalement". Bug: in the per-Interface port tables a long Port Label (ad-01) overflowed the table, and a narrower window forced a scroll. Fixed: the tables take their column width and the Port Label wraps (checked at 900px). Waiting for the graph library research before closing the prototype.

2026-11-05 step 0 of `../graph-library.md` (same files, two toggles in the bottom bar, `?layout=elk` and `?ports=nodes`; Per source, auditor):
- **Ports in the nodes, default layout**: labels readable, edges keep their colours, but the same tall layout.
- **ELK layout (built into the vendored Mermaid 10.9.8)**: the whole Source fits one screen, the Zones side by side. But Mermaid 10's ELK renderer drops `linkStyle` and subgraph `style`: every edge grey, every Zone frame the same blue, the dotted Machine links gone; the edges become a bundle of orthogonal wires.
- **ELK + ports in the nodes + the Flow Policy icon in the node** (✕ / ? / ✓): the most compact and readable nodes, the Flow Policy survives on the node; the wires carry no information any more.
Mermaid 12 (5.5 MB, `mergeEdges`) not tried.

2026-11-05 **Cytoscape POC** (`../graph-library.md`, candidate 1), commit `c46ee1e` on the prototype branch. Open `../nmap_matrice-proto-report/prototype_report/cytoscape_poc/poc.html` by double-click (offline; rebuild: `python prototype_report/cytoscape_poc/build.py` from the worktree root). Per source only, demo Mission, nothing else of the report touched.
- **What it is**: Cytoscape.js 3.34.4 + fcose 2.2.0 (with layout-base 2.0.1, cose-base 2.2.0), all MIT, inlined: the page weighs **794 KB** (Mermaid 10.9.8 alone is 3.34 MB). Python emits JSON only (Interfaces, verdict, ports with admin / Flow Policy status, Zone and Machine colours from `zone_palette` / `machine_palette`); ~220 lines of JS draw it.
- **Bar**: Source picker (default auditor); Layout *Zones around the Source* (default) / *fcose*; Edges *one per Interface* / *one per Zone*; Ports *in the nodes* / *on the edges*; Machine *colour* / *dotted link* (hover always rings the other Interfaces of the Machine in amber); Reset layout; Export PNG; one checkbox per Zone (hides the Zone and its edges). Hover tooltip: Interface, Zone, type, Machine (how many of its Interfaces are reached), verdict, each open port with its Flow Policy mark, Flow Policy status. Legend = the report's `_diagram_legend` + node icon, Machine colour, dotted link, per-Zone edge.
- **Nodes**: each target Interface is drawn as a small SVG image (Cytoscape labels are plain text, no bold or red inside one label): ✕ / ? / ✓ icon, name bold, IP grey, ports with admin bold and denied red, "reachable" / "alive" in italics. Source = navy hexagon, cyan border.
- **Observed, Zones around the Source** (each Zone a grid of its Interfaces, the frames on an ellipse around the Source, the tightest ring without overlap that best fills the canvas; deterministic by construction): the auditor's 39 targets fit one 1600×1100 screen at zoom 0.92, text readable without zooming; both dimensions used; no stretched frame; no overlapping labels. jump-dmz: red edges and ✕ icons, red 443 on the admin Interfaces stand out at once. Weak point: an edge passes under the nodes of its Zone that sit in front of its target, so it seems to start from that node (jump-dmz: a red line looks like backup-01 → ilo-01). Also an edge arrowhead can land on the Zone title (audit).
- **Observed, one edge per Zone**: the cleanest picture (5 thick arrows, the nodes carry ports and status); removes the under-node problem; loses the per-Interface dashed line, which the node's "reachable" already says.
- **Observed, fcose**: both dimensions used and frames not stretched, but a star of satellites with empty corners: zoom 0.59 on the auditor, text too small without zooming; Interfaces scattered inside the frames. Not deterministic by itself (3 reloads, 3 layouts); deterministic with a seeded `Math.random` during the layout (checked). Dropped after trying: `cose` (Zone frames overlap) and fcose started from the ring (no gain over the ring).
- **Ports on the edges**: labels near the target collide with the nodes of the same Zone and cannot be bold or red (canvas text: denied marked `443✕`); hidden below a zoom level. In the nodes reads better.
- **Machine ties**: colour reads at a glance across Zones (fw-01 blue in 5 Zones); dotted links add long lines across the diagram (excluded from the layout so they no longer stretch frames); the hover ring is the clearest but does not show in a PNG.
- **Exports**: `cy.png({full:true, scale:2})` includes the SVG node images, sharp (checked). SVG: not built in; the GPL cytoscape-svg extension was not added. A home-made SVG would write the same node images (already SVG) plus frames and straight edges from `cy` positions and styles: bounded, est. ~80-120 lines.
- **Speed**: first draw (elements + layout) ~100 ms with the ring, ~150 ms with fcose (headless Chrome, auditor).
- Not tried: cytoscape-elk, bubble sets, inside the app iframe.

Awaiting the user's verdict.

2026-11-05 verdict on the Cytoscape POC: **adopted** ("on va plutôt partir là-dessus"). Liked: the data is far more condensed, hover rings the other Interfaces of the Machine (web-01 in two Zones), new interactions; PNG is enough, no SVG needed; fcose no better (worse). To improve: a more sober look (the POC looks younger, less serious than the Mermaid diagrams); a nicer Source shape than the hexagon; Zones more rectangular (limit columns), more layout presets (Source on the left, Zones above / below), edges arriving from the side facing the Source (dragging servers into one or two columns made even ports-on-edges readable); look for existing community layouts; ports on the edges kept as an option; a tidy options panel; dotted Machine links optional; **never red for a Zone or a Machine** (backup-01 drawn red in its Machine colour was read as a Finding): red / amber / green stay reserved for the Flow Policy. POC round 2 delegated.

2026-11-05 **Cytoscape POC round 2** (user verdict on round 1: Cytoscape adopted; PNG enough; more sober; a nicer Source; better layouts; ports on the edges usable; tidy remembered options; no red for Zones or Machines). Commit `15bb68c`, same file `../nmap_matrice-proto-report/prototype_report/cytoscape_poc/poc.html` (804 KB, offline).
- **Default layout "Zones facing the Source (best fit)"** (hand-made, ~60 lines): each Zone frame turns one side to the Source: stacks on its right and left (nodes in columns), rows above and below it (nodes in rows), the rows outside the stacks. Every assignment of Zones to sides is tried, the one that fills the canvas best is kept (deterministic). Columns per Zone: 1 up to 8 Interfaces, 2 up to 16, 3 beyond; rows: 1 up to 6, 2 up to 12, 3 beyond; with 2+ lines the far line is staggered so its edges pass between the nodes of the near one. Edges at right angles: one trunk from the Source per side, a bus just outside each frame, one drop per Interface; no edge passes under a node; Findings drawn on top. Observed: auditor (39 targets) and jump-dmz fit one 1600×1100 screen at zoom 1.24 / 1.37, text read without zooming; bastion-01 the same. The bus mixes the colours where edges share it; the drop and the node icon carry the status.
- **Other layouts in the menu**: "Zones on both sides of the Source" (the arrangement the user dragged by hand: tall columns left and right; auditor at zoom 0.69); "Zones around the Source" (the round 1 ring with rectangular Zones: straight edges still pass under nodes); fcose (seeded, as round 1).
- **Edges**: one per Interface or one per Zone (per Zone + right angles gives the cleanest picture: 5 arrows); right angles or straight.
- **Ports on the edges**: a small tag on each edge just before its target, same marks as in the node (bold admin, red denied), border in the edge colour; Zones then use 1 column or 1 row, tags under the nodes in rows. jump-dmz reads well; the auditor fits but small (many tags).
- **Style**: nodes are SVG cards (white, 1px border, radius 3, name navy 600, IP slate, ports ink, status icon); Zone frames tinted, 1px border, radius 4, title "zone · count"; the Source is a navy card with a cyan bar and a "SOURCE" caption; hover rings the Machine's other Interfaces in cyan (amber is the Flow Policy's).
- **Palette (POC-local, `build.py`)**: no red, amber or green for Zones or Machines. Zones (fill / stroke / title), cyclic: blue `#f1f7ff/#6388b9/#15365d`, teal `#edfafb/#3b959e/#004049`, violet `#f7f5ff/#8a7cb4/#392b5a`, slate `#f4f7fa/#798898/#2b3743`, plum `#fcf4fc/#a074a3/#49254c`, sky `#eef9ff/#4a90b0/#003c56`, indigo `#f4f6ff/#7782ba/#2a305e`. The dataviz validator fails them as categorical colours (sober tints of cool hues are too close): the title names the Zone, the tint only helps. Machines: a 4px bar and border in `#3a4e9d` indigo, `#a35ec1` purple, `#48a5c7` steel cyan, `#bb9af4` lavender: the validator passes them on all pairs (normal vision ΔE 15.7; CVD 6.7 and contrast below 3:1 are warnings, covered by the name in each node). A search found no 5th cool hue that passes: beyond 4 Machines the colours repeat (hover ring and tooltip disambiguate).
- **Options panel** "Options" (folded by default): Edges, Ports, Machine (colour on, dotted link off), Zones (checkboxes); the Layout menu, Reset layout and Export PNG stay in the top bar; everything remembered per viewer in localStorage (try/catch).
- **Community layouts tried** (same data, auditor): ELK layered through cytoscape-elk (elkjs 0.9.3, EPL): one very tall column, zoom 0.24, the star problem again; ELK stress and rectpacking with `INCLUDE_CHILDREN`: Zones side by side as columns but edges cross other Zones and nodes; cola (cytoscape-cola 2.5.1 + WebCola, MIT): Zones stacked, edges through nodes, 1.2 s. ELK adds 1.6 MB. None kept (rebuild with them: `build.py --out X trial/*.js`). Not tried, with the reason: cise (no compound nodes, circles of clusters), avsdf (one circle), spread / euler (no compound support), klay (superseded by ELK).
- First draw ~70-90 ms with the default layout.

Awaiting the user's verdict.

2026-11-05 verdict on Cytoscape POC round 2: **validated** ("c'est bien ce que tu proposes"). Liked: right angles, the orientations, the Machine colour (shows Machines spanning Zones: keep the option). Zone tints sometimes hard to see. fcose off-topic: dropped. New wish: right-click on a Zone to change its arrangement (one column, several columns, one row…), else the same choice in the options for every Zone, or an automatic rule picking the best density. Spec updated; implementation sliced into `02`–`09`. Prototype kept on branch `prototype/report-readability` (`prototype_report/`, `prototype_report/cytoscape_poc/`).
