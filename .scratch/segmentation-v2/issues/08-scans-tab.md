# Scans tab

Status: done
Blocked by: 06
Stage: Stage 1 (see ../spec.md)

## What

Report tab 'Scans': one row per Scan (Source machine/zone, date, full nmap command, proto, ports as ranges, target count, file, disagreements with other Scans). Coverage per target Interface (tested by which Scans, on which ports). Matrix cell tooltip lists the Scans behind its verdict.

## Acceptance

- tab readable with 50+ scans (sortable or filterable by Source)
- tooltip present on host matrix cells
