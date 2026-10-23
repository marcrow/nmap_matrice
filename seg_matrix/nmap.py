"""Discovery and parsing of nmap outputs (xml > gnmap > classic)."""

from __future__ import annotations

import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

SCAN_EXT_PRIORITY = (".xml", ".gnmap", ".nmap")


def detect_pn(path: str) -> bool:
    """Detect the -Pn option in the nmap file header (xml args / gnmap comment)."""
    try:
        head = open(path, encoding="utf-8", errors="replace").read(4096)
    except OSError:
        return False
    return bool(re.search(r'(?:^|[\s"])-Pn(?:[\s"]|$)', head))


def discover_scans(scan_dir: str) -> dict[str, str]:
    by_ip: dict[str, dict[str, str]] = defaultdict(dict)
    for entry in os.listdir(scan_dir):
        full = os.path.join(scan_dir, entry)
        if not os.path.isfile(full):
            continue
        base, ext = os.path.splitext(entry)
        ext = ext.lower()
        if ext in SCAN_EXT_PRIORITY:
            by_ip[base][ext] = full
    chosen: dict[str, str] = {}
    for ip, variants in by_ip.items():
        for ext in SCAN_EXT_PRIORITY:
            if ext in variants:
                chosen[ip] = variants[ext]
                break
    return chosen


def parse_xml(path: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        print(f"[!] Unreadable XML {path}: {e}", file=sys.stderr)
        return out
    for host in root.iter("host"):
        st = host.find("status")
        state = st.get("state") if st is not None else None
        a = host.find("address[@addrtype='ipv4']")
        if a is None:
            a = host.find("address[@addrtype='ipv6']")
        if a is None:
            continue
        rec = out.setdefault(a.get("addr"), {"state": state, "ports": [], "ignored": []})
        rec["state"] = state or rec["state"]
        ports = host.find("ports")
        if ports is not None:
            for ep in ports.findall("extraports"):
                rec["ignored"].append((ep.get("state"), int(ep.get("count", "0") or 0)))
            for p in ports.findall("port"):
                pst = p.find("state")
                rec["ports"].append(
                    (
                        int(p.get("portid")),
                        p.get("protocol"),
                        pst.get("state") if pst is not None else "unknown",
                    )
                )
    return out


_GNMAP_HOST = re.compile(r"Host:\s+(\S+)\s+\([^)]*\)\s+(.*)")
_GNMAP_IGNORED = re.compile(r"(\w+)\s+\((\d+)\)")


def parse_gnmap(path: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        if not line.startswith("Host: "):
            continue
        m = _GNMAP_HOST.match(line)
        if not m:
            continue
        ip, rest = m.group(1), m.group(2)
        rec = out.setdefault(ip, {"state": None, "ports": [], "ignored": []})
        if rest.startswith("Status:"):
            rec["state"] = rest.split("Status:", 1)[1].strip().lower()
        elif rest.startswith("Ports:"):
            rec["state"] = rec["state"] or "up"
            ports_part = rest[len("Ports:") :]
            if "\tIgnored State:" in ports_part:
                ports_part, ig = ports_part.split("\tIgnored State:", 1)
                im = _GNMAP_IGNORED.search(ig)
                if im:
                    rec["ignored"].append((im.group(1), int(im.group(2))))
            for tok in ports_part.split(","):
                tok = tok.strip()
                parts = tok.split("/")
                if len(parts) < 3:
                    continue
                try:
                    rec["ports"].append((int(parts[0]), parts[2], parts[1]))
                except ValueError:
                    continue
    return out


def parse_nmap_classic(path: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    cur: str | None = None
    ip_re = re.compile(r"Nmap scan report for (?:.*\()?(\d+\.\d+\.\d+\.\d+)\)?")
    port_re = re.compile(r"^(\d+)/(\w+)\s+(\w+)")
    for line in open(path, encoding="utf-8", errors="replace"):
        m = ip_re.search(line)
        if m:
            cur = m.group(1)
            out.setdefault(cur, {"state": "up", "ports": [], "ignored": []})
            continue
        if cur and "Host is up" in line:
            out[cur]["state"] = "up"
        pm = port_re.match(line.strip())
        if cur and pm:
            out[cur]["ports"].append((int(pm.group(1)), pm.group(2), pm.group(3)))
    return out


def parse_scan(path: str) -> dict[str, dict]:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".xml":
        return parse_xml(path)
    if ext == ".gnmap":
        return parse_gnmap(path)
    return parse_nmap_classic(path)
