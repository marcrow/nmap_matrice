# Flow policy

Status: done
Blocked by: 10
Stage: Stage 4 (see ../spec.md)

## What

Load optional `flow_policy.csv` (`src;dst;ports;action;comment`) and evaluate per ADR-0002 and the spec precedence example. Findings = explicitly denied observed flows; Undeclared Flows shown apart; policy colouring in graphs. Without a policy: no Findings, no policy colouring; remove the current cross-zone findings tab/`findings.md`, keep Anomalies.

## Acceptance

- spec precedence example passes as a test
- report without policy has no Findings
