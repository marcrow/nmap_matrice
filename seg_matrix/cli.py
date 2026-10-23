"""Command line entry point."""

from __future__ import annotations

import argparse
import os
import sys

from seg_matrix.analysis import analyze
from seg_matrix.inventory import load_inventory
from seg_matrix.nmap import SCAN_EXT_PRIORITY, discover_scans, parse_scan
from seg_matrix.port_groups import load_port_groups
from seg_matrix.render.common import write_output
from seg_matrix.render.html import write_html
from seg_matrix.render.markdown import (
    write_exposure_md,
    write_findings_md,
    write_host_matrix_md,
    write_zone_matrix_md,
)
from seg_matrix.render.mermaid import mermaid_hosts, mermaid_source, mermaid_zone


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Segmentation matrix + Mermaid + HTML report.",
        epilog="Mission folder: inventory.csv, scans/<source_ip>/*.xml, report/ (generated).",
    )
    ap.add_argument("mission", nargs="?", help="Mission folder (sets the defaults of -i, -s and -o)")
    ap.add_argument("-i", "--inventory", help="Inventory CSV (ip;zone;type;name) [mission/inventory.csv]")
    ap.add_argument(
        "-s", "--scans", help="nmap outputs: <dir>/<source_ip>/* or <dir>/<source_ip>.<ext> [mission/scans]"
    )
    ap.add_argument(
        "--port-groups",
        help="Port Groups CSV (group;ports) overriding the defaults [mission/port_groups.csv]",
    )
    ap.add_argument("-o", "--out", help="Output directory [mission/report, else ./seg_report]")
    ap.add_argument(
        "--pn", action="store_true", help="Force -Pn mode (host-up ignored, verdict from ports only)"
    )
    ap.add_argument("--host-graph", action="store_true", help="Also generate the global host-level Mermaid")
    args = ap.parse_args()
    if args.mission:
        args.inventory = args.inventory or os.path.join(args.mission, "inventory.csv")
        args.scans = args.scans or os.path.join(args.mission, "scans")
        args.out = args.out or os.path.join(args.mission, "report")
        args.port_groups = args.port_groups or os.path.join(args.mission, "port_groups.csv")
    elif not (args.inventory and args.scans):
        ap.error("give a mission folder, or both -i and -s")
    args.out = args.out or "./seg_report"
    return args


def main() -> None:
    args = _parse_args()
    inv = load_inventory(args.inventory)
    if not os.path.isdir(args.scans):
        sys.exit(f"[!] Scan directory not found: {args.scans}")
    files = discover_scans(args.scans)
    orphan = sorted(set(files) - set(inv))  # source folder / file name that is not an inventory IP
    scans = {src: [parse_scan(p, src) for p in paths] for src, paths in files.items() if src in inv}
    if not scans:
        sys.exit(f"[!] No scan of an inventory source found in {args.scans} ({', '.join(SCAN_EXT_PRIORITY)})")

    os.makedirs(os.path.join(args.out, "mermaid"), exist_ok=True)
    if args.port_groups and not args.mission and not os.path.isfile(args.port_groups):
        sys.exit(f"[!] Port Groups file not found: {args.port_groups}")
    a = analyze(inv, scans, orphan, force_pn=args.pn, port_groups=load_port_groups(args.port_groups))
    matrix, missing, unknown, agg, exp = a.matrix, a.missing, a.unknown, a.agg, a.exp

    write_host_matrix_md(matrix, inv, args.out)
    write_zone_matrix_md(agg, inv, args.out)
    write_exposure_md(exp, inv, args.out)
    write_findings_md(matrix, inv, missing, unknown, orphan, args.out)
    write_output(args.out, "segmentation.mmd", mermaid_zone(agg, inv, a.highlight))
    if args.host_graph:
        write_output(args.out, "segmentation_hosts.mmd", mermaid_hosts(matrix, inv, a.highlight))
    for s in matrix:
        write_output(
            os.path.join(args.out, "mermaid"), f"{s}.mmd", mermaid_source(s, matrix[s], inv, a.highlight)
        )
    html_path = write_html(a, args.out)

    n_scans = sum(len(v) for v in scans.values())
    print(
        f"[+] Inventory: {len(inv)} targets | Scans: {n_scans} -> {len(matrix)} source(s) "
        f"(-Pn detected/forced on {a.pn_count} scan(s))"
    )
    if orphan:
        print(f"[!] {len(orphan)} ignored scan(s), not an inventory source IP: {', '.join(orphan)}")
    if missing:
        print(f"[!] {len(missing)} source(s) without scan: {', '.join(missing)}")
    if unknown:
        print(f"[!] {len(unknown)} host(s) outside inventory: {', '.join(unknown)}")
    print(f"[+] HTML report: {html_path}")
    print(f"[+] md/csv/mmd outputs in: {args.out}")
