"""Standalone tabbed HTML report, offline: its scripts (Cytoscape.js included) are inlined."""

from __future__ import annotations

import base64
import html
import json
import re
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable
from pathlib import Path

from segowl.analysis import (
    Analysis,
    Matrix,
    Rebound,
    Row,
    ZoneAgg,
    ZoneMatrix,
    rebounds,
)
from segowl.inventory import Host, Inventory, extra_columns, ordered_ips
from segowl.policy import ALLOW, DENY, UNDECLARED, worst
from segowl.ports import Port, count_ports, format_ranges, port_label, ports_text
from segowl.render.common import machine_palette, write_output, zone_palette
from segowl.render.mermaid import (
    GREY,
    POLICY_COLORS,
    SLATE,
    EdgeStatus,
    hid,
)
from segowl.verdict import ALIVE, BLOCK, NODATA, OPEN, REACH, STATE_RANK, VCLASS, VERDICT_NAME, Cell

ASSETS = Path(__file__).resolve().parent.parent / "assets"
# the report takes the app's palette (app.css :root) so both stay one look
APP_ROOT = re.search(r":root\{[^}]*\}", (ASSETS / "app.css").read_text(encoding="utf-8")).group()
HTML_CSS = APP_ROOT + (ASSETS / "report.css").read_text(encoding="utf-8")
HTML_JS = (ASSETS / "report.js").read_text(encoding="utf-8")
# Cytoscape (ADR-0005) and the diagram code, inlined: report.html stays offline
GRAPH_JS = "\n".join(
    (ASSETS / f).read_text(encoding="utf-8") for f in ("cytoscape.min.js", "report_graph.js")
)
GRAPH_JS = GRAPH_JS.replace("</script", "<\\/script")
LOGO_SVG = (ASSETS / "logo.svg").read_text(encoding="utf-8")
FAVICON = "data:image/svg+xml;base64," + base64.b64encode(LOGO_SVG.encode()).decode()


def _provenance(c: Cell) -> str:
    """Tooltip of a matrix cell: the Scans behind the verdict and their disagreements."""
    lines = ["Scans: " + (", ".join(c.scans) or "none")]
    for (port, proto), states in c.conflicts.items():
        lines.append(
            f"Conflict {port_label((port, proto))}: " + ", ".join(f"{st} ({sc})" for sc, st in states.items())
        )
    return html.escape("\n".join(lines), quote=True)


Highlight = Callable[[Port], bool]


def _no_highlight(port: Port) -> bool:
    return False


def _ports_attr(ports: Iterable[Port], highlight: Highlight) -> str:
    """Attributes read by the Port Group filter: data-p (every open port), data-b (the admin ones, bold)."""
    ports = list(ports)
    admin = ports_text([p for p in ports if highlight(p)])
    return f' data-p="{ports_text(ports)}"' + (f' data-b="{admin}"' if admin else "")


def _ports_html(ports: Iterable[Port], highlight: Highlight, cap: int = 0) -> str:
    """Open ports, admin ones bold; beyond cap, '+n'. Mirrored by portsHtml in report.js."""
    t = [f"<b>{port_label(p)}</b>" if highlight(p) else port_label(p) for p in sorted(ports)]
    return ",".join(t[:cap]) + f" <small>+{len(t) - cap}</small>" if cap and len(t) > cap else ",".join(t)


FLOW = {
    DENY: ("✕", "Finding: denied by the Flow Policy"),
    UNDECLARED: ("?", "undeclared"),
    ALLOW: ("✓", "allowed"),
}
MARK = {
    REACH: "closed",
    ALIVE: "ping",
    BLOCK: "×",
    NODATA: "–",
}  # BLOCKED tested and blocked, UNSEEN never seen


def _pg(st: str | None) -> str:
    """Flow Policy mark: its colour always comes with its icon."""
    return f'<i class="pg pg-{st}" title="{FLOW[st][1]}">{FLOW[st][0]}</i>' if st else ""


def _cell_html(c: Cell, highlight: Highlight = _no_highlight, st: str | None = None) -> str:
    """A matrix tile: tinted by the Flow Policy (with its icon), the verdict as a dot (CSS), the ports."""
    cls = VCLASS[c.verdict] + (" conflict" if c.conflicts else "") + (f" p-{st}" if st else "")
    txt = _ports_html(c.open_ports, highlight) if c.verdict == OPEN else MARK.get(c.verdict, "")
    return (
        f'<td class="{cls}"{_ports_attr(c.open_ports, highlight)} title="{_provenance(c)}">'
        f'{_pg(st)}<span class="pl">{txt}</span></td>'
    )


def _host_title(h: Host) -> str:
    """Tooltip of an Interface: zone, type and free inventory columns."""
    return html.escape(
        " · ".join([h.ip, h.zone, h.htype] + [f"{k}: {v}" for k, v in h.extra.items()]), quote=True
    )


CORNER = '<th class="corner">from ↓ · to →</th>'


def _host_matrix_html(
    matrix: Matrix, inv: Inventory, highlight: Highlight = _no_highlight, status: EdgeStatus | None = None
) -> str:
    dsts = ordered_ips(inv)
    srcs = [ip for ip in dsts if ip in matrix]
    mpal = machine_palette(inv)

    def th(ip: str) -> str:
        m = mpal.get(inv[ip].machine)
        style = f' style="background:{m[0]};color:{m[2]}"' if m else ""
        return f'<th{style} title="{_host_title(inv[ip])}">{html.escape(inv[ip].short)}</th>'

    head = "".join(th(d) for d in dsts)
    rows = []
    for s in srcs:
        cells = [
            '<td class="v-self"></td>'
            if inv[d].machine == inv[s].machine
            else _cell_html(matrix[s].get(d, Cell()), highlight, (status or {}).get((s, d)))
            for d in dsts
        ]
        rows.append(f"<tr>{th(s)}{''.join(cells)}</tr>")
    return (
        f'<div class="tablewrap"><table class="mx"><thead><tr>{CORNER}{head}</tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )


def _zone_chip(z: str, pal: dict[str, tuple[str, str, str]]) -> str:
    f, s, t = pal[z]
    return f'<span class="zchip" style="background:{f};border-color:{s};color:{t}">{html.escape(z)}</span>'


def _zone_matrix_html(
    agg: ZoneMatrix, inv: Inventory, highlight: Highlight = _no_highlight, status: EdgeStatus | None = None
) -> str:
    pal = zone_palette(inv)
    zones = sorted(pal)
    head = "".join(f"<th>{_zone_chip(z, pal)}</th>" for z in zones)
    rows = []
    for zs in zones:
        cells = []
        for zd in zones:
            a = agg.get((zs, zd)) or ZoneAgg()
            st = (status or {}).get((zs, zd))
            txt = _ports_html(a.open_ports, highlight, cap=6) if a.verdict == OPEN else MARK[a.verdict]
            pairs = (
                f'<small class="pairs">{a.pass_pairs}/{a.total_pairs} pairs</small>'
                if a.verdict >= ALIVE
                else ""
            )
            cells.append(
                f'<td class="{VCLASS[a.verdict]}{f" p-{st}" if st else ""}"'
                f'{_ports_attr(a.open_ports, highlight)} data-cap="6">'
                f'{_pg(st)}<span class="pl">{txt}</span>{pairs}</td>'
            )
        rows.append(f"<tr><th>{_zone_chip(zs, pal)}</th>{''.join(cells)}</tr>")
    return (
        f'<div class="tablewrap"><table class="mx zm"><thead><tr>{CORNER}{head}</tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )


def _ranges_html(proto: str, ranges: list[tuple[int, int]], label: str | None = None, cap: int = 40) -> str:
    """'tcp 22,80' inline; a long list (e.g. --top-ports 1000) folds into a click-to-open spoiler."""
    full = format_ranges(ranges)
    if label is None and len(full) <= cap:
        return f"{proto} {html.escape(full)}"
    summary = f"{proto} {label or f'{count_ports(ranges)} ports'}"
    return (
        f'<details class="ports"><summary>{html.escape(summary)}</summary>'
        f'<div class="plist">{html.escape(full)}</div></details>'
    )


def _tested_html(c: Cell) -> str:
    """Coverage of a cell: ports tested per protocol, '?' when a non-XML Scan cannot tell."""
    if not c.scans:
        return ""
    parts = [_ranges_html(proto, r) for proto, r in sorted(c.tested.items())]
    if not c.coverage_known:
        parts.append('<span class="warn" title="a Scan behind this cell is not XML">?</span>')
    return "<br>".join(parts)


Labels = dict[str, list[tuple[str, str]]]  # port label -> [(product, tags)]


def _labels(a: Analysis) -> Labels:
    """Port label ('22', 'udp:161') -> [(product, tags)] of its Port Labels."""
    out: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for r in a.labels:
        out[r[0].lower()].append((r[1], r[2]))
    return out


def _port_detail(src: str, d: str, a: Analysis, labels: Labels) -> str:
    """Per port open in a Scan of the Source (or disputed): the state each Scan saw, and its Port Labels."""
    scans = [(sc.name, a.scan_row(sc).get(d)) for sc in a.scans[src]]
    conf = a.matrix[src][d].conflicts
    ports = sorted({p for _, c in scans if c for p in c.open_ports} | set(conf))
    head = "".join(f"<th>{html.escape(n)}</th>" for n, _ in scans)
    rows = []
    for p in ports:
        cells = []
        for n, c in scans:
            if c and p in c.open_ports:
                cells.append('<td class="st-open">open</td>')
            elif n in conf.get(p, {}):
                cells.append(f'<td class="st-conf">{html.escape(conf[p][n])}</td>')
            elif c and c.is_tested(*p):
                cells.append('<td class="muted">not open</td>')
            else:
                cells.append('<td class="muted">not tested</td>')
        desc = "<br>".join(
            html.escape(prod)
            + "".join(f' <span class="tg">{html.escape(t)}</span>' for t in tags.split(",") if t)
            for prod, tags in labels.get(port_label(p).lower(), [])[:3]
        )
        desc = desc or '<span class="muted">no Port Label</span>'
        rows.append(
            f'<tr><th>{_ports_html([p], a.highlight)}</th>{"".join(cells)}<td class="lab">{desc}</td></tr>'
        )
    return (
        f'<table class="pd"><thead><tr><th>port</th>{head}<th>Port Label</th></tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def _source_table_html(src: str, a: Analysis) -> str:
    """Target details of a Source; a row with open ports unfolds what each Scan saw per port."""
    inv, row, labels = a.inv, a.matrix[src], _labels(a)
    extras = extra_columns(inv)
    rows = []
    for d in ordered_ips(inv):
        if inv[d].machine == inv[src].machine:
            continue
        c = row.get(d, Cell())
        more = bool(c.open_ports or c.conflicts)
        rows.append(
            ('<tr class="row-more" onclick="toggleMore(this)"><th>▸ ' if more else "<tr><th>")
            + f"{html.escape(inv[d].short)}</th>"
            f"<td>{html.escape(inv[d].zone)}</td><td>{html.escape(inv[d].htype)}</td>"
            f"<td>{_vb(c.verdict)}</td>"
            f"<td{_ports_attr(c.open_ports, a.highlight)}>{_ports_html(c.open_ports, a.highlight)}</td>"
            f"<td>{_tested_html(c)}</td>"
            f"<td>{html.escape(', '.join(c.scans))}</td>"
            + "".join(f"<td>{html.escape(inv[d].extra.get(k, ''))}</td>" for k in extras)
            + "</tr>"
        )
        if more:
            detail = _port_detail(src, d, a, labels)
            rows.append(f'<tr class="more" hidden><td colspan="{7 + len(extras)}">{detail}</td></tr>')
    return (
        '<div class="tablewrap"><table class="fit"><thead><tr><th>target</th><th>zone</th><th>type</th>'
        "<th>verdict</th><th>open ports</th><th>tested ports</th><th>scans</th>"
        + "".join(f"<th>{html.escape(k)}</th>" for k in extras)
        + f"</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
    )


def _vb(verdict: int) -> str:
    """Verdict badge in a table: one navy hue, darker = more open (red / amber / green: Flow Policy)."""
    return f'<span class="vb {VCLASS[verdict]}">{VERDICT_NAME[verdict]}</span>'


def _line(col: str, dash: bool = False) -> str:
    da = ' stroke-dasharray="5 4"' if dash else ""
    line = f'<line x1="1" y1="5" x2="27" y2="5" stroke="{col}" stroke-width="2.5"{da}/>'
    return f'<svg width="28" height="10">{line}</svg>'


def _diagram_legend(policy: bool, graph: bool = False) -> str:
    """What the diagrams use, and only that: edge colours, dashed edge, port marks (and, in a Cytoscape
    diagram, the Machine colour bar)."""
    if policy:
        edges = (
            f"<span>{_line(POLICY_COLORS[DENY])}{_pg(DENY)} open, denied: <b>Finding</b></span>"
            f"<span>{_line(POLICY_COLORS[UNDECLARED])}{_pg(UNDECLARED)} open, undeclared</span>"
            f"<span>{_line(POLICY_COLORS[ALLOW])}{_pg(ALLOW)} open, allowed</span>"
        )
        ports = (
            "port numbers: <b>bold</b> = admin port, "
            f'<span style="color:{POLICY_COLORS[DENY]}">red</span> = denied by the Flow Policy'
        )
    else:
        edges = (
            f"<span>{_line(POLICY_COLORS[UNDECLARED])}{_pg(UNDECLARED)} open across zones "
            "(no Flow Policy: undeclared)</span>"
            f"<span>{_line(GREY)} open inside a zone</span>"
        )
        ports = "port numbers: <b>bold</b> = admin port"
    machine = (
        '<span class="sep"></span><span><i class="mbar"></i> same colour bar: Interfaces of one Machine'
        "</span>"
        if graph
        else ""
    )
    return (
        f'<div class="lg">{edges}<span>{_line(SLATE, True)} reachable, no open port</span>'
        f'<span class="sep"></span><span>{ports}</span>{machine}</div>'
    )


def _matrix_legend(policy: bool) -> str:
    """What the matrix cells use, and only that: each item is a tile drawn like a cell."""

    def t(cls: str, inner: str, label: str) -> str:
        return f'<span><i class="lt {cls}">{inner}</i>{label}</span>'

    pol = (
        '<span class="sep"></span>'
        + t(f"v-open p-{DENY}", f"{_pg(DENY)}ports", "Finding (denied)")
        + t(f"v-open p-{UNDECLARED}", f"{_pg(UNDECLARED)}ports", "undeclared")
        + t(f"v-open p-{ALLOW}", f"{_pg(ALLOW)}ports", "allowed")
        if policy
        else ""
    )
    return (
        '<div class="lg">'
        + t("v-open", "ports", "OPEN: the open ports")
        + t("v-reach", "closed", "reachable (closed port)")
        + t("v-alive", "ping", "alive (ping/ARP)")
        + t("v-block", "×", "blocked")
        + t("v-none", "–", "unseen")
        + t("v-self", "", "same Machine")
        + t("v-open conflict", "ports", "Scans disagree")
        + '<span class="sep"></span>'
        + t("v-open", "<b>22</b>,80", "bold: admin port")
        + '<span class="muted">dot: verdict, darker = more open</span>'
        + pol
        + "</div>"
    )


def _sec(title: str, body: str) -> str:
    """A top-level section of a tab: a white card with its title."""
    return f'<div class="sec"><h2>{title}</h2>{body}</div>'


def _zone_tag(z: str) -> str:
    return f'<span class="tag">{html.escape(z)}</span>'


FROM, INTO = "Source Zones", "its other Zones"  # the two frames of a Pivot Machine diagram
REBOUND, BYPASS = "#FFB020", POLICY_COLORS[DENY]  # rebound: brand amber (user's choice); bypass: red


def _names(a: Analysis, ips: list[str], cap: int = 5) -> str:
    txt = ", ".join(html.escape(a.inv[i].short) for i in ips[:cap])
    return txt + (f" +{len(ips) - cap}" if len(ips) > cap else "")


def _pivot_graph(a: Analysis, machine: str, hits: list, rbs: list[Rebound]) -> dict:
    """In: each Source Zone -> the Interfaces its Sources reach (ports). Out: each rebound Interface -> its
    Zone."""
    inv, multi = a.inv, set(machine_palette(a.inv))
    ifaces = [ip for ip in ordered_ips(inv) if inv[ip].machine == machine]
    nodes = []
    for z in sorted({inv[s].zone for s, _, _ in hits}):
        srcs = sorted({s for s, _, _ in hits if inv[s].zone == z})
        links = []
        for d in sorted({d for s, d, _ in hits if inv[s].zone == z}):
            ports: dict[str, dict] = {}
            for s in srcs:
                if d in a.matrix[s] and a.matrix[s][d].verdict == OPEN:
                    for p in _link(a, s, d)["ports"]:
                        if p["l"] not in ports or p["st"] == DENY:
                            ports[p["l"]] = p
            links.append(
                {"to": d, "verdict": "OPEN", "ports": list(ports.values()), "cross": z != inv[d].zone}
            )
        names = ", ".join(html.escape(inv[x].short) for x in srcs)
        tip = f"<h4>{html.escape(z)}</h4>Sources: {names}<br>reach {', '.join(lk['to'] for lk in links)}"
        nodes.append({"ip": f"from:{z}", "name": z, "sub": "", "zone": FROM, "links": links, "tip": tip})
    for r in rbs:
        best = max(r.gain.values(), key=len)
        bypass = any(r.bypass(z) for z in r.gain)
        note = (
            "bypass, all of it" if bypass else f"+{len(best)} not reached directly" if best else "nothing new"
        )
        nodes.append(
            {
                "ip": f"into:{r.into}",
                "name": r.into,
                "zone": INTO,
                "sub": f"through {r.through}",
                "note": note,
                "noteCol": BYPASS if bypass else "#6B7C93",
                "links": [
                    {
                        "to": r.through,
                        "verdict": "OPEN",
                        "ports": [],
                        "cross": False,
                        "keep": True,
                        "inward": False,
                    }
                    | {"col": BYPASS if bypass else REBOUND, "dash": True}
                ],
                "tip": f"<h4>into {html.escape(r.into)}</h4>"
                + "<br>".join(
                    f"from {html.escape(z)}: {'bypass, ' if r.bypass(z) else ''}"
                    f"+{len(add)} of the {len(r.others)} other Interface(s)"
                    for z, add in r.gain.items()
                ),
            }
        )
    return {
        "file": f"pivot-{machine}",
        "center": {"machine": machine, "ifaces": [_node(a, d, multi) for d in ifaces]},
        "zones": {
            **zone_palette(inv),
            FROM: ("#f4f7fa", "#6B7C93", "#2b3743"),
            INTO: ("#fffaf0", REBOUND, "#7a4a00"),
        },
        "machines": {},
        "nodes": nodes,
        "inward": True,
        "sides": {FROM: "L", INTO: "R"},
    }


def _pivots_html(a: Analysis) -> str:
    """One card per Pivot Machine: who reaches it (In) and, for each of its other Zones, what the rebound
    adds to what each Source Zone already reaches directly (Out). Bypasses first; nothing new: folded."""
    inv, st, e = a.inv, a.pair_status(a.matrix), html.escape
    cards = []
    for machine, hits in a.pivots.items():
        rbs = rebounds(a.matrix, inv, machine, hits)
        n_bypass = sum(any(r.bypass(z) for z in r.gain) for r in rbs)
        gains = sum(max(len(g) for g in r.gain.values()) for r in rbs)
        out_rows = []
        for r in rbs:
            parts = []
            for z, add in r.gain.items():
                if not r.others:
                    parts.append(f"{_zone_tag(z)} nothing else in this Zone")
                elif r.bypass(z):
                    parts.append(
                        f'{_zone_tag(z)} <span class="byp">bypass</span> +{len(add)}, all of it: '
                        + _names(a, add)
                    )
                elif add:
                    parts.append(f"{_zone_tag(z)} <b>+{len(add)}</b>: {_names(a, add)}")
                else:
                    parts.append(
                        f'{_zone_tag(z)} <span class="muted">nothing new, already reaches all '
                        f"{len(r.others)}</span>"
                    )
            out_rows.append(
                f"<tr><th>{_zone_tag(r.into)}</th><td>{e(r.through)}<br>"
                f'<small class="muted">{len(r.others)} other '
                f"Interface(s) in {e(r.into)}</small></td><td>{'<br>'.join(parts)}</td></tr>"
            )
        in_rows = "".join(
            f"<tr><th>{e(inv[s].short)} {_zone_tag(inv[s].zone)}</th><td>{e(d)} {_zone_tag(inv[d].zone)}</td>"
            f"<td{_ports_attr(ports, a.highlight)}>{_pg(st.get((s, d)))}"
            f'<span class="pl">{_ports_html(ports, a.highlight)}</span></td></tr>'
            for s, d, ports in sorted(hits, key=lambda h: (inv[h[0]].zone, h[0], h[1]))
        )
        zones = " ".join(_zone_tag(inv[i].zone) for i in ordered_ips(inv) if inv[i].machine == machine)
        badge = (
            f'<span class="byp">{n_bypass} bypass</span>'
            if n_bypass
            else ""
            if gains
            else '<span class="tag">nothing new</span>'
        )
        tables = (
            '<div class="pv"><div><h4>In: who reaches it</h4><table class="pd"><thead><tr><th>Source</th>'
            "<th>Interface reached</th><th>open ports</th></tr></thead>"
            f"<tbody>{in_rows}</tbody></table></div>"
            '<div><h4>Out: what the rebound adds</h4><table class="pd"><thead><tr><th>into</th>'
            "<th>through</th>"
            "<th>per Source Zone, the Interfaces it does not reach directly</th></tr></thead><tbody>"
            + (
                "".join(out_rows)
                or "<tr><td colspan=3>Nowhere: no Source lands in another Zone through it.</td></tr>"
            )
            + "</tbody></table></div></div>"
        )
        body = _graph(_pivot_graph(a, machine, hits, rbs)) + tables
        if not gains:
            body = (
                f'<details ontoggle="renderVisible(this)"><summary>{len(hits)} flow(s), the rebound adds '
                "nothing to "
                f"what the Source Zones already reach</summary>{body}</details>"
            )
        head = f'<div class="ph"><b class="pm">{e(machine)}</b> {zones} {badge}</div>'
        cards.append(
            (
                -n_bypass,
                -gains,
                machine,
                f'<div class="sec pivot{"" if gains else " calm"}">{head}{body}</div>',
            )
        )
    return (
        "".join(c[-1] for c in sorted(cards))
        or "<p>None: no Machine spanning several Zones is reached OPEN.</p>"
    )


def _zone_graph(a: Analysis) -> dict:
    """Global view diagram: one node per Zone, one link per Zone pair passing (OPEN, reachable or alive), each
    open port with the worst Flow Policy status it has between those two Zones."""
    inv, pal = a.inv, zone_palette(a.inv)
    port_st: dict[tuple[str, str, Port], str] = {}
    for (s, d, p), rule in a.decisions.items():
        k, st = (inv[s].zone, inv[d].zone, p), UNDECLARED if rule is None else rule.action
        port_st[k] = worst([port_st[k], st]) if k in port_st else st
    links = []
    for (zs, zd), z in sorted(a.agg.items()):
        if z.verdict < ALIVE:
            continue
        ports = [
            {"l": port_label(p), "admin": a.highlight(p), "st": port_st.get((zs, zd, p))}
            for p in sorted(z.open_ports)
        ]
        ports.sort(key=lambda p: (p["st"] != DENY, not p["admin"]))
        word = f"{z.pass_pairs} {'alive' if z.verdict == ALIVE else 'reachable'}"
        links.append(
            {"from": zs, "to": zd, "verdict": VERDICT_NAME[z.verdict], "ports": ports, "cross": zs != zd}
            | {"pairs": f"{z.pass_pairs}/{z.total_pairs}", "word": word}
        )
    count = Counter(h.zone for h in inv.values())
    return {
        "zonegraph": True,
        "file": "zones",
        "zones": pal,
        "nodes": [{"zone": z, "n": count[z]} for z in sorted(pal)],
        "links": links,
    }


def _global_tab(a: Analysis) -> str:
    return (
        _sec(
            "Global diagram (zone &rarr; zone)",
            _graph(_zone_graph(a))
            + _diagram_legend(a.policy is not None).replace(
                "</div>", '<span class="sep"></span><span>hover an edge: its Interface pairs</span></div>'
            ),
        )
        + _sec(
            "Zone &rarr; zone matrix",
            _zone_matrix_html(a.agg, a.inv, a.highlight, a.zone_status(a.matrix))
            + _matrix_legend(a.policy is not None),
        )
        + _sec(
            "Host &rarr; host matrix",
            '<p class="hint">Hover a cell for the Scans behind its verdict.</p>'
            + _host_matrix_html(a.matrix, a.inv, a.highlight, a.pair_status(a.matrix))
            + _matrix_legend(a.policy is not None),
        )
    )


def _pivots_tab(a: Analysis) -> str:
    rebound = (
        f"<span>{_line(REBOUND, True)} rebound: from this Machine, its other Zones</span>"
        f"<span>{_line(BYPASS, True)} bypass: the Source Zone reaches nothing else there directly</span>"
        "</div>"
    )
    return (
        '<div class="explain">A <b>Pivot Machine</b> has Interfaces in several Zones and a Source reaches it '
        "OPEN: whoever holds it lands in all its Zones at once (a rebound). Each card shows who reaches it "
        "(In) and, for each of its other Zones, which Interfaces the rebound adds to what the Source Zone "
        "reaches directly (Out). Adds everything: a <b>bypass</b> of the segmentation. Bypasses first."
        "<br><small>Machines are grouped by inventory name: a device known under two names is not detected, "
        "so this list is not exhaustive.</small></div>"
        + _diagram_legend(a.policy is not None, graph=True).removesuffix("</div>")
        + rebound
        + _pivots_html(a)
    )


def _nmap_ports(ports: Iterable[Port]) -> str:
    """Ports ready for nmap -p: '22,443', or 'T:22,443,U:53' as soon as another protocol is in."""
    by = {pr: ",".join(str(n) for n, q in sorted(set(ports)) if q == pr) for pr in ("tcp", "udp", "sctp")}
    if not by["udp"] and not by["sctp"]:
        return by["tcp"]
    return ",".join(f"{pr[0].upper()}:{v}" for pr, v in by.items() if v)


def _copy_btn(ports: set[Port], what: str) -> str:
    v = _nmap_ports(ports)
    btn = f'<button class="btn copy" data-ports="{v}" title="nmap -p {v}" onclick="copyPorts(this)">'
    return f"{btn}Copy {what}</button>" if ports else ""


def _iface_ports(a: Analysis, d: str, labels: Labels) -> tuple[str, set[Port]]:
    """One Interface: every port open from some Source × each Source (open with its Flow Policy mark / not
    open / not tested, from Coverage), with the Port Label. Returns the HTML and the open ports."""
    inv = a.inv
    srcs = [s for s in a.sources if inv[s].machine != inv[d].machine]
    cells = {s: a.matrix[s].get(d) for s in srcs}
    ports = sorted({p for c in cells.values() if c for p in c.open_ports})
    title = f"<h4>{html.escape(d)} {_zone_tag(inv[d].zone)}"
    if not ports:
        return f'<div>{title} <span class="muted small">no port open from any Source</span></h4></div>', set()
    head = "".join(f"<th>{html.escape(inv[s].short)} {_zone_tag(inv[s].zone)}</th>" for s in srcs)
    rows = []
    for p in ports:
        tds = []
        for s in srcs:
            c = cells[s]
            if c and p in c.open_ports:
                mark = _pg(a.flow_status(s, d, p) if a.policy is not None else None)
                tds.append(f'<td class="st-open">{mark}open</td>')
            elif c and c.is_tested(*p):
                tds.append('<td class="st-closed">not open</td>')
            else:
                tds.append('<td class="muted">not tested</td>')
        desc = ", ".join(html.escape(prod) for prod, _ in labels.get(port_label(p).lower(), [])[:2])
        desc = desc or '<span class="muted">–</span>'
        rows.append(
            f'<tr data-pr="{port_label(p)}"><th>{_ports_html([p], a.highlight)}</th>{"".join(tds)}'
            f'<td class="lab">{desc}</td></tr>'
        )
    return (
        f'<div>{title} <span class="muted small">{len(ports)} open port(s)</span> '
        f"{_copy_btn(set(ports), 'its open ports')}</h4>"
        f'<table class="pd pm-ports"><thead><tr><th>port</th>{head}<th>Port Label</th></tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table></div>",
        set(ports),
    )


def _flow_row(a: Analysis, s: str, d: str, c: Cell, st: dict) -> str:
    """Cells shared by the Per target tables: verdict, open ports with the Flow Policy mark."""
    return (
        f"<td>{_vb(c.verdict)}</td>"
        f"<td{_ports_attr(c.open_ports, a.highlight)}>{_pg(st.get((s, d)))}"
        f'<span class="pl">{_ports_html(c.open_ports, a.highlight)}</span></td>'
    )


def _pertarget_tab(a: Analysis) -> str:
    """Mirror of Per source, per Machine: pick it (name, IP or Zone), see who reaches each Interface."""
    inv, st, labels = a.inv, a.pair_status(a.matrix), _labels(a)
    machines = defaultdict(list)
    for d in ordered_ips(inv):
        machines[inv[d].machine].append(d)
    reached = {
        m: ips
        for m, ips in machines.items()
        if any(d in r and r[d].verdict >= ALIVE for r in a.matrix.values() for d in ips)
    }
    e = html.escape
    opts = "".join(
        f'<option value="{e(m)} · {e(", ".join(ips))} · {e(", ".join(sorted({inv[i].zone for i in ips})))}" '
        f'data-k="tgt_{hid(ips[0])}">'
        for m, ips in reached.items()
    )
    panes = []
    for i, (m, ips) in enumerate(reached.items()):
        seen = "".join(
            f"<tr><th>{e(inv[s].short)}</th><td>{e(inv[s].zone)}</td><td>{e(d)}</td><td>{e(inv[d].zone)}</td>"
            f"{_flow_row(a, s, d, c, st)}<td>{_tested_html(c)}</td></tr>"
            for d in ips
            for s in a.sources
            if (c := a.matrix[s].get(d)) is not None
        )
        parts = [_iface_ports(a, d, labels) for d in ips]
        total = set().union(*(p for _, p in parts))
        zones = ", ".join(sorted({inv[x].zone for x in ips}))
        copy_all = _copy_btn(total, "all the Machine’s open ports") if len(ips) > 1 else ""
        panes.append(
            f'<div class="tgtpane sec" id="tgt_{hid(ips[0])}" style="display:{"none" if i else "block"}">'
            f'<h2>{e(m)} <span class="tag">{len(ips)} Interface(s) · {e(zones)}</span>'
            f'<span class="tag">{len(total)} port(s) open on the Machine</span></h2>'
            + _graph(_target_graph(a, m, ips))
            + _diagram_legend(a.policy is not None, graph=True)
            + f"<h3>Open ports per Interface, and from which Source {copy_all}</h3>"
            '<div class="pmgrid">' + "".join(h for h, _ in parts) + "</div>"
            "<h3>Seen from each Source</h3>"
            '<div class="tablewrap"><table class="fit"><thead><tr><th>source</th><th>zone</th>'
            "<th>Interface</th><th>its zone</th><th>verdict</th><th>open ports</th><th>tested ports</th></tr>"
            f"</thead><tbody>{seen}</tbody></table></div></div>"
        )
    allrows = "".join(
        f"<tr><th>{e(inv[d].short)}</th><td>{e(inv[d].zone)}</td>"
        f"<td>{e(inv[s].short)}</td><td>{e(inv[s].zone)}</td>"
        f"{_flow_row(a, s, d, c, st)}<td>{FLOW[st[(s, d)]][1] if (s, d) in st else ''}</td></tr>"
        for d in ordered_ips(inv)
        for s in a.sources
        if (c := a.matrix[s].get(d)) is not None and c.verdict >= ALIVE
    )
    overview = (
        '<details class="sec"><summary><b>All targets</b> · every target a Source reaches, one row per '
        "target × Source</summary>"
        '<div class="tablewrap"><table class="fit"><thead><tr><th>target</th><th>zone</th>'
        "<th>source</th><th>src zone</th><th>verdict</th><th>open ports</th><th>Flow Policy</th></tr></thead>"
        f"<tbody>{allrows}</tbody></table></div></details>"
    )
    return (
        overview + '<label class="pick">Machine <input id="tgtq" type="search" list="tgtlist" '
        'placeholder="name, IP or zone…" '
        'oninput="pickTarget(this.value)" autocomplete="off"></label>'
        f'<datalist id="tgtlist">{opts}</datalist>'
        f'<span class="hint"> {len(reached)} Machines reached by at least one Source</span>' + "".join(panes)
    )


def _json(data: object) -> str:
    """JSON safe inside a <script> element."""
    return json.dumps(data).replace("<", "\\u003c")


def _graph(data: dict) -> str:
    """A Cytoscape diagram, drawn by report_graph.js the first time it is shown."""
    return f'<div class="graph"><script type="application/json">{_json(data)}</script></div>'


def _link(a: Analysis, s: str, d: str) -> dict:
    """The flow Source s -> Interface d in a diagram: verdict, open ports with admin and Flow Policy marks."""
    c = a.matrix[s][d]
    ports = [
        {
            "l": port_label(p),
            "admin": a.highlight(p),
            "st": a.flow_status(s, d, p) if a.policy is not None else None,
        }
        for p in (c.open_ports if c.verdict == OPEN else [])
    ]
    ports.sort(key=lambda p: (p["st"] != DENY, not p["admin"]))  # what matters first
    return {"verdict": VERDICT_NAME[c.verdict], "ports": ports, "cross": a.inv[s].zone != a.inv[d].zone}


def _node(a: Analysis, ip: str, multi: set[str]) -> dict:
    """An Interface as a diagram node: what its card and tooltip name."""
    h = a.inv[ip]
    return {
        "ip": ip,
        "name": h.name,
        "zone": h.zone,
        "type": h.htype,
        "machine": h.machine,
        "multi": h.machine in multi,
    }


def _palettes(a: Analysis) -> dict:
    return {"zones": zone_palette(a.inv), "machines": {m: c[1] for m, c in machine_palette(a.inv).items()}}


def _source_graph(a: Analysis, s: str) -> dict:
    """Per source diagram: the Source in the centre, the Interfaces it reaches in their Zone frames."""
    inv, multi = a.inv, set(machine_palette(a.inv))
    return {
        "file": f"per-source-{inv[s].short}".replace(" · ", "-"),
        "center": _node(a, s, multi),
        **_palettes(a),
        "nodes": [
            {**_node(a, d, multi), **_link(a, s, d)} for d, c in a.matrix[s].items() if c.verdict >= ALIVE
        ],
    }


def _target_graph(a: Analysis, machine: str, ips: list[str]) -> dict:
    """Per target diagram: the Machine as a frame holding its Interfaces, the Sources reaching them around it
    in their Zone frames (arrows towards the Machine)."""
    multi = set(machine_palette(a.inv))
    nodes = []
    for s in a.sources:
        links = [
            {"to": d, **_link(a, s, d)} for d in ips if d in a.matrix[s] and a.matrix[s][d].verdict >= ALIVE
        ]
        if links:
            nodes.append({**_node(a, s, multi), "links": links})
    return {
        "file": f"per-target-{machine}",
        "center": {"machine": machine, "ifaces": [_node(a, d, multi) for d in ips]},
        **_palettes(a),
        "nodes": nodes,
        "inward": True,
    }


def _persource_tab(a: Analysis) -> str:
    inv = a.inv
    by_m = defaultdict(list)
    for s in a.sources:
        by_m[inv[s].machine].append(s)
    options = "".join(
        f'<optgroup label="{html.escape(m)}">'
        + "".join(
            f'<option value="src_{hid(s)}">{html.escape(inv[s].short)} ({html.escape(inv[s].zone)})</option>'
            for s in ips
        )
        + "</optgroup>"
        for m, ips in by_m.items()
    )
    panes = []
    for i, s in enumerate(a.sources):
        panes.append(
            f'<div class="srcpane sec" id="src_{hid(s)}" style="display:{"block" if i == 0 else "none"}">'
            f"<h2>{html.escape(inv[s].short)} "
            f'<span class="tag">{html.escape(inv[s].zone)} · {html.escape(inv[s].htype)} · '
            f"{html.escape(s)}</span>"
            f'<span class="tag">{len(a.scans[s])} scan(s)</span></h2>'
            + _graph(_source_graph(a, s))
            + _diagram_legend(a.policy is not None, graph=True)
            + '<h3>Target details</h3><p class="hint">Click a row with open ports: what each Scan saw on '
            f"each port, and its Port Label.</p>{_source_table_html(s, a)}</div>"
        )
    return (
        f'<label class="pick">Source <select id="srcsel" onchange="showSource(this.value)">{options}</select>'
        "</label>" + "".join(panes)
    )


def _scans_tab(a: Analysis) -> str:
    rows = []
    for src in a.sources:
        h = a.inv[src]
        # number of (target, port) disagreements each Scan takes part in
        conflicts = Counter(
            sc for c in a.matrix[src].values() for states in c.conflicts.values() for sc in states
        )
        for sc in a.scans[src]:
            if sc.coverage is None:
                cov = '<span class="warn">unknown (not XML)</span>'
            else:
                top = re.search(r"--top-ports[ =](\d+)", sc.command)
                cov = "".join(
                    _ranges_html(proto, r, f"top-ports {top.group(1)}" if top else None)
                    for proto, r in sorted(sc.coverage.items())
                )
            rows.append(
                f"<tr><th>{html.escape(h.short)}</th><td>{html.escape(h.zone)}</td>"
                f"<td>{html.escape(sc.name)}</td><td>{html.escape(sc.started)}</td>"
                f"<td>{cov}</td><td>{len(sc.hosts)}</td>"
                f'<td class="{"warn" if conflicts[sc.name] else ""}">{conflicts[sc.name] or ""}</td>'
                f'<td class="cmd"><code>{html.escape(sc.command)}</code></td></tr>'
            )
    scans_table = (
        f'<div class="tablewrap"><table class="fit"><thead><tr>'
        "<th>source</th><th>zone</th><th>file</th><th>started</th><th>tested ports</th>"
        "<th>hosts in output</th><th>conflicts</th><th>command</th></tr>"
        f"</thead><tbody>{''.join(rows)}</tbody></table></div>"
    )

    # Conflicts: ports on which the Scans of a Source disagree, and the state the Source View keeps
    conf_rows = []
    for src in a.sources:
        for d, c in a.matrix[src].items():
            for port, states in c.conflicts.items():
                kept = max(states.values(), key=lambda st: STATE_RANK.get(st, 0))
                seen = "<br>".join(
                    f"{html.escape(st)} <small>{html.escape(sc)}</small>" for sc, st in states.items()
                )
                from_ = ", ".join(sc for sc, st in states.items() if st == kept)
                conf_rows.append(
                    f"<tr><th>{html.escape(a.inv[src].short)}</th><th>{html.escape(a.inv[d].short)}</th>"
                    f"<td>{html.escape(a.inv[d].zone)}</td><td>{port_label(port)}</td><td>{seen}</td>"
                    f"<td><b>{html.escape(kept)}</b> <small>from {html.escape(from_)}</small></td></tr>"
                )
    conflicts_table = (
        f'<div class="tablewrap"><table class="fit"><thead><tr><th>source</th><th>target</th>'
        "<th>zone</th><th>port</th><th>state per Scan</th><th>kept (most permissive)</th></tr></thead>"
        f"<tbody>{''.join(conf_rows)}</tbody></table></div>"
        if conf_rows
        else "<p>None: the Scans of each Source agree on every port listed.</p>"
    )
    excluded = "".join(
        f"<li>{html.escape(a.inv[src].short if src in a.inv else src)}: <code>{html.escape(p)}</code></li>"
        for src, paths in a.excluded.items()
        for p in paths
    )

    # Coverage per target Interface: which Source tested it, how many ports, through which Scans
    inv, srcs = a.inv, a.sources
    head = "".join(f'<th title="{html.escape(inv[s].zone)}">{html.escape(inv[s].short)}</th>' for s in srcs)
    cov_rows = []
    for d in ordered_ips(inv):
        cells = []
        for s in srcs:
            c = a.matrix[s].get(d)
            if c is None:
                cells.append('<td class="muted">-</td>')
            elif not c.scans:
                cells.append('<td class="muted" title="in no Scan output">.</td>')
            else:
                txt = " · ".join(f"{proto} {count_ports(r)}" for proto, r in sorted(c.tested.items()))
                txt += "" if c.coverage_known else " ?"
                tip = html.escape("\n".join(c.scans), quote=True)
                cells.append(
                    f'<td title="{tip}">{html.escape(txt.strip())} <small>({len(c.scans)})</small></td>'
                )
        cov_rows.append(
            f'<tr><th title="{_host_title(inv[d])}">{html.escape(inv[d].short)}</th>{"".join(cells)}</tr>'
        )
    coverage_table = (
        f'<div class="tablewrap"><table><thead>'
        f"<tr><th>target \\ source</th>{head}</tr></thead>"
        f"<tbody>{''.join(cov_rows)}</tbody></table></div>"
    )
    return (
        _sec(
            "Scans",
            '<p class="hint">One row per Scan. When Scans of a Source disagree on a port, the most '
            "permissive state wins (an open port seen once proves the flow passed); the conflicts column "
            "counts the disagreements a Scan takes part in, detailed in the matrix cell tooltips.</p>"
            + scans_table,
        )
        + _sec(
            "Conflicts",
            '<p class="hint">Ports on which the Scans of a Source disagree. To take a Scan out of the '
            "analysis, move its file into a sub-folder of its source folder (e.g. "
            "<code>scans/&lt;source_ip&gt;/excluded/</code>) and regenerate the report: it is then listed "
            "below as excluded, not read.</p>"
            + conflicts_table
            + f"<h3>Excluded scans</h3><ul>{excluded or '<li>None</li>'}</ul>",
        )
        + _sec(
            "Coverage per target",
            '<p class="hint">Number of ports tested per protocol from each Source (number of Scans); '
            "<code>.</code> = in no Scan output, <code>?</code> = a non-XML Scan does not tell which "
            "ports it tested. Hover a cell for the Scans.</p>" + coverage_table,
        )
    )


def _anomalies_tab(a: Analysis) -> str:
    inv = a.inv
    missing = "".join(
        f"<li>{html.escape(ip)} — {html.escape(inv[ip].short)} {_zone_tag(inv[ip].zone)}</li>"
        if ip in inv
        else f'<li>{html.escape(ip)} <span class="warn">not in the inventory</span></li>'
        for ip in a.missing
    )
    unknown = "".join(f'<li class="warn">{html.escape(ip)}</li>' for ip in a.unknown)
    orphan = "".join(f'<li class="warn">{html.escape(ip)}</li>' for ip in a.orphan)
    return (
        _sec(
            "Sources without scan",
            '<p class="hint">Declared Sources (a <code>scans/&lt;ip&gt;/</code> folder) that hold no Scan '
            "yet.</p>"
            f"<ul>{missing or '<li>None: every declared Source has a Scan.</li>'}</ul>",
        )
        + _sec("Reachable hosts outside the inventory", f"<ul>{unknown or '<li>None</li>'}</ul>")
        + _sec(
            "Ignored scans",
            "<p>Source folder or file name is not an inventory IP "
            "(expected: <code>scans/&lt;source_ip&gt;/*.xml</code> "
            f"or <code>scans/&lt;source_ip&gt;.xml</code>).</p><ul>{orphan or '<li>None</li>'}</ul>",
        )
        + _sec(
            "Asymmetric flows",
            '<p class="hint">A reaches B (OPEN or closed ports) while B &rarr; A is blocked: typically a '
            "one-way firewall rule. Only pairs where both are Sources and both directions tested common "
            "ports.</p>" + _asymmetry_html(a),
        )
    )


def _asymmetry_html(a: Analysis) -> str:
    inv = a.inv
    if not a.asymmetries:
        return "<p>None among the pairs scanned in both directions.</p>"
    by_zone: Counter[tuple[str, str]] = Counter((inv[x].zone, inv[y].zone) for x, y in a.asymmetries)
    summary = "".join(
        f"<tr><th>{html.escape(zx)}</th><th>{html.escape(zy)}</th><td>{n}</td></tr>"
        for (zx, zy), n in sorted(by_zone.items())
    )
    detail = "".join(
        f"<tr><th>{html.escape(inv[x].short)}</th><td>{html.escape(inv[x].zone)}</td>"
        f"<th>{html.escape(inv[y].short)}</th><td>{html.escape(inv[y].zone)}</td>"
        f"{_cell_html(a.matrix[x][y], a.highlight)}{_cell_html(a.matrix[y][x])}</tr>"
        for x, y in sorted(a.asymmetries, key=lambda p: (inv[p[0]].zone, inv[p[1]].zone, p))
    )
    return (
        '<div class="tablewrap"><table><thead><tr><th>passes from zone</th><th>to zone</th>'
        f"<th>interface pairs</th></tr></thead><tbody>{summary}</tbody></table></div>"
        f"<h3>Detail</h3>"
        '<div class="tablewrap"><table class="mx"><thead><tr><th>A</th><th>zone</th><th>B</th><th>zone</th>'
        f"<th>A &rarr; B</th><th>B &rarr; A</th></tr></thead><tbody>{detail}</tbody></table></div>"
    )


def _diff_cells(row: Row) -> dict:
    return {
        d: {
            "v": VERDICT_NAME[c.verdict],
            "open": [port_label(p) for p in c.open_ports],
            "tested": c.tested if c.coverage_known else None,
        }
        for d, c in row.items()
        if c.scans
    }


def _diff_tab(a: Analysis) -> str:
    """Scan Diff, computed in the browser from the embedded observations of every Scan and Source View."""
    sets, options = [], []
    for src in a.sources:
        h, group = a.inv[src], []
        for label, row in [(f"Source View ({len(a.scans[src])} scans)", a.matrix[src])] + [
            (f"{sc.name} · {sc.started}", a.scan_row(sc)) for sc in a.scans[src]
        ]:
            group.append(f'<option value="{len(sets)}">{html.escape(label)}</option>')
            sets.append({"label": f"{h.short} — {label}", "cells": _diff_cells(row)})
        options.append(
            f'<optgroup label="{html.escape(h.short)} ({html.escape(h.zone)})">{"".join(group)}</optgroup>'
        )
    if len(sets) < 2:
        return _sec("Scan Diff", "<p>Needs at least two Scans.</p>")
    targets = {ip: {"name": h.short, "zone": h.zone} for ip, h in a.inv.items()}
    data = _json({"sets": sets, "targets": targets})
    select = "".join(options)
    return _sec(
        "Scan Diff",
        '<p class="hint">Compares the open ports seen by two Scans or Source Views: over time '
        "(same Source, before / after a fix) or across Sources (what one sees that the other does not). "
        "<b>added</b> = open in B, tested and not open in A; <b>removed</b> = the reverse; "
        "<b>not comparable</b> = the other side did not test the port (or its Coverage is unknown).</p>"
        f'<div class="srcbar"><label>A <select id="diff-a" onchange="runDiff()">{select}</select></label>'
        f'<label>B <select id="diff-b" onchange="runDiff()">{select}</select></label></div>'
        f'<div id="diff-out"></div><script type="application/json" id="diff-data">{data}</script>',
    )


def _flows_table(rows: list[list[str]], head: list[str]) -> str:
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return (
        f'<div class="tablewrap"><table><thead><tr>{"".join(f"<th>{h}</th>" for h in head)}'
        f"</tr></thead><tbody>{body or '<tr><td>None.</td></tr>'}</tbody></table></div>"
    )


def _policy_tab(a: Analysis) -> str:
    inv, e = a.inv, html.escape
    hits = Counter(r.line for r in a.decisions.values() if r is not None)
    side = ["source", "src zone", "target", "dst zone", "port"]

    def flow(s: str, d: str, p: Port) -> list[str]:
        return [
            e(inv[s].short),
            e(inv[s].zone),
            e(inv[d].short),
            e(inv[d].zone),
            _ports_html([p], a.highlight),
        ]

    def zkey(t: tuple) -> tuple:
        return inv[t[0]].zone, inv[t[1]].zone, t

    findings = [flow(s, d, p) + [e(str(r)), e(r.comment)] for s, d, p, r in sorted(a.findings, key=zkey)]
    undeclared = [flow(s, d, p) for s, d, p in sorted(a.undeclared, key=zkey)]
    rules = [
        [str(r.line), e(r.src), e(r.dst), e(r.ports_spec), r.action, e(r.comment), str(hits[r.line])]
        + ([] if hits[r.line] else ['<span class="warn">never matched</span>'])
        for r in a.policy or []
    ]
    allowed = len(a.decisions) - len(findings) - len(undeclared)
    never = sum(1 for r in a.policy or [] if not hits[r.line])

    def tile(target: str, cls: str, icon: str, n: int, what: str, sub: str) -> str:
        go = f"document.getElementById('{target}').scrollIntoView({{behavior:'smooth'}})" if target else ""
        return f'<a class="tile {cls}" onclick="{go}">{icon}<b>{n}</b> {what}<small>{sub}</small></a>'

    return (
        '<div class="tiles">'
        + tile("pf", "t-deny", _pg(DENY), len(findings), "Finding(s)", "OPEN flows the Flow Policy denies")
        + tile(
            "pu", "t-undeclared", _pg(UNDECLARED), len(undeclared), "undeclared", "OPEN flows no rule covers"
        )
        + tile("", "t-allow", _pg(ALLOW), allowed, "allowed", "OPEN flows a rule allows")
        + tile("pr", "", "", len(a.policy or []), "rule(s)", f"{never} never matched")
        + "</div>"
        '<p class="hint">Evaluated on OPEN ports. The most specific rule wins (src Machine &gt; Zone &gt; *, '
        "then dst, then listed ports &gt; *); at equal specificity deny wins. A flow no rule covers is "
        "undeclared, never a Finding.</p>"
        + _sec(
            '<span id="pf">Findings: OPEN flows explicitly denied</span>',
            _flows_table(findings, side + ["rule", "comment"]),
        )
        + _sec('<span id="pu">Undeclared flows</span>', _flows_table(undeclared, side))
        + _sec(
            '<span id="pr">Rules</span>',
            _flows_table(rules, ["line", "src", "dst", "ports", "action", "comment", "flows decided", ""]),
        )
    )


def _tabs(a: Analysis) -> list[tuple[str, str, str, str, Callable[[Analysis], str]]]:
    """(key, title, count, one-line description, render) of the big tabs, in display order."""
    n_scans = sum(len(v) for v in a.scans.values())
    n_conf = sum(len(c.conflicts) for row in a.matrix.values() for c in row.values())
    reached = sum(1 for d in a.inv if any(d in r and r[d].verdict >= ALIVE for r in a.matrix.values()))
    policy = f"{len(a.findings)} Findings · {len(a.undeclared)} undeclared" if a.policy is not None else ""
    tabs = [
        (
            "global",
            "Global view",
            f"{len(zone_palette(a.inv))} zones",
            "diagram, zone and host matrices",
            _global_tab,
        ),
        ("policy", "Flow Policy", policy, "Findings, undeclared flows, rules", _policy_tab),
        ("pivots", "Pivot Machines", str(len(a.pivots)), "rebounds into other zones", _pivots_tab),
        ("persource", "Per source", str(len(a.sources)), "what each Source reaches", _persource_tab),
        ("pertarget", "Per target", str(reached), "who reaches each target", _pertarget_tab),
        (
            "scans",
            "Scans",
            f"{n_scans} · {n_conf} conflict(s)",
            "coverage, conflicts, anomalies",
            lambda a: _scans_tab(a) + _anomalies_tab(a),
        ),
        ("diff", "Diff", "", "before / after, Source vs Source", _diff_tab),
    ]
    return [t for t in tabs if t[0] != "policy" or a.policy is not None]


def _group_filter(a: Analysis) -> str:
    """Port Group chips (filter every tab to the OPEN flows of the group; a dropdown beyond 8 groups)
    and the groups as JSON."""
    if not a.port_groups:
        return ""
    names = list(a.port_groups)
    if len(names) > 8:
        opts = "".join(f'<option value="{i}">{html.escape(g)}</option>' for i, g in enumerate(names))
        picker = f'<select onchange="setGroup(this.value)"><option value="">all ports</option>{opts}</select>'
    else:
        picker = '<button class="gchip on" data-g="" onclick="pickGroup(this)">all ports</button>' + "".join(
            f'<button class="gchip" data-g="{i}" onclick="pickGroup(this)">{html.escape(g)}</button>'
            for i, g in enumerate(names)
        )
    data = _json(list(a.port_groups.values()))
    return (
        f'<div class="groupsel"><span>Port Group</span><div>{picker}</div>'
        '<span class="note">This filter applies to every tab.</span></div>'
        f'<script type="application/json" id="port-groups">{data}</script>'
    )


def write_html(a: Analysis, out_dir: str) -> str:
    tabs = _tabs(a)
    n_scans = sum(len(v) for v in a.scans.values())
    meta = (
        f"{len(a.inv)} targets · {len(a.sources)} Source(s) · {n_scans} Scan(s) · "
        f"{len(a.unknown)} host(s) outside the inventory · {len(a.orphan)} ignored Scan(s)"
    )
    buttons = "".join(
        f'<a class="{"on" if i == 0 else ""}" data-tab="{key}" href="#{key}" '
        f"onclick=\"showTab('{key}');return false\">"
        f"<b>{title}{f'<span class=n>{count}</span>' if count else ''}</b><span>{desc}</span></a>"
        for i, (key, title, count, desc, _) in enumerate(tabs)
    )
    panes = "".join(
        f'<section id="tab-{key}" class="pane{" active" if i == 0 else ""}">{render(a)}</section>'
        for i, (key, _, _, _, render) in enumerate(tabs)
    )
    doc = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="{FAVICON}">
<title>SegOWL segmentation report</title>
<style>{HTML_CSS}</style></head><body>
<script>if(window.self!==window.top) document.body.classList.add('embed');</script>
<header class="rhead"><div class="brand">{LOGO_SVG}<span>Seg<b>OWL</b></span></div>
<div><h1>Network segmentation report</h1><div class="meta">{meta}</div></div></header>
<div class="rtop"><div class="bigtabs">{buttons}</div>{_group_filter(a)}</div>
<main>{panes}</main>
<script>{GRAPH_JS}</script>
<script>{HTML_JS}</script></body></html>"""
    return write_output(out_dir, "report.html", doc)
