"""Standalone tabbed HTML report (offline: mermaid is inlined when bundled)."""

from __future__ import annotations

import html
import json
import os
import re
import sys
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable
from pathlib import Path

from seg_matrix.analysis import Analysis, Exposure, Matrix, Row, ZoneMatrix, aggregate_zones
from seg_matrix.inventory import Host, Inventory, extra_columns, ordered_ips
from seg_matrix.ports import Port, count_ports, format_ranges, port_label, ports_text
from seg_matrix.render.common import machine_palette, write_output, zone_cell, zone_palette
from seg_matrix.render.mermaid import EdgeStatus, hid, mermaid_source, mermaid_zone, zid
from seg_matrix.verdict import REACH, STATE_RANK, VCLASS, VERDICT_NAME, Cell, cell_text

ASSETS = Path(__file__).resolve().parent.parent / "assets"
HTML_CSS = (ASSETS / "report.css").read_text(encoding="utf-8")
HTML_JS = (ASSETS / "report.js").read_text(encoding="utf-8")
MERMAID_JS = ASSETS / "mermaid.min.js"  # bundled -> inlined in report.html (offline)
MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"


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


def _ports_attr(ports: Iterable[Port], highlight: Highlight) -> tuple[str, str]:
    """(data-p attribute read by the Port Group filter, highlight class) of an element showing open ports."""
    ports = list(ports)
    return f' data-p="{ports_text(ports)}"', " admin" if any(highlight(p) for p in ports) else ""


def _cell_html(c: Cell, highlight: Highlight = _no_highlight) -> str:
    attr, hl = _ports_attr(c.open_ports, highlight)
    cls = VCLASS[c.verdict] + (" conflict" if c.conflicts else "") + hl
    return f'<td class="{cls}"{attr} title="{_provenance(c)}">{html.escape(cell_text(c))}</td>'


def _host_title(h: Host) -> str:
    """Tooltip of an Interface: zone, type and free inventory columns."""
    return html.escape(
        " · ".join([h.ip, h.zone, h.htype] + [f"{k}: {v}" for k, v in h.extra.items()]), quote=True
    )


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
        cells = []
        for d in dsts:
            if inv[d].machine == inv[s].machine:
                cells.append('<td class="v-self">-</td>')
            else:
                cell = _cell_html(matrix[s].get(d, Cell()), highlight)
                if st := (status or {}).get((s, d)):
                    cell = cell.replace('<td class="', f'<td class="p-{st} ', 1)
                cells.append(cell)
        rows.append(f"<tr>{th(s)}{''.join(cells)}</tr>")
    return (
        f'<div class="tablewrap"><table><thead><tr><th>source \\ target</th>{head}</tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )


def _zone_matrix_html(
    agg: ZoneMatrix, inv: Inventory, highlight: Highlight = _no_highlight, status: EdgeStatus | None = None
) -> str:
    zones = sorted(zone_palette(inv))
    head = "".join(f"<th>{html.escape(z)}</th>" for z in zones)
    rows = []
    for zs in zones:
        cells = []
        for zd in zones:
            a = agg.get((zs, zd))
            cls, txt = zone_cell(a)
            pairs = f"<br><small>{a.reach_pairs}/{a.total_pairs}</small>" if a and a.reach_pairs else ""
            attr, hl = _ports_attr(a.open_ports if a else [], highlight)
            st = (status or {}).get((zs, zd))
            cls += f" p-{st}" if st else ""
            cells.append(f'<td class="{cls}{hl}"{attr}>{html.escape(txt)}{pairs}</td>')
        rows.append(f"<tr><th>{html.escape(zs)}</th>{''.join(cells)}</tr>")
    return (
        f'<div class="tablewrap"><table><thead><tr><th>src \\ dst</th>{head}</tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )


def _ranges_html(ranges: list[tuple[int, int]], cap: int = 60) -> str:
    """Port ranges, shortened when long (e.g. --top-ports 1000); the full list is in the tooltip."""
    full = format_ranges(ranges)
    if len(full) <= cap:
        return html.escape(full)
    short = html.escape(full[:cap].rsplit(",", 1)[0])
    return f'<span title="{html.escape(full, quote=True)}">{short},&hellip;</span>'


def _tested_html(c: Cell) -> str:
    """Coverage of a cell: ports tested per protocol, '?' when a non-XML Scan cannot tell."""
    if not c.scans:
        return ""
    parts = [f"{proto} {_ranges_html(r)}" for proto, r in sorted(c.tested.items())]
    if not c.coverage_known:
        parts.append('<span class="warn" title="a Scan behind this cell is not XML">?</span>')
    return "<br>".join(parts)


def _source_table_html(src: str, row: Row, inv: Inventory, highlight: Highlight = _no_highlight) -> str:
    extras = extra_columns(inv)
    rows = []
    for d in ordered_ips(inv):
        if inv[d].machine == inv[src].machine:
            continue
        c = row.get(d, Cell())
        attr, hl = _ports_attr(c.open_ports, highlight)
        rows.append(
            f"<tr><th>{html.escape(inv[d].short)}</th>"
            f"<td>{html.escape(inv[d].zone)}</td><td>{html.escape(inv[d].htype)}</td>"
            f'<td class="{VCLASS[c.verdict]}">{VERDICT_NAME[c.verdict]}</td>'
            f'<td class="{hl.strip()}"{attr}>{html.escape(ports_text(c.open_ports))}</td>'
            f"<td>{_tested_html(c)}</td>"
            f"<td>{html.escape(', '.join(sc.split('/', 1)[1] for sc in c.scans))}</td>"
            + "".join(f"<td>{html.escape(inv[d].extra.get(k, ''))}</td>" for k in extras)
            + "</tr>"
        )
    return (
        '<div class="tablewrap"><table><thead><tr><th>target</th><th>zone</th><th>type</th>'
        "<th>verdict</th><th>open ports</th><th>tested ports</th><th>scans</th>"
        + "".join(f"<th>{html.escape(k)}</th>" for k in extras)
        + f"</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
    )


def _exposure_html(exp: Exposure, inv: Inventory, highlight: Highlight = _no_highlight) -> str:
    blocks = []
    for d in inv:
        opens, reach = exp[d]
        if not opens and not reach:
            continue
        items = "".join(
            '<li class="{1}"{0}>'.format(*_ports_attr(ports, highlight))
            + '<span class="warn">OPEN</span> from '
            f"<b>{html.escape(inv[s].short)}</b> "
            f'<span class="tag">{html.escape(inv[s].zone)}</span>: '
            f'<span class="pl">{ports_text(ports)}</span></li>'
            for s, ports in opens
        ) + "".join(
            f'<li data-p="">reachable (closed) from {html.escape(inv[s].short)} '
            f'<span class="tag">{html.escape(inv[s].zone)}</span></li>'
            for s in reach
        )
        blocks.append(
            f'<div class="card"><b>{html.escape(inv[d].short)}</b> '
            f'<span class="tag">{html.escape(inv[d].zone)} · {html.escape(inv[d].htype)}</span>'
            f"<ul>{items}</ul></div>"
        )
    return "".join(blocks) or "<p>No exposure.</p>"


def _zone_legend_html(inv: Inventory) -> str:
    pal = zone_palette(inv)
    chips = "".join(
        f'<span style="background:{f};border:1px solid {s};color:{t};'
        f'padding:2px 9px;border-radius:12px;margin:0 6px 4px 0;display:inline-block;font-size:12px;">'
        f"{html.escape(z)}</span>"
        for z, (f, s, t) in sorted(pal.items())
    )
    return f'<div style="margin:4px 0 12px;">{chips}</div>'


def _legend(policy: bool = False) -> str:
    colours = (
        '<span class="p-deny v-open">denied (Finding)</span>'
        '<span class="p-undeclared v-open">undeclared</span>'
        '<span class="p-allow v-open">allowed</span> — OPEN flows by Flow Policy'
        if policy
        else '<span style="color:#e11d48">— red = cross-zone OPEN</span>'
    )
    return (
        '<div class="legend">'
        '<span class="v-open">OPEN service</span>'
        '<span class="v-reach">reachable (closed)</span>'
        '<span class="v-alive">alive (ping/ARP)</span>'
        '<span class="v-block">blocked</span>'
        '<span class="v-none">unseen</span>'
        '<span class="v-none conflict">Scans disagree</span>'
        f"{colours}</div>"
    )


def _zone_tag(z: str) -> str:
    return f'<span class="tag">{html.escape(z)}</span>'


def _pivots_html(a: Analysis) -> str:
    inv, blocks = a.inv, []
    for machine, hits in sorted(a.pivots.items()):
        zones = sorted({h.zone for h in inv.values() if h.machine == machine})
        by_zone = defaultdict(list)
        for s, d, ports in hits:
            by_zone[inv[s].zone].append((s, d, ports))
        groups = []
        for z, rows in sorted(by_zone.items()):
            onward = ", ".join(_zone_tag(x) for x in zones if x != z)
            items = "".join(
                '<li class="{1}"{0}>'.format(*_ports_attr(ports, a.highlight))
                + f"{html.escape(inv[s].short)} &rarr; {html.escape(d)} {_zone_tag(inv[d].zone)}: "
                f'<span class="pl">{ports_text(ports)}</span></li>'
                for s, d, ports in rows
            )
            groups.append(f"<div>from {_zone_tag(z)} &rarr; leads to {onward}<ul>{items}</ul></div>")
        blocks.append(
            f'<div class="card"><b>{html.escape(machine)}</b> spans {", ".join(_zone_tag(z) for z in zones)}'
            f"{''.join(groups)}</div>"
        )
    return "".join(blocks) or "<p>None: no machine spanning several zones is reached OPEN.</p>"


def _diagram(base: str, variants: list[str]) -> str:
    """Mermaid block; data-g<i> holds the diagram restricted to the i-th Port Group (filter in the header)."""
    attrs = "".join(f' data-g{i}="{html.escape(v, quote=True)}"' for i, v in enumerate(variants))
    return f'<pre class="mermaid"{attrs}>{html.escape(base)}</pre>'


def _global_tab(a: Analysis) -> str:
    return "".join(
        [
            "<h2>Global diagram (zone &rarr; zone)</h2>",
            _zone_legend_html(a.inv),
            _legend(a.policy is not None),
            _diagram(
                mermaid_zone(a.agg, a.inv, a.highlight, a.zone_status(a.matrix)),
                [
                    mermaid_zone(aggregate_zones(m, a.inv), a.inv, a.highlight, a.zone_status(m))
                    for m in a.group_matrices.values()
                ],
            ),
            "<h2>Consolidated zone &rarr; zone matrix</h2>",
            _zone_matrix_html(a.agg, a.inv, a.highlight, a.zone_status(a.matrix)),
            "<h2>Consolidated host &rarr; host matrix</h2>",
            '<p class="legend">Hover a cell for the Scans behind its verdict.</p>',
            _legend(a.policy is not None),
            _host_matrix_html(a.matrix, a.inv, a.highlight, a.pair_status(a.matrix)),
            "<h2>Pivot Machines</h2>",
            '<p class="legend">Machines spanning several zones and reached OPEN: from the source zone, '
            "a one-hop path to the machine's other zones.</p>",
            _pivots_html(a),
            "<h2>Exposure per target</h2>",
            _exposure_html(a.exp, a.inv, a.highlight),
        ]
    )


def _persource_tab(a: Analysis) -> str:
    inv, matrix = a.inv, a.matrix
    status = a.pair_status(matrix)
    group_views = [(m, a.pair_status(m)) for m in a.group_matrices.values()]
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
        disp = "block" if i == 0 else "none"
        zs = sorted({inv[d].zone for d, c in matrix[s].items() if c.verdict >= REACH})
        boxes = "".join(
            f'<label><input type="checkbox" checked value="{zid(z)}" onchange="refilter(this)"> '
            f"{html.escape(z)}</label>"
            for z in zs
        )
        bar = (
            f'<div class="srcbar" data-name="{html.escape(inv[s].short)}"><b>Zones:</b>{boxes}'
            "<span><button onclick=\"exportImg(this,'svg')\">Export SVG</button> "
            "<button onclick=\"exportImg(this,'png')\">Export PNG</button></span></div>"
        )
        panes.append(
            f'<div class="srcpane" id="src_{hid(s)}" style="display:{disp}">'
            f"<h2>{html.escape(inv[s].short)} "
            f'<span class="tag">{html.escape(inv[s].zone)} · {html.escape(inv[s].htype)} · {s}</span>'
            f'<span class="tag">{len(a.scans[s])} scan(s)</span></h2>'
            + bar
            + _diagram(
                mermaid_source(s, matrix[s], inv, a.highlight, status),
                [mermaid_source(s, m[s], inv, a.highlight, st) for m, st in group_views],
            )
            + f"<h3>Target details</h3>{_source_table_html(s, matrix[s], inv, a.highlight)}</div>"
        )
    return f'<select id="srcsel" onchange="showSource(this.value)">{options}</select>' + "".join(panes)


def _filter_box() -> str:
    return '<input class="filter" placeholder="Filter rows..." oninput="filterRows(this)">'


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
                cov = "<br>".join(
                    (
                        f'{proto} <span title="{html.escape(format_ranges(r), quote=True)}">'
                        f"top-ports {top.group(1)}</span>"
                        if top
                        else f"{proto} {_ranges_html(r)}"
                    )
                    + f" <small>({count_ports(r)} ports)</small>"
                    for proto, r in sorted(sc.coverage.items())
                )
            rows.append(
                f"<tr><th>{html.escape(h.short)}</th><td>{html.escape(h.zone)}</td>"
                f"<td>{html.escape(sc.name.split('/', 1)[1])}</td><td>{html.escape(sc.started)}</td>"
                f"<td>{cov}</td><td>{len(sc.hosts)}</td>"
                f'<td class="{"warn" if conflicts[sc.name] else ""}">{conflicts[sc.name] or ""}</td>'
                f'<td class="cmd"><code>{html.escape(sc.command)}</code></td></tr>'
            )
    scans_table = (
        f'{_filter_box()}<div class="tablewrap"><table><thead><tr>'
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
                    f"{html.escape(st)} <small>{html.escape(sc.split('/', 1)[1])}</small>"
                    for sc, st in states.items()
                )
                from_ = ", ".join(sc.split("/", 1)[1] for sc, st in states.items() if st == kept)
                conf_rows.append(
                    f"<tr><th>{html.escape(a.inv[src].short)}</th><th>{html.escape(a.inv[d].short)}</th>"
                    f"<td>{html.escape(a.inv[d].zone)}</td><td>{port_label(port)}</td><td>{seen}</td>"
                    f"<td><b>{html.escape(kept)}</b> <small>from {html.escape(from_)}</small></td></tr>"
                )
    conflicts_table = (
        f'{_filter_box()}<div class="tablewrap"><table><thead><tr><th>source</th><th>target</th>'
        "<th>zone</th><th>port</th><th>state per Scan</th><th>kept (most permissive)</th></tr></thead>"
        f"<tbody>{''.join(conf_rows)}</tbody></table></div>"
        if conf_rows
        else "<p>None: the Scans of each Source agree on every port listed.</p>"
    )
    excluded = "".join(
        f"<li>{html.escape(a.inv[src].short if src in a.inv else src)}: "
        f"<code>{html.escape(os.path.relpath(p, os.path.dirname(os.path.dirname(paths[0]))))}</code></li>"
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
                cells.append('<td class="v-self">-</td>')
            elif not c.scans:
                cells.append('<td class="v-none" title="in no Scan output">.</td>')
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
        f'{_filter_box()}<div class="tablewrap"><table><thead>'
        f"<tr><th>target \\ source</th>{head}</tr></thead>"
        f"<tbody>{''.join(cov_rows)}</tbody></table></div>"
    )
    return (
        "<h2>Scans</h2>"
        '<p class="legend">One row per Scan. When Scans of a Source disagree on a port, the most '
        "permissive state wins (an open port seen once proves the flow passed); the conflicts column "
        "counts the disagreements a Scan takes part in, detailed in the matrix cell tooltips.</p>"
        f"{scans_table}"
        "<h2>Conflicts</h2>"
        '<p class="legend">Ports on which the Scans of a Source disagree. To take a Scan out of the '
        "analysis, move its file into a sub-folder of its source folder (e.g. "
        "<code>scans/&lt;source_ip&gt;/excluded/</code>) and regenerate the report: it is then listed "
        "below as excluded, not read.</p>"
        f"{conflicts_table}"
        f"<h3>Excluded scans</h3><ul>{excluded or '<li>None</li>'}</ul>"
        "<h2>Coverage per target</h2>"
        '<p class="legend">Number of ports tested per protocol from each Source (number of Scans); '
        "<code>.</code> = in no Scan output, <code>?</code> = a non-XML Scan does not tell which ports it "
        "tested. Hover a cell for the Scans.</p>"
        f"{coverage_table}"
    )


def _anomalies_tab(a: Analysis) -> str:
    inv = a.inv
    missing = "".join(
        f'<li>{ip} — {html.escape(inv[ip].short)} <span class="tag">{html.escape(inv[ip].zone)}</span></li>'
        for ip in a.missing
    )
    unknown = "".join(f'<li class="warn">{ip}</li>' for ip in a.unknown)
    orphan = "".join(f'<li class="warn">{html.escape(ip)}</li>' for ip in a.orphan)
    return (
        f"<h2>Sources without scan</h2><ul>{missing or '<li>None</li>'}</ul>"
        f"<h2>Reachable hosts outside the inventory</h2><ul>{unknown or '<li>None</li>'}</ul>"
        "<h2>Ignored scans</h2><p>Source folder or file name is not an inventory IP "
        "(expected: <code>scans/&lt;source_ip&gt;/*.xml</code> "
        f"or <code>scans/&lt;source_ip&gt;.xml</code>).</p><ul>{orphan or '<li>None</li>'}</ul>"
        "<h2>Asymmetric flows</h2>"
        '<p class="legend">A reaches B (OPEN or closed ports) while B &rarr; A is blocked: typically a '
        "one-way firewall rule. Only pairs where both are Sources and both directions tested common "
        "ports.</p>" + _asymmetry_html(a)
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
        f"<h3>Detail</h3>{_filter_box()}"
        '<div class="tablewrap"><table><thead><tr><th>A</th><th>zone</th><th>B</th><th>zone</th>'
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
            (f"{sc.name.split('/', 1)[1]} · {sc.started}", a.scan_row(sc)) for sc in a.scans[src]
        ]:
            group.append(f'<option value="{len(sets)}">{html.escape(label)}</option>')
            sets.append({"label": f"{h.short} — {label}", "cells": _diff_cells(row)})
        options.append(
            f'<optgroup label="{html.escape(h.short)} ({html.escape(h.zone)})">{"".join(group)}</optgroup>'
        )
    if len(sets) < 2:
        return "<h2>Scan Diff</h2><p>Needs at least two Scans.</p>"
    targets = {ip: {"name": h.short, "zone": h.zone} for ip, h in a.inv.items()}
    data = json.dumps({"sets": sets, "targets": targets}).replace("</", "<\\/")
    select = "".join(options)
    return (
        "<h2>Scan Diff</h2>"
        '<p class="legend">Compares the open ports seen by two Scans or Source Views: over time '
        "(same Source, before / after a fix) or across Sources (what one sees that the other does not). "
        "<b>added</b> = open in B, tested and not open in A; <b>removed</b> = the reverse; "
        "<b>not comparable</b> = the other side did not test the port (or its Coverage is unknown).</p>"
        f'<div class="srcbar"><label>A <select id="diff-a" onchange="runDiff()">{select}</select></label>'
        f'<label>B <select id="diff-b" onchange="runDiff()">{select}</select></label></div>'
        f'<div id="diff-out"></div><script type="application/json" id="diff-data">{data}</script>'
    )


def _mermaid_script() -> str:
    if MERMAID_JS.is_file():
        return (
            "<script>"
            + MERMAID_JS.read_text(encoding="utf-8").replace("</script", "<\\/script")
            + "</script>"
        )
    print(
        f"[!] {MERMAID_JS} missing: report.html will load mermaid from the CDN (network required)",
        file=sys.stderr,
    )
    return f'<script src="{MERMAID_CDN}"></script>'


def _flows_table(rows: list[list[str]], head: list[str]) -> str:
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return (
        f'{_filter_box()}<div class="tablewrap"><table><thead><tr>{"".join(f"<th>{h}</th>" for h in head)}'
        f"</tr></thead><tbody>{body or '<tr><td>None.</td></tr>'}</tbody></table></div>"
    )


def _policy_tab(a: Analysis) -> str:
    inv, e = a.inv, html.escape
    hits = Counter(r.line for r in a.decisions.values() if r is not None)
    side = ["source", "src zone", "target", "dst zone", "port"]

    def flow(s: str, d: str, p: Port) -> list[str]:
        return [e(inv[s].short), e(inv[s].zone), e(inv[d].short), e(inv[d].zone), port_label(p)]

    def zkey(t: tuple) -> tuple:
        return inv[t[0]].zone, inv[t[1]].zone, t

    findings = [flow(s, d, p) + [e(str(r)), e(r.comment)] for s, d, p, r in sorted(a.findings, key=zkey)]
    undeclared = [flow(s, d, p) for s, d, p in sorted(a.undeclared, key=zkey)]
    rules = [
        [str(r.line), e(r.src), e(r.dst), e(r.ports_spec), r.action, e(r.comment), str(hits[r.line]) or "0"]
        + ([] if hits[r.line] else ['<span class="warn">never matched</span>'])
        for r in a.policy or []
    ]
    allowed = len(a.decisions) - len(findings) - len(undeclared)
    return (
        "<h2>Flow Policy</h2>"
        f'<div class="legend"><span class="p-deny v-open">{len(findings)} Finding(s)</span>'
        f'<span class="p-undeclared v-open">{len(undeclared)} undeclared</span>'
        f'<span class="p-allow v-open">{allowed} allowed</span> '
        f"OPEN flows · {len(a.policy or [])} rule(s)</div>"
        '<p class="legend">Evaluated on OPEN ports. The most specific rule wins '
        "(src Machine &gt; Zone &gt; *, "
        "then dst, then listed ports &gt; *); at equal specificity deny wins. A flow no rule covers is "
        "undeclared, never a Finding.</p>"
        "<h3>Findings: OPEN flows explicitly denied</h3>"
        + _flows_table(findings, side + ["rule", "comment"])
        + "<h3>Undeclared flows</h3>"
        + _flows_table(undeclared, side)
        + "<h3>Rules</h3>"
        + _flows_table(rules, ["line", "src", "dst", "ports", "action", "comment", "flows decided", ""])
    )


TABS = (
    ("global", "Global view", _global_tab),
    ("policy", "Flow Policy", _policy_tab),
    ("persource", "Per source", _persource_tab),
    ("scans", "Scans", _scans_tab),
    ("diff", "Diff", _diff_tab),
    ("anomalies", "Anomalies", _anomalies_tab),
)


def _group_filter(a: Analysis) -> str:
    """Port Group selector (filters every view to the OPEN flows of the group) and the groups as JSON."""
    if not a.port_groups:
        return ""
    options = "".join(f'<option value="{i}">{html.escape(g)}</option>' for i, g in enumerate(a.port_groups))
    data = json.dumps(list(a.port_groups.values())).replace("</", "<\\/")
    return (
        '<label class="groupsel">Port group: <select onchange="setGroup(this.value)">'
        f'<option value="">all ports</option>{options}</select></label>'
        f'<script type="application/json" id="port-groups">{data}</script>'
    )


def write_html(a: Analysis, out_dir: str) -> str:
    tabs = [t for t in TABS if t[0] != "policy" or a.policy is not None]
    n_scans = sum(len(v) for v in a.scans.values())
    meta = (
        f"{len(a.inv)} targets · {len(a.sources)} scanned source(s) · {n_scans} scan(s) · "
        f"{len(a.missing)} without scan · {len(a.unknown)} host(s) outside inventory · "
        f"{len(a.orphan)} ignored scan(s)"
    )
    buttons = "".join(
        f'<button class="tab{" active" if i == 0 else ""}" data-tab="{key}" '
        f"onclick=\"showTab('{key}')\">{title}</button>"
        for i, (key, title, _) in enumerate(tabs)
    )
    panes = "".join(
        f'<section id="tab-{key}" class="pane{" active" if i == 0 else ""}">{render(a)}</section>'
        for i, (key, _, render) in enumerate(tabs)
    )
    doc = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Segmentation report</title>
{_mermaid_script()}
<style>{HTML_CSS}</style></head><body>
<header><h1>Network segmentation report</h1>
<div class="meta">{meta}</div>{_group_filter(a)}</header>
<div class="tabs">{buttons}</div>
{panes}
<script>{HTML_JS}</script></body></html>"""
    return write_output(out_dir, "report.html", doc)
