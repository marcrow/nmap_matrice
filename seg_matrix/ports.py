"""Port ranges as nmap writes them ("1-21,23,25-1000"), kept as merged (lo, hi) tuples."""

from __future__ import annotations

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
