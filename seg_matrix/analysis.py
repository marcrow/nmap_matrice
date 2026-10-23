"""Host matrix, zone aggregation and target exposure built from the parsed scans."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import cached_property

from seg_matrix.inventory import Inventory, ordered_ips
from seg_matrix.nmap import HostRecord, Scan
from seg_matrix.port_groups import HIGHLIGHT, PortGroups
from seg_matrix.ports import Port, in_port_set, merge_ranges, overlaps
from seg_matrix.verdict import ALIVE, BLOCK, OPEN, REACH, Cell, classify

Row = dict[str, Cell]  # target ip -> verdict cell
Matrix = dict[str, Row]  # source ip -> row
Exposure = dict[
    str, tuple[list[tuple[str, list[Port]]], list[str]]
]  # target -> (OPEN sources, REACH sources)
Observation = tuple[Scan, HostRecord]  # what one Scan saw of one target


def _conflicts(observations: list[Observation]) -> dict[tuple[int, str], dict[str, str]]:
    """Ports on which the Scans disagree, with each Scan's state.

    ponytail: only ports some Scan lists explicitly; a grouped-range change (closed -> filtered on
    ports nobody lists) is not flagged, add a range comparison if that case matters.
    """
    listed = {(p, proto) for _, rec in observations for p, proto, _ in rec.ports}
    out = {}
    for port, proto in sorted(listed):
        states = {sc.name: st for sc, rec in observations if (st := rec.state_of(port, proto)) is not None}
        if len(set(states.values())) > 1:
            out[(port, proto)] = states
    return out


def source_view_cell(observations: list[Observation], force_pn: bool = False) -> Cell:
    """Combines a Source's Scans of one target: the most permissive state wins (ADR-0001)."""
    if not observations:
        return Cell()
    cells = [classify(rec, force_pn or sc.pn) for sc, rec in observations]
    tested: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for sc, _ in observations:
        for proto, ranges in (sc.coverage or {}).items():
            tested[proto] += ranges
    return Cell(
        verdict=max(c.verdict for c in cells),
        open_ports=sorted({p for c in cells for p in c.open_ports}),
        scans=[sc.name for sc, _ in observations],
        conflicts=_conflicts(observations),
        tested={proto: merge_ranges(r) for proto, r in tested.items()},
        coverage_known=all(sc.coverage is not None for sc, _ in observations),
    )


def build_matrix(
    inv: Inventory, scans: dict[str, list[Scan]], force_pn: bool = False
) -> tuple[Matrix, list[str], list[str], int]:
    """Source Views of every scanned Source.

    Returns (matrix, sources without scan, reachable IPs outside the inventory, -Pn Scan count).
    """
    matrix: Matrix = {}
    unknown: set[str] = set()
    for src in inv:
        if src not in scans:
            continue
        src_scans = sorted(scans[src], key=lambda sc: (sc.start_ts, sc.name))
        self_ips = {ip for ip, h in inv.items() if h.machine == inv[src].machine}
        for sc in src_scans:
            for dip, rec in sc.hosts.items():
                if (
                    dip not in self_ips
                    and dip not in inv
                    and classify(rec, force_pn or sc.pn).verdict >= ALIVE
                ):
                    unknown.add(dip)
        matrix[src] = {
            dst: source_view_cell([(sc, sc.hosts[dst]) for sc in src_scans if dst in sc.hosts], force_pn)
            for dst in inv
            if dst not in self_ips
        }
    missing = sorted(ip for ip in inv if ip not in scans)
    pn_count = sum(1 for src in matrix for sc in scans[src] if force_pn or sc.pn)
    return matrix, missing, sorted(unknown), pn_count


@dataclass
class ZoneAgg:
    verdict: int = BLOCK
    open_ports: set[Port] = field(default_factory=set)
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
                a.open_ports.update(c.open_ports)
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
                opens.append((s, c.open_ports))
            elif c.verdict == REACH:
                reach.append(s)
        exp[d] = (opens, reach)
    return exp


def restrict(matrix: Matrix, keep: Callable[[Port], bool]) -> Matrix:
    """The OPEN flows on the kept ports only (e.g. a Port Group view); everything else becomes unseen."""
    out: Matrix = {}
    for s, row in matrix.items():
        out[s] = {}
        for d, c in row.items():
            ports = [p for p in c.open_ports if keep(p)]
            out[s][d] = Cell(OPEN, ports, c.scans) if ports else Cell(scans=c.scans)
    return out


# machine -> [(source ip, reached interface ip, open ports)]
Pivots = dict[str, list[tuple[str, str, list[Port]]]]


def pivot_machines(matrix: Matrix, inv: Inventory) -> Pivots:
    """Machines spanning several Zones and reached OPEN: one-hop paths from the Source's Zone to their others.

    ponytail: one hop only; chain pivots (A reaches M1 which reaches M2) if an engagement needs it.
    """
    zones_of: dict[str, set[str]] = defaultdict(set)
    for h in inv.values():
        zones_of[h.machine].add(h.zone)
    out: Pivots = defaultdict(list)
    for s, row in matrix.items():
        for d, c in row.items():
            if c.verdict == OPEN and len(zones_of[inv[d].machine]) > 1:
                out[inv[d].machine].append((s, d, c.open_ports))
    return dict(out)


def _comparable(a: Cell, b: Cell) -> bool:
    """Both directions tested some common ports (or a non-XML Scan leaves it unknown)."""
    if not (a.coverage_known and b.coverage_known):
        return True
    return any(overlaps(r, b.tested.get(proto, [])) for proto, r in a.tested.items())


def asymmetries(matrix: Matrix) -> list[tuple[str, str]]:
    """(a, b) where a -> b passes (OPEN/REACHABLE) but b -> a is BLOCKED, both being Sources."""
    out = []
    for a, row in matrix.items():
        for b, ab in row.items():
            ba = matrix.get(b, {}).get(a)
            if ba and ab.verdict >= REACH and ba.verdict == BLOCK and _comparable(ab, ba):
                out.append((a, b))
    return out


@dataclass
class Analysis:
    """Everything the renderers need, computed once from the inventory and the Scans."""

    inv: Inventory
    scans: dict[str, list[Scan]]  # source ip -> its Scans, oldest first
    orphan: list[str]  # ignored scans: source folder / file name that is not an inventory IP
    matrix: Matrix
    missing: list[str]  # inventory IPs without any Scan
    unknown: list[str]  # reachable IPs outside the inventory
    pn_count: int
    agg: ZoneMatrix
    exp: Exposure
    port_groups: PortGroups = field(default_factory=dict)

    @property
    def sources(self) -> list[str]:
        return [ip for ip in ordered_ips(self.inv) if ip in self.matrix]

    def in_group(self, group: str) -> Callable[[Port], bool]:
        port_set = self.port_groups.get(group, {})
        return lambda port: in_port_set(port, port_set)

    @cached_property
    def group_matrices(self) -> dict[str, Matrix]:
        """One restricted matrix per Port Group, for the report's group filter."""
        return {g: restrict(self.matrix, self.in_group(g)) for g in self.port_groups}

    @cached_property
    def pivots(self) -> Pivots:
        return pivot_machines(self.matrix, self.inv)

    @cached_property
    def asymmetries(self) -> list[tuple[str, str]]:
        return asymmetries(self.matrix)

    @property
    def highlight(self) -> Callable[[Port], bool]:
        """Ports to highlight in every view (the admin Port Group)."""
        return self.in_group(HIGHLIGHT)


def analyze(
    inv: Inventory,
    scans: dict[str, list[Scan]],
    orphan: list[str],
    force_pn: bool = False,
    port_groups: PortGroups | None = None,
) -> Analysis:
    scans = {src: sorted(v, key=lambda sc: (sc.start_ts, sc.name)) for src, v in scans.items()}
    matrix, missing, unknown, pn_count = build_matrix(inv, scans, force_pn)
    agg, exp = aggregate_zones(matrix, inv), target_exposure(matrix, inv)
    return Analysis(inv, scans, orphan, matrix, missing, unknown, pn_count, agg, exp, port_groups or {})
