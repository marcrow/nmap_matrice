"""Command line entry point."""

from __future__ import annotations

import argparse
import os
import sys

from segowl.analysis import analyze
from segowl.inventory import load_inventory
from segowl.nmap import SCAN_EXT_PRIORITY, discover_excluded, discover_scans, parse_scan
from segowl.policy import load_policy
from segowl.port_groups import load_port_groups
from segowl.render.common import write_output
from segowl.render.exports import write_observed_flows, write_observed_zone_flows
from segowl.render.html import write_html
from segowl.render.markdown import (
    write_exposure_md,
    write_findings_md,
    write_host_matrix_md,
    write_zone_matrix_md,
)
from segowl.render.mermaid import mermaid_hosts, mermaid_source, mermaid_zone


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
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
    ap.add_argument(
        "--policy", help="Flow Policy CSV (src;dst;ports;action;comment) [mission/flow_policy.csv]"
    )
    ap.add_argument("-o", "--out", help="Output directory [mission/report, else ./seg_report]")
    ap.add_argument(
        "--pn", action="store_true", help="Force -Pn mode (host-up ignored, verdict from ports only)"
    )
    ap.add_argument("--host-graph", action="store_true", help="Also generate the global host-level Mermaid")
    args = ap.parse_args(argv)
    if not args.mission and not (args.inventory and args.scans):
        ap.error("give a mission folder, or both -i and -s")
    return mission_defaults(args)


def mission_defaults(args: argparse.Namespace) -> argparse.Namespace:
    """Fill the paths a mission folder implies, keeping the ones given explicitly."""
    if args.mission:
        args.inventory = args.inventory or os.path.join(args.mission, "inventory.csv")
        args.scans = args.scans or os.path.join(args.mission, "scans")
        args.out = args.out or os.path.join(args.mission, "report")
        mission_groups = os.path.join(args.mission, "port_groups.csv")
        args.port_groups = args.port_groups or (mission_groups if os.path.isfile(mission_groups) else None)
        mission_policy = os.path.join(args.mission, "flow_policy.csv")
        args.policy = args.policy or (mission_policy if os.path.isfile(mission_policy) else None)
    args.out = args.out or "./seg_report"
    return args


def main() -> None:
    if sys.argv[1:2] in (["serve"], ["user"]):  # app subcommands; a mission folder is never named so
        from segowl.app import main as app_main

        app_main(sys.argv[1:])
        return
    print("\n".join(run(_parse_args())))


def run(args: argparse.Namespace) -> list[str]:
    """Generate every output; return the summary lines. Fatal input errors raise SystemExit(message)."""
    inv = load_inventory(args.inventory)
    if not os.path.isdir(args.scans):
        sys.exit(f"[!] Scan directory not found: {args.scans}")
    files = discover_scans(args.scans)
    orphan = sorted(set(files) - set(inv))  # source folder / file name that is not an inventory IP
    scans = {src: [parse_scan(p, src) for p in paths] for src, paths in files.items() if src in inv}
    if not scans:
        sys.exit(f"[!] No scan of an inventory source found in {args.scans} ({', '.join(SCAN_EXT_PRIORITY)})")

    os.makedirs(os.path.join(args.out, "mermaid"), exist_ok=True)
    if args.port_groups and not os.path.isfile(args.port_groups):
        sys.exit(f"[!] Port Groups file not found: {args.port_groups}")
    if args.policy and not os.path.isfile(args.policy):
        sys.exit(f"[!] Flow Policy file not found: {args.policy}")
    groups = load_port_groups(args.port_groups)
    policy = load_policy(args.policy, inv, groups) if args.policy else None
    excluded = discover_excluded(args.scans)
    a = analyze(inv, scans, orphan, force_pn=args.pn, port_groups=groups, policy=policy, excluded=excluded)
    matrix, missing, unknown, agg, exp = a.matrix, a.missing, a.unknown, a.agg, a.exp

    write_host_matrix_md(matrix, inv, args.out)
    write_zone_matrix_md(agg, inv, args.out)
    write_exposure_md(exp, inv, args.out)
    if policy is not None:
        write_findings_md(a, args.out)
    pair_status = a.pair_status(matrix)
    write_output(
        args.out,
        "segmentation.mmd",
        mermaid_zone(agg, inv, a.highlight, a.zone_status(matrix), a.zone_denied),
    )
    if args.host_graph:
        write_output(
            args.out, "segmentation_hosts.mmd", mermaid_hosts(matrix, inv, a.highlight, pair_status, a.denied)
        )
    for s in matrix:
        mmd = mermaid_source(s, matrix[s], inv, a.highlight, pair_status, a.denied)
        write_output(os.path.join(args.out, "mermaid"), f"{s}.mmd", mmd)
    write_observed_flows(a, args.out)
    write_observed_zone_flows(a, args.out)
    html_path = write_html(a, args.out)

    n_scans = sum(len(v) for v in scans.values())
    lines = [
        f"[+] Inventory: {len(inv)} targets | Scans: {n_scans} -> {len(matrix)} source(s) "
        f"(-Pn detected/forced on {a.pn_count} scan(s))"
    ]
    if orphan:
        lines.append(f"[!] {len(orphan)} ignored scan(s), not an inventory source IP: {', '.join(orphan)}")
    if excluded:
        lines.append(f"[+] {sum(map(len, excluded.values()))} excluded scan(s) in sub-folders, not read")
    if missing:
        lines.append(f"[!] {len(missing)} source(s) without scan: {', '.join(missing)}")
    if unknown:
        lines.append(f"[!] {len(unknown)} host(s) outside inventory: {', '.join(unknown)}")
    if policy is not None:
        lines.append(
            f"[+] Flow Policy: {len(policy)} rule(s) -> {len(a.findings)} Finding(s), "
            f"{len(a.undeclared)} undeclared"
        )
    lines.append(f"[+] HTML report: {html_path}")
    lines.append(f"[+] md/csv/mmd outputs in: {args.out}")
    return lines
