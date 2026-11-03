# Consolidated host -> host matrix

Legend: `OPEN`=service reachable | `o`=reachable (closed) | `~`=alive (ping/ARP) | `x`=blocked | `.`=unseen | `-`=same machine

| source \ target | auditor · 172.31.250.1 | app-01 · 172.31.250.10 | db-01 · 172.31.250.20 | ghost-01 · 172.31.250.30 | never-scanned · 172.31.251.40 |
|---|---|---|---|---|---|
| **auditor · 172.31.250.1** | - | 22,udp:161,6379,8443 | 5432 | x | . |
