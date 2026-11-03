# Observed flow exports

Status: done
Blocked by: 09, 14
Stage: Stage 4 (see ../spec.md)

## What

Write `observed_flows.csv` (Source → Interface → proto/port with IP, Machine, Zone and free columns on both sides, state, Scans) and `observed_zone_flows.csv` (per Zone pair and port, Flow Policy format with empty `action`).

## Acceptance

- `observed_zone_flows.csv` with actions filled loads as a valid flow_policy.csv
