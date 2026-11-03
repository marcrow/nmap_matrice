# Server: segowl serve, auth, report

Status: done
Blocked by: 01
Spec: ../spec.md

## What

`segowl serve <mission_dir>` (stdlib, ADR-0004): creates the skeleton, serves the navigation shell and `report.html` regenerated on change. `segowl user add <login>` writes `~/.config/segowl/users` (scrypt). No users file → refuse non-loopback `--host`. `--cert/--key` → HTTPS. Optimistic save helper (refuse if the file fingerprint changed) used by every editor.

## Acceptance

- login required when a users file exists; wrong password refused
- `--host 0.0.0.0` without users file refused
- a save on a file modified since load is refused, nothing overwritten

## Comments

2026-11-03 done: `segowl/app.py` (stdlib server, login form with an in-memory session cookie: HttpOnly, SameSite=Strict, Secure under TLS; no native auth popup), `cli.run()` returns the summary lines so the server can reuse it, regeneration happens lazily on request whenever the Mission's file state (paths, mtimes, sizes, `report/` excluded) changes, and `save_file()` does the optimistic, atomic save for the editors. Tests in `tests/test_app.py`.
Known limits: `segowl serve`/`segowl user` take over a mission folder literally named `serve` or `user`; sessions are lost on restart.
