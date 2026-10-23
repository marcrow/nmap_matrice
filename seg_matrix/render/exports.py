"""CSV exports of the observed flows, to reuse in the audit report or to bootstrap a Flow Policy."""

from __future__ import annotations

import csv
import os
from collections import defaultdict

from seg_matrix.analysis import Analysis
from seg_matrix.inventory import Host, extra_columns
from seg_matrix.policy import UNDECLARED
from seg_matrix.ports import Port, port_label
from seg_matrix.verdict import ALIVE, OPEN, REACH


def write_observed_flows(a: Analysis, out_dir: str) -> str:
    """One row per Source -> Interface -> port that is open, plus one per pair only reachable / alive."""
    extras = extra_columns(a.inv)
    policy = a.policy is not None

    def side(h: Host) -> list[str]:
        return [h.ip, h.machine, h.zone, h.htype] + [h.extra.get(k, "") for k in extras]

    head = [f"{p}_{c}" for p in ("src", "dst") for c in ["ip", "machine", "zone", "type"] + extras]
    head += ["proto", "port", "state"] + (["policy", "rule"] if policy else []) + ["scans"]
    path = os.path.join(out_dir, "observed_flows.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:  # BOM: spreadsheets detect UTF-8
        w = csv.writer(fh, delimiter=";")
        w.writerow(head)
        for s in a.sources:
            for d, c in a.matrix[s].items():
                base = side(a.inv[s]) + side(a.inv[d])
                scans = ",".join(c.scans)
                if c.verdict == OPEN:
                    for port in c.open_ports:
                        decision = []
                        if policy:
                            rule = a.decisions[(s, d, port)]
                            decision = [rule.action if rule else UNDECLARED, f"#{rule.line}" if rule else ""]
                        w.writerow(base + [port[1], port[0], "open"] + decision + [scans])
                elif c.verdict in (REACH, ALIVE):
                    state = "reachable" if c.verdict == REACH else "alive"
                    w.writerow(base + ["", "", state] + (["", ""] if policy else []) + [scans])
    return path


def write_observed_zone_flows(a: Analysis, out_dir: str) -> str:
    """Observed OPEN flows per Zone pair and port, in Flow Policy format with an empty action.

    Fill the action column (allow / deny), keep the rows you want, and use it as flow_policy.csv.
    """
    flows: dict[tuple[str, str, Port], set[tuple[str, str]]] = defaultdict(set)
    for s, row in a.matrix.items():
        for d, c in row.items():
            for port in c.open_ports:
                flows[(a.inv[s].zone, a.inv[d].zone, port)].add((s, d))
    path = os.path.join(out_dir, "observed_zone_flows.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:  # BOM: spreadsheets detect UTF-8
        w = csv.writer(fh, delimiter=";")
        w.writerow(["src", "dst", "ports", "action", "comment"])
        for (zs, zd, port), pairs in sorted(flows.items()):
            s, d = min(pairs)
            comment = f"{len(pairs)} pair(s), e.g. {a.inv[s].short} -> {a.inv[d].short}"
            if a.policy is not None:
                statuses = sorted({a.flow_status(x, y, port) for x, y in pairs})
                comment += f"; currently {'/'.join(statuses)}"
            w.writerow([zs, zd, port_label(port), "", comment])
    return path
