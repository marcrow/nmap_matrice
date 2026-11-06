# Getting started

## Install

Python 3.10+ and nothing else: no dependency, no database. nmap is only needed on the machines you scan from.

```bash
git clone https://github.com/marcrow/segowl.git && cd segowl
python3 -m segowl serve demo/        # the app on http://127.0.0.1:8000/
```

Run it from the repository root. `pip install .` also provides a `segowl` command.

## Try the demo

`demo/` is a complete Mission: a fictitious company (`*.corp.local`, `10.x`) in five Zones, 41 Interfaces,
scanned for real from three Sources (the auditor's laptop, a jump host in the DMZ, a bastion in admin). The Flow
Policy is what the "client" declares; the firewall lets more through, hence 10 Findings and undeclared flows to
decide on.

```bash
python3 -m segowl serve demo/      # the app
python3 -m segowl demo/            # or the offline report only, in demo/report/
```

!!! tip "Break it freely"
    git ignores your edits in `demo/`: change the inventory, the policy, drop scans, nothing shows up in
    `git status`.

## Your own Mission

```bash
python3 -m segowl serve ~/missions/acme/   # folder created if missing
```

The **Overview** page lists the steps of the audit and ticks them as you go. The menu follows the audit
order:

| Menu | What you do there |
|---|---|
| **Overview** | Where you stand: the checklist of the audit path. |
| **Inventory & Zones** | Paste or edit the inventory, take the names from the Scans. |
| **Auditor Kit** | Your tooling, carried from Mission to Mission: Scan Profiles, Port Groups, Port Labels, Kits. |
| **Scans** | Build the nmap command, download one script per Source, drop the results. |
| **Flow Policy** | Decide, Zone by Zone, what may cross. |
| **Report** | The report, regenerated whenever a Mission file changes. |

The app reads and writes the Mission folder and nothing else: you can edit the files by hand, the app and the
report follow.

## Report only, no app

```bash
python3 -m segowl ~/missions/acme/ --host-graph
python3 -m segowl -i inventory.csv -s ./scans/ -o ./report/   # explicit paths
```

## A shared server

By default the app listens on loopback only, without login. To share it with a team:

```bash
python3 -m segowl user add alice     # login is now required
python3 -m segowl serve mission/ --host 0.0.0.0 --cert cert.pem --key key.pem   # HTTPS
```

Accounts, certificates, sessions: [Team server and login](team-server.md).
