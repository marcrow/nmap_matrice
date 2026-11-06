# Suggest that two inventory names may be one Machine

Status: needs-triage

Vocabulary: `GLOSSARY.md` (Interface, Machine, Pivot Machine, Scan). Idea raised by the user on 2026-11-05 during the `report-readability` prototype; not a goal today.

## Idea

A Machine is what the inventory names, so a device carrying one name per network shows as several Machines, and the Pivot Machine it is goes unnoticed. From the Scan results, estimate how likely two Interfaces with different names are the same device, and suggest the merge to the auditor (never apply it).

## Notes for triage

- Feasibility unknown. Leads: identical open port sets and Port Labels, nmap OS fingerprint and service versions (`-O`, `-sV`, which the parser does not read today, see `.scratch/scan-services/`), SSH host keys or TLS certificates (NSE scripts), MAC address when the Source shares the segment.
- Output is a probability with its evidence, the decision stays the auditor's (rename in the inventory).
