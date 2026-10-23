"""Command line entry point."""

from __future__ import annotations

import argparse
import os
import sys

from seg_matrix.analysis import aggregate_zones, build_matrix, target_exposure
from seg_matrix.inventory import load_inventory
from seg_matrix.nmap import SCAN_EXT_PRIORITY, discover_scans
from seg_matrix.render.common import write_output
from seg_matrix.render.html import write_html
from seg_matrix.render.markdown import (
    write_exposure_md,
    write_findings_md,
    write_host_matrix_md,
    write_zone_matrix_md,
)
from seg_matrix.render.mermaid import mermaid_hosts, mermaid_source, mermaid_zone


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Segmentation matrix + Mermaid + HTML report.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("-i", "--inventory", required=True, help="Inventory CSV (ip;zone;type;name)")
    ap.add_argument("-s", "--scans", required=True, help="Directory of nmap outputs (<ip>.xml/.gnmap/.nmap)")
    ap.add_argument("-o", "--out", default="./seg_report", help="Output directory")
    ap.add_argument(
        "--pn", action="store_true", help="Force -Pn mode (host-up ignored, verdict from ports only)"
    )
    ap.add_argument("--host-graph", action="store_true", help="Also generate the global host-level Mermaid")
    args = ap.parse_args()

    os.makedirs(os.path.join(args.out, "mermaid"), exist_ok=True)
    inv = load_inventory(args.inventory)
    scans = discover_scans(args.scans)
    if not scans:
        sys.exit(f"[!] No scan found in {args.scans} ({', '.join(SCAN_EXT_PRIORITY)})")

    matrix, missing, unknown, pn_count = build_matrix(inv, scans, force_pn=args.pn)
    orphan = sorted(set(scans) - set(inv))  # files whose name is not a source IP of the inventory
    agg = aggregate_zones(matrix, inv)
    exp = target_exposure(matrix, inv)

    write_host_matrix_md(matrix, inv, args.out)
    write_zone_matrix_md(agg, inv, args.out)
    write_exposure_md(exp, inv, args.out)
    write_findings_md(matrix, inv, missing, unknown, orphan, args.out)
    write_output(args.out, "segmentation.mmd", mermaid_zone(agg, inv))
    if args.host_graph:
        write_output(args.out, "segmentation_hosts.mmd", mermaid_hosts(matrix, inv))
    for s in matrix:
        write_output(os.path.join(args.out, "mermaid"), f"{s}.mmd", mermaid_source(s, matrix[s], inv))
    html_path = write_html(matrix, inv, agg, exp, missing, unknown, orphan, args.out)

    print(
        f"[+] Inventory: {len(inv)} targets | Scans: {len(scans)} file(s) -> {len(matrix)} source(s) "
        f"(-Pn detected/forced on {pn_count})"
    )
    if orphan:
        print(
            f"[!] {len(orphan)} ignored scan(s), file name is not a source IP of the inventory: "
            f"{', '.join(orphan)}"
        )
    if missing:
        print(f"[!] {len(missing)} source(s) without scan: {', '.join(missing)}")
    if unknown:
        print(f"[!] {len(unknown)} host(s) outside inventory: {', '.join(unknown)}")
    print(f"[+] HTML report: {html_path}")
    print(f"[+] md/csv/mmd outputs in: {args.out}")
