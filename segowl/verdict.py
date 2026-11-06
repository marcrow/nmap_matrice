"""Verdicts of a Source -> Interface pair, derived from the port states nmap reports."""

from __future__ import annotations

from dataclasses import dataclass, field

from segowl.nmap import HostRecord
from segowl.ports import Port, Ranges, in_ranges, ports_text

OPEN, REACH, ALIVE, BLOCK, NODATA = 3, 2, 1, 0, -1
VERDICT_NAME = {OPEN: "OPEN", REACH: "REACHABLE", ALIVE: "ALIVE", BLOCK: "BLOCKED", NODATA: "UNSEEN"}
SYM = {OPEN: "OPEN", REACH: "o", ALIVE: "~", BLOCK: "x", NODATA: "."}
# Port states from most to least permissive: the Source View keeps the highest (ADR-0001)
STATE_RANK = {
    "open": 3,
    "closed": 2,
    "unfiltered": 2,
    "filtered": 1,
    "open|filtered": 1,
    "closed|filtered": 1,
}
VCLASS = {OPEN: "v-open", REACH: "v-reach", ALIVE: "v-alive", BLOCK: "v-block", NODATA: "v-none"}


@dataclass
class Cell:
    """Verdict of a Source -> Interface pair, with the Scans behind it."""

    verdict: int = NODATA
    open_ports: list[Port] = field(default_factory=list)
    scans: list[str] = field(default_factory=list)  # Scans in which the target appears
    conflicts: dict[tuple[int, str], dict[str, str]] = field(default_factory=dict)  # port -> {scan: state}
    tested: dict[str, Ranges] = field(default_factory=dict)  # Coverage: proto -> ports tested
    coverage_known: bool = True  # False when a Scan behind the cell is not XML

    def is_tested(self, port: int, proto: str = "tcp") -> bool | None:
        """True/False when Coverage says so, None when it cannot tell (non-XML Scan, port not in XML ones)."""
        if in_ranges(port, self.tested.get(proto, [])):
            return True
        return None if not self.coverage_known else False


def classify(rec: HostRecord | None, pn: bool) -> Cell:
    if rec is None:
        return Cell()
    # open|filtered = no reply (UDP, -sF/-sN/-sX): proves nothing got through, counts as filtered
    open_ports = sorted({(pid, proto) for (pid, proto, s) in rec.ports if s == "open"})
    # closed (RST) and unfiltered (-sA: the ACK got an RST) both prove the L4 flow crosses
    passed = any(s in ("closed", "unfiltered") for (_, _, s) in rec.ports) or any(
        s in ("closed", "unfiltered") and c for s, c in rec.ignored
    )
    filtered = any(s in ("filtered", "open|filtered") for (_, _, s) in rec.ports) or any(
        s in ("filtered", "open|filtered") and c for s, c in rec.ignored
    )
    if open_ports:
        v = OPEN
    elif passed:
        v = REACH
    elif not pn:
        # answered host discovery (ping/ARP) but no port got through: a lead to scan deeper
        v = ALIVE if rec.state == "up" else BLOCK
    else:
        v = BLOCK if filtered else NODATA  # -Pn: 'host up' carries no information
    return Cell(v, open_ports)


def cell_text(c: Cell) -> str:
    if c.verdict == OPEN:
        return ports_text(c.open_ports) or "OPEN"
    return SYM[c.verdict]
