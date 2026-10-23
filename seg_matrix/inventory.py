"""Inventory: one CSV row per Interface; rows sharing a name form a Machine."""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass


@dataclass
class Host:
    ip: str
    zone: str
    htype: str
    name: str

    @property
    def machine(self) -> str:
        return self.name or self.ip

    @property
    def short(self) -> str:
        return f"{self.name} · {self.ip}" if self.name else self.ip


Inventory = dict[str, Host]  # ip -> Interface


def load_inventory(path: str) -> Inventory:
    hosts: Inventory = {}
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as fh:
        for row in csv.reader(fh, delimiter=";"):
            row = [c.strip() for c in row]
            if not row or not row[0]:
                continue
            if row[0].lower() in ("ip", "adresse", "address"):
                continue
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
            )
    if not hosts:
        sys.exit(f"[!] No host loaded from {path} (expected: ip;zone;type;name)")
    return hosts


def ordered_ips(inv: Inventory) -> list[str]:
    """Inventory IPs, interfaces of the same machine side by side (first-appearance order)."""
    rank = {m: i for i, m in enumerate(dict.fromkeys(h.machine for h in inv.values()))}
    return sorted(inv, key=lambda ip: rank[inv[ip].machine])
