# Port Groups editor

Status: ready-for-agent
Blocked by: 02
Spec: ../spec.md

## What

Auditor Kit › Port Groups as in the prototype: shipped (grey) and Mission groups, first column "source" sortable; editing a shipped group's ports creates the Mission's replacement, "Reset to shipped" removes it; ports as chips folded beyond 10; ports editor with autocompletion (Port Labels, IANA, `udp:`, UDP twin, `@group` inserts a copy of its ports); syntax validated inline; rename (Mission groups only) rewrites `flow_policy.csv` and `scan_profiles.csv` at once; delete only when unused; "used by" lists the profiles, the rules on hover. Optimistic save (fingerprints) like every editor.

## Acceptance

- a Mission group with a shipped name replaces it in the report and the scripts; Reset brings the shipped one back
- renaming a group used by rules and profiles rewrites both files; the CLI loads them without error
- a group still referenced cannot be deleted; the UI says by what
- `@web` typed in a ports cell inserts web's ports; the file never contains a group reference
