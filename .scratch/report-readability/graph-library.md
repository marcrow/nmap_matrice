# Graph library to replace Mermaid in report.html?

Research note, 2026-11-05. Status: input for a decision, not a decision.

## Question

Which JavaScript graph-drawing library could replace Mermaid for the network diagrams of the offline `report.html`, and is it worth a proof of concept (POC)?

## Constraints

- Works offline on an air-gapped machine: the library is inlined into `report.html`. No CDN, no network, no build step, no npm at runtime. Vendoring one minified UMD/IIFE file per library is fine. No React or Vue.
- Same file runs inside the local web app (iframe).
- Exports SVG and PNG of a diagram. Today both come from Mermaid's SVG.
- Size budget for reference: the vendored `segowl/assets/mermaid.min.js` is **3.34 MB** (Mermaid **10.9.8**). The report is a local file, so the raw size matters, not the gzip size.
- SegOWL declares no licence (no `LICENSE`, none in `pyproject.toml`). Inlining GPL or EPL code in a report handed to a client is a decision to make, not a detail.

## What the per-Source diagram must show

One Source linked to ~38 target Interfaces in 5 Zone boxes (compound groups, coloured per Zone), 3 Machines with several Interfaces. Edges are coloured by Flow Policy status, dashed for "reachable", and labelled with port lists. Interfaces of one Machine are visibly tied together. Nice to have: drag, zoom, hover detail, hiding nodes.

## Why Mermaid fails here (root cause)

The per-Source diagram is a **star**: 1 node linked to 38. A layered layout (dagre in Mermaid, but also ELK layered and Graphviz `dot`) puts all 38 targets in the same layer. So the layer is either one very tall column (LR) or one very wide row (TB), whatever the library. The 38 port labels sit on 38 long edges that converge on one node, so they collide. A Machine with Interfaces in two Zones adds a cross-box edge that stretches both boxes.

So a new library helps only if it brings one of these:

1. a layout that uses both dimensions (Zone boxes packed around or beside the Source: force-directed with compound support, or rectangle packing inside the boxes);
2. readability tools that Mermaid lacks: labels hidden below a zoom level, label backgrounds, hover detail instead of printed labels, hiding a Zone.

Library-independent finding: moving the port lists **off the edges** (into the target node, or into a hover tooltip, coloured by status) removes most of the clutter, whatever draws the diagram.

## Finding: Mermaid itself has moved

- **Mermaid 12.0.0** (10 Sep 2026) bundles ELK and makes it the **default flowchart layout**. The single-file `mermaid.min.js` includes it (5.54 MB raw for 12.3.0). Breaking changes: ES2024 and Safari 17.4+ required, `defaultRenderer` removed in favour of the top-level `layout` option, new default theme and look.
- Mermaid's ELK options include `mergeEdges` (bundles the 38 edges leaving the Source into a trunk, which suits a star), `nodePlacementStrategy`, `considerModelOrder`, `straightenEdges`. Other algorithms are selectable: `elk.stress`, `elk.force`, `elk.box`, `elk.rectpacking`, `elk.mrtree`.
- The vendored **10.9.8 already contains ELK** (342 `org.eclipse.elk` strings and a `flowchart-elk` diagram type). So `flowchart-elk TB` can be tried today without changing the file, and EPL-licensed code already ships in every report.

Mermaid still gives no per-box layout, no zoom, no hover, and no hiding of nodes without regenerating the text.

## Comparison

Sizes are measured on the files we would vendor (jsDelivr, latest version, 2026-11-05). "Raw" is what lands in `report.html`.

| Candidate | Licence | What to vendor (raw / gzip) | Zone boxes (compound) and layout | Edge labels / colour / dash | SVG / PNG export | Interactivity | Last release | Offline inlining |
|---|---|---|---|---|---|---|---|---|
| **Mermaid 12.3 (ELK default)**, baseline | MIT (bundled elkjs is EPL-2.0 OR GPL-3.0) | `mermaid.min.js` 5.54 MB / 1.58 MB | Subgraphs. ELK layered is still layered: the star problem stays, but `mergeEdges` and orthogonal routing may help | Yes / `linkStyle` / dashed | SVG native, PNG via canvas (as today) | None built in (our code only) | 12.3.0, 2026-11-03 | One IIFE file, as today |
| **Cytoscape.js** + fcose | MIT (core and fcose) | core 436 KB / 136 KB + fcose chain (layout-base, cose-base, cytoscape-fcose, unminified UMD) 324 KB / 69 KB = **760 KB** | Compound nodes via `data.parent`, nesting allowed. fcose has "full support for compound graphs", plus fixed, alignment and relative-placement constraints | `label`, `text-rotation: autorotate`, `text-background-*`, `min-zoomed-font-size`; `line-color`; `line-style: dashed` | PNG/JPG **built in** (`cy.png`, `full`, `scale`). SVG only via **cytoscape-svg (GPL-3.0**, 21 KB, last release 2022-05) or our own serializer | Drag, zoom, pan built in; events for hover; hide with `display: none` | core 3.34.4 2026-10-15; fcose 2.2.0 2023-01 (stable, Mermaid itself depends on it) | UMD files, register themselves on a `<script>` tag |
| Cytoscape.js + cytoscape-elk | MIT + elkjs EPL-2.0/GPL-3.0 | core 436 KB + 11 KB + `elk.bundled.js` 1.65 MB = **2.09 MB** | Adapter builds a hierarchical ELK graph from the parents (read in the source). Uses ELK node positions only, Cytoscape draws the edges. Per-node layout options available (`nodeLayoutOptions`) | as above | as above | as above | 2.3.0, 2024-11 | UMD |
| Cytoscape.js + cytoscape-dagre / cola | MIT | +46 KB (dagre bundled) / +22 KB + WebCola 80 KB | dagre: same layered problem. cola: compound-aware, last WebCola release 2019 | as above | as above | as above | dagre 4.0.1 2026-08; cola 2.5.1 2022 | UMD |
| **ELK.js alone + our own SVG** | EPL-2.0 OR GPL-3.0 | `elk.bundled.js` **1.65 MB** / 477 KB | Best compound model: hierarchical graph, each box can use its own algorithm (`rectpacking`/`box` inside Zones, `layered`/`stress` at top level). Cross-box edges need `hierarchyHandling: INCLUDE_CHILDREN` with layered | Label placement computed by ELK; we draw colour and dash ourselves | SVG native (we write it), PNG via canvas as today | Whatever we write (zoom through `viewBox`) | 0.12.1, 2026-10-28 | UMD, global `ELK` |
| AntV G6 5 | MIT | `g6.min.js` **1.38 MB** / 390 KB + `@antv/g-svg` 49 KB for SVG rendering | Combos (nested). antv-dagre with `sortByCombo`; maintainers say combo + dagre is "not well tested" (overlaps reported) | Yes / yes / `lineDash` | Canvas by default, SVG renderer as a plugin | Rich (behaviours, tooltips, BubbleSets plugin for overlapping groups) | 5.1.1, 2026-05 | UMD |
| vis-network | Apache-2.0 OR MIT | standalone 654 KB / 155 KB | **No container boxes.** `groups` = shared style only, clustering = collapse into one node | Yes / yes / `dashes` | Canvas only, no SVG | Drag, zoom, physics | 10.1.4, 2026-10-27 | UMD |
| sigma.js + graphology | MIT | 393 KB + 74 KB | **No compound.** WebGL, made for thousands of nodes | Labels yes; dashed edges not in core | No SVG | Very fast pan and zoom | 4.0.4, 2026-10-27 | UMD |
| d3 (d3-force / d3-hierarchy) | ISC | d3 full 281 KB / 92 KB (d3-force alone 8 KB + deps) | Nothing built in: Zone hulls and clustering forces to write by hand. This is the "Obsidian graph" look | All by hand | SVG native | All by hand | 7.9.2, 2026-11-03 | UMD |
| force-graph | MIT | 173 KB | No groups. Canvas | Partial | No SVG | Drag, zoom | 1.52.0, 2026-09 | UMD |
| JointJS core (+ layout-directed-graph) | MPL-2.0 | 474 KB / 144 KB + 4 KB + dagre 49 KB | Embedding (parent and children), `clusterPadding`. Layout is dagre (same layered problem); MSAGL layout is ESM-only | Yes / yes / yes | The paper is SVG. Packaged `toSVG`/`toPNG` export is sold as JointJS+ | Drag (it is a diagram editor), zoom | 4.3.4, 2026-10-27 | UMD |
| Graphviz in the browser (Viz.js) | MIT (Graphviz: EPL) | `viz-global.js` **1.33 MB** / 479 KB (WebAssembly inlined) | Clusters (`subgraph cluster_*`). `dot` = same layered problem; `fdp` handles clusters with a force layout | Very good label placement / yes / yes | SVG native, PNG via canvas | None (static SVG) | 3.31.0, 2026-09-28 | UMD with the WebAssembly inlined (`@hpcc-js/wasm-graphviz` is ESM only) |
| AntV X6 | MIT | 583 KB / 166 KB | Embedding, no compound-aware layout bundled | Yes | SVG-based | Editor-grade | 3.1.8, 2026-08 | UMD |
| MSAGL (`@msagl/core`) | MIT | 778 KB / 196 KB (IIFE, global `msagl`) | Clusters in Sugiyama and MDS layouts; layout only, renderer to write (the SVG renderer package is not bundled) | by hand | by hand | by hand | 1.1.24, 2026-04 | IIFE core only |
| maxGraph | Apache-2.0 | no single-file bundle (ESM/CJS trees only) | Swimlanes, hierarchical | - | SVG | Editor | 0.25.1, 2026-10 | **Needs a build step: excluded** |
| ECharts graph series | Apache-2.0 | 1 MB+ | No compound | - | SVG renderer exists | - | 6.1.0, 2026-05 | **Not a fit: excluded** |

### Notes that weigh on the choice

- **Cytoscape SVG export** is the main weak point: the only extension is GPL-3.0, unmaintained since 2022, and built on canvas2svg. Alternatives are PNG only (built in, `scale: 3` is enough for a Word report), or our own SVG serializer from node positions, sizes and our own style mapping (we know every style we set, so this is bounded work).
- **Cytoscape determinism**: fcose randomises by default. A report needs the same picture on every open, so we need `randomize: false` from a deterministic initial position, or ELK (deterministic).
- **Machine across Zones**: no library draws one box that sits in two Zone boxes. The workable options everywhere are the same colour or ring for Interfaces of one Machine, a thin dotted "same Machine" link, or a bubble-set contour (`cytoscape-bubblesets` 28 KB, MIT, needs `cytoscape-layers`; G6 has it built in). Bubble sets are drawn on an extra layer, so check that `cy.png` exports them.
- **Licences**: elkjs (EPL-2.0 or GPL-3.0) already ships inside today's Mermaid bundle. cytoscape-svg (GPL-3.0) would be new.

## Recommendation

**Yes, a time-boxed POC is worth it, but start with the step that costs nothing.**

0. **Before any POC (about an hour):** render the largest per-Source diagram of the demo Mission with ELK. First `flowchart-elk` in the vendored 10.9.8, then Mermaid 12.3 with `layout: elk` and `elk: {mergeEdges: true}`, ports moved off the edges into the target nodes. If that is readable, stop: no new library, one file swapped.
1. **POC candidate 1: Cytoscape.js + fcose** (also try cytoscape-elk on the same data, it costs one more file). It is the best fit for the brief: MIT, about 760 KB (smaller than today's Mermaid), compound Zone boxes respected by the layout, every edge style needed, zoom-dependent labels, hover, hiding a Zone, drag for free, PNG built in. Its risk is SVG export.
2. **POC candidate 2, only if the static SVG output matters more than interactivity: ELK.js alone plus our own SVG renderer.** It gives the most control over a star (rectangle packing inside Zone boxes, edges drawn our way), deterministic output, native SVG export, and no new licence. The cost is writing and maintaining the renderer and the zoom.

Not worth testing: vis-network and sigma.js (no Zone boxes), G6 (heaviest, and combo plus dagre layouts are fragile per its maintainers), JointJS and X6 (diagram editors, layered layout or paid export), Graphviz (static, and `dot` has the same star problem as dagre), plain d3 (everything by hand, where Cytoscape gives the same result ready-made).

### What the POC must test to decide

Use the same data for every option: the per-Source diagram of the demo Mission (1 Source, ~38 targets, 5 Zones, 3 multi-Interface Machines). Compare side by side with today's Mermaid.

1. **Readability at a glance**: both dimensions used (no single column or row), no Zone box stretched by a multi-Zone Machine, no overlapping labels at the default zoom.
2. **Ports**: on the edge, in the node, or on hover. Which one the auditor reads fastest.
3. **Same output every time**: the layout is identical across reloads (deterministic), so an exported figure can be reproduced.
4. **Exports**: a PNG good enough to paste into a Word report (`cy.png({full: true, scale: 3})`), and an SVG: is a home-made SVG serializer under ~150 lines, or must we accept the GPL extension or PNG only?
5. **Machine tie**: colour, dotted link, or bubble set. Which one reads best across Zones, and whether it survives export.
6. **Interactivity worth having**: hide a Zone (today's Zone filters), hover detail, zoom. Drag is a bonus, not a criterion.
7. **Cost**: added bytes in `report.html`, time to first draw with 38 targets inside the app iframe, lines of `report.js` added, and whether the Python side only emits JSON (nodes, edges, styles) instead of Mermaid text.
8. **Scope**: the global, per-Zone, per-target and Pivot diagrams stay in Mermaid or move too. Two libraries in one report means two exports and two themes to maintain.

## Sources

- Mermaid layouts (ELK built in, default from 12.0.0): https://mermaid.js.org/config/layouts.html
- Mermaid ELK config properties: https://mermaid.js.org/config/schema-docs/config-properties-elk.html
- Mermaid releases (12.0.0 breaking changes, IIFE bundle grows ~500 KB gzip, 12.2 elkjs licence note): https://github.com/mermaid-js/mermaid/releases and https://github.com/mermaid-js/mermaid/releases?page=2
- Cytoscape.js docs (compound `data.parent`, `cy.png`, `line-style`, `text-rotation`, `min-zoomed-font-size`, `text-background-color`): https://js.cytoscape.org/
- cytoscape-fcose (compound support, constraints, UMD script order): https://github.com/iVis-at-Bilkent/cytoscape.js-fcose
- cytoscape-elk (adapter; compound handling read in `dist/cytoscape-elk.js`, `makeGraph`): https://github.com/cytoscape/cytoscape.js-elk
- cytoscape-svg (GPL-3.0): https://github.com/kinimesi/cytoscape-svg
- cytoscape-bubblesets: https://www.npmjs.com/package/cytoscape-bubblesets
- ELK hierarchy handling: https://eclipse.dev/elk/reference/options/org-eclipse-elk-hierarchyHandling.html ; elkjs: https://github.com/kieler/elkjs
- G6 renderer (`@antv/g-svg`): https://g6.antv.antgroup.com/en/manual/further-reading/renderer ; dagre with combos: https://g6.antv.antgroup.com/en/examples/layout/dagre/antv-dagre-combo/ ; maintainer comments on combo layouts: https://github.com/antvis/G6/issues/5988 ; releases: https://github.com/antvis/G6/releases
- vis-network (canvas, groups, clustering): https://visjs.github.io/vis-network/docs/network/
- sigma.js (WebGL): https://www.sigmajs.org/
- JointJS DirectedGraph (`clusterPadding`): https://docs.jointjs.com/api/layout/DirectedGraph ; MSAGL layout: https://docs.jointjs.com/learn/features/automatic-layouts/msagl
- Graphviz `fdp` (clusters): https://graphviz.org/docs/layouts/fdp/ ; Viz.js: https://github.com/mdaines/viz-js
- MSAGL JS: https://github.com/microsoft/msagljs
- Versions, licences and release dates: npm registry, `https://registry.npmjs.org/<package>`. File sizes: jsDelivr, `https://data.jsdelivr.com/v1/packages/npm/<package>@<version>?structure=flat` and the files themselves, `https://cdn.jsdelivr.net/npm/<package>@<version>/<file>` (measured 2026-11-05).
- Vendored Mermaid version and its ELK content: `segowl/assets/mermaid.min.js` (version string `10.9.8`, `flowchart-elk`, 342 `org.eclipse.elk` strings).
