# Scan diff tab

Status: ready-for-agent
Blocked by: 08
Stage: Stage 3 (see ../spec.md)

## What

In-browser Diff tab: two selectors, each any Scan or any Source View (data embedded as JSON). Result: added / removed / unchanged / not comparable (port tested on one side only). No CLI subcommand.

## Acceptance

- diff of broad vs targeted fixture shows extra ports as added
- port tested on one side only shown as not comparable
