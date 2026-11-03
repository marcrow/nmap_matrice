# Flow Policy editor

Status: needs-triage
Blocked by: 03
Spec: ../spec.md

## What

Rule grid as validated in 01: dynamic dropdowns (Zones, Machines, Port Groups, `*`), port syntax validation, "bootstrap from observed flows" (observed_zone_flows draft). Writes `flow_policy.csv` in the existing format (ADR-0002 unchanged).

## Acceptance

- a rule on an unknown Zone is flagged inline
- bootstrap then save produces a file the CLI loads without error
