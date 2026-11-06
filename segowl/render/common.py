"""Helpers shared by the renderers: output writing, palettes, cell text."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from segowl.analysis import ZoneAgg
from segowl.inventory import Inventory
from segowl.ports import ports_text
from segowl.verdict import NODATA, OPEN, REACH, SYM, VCLASS

# Red, amber and green belong to the Flow Policy (always with an icon): no Zone or Machine uses them.
# Zone (fill, stroke, title text): a distinct hue on the border and title, the fill stays pale. 8 hues, dark
# and light variants, every pair apart (OKLab x100: >= 15.4 normal vision, >= 8.7 deutan / protan); beyond
# 8 Zones they repeat and the title alone names the Zone.
ZONE_COLORS = [
    ("#eff8ff", "#1565c0", "#0b3c75"),  # blue
    ("#fff3ee", "#8d6e63", "#51352c"),  # taupe
    ("#f6f5ff", "#7c4dff", "#3c3072"),  # violet
    ("#eafafe", "#1597ad", "#00495e"),  # cyan
    ("#f5f5ff", "#3d2a8a", "#3a3173"),  # indigo
    ("#eafbfd", "#80deea", "#004954"),  # light cyan
    ("#eafbf9", "#0b5f5a", "#004944"),  # dark teal
    ("#f7f5ff", "#b9a6f2", "#432e6f"),  # lavender
]
# Machine (fill, stroke, text): the 4 cool hues that pass the validator on all pairs; a 5th does not exist.
MACHINE_COLORS = [
    ("#e7eaf3", "#3a4e9d", "#1d274e"),  # indigo
    ("#f4ecf8", "#a35ec1", "#522f60"),  # purple
    ("#e9f4f8", "#48a5c7", "#245264"),  # steel cyan
    ("#f7f3fe", "#bb9af4", "#5e4d7a"),  # lavender
]


def write_output(out_dir: str, name: str, text: str) -> str:
    path = Path(out_dir, name)
    path.write_text(text + "\n", encoding="utf-8")
    return str(path)


def zone_palette(inv: Inventory) -> dict[str, tuple[str, str, str]]:
    zones = sorted({h.zone for h in inv.values()})
    return {z: ZONE_COLORS[i % len(ZONE_COLORS)] for i, z in enumerate(zones)}


def machine_palette(inv: Inventory) -> dict[str, tuple[str, str, str]]:
    """Own colour (fill, stroke, text) per multi-interface Machine, cycling through MACHINE_COLORS."""
    count: dict[str, int] = defaultdict(int)
    for h in inv.values():
        count[h.machine] += 1
    multi = sorted(m for m, n in count.items() if n > 1)
    return {m: MACHINE_COLORS[i % len(MACHINE_COLORS)] for i, m in enumerate(multi)}


def zone_cell(a: ZoneAgg | None) -> tuple[str, str]:
    """(css class, text) of a zone -> zone cell, without the pair counter."""
    if not a or a.verdict < REACH:
        return VCLASS[a.verdict if a else NODATA], SYM[a.verdict if a else NODATA]
    ports = ports_text(sorted(a.open_ports)[:6])
    return VCLASS[a.verdict], f"{'OPEN' if a.verdict == OPEN else 'o'} {ports}".strip()
