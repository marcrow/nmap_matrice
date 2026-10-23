"""Standalone tabbed HTML report (offline: mermaid is inlined when bundled)."""

from __future__ import annotations

import html
import json
import sys
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable
from pathlib import Path

from seg_matrix.analysis import Analysis, Exposure, Matrix, Row, ZoneMatrix, aggregate_zones
from seg_matrix.inventory import Host, Inventory, extra_columns, ordered_ips
from seg_matrix.ports import Port, count_ports, format_ranges, port_label, ports_text
from seg_matrix.render.common import machine_palette, write_output, zone_cell, zone_palette
from seg_matrix.render.mermaid import hid, mermaid_source, mermaid_zone, zid
from seg_matrix.verdict import REACH, VCLASS, VERDICT_NAME, Cell, cell_text

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


def _host_matrix_html(matrix: Matrix, inv: Inventory, highlight: Highlight = _no_highlight) -> str:
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
                cells.append(_cell_html(matrix[s].get(d, Cell()), highlight))
        rows.append(f"<tr>{th(s)}{''.join(cells)}</tr>")
    return (
        f'<div class="tablewrap"><table><thead><tr><th>source \\ target</th>{head}</tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )


def _zone_matrix_html(agg: ZoneMatrix, inv: Inventory, highlight: Highlight = _no_highlight) -> str:
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
            cells.append(f'<td class="{cls}{hl}"{attr}>{html.escape(txt)}{pairs}</td>')
        rows.append(f"<tr><th>{html.escape(zs)}</th>{''.join(cells)}</tr>")
    return (
        f'<div class="tablewrap"><table><thead><tr><th>src \\ dst</th>{head}</tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )


def _tested_html(c: Cell) -> str:
    """Coverage of a cell: ports tested per protocol, '?' when a non-XML Scan cannot tell."""
    if not c.scans:
        return ""
    parts = [f"{proto} {html.escape(format_ranges(r))}" for proto, r in sorted(c.tested.items())]
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


def _legend() -> str:
    return (
        '<div class="legend">'
        '<span class="v-open">OPEN service</span>'
        '<span class="v-reach">reachable (closed)</span>'
        '<span class="v-alive">alive (ping/ARP)</span>'
        '<span class="v-block">blocked</span>'
        '<span class="v-none">unseen</span>'
        '<span class="v-none conflict">Scans disagree</span>'
        '<span style="color:#e11d48">— red = cross-zone OPEN</span></div>'
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
            _legend(),
            _diagram(
                mermaid_zone(a.agg, a.inv, a.highlight),
                [
                    mermaid_zone(aggregate_zones(m, a.inv), a.inv, a.highlight)
                    for m in a.group_matrices.values()
                ],
            ),
            "<h2>Consolidated zone &rarr; zone matrix</h2>",
            _zone_matrix_html(a.agg, a.inv, a.highlight),
            "<h2>Consolidated host &rarr; host matrix</h2>",
            '<p class="legend">Hover a cell for the Scans behind its verdict.</p>',
            _legend(),
            _host_matrix_html(a.matrix, a.inv, a.highlight),
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
                mermaid_source(s, matrix[s], inv, a.highlight),
                [mermaid_source(s, m[s], inv, a.highlight) for m in a.group_matrices.values()],
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
                cov = "<br>".join(
                    f"{proto} {html.escape(format_ranges(r))} <small>({count_ports(r)} ports)</small>"
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


TABS = (
    ("global", "Global view", _global_tab),
    ("persource", "Per source", _persource_tab),
    ("scans", "Scans", _scans_tab),
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
    n_scans = sum(len(v) for v in a.scans.values())
    meta = (
        f"{len(a.inv)} targets · {len(a.sources)} scanned source(s) · {n_scans} scan(s) · "
        f"{len(a.missing)} without scan · {len(a.unknown)} host(s) outside inventory · "
        f"{len(a.orphan)} ignored scan(s)"
    )
    buttons = "".join(
        f'<button class="tab{" active" if i == 0 else ""}" data-tab="{key}" '
        f"onclick=\"showTab('{key}')\">{title}</button>"
        for i, (key, title, _) in enumerate(TABS)
    )
    panes = "".join(
        f'<section id="tab-{key}" class="pane{" active" if i == 0 else ""}">{render(a)}</section>'
        for i, (key, _, render) in enumerate(TABS)
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
