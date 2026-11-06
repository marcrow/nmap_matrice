# Matrix cells and legends: two colour codes, one legend per view

Status: done
Blocked by: 02
Spec: ../spec.md

## What

Zone and host matrices take the Flow Policy editor's tile style (3px spacing, 7px radius, zone chips as headers, "from ↓ · to →" corner). Cells: neutral tiles tinted by the Flow Policy (red / amber / green) with its icon ✕ / ? / ✓, the verdict as a navy dot (darker = more open); BLOCKED a filled grey tile with ×, UNSEEN an empty dashed tile with –, REACHABLE reads `closed`, ALIVE reads `ping`; same Machine hatched; only admin ports bold (the red left bar goes). Without a Flow Policy no red anywhere: cross-zone OPEN edges amber, same-zone grey. One legend per view: under the diagrams only edge colours, dashed edge and the port marks ("bold = admin port, red = denied by the Flow Policy"); under the matrices only tiles drawn exactly like the cells (incl. same Machine and Scans disagree, "ports" instead of sample numbers). The Port Group filter changes only the port text of a cell (icon, bold, tile kept) and freezes the column widths, so tiles do not jump.

Reference: branch `prototype/report-readability`, `html.py` `_cell_html`, `MARK`, `_zone_matrix_html`, `_host_matrix_html`, `_matrix_legend`, `_diagram_legend`; `report.css` (`:is(.mx td,.lt)` rules, `.lt`); `report.js` `setGroup`.

## Acceptance

- on the demo: a Finding cell is a red-tinted tile with ✕, BLOCKED and UNSEEN look different, every mark in a cell appears in the legend under it
- leaving "all ports" for a group and back does not move any tile
- `lab/` without a Flow Policy shows no red

## Comments

**2026-11-05, done.** Cells: `html.py` `_cell_html` (tile tinted by the Flow Policy with `_pg` icon, verdict dot in CSS, `MARK` closed / ping / × / –), `_zone_matrix_html` (zone chips, `+n` beyond 6 ports, pairs), `CORNER` "from ↓ · to →"; the `admin` red bar is gone, admin ports are bold everywhere (`_ports_html`, `data-b`). Legends: `_diagram_legend` under every diagram, `_matrix_legend` under every matrix (tiles drawn with the cell classes). Mermaid (`mermaid.py` `_label`, `_edge`): denied ports red, admin bold; without a Flow Policy cross-zone OPEN amber, same-zone grey, reachable slate dashed; `Analysis.denied` / `zone_denied` feed them (the `.mmd` snapshots changed accordingly). `report.js` `filterPorts` rewrites only the port text (`portsHtml`, mirror of `_ports_html`), `freeze` sets the matrix column widths from the unfiltered layout (also on a tab first shown while a group is active). Checked headless: demo Findings are red tiles with ✕; picking `db` then `all ports` moves no tile (positions compared before / after); demo inventory with the `lab/out` Scans and no Flow Policy uses no red. Table verdicts became navy badges (`_vb`).
