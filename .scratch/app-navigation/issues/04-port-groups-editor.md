# Port Groups editor

Status: needs-triage
Blocked by: 02
Spec: ../spec.md

## What

Auditor Kit › Port Groups: grid of shipped (greyed) and Mission groups; editing a shipped group creates the Mission override, "reset to shipped" removes it; port syntax validated inline; rename rewrites `flow_policy.csv` and `scan_profiles.csv` at once; delete only when unused. Optimistic save (fingerprints) like every editor.

## Acceptance

- a Mission group with a shipped name overrides it in the report and the scripts; reset brings the shipped one back
- renaming a group used by rules and profiles rewrites both files; the CLI loads them without error
- a group still referenced cannot be deleted; the UI says by what
