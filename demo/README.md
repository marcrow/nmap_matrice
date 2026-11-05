# Demo Mission

A complete Mission to try SegOWL without scanning anything:

```
python3 -m segowl serve demo/      # the app, http://127.0.0.1:8000/
python3 -m segowl demo/            # or the offline report only, in demo/report/
```

A fictitious company (`*.corp.local`, `10.x`) in five Zones (audit, dmz, servers, admin, users), 41 Interfaces,
scanned for real by nmap from three Sources: the auditor's laptop (audit), a jump host (dmz) and a bastion (admin).
The Flow Policy is what the "client" declares; the firewall lets more through, hence 10 Findings (database
reachable from the DMZ, iLO from the DMZ, telnet on the switch…) and undeclared flows to decide on. web-01,
monitor-01 and backup-01 sit on two Zones.

Change anything: git ignores your edits here (see below). The Scans come from the Docker lab in `lab/`
(`python3 lab/lab.py up && python3 lab/lab.py demo` rebuilds them).

Maintainers: the files are committed with `git update-index --skip-worktree`, so local edits never show up. To
commit a new version: `git ls-files demo | xargs git update-index --no-skip-worktree`, commit, then set it back.
