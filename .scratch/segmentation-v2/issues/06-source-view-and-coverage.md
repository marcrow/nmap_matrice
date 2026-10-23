# Source view and coverage

Status: ready-for-agent
Blocked by: 04, 05
Stage: Stage 1 (see ../spec.md)

## What

Several Scans per Source combined into a Source View (ADR-0001: most permissive state per proto/port wins, disagreements recorded). Coverage from XML `scaninfo` + args + start time: per Source → Interface, which ports were tested by which Scans. Non-XML formats: Coverage unknown, never assert a port untested.

## Acceptance

- broad + targeted fixture: extra ports appear in the Source View
- disagreement open/filtered on same port is kept as open and flagged
- a port absent from every scaninfo is reported untested, not UNSEEN
