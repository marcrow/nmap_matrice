# Read the resolved names from the Scans and serve the proposals

Status: ready-for-agent
Blocked by: 01
Spec: ../spec.md

## What

- `segowl/nmap.py`: each host record keeps the name nmap reports: XML `<hostname>` (PTR preferred over `user`), gnmap `Host: ip (name)`, `.nmap` `Nmap scan report for name (ip)`. Lower case, no trailing dot.
- `GET /api/inventory` (or a sibling endpoint) adds, per IP, the names by Source, and the IPs of the Scans absent from the inventory with verdict ALIVE or better (name and verdict). It also gives what the panel needs to tell a skip: the Machines the Flow Policy names (`D.refs` already counts Zone references).
- Nothing stored; the names never reach a kit.

## Acceptance

- a test per format on a fixture with a name, without a name (`-n`), and with a mixed-case trailing-dot name
- the demo Mission (`demo/`) returns `fw-01.corp.local` for its firewall Interfaces
- an IP down or absent in every Scan is not proposed as "not in the inventory"

## Comments
