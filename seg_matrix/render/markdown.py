"""Markdown and CSV outputs."""

from __future__ import annotations

import csv
import os

from seg_matrix.analysis import Analysis, Exposure, Matrix, ZoneMatrix
from seg_matrix.inventory import Inventory, ordered_ips
from seg_matrix.ports import port_label, ports_text
from seg_matrix.render.common import write_output, zone_cell, zone_palette
from seg_matrix.verdict import VERDICT_NAME, Cell, cell_text


def write_host_matrix_md(matrix: Matrix, inv: Inventory, out_dir: str) -> None:
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
                w.writerow(
                    [
                        s,
                        d,
                        inv[s].zone,
                        inv[d].zone,
                        VERDICT_NAME[c.verdict],
                        ports_text(c.open_ports),
                    ]
                )
    lines = [
        "# Consolidated host -> host matrix",
        "",
        "Legend: `OPEN`=service reachable | `o`=reachable (closed) | `~`=alive (ping/ARP) | "
        "`x`=blocked | `.`=unseen | `-`=same machine",
        "",
        "| source \\ target | " + " | ".join(inv[d].short for d in dsts) + " |",
        "|" + "---|" * (len(dsts) + 1),
    ]
    for s in srcs:
        cells = []
        for d in dsts:
            if inv[d].machine == inv[s].machine:
                cells.append("-")
                continue
            cells.append(cell_text(matrix[s].get(d, Cell())))
        lines.append(f"| **{inv[s].short}** | " + " | ".join(cells) + " |")
    write_output(out_dir, "matrix_hosts.md", "\n".join(lines))


def write_zone_matrix_md(agg: ZoneMatrix, inv: Inventory, out_dir: str) -> None:
    zones = sorted(zone_palette(inv))
    md = [
        "# Consolidated zone -> zone matrix",
        "",
        "| src \\ dst | " + " | ".join(zones) + " |",
        "|" + "---|" * (len(zones) + 1),
    ]
    for zs in zones:
        cells = []
        for zd in zones:
            a = agg.get((zs, zd))
            _, txt = zone_cell(a)
            cells.append(txt + (f" ({a.reach_pairs}/{a.total_pairs})" if a and a.reach_pairs else ""))
        md.append(f"| **{zs}** | " + " | ".join(cells) + " |")
    write_output(out_dir, "matrix_zones.md", "\n".join(md))


def write_exposure_md(exp: Exposure, inv: Inventory, out_dir: str) -> None:
    lines = ["# Exposure per target (who reaches what)", ""]
    for d in inv:
        opens, reach = exp[d]
        if not opens and not reach:
            continue
        lines.append(f"## {inv[d].short} — {inv[d].ip} ({inv[d].zone}/{inv[d].htype})")
        for s, ports in opens:
            lines.append(f"- OPEN from **{inv[s].short}** ({inv[s].zone}): {ports_text(ports)}")
        for s in reach:
            lines.append(f"- reachable (closed) from {inv[s].short} ({inv[s].zone})")
        lines.append("")
    write_output(out_dir, "exposure_targets.md", "\n".join(lines))


def write_findings_md(a: Analysis, out_dir: str) -> None:
    """Findings (flows the Flow Policy explicitly denies) and Undeclared Flows; only with a Flow Policy."""
    inv = a.inv
    lines = [
        "# Findings",
        "",
        "Observed OPEN flows explicitly denied by the Flow Policy.",
        "",
        "| src zone | source | dst zone | target | port | rule | comment |",
        "|---|---|---|---|---|---|---|",
    ]
    rows = sorted(
        (inv[s].zone, inv[s].short, inv[d].zone, inv[d].short, port_label(p), str(r), r.comment)
        for s, d, p, r in a.findings
    )
    lines += ["| " + " | ".join(row) + " |" for row in rows] or ["_None._"]
    lines += [
        "",
        "## Undeclared flows",
        "",
        "Observed OPEN flows the Flow Policy says nothing about.",
        "",
        "| src zone | source | dst zone | target | port |",
        "|---|---|---|---|---|",
    ]
    rows = sorted(
        (inv[s].zone, inv[s].short, inv[d].zone, inv[d].short, port_label(p)) for s, d, p in a.undeclared
    )
    lines += ["| " + " | ".join(row) + " |" for row in rows] or ["_None._"]
    write_output(out_dir, "findings.md", "\n".join(lines))
