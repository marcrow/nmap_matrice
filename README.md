# seg_matrix — segmentation matrix + Mermaid + HTML report

## Workflow

1. **Inventory** `inventory.csv` (`;` separator, optional header), `type` in snake_case:
   ```
   ip;zone;type;name
   10.0.2.1;internal;vm;app-01
   ```

2. **Scans** — one scan *from each source*, output named after the source IP:
   ```bash
   nmap -Pn -p- --open -oA "$SRC_IP" <targets>   # through proxychains/SOCKS if pivoting
   ```
   `-oA` produces `<SRC_IP>.xml/.gnmap/.nmap`. Parsing priority: xml > gnmap > nmap.
   A file whose name is not an inventory IP is **ignored**: it is listed in the terminal
   and in the Anomalies tab ("Ignored scans").

   Multi-interface machines (admin, service, iLO, monitoring...): one row per
   interface, same `name`. Without a name, the machine = the IP. A duplicate IP is an error.
   ```
   10.0.2.1;T1-service;vm;app-01
   10.9.0.1;T0-admin;vm;app-01
   10.8.0.1;ilo;ilo;app-01
   ```

3. **Generation**:
   ```bash
   python3 -m seg_matrix -i inventory.csv -s ./scans/ -o ./report/ --host-graph
   ```
   Run from the repository root: no installation and no dependency needed (Python >= 3.10).
   `pip install .` also provides a `seg_matrix` command.

## Self exclusion
All interfaces of the source machine are always removed from the results: a scan that
sees itself locally typically shows many "open" ports that would skew the matrix.

## Outputs
- `report.html`         : **standalone tabbed report** (Global view / Per source / Anomalies)
- `matrix_hosts.md/.csv`: consolidated host -> host matrix
- `matrix_zones.md`     : consolidated zone -> zone matrix
- `exposure_targets.md` : target-oriented view (who reaches what)
- `segmentation.mmd`    : global zone Mermaid
- `mermaid/<ip>.mmd`    : per-source Mermaid
- `segmentation_hosts.mmd` : global host Mermaid (`--host-graph` option)
- `findings.md`         : cross-zone exposures + anomalies


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
