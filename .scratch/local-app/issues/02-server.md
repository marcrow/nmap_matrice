# Server: segowl serve, auth, report

Status: needs-triage
Blocked by: 01
Spec: ../spec.md

## What

`segowl serve <mission_dir>` (stdlib, ADR-0004): creates the skeleton, serves the navigation shell and `report.html` regenerated on change. `segowl user add <login>` writes `~/.config/segowl/users` (scrypt). No users file → refuse non-loopback `--host`. `--cert/--key` → HTTPS. Optimistic save helper (refuse if the file fingerprint changed) used by every editor.

## Acceptance

- login required when a users file exists; wrong password refused
- `--host 0.0.0.0` without users file refused
- a save on a file modified since load is refused, nothing overwritten
