"""Scan Profiles: reusable nmap recipes (ports + options) that never carry targets (GLOSSARY).

scan_profiles.csv: name;ports;options
  ports   : the Flow Policy port syntax (22,8000-8100,udp:161,@<Port Group>) plus top:<N> (nmap --top-ports)
  options : any nmap options except DENIED ones (targets, client data, output handled by SegOWL, --open)

nmap intersects --top-ports with -p instead of adding them (checked on nmap 7.94), so a profile
that mixes both is exported as two Scans, <name>-top<N> and <name>-ports, merged later into the
Source View like any other pair of Scans.
"""

from __future__ import annotations

import csv
import functools
import io
import re
import shlex
from dataclasses import dataclass
from pathlib import Path

from segowl import csvfile
from segowl.port_groups import PortGroups
from segowl.ports import PortSet, count_ports, format_ranges, parse_port_set

DEFAULTS = Path(__file__).resolve().parent / "defaults"
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")  # used in file names and shell scripts
DENIED = {
    "-iL": "carries a target list (targets always come from the inventory)",
    "-iR": "scans random Internet hosts",
    "--exclude": "carries client IPs",
    "--excludefile": "carries client IPs",
    "-S": "carries a spoofed source IP",
    "-D": "carries decoy IPs",
    "--proxies": "carries proxy addresses",
    "--dns-servers": "carries client DNS IPs",
    "--script-args": "may carry hosts or credentials",
    "--script-args-file": "may carry hosts or credentials",
    "--resume": "output is managed by SegOWL",
    "--open": "hides closed ports, so REACHABLE disappears",
}
_OUTPUT = re.compile(r"^-o[ANXGS]")  # -oA, -oX, -oN, -oG, -oS: SegOWL writes the outputs
NMAP_PREFIX = {"tcp": "T", "udp": "U", "sctp": "S"}


@dataclass
class Profile:
    name: str
    ports: str
    options: str
    description: str = ""  # what it is for; optional 4th column


def read_profiles(text: str) -> list[Profile]:
    return [Profile(*(r + [""] * 4)[:4]) for _, r in csvfile.rows(text) if r[0].lower() != "name"]


def profiles_text(profiles: list[Profile]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";", lineterminator="\n")
    # no description typed: the 3-column format stays; a row without one keeps its 3 cells
    w.writerow(["name", "ports", "options"] + ["description"] * any(p.description for p in profiles))
    w.writerows([p.name, p.ports, p.options] + [p.description] * bool(p.description) for p in profiles)
    return buf.getvalue()


def denied_reason(token: str) -> str | None:
    flag = token.split("=", 1)[0]
    if flag in DENIED:
        return DENIED[flag]
    return "output is managed by SegOWL" if _OUTPUT.match(token) else None


def split_ports(p: Profile, groups: PortGroups) -> tuple[int, PortSet]:
    """(top-ports N or 0, explicit ports with Port Groups expanded). Raises ValueError."""
    top, rest = 0, []
    for token in (t.strip() for t in p.ports.split(",")):
        if not token.startswith("top:"):
            rest.append(token)
        elif not token[4:].isdigit() or not 1 <= int(token[4:]) <= 65535:
            raise ValueError(f"invalid top ports {token!r}")
        else:
            top = max(top, int(token[4:]))
    return top, parse_port_set(",".join(rest), groups)


def validate(p: Profile, groups: PortGroups) -> list[str]:
    errors = []
    if not NAME_RE.match(p.name):
        errors.append(f"name {p.name!r}: letters, digits, . _ - only")
    try:
        top, explicit = split_ports(p, groups)
        if not top and not explicit:
            errors.append(f"{p.name}: no port")
    except ValueError as e:
        errors.append(f"{p.name}: {e}")
    try:
        tokens = shlex.split(p.options)
    except ValueError as e:
        return [*errors, f"{p.name}: options: {e}"]
    errors += [f"{p.name}: {t} refused: {why}" for t in tokens if (why := denied_reason(t))]
    return errors


def commands(p: Profile, groups: PortGroups, out_dir: str, targets: str) -> list[tuple[str, str, list[str]]]:
    """[(label, output base name, nmap argv)]: one Scan, or two when top ports meet explicit ports."""
    top, explicit = split_ports(p, groups)
    opts = shlex.split(p.options)
    spec = ",".join(f"{NMAP_PREFIX[proto]}:{format_ranges(r)}" for proto, r in sorted(explicit.items()) if r)
    with_udp = opts + (["-sU"] if "udp" in explicit and "-sU" not in opts else [])
    tcp_only = [o for o in opts if o != "-sU"]

    def cmd(base, options, ports):
        return ["nmap", *options, *ports, "-iL", targets, "-oA", f"{out_dir}/{base}"]

    if top and spec:
        return [
            (
                f"nmap top {top} ports",
                f"{p.name}-top{top}",
                cmd(f"{p.name}-top{top}", tcp_only, ["--top-ports", str(top)]),
            ),
            ("explicit ports", f"{p.name}-ports", cmd(f"{p.name}-ports", with_udp, ["-p", spec])),
        ]
    if top:
        return [(f"nmap top {top} ports", p.name, cmd(p.name, opts, ["--top-ports", str(top)]))]
    return [("explicit ports", p.name, cmd(p.name, with_udp, ["-p", spec]))]


def expected_files(p: Profile, groups: PortGroups) -> list[str]:
    try:
        return [base for _, base, _ in commands(p, groups, ".", "targets")]
    except ValueError:
        return []


def counts(p: Profile, groups: PortGroups) -> dict[str, int]:
    top, explicit = split_ports(p, groups)
    return {"top": top, **{proto: count_ports(explicit.get(proto, [])) for proto in ("tcp", "udp")}}


def script(p: Profile, groups: PortGroups, mission: str, src: str, src_label: str, targets: list[str]) -> str:
    """A self-contained shell script to run on the Source; its outputs go in scans/<src>/."""
    out, tfile = f"scans/{src}", f"targets/{src}-{p.name}.txt"
    lines = [
        "#!/bin/sh",
        f"# SegOWL — Mission {mission} · Source {src_label} · Scan Profile {p.name}",
        f"# {len(targets)} targets: the inventory minus this Source's own Interfaces (Self).",
        "# Run it on the Source, from any folder, then copy the scans/ folder back into the Mission.",
        "set -e",
        'cd "$(dirname "$0")"',
        f"mkdir -p {out} targets",
        f"cat > {tfile} <<'SEGOWL_TARGETS'",
        *targets,
        "SEGOWL_TARGETS",
    ]
    for label, _, argv in commands(p, groups, out, tfile):
        lines += [f"# {label}", shlex.join(argv)]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- port search
def _csv_rows(path: Path) -> list[list[str]]:
    return [r for _, r in csvfile.rows(csvfile.read(path))]


def label_key(row) -> tuple[str, str]:
    """What names a Port Label: port + product (case aside); several products may share a port."""
    return row[0].lower(), row[1].lower()


def read_labels(path: Path) -> list[tuple[str, str, str, str, str]]:
    """The rows of one port_labels.csv; vendor and cleartext are optional trailing columns."""
    return [tuple((r + [""] * 5)[:5]) for r in _csv_rows(path) if r[0].lower() != "port"]


def load_labels(mission_file: Path | None = None) -> list[tuple[str, str, str, str, str]]:
    """Port Labels (port, product, tags, vendor, cleartext): the shipped ones, a Mission row replacing
    the shipped label of the same port + product, then the Mission's new labels."""
    rows = {label_key(r): r for r in read_labels(DEFAULTS / "port_labels.csv")}
    rows.update({label_key(r): r for r in read_labels(mission_file)} if mission_file else {})
    return list(rows.values())


@functools.cache
def iana() -> list[tuple[str, str, str, str]]:
    return [tuple((r + ["", "", "", ""])[:4]) for r in _csv_rows(DEFAULTS / "iana_ports.csv")[1:]]


def search_ports(q: str, groups: dict[str, str], labels: list[tuple[str, ...]], limit=60) -> list[dict]:
    """Port Groups, then Port Labels (tags, exact product first), then IANA; a typed port or top N first."""
    q = q.strip().lower()
    if not q:
        return []
    out: list[dict] = []
    if m := re.fullmatch(r"top[: ]?(\d*)", q):
        out += [
            {"key": f"top:{n}", "label": f"nmap's {n} most common ports", "src": "top ports"}
            for n in ([m[1]] if m[1] else ["100", "1000", "5000"])
        ]
    if re.fullmatch(r"((udp|tcp|sctp):)?\d+(-\d+)?", q):
        out.append({"key": q.removeprefix("tcp:"), "label": "this port as typed", "src": "typed"})
    out += [
        {"key": f"@{g}", "label": f"Port Group · {spec}", "src": "Port Group"}
        for g, spec in groups.items()
        if q in g.lower() or q in spec.split(",")
    ]
    # cleartext=yes is searched and shown as one more tag
    labels = [
        (p, prod, ",".join(filter(None, [t, "cleartext" * (c == "yes")])), v) for p, prod, t, v, c in labels
    ]
    # a partly typed port (338, udp:16) also finds the ports it starts, after the exact matches
    m = re.fullmatch(r"(?:(udp|tcp):)?(\d+)", q)

    def starts(key: str) -> bool:
        return (
            bool(m) and key.removeprefix("udp:").startswith(m[2]) and (m[1] != "udp") ^ key.startswith("udp:")
        )

    tagged = sorted({lab[0] for lab in labels if q in lab[2].split(",")})
    if len(tagged) > 1:
        out.append(
            {
                "key": ",".join(tagged),
                "label": f"all {len(tagged)} ports tagged {q!r}",
                "src": "tag",
                "many": tagged,
            }
        )

    def match(w: str, lab: tuple[str, ...]) -> bool:  # starts() only fires for a one-word numeric query
        return (
            w == lab[0].removeprefix("udp:")
            or starts(lab[0])
            or w in lab[1].lower()
            or w in lab[2].split(",")
            or w in lab[3].lower()
        )

    # several words: each one must match the port, the product, a tag or the vendor ("veeam backup")
    hits = [lab for lab in labels if all(match(w, lab) for w in q.split())]
    hits.sort(
        key=lambda lab: (
            not (lab[1].lower() == q or (lab[1].lower().startswith(q + " ") and "alternate" not in lab[1])),
            starts(lab[0]) and lab[0].removeprefix("udp:") != m[2],
        )
    )
    # not for a typed port (its completions) nor a tag (the "all N ports tagged" entry above selects them)
    result_ports = sorted({lab[0] for lab in hits})
    if len(result_ports) > 1 and not m and len(tagged) < 2:
        total = sum(count_ports(r) for r in parse_port_set(",".join(result_ports)).values())
        ranges = " ".join(p for p in result_ports if "-" in p)
        warn = f"select all {total} ports listed ⚠ check them first" + (
            f", ranges: {ranges}" if ranges else ""
        )
        out.append(
            {
                "key": ",".join(result_ports),
                "label": warn,
                "src": "search",
                "many": result_ports,
                "ports": total,
            }
        )
        limit = max(limit, len(out) + len(hits))  # every listed port is shown: you add what you see
    out += [
        {
            "key": p,
            "label": f"{prod} · {vendor}" if vendor and vendor.lower() not in prod.lower() else prod,
            "tags": tags,
            "src": "Port Label",
        }
        for p, prod, tags, vendor in hits
    ]
    seen = {o["key"] for o in out}
    for name, port, proto, desc in iana():
        key = port if proto == "tcp" else f"{proto}:{port}"
        if key not in seen and (q == port or starts(key) or q in name.lower() or q in desc.lower()):
            out.append({"key": key, "label": f"{name} — {desc}", "src": "IANA"})
            seen.add(key)
        if len(out) >= limit:
            break
    return out[:limit]
