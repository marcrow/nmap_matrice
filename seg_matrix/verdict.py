"""Verdicts of a Source -> Interface pair, derived from the port states nmap reports."""

from __future__ import annotations

from dataclasses import dataclass, field

OPEN, REACH, ALIVE, BLOCK, NODATA = 3, 2, 1, 0, -1
VERDICT_NAME = {OPEN: "OPEN", REACH: "REACHABLE", ALIVE: "ALIVE", BLOCK: "BLOCKED", NODATA: "UNSEEN"}
SYM = {OPEN: "OPEN", REACH: "o", ALIVE: "~", BLOCK: "x", NODATA: "."}
VCLASS = {OPEN: "v-open", REACH: "v-reach", ALIVE: "v-alive", BLOCK: "v-block", NODATA: "v-none"}


@dataclass
class Cell:
    verdict: int = NODATA
    open_ports: list[tuple[int, str]] = field(default_factory=list)


def classify(rec: dict | None, pn: bool) -> Cell:
    if rec is None:
        return Cell()
    # open|filtered = no reply (UDP, -sF/-sN/-sX): proves nothing got through, counts as filtered
    open_ports = sorted({(pid, proto) for (pid, proto, s) in rec["ports"] if s == "open"})
    closed = sum(1 for (_, _, s) in rec["ports"] if s == "closed")
    filtered = sum(1 for (_, _, s) in rec["ports"] if s in ("filtered", "open|filtered"))
    for s, c in rec["ignored"]:
        if s == "closed":
            closed += c
        elif s in ("filtered", "open|filtered"):
            filtered += c
    up = rec.get("state") == "up"
    if open_ports:
        v = OPEN
    elif closed > 0:
        v = REACH
    elif filtered > 0:
        v = BLOCK
    elif not pn:
        v = ALIVE if up else BLOCK  # answers at L3/L2 (ping/ARP) with no port getting through
    else:
        v = NODATA  # -Pn: 'host up' carries no information, no usable port data
    return Cell(v, open_ports)


def cell_text(c: Cell) -> str:
    if c.verdict == OPEN:
        return ",".join(str(p) for p, _ in c.open_ports) or "OPEN"
    return SYM[c.verdict]
