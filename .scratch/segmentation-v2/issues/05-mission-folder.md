# Mission folder

Status: done
Blocked by: 03
Stage: Stage 1 (see ../spec.md)

## What

`seg_matrix mission/` reads `inventory.csv`, optional `flow_policy.csv` / `port_groups.csv`, `scans/<src_ip>/*` (any file name), writes `report/`. Legacy `-i/-s/-o` override paths; legacy `scans/<ip>.{xml,gnmap,nmap}` at the scans root still accepted. Unknown source folders listed as ignored scans.

## Acceptance

- both layouts produce a report
- ignored scans listed in terminal and Anomalies tab
