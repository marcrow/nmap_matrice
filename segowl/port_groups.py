"""Port Groups: named sets of ports (admin, db, web...) used to filter and highlight flows."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from segowl import csvfile
from segowl.ports import PortSet, parse_port_set

DEFAULTS = Path(__file__).resolve().parent / "defaults" / "port_groups.csv"
HIGHLIGHT = "admin"  # flows on this group's ports are highlighted in every view

PortGroups = dict[str, PortSet]


def _read(path: str) -> PortGroups:
    groups: PortGroups = {}
    for line_no, row in csvfile.rows(csvfile.read(path)):
        if row[0].lower() == "group":
            continue
        if len(row) < 2 or not row[1]:
            sys.exit(f"[!] {path}:{line_no}: expected group;ports")
        try:
            groups[row[0]] = parse_port_set(row[1])
        except ValueError as e:
            sys.exit(f"[!] {path}:{line_no}: {e}")
    return groups


def load_port_groups(mission_file: str | None = None) -> PortGroups:
    """Shipped defaults, overridden group by group by the mission file when it exists."""
    groups = _read(str(DEFAULTS))
    if mission_file and os.path.isfile(mission_file):
        groups.update(_read(mission_file))
    return groups
