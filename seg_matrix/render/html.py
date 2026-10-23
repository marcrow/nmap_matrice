"""Standalone tabbed HTML report (offline: mermaid is inlined when bundled)."""

from __future__ import annotations

import html
import sys
from collections import defaultdict
from pathlib import Path

from seg_matrix.analysis import Exposure, Matrix, Row, ZoneMatrix
from seg_matrix.inventory import Inventory, ordered_ips
from seg_matrix.ports import ports_text
from seg_matrix.render.common import machine_palette, write_output, zone_cell, zone_palette
from seg_matrix.render.mermaid import hid, mermaid_source, mermaid_zone, zid
from seg_matrix.verdict import REACH, VCLASS, VERDICT_NAME, Cell, cell_text

ASSETS = Path(__file__).resolve().parent.parent / "assets"
HTML_CSS = (ASSETS / "report.css").read_text(encoding="utf-8")
HTML_JS = (ASSETS / "report.js").read_text(encoding="utf-8")
MERMAID_JS = ASSETS / "mermaid.min.js"  # bundled -> inlined in report.html (offline)
MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"


def _cell_html(c: Cell) -> str:
    return f'<td class="{VCLASS[c.verdict]}">{html.escape(cell_text(c))}</td>'


def _host_matrix_html(matrix: Matrix, inv: Inventory) -> str:
    dsts = ordered_ips(inv)
    srcs = [ip for ip in dsts if ip in matrix]
    mpal = machine_palette(inv)

    def th(ip: str) -> str:
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
        rows.append(f"<tr>{th(s)}{''.join(cells)}</tr>")
    return (
        f'<div class="tablewrap"><table><thead><tr><th>source \\ target</th>{head}</tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )


def _zone_matrix_html(agg: ZoneMatrix, inv: Inventory) -> str:
    zones = sorted(zone_palette(inv))
    head = "".join(f"<th>{html.escape(z)}</th>" for z in zones)
    rows = []
    for zs in zones:
        cells = []
        for zd in zones:
            a = agg.get((zs, zd))
            cls, txt = zone_cell(a)
            pairs = f"<br><small>{a.reach_pairs}/{a.total_pairs}</small>" if a and a.reach_pairs else ""
            cells.append(f'<td class="{cls}">{html.escape(txt)}{pairs}</td>')
        rows.append(f"<tr><th>{html.escape(zs)}</th>{''.join(cells)}</tr>")
    return (
        f'<div class="tablewrap"><table><thead><tr><th>src \\ dst</th>{head}</tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )


def _source_table_html(src: str, row: Row, inv: Inventory) -> str:
    rows = []
    for d in ordered_ips(inv):
        if inv[d].machine == inv[src].machine:
            continue
        c = row.get(d, Cell())
        ports = ports_text(c.open_ports)
        rows.append(
            f"<tr><th>{html.escape(inv[d].short)}</th>"
            f"<td>{html.escape(inv[d].zone)}</td><td>{html.escape(inv[d].htype)}</td>"
            f'<td class="{VCLASS[c.verdict]}">{VERDICT_NAME[c.verdict]}</td>'
            f"<td>{html.escape(ports)}</td></tr>"
        )
    return (
        '<div class="tablewrap"><table><thead><tr><th>target</th><th>zone</th><th>type</th>'
        f"<th>verdict</th><th>open ports</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
    )


def _exposure_html(exp: Exposure, inv: Inventory) -> str:
    blocks = []
    for d in inv:
        opens, reach = exp[d]
        if not opens and not reach:
            continue
        items = "".join(
            f'<li><span class="warn">OPEN</span> from <b>{html.escape(inv[s].short)}</b> '
            f'<span class="tag">{html.escape(inv[s].zone)}</span>: {ports_text(ports)}</li>'
            for s, ports in opens
        ) + "".join(
            f"<li>reachable (closed) from {html.escape(inv[s].short)} "
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


def write_html(
    matrix: Matrix,
    inv: Inventory,
    agg: ZoneMatrix,
    exp: Exposure,
    missing: list[str],
    unknown: list[str],
    orphan: list[str],
    out_dir: str,
) -> str:
    srcs = [ip for ip in ordered_ips(inv) if ip in matrix]
    legend = (
        '<div class="legend">'
        '<span class="v-open">OPEN service</span>'
        '<span class="v-reach">reachable (closed)</span>'
        '<span class="v-alive">alive (ping/ARP)</span>'
        '<span class="v-block">blocked</span>'
        '<span class="v-none">unseen</span>'
        '<span style="color:#e11d48">— red = cross-zone OPEN</span></div>'
    )

    # Global tab
    glob = [
        "<h2>Global diagram (zone &rarr; zone)</h2>",
        _zone_legend_html(inv),
        legend,
        f'<pre class="mermaid">{html.escape(mermaid_zone(agg, inv))}</pre>',
        "<h2>Consolidated zone &rarr; zone matrix</h2>",
        _zone_matrix_html(agg, inv),
        "<h2>Consolidated host &rarr; host matrix</h2>",
        legend,
        _host_matrix_html(matrix, inv),
        "<h2>Exposure per target</h2>",
        _exposure_html(exp, inv),
    ]

    # Per-source tab
    by_m = defaultdict(list)
    for s in srcs:
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
    src_panes = []
    for i, s in enumerate(srcs):
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
        src_panes.append(
            f'<div class="srcpane" id="src_{hid(s)}" style="display:{disp}">'
            f"<h2>{html.escape(inv[s].short)} "
            f'<span class="tag">{html.escape(inv[s].zone)} · {html.escape(inv[s].htype)} · {s}</span></h2>'
            f'{bar}<pre class="mermaid">{html.escape(mermaid_source(s, matrix[s], inv))}</pre>'
            f"<h3>Target details</h3>{_source_table_html(s, matrix[s], inv)}</div>"
        )
    persource = [f'<select id="srcsel" onchange="showSource(this.value)">{options}</select>'] + src_panes

    # Anomalies tab
    anomalies = ["<h2>Sources without scan</h2>"]
    anomalies.append(
        "<ul>"
        + (
            "".join(
                f"<li>{ip} — {html.escape(inv[ip].short)} "
                f'<span class="tag">{html.escape(inv[ip].zone)}</span></li>'
                for ip in missing
            )
            or "<li>None</li>"
        )
        + "</ul>"
    )
    anomalies.append("<h2>Reachable hosts outside the inventory</h2>")
    anomalies.append(
        "<ul>" + ("".join(f'<li class="warn">{ip}</li>' for ip in unknown) or "<li>None</li>") + "</ul>"
    )
    anomalies.append(
        "<h2>Ignored scans</h2><p>Source folder or file name is not an inventory IP "
        "(expected: <code>scans/&lt;source_ip&gt;/*.xml</code> "
        "or <code>scans/&lt;source_ip&gt;.xml</code>).</p>"
    )
    anomalies.append(
        "<ul>"
        + ("".join(f'<li class="warn">{html.escape(ip)}</li>' for ip in orphan) or "<li>None</li>")
        + "</ul>"
    )

    if MERMAID_JS.is_file():
        mjs = (
            "<script>"
            + MERMAID_JS.read_text(encoding="utf-8").replace("</script", "<\\/script")
            + "</script>"
        )
    else:
        print(
            f"[!] {MERMAID_JS.name} missing next to the script: report.html will load mermaid from the CDN "
            "(network required)",
            file=sys.stderr,
        )
        mjs = f'<script src="{MERMAID_CDN}"></script>'

    meta = (
        f"{len(inv)} targets · {len(srcs)} scanned source(s) · {len(missing)} without scan · "
        f"{len(unknown)} host(s) outside inventory · {len(orphan)} ignored scan(s)"
    )
    doc = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Segmentation report</title>
{mjs}
<style>{HTML_CSS}</style></head><body>
<header><h1>Network segmentation report</h1>
<div class="meta">{meta}</div></header>
<div class="tabs">
<button class="tab active" data-tab="global" onclick="showTab('global')">Global view</button>
<button class="tab" data-tab="persource" onclick="showTab('persource')">Per source</button>
<button class="tab" data-tab="anomalies" onclick="showTab('anomalies')">Anomalies</button>
</div>
<section id="tab-global" class="pane active">{"".join(glob)}</section>
<section id="tab-persource" class="pane">{"".join(persource)}</section>
<section id="tab-anomalies" class="pane">{"".join(anomalies)}</section>
<script>{HTML_JS}</script></body></html>"""
    return write_output(out_dir, "report.html", doc)
