"""seg_matrix — Segmentation matrix & Mermaid diagrams for network segmentation testing.

PRINCIPLE
---------
For each "source" host in the inventory, an nmap scan is launched *from* that host
(SSH/SOCKS pivot, local agent, etc.) towards the rest of the perimeter. The nmap output
is named after the source IP: <source_ip>.xml | .gnmap | .nmap.
A single `nmap -oA <source_ip> ...` produces all three formats at once.

The script cross-checks each scan with the CSV inventory (ip;zone;type;name) and writes:
  - matrix_hosts.md / .csv    : consolidated host -> host matrix
  - matrix_zones.md           : consolidated zone -> zone matrix
  - exposure_targets.md       : target-oriented view (who reaches what)
  - segmentation.mmd          : global zone Mermaid
  - mermaid/<ip>.mmd          : per-source Mermaid
  - findings.md               : Findings and undeclared flows (with a Flow Policy only)
  - report.html               : standalone tabbed report (Global / Per source / Anomalies)
    (assets/mermaid.min.js is inlined -> viewable offline; otherwise CDN)

MULTI-INTERFACE MACHINES & SELF EXCLUSION
-----------------------------------------
Each inventory row is an interface (one IP in one zone). Rows sharing the same `name`
form a machine (no name: machine = IP). All interfaces of the source machine are
excluded from its scan (it sees itself locally).
A duplicate IP in the inventory is an error.

SEGMENTATION SEMANTICS
----------------------
  OPEN       : >=1 "open" port        -> service reachable (effective access)
  REACHABLE  : no open but closed     -> RST received, the L4 flow crosses the segmentation
  ALIVE      : no port, host up       -> answers at L3/L2 (ping/ARP); never with -Pn
  BLOCKED    : "filtered" only        -> flow blocked (isolation OK) / host down
  UNSEEN     : target absent from the scan output

USAGE
-----
  python3 -m seg_matrix -i inventory.csv -s ./scans/ -o ./report/
  python3 -m seg_matrix -i inventory.csv -s ./scans/ --host-graph
"""
