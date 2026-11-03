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
2026-11-03 second pass (verification): 437 rows, validated with `parse_port_set`, all tags from the header vocabulary, 66 rows tagged `network`. Nearly every product is now `[checked]` against a vendor page, RFC or IANA in `07-sources.md`. Fixed: iDRAC (5900 relabelled, 5901 added), Supermicro virtual media is TCP 623, ESXi CIM 5988 (not 5989), vCenter 9443/7444/6501/6502 labelled vSphere 6.x, Fortinet 8008 (policy override, not FSSO) and 10443 (EMS packages, not SSL VPN), plus 703/8010/8014. Also fixed: Commvault 8401/8403 labels, Ceph 6800-7568, RustDesk 21114-21119, ESET 2223, Oracle CMAN 1630/1830, Palo Alto HA labels. Added Acronis 7780, Kaspersky 13299/8080/udp:15000, Consul 8600, Wazuh 1516, ConfigMgr multicast. Removed: HPE iLO 3002, iDRAC 3668, Supermicro 5120/5123, SAP ASE 5000, Data Domain 2051 (replaced by 3009), ESXi udp:427, Portainer 9000. Added a network section (RIP/RIPng, LDP, BFD, HSRP, RADIUS CoA, RadSec, syslog 601/DTLS, SNMP over TLS, RESTCONF, OpenFlow, Geneve, L2TP, Junos XML 3220/3221, Cisco reverse Telnet 2001-2016), plus 20 "common alternate port" rows (convention). Not done: these rows are still `[unverified]` because the vendor page is behind a login, blocked, or silent: Check Point (sk52421 login), UniFi 8080/8443 (help.ui.com 403), CyberArk 1858, ScreenConnect 8040/8041 (login), Db2 50000 (25000 on 11.5.6+), Graylog GELF 12201. NetFlow udp:2055 is marked convention. Status left unchanged until a human with vendor logins checks these.
