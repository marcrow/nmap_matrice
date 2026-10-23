# Segmentation v2: from POC to a reliable audit tool

Status: ready-for-agent

Vocabulary: `GLOSSARY.md`. Decisions: `docs/adr/0001..0003`.

## Goal

Turn the POC into a maintainable, offline-first tool that lets the auditor:
read the global and per-Source views (already valuable), add follow-up Scans at any time
and see clearly what was tested from where, compare Scans, spot Pivot Machines and
asymmetries, and, when a Flow Policy exists, get Findings against it.

Non-goals: generic converter for client flow matrices (conversion stays outside the tool),
full report generation (the auditor exports PNG/SVG and CSV into their own report).

## Constraints

- Offline: `report.html` stays standalone (mermaid inlined), no CDN required.
- Zero runtime dependency for the core. Dev only: `pytest`, `ruff`.
- Everything in English: code, CLI output, README, report UI, GLOSSARY.
- Tests limited to behaviour that matters (~6 tests), on real nmap output generated locally.
- The mission folder is the only state (ADR-0003).

## Mission folder

```
mission/
  inventory.csv        ip;zone;type;name[;free columns...]  header required beyond 4 columns
  flow_policy.csv      optional
  port_groups.csv      optional, defaults shipped with the tool
  scans/<src_ip>/*.xml any file name; XML is the reference format
  report/              generated
```
`seg_matrix mission/`. Legacy `-i/-s/-o` kept as overrides; legacy `scans/<ip>.{xml,gnmap,nmap}`
at the scans root still accepted.

## Stages (stop after each one to decide whether the next is still worth it)

### Stage 0: translation and bug fix
- Translate code, CLI messages, README, HTML report to English. `NON-VU` → `UNSEEN`. No behaviour change.
- `open|filtered` is never OPEN; it counts as filtered (UDP no-reply, -sF/-sN/-sX).

### Stage 1: data model
- Split into a small package (parsers / model / render / cli), `pyproject.toml`, type hints, ruff, pytest.
- Real nmap fixtures generated against throwaway Docker containers (UDP needs `sudo`, run by the user).
- Several Scans per Source combined into a Source View: most permissive state wins (ADR-0001), disagreements surfaced.
- Coverage from the XML (`scaninfo`, args, start time): distinguishes "tested, not seen" from "never tested". Other formats: Coverage marked unknown, untested ports never asserted.
- UDP handled end to end (verdicts, matrices, graphs label proto).
- Scans tab: one row per Scan (Source machine/zone, date, full command, proto, port ranges, target count, file, disagreements); Coverage per target Interface; matrix cell tooltip lists the Scans behind the verdict.
- Inventory free columns shown in tables, tooltips and exports, no logic attached.

### Stage 2: auditor reading
- Port Groups (`admin`, `db`, `web`…) from a defaults file the auditor can override; filter and highlight in views.
- Pivot Machines: Machine spanning ≥2 Zones, reached OPEN from another Zone; list Machine → Zones bridged → Zones reaching it, by which ports. One hop only.
- Asymmetry: A→B OPEN/REACHABLE while B→A BLOCKED, only when both are Sources and Coverage makes it comparable. Zone-pair level with Machine detail, in the Anomalies tab.

### Stage 3: Scan Diff
- In-browser Diff tab: pick any Scan or Source View on each side; show added / removed / unchanged / not comparable (port tested on one side only). No CLI subcommand.

### Stage 4: Flow Policy and exports
- `flow_policy.csv`: `src;dst;ports;action;comment`. `src`/`dst` = Zone, Machine or `*`. `ports` = `*`, `22,443`, `8000-8100`, `@group`, `udp:161`. `action` = `allow|deny`.
- Evaluation (ADR-0002): uncovered flow = Undeclared (shown apart, never a Finding). Precedence: src/dst specificity (Machine > Zone > `*`, src first then dst), then port specificity (explicit or `@group` > `*`), then `deny` wins.
  Example: `user;dmz;443;allow` + `user;dmz;*;deny` + `user;dc-01;*;allow` → user→dmz:22 Finding, user→dmz:443 allowed, user→dc-01:any allowed.
- Without a Flow Policy: no Findings, no policy colouring (the current cross-zone "findings" tab/file is removed). Anomalies tab kept.
- Exports: `observed_flows.csv` (one row per Source → Interface → proto/port, with IP, Machine, Zone, free columns on both sides, state, Scans) and `observed_zone_flows.csv` (per Zone pair and port, in Flow Policy format with empty `action`, to bootstrap a policy).

### Stage 5: local app (deferred)
Web framework, file-based auth, Docker, scan upload, Flow Policy editor: dedicated grilling session after stage 4. Only fixed constraint: ADR-0003.

## Explicitly out for now
Allowed-but-never-observed flows, multi-hop pivot chains, diff CLI subcommand, generic flow-matrix converter.
