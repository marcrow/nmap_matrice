# Per target per Machine: Sources diagram, open ports per Interface, copy

Status: done
Blocked by: 04, 05
Spec: ../spec.md

## What

Per target replaces Exposure per target and works per Machine: a search (name, IP, Zone) offers Machines; the Machine is a frame holding all its Interfaces, the Sources reaching them grouped by Zone (Cytoscape, same look and options as Per source). Under the diagram, per Interface: open ports × Sources (open with the Flow Policy icon / not open / not tested, from Coverage) and the Port Label (wrapping, the table fits narrow windows), with a **Copy its open ports** button (merged across Sources, `nmap -p` form: `22,443`, `T:22,U:53`) and **Copy all the Machine's open ports**. Then the "Seen from each Source" table. A folded **All targets** table (target × Source: target, Zone, Source, verdict, open ports, Flow Policy), searchable and sortable, above the picker. The Port Group filter applies to the diagram and every table row.

Reference: branch `prototype/report-readability`, `html.py` `_pertarget_tab`, `_iface_ports`, `_nmap_ports`, `_copy_btn`; `report.js` `pickTarget`, `copyPorts`.

## Acceptance

- searching "fw-01" shows one frame with its 5 Interfaces and the 3 Sources
- ad-01's port table (13 ports, long labels) fits a 900px window without horizontal scroll
- Copy on an Interface with UDP gives `T:…,U:…`; works in `report.html` opened as a file (clipboard fallback)
- `_nmap_ports` has a test

## Comments

**2026-11-05, done.** `html.py` `_pertarget_tab` (folded All targets, Machine search on a `<datalist>`: name · IPs · zones, then one pane per Machine), `_target_graph`, `_iface_ports`, `_nmap_ports`, `_copy_btn`; Exposure per target (`_exposure_html`) is gone. Diagram: `report_graph.js` takes nodes with `links` (a Source reaching several Interfaces of the Machine); the centre is a frame holding the Interfaces in one column, each bordered with its Zone colour, arrows towards them (`edge.in`); edges of different Sources get their own trunk (`lane`). With a Machine in the centre "Zones facing the Source" places the Zones beside it only (an edge leaving an Interface of the column upwards would pass under its neighbours). A small diagram is not zoomed beyond 1.1. `copyPorts` falls back to a textarea when the clipboard API is missing or refused (a `file://` page counts as secure but headless refuses). Checked headless: "fw-01" → one frame with its 5 Interfaces and the 3 Sources; ad-01's 13-port table fits a 900 px window (no page overflow); Copy on ad-01 gives `T:53,…,5985,U:123` from the file. Test: `test_nmap_ports_lists_tcp_plainly_and_prefixes_protocols_when_mixed`.
