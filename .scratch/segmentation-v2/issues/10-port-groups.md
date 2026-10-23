# Port groups

Status: ready-for-agent
Blocked by: 06
Stage: Stage 2 (see ../spec.md)

## What

Port Groups: defaults file shipped with the tool (`admin`, `db`, `web`…), overridden by `mission/port_groups.csv`. Report filter by group, highlight of admin ports in views.

## Acceptance

- filtering by `admin` hides other flows in matrices and graphs
- mission file overrides a default group
