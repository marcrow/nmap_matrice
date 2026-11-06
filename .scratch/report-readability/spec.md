# Report readability: one look with the app, matrices like the Flow Policy one, legends that explain themselves, more visuals

Status: done

Vocabulary: `GLOSSARY.md` (Finding, Flow Policy, Pivot Machine, Port Group, Source, Undeclared Flow, Zone). Raised by the user on 2026-11-05 while trying the app on the lab (`lab/`).

## Feedback

1. **The report inside the app looks nested**: `/report` is an iframe of `report.html` (`segowl/app.py`), which brings its own header (title, meta, SegOWL logo) and its own row of tabs under the app's header and nav. Rethink how the report is laid out, embedded and on its own, keeping the app and the offline `report.html` consistent; the report sections could switch like the Auditor Kit big tabs (`kit_body`, `.bigtabs`). The Port Group filter in the report header applies to every view (good); where it lives in the new layout is open.
2. **The legends sit above diagrams they do not describe** (see "What the legend mixes today").
3. **The matrices are ugly**: take inspiration from the Zone matrix of the Flow Policy editor (`/policy`, `app_policy.js`).
4. **Pivot Machines are unreadable**: a long list of details that nobody reads, so the feature is lost. Wanted: a diagram, with the detail still available, expanded on demand.
5. **Exposure per target**: keep the detail, but add a search field and a diagram for the chosen target, if it is not too costly.
6. **Mermaid diagrams** are not the prettiest but they work; improving them is optional.
7. **The Flow Policy tab is hard to read**: one big table. What the auditor reads there is mostly the Findings, but it also holds the Undeclared Flows (hence the name Flow Policy). Wanted: per-column filters as elsewhere in the app, plus any other readability gain.
8. **Per source is liked** (diagrams, Zone filters, exports do the job), but its checkboxes, buttons and dropdown have no style.
9. **Target details** only shows the open ports in green, not the detail of the Scans.
10. **Scans tab** works; its rendering could be nicer.
11. **Anomalies › Sources without scan** lists every inventory Interface without a Scan (`analysis.py` `missing`). A target that was never meant to be a Source is not an anomaly: only a declared Source (a `scans/<ip>/` folder, as the Scans page creates) without a Scan is one.

## What the legend mixes today (`segowl/render/html.py` `_legend`, `segowl/render/mermaid.py`)

One line of chips, under every diagram, holds three separate codes:

- **Matrix cell states** (`v-open`, `v-reach`, `v-alive`, `v-block`, `v-none`, `conflict`): OPEN service / reachable (closed) / alive (ping/ARP) / blocked / unseen / Scans disagree. They colour the **matrix cells**, not the diagram, but they are shown above the diagram.
- **Edge colour = Flow Policy verdict** of the OPEN flows (only when a Flow Policy exists): red = denied (Finding), orange = undeclared, green = allowed. Without a Flow Policy: red = cross-zone OPEN, green = same-zone. Dashed edge = reachable, no open port.
- **Red bold port number in an edge label = a port of the admin Port Group** (`mermaid.py` `_label`, `analysis.py` `HIGHLIGHT`). This code appears nowhere in the legend. In the matrices the admin ports are a red left bar (`report.css` `.admin`).

So red stands for three things (blocked cell, denied edge, admin port), and OPEN is green in a matrix cell while the same flow can be a red edge.

## Decided

- **One legend per view**: under the diagrams, only what the diagrams use (edge colours, dashed edge, port marks), worded like the app Overview legend (`overview.html`); under the matrices, only the cell states.
- **Ports in an edge label**: red = a port the Flow Policy denies (the port of a Finding); bold = a port of the admin Port Group; plain otherwise (an allowed port is never red). The edge colour keeps the Flow Policy verdict. No colour per Port Group: groups overlap. The report stays standalone: the Port Groups are embedded in `report.html`, no app needed.
- **Red means Finding**: BLOCKED is no longer red. The whole colour set of the verdicts is to be redesigned (the user asks for design help), since the verdict colours and the Flow Policy colours clash today.
- **Report matrices take the style of the Flow Policy matrix** (spacing, fonts, headers, borders), not its cell layout: one cell holds a decision, the other an observation. The report stays offline (`report.html` with no CDN) and readable when printed or pasted into an audit report.
- **Form controls of the report** (checkboxes, buttons, selects) get the app's styles.
- **Scope**: every diagram (global, per Source, per Zone) and every matrix.
- **One `report.html`, two chromes**: inside the app it hides its own header (title, logo) and shows its sections as Auditor Kit big tabs (title, one-line description, count), sticky, with the Port Group filter. On its own it keeps a plain header above the same big tabs. The app does not re-render the report.
- **Two colour codes, never mixed**: red / amber / green are reserved for the Flow Policy, always with an icon (✕ Finding, ? undeclared, ✓ allowed). Matrix cells (prototype round 1, variant B): neutral tiles tinted by the Flow Policy, the verdict as a small navy dot (ordinal: OPEN darkest). Shaded navy tiles (variant A) were rejected as too heavy.
- **Without a Flow Policy** every flow is undeclared (ADR-0002): cross-zone OPEN edges are orange, same-zone edges grey. No red without a Flow Policy.
- **Pivot Machines, explained**: each card says in plain words why the Machine is a rebound (its Interfaces, who reaches which one OPEN on which ports) and draws both sides: in, the Source Zones → the Interface they reach; out, each other Interface → its Zone, with what that Zone holds and what the Source's Zone already reaches there directly (bypass when nothing, else "k / N reached directly"). If the Machine is itself a Source, what it was seen reaching there. Legend: "rebound: from this Machine, its other Zones". Cards with a bypass first; the detailed list folded below.
- **BLOCKED and UNSEEN stay distinct** (tested and blocked vs never seen, cf. Coverage): BLOCKED a filled grey tile with ×, UNSEEN an empty dashed tile with –.
- **Per target works per Machine**: the search (name, IP, Zone) offers Machines; a multi-Interface Machine is drawn as a frame holding all its Interfaces, the Sources grouped by Zone; the table gets an Interface column.
- **Exposure overview kept**: above the Per target picker, a folded "All targets" table (one row per target × Source reaching it: target, Zone, Source, verdict, open ports, Flow Policy), searchable and sortable.
- **Port Group selector as chips** in the sticky bar (`all ports`, then one chip per group, active one filled); a dropdown beyond about 8 groups.
- **Sections delimited**: each section is a white card with its title.
- **Per target tab**, mirror of Per source, replaces Exposure per target: a picker with search, a diagram of the Sources reaching the target grouped by Zone, the detail table. Mermaid text generated per target, drawn only when selected.
- **Tables: one search field per table, sort by clicking a column header** (click again: reverse), plain JS in `report.js`, on every report table; they stay real `<table>`s (copy into an audit report). No Tabulator in the report. Per-column filters were tried in the prototype and rejected (too heavy).
- **The Flow Policy tab keeps its name**; its big tab carries the counts ("3 Findings · 12 undeclared").
- **Target details** gets a row that unfolds: per port, the state each Scan saw (provenance, today only in the matrix tooltips) and its Port Label (product, tags).
- **Sources without scan** lists declared Sources (a `scans/<ip>/` folder, made by the Scans page or by hand) that hold no Scan, not every Interface. By hand, an auditor who never makes empty folders gets an empty list, never a false anomaly.

- **Seven big tabs, in this order**: Global view (diagram, Zone and host matrices) · Flow Policy · Pivot Machines · Per source · Per target · Scans (Scans, Conflicts, Coverage and the former Anomalies tab: all say whether the data is complete and reliable) · Diff.
- **One admin marker everywhere**: admin ports are bold, in edge labels and in matrix cells (the red left bar goes).
- **No print feature for now**: the prototype's Print / PDF rendering was ugly; better no button than a bad one. What goes into an audit report is the exported diagrams and copied tables.
- **The app Overview** takes the same palette and legend wording as the report.
- **Diagrams move to Cytoscape.js** (ADR-0005), validated on the POC (`prototype_report/cytoscape_poc/`, round 2). Layout presets written for SegOWL, default **Zones facing the Source**: each Zone on one side of the Source (columns left / right, rows above / below), the assignment that fills the screen best, right-angle edges that never pass under a node, deterministic. Also offered: Zones on both sides, Zones around the Source. fcose and the community layouts (ELK, cola) are dropped. Sober look (white cards, thin borders, navy / slate text), the Source as a navy card with a cyan bar. Ports and the Flow Policy icon in the target nodes by default; ports on the edges (a tag before the target) and one edge per Zone as options. A Machine's Interfaces share a colour bar (kept: it shows Machines spanning Zones), hover rings them in cyan; dotted links optional, off. Options in a folded panel, remembered per viewer. PNG export only (SVG not needed).
- **Arranging a Zone**: right-click on a Zone frame offers one column, two columns, one row, two rows, auto. Auto follows the density rule (beside the Source: 1 column up to 8 Interfaces, 2 up to 16, 3 beyond; above / below: 1 row up to 6, 2 up to 12, 3 beyond; with ports on the edges always one column or row). The same choice for every Zone sits in the options panel.
- **Zone and Machine colours never use red / amber / green** (reserved for the Flow Policy): Zones in pale cool tints identified by their title, Machines in 4 validated cool hues (`#3a4e9d`, `#a35ec1`, `#48a5c7`, `#bb9af4`, repeating beyond). The POC's Zone tints were too close to tell apart: each Zone gets a distinct validated hue on its border and title, the fill stays pale. The Pivot rebound stays amber (user's choice).
- **Per target**: per Interface, open ports × Sources with the Port Label, and a button that copies its open ports merged across Sources in `nmap -p` form (`22,443`, `T:22,U:53`); one for the whole Machine.
- **Pivot Machine cards**: name, Zone tags, bypass count; In (who reaches which Interface); Out: for every other Zone and every Source Zone landing there, the Interfaces the rebound adds to what that Source Zone reaches directly ("+3: …", "nothing new", bypass when it adds everything). Cards with a bypass first; a Machine whose rebound adds nothing is folded. One explanation at the top of the tab, dark on white, saying the list is not exhaustive (Machines grouped by inventory name).
- **Matrix legend**: every item is a tile drawn like a cell; same Machine (hatched) and Scans disagree included; the cells read `closed` / `ping` instead of `o` / `~`, and the legend tiles show "ports" rather than sample numbers. The Port Group filter changes only the port text of a cell (icon, bold and tile kept, column widths frozen).
- **Port Group bar** in brand amber with "This filter applies to every tab"; it filters every tab, Per target included.
- **Full width**: the report uses the whole window (no max width), diagrams first.
- **Scans tab**: the app's table style and the column filters are enough for now; the prototype will tell if more is needed.

## Next

Prototype done (`issues/01-prototype.md`, branch `prototype/report-readability`). Implementation: `issues/02` to `issues/10`, all done (2026-11-06, PR #3).

## Out of scope

- nmap service names and versions (`-sV`) in Target details: the parser does not read `<service>` today. Traced in `.scratch/scan-services/`.
