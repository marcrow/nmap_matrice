"""Helpers shared by the renderers: output writing, palettes, cell text."""

from __future__ import annotations

import colorsys
from collections import defaultdict
from pathlib import Path

from seg_matrix.analysis import ZoneAgg
from seg_matrix.inventory import Inventory
from seg_matrix.ports import ports_text
from seg_matrix.verdict import OPEN, VCLASS

# Zone palette (fill, stroke, text) — modern, cyclic
ZONE_COLORS = [
    ("#eef5ff", "#3b82f6", "#1e3a5f"),  # blue
    ("#eafaf1", "#22a565", "#14532d"),  # green
    ("#fff4e6", "#f59e0b", "#7c4a03"),  # amber
    ("#fdeef4", "#db2777", "#7a1840"),  # pink
    ("#f1eefe", "#7c3aed", "#3f2a7a"),  # violet
    ("#e6fbf8", "#14b8a6", "#115e59"),  # teal
    ("#fef0f0", "#ef4444", "#7f1d1d"),  # red
]


def write_output(out_dir: str, name: str, text: str) -> str:
    path = Path(out_dir, name)
    path.write_text(text + "\n", encoding="utf-8")
    return str(path)


def zone_palette(inv: Inventory) -> dict[str, tuple[str, str, str]]:
    zones = sorted({h.zone for h in inv.values()})
    return {z: ZONE_COLORS[i % len(ZONE_COLORS)] for i, z in enumerate(zones)}


def machine_palette(inv: Inventory) -> dict[str, tuple[str, str, str]]:
    """Own colour (fill, stroke, text) per multi-interface machine; golden-angle hues."""
    count = defaultdict(int)
    for h in inv.values():
        count[h.machine] += 1
    multi = sorted(m for m, n in count.items() if n > 1)

    def hexc(hue: float, light: float, sat: float) -> str:
        return "#" + "".join(f"{round(c * 255):02x}" for c in colorsys.hls_to_rgb(hue, light, sat))

    return {
        m: (hexc(i * 0.618 % 1, 0.85, 0.75), hexc(i * 0.618 % 1, 0.40, 0.70), hexc(i * 0.618 % 1, 0.20, 0.60))
        for i, m in enumerate(multi)
    }


def zone_cell(a: ZoneAgg | None) -> tuple[str, str]:
    """(css class, text) of a zone -> zone cell, without the pair counter."""
    if not a:
        return "v-none", "."
    if a.reach_pairs == 0:
        return "v-block", "x"
    ports = ports_text(sorted(a.open_ports)[:6])
    return VCLASS[a.verdict], f"{'OPEN' if a.verdict == OPEN else 'o'} {ports}".strip()
