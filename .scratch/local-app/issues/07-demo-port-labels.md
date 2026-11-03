# Demo port_labels.csv

Status: ready-for-agent
Blocked by: –
Spec: ../spec.md

## What

Research agent builds `segowl/defaults/port_labels.csv` (`port;product;tags`, `udp:` prefix for UDP), fairly complete for internal segmentation audits: backup (Veeam…), out-of-band (iLO, iDRAC, IPMI, BMC), virtualization (ESXi, vCenter, Hyper-V, Proxmox), network/security appliances (Fortinet, Palo Alto, Cisco), AD/Windows admin (RDP, WinRM, SMB, RPC), databases, monitoring (Zabbix, Nagios, PRTG, SNMP), DevOps (Kubernetes, Docker, Jenkins). Sources: vendor documentation only, each product's doc URL kept in the PR description; no data copied from nmap-services (NPSL).

## Acceptance

- every row cites a vendor-doc source in the PR
- tags drawn from a small fixed vocabulary listed at the top of the file

## Comments

2026-11-03: first pass written (387 rows, 15 tags incl. `messaging`). Only 4 sources fetched and checked (Proxmox, Kubernetes, Veeam, Palo Alto); others cited from memory, see `07-sources.md`. Remaining: verify every unchecked URL/port (HPE iLO, Dell iDRAC, Fortinet, VMware, Nutanix, Check Point, F5, Commvault first), drop or fix Acronis 9877, SAP ASE 5000, Supermicro 5120/5123. Loader in 04 must skip `#` lines anywhere.
2026-11-03 user feedback: add common ALTERNATE ports as their own labels (SSH 2222/2200/8022, RDP 3388/3390, etc., "X — common alternate port"), and make sure the `network` tag is well populated. Today 2222 is only labelled as ESET.
