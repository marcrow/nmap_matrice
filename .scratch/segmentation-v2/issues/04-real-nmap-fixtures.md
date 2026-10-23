# Real nmap fixtures

Status: done
Blocked by: 03
Stage: Stage 1 (see ../spec.md)

## What

Script that starts a few throwaway Docker containers on an isolated network (some listening TCP/UDP services, one filtered via iptables or no listener) and runs real nmap from a container/host to produce `tests/fixtures/`: a full -p- TCP XML, a targeted follow-up XML with extra ports, a -sU XML, one .gnmap. UDP and SYN scans need root: hand the user the exact `! sudo ...` command. Fixtures are committed; the script is kept for regeneration.

## Acceptance

- fixtures validate against `/usr/share/nmap/nmap.dtd`
- no IP or hostname outside the Docker network
