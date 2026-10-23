"""Mermaid diagrams: global zone graph, per-source graph, global host graph."""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Callable, Iterable

from seg_matrix.analysis import Matrix, Row, ZoneMatrix
from seg_matrix.inventory import Inventory, ordered_ips
from seg_matrix.ports import Port, port_label
from seg_matrix.render.common import machine_palette, zone_palette
from seg_matrix.verdict import OPEN, REACH

# Mermaid init directive (theme, font). 'linear' curve is mandatory: Mermaid puts the label in
# the middle of the dagre polyline, and 'basis' smooths the path beside it (label off by one link).
MERMAID_INIT = (
    "%%{init: {'theme':'base','themeVariables':{"
    "'fontFamily':'ui-sans-serif,-apple-system,Segoe UI,Roboto,sans-serif',"
    "'fontSize':'13px','lineColor':'#94a3b8'},"
    "'flowchart':{'curve':'linear','htmlLabels':true,"
    "'nodeSpacing':40,'rankSpacing':60,'padding':8}}}%%"
)


def _no_highlight(port: Port) -> bool:
    return False


def _label(ports: Iterable[Port], highlight: Callable[[Port], bool], cap: int = 6) -> str:
    """Edge label; highlighted (admin) ports in red."""
    labels = [
        f"<b style='color:#b91c1c'>{port_label(p)}</b>" if highlight(p) else port_label(p)
        for p in sorted(ports)
    ]
    return ",".join(labels[:cap]) + (",..." if len(labels) > cap else "")


def zid(z: str) -> str:
    return "Z_" + re.sub(r"[^A-Za-z0-9]", "_", z)


def hid(ip: str) -> str:
    return "H_" + ip.replace(".", "_").replace(":", "_")


def _safe(s: object) -> str:
    return str(s).replace('"', "'").replace("|", "/")


def _edge(
    a: str,
    b: str,
    verdict: int,
    cross: bool,
    label: str,
    idx: int,
    w_open: str = "2.5px",
    w_reach: str = "2px",
) -> tuple[str, str]:
    """Mermaid edge + its linkStyle: solid red/green if OPEN, dashed amber/grey otherwise."""
    if verdict == OPEN:
        col = "#e11d48" if cross else "#16a34a"
        return (
            f'  {a} ==>|"{_safe(label)}"| {b}',
            f"  linkStyle {idx} stroke:{col},stroke-width:{w_open},stroke-linecap:round;",
        )
    col = "#f59e0b" if cross else "#94a3b8"
    return (
        f'  {a} -.->|"{_safe(label)}"| {b}',
        f"  linkStyle {idx} stroke:{col},stroke-width:{w_reach},stroke-dasharray:5 4,stroke-linecap:round;",
    )


def _zone_subgraphs(
    zones: dict[str, list[str]], inv: Inventory, node_label: Callable[[str], str]
) -> list[str]:
    """classDef + subgraph per zone; zones = {zone: [ip]}, node_label(ip) -> node text.
    The zone colours the subgraph background; the node takes its machine colour if it is
    multi-interface, otherwise a white fill bordered with the zone colour."""
    pal, mpal = zone_palette(inv), machine_palette(inv)
    L = []
    for z in sorted(zones):
        f, s, t = pal[z]
        L.append(f"  classDef z_{zid(z)} fill:#ffffff,stroke:{s},stroke-width:1.5px,color:{t};")
    for m, (f, s, t) in sorted(mpal.items()):
        L.append(f"  classDef m_{zid(m)} fill:{f},stroke:{s},stroke-width:2px,color:{t};")
    for z, ips in sorted(zones.items()):
        f, s, t = pal[z]
        L.append(f'  subgraph {zid(z)}["{_safe(z)}"]')
        L += [
            f'    {hid(ip)}("{node_label(ip)}"):::'
            + (f"m_{zid(inv[ip].machine)}" if inv[ip].machine in mpal else f"z_{zid(z)}")
            for ip in ips
        ]
        L.append("  end")
        L.append(f"  style {zid(z)} fill:{f}aa,stroke:{s},stroke-width:1px,color:{t}")
    return L


def _machine_links(ips: list[str], inv: Inventory, idx: int) -> tuple[list[str], list[str]]:
    """Grey dotted line without arrow between interfaces of the same machine present in the graph."""
    by_m = defaultdict(list)
    for ip in ips:
        by_m[inv[ip].machine].append(ip)
    lines, styles = [], []
    for group in by_m.values():
        for a, b in zip(group, group[1:], strict=False):
            lines.append(f"  {hid(a)} -.- {hid(b)}")
            styles.append(
                f"  linkStyle {idx + len(styles)} stroke:#94a3b8,stroke-width:1px,stroke-dasharray:2 3;"
            )
    return lines, styles


def mermaid_zone(agg: ZoneMatrix, inv: Inventory, highlight: Callable[[Port], bool] = _no_highlight) -> str:
    pal = zone_palette(inv)
    L = [MERMAID_INIT, "flowchart LR"]
    for z, (f, s, t) in sorted(pal.items()):
        L.append(f'  {zid(z)}(["{_safe(z)}"])')
        L.append(f"  style {zid(z)} fill:{f},stroke:{s},stroke-width:2px,color:{t}")
    styles = []
    for (zs, zd), a in sorted(agg.items()):
        if a.reach_pairs == 0:
            continue
        label = _label(a.open_ports, highlight) if a.open_ports else f"{a.reach_pairs} host(s)"
        line, style = _edge(zid(zs), zid(zd), a.verdict, zs != zd, label, len(styles))
        L.append(line)
        styles.append(style)
    return "\n".join(L + styles)


def mermaid_source(
    src: str, row: Row, inv: Inventory, highlight: Callable[[Port], bool] = _no_highlight
) -> str:
    """Modern radial view: source (hexagon) + reachable targets, grouped/tinted by zone."""
    reach = {d: c for d, c in row.items() if c.verdict >= REACH}
    if not reach:
        return (
            MERMAID_INIT + "\nflowchart LR\n"
            f'  S{{{{"{_safe(inv[src].short)}<br/><small>no reachable target</small>"}}}}\n'
            "  style S fill:#1f2937,stroke:#0f172a,stroke-width:2px,color:#ffffff"
        )
    zones = defaultdict(list)
    for d in reach:
        zones[inv[d].zone].append(d)
    L = [
        MERMAID_INIT,
        "flowchart LR",
        f'  S{{{{"{_safe(inv[src].short)}<br/><small>{_safe(inv[src].zone)} · source</small>"}}}}',
        "  style S fill:#1f2937,stroke:#0f172a,stroke-width:2px,color:#ffffff",
    ]
    L += _zone_subgraphs(
        zones, inv, lambda ip: f"{_safe(inv[ip].short)}<br/><small>{_safe(inv[ip].htype)}</small>"
    )
    styles = []
    for d, c in reach.items():
        label = _label(c.open_ports, highlight) if c.verdict == OPEN else "reachable"
        line, style = _edge("S", hid(d), c.verdict, inv[src].zone != inv[d].zone, label, len(styles))
        L.append(line)
        styles.append(style)
    ml, ms = _machine_links(list(reach), inv, len(styles))
    return "\n".join(L + ml + styles + ms)


def mermaid_hosts(matrix: Matrix, inv: Inventory, highlight: Callable[[Port], bool] = _no_highlight) -> str:
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
            line, style = _edge(
                hid(s),
                hid(d),
                OPEN,
                inv[s].zone != inv[d].zone,
                _label(c.open_ports, highlight),
                len(styles),
                w_open="2px",
            )
            L.append(line)
            styles.append(style)
    ml, ms = _machine_links(ordered_ips(inv), inv, len(styles))
    return "\n".join(L + ml + styles + ms)
