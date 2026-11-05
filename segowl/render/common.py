"""Helpers shared by the renderers: output writing, palettes, cell text."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from segowl.analysis import ZoneAgg
from segowl.inventory import Inventory
from segowl.ports import ports_text
from segowl.verdict import NODATA, OPEN, REACH, SYM, VCLASS

# Red, amber and green belong to the Flow Policy (always with an icon): no Zone or Machine uses them.
# Zone (fill, stroke, title text): a distinct hue on the border and title, the fill stays pale. The 5 strokes
# pass the dataviz validator in Zone order (light, adjacent pairs; CVD cyan / orchid 6.1, legal: every
# Zone carries its title). Beyond 5 Zones the hues repeat and the title alone names the Zone.
ZONE_COLORS = [
    ("#eef4fc", "#2a78d6", "#174276"),  # blue
    ("#fbf2f7", "#d0609a", "#723555"),  # orchid
    ("#ecf7f8", "#1597ad", "#0c535f"),  # cyan
    ("#f2f0fb", "#5b45c9", "#32266f"),  # violet
    ("#f7f3ee", "#a0662f", "#58381a"),  # brown
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
