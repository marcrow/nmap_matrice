# seg_matrix — segmentation matrix + Mermaid + HTML report

## Workflow

Everything for one engagement lives in a **mission folder**:
```
mission/
  inventory.csv            ip;zone;type;name
  port_groups.csv          optional, overrides the default Port Groups
  flow_policy.csv          optional, the expected flows
  scans/<source_ip>/*.xml  any file name, one folder per Source
  report/                  generated
```

1. **Inventory** `inventory.csv` (`;` separator, optional header), `type` in snake_case:
   ```
   ip;zone;type;name
   10.0.2.1;internal;vm;app-01
   ```
   Extra columns (owner, criticality, OS, notes...) are allowed and shown in the report,
   with no logic attached; a header line is then required to name them:
   `ip;zone;type;name;owner;criticality`.

   Multi-interface machines (admin, service, iLO, monitoring...): one row per
   interface, same `name`. Without a name, the machine = the IP. A duplicate IP is an error.
   ```
   10.0.2.1;T1-service;vm;app-01
   10.9.0.1;T0-admin;vm;app-01
   10.8.0.1;ilo;ilo;app-01
   ```

2. **Scans** — launched *from each Source*, stored in `scans/<source_ip>/`:
   ```bash
   mkdir -p mission/scans/$SRC_IP && cd mission/scans/$SRC_IP
   nmap -Pn -p- -oA broad <targets>          # through proxychains/SOCKS if pivoting
   nmap -Pn -p 8443,9200 -oA follow-up <ip>  # any later follow-up, any parameters
   ```
   A Source may have **any number of Scans**: they are combined into its Source View
   (the most permissive state of a port wins, see `docs/adr/0001-*`; disagreements are kept).
   Keep the **XML** output: it is the reference format, the only one telling which ports
   were tested (Coverage). For one scan written in several formats (`-oA`), xml > gnmap > nmap.
   Avoid `--open`: closed ports are what reveals a REACHABLE flow.
   `--top-ports N` works too: nmap writes the expanded port list in the XML.
   To **take a Scan out** (e.g. one that conflicts with the others, see the Conflicts table of the
   Scans tab), move its file into a sub-folder of its source folder, e.g.
   `scans/<source_ip>/excluded/`: it is no longer read, only listed as excluded.
   A source folder that is not an inventory IP is **ignored** and listed in the terminal and
   the Anomalies tab. The legacy layout `scans/<source_ip>.xml` is still accepted.

3. **Generation**:
   ```bash
   python3 -m seg_matrix mission/ --host-graph
   python3 -m seg_matrix -i inventory.csv -s ./scans/ -o ./report/   # explicit paths (override)
   ```
   Run from the repository root: no installation and no dependency needed (Python >= 3.10).
   `pip install .` also provides a `seg_matrix` command.

## Port Groups
Named sets of ports (`admin`, `directory`, `db`, `web`, `file`) shipped in
`seg_matrix/defaults/port_groups.csv`. A `mission/port_groups.csv` (`group;ports`, e.g.
`admin;22,3389,5985,udp:161`) replaces a group of the same name or adds new ones.
The **Port group** selector in the report header restricts every view (matrices, diagrams,
exposure) to the OPEN flows on that group's ports. Open `admin` ports are always highlighted:
red bar on cells, red labels on diagram edges.

## Flow Policy (optional)
Without a Flow Policy the tool shows the views and the auditor judges: there are no Findings.
With `mission/flow_policy.csv` (or `--policy FILE`), every OPEN flow is evaluated:
```
src;dst;ports;action;comment
user;dmz;443;allow;web only
user;dmz;*;deny;
user;dc-01;*;allow;the machine rule beats the zone rule
```
- `src` / `dst`: a Zone, a Machine or `*`; `ports`: `*`, `22,443`, `8000-8100`, `udp:161`,
  `@admin` (Port Group), combinable; `action`: `allow` / `deny` (empty = no decision yet, skipped).
- The most specific rule wins: src (Machine > Zone > `*`), then dst, then ports (listed > `*`);
  at equal specificity `deny` wins (`docs/adr/0002-*`).
- An explicitly denied flow is a **Finding**; a flow no rule covers is **undeclared**, never a Finding.
  In the example: user -> dmz:22 is a Finding, user -> dmz:443 and user -> dc-01:* are allowed.
- The report gains a Flow Policy tab (Findings, undeclared flows, rules and how many flows each
  decided) and colours OPEN flows by status: red denied, amber undeclared, green allowed.

## Scan Diff
The **Diff** tab compares the open ports seen by any two Scans or Source Views: over time
(same Source, before / after a fix) or across Sources (what one sees that the other does not).
A port is *added* / *removed* only if the other side tested it; otherwise it is *not comparable*
(XML Coverage required).

## Pivot Machines and asymmetric flows
- **Pivot Machines** (Global view): machines whose interfaces span several zones and that a
  Source reaches OPEN. From the Source's zone they are a one-hop path to the machine's other
  zones (e.g. a user workstation reaching the service interface of a server also in T0).
- **Asymmetric flows** (Anomalies tab): A reaches B (OPEN or closed ports) while B -> A is
  blocked, typically a one-way firewall rule. Reported only when both are Sources and both
  directions tested common ports.

## Self exclusion
All interfaces of the source machine are always removed from the results: a scan that
sees itself locally typically shows many "open" ports that would skew the matrix.

## Outputs
- `report.html`         : **standalone tabbed report** (Global view / Per source / Scans / Anomalies).
  The Scans tab lists every Scan (file, date, command, tested ports, conflicts) and the
  Coverage per target; matrix cells show in a tooltip the Scans behind their verdict.
- `matrix_hosts.md/.csv`: consolidated host -> host matrix
- `matrix_zones.md`     : consolidated zone -> zone matrix
- `exposure_targets.md` : target-oriented view (who reaches what)
- `segmentation.mmd`    : global zone Mermaid
- `mermaid/<ip>.mmd`    : per-source Mermaid
- `segmentation_hosts.mmd` : global host Mermaid (`--host-graph` option)
- `findings.md`         : Findings and undeclared flows (only with a Flow Policy)
- `observed_flows.csv`  : one row per Source -> Interface -> open port (plus reachable / alive
  pairs), with machine, zone, type and free columns on both sides, Flow Policy decision, Scans
- `observed_zone_flows.csv` : observed OPEN flows per zone pair and port **in Flow Policy format**
  with an empty `action`: fill it (allow / deny) and save it as `flow_policy.csv` to start a policy


## -Pn mode
`-Pn` scans are supported natively (and even recommended): the option is auto-detected
from the nmap file header, or can be forced with `--pn`. In -Pn mode the "host up" state
(always true) is ignored; the verdict relies only on port states (open/closed/filtered).
Benefit: blocked targets show up as `filtered` (-> blocked) instead of being absent.

## Verdicts
- `OPEN`  : >=1 open port -> service reachable
- `o`     : closed ports (RST) -> L4 flow admitted up to the host (permeable segmentation, no service)
- `~`     : alive (ping/ARP), no port getting through -> outside `-Pn` only
- `x`     : filtered / down -> blocked
- `.`     : target absent from the scan output (unseen)

## Graphs
The zone colours the background of its frame. Each multi-interface machine has its own
node colour, and its interfaces are linked by a grey dotted line; single-interface
machines stay white, bordered with the zone colour.

## HTML report (offline)
`seg_matrix/assets/mermaid.min.js` (shipped in the repo, v10.9.8) is
inlined into `report.html`: the report is self-contained and renders without network.
If it is missing, the report loads mermaid from the jsdelivr CDN (network required) and, on
failure, shows the diagram source instead of a `mermaid is not defined` error.

## Development
```bash
uv run --no-project --with pytest python -m pytest   # tests
uvx ruff check . && uvx ruff format --check .        # lint + format
```
Layout: `seg_matrix/` — `inventory.py` (CSV), `nmap.py` (discovery + parsers), `verdict.py`,
`analysis.py` (matrices), `render/` (Markdown/CSV, Mermaid, HTML + `assets/`), `cli.py`.
Domain vocabulary: `GLOSSARY.md`; decisions: `docs/adr/`.
