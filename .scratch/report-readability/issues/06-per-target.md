# Per target per Machine: Sources diagram, open ports per Interface, copy

Status: ready-for-agent
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
