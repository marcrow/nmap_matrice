#!/usr/bin/env python3
"""
seg_matrix.py — Segmentation matrix & Mermaid diagrams for network segmentation testing.

PRINCIPLE
---------
For each "source" host in the inventory, an nmap scan is launched *from* that host
(SSH/SOCKS pivot, local agent, etc.) towards the rest of the perimeter. The nmap output
is named after the source IP: <source_ip>.xml | .gnmap | .nmap.
A single `nmap -oA <source_ip> ...` produces all three formats at once.

The script cross-checks each scan with the CSV inventory (ip;zone;type;name) and writes:
  - matrix_hosts.md / .csv    : consolidated host -> host matrix
  - matrix_zones.md           : consolidated zone -> zone matrix
  - exposure_targets.md       : target-oriented view (who reaches what)
  - segmentation.mmd          : global zone Mermaid
  - mermaid/<ip>.mmd          : per-source Mermaid
  - findings.md               : cross-zone exposures + anomalies
  - report.html               : standalone tabbed report (Global / Per source / Anomalies)
    (mermaid.min.js next to the script is inlined -> viewable offline; otherwise CDN)

MULTI-INTERFACE MACHINES & SELF EXCLUSION
-----------------------------------------
Each inventory row is an interface (one IP in one zone). Rows sharing the same `name`
form a machine (no name: machine = IP). All interfaces of the source machine are
excluded from its scan (it sees itself locally).
A duplicate IP in the inventory is an error.

SEGMENTATION SEMANTICS
----------------------
  OPEN       : >=1 "open" port        -> service reachable (effective access)
  REACHABLE  : no open but closed     -> RST received, the L4 flow crosses the segmentation
  ALIVE      : no port, host up       -> answers at L3/L2 (ping/ARP); never with -Pn
  BLOCKED    : "filtered" only        -> flow blocked (isolation OK) / host down
  UNSEEN     : target absent from the scan output

USAGE
-----
  python3 seg_matrix.py -i inventory.csv -s ./scans/ -o ./report/
  python3 seg_matrix.py -i inventory.csv -s ./scans/ --host-graph
"""

from __future__ import annotations

import argparse
import colorsys
import csv
import html
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

OPEN, REACH, ALIVE, BLOCK, NODATA = 3, 2, 1, 0, -1
VERDICT_NAME = {OPEN: "OPEN", REACH: "REACHABLE", ALIVE: "ALIVE", BLOCK: "BLOCKED", NODATA: "UNSEEN"}
SYM = {OPEN: "OPEN", REACH: "o", ALIVE: "~", BLOCK: "x", NODATA: "."}
VCLASS = {OPEN: "v-open", REACH: "v-reach", ALIVE: "v-alive", BLOCK: "v-block", NODATA: "v-none"}
SCAN_EXT_PRIORITY = (".xml", ".gnmap", ".nmap")
MERMAID_JS = Path(__file__).with_name("mermaid.min.js")   # present -> inlined in report.html (offline)
MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"

# Zone palette (fill, stroke, text) — modern, cyclic
ZONE_COLORS = [
    ("#eef5ff", "#3b82f6", "#1e3a5f"),  # blue
    ("#eafaf1", "#22a565", "#14532d"),  # green
    ("#fff4e6", "#f59e0b", "#7c4a03"),  # amber
    ("#fdeef4", "#db2777", "#7a1840"),  # pink
    ("#f1eefe", "#7c3aed", "#3f2a7a"),  # violet
    ("#e6fbf8", "#14b8a6", "#115e59"),  # teal
    ("#fef0f0", "#ef4444", "#7f1d1d"),  # red
]

# Mermaid init directive (theme, font). 'linear' curve is mandatory: Mermaid puts the label in
# the middle of the dagre polyline, and 'basis' smooths the path beside it (label off by one link).
MERMAID_INIT = (
    "%%{init: {'theme':'base','themeVariables':{"
    "'fontFamily':'ui-sans-serif,-apple-system,Segoe UI,Roboto,sans-serif',"
    "'fontSize':'13px','lineColor':'#94a3b8'},"
    "'flowchart':{'curve':'linear','htmlLabels':true,"
    "'nodeSpacing':40,'rankSpacing':60,'padding':8}}}%%"
)


def _write(out_dir: str, name: str, text: str) -> str:
    path = Path(out_dir, name)
    path.write_text(text + "\n", encoding="utf-8")
    return str(path)


def zone_palette(inv) -> Dict[str, Tuple[str, str, str]]:
    zones = sorted({h.zone for h in inv.values()})
    return {z: ZONE_COLORS[i % len(ZONE_COLORS)] for i, z in enumerate(zones)}


def machine_palette(inv) -> Dict[str, Tuple[str, str, str]]:
    """Own colour (fill, stroke, text) per multi-interface machine; golden-angle hues."""
    count = defaultdict(int)
    for h in inv.values():
        count[h.machine] += 1
    multi = sorted(m for m, n in count.items() if n > 1)

    def hexc(h, l, s):
        return "#" + "".join(f"{round(c * 255):02x}" for c in colorsys.hls_to_rgb(h, l, s))
    return {m: (hexc(i * 0.618 % 1, .85, .75), hexc(i * 0.618 % 1, .40, .70), hexc(i * 0.618 % 1, .20, .60))
            for i, m in enumerate(multi)}


def ordered_ips(inv) -> List[str]:
    """Inventory IPs, interfaces of the same machine side by side (first-appearance order)."""
    rank = {m: i for i, m in enumerate(dict.fromkeys(h.machine for h in inv.values()))}
    return sorted(inv, key=lambda ip: rank[inv[ip].machine])


def detect_pn(path: str) -> bool:
    """Detect the -Pn option in the nmap file header (xml args / gnmap comment)."""
    try:
        head = open(path, encoding="utf-8", errors="replace").read(4096)
    except OSError:
        return False
    return bool(re.search(r'(?:^|[\s"])-Pn(?:[\s"]|$)', head))


# =============================================================================
# Inventory
# =============================================================================
@dataclass
class Host:
    ip: str
    zone: str
    htype: str
    name: str

    @property
    def machine(self) -> str:
        return self.name or self.ip

    @property
    def short(self) -> str:
        return f"{self.name} · {self.ip}" if self.name else self.ip


def load_inventory(path: str) -> Dict[str, Host]:
    hosts: Dict[str, Host] = {}
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as fh:
        for row in csv.reader(fh, delimiter=";"):
            row = [c.strip() for c in row]
            if not row or not row[0]:
                continue
            if row[0].lower() in ("ip", "adresse", "address"):
                continue
            ip = row[0]
            if ip in hosts:
                sys.exit(f"[!] Duplicate IP in {path}: {ip} ({hosts[ip].zone}/{hosts[ip].name} "
                         f"and {';'.join(row[1:])}) — an interface belongs to exactly one zone")
            hosts[ip] = Host(
                ip=ip,
                zone=row[1] if len(row) > 1 else "?",
                htype=row[2] if len(row) > 2 else "?",
                name=row[3] if len(row) > 3 else "",
            )
    if not hosts:
        sys.exit(f"[!] No host loaded from {path} (expected: ip;zone;type;name)")
    return hosts


# =============================================================================
# nmap discovery & parsing
# =============================================================================
def discover_scans(scan_dir: str) -> Dict[str, str]:
    by_ip: Dict[str, Dict[str, str]] = defaultdict(dict)
    for entry in os.listdir(scan_dir):
        full = os.path.join(scan_dir, entry)
        if not os.path.isfile(full):
            continue
        base, ext = os.path.splitext(entry)
        ext = ext.lower()
        if ext in SCAN_EXT_PRIORITY:
            by_ip[base][ext] = full
    chosen: Dict[str, str] = {}
    for ip, variants in by_ip.items():
        for ext in SCAN_EXT_PRIORITY:
            if ext in variants:
                chosen[ip] = variants[ext]
                break
    return chosen


def parse_xml(path: str) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        print(f"[!] Unreadable XML {path}: {e}", file=sys.stderr)
        return out
    for host in root.iter("host"):
        st = host.find("status")
        state = st.get("state") if st is not None else None
        a = host.find("address[@addrtype='ipv4']")
        if a is None:
            a = host.find("address[@addrtype='ipv6']")
        if a is None:
            continue
        rec = out.setdefault(a.get("addr"), {"state": state, "ports": [], "ignored": []})
        rec["state"] = state or rec["state"]
        ports = host.find("ports")
        if ports is not None:
            for ep in ports.findall("extraports"):
                rec["ignored"].append((ep.get("state"), int(ep.get("count", "0") or 0)))
            for p in ports.findall("port"):
                pst = p.find("state")
                rec["ports"].append((int(p.get("portid")), p.get("protocol"),
                                     pst.get("state") if pst is not None else "unknown"))
    return out


_GNMAP_HOST = re.compile(r"Host:\s+(\S+)\s+\([^)]*\)\s+(.*)")
_GNMAP_IGNORED = re.compile(r"(\w+)\s+\((\d+)\)")


def parse_gnmap(path: str) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        if not line.startswith("Host: "):
            continue
        m = _GNMAP_HOST.match(line)
        if not m:
            continue
        ip, rest = m.group(1), m.group(2)
        rec = out.setdefault(ip, {"state": None, "ports": [], "ignored": []})
        if rest.startswith("Status:"):
            rec["state"] = rest.split("Status:", 1)[1].strip().lower()
        elif rest.startswith("Ports:"):
            rec["state"] = rec["state"] or "up"
            ports_part = rest[len("Ports:"):]
            if "\tIgnored State:" in ports_part:
                ports_part, ig = ports_part.split("\tIgnored State:", 1)
                im = _GNMAP_IGNORED.search(ig)
                if im:
                    rec["ignored"].append((im.group(1), int(im.group(2))))
            for tok in ports_part.split(","):
                tok = tok.strip()
                parts = tok.split("/")
                if len(parts) < 3:
                    continue
                try:
                    rec["ports"].append((int(parts[0]), parts[2], parts[1]))
                except ValueError:
                    continue
    return out


def parse_nmap_classic(path: str) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    cur: Optional[str] = None
    ip_re = re.compile(r"Nmap scan report for (?:.*\()?(\d+\.\d+\.\d+\.\d+)\)?")
    port_re = re.compile(r"^(\d+)/(\w+)\s+(\w+)")
    for line in open(path, encoding="utf-8", errors="replace"):
        m = ip_re.search(line)
        if m:
            cur = m.group(1)
            out.setdefault(cur, {"state": "up", "ports": [], "ignored": []})
            continue
        if cur and "Host is up" in line:
            out[cur]["state"] = "up"
        pm = port_re.match(line.strip())
        if cur and pm:
            out[cur]["ports"].append((int(pm.group(1)), pm.group(2), pm.group(3)))
    return out


def parse_scan(path: str) -> Dict[str, dict]:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".xml":
        return parse_xml(path)
    if ext == ".gnmap":
        return parse_gnmap(path)
    return parse_nmap_classic(path)


# =============================================================================
# Classification
# =============================================================================
@dataclass
class Cell:
    verdict: int = NODATA
    open_ports: List[Tuple[int, str]] = field(default_factory=list)


def classify(rec: Optional[dict], pn: bool) -> Cell:
    if rec is None:
        return Cell()
    # open|filtered = no reply (UDP, -sF/-sN/-sX): proves nothing got through, counts as filtered
    open_ports = sorted({(pid, proto) for (pid, proto, s) in rec["ports"] if s == "open"})
    closed = sum(1 for (_, _, s) in rec["ports"] if s == "closed")
    filtered = sum(1 for (_, _, s) in rec["ports"] if s in ("filtered", "open|filtered"))
    for (s, c) in rec["ignored"]:
        if s == "closed":
            closed += c
        elif s in ("filtered", "open|filtered"):
            filtered += c
    up = rec.get("state") == "up"
    if open_ports:
        v = OPEN
    elif closed > 0:
        v = REACH
    elif filtered > 0:
        v = BLOCK
    elif not pn:
        v = ALIVE if up else BLOCK   # answers at L3/L2 (ping/ARP) with no port getting through
    else:
        v = NODATA         # -Pn: 'host up' carries no information, no usable port data
    return Cell(v, open_ports)


def _cell_txt(c: Cell) -> str:
    if c.verdict == OPEN:
        return ",".join(str(p) for p, _ in c.open_ports) or "OPEN"
    return SYM[c.verdict]


def _zone_cell(a) -> Tuple[str, str]:
    """(css class, text) of a zone -> zone cell, without the pair counter."""
    if not a:
        return "v-none", "."
    if a.reach_pairs == 0:
        return "v-block", "x"
    ports = ",".join(str(p) for p in sorted(a.open_ports)[:6])
    return VCLASS[a.verdict], f"{'OPEN' if a.verdict == OPEN else 'o'} {ports}".strip()


# =============================================================================
# Matrix
# =============================================================================
def build_matrix(inv, scans, force_pn=False) -> Tuple[Dict[str, Dict[str, Cell]], List[str], List[str], int]:
    parsed = {ip: parse_scan(path) for ip, path in scans.items()}
    pn_of = {ip: (True if force_pn else detect_pn(path)) for ip, path in scans.items()}
    matrix: Dict[str, Dict[str, Cell]] = {}
    unknown: Set[str] = set()
    for src in inv:
        if src not in parsed:
            continue
        pn = pn_of[src]
        self_ips = {ip for ip, h in inv.items() if h.machine == inv[src].machine}
        seen = parsed[src]
        for dip, rec in seen.items():
            if dip in self_ips or dip in inv:
                continue
            if classify(rec, pn).verdict >= ALIVE:
                unknown.add(dip)
        row = {dst: classify(seen.get(dst), pn) for dst in inv if dst not in self_ips}
        matrix[src] = row
    missing = sorted(ip for ip in inv if ip not in scans)
    pn_count = sum(1 for ip in matrix if pn_of.get(ip))
    return matrix, missing, sorted(unknown), pn_count


@dataclass
class ZoneAgg:
    verdict: int = BLOCK
    open_ports: Set[int] = field(default_factory=set)
    reach_pairs: int = 0
    total_pairs: int = 0


def aggregate_zones(matrix, inv) -> Dict[Tuple[str, str], ZoneAgg]:
    agg: Dict[Tuple[str, str], ZoneAgg] = defaultdict(ZoneAgg)
    for s, row in matrix.items():
        zs = inv[s].zone
        for d, c in row.items():
            a = agg[(zs, inv[d].zone)]
            a.total_pairs += 1
            if c.verdict >= REACH:
                a.reach_pairs += 1
                a.verdict = max(a.verdict, c.verdict)
                a.open_ports.update(p for p, _ in c.open_ports)
    return agg


# =============================================================================
# Mermaid helpers
# =============================================================================
def _zid(z): return "Z_" + re.sub(r"[^A-Za-z0-9]", "_", z)
def _hid(ip): return "H_" + ip.replace(".", "_").replace(":", "_")
def _safe(s): return str(s).replace('"', "'").replace("|", "/")


def _ports_label(ports, cap=6):
    ps = sorted(ports)
    s = ",".join(str(p) for p in ps[:cap])
    return s + ",..." if len(ps) > cap else s


def _edge(a, b, verdict, cross, label, idx, w_open="2.5px", w_reach="2px"):
    """Mermaid edge + its linkStyle: solid red/green if OPEN, dashed amber/grey otherwise."""
    if verdict == OPEN:
        col = "#e11d48" if cross else "#16a34a"
        return (f'  {a} ==>|"{_safe(label)}"| {b}',
                f"  linkStyle {idx} stroke:{col},stroke-width:{w_open},stroke-linecap:round;")
    col = "#f59e0b" if cross else "#94a3b8"
    return (f'  {a} -.->|"{_safe(label)}"| {b}',
            f"  linkStyle {idx} stroke:{col},stroke-width:{w_reach},stroke-dasharray:5 4,stroke-linecap:round;")


def _zone_subgraphs(zones, inv, node_label) -> List[str]:
    """classDef + subgraph per zone; zones = {zone: [ip]}, node_label(ip) -> node text.
    The zone colours the subgraph background; the node takes its machine colour if it is
    multi-interface, otherwise a white fill bordered with the zone colour."""
    pal, mpal = zone_palette(inv), machine_palette(inv)
    L = []
    for z in sorted(zones):
        f, s, t = pal[z]
        L.append(f'  classDef z_{_zid(z)} fill:#ffffff,stroke:{s},stroke-width:1.5px,color:{t};')
    for m, (f, s, t) in sorted(mpal.items()):
        L.append(f'  classDef m_{_zid(m)} fill:{f},stroke:{s},stroke-width:2px,color:{t};')
    for z, ips in sorted(zones.items()):
        f, s, t = pal[z]
        L.append(f'  subgraph {_zid(z)}["{_safe(z)}"]')
        L += [f'    {_hid(ip)}("{node_label(ip)}"):::'
              + (f"m_{_zid(inv[ip].machine)}" if inv[ip].machine in mpal else f"z_{_zid(z)}") for ip in ips]
        L.append("  end")
        L.append(f'  style {_zid(z)} fill:{f}aa,stroke:{s},stroke-width:1px,color:{t}')
    return L


def _machine_links(ips, inv, idx):
    """Grey dotted line without arrow between interfaces of the same machine present in the graph."""
    by_m = defaultdict(list)
    for ip in ips:
        by_m[inv[ip].machine].append(ip)
    lines, styles = [], []
    for group in by_m.values():
        for a, b in zip(group, group[1:]):
            lines.append(f"  {_hid(a)} -.- {_hid(b)}")
            styles.append(f"  linkStyle {idx + len(styles)} stroke:#94a3b8,stroke-width:1px,stroke-dasharray:2 3;")
    return lines, styles


def mermaid_zone(agg, inv) -> str:
    pal = zone_palette(inv)
    L = [MERMAID_INIT, "flowchart LR"]
    for z, (f, s, t) in sorted(pal.items()):
        L.append(f'  {_zid(z)}(["{_safe(z)}"])')
        L.append(f'  style {_zid(z)} fill:{f},stroke:{s},stroke-width:2px,color:{t}')
    styles = []
    for (zs, zd), a in sorted(agg.items()):
        if a.reach_pairs == 0:
            continue
        label = _ports_label(a.open_ports) if a.open_ports else f"{a.reach_pairs} host(s)"
        line, style = _edge(_zid(zs), _zid(zd), a.verdict, zs != zd, label, len(styles))
        L.append(line)
        styles.append(style)
    return "\n".join(L + styles)


def mermaid_source(src, row, inv) -> str:
    """Modern radial view: source (hexagon) + reachable targets, grouped/tinted by zone."""
    reach = {d: c for d, c in row.items() if c.verdict >= REACH}
    if not reach:
        return (MERMAID_INIT + "\nflowchart LR\n"
                f'  S{{{{"{_safe(inv[src].short)}<br/><small>no reachable target</small>"}}}}\n'
                "  style S fill:#1f2937,stroke:#0f172a,stroke-width:2px,color:#ffffff")
    zones = defaultdict(list)
    for d in reach:
        zones[inv[d].zone].append(d)
    L = [MERMAID_INIT, "flowchart LR",
         f'  S{{{{"{_safe(inv[src].short)}<br/><small>{_safe(inv[src].zone)} · source</small>"}}}}',
         "  style S fill:#1f2937,stroke:#0f172a,stroke-width:2px,color:#ffffff"]
    L += _zone_subgraphs(zones, inv,
                         lambda ip: f"{_safe(inv[ip].short)}<br/><small>{_safe(inv[ip].htype)}</small>")
    styles = []
    for d, c in reach.items():
        label = _ports_label([p for p, _ in c.open_ports]) if c.verdict == OPEN else "reachable"
        line, style = _edge("S", _hid(d), c.verdict, inv[src].zone != inv[d].zone, label, len(styles))
        L.append(line)
        styles.append(style)
    ml, ms = _machine_links(list(reach), inv, len(styles))
    return "\n".join(L + ml + styles + ms)


def mermaid_hosts(matrix, inv) -> str:
    zones = defaultdict(list)
    for ip in ordered_ips(inv):
        zones[inv[ip].zone].append(ip)
    L = [MERMAID_INIT, "flowchart LR"]
    L += _zone_subgraphs(zones, inv, lambda ip: _safe(inv[ip].short))
    styles = []
    for s, row in matrix.items():
        for d, c in row.items():
            if c.verdict != OPEN:
                continue
            line, style = _edge(_hid(s), _hid(d), OPEN, inv[s].zone != inv[d].zone,
                                _ports_label([p for p, _ in c.open_ports]), len(styles), w_open="2px")
            L.append(line)
            styles.append(style)
    ml, ms = _machine_links(ordered_ips(inv), inv, len(styles))
    return "\n".join(L + ml + styles + ms)


# =============================================================================
# Markdown / csv outputs
# =============================================================================
def write_host_matrix_md(matrix, inv, out_dir):
    dsts = ordered_ips(inv)
    srcs = [ip for ip in dsts if ip in matrix]
    with open(os.path.join(out_dir, "matrix_hosts.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["source", "destination", "src_zone", "dst_zone", "verdict", "open_ports"])
        for s in srcs:
            for d in dsts:
                if inv[d].machine == inv[s].machine:
                    continue
                c = matrix[s].get(d, Cell())
                w.writerow([s, d, inv[s].zone, inv[d].zone, VERDICT_NAME[c.verdict],
                            ",".join(str(p) for p, _ in c.open_ports)])
    lines = ["# Consolidated host -> host matrix", "",
             "Legend: `OPEN`=service reachable | `o`=reachable (closed) | `~`=alive (ping/ARP) | "
             "`x`=blocked | `.`=unseen | `-`=same machine", "",
             "| source \\ target | " + " | ".join(inv[d].short for d in dsts) + " |",
             "|" + "---|" * (len(dsts) + 1)]
    for s in srcs:
        cells = []
        for d in dsts:
            if inv[d].machine == inv[s].machine:
                cells.append("-")
                continue
            cells.append(_cell_txt(matrix[s].get(d, Cell())))
        lines.append(f"| **{inv[s].short}** | " + " | ".join(cells) + " |")
    _write(out_dir, "matrix_hosts.md", "\n".join(lines))


def write_zone_matrix_md(agg, inv, out_dir):
    zones = sorted(zone_palette(inv))
    md = ["# Consolidated zone -> zone matrix", "",
          "| src \\ dst | " + " | ".join(zones) + " |", "|" + "---|" * (len(zones) + 1)]
    for zs in zones:
        cells = []
        for zd in zones:
            a = agg.get((zs, zd))
            _, txt = _zone_cell(a)
            cells.append(txt + (f" ({a.reach_pairs}/{a.total_pairs})" if a and a.reach_pairs else ""))
        md.append(f"| **{zs}** | " + " | ".join(cells) + " |")
    _write(out_dir, "matrix_zones.md", "\n".join(md))


def target_exposure(matrix, inv):
    """For each target: OPEN sources (with ports) and REACH sources."""
    exp = {}
    for d in inv:
        opens, reach = [], []
        for s, row in matrix.items():
            c = row.get(d)
            if not c:
                continue
            if c.verdict == OPEN:
                opens.append((s, [p for p, _ in c.open_ports]))
            elif c.verdict == REACH:
                reach.append(s)
        exp[d] = (opens, reach)
    return exp


def write_exposure_md(exp, inv, out_dir):
    lines = ["# Exposure per target (who reaches what)", ""]
    for d in inv:
        opens, reach = exp[d]
        if not opens and not reach:
            continue
        lines.append(f"## {inv[d].short} — {inv[d].ip} ({inv[d].zone}/{inv[d].htype})")
        for s, ports in opens:
            lines.append(f"- OPEN from **{inv[s].short}** ({inv[s].zone}): {','.join(map(str, ports))}")
        for s in reach:
            lines.append(f"- reachable (closed) from {inv[s].short} ({inv[s].zone})")
        lines.append("")
    _write(out_dir, "exposure_targets.md", "\n".join(lines))


def write_findings_md(matrix, inv, missing, unknown, orphan, out_dir):
    lines = ["# Segmentation summary", "", "## Cross-zone exposures (effective access)", "",
             "| src zone | dst zone | source | target | open ports |", "|---|---|---|---|---|"]
    rows = []
    for s, row in matrix.items():
        for d, c in row.items():
            if inv[s].zone != inv[d].zone and c.verdict == OPEN:
                rows.append((inv[s].zone, inv[d].zone, inv[s].short, inv[d].short,
                             ",".join(str(p) for p, _ in c.open_ports)))
    lines += [f"| {a} | {b} | {x} | {y} | {p} |" for a, b, x, y, p in sorted(rows)] or ["_None._"]
    lines += ["", "## Coverage anomalies", ""]
    if missing:
        lines.append("**Sources without scan:**")
        lines += [f"- {ip} ({inv[ip].short}, {inv[ip].zone})" for ip in missing]
        lines.append("")
    if unknown:
        lines.append("**Reachable hosts outside the inventory:**")
        lines += [f"- {ip}" for ip in unknown]
        lines.append("")
    if orphan:
        lines.append("**Ignored scans (file name is not a source IP of the inventory):**")
        lines += [f"- {ip}.*" for ip in orphan]
    if not missing and not unknown and not orphan:
        lines.append("_Full coverage._")
    _write(out_dir, "findings.md", "\n".join(lines))


# =============================================================================
# Standalone tabbed HTML rendering
# =============================================================================
HTML_CSS = """
:root{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;}
body{margin:0;background:#f7f8fa;color:#1c2430;}
header{background:#13223a;color:#fff;padding:14px 22px;}
header h1{margin:0;font-size:18px;}
header .meta{font-size:12px;opacity:.8;margin-top:3px;}
.tabs{display:flex;gap:4px;background:#26344e;padding:0 12px;}
.tab{background:none;border:none;color:#cbd5e6;padding:11px 16px;cursor:pointer;font-size:14px;border-bottom:3px solid transparent;}
.tab:hover{color:#fff;}
.tab.active{color:#fff;border-bottom-color:#ffb547;font-weight:600;}
.pane{display:none;padding:20px 22px;max-width:100%;}
.pane.active{display:block;}
h2{font-size:16px;margin:22px 0 8px;}
h3{font-size:14px;margin:16px 0 6px;color:#33415c;}
.legend{font-size:12px;color:#5a6678;margin:6px 0 14px;}
.legend span{display:inline-block;padding:2px 7px;border-radius:4px;margin-right:6px;}
.tablewrap{overflow:auto;border:1px solid #e1e5ec;border-radius:8px;max-height:70vh;background:#fff;}
table{border-collapse:collapse;font-size:12px;width:max-content;}
th,td{border:1px solid #e7eaf0;padding:5px 8px;text-align:center;white-space:nowrap;}
thead th{position:sticky;top:0;background:#eef1f6;z-index:2;}
tbody th{position:sticky;left:0;background:#f3f5f9;text-align:left;z-index:1;}
.v-open{background:#d7f5dd;color:#04611f;font-weight:600;}
.v-reach{background:#fdebcf;color:#8a5200;}
.v-alive{background:#e4ecf7;color:#3b5578;}
.v-block{background:#f6dada;color:#8a1a1a;}
.v-none{background:#f1f1f3;color:#9aa3b2;}
.v-self{background:#e9eef6;color:#5a6b86;}
.mermaid{background:#fff;border:1px solid #e1e5ec;border-radius:8px;padding:10px;margin:8px 0;overflow:auto;font-family:inherit;}  /* pre is monospace otherwise: labels measured in sans-serif then truncated */
.err{color:#c0392b;font-size:12px;white-space:pre-wrap;}
select{padding:6px 10px;font-size:14px;border-radius:6px;border:1px solid #c3cad6;margin:6px 0 12px;}
.card{background:#fff;border:1px solid #e1e5ec;border-radius:8px;padding:12px 14px;margin:8px 0;font-size:13px;}
.tag{display:inline-block;background:#eef1f6;border-radius:4px;padding:1px 6px;font-size:11px;margin-left:6px;color:#5a6678;}
ul{margin:4px 0 4px 18px;padding:0;font-size:13px;}
.warn{color:#b5651d;font-weight:600;}
.srcbar{font-size:13px;margin:4px 0;display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center;}
.srcbar label{cursor:pointer;}
.srcbar button{padding:4px 10px;border-radius:6px;border:1px solid #c3cad6;background:#fff;cursor:pointer;}
"""

HTML_JS = r"""
const HAS_MM = typeof mermaid !== 'undefined';
if(HAS_MM) mermaid.initialize({startOnLoad:false, securityLevel:'loose', theme:'default', flowchart:{htmlLabels:true}});
let idc=0;
async function renderVisible(scope){
  if(!scope) return;
  for(const el of [...scope.querySelectorAll('.mermaid:not([data-done])')]){
    if(el.offsetParent===null) continue;
    el.setAttribute('data-done','1');
    if(!HAS_MM){el.innerHTML='<b class="err">mermaid.js not loaded (offline? put mermaid.min.js next to seg_matrix.py); diagram source:</b><br>'+el.innerHTML; continue;}
    el.dataset.src=el.textContent;
    try{const {svg}=await mermaid.render('mm'+(idc++), el.textContent); el.innerHTML=svg;}
    catch(e){el.innerHTML='<pre class="err">'+String(e)+'</pre>';}
  }
}
function showTab(id){
  document.querySelectorAll('.pane').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('tab-'+id).classList.add('active');
  document.querySelector('.tab[data-tab="'+id+'"]').classList.add('active');
  renderVisible(document.getElementById('tab-'+id));
}
function showSource(key){
  document.querySelectorAll('.srcpane').forEach(p=>p.style.display='none');
  const el=document.getElementById(key);
  if(el){el.style.display='block'; renderVisible(el);}
}
// Removes from the Mermaid source the subgraphs of unchecked zones (off = Set of Z_* ids), their edges,
// and renumbers the linkStyle lines (index = order of edges in the source).
function filterZones(src, off){
  const lines=src.split('\n'), drop=new Set(), out=[], styles=[], keep=[];
  let cur=null;
  const sub=l=>(l.match(/^\s*subgraph (\w+)\[/)||[])[1], isEnd=l=>/^\s*end\s*$/.test(l);
  for(const l of lines){
    if(sub(l)){cur=sub(l);continue;} if(isEnd(l)){cur=null;continue;}
    const n=l.match(/^\s*(H_\w+)\(/); if(n && off.has(cur)) drop.add(n[1]);
  }
  cur=null;
  for(const l of lines){
    if(sub(l)) cur=sub(l);
    const skip=cur!==null && off.has(cur);
    if(isEnd(l)) cur=null;
    if(skip) continue;
    const st=l.match(/^\s*style (\w+)/); if(st && off.has(st[1])) continue;
    if(/^\s*linkStyle /.test(l)){styles.push(l);continue;}
    if(/(==>|-\.-)/.test(l)){
      const p=l.trim().split(/\s+/), ok=!drop.has(p[0]) && !drop.has(p[p.length-1]);
      keep.push(ok); if(ok) out.push(l); continue;
    }
    out.push(l);
  }
  let k=0;
  styles.forEach((s,i)=>{ if(keep[i]) out.push(s.replace(/linkStyle \d+/, 'linkStyle '+(k++))); });
  return out.join('\n');
}
async function refilter(cb){
  const pane=cb.closest('.srcpane'), el=pane.querySelector('.mermaid');
  if(!HAS_MM || !el.dataset.src) return;
  const off=new Set([...pane.querySelectorAll('.srcbar input:not(:checked)')].map(i=>i.value));
  try{const {svg}=await mermaid.render('mm'+(idc++), filterZones(el.dataset.src, off)); el.innerHTML=svg;}
  catch(e){el.innerHTML='<pre class="err">'+String(e)+'</pre>';}
}
function dl(name, url){const a=document.createElement('a'); a.href=url; a.download=name; a.click();}
// Exports the displayed (thus filtered) diagram; fully local, no network.
function exportImg(btn, fmt){
  const bar=btn.closest('.srcbar'), s=bar.closest('.srcpane').querySelector('.mermaid svg');
  if(!s) return;
  const zs=[...bar.querySelectorAll('input:checked')].map(i=>i.parentNode.textContent.trim());
  const all=bar.querySelectorAll('input').length===zs.length;
  const name=(bar.dataset.name+(all?'':'_'+zs.join('-'))).replace(/[^\w.-]+/g,'_');
  const vb=s.viewBox.baseVal, w=Math.ceil(vb.width), h=Math.ceil(vb.height);
  const c=s.cloneNode(true);
  c.setAttribute('xmlns','http://www.w3.org/2000/svg');
  c.setAttribute('width',w); c.setAttribute('height',h);
  c.setAttribute('style','font-family:'+getComputedStyle(document.body).fontFamily+';background:#fff');
  const x=new XMLSerializer().serializeToString(c);
  if(fmt==='svg'){dl(name+'.svg', URL.createObjectURL(new Blob([x],{type:'image/svg+xml'}))); return;}
  const img=new Image();
  img.onload=()=>{
    const k=2, cv=document.createElement('canvas'); cv.width=w*k; cv.height=h*k;
    const g=cv.getContext('2d'); g.fillStyle='#fff'; g.fillRect(0,0,cv.width,cv.height);
    g.scale(k,k); g.drawImage(img,0,0,w,h);
    try{cv.toBlob(b=>dl(name+'.png', URL.createObjectURL(b)));}
    catch(e){alert('PNG refused by this browser (HTML labels): use the SVG export.');}
  };
  img.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(x);
}
window.addEventListener('DOMContentLoaded',()=>renderVisible(document.getElementById('tab-global')));
"""


def _cell_html(c: Cell) -> str:
    return f'<td class="{VCLASS[c.verdict]}">{html.escape(_cell_txt(c))}</td>'


def _host_matrix_html(matrix, inv) -> str:
    dsts = ordered_ips(inv)
    srcs = [ip for ip in dsts if ip in matrix]
    mpal = machine_palette(inv)

    def th(ip):
        m = mpal.get(inv[ip].machine)
        style = f' style="background:{m[0]};color:{m[2]}"' if m else ""
        return f"<th{style}>{html.escape(inv[ip].short)}</th>"
    head = "".join(th(d) for d in dsts)
    rows = []
    for s in srcs:
        cells = []
        for d in dsts:
            if inv[d].machine == inv[s].machine:
                cells.append('<td class="v-self">-</td>')
            else:
                cells.append(_cell_html(matrix[s].get(d, Cell())))
        rows.append(f'<tr>{th(s)}{"".join(cells)}</tr>')
    return (f'<div class="tablewrap"><table><thead><tr><th>source \\ target</th>{head}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


def _zone_matrix_html(agg, inv) -> str:
    zones = sorted(zone_palette(inv))
    head = "".join(f"<th>{html.escape(z)}</th>" for z in zones)
    rows = []
    for zs in zones:
        cells = []
        for zd in zones:
            a = agg.get((zs, zd))
            cls, txt = _zone_cell(a)
            pairs = f"<br><small>{a.reach_pairs}/{a.total_pairs}</small>" if a and a.reach_pairs else ""
            cells.append(f'<td class="{cls}">{html.escape(txt)}{pairs}</td>')
        rows.append(f'<tr><th>{html.escape(zs)}</th>{"".join(cells)}</tr>')
    return (f'<div class="tablewrap"><table><thead><tr><th>src \\ dst</th>{head}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


def _source_table_html(src, row, inv) -> str:
    rows = []
    for d in ordered_ips(inv):
        if inv[d].machine == inv[src].machine:
            continue
        c = row.get(d, Cell())
        ports = ",".join(str(p) for p, _ in c.open_ports)
        rows.append(f'<tr><th>{html.escape(inv[d].short)}</th>'
                    f'<td>{html.escape(inv[d].zone)}</td><td>{html.escape(inv[d].htype)}</td>'
                    f'<td class="{VCLASS[c.verdict]}">{VERDICT_NAME[c.verdict]}</td>'
                    f'<td>{html.escape(ports)}</td></tr>')
    return ('<div class="tablewrap"><table><thead><tr><th>target</th><th>zone</th><th>type</th>'
            f'<th>verdict</th><th>open ports</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


def _exposure_html(exp, inv) -> str:
    blocks = []
    for d in inv:
        opens, reach = exp[d]
        if not opens and not reach:
            continue
        items = "".join(
            f'<li><span class="warn">OPEN</span> from <b>{html.escape(inv[s].short)}</b> '
            f'<span class="tag">{html.escape(inv[s].zone)}</span>: {",".join(map(str, ports))}</li>'
            for s, ports in opens
        ) + "".join(
            f'<li>reachable (closed) from {html.escape(inv[s].short)} '
            f'<span class="tag">{html.escape(inv[s].zone)}</span></li>' for s in reach
        )
        blocks.append(f'<div class="card"><b>{html.escape(inv[d].short)}</b> '
                      f'<span class="tag">{html.escape(inv[d].zone)} · {html.escape(inv[d].htype)}</span>'
                      f'<ul>{items}</ul></div>')
    return "".join(blocks) or "<p>No exposure.</p>"


def _zone_legend_html(inv) -> str:
    pal = zone_palette(inv)
    chips = "".join(
        f'<span style="background:{f};border:1px solid {s};color:{t};'
        f'padding:2px 9px;border-radius:12px;margin:0 6px 4px 0;display:inline-block;font-size:12px;">'
        f'{html.escape(z)}</span>'
        for z, (f, s, t) in sorted(pal.items())
    )
    return f'<div style="margin:4px 0 12px;">{chips}</div>'


def write_html(matrix, inv, agg, exp, missing, unknown, orphan, out_dir):
    srcs = [ip for ip in ordered_ips(inv) if ip in matrix]
    legend = ('<div class="legend">'
              '<span class="v-open">OPEN service</span>'
              '<span class="v-reach">reachable (closed)</span>'
              '<span class="v-alive">alive (ping/ARP)</span>'
              '<span class="v-block">blocked</span>'
              '<span class="v-none">unseen</span>'
              '<span style="color:#e11d48">— red = cross-zone OPEN</span></div>')

    # Global tab
    glob = ["<h2>Global diagram (zone &rarr; zone)</h2>", _zone_legend_html(inv), legend,
            f'<pre class="mermaid">{html.escape(mermaid_zone(agg, inv))}</pre>',
            "<h2>Consolidated zone &rarr; zone matrix</h2>", _zone_matrix_html(agg, inv),
            "<h2>Consolidated host &rarr; host matrix</h2>", legend, _host_matrix_html(matrix, inv),
            "<h2>Exposure per target</h2>", _exposure_html(exp, inv)]

    # Per-source tab
    by_m = defaultdict(list)
    for s in srcs:
        by_m[inv[s].machine].append(s)
    options = "".join(
        f'<optgroup label="{html.escape(m)}">'
        + "".join(f'<option value="src_{_hid(s)}">{html.escape(inv[s].short)} ({html.escape(inv[s].zone)})</option>'
                  for s in ips)
        + "</optgroup>"
        for m, ips in by_m.items())
    src_panes = []
    for i, s in enumerate(srcs):
        disp = "block" if i == 0 else "none"
        zs = sorted({inv[d].zone for d, c in matrix[s].items() if c.verdict >= REACH})
        boxes = "".join(f'<label><input type="checkbox" checked value="{_zid(z)}" onchange="refilter(this)"> '
                        f'{html.escape(z)}</label>' for z in zs)
        bar = (f'<div class="srcbar" data-name="{html.escape(inv[s].short)}"><b>Zones:</b>{boxes}'
               '<span><button onclick="exportImg(this,\'svg\')">Export SVG</button> '
               '<button onclick="exportImg(this,\'png\')">Export PNG</button></span></div>')
        src_panes.append(
            f'<div class="srcpane" id="src_{_hid(s)}" style="display:{disp}">'
            f'<h2>{html.escape(inv[s].short)} <span class="tag">{html.escape(inv[s].zone)} · {html.escape(inv[s].htype)} · {s}</span></h2>'
            f'{bar}<pre class="mermaid">{html.escape(mermaid_source(s, matrix[s], inv))}</pre>'
            f'<h3>Target details</h3>{_source_table_html(s, matrix[s], inv)}</div>')
    persource = [f'<select id="srcsel" onchange="showSource(this.value)">{options}</select>'] + src_panes

    # Anomalies tab
    anomalies = ["<h2>Sources without scan</h2>"]
    anomalies.append("<ul>" + ("".join(f"<li>{ip} — {html.escape(inv[ip].short)} "
                     f'<span class="tag">{html.escape(inv[ip].zone)}</span></li>' for ip in missing)
                     or "<li>None</li>") + "</ul>")
    anomalies.append("<h2>Reachable hosts outside the inventory</h2>")
    anomalies.append("<ul>" + ("".join(f'<li class="warn">{ip}</li>' for ip in unknown)
                     or "<li>None</li>") + "</ul>")
    anomalies.append("<h2>Ignored scans</h2><p>File name is not a source IP of the inventory "
                     "(expected: <code>&lt;source_ip&gt;.xml|.gnmap|.nmap</code>).</p>")
    anomalies.append("<ul>" + ("".join(f'<li class="warn">{html.escape(ip)}.*</li>' for ip in orphan)
                     or "<li>None</li>") + "</ul>")

    if MERMAID_JS.is_file():
        mjs = "<script>" + MERMAID_JS.read_text(encoding="utf-8").replace("</script", "<\\/script") + "</script>"
    else:
        print(f"[!] {MERMAID_JS.name} missing next to the script: report.html will load mermaid from the CDN "
              "(network required)", file=sys.stderr)
        mjs = f'<script src="{MERMAID_CDN}"></script>'

    doc = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Segmentation report</title>
{mjs}
<style>{HTML_CSS}</style></head><body>
<header><h1>Network segmentation report</h1>
<div class="meta">{len(inv)} targets · {len(srcs)} scanned source(s) · {len(missing)} without scan · {len(unknown)} host(s) outside inventory · {len(orphan)} ignored scan(s)</div></header>
<div class="tabs">
<button class="tab active" data-tab="global" onclick="showTab('global')">Global view</button>
<button class="tab" data-tab="persource" onclick="showTab('persource')">Per source</button>
<button class="tab" data-tab="anomalies" onclick="showTab('anomalies')">Anomalies</button>
</div>
<section id="tab-global" class="pane active">{''.join(glob)}</section>
<section id="tab-persource" class="pane">{''.join(persource)}</section>
<section id="tab-anomalies" class="pane">{''.join(anomalies)}</section>
<script>{HTML_JS}</script></body></html>"""
    return _write(out_dir, "report.html", doc)


# =============================================================================
# Main
# =============================================================================
def main():
    ap = argparse.ArgumentParser(description="Segmentation matrix + Mermaid + HTML report.",
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-i", "--inventory", required=True, help="Inventory CSV (ip;zone;type;name)")
    ap.add_argument("-s", "--scans", required=True, help="Directory of nmap outputs (<ip>.xml/.gnmap/.nmap)")
    ap.add_argument("-o", "--out", default="./seg_report", help="Output directory")
    ap.add_argument("--pn", action="store_true", help="Force -Pn mode (host-up ignored, verdict from ports only)")
    ap.add_argument("--host-graph", action="store_true", help="Also generate the global host-level Mermaid")
    args = ap.parse_args()

    os.makedirs(os.path.join(args.out, "mermaid"), exist_ok=True)
    inv = load_inventory(args.inventory)
    scans = discover_scans(args.scans)
    if not scans:
        sys.exit(f"[!] No scan found in {args.scans} ({', '.join(SCAN_EXT_PRIORITY)})")

    matrix, missing, unknown, pn_count = build_matrix(inv, scans, force_pn=args.pn)
    orphan = sorted(set(scans) - set(inv))   # files whose name is not a source IP of the inventory
    agg = aggregate_zones(matrix, inv)
    exp = target_exposure(matrix, inv)

    write_host_matrix_md(matrix, inv, args.out)
    write_zone_matrix_md(agg, inv, args.out)
    write_exposure_md(exp, inv, args.out)
    write_findings_md(matrix, inv, missing, unknown, orphan, args.out)
    _write(args.out, "segmentation.mmd", mermaid_zone(agg, inv))
    if args.host_graph:
        _write(args.out, "segmentation_hosts.mmd", mermaid_hosts(matrix, inv))
    for s in matrix:
        _write(os.path.join(args.out, "mermaid"), f"{s}.mmd", mermaid_source(s, matrix[s], inv))
    html_path = write_html(matrix, inv, agg, exp, missing, unknown, orphan, args.out)

    print(f"[+] Inventory: {len(inv)} targets | Scans: {len(scans)} file(s) -> {len(matrix)} source(s) "
          f"(-Pn detected/forced on {pn_count})")
    if orphan:
        print(f"[!] {len(orphan)} ignored scan(s), file name is not a source IP of the inventory: "
              f"{', '.join(orphan)}")
    if missing:
        print(f"[!] {len(missing)} source(s) without scan: {', '.join(missing)}")
    if unknown:
        print(f"[!] {len(unknown)} host(s) outside inventory: {', '.join(unknown)}")
    print(f"[+] HTML report: {html_path}")
    print(f"[+] md/csv/mmd outputs in: {args.out}")


if __name__ == "__main__":
    main()
