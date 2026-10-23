# Scan diff tab

Status: done
Blocked by: 08
Stage: Stage 3 (see ../spec.md)

## What

In-browser Diff tab: two selectors, each any Scan or any Source View (data embedded as JSON). Result: added / removed / unchanged / not comparable (port tested on one side only). No CLI subcommand.

## Acceptance

- diff of broad vs targeted fixture shows extra ports as added
- port tested on one side only shown as not comparable

## Comments

- Done. Acceptance adjusted: broad (1-1000) vs targeted (5432,6379,8443) shows the extra ports as
  **not comparable**, not added, since the broad sweep never tested them; "added" requires the port
  to be tested on the A side. broad vs after_fix shows 22 as removed. Verdict changes are listed only
  for targets present in both outputs.
