# Reading the report

`report/report.html` is one self-contained file: it opens without network, on the client's offline machine
too. It is regenerated whenever a Mission file changes, by hand or from the app.

## Verdicts

The verdict of a Source → Interface pair, from most permissive to most closed:

| Mark | Verdict | Meaning |
|---|---|---|
| `OPEN` | OPEN | At least one open port: a service is reachable. |
| `o` | REACHABLE | Closed ports (RST): the flow crosses the segmentation, no service listens. |
| `~` | ALIVE | Answers ping/ARP, no port gets through: scan it deeper. Never in a `-Pn` Scan. |
| `x` | BLOCKED | Down, or only filtered ports under `-Pn`. |
| `.` | UNSEEN | Absent from the scan output. |

## Two views of the same scans

**Per Zone**: every Zone pair, the open ports on each edge.

![Zone view](../img/tutorial/zone-view.svg)

**Per Source**: everything one Source reaches, grouped by Zone.

![Source view](../img/tutorial/source-view.svg)

🟥 ✕ open, denied: Finding · 🟧 ? open, undeclared · 🟩 ✓ open, allowed · dashed: reachable, no open port ·
port numbers: **bold** = admin port, red = denied by the Flow Policy.

Zones get their own hue, never red, amber or green: those belong to the Flow Policy. Each multi-interface
Machine has its own colour; single-interface Machines stay white.

## The tabs

| Tab | What you find |
|---|---|
| **Global view** | Zone diagram, Zone and host matrices |
| **Flow Policy** | Findings, undeclared flows, rules and how many flows each decided |
| **Pivot Machines** | Machines spanning several Zones that a Source reaches: one hop into their other Zones |
| **Per source** | What each Source reaches |
| **Per target** | Who reaches each target |
| **Scans** | Every Scan (file, date, command, tested ports, conflicts), Coverage per target, anomalies |
| **Diff** | Before / after, Source vs Source |

The **Port Group** chips filter every tab at once. Matrix cells show in a tooltip the Scans behind their
verdict.

### Retest: the Diff tab

![Retest compared cell by cell](../img/tutorial/retest.svg)

Compare the open ports of any two Scans or Source Views: over time (same Source, before / after a fix) or
across Sources. A port is *added* / *removed* only if the other side tested it; otherwise it is *not
comparable* (XML Coverage required).

### Asymmetric flows

In the Anomalies: A reaches B while B → A is blocked, typically a one-way firewall rule. Reported only when
both are Sources and both directions tested common ports.

## Into your own report

Diagrams have an **Export PNG** button. Next to `report.html`, the folder holds text outputs to paste or
process:

| File | Content |
|---|---|
| `matrix_zones.md` | Zone → Zone matrix |
| `matrix_hosts.md` / `.csv` | Host → host matrix |
| `exposure_targets.md` | Who reaches what, per target |
| `findings.md` | Findings and undeclared flows (with a Flow Policy) |
| `observed_flows.csv` | One row per Source → Interface → open port, with Machine, Zone, type, your columns, decision, Scans |
| `observed_zone_flows.csv` | Observed open flows in Flow Policy format, to start a policy |
| `segmentation.mmd`, `mermaid/<ip>.mmd` | Mermaid diagrams (global, per Source); `segmentation_hosts.mmd` with `--host-graph` |
