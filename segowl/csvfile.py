"""The Mission's CSV files: `;`-separated, UTF-8 (BOM tolerated), `#` lines are comments."""

from __future__ import annotations

import csv
import io
from collections.abc import Iterator
from pathlib import Path


def read(path: str | Path) -> str:
    """The file's text, '' when it does not exist."""
    p = Path(path)
    return p.read_text(encoding="utf-8-sig", errors="replace") if p.is_file() else ""


def rows(text: str, blank_first: bool = False) -> Iterator[tuple[int, list[str]]]:
    """(line number, stripped cells) of each row; comments, blank lines and the trailing empty cells
    spreadsheets pad rows with are dropped, and so are rows with an empty first cell unless `blank_first`."""
    for n, row in enumerate(csv.reader(io.StringIO(text.lstrip("﻿")), delimiter=";"), 1):
        row = [c.strip() for c in row]
        while row and not row[-1]:
            row.pop()
        if row and (row[0] or blank_first) and not row[0].startswith("#"):
            yield n, row
