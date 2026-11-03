"""Read and rewrite the Mission's plain files for the app editors (docs/adr/0003).

The CLI never needs any of this: it reads the same files as they are. `zones.csv` only exists for
the app (a Zone without Interface yet, or a description) and the CLI ignores it.
"""

from __future__ import annotations

import csv
import io
import os
import tempfile
from collections import Counter

from segowl.inventory import BASE_COLUMNS, load_inventory

HEADER_FIRST_CELLS = ("ip", "adresse", "address")


def _rows(text: str):
    for row in csv.reader(io.StringIO(text.lstrip("﻿")), delimiter=";"):
        row = [c.strip() for c in row]
        while row and not row[-1]:  # spreadsheets pad rows with empty cells
            row.pop()
        if row and not row[0].startswith("#"):
            yield row


def _write(rows) -> str:
    out = io.StringIO()
    csv.writer(out, delimiter=";", lineterminator="\n").writerows(rows)
    return out.getvalue()


# ---------------------------------------------------------------- inventory
def read_inventory(text: str) -> tuple[list[str], list[dict[str, str]]]:
    """(free column names, rows as dicts), tolerant of a missing header and of invalid values."""
    columns, rows = list(BASE_COLUMNS), []
    for row in _rows(text):
        if row[0].lower() in HEADER_FIRST_CELLS:
            columns = [*BASE_COLUMNS, *row[len(BASE_COLUMNS) :]]
            continue
        while len(columns) < len(row):
            columns.append(f"column{len(columns) + 1}")
        rows.append({c: row[i] if i < len(row) else "" for i, c in enumerate(columns)})
    return columns[len(BASE_COLUMNS) :], rows


def inventory_text(free: list[str], rows: list[dict]) -> str:
    cols = [*BASE_COLUMNS, *free]
    body = [[str(r.get(c) or "").strip() for c in cols] for r in rows]
    return _write([cols, *(v for v in body if any(v))])


def check_inventory(text: str) -> str | None:
    """The CLI's own validation message for this inventory, or None when it loads (or is empty)."""
    if not read_inventory(text)[1]:
        return None
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as fh:
        fh.write(text)
    try:
        load_inventory(fh.name)
        return None
    except SystemExit as e:
        return str(e.code).replace(fh.name, "inventory.csv")
    finally:
        os.unlink(fh.name)


# ---------------------------------------------------------------- zones.csv
def read_zones(text: str) -> list[dict[str, str]]:
    return [{"name": r[0], "desc": r[1] if len(r) > 1 else ""} for r in _rows(text) if r[0].lower() != "zone"]


def zones_text(zones: list[dict], used: set[str]) -> str | None:
    """zones.csv content, or None when every Zone is in the inventory and has no description."""
    keep = [z for z in zones if z.get("name") and (z["name"] not in used or z.get("desc"))]
    return (
        _write([["zone", "description"], *([z["name"], z.get("desc", "")] for z in keep)]) if keep else None
    )


# ---------------------------------------------------------------- Flow Policy references
def policy_refs(text: str) -> Counter:
    """How many rule ends (src or dst) name each Zone / Machine."""
    refs: Counter = Counter()
    for row in _rows(text):
        if row[0].lower() != "src":
            refs.update(row[:2])
    return refs


def rename_in_policy(text: str, old: str, new: str) -> tuple[str, int]:
    """Rewrite src/dst equal to `old`; comment lines and every other field are kept as they are."""
    out, n = [], 0
    for line in text.splitlines(keepends=True):
        row = next(csv.reader([line], delimiter=";"), [])
        if not row or line.lstrip().startswith("#") or row[0].strip().lower() == "src":
            out.append(line)
            continue
        hits = [i for i in (0, 1) if i < len(row) and row[i].strip() == old]
        for i in hits:
            row[i] = new
        n += len(hits)
        out.append(_write([row]) if hits else line)
    return "".join(out), n


def rename_in_inventory(text: str, field: str, old: str, new: str) -> tuple[str, int]:
    free, rows = read_inventory(text)
    n = 0
    for r in rows:
        if r.get(field) == old:
            r[field], n = new, n + 1
    return inventory_text(free, rows), n


def rename_in_zones(text: str, old: str, new: str) -> str:
    zones = read_zones(text)
    for z in zones:
        if z["name"] == old:
            z["name"] = new
    return _write([["zone", "description"], *([z["name"], z["desc"]] for z in zones)])
