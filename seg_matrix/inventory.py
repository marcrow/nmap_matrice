"""Inventory: one CSV row per Interface; rows sharing a name form a Machine."""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass, field

BASE_COLUMNS = ("ip", "zone", "type", "name")


@dataclass
class Host:
    ip: str
    zone: str
    htype: str
    name: str
    extra: dict[str, str] = field(default_factory=dict)  # free columns (owner, criticality...), no logic

    @property
    def machine(self) -> str:
        return self.name or self.ip

    @property
    def short(self) -> str:
        return f"{self.name} · {self.ip}" if self.name else self.ip


Inventory = dict[str, Host]  # ip -> Interface


def load_inventory(path: str) -> Inventory:
    hosts: Inventory = {}
    header: list[str] | None = None
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as fh:
        for line_no, row in enumerate(csv.reader(fh, delimiter=";"), 1):
            row = [c.strip() for c in row]
            while row and not row[-1]:  # spreadsheets pad rows with empty cells
                row.pop()
            if not row or not row[0]:
                continue
            if row[0].lower() in ("ip", "adresse", "address"):
                header = row
                continue
            if len(row) > len(BASE_COLUMNS) and (header is None or len(header) < len(row)):
                sys.exit(
                    f"[!] {path}:{line_no}: {len(row)} columns but no header naming them — "
                    f"add a first line such as {';'.join(BASE_COLUMNS)};owner;criticality"
                )
            ip = row[0]
            if ip in hosts:
                sys.exit(
                    f"[!] Duplicate IP in {path}: {ip} ({hosts[ip].zone}/{hosts[ip].name} "
                    f"and {';'.join(row[1:])}) — an interface belongs to exactly one zone"
                )
            hosts[ip] = Host(
                ip=ip,
                zone=row[1] if len(row) > 1 else "?",
                htype=row[2] if len(row) > 2 else "?",
                name=row[3] if len(row) > 3 else "",
                extra={header[i]: v for i, v in enumerate(row) if i >= len(BASE_COLUMNS) and v}
                if header
                else {},
            )
    if not hosts:
        sys.exit(f"[!] No host loaded from {path} (expected: ip;zone;type;name)")
    return hosts


def extra_columns(inv: Inventory) -> list[str]:
    """Free column names, in first-appearance order."""
    return list(dict.fromkeys(k for h in inv.values() for k in h.extra))


def ordered_ips(inv: Inventory) -> list[str]:
    """Inventory IPs, interfaces of the same machine side by side (first-appearance order)."""
    rank = {m: i for i, m in enumerate(dict.fromkeys(h.machine for h in inv.values()))}
    return sorted(inv, key=lambda ip: rank[inv[ip].machine])
