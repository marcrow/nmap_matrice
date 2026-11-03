"""Port ranges as nmap writes them ("1-21,23,25-1000"), kept as merged (lo, hi) tuples."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

Ranges = list[tuple[int, int]]


def merge_ranges(ranges: list[tuple[int, int]]) -> Ranges:
    out: Ranges = []
    for lo, hi in sorted(ranges):
        if out and lo <= out[-1][1] + 1:
            out[-1] = (out[-1][0], max(out[-1][1], hi))
        else:
            out.append((lo, hi))
    return out


def parse_ranges(spec: str) -> Ranges:
    ranges = []
    for part in spec.split(","):
        part = part.strip().split(":")[-1]  # tolerate "T:22" style prefixes
        if part:
            lo, _, hi = part.partition("-")
            ranges.append((int(lo), int(hi or lo)))
    return merge_ranges(ranges)


def in_ranges(port: int, ranges: Ranges) -> bool:
    return any(lo <= port <= hi for lo, hi in ranges)


def overlaps(a: Ranges, b: Ranges) -> bool:
    return any(lo1 <= hi2 and lo2 <= hi1 for lo1, hi1 in a for lo2, hi2 in b)


def count_ports(ranges: Ranges) -> int:
    return sum(hi - lo + 1 for lo, hi in ranges)


def format_ranges(ranges: Ranges) -> str:
    return ",".join(str(lo) if lo == hi else f"{lo}-{hi}" for lo, hi in ranges)


Port = tuple[int, str]  # (port, proto)


def port_label(port: Port) -> str:
    """TCP is implied: "22"; any other protocol is prefixed: "udp:161"."""
    number, proto = port
    return str(number) if proto == "tcp" else f"{proto}:{number}"


def ports_text(ports: Iterable[Port], cap: int | None = None) -> str:
    labels = [port_label(p) for p in sorted(ports)]
    if cap is not None and len(labels) > cap:
        return ",".join(labels[:cap]) + ",..."
    return ",".join(labels)


PortSet = dict[str, Ranges]  # proto -> ranges
PROTOS = ("tcp", "udp", "sctp")


def parse_port_set(spec: str) -> PortSet:
    """'22,443,8000-8100,udp:161' -> {'tcp': [...], 'udp': [...]}; TCP is implied."""
    raw: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for token in spec.split(","):
        token = token.strip()
        if not token:
            continue
        proto, _, ports = token.rpartition(":")
        proto = proto.lower() or "tcp"
        if proto not in PROTOS:
            raise ValueError(f"unknown protocol in {token!r} (expected {', '.join(PROTOS)})")
        try:
            raw[proto] += parse_ranges(ports)
        except ValueError:
            raise ValueError(f"invalid port in {token!r}") from None
    return {proto: merge_ranges(r) for proto, r in raw.items()}


def in_port_set(port: Port, port_set: PortSet) -> bool:
    return in_ranges(port[0], port_set.get(port[1], []))
