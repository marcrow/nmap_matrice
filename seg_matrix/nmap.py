"""Discovery and parsing of nmap outputs into Scans (xml > gnmap > classic)."""

from __future__ import annotations

import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass, field

from seg_matrix.ports import Ranges, in_ranges, merge_ranges, parse_ranges

SCAN_EXT_PRIORITY = (".xml", ".gnmap", ".nmap")
_PN = re.compile(r'(?:^|[\s"])-Pn(?:[\s"]|$)')
# "# Nmap 7.94SVN scan initiated Fri Oct 23 16:15:44 2026 as: nmap -sT ..." (gnmap / normal output)
_HEADER = re.compile(r"^# Nmap \S+ scan initiated ?(.*?) as: (.*)$")


@dataclass
class HostRecord:
    """What one Scan saw of one target IP."""

    state: str | None = None
    ports: list[tuple[int, str, str]] = field(default_factory=list)  # (port, proto, state) listed by nmap
    ignored: list[tuple[str, int]] = field(default_factory=list)  # (state, count) of ports nmap grouped
    rest: list[tuple[str, Ranges, str]] = field(
        default_factory=list
    )  # (proto, ranges, state) of grouped ports

    def state_of(self, port: int, proto: str) -> str | None:
        """State of a port in this Scan, or None when the Scan says nothing attributable about it."""
        for p, pr, s in self.ports:
            if p == port and pr == proto:
                return s
        for pr, ranges, s in self.rest:
            if pr == proto and in_ranges(port, ranges):
                return s
        return None


@dataclass
class Scan:
    """One nmap run from a Source."""

    path: str
    source: str
    command: str = ""
    started: str = ""
    start_ts: int = 0
    pn: bool = False
    coverage: dict[str, Ranges] | None = None  # proto -> tested ports; None = unknown (non-XML output)
    hosts: dict[str, HostRecord] = field(default_factory=dict)

    @property
    def name(self) -> str:
        return f"{self.source}/{os.path.basename(self.path)}"


def _best_formats(paths: list[str]) -> list[str]:
    """One file per scan: `nmap -oA x` writes x.xml/x.gnmap/x.nmap, keep the richest format."""
    by_stem: dict[str, dict[str, str]] = defaultdict(dict)
    for p in paths:
        stem, ext = os.path.splitext(p)
        if ext.lower() in SCAN_EXT_PRIORITY:
            by_stem[stem][ext.lower()] = p
    return sorted(next(v[e] for e in SCAN_EXT_PRIORITY if e in v) for v in by_stem.values())


def discover_scans(scan_dir: str) -> dict[str, list[str]]:
    """Source IP -> scan files, from `<scan_dir>/<source_ip>/*` (any name) or legacy `<source_ip>.<ext>`."""
    found: dict[str, list[str]] = defaultdict(list)
    for entry in sorted(os.listdir(scan_dir)):
        full = os.path.join(scan_dir, entry)
        if os.path.isdir(full):
            found[entry] += [os.path.join(full, f) for f in os.listdir(full)]
        elif os.path.splitext(entry)[1].lower() in SCAN_EXT_PRIORITY:
            found[os.path.splitext(entry)[0]].append(full)
    return {src: picked for src, paths in found.items() if (picked := _best_formats(paths))}


def parse_xml(path: str, source: str) -> Scan:
    scan = Scan(path, source)
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        print(f"[!] Unreadable XML {path}: {e}", file=sys.stderr)
        return scan
    scan.command = root.get("args", "")
    scan.started = root.get("startstr", "")
    scan.start_ts = int(root.get("start") or 0)
    scan.pn = bool(_PN.search(scan.command))
    coverage: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for si in root.findall("scaninfo"):
        coverage[si.get("protocol", "tcp")] += parse_ranges(si.get("services", ""))
    scan.coverage = {proto: merge_ranges(r) for proto, r in coverage.items()}

    for host in root.iter("host"):
        st = host.find("status")
        a = host.find("address[@addrtype='ipv4']")
        if a is None:
            a = host.find("address[@addrtype='ipv6']")
        if a is None:
            continue
        rec = scan.hosts.setdefault(a.get("addr"), HostRecord())
        rec.state = (st.get("state") if st is not None else None) or rec.state
        ports = host.find("ports")
        if ports is None:
            continue
        extras = ports.findall("extraports")
        for ep in extras:
            state = ep.get("state")
            rec.ignored.append((state, int(ep.get("count", "0") or 0)))
            for er in ep.findall("extrareasons"):
                if er.get("ports"):  # nmap >= 7.9x lists the grouped ports
                    rec.rest.append((er.get("proto", "tcp"), parse_ranges(er.get("ports")), state))
        if not rec.rest and len(extras) == 1 and len(scan.coverage) == 1:
            # older nmap: a single grouped state covers every tested port not listed explicitly
            ((proto, ranges),) = scan.coverage.items()
            rec.rest.append((proto, ranges, extras[0].get("state")))
        for p in ports.findall("port"):
            pst = p.find("state")
            rec.ports.append(
                (int(p.get("portid")), p.get("protocol"), pst.get("state") if pst is not None else "unknown")
            )
    return scan


def _read_header(path: str, scan: Scan) -> None:
    with open(path, encoding="utf-8", errors="replace") as fh:
        m = _HEADER.match(fh.readline().rstrip("\n"))
    if m:
        scan.started, scan.command = m.group(1), m.group(2)
        scan.pn = bool(_PN.search(scan.command))


_GNMAP_HOST = re.compile(r"Host:\s+(\S+)\s+\([^)]*\)\s+(.*)")
_GNMAP_IGNORED = re.compile(r"(\w+)\s+\((\d+)\)")


def parse_gnmap(path: str, source: str) -> Scan:
    scan = Scan(path, source)
    _read_header(path, scan)
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        if not line.startswith("Host: "):
            continue
        m = _GNMAP_HOST.match(line)
        if not m:
            continue
        ip, rest = m.group(1), m.group(2)
        rec = scan.hosts.setdefault(ip, HostRecord())
        if rest.startswith("Status:"):
            rec.state = rest.split("Status:", 1)[1].strip().lower()
        elif rest.startswith("Ports:"):
            rec.state = rec.state or "up"
            ports_part = rest[len("Ports:") :]
            if "\tIgnored State:" in ports_part:
                ports_part, ig = ports_part.split("\tIgnored State:", 1)
                im = _GNMAP_IGNORED.search(ig)
                if im:
                    rec.ignored.append((im.group(1), int(im.group(2))))
            for tok in ports_part.split(","):
                parts = tok.strip().split("/")
                if len(parts) < 3:
                    continue
                try:
                    rec.ports.append((int(parts[0]), parts[2], parts[1]))
                except ValueError:
                    continue
    return scan


def parse_nmap_classic(path: str, source: str) -> Scan:
    scan = Scan(path, source)
    _read_header(path, scan)
    cur: HostRecord | None = None
    ip_re = re.compile(r"Nmap scan report for (?:.*\()?(\d+\.\d+\.\d+\.\d+)\)?")
    port_re = re.compile(r"^(\d+)/(\w+)\s+([\w|]+)")
    for line in open(path, encoding="utf-8", errors="replace"):
        m = ip_re.search(line)
        if m:
            cur = scan.hosts.setdefault(m.group(1), HostRecord(state="up"))
            continue
        pm = port_re.match(line.strip())
        if cur and pm:
            cur.ports.append((int(pm.group(1)), pm.group(2), pm.group(3)))
    return scan


def parse_scan(path: str, source: str) -> Scan:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".xml":
        return parse_xml(path, source)
    if ext == ".gnmap":
        return parse_gnmap(path, source)
    return parse_nmap_classic(path, source)
