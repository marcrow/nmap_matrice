"""Flow Policy: the optional, auditor-supplied statement of allowed / denied flows (ADR-0002).

flow_policy.csv: src;dst;ports;action;comment
  src, dst : a Zone, a Machine or *
  ports    : *, 22,443, 8000-8100, udp:161, @<Port Group>, combinable (22,@web)
  action   : allow | deny (empty = no decision yet, the row is skipped)

The most specific rule wins: src (Machine > Zone > *), then dst, then ports (listed > *);
at equal specificity deny wins. A flow no rule covers is Undeclared, never a Finding.
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from dataclasses import dataclass

from seg_matrix.inventory import Host, Inventory
from seg_matrix.port_groups import PortGroups
from seg_matrix.ports import Port, PortSet, in_port_set, merge_ranges, parse_port_set

ALLOW, DENY, UNDECLARED = "allow", "deny", "undeclared"
SEVERITY = {DENY: 2, UNDECLARED: 1, ALLOW: 0}  # to colour an edge carrying several flows
ANY, ZONE, MACHINE = 0, 1, 2  # specificity of a src / dst


@dataclass
class Rule:
    line: int
    src: str
    dst: str
    ports_spec: str
    action: str
    comment: str
    src_kind: int
    dst_kind: int
    ports: PortSet | None  # None = any port

    @property
    def specificity(self) -> tuple[int, int, int]:
        return self.src_kind, self.dst_kind, 0 if self.ports is None else 1

    def _side(self, name: str, kind: int, h: Host) -> bool:
        return kind == ANY or (kind == ZONE and h.zone == name) or (kind == MACHINE and h.machine == name)

    def matches(self, src: Host, dst: Host, port: Port) -> bool:
        return (
            self._side(self.src, self.src_kind, src)
            and self._side(self.dst, self.dst_kind, dst)
            and (self.ports is None or in_port_set(port, self.ports))
        )

    def __str__(self) -> str:
        return f"#{self.line} {self.src} -> {self.dst} {self.ports_spec} {self.action}"


def _kind(name: str, inv: Inventory, where: str) -> int:
    if name == "*":
        return ANY
    is_zone = any(h.zone == name for h in inv.values())
    is_machine = any(h.machine == name for h in inv.values())
    if is_zone and is_machine:
        sys.exit(f"[!] {where}: {name!r} is both a Zone and a Machine of the inventory")
    if not (is_zone or is_machine):
        sys.exit(f"[!] {where}: {name!r} is neither a Zone nor a Machine of the inventory")
    return MACHINE if is_machine else ZONE


def _ports(spec: str, groups: PortGroups, where: str) -> PortSet | None:
    if spec in ("", "*"):
        return None
    raw: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for token in spec.split(","):
        token = token.strip()
        if token.startswith("@"):
            if token[1:] not in groups:
                sys.exit(f"[!] {where}: unknown Port Group {token!r} (known: {', '.join(groups)})")
            part = groups[token[1:]]
        else:
            try:
                part = parse_port_set(token)
            except ValueError as e:
                sys.exit(f"[!] {where}: {e}")
        for proto, ranges in part.items():
            raw[proto] += ranges
    return {proto: merge_ranges(r) for proto, r in raw.items()}


def load_policy(path: str, inv: Inventory, groups: PortGroups) -> list[Rule]:
    rules, skipped = [], 0
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for line_no, row in enumerate(csv.reader(fh, delimiter=";"), 1):
            row = [c.strip() for c in row] + [""] * 5
            if not row[0] or row[0].startswith("#") or row[0].lower() == "src":
                continue
            where = f"{path}:{line_no}"
            src, dst, ports, action, comment = row[:5]
            if not action:
                skipped += 1
                continue
            if action.lower() not in (ALLOW, DENY):
                sys.exit(f"[!] {where}: action must be allow or deny, not {action!r}")
            rules.append(
                Rule(
                    line_no,
                    src,
                    dst,
                    ports or "*",
                    action.lower(),
                    comment,
                    _kind(src, inv, where),
                    _kind(dst, inv, where),
                    _ports(ports, groups, where),
                )  # fmt: skip
            )
    if skipped:
        print(f"[!] {path}: {skipped} row(s) without action skipped (no decision yet)", file=sys.stderr)
    return rules


def decide(rules: list[Rule], src: Host, dst: Host, port: Port) -> Rule | None:
    """The rule that decides this flow, None when it is Undeclared."""
    hits = [r for r in rules if r.matches(src, dst, port)]
    if not hits:
        return None
    best = max(r.specificity for r in hits)
    top = [r for r in hits if r.specificity == best]
    return next((r for r in top if r.action == DENY), top[0])


def worst(statuses: list[str]) -> str | None:
    return max(statuses, key=SEVERITY.__getitem__, default=None)
