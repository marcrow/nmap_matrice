# Udp end to end

Status: ready-for-agent
Blocked by: 06
Stage: Stage 1 (see ../spec.md)

## What

Handle UDP throughout: verdicts per proto (UDP closed = REACHABLE), matrices and graph labels show proto when not TCP (`udp:161`).

## Acceptance

- -sU fixture yields the expected verdicts
- TCP-only reports unchanged
