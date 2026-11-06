# Show nmap service names and versions in the report

Status: needs-triage

Vocabulary: `GLOSSARY.md` (Port Label, Scan, Source View). Idea raised by the user on 2026-11-05 during the `report-readability` grilling; traced for later.

## Idea

When a Scan ran with service detection (`-sV`), show per open port what nmap identified (service name, product, version) in Target details, next to the Port Label.

## Notes for triage

- `segowl/nmap.py` does not read `<service name= product= version=/>` (XML) or the service column of gnmap today.
- Several Scans of one Source may identify a port differently: pick a rule (most detailed, or most recent) and keep the disagreement visible, like the verdict (ADR-0001).
- A Scan without `-sV` gives nmap's guess from `nmap-services`: mark it as a guess, not an identification.
