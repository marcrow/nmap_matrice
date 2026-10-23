"""Markdown and CSV outputs."""

from __future__ import annotations

import csv
import os

from seg_matrix.analysis import Exposure, Matrix, ZoneMatrix
from seg_matrix.inventory import Inventory, ordered_ips
from seg_matrix.ports import ports_text
from seg_matrix.render.common import write_output, zone_cell, zone_palette
from seg_matrix.verdict import OPEN, VERDICT_NAME, Cell, cell_text


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


def write_findings_md(
    matrix: Matrix, inv: Inventory, missing: list[str], unknown: list[str], orphan: list[str], out_dir: str
) -> None:
    lines = [
        "# Segmentation summary",
        "",
        "## Cross-zone exposures (effective access)",
        "",
        "| src zone | dst zone | source | target | open ports |",
        "|---|---|---|---|---|",
    ]
    rows = []
    for s, row in matrix.items():
        for d, c in row.items():
            if inv[s].zone != inv[d].zone and c.verdict == OPEN:
                rows.append(
                    (
                        inv[s].zone,
                        inv[d].zone,
                        inv[s].short,
                        inv[d].short,
                        ports_text(c.open_ports),
                    )
                )
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
        lines.append("**Ignored scans (source folder or file name is not an inventory IP):**")
        lines += [f"- {ip}" for ip in orphan]
    if not missing and not unknown and not orphan:
        lines.append("_Full coverage._")
    write_output(out_dir, "findings.md", "\n".join(lines))
