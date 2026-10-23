"""Host matrix, zone aggregation and target exposure built from the parsed scans."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from seg_matrix.inventory import Inventory
from seg_matrix.nmap import detect_pn, parse_scan
from seg_matrix.verdict import ALIVE, BLOCK, OPEN, REACH, Cell, classify

Row = dict[str, Cell]  # target ip -> verdict cell
Matrix = dict[str, Row]  # source ip -> row
Exposure = dict[str, tuple[list[tuple[str, list[int]]], list[str]]]  # target -> (OPEN sources, REACH sources)


def build_matrix(
    inv: Inventory, scans: dict[str, str], force_pn: bool = False
) -> tuple[Matrix, list[str], list[str], int]:
    """Returns (matrix, sources without scan, reachable IPs outside the inventory, -Pn source count)."""
    parsed = {ip: parse_scan(path) for ip, path in scans.items()}
    pn_of = {ip: (True if force_pn else detect_pn(path)) for ip, path in scans.items()}
    matrix: Matrix = {}
    unknown: set[str] = set()
    for src in inv:
        if src not in parsed:
            continue
        pn = pn_of[src]
        self_ips = {ip for ip, h in inv.items() if h.machine == inv[src].machine}
        seen = parsed[src]
        for dip, rec in seen.items():
            if dip in self_ips or dip in inv:
                continue
            if classify(rec, pn).verdict >= ALIVE:
                unknown.add(dip)
        row = {dst: classify(seen.get(dst), pn) for dst in inv if dst not in self_ips}
        matrix[src] = row
    missing = sorted(ip for ip in inv if ip not in scans)
    pn_count = sum(1 for ip in matrix if pn_of.get(ip))
    return matrix, missing, sorted(unknown), pn_count


@dataclass
class ZoneAgg:
    verdict: int = BLOCK
    open_ports: set[int] = field(default_factory=set)
    reach_pairs: int = 0
    total_pairs: int = 0


ZoneMatrix = dict[tuple[str, str], ZoneAgg]


def aggregate_zones(matrix: Matrix, inv: Inventory) -> ZoneMatrix:
    agg: ZoneMatrix = defaultdict(ZoneAgg)
    for s, row in matrix.items():
        zs = inv[s].zone
        for d, c in row.items():
            a = agg[(zs, inv[d].zone)]
            a.total_pairs += 1
            if c.verdict >= REACH:
                a.reach_pairs += 1
                a.verdict = max(a.verdict, c.verdict)
                a.open_ports.update(p for p, _ in c.open_ports)
    return agg


def target_exposure(matrix: Matrix, inv: Inventory) -> Exposure:
    """For each target: OPEN sources (with ports) and REACH sources."""
    exp: Exposure = {}
    for d in inv:
        opens, reach = [], []
        for s, row in matrix.items():
            c = row.get(d)
            if not c:
                continue
            if c.verdict == OPEN:
                opens.append((s, [p for p, _ in c.open_ports]))
            elif c.verdict == REACH:
                reach.append(s)
        exp[d] = (opens, reach)
    return exp
