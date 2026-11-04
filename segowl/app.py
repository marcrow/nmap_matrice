"""Local web app around a Mission folder: `segowl serve <mission>` and `segowl user add <login>`.

Standard library only (docs/adr/0004). The Mission folder stays the only state (docs/adr/0003):
the report is regenerated from it whenever its files change, whoever changed them.
"""

from __future__ import annotations

import argparse
import getpass
import hashlib
import hmac
import html
import http.cookies
import io
import ipaddress
import json
import os
import secrets
import shlex
import ssl
import sys
import tempfile
import threading
import urllib.parse
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from segowl import cli, kits
from segowl import mission_files as mf
from segowl import scan_profiles as sp
from segowl.inventory import load_inventory
from segowl.nmap import SCAN_EXT_PRIORITY
from segowl.policy import _kind as policy_kind
from segowl.policy import _ports as policy_ports
from segowl.policy import load_policy
from segowl.port_groups import DEFAULTS as GROUP_DEFAULTS
from segowl.port_groups import load_port_groups

ASSETS = Path(__file__).parent / "assets"
STATIC = {  # served under /static/
    "logo.svg": "image/svg+xml",
    "app.css": "text/css; charset=utf-8",
    "app_inventory.js": "text/javascript; charset=utf-8",
    "app_mission.js": "text/javascript; charset=utf-8",
    "app_kits.js": "text/javascript; charset=utf-8",
    "app_policy.js": "text/javascript; charset=utf-8",
    "app_profiles.js": "text/javascript; charset=utf-8",
    "app_scans.js": "text/javascript; charset=utf-8",
    "tabulator.min.js": "text/javascript; charset=utf-8",
    "tabulator.min.css": "text/css; charset=utf-8",
}
LOCK = threading.RLock()  # ponytail: one lock for regeneration and saves, per-file locks if it ever bites
COOKIE = "segowl_session"
INVENTORY_HEADER = "ip;zone;type;name\n"
MAX_BODY = 20_000_000


# ---------------------------------------------------------------- users file
def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt${salt.hex()}${digest.hex()}"


def check_password(password: str, stored: str) -> bool:
    try:
        _, salt, _ = stored.split("$")
        return hmac.compare_digest(hash_password(password, bytes.fromhex(salt)), stored)
    except ValueError:
        return False


def load_users(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    users = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            login, _, stored = line.partition(":")
            users[login] = stored
    return users


def add_user(path: Path, login: str, password: str) -> None:
    if not login or ":" in login:
        raise SystemExit("[!] Invalid login (empty or contains ':')")
    users = load_users(path)
    users[login] = hash_password(password)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{u}:{h}\n" for u, h in users.items()), encoding="utf-8")
    path.chmod(0o600)


# ---------------------------------------------------------------- mission folder
def fingerprint(path: Path) -> str:
    """Content fingerprint used for optimistic saves ('' when the file does not exist)."""
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""


class Conflict(Exception):
    """The file changed since the editor loaded it."""


def check_fingerprints(expected: dict[Path, str]) -> None:
    for path, fp in expected.items():
        if fingerprint(path) != fp:
            raise Conflict(f"{path.name} was modified by someone else since you loaded it: reload.")


def write_file(path: Path, content: str | None) -> None:
    """Atomic write (a reader never sees half a file); None removes the file."""
    if content is None:
        path.unlink(missing_ok=True)
        return
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def save_file(path: Path, content: str, expected: str) -> str:
    """Write `content` only if the file still has the fingerprint the editor loaded; return the new one."""
    with LOCK:
        check_fingerprints({path: expected})
        write_file(path, content)
        return fingerprint(path)


def ensure_skeleton(mission: Path) -> None:
    (mission / "scans").mkdir(parents=True, exist_ok=True)
    inv = mission / "inventory.csv"
    if not inv.exists():
        inv.write_text(INVENTORY_HEADER, encoding="utf-8")


def mission_state(mission: Path) -> tuple:
    """Changes whenever an input file of the report is added, removed or modified."""
    entries = []
    for root, dirs, files in os.walk(mission):
        if Path(root) == mission:
            dirs[:] = [d for d in dirs if d != "report"]
        for f in files:
            st = os.stat(os.path.join(root, f))
            entries.append((root, f, st.st_mtime_ns, st.st_size))
    return tuple(sorted(entries))


class Mission:
    def __init__(self, path: Path, config: Path | None = None):
        self.path = path
        self.config = config or Path.home() / ".config" / "segowl"  # holds kit_dirs
        self.state: tuple | None = None
        self.lines: list[str] = []
        self.error = ""
        self.fallback: tuple[tuple | None, str] = (None, "")  # (state, observed flows) when the report fails

    def file(self, name: str) -> Path:
        return self.path / name

    def text(self, name: str) -> str:
        p = self.file(name)
        return p.read_text(encoding="utf-8-sig", errors="replace") if p.is_file() else ""

    def refresh(self) -> None:
        """Regenerate the report if the Mission changed since the last generation."""
        with LOCK:
            state = mission_state(self.path)
            if state == self.state:
                return
            args = argparse.Namespace(
                mission=str(self.path),
                inventory=None,
                scans=None,
                port_groups=None,
                policy=None,
                out=None,
                pn=False,
                host_graph=True,
            )
            try:
                self.lines, self.error = cli.run(cli.mission_defaults(args)), ""
            except SystemExit as e:
                self.lines, self.error = [], str(e.code)
            except Exception as e:  # a broken input file must not take the app down
                self.lines, self.error = [], f"[!] {type(e).__name__}: {e}"
            self.state = state

    # ---- inventory editor
    def fps(self) -> dict[str, str]:
        return {n: fingerprint(self.file(n)) for n in ("inventory.csv", "zones.csv", "flow_policy.csv")}

    def inventory(self) -> dict:
        free, rows = mf.read_inventory(self.text("inventory.csv"))
        return {
            "fp": self.fps(),
            "columns": free,
            "rows": rows,
            "zones": mf.read_zones(self.text("zones.csv")),
            "refs": dict(mf.policy_refs(self.text("flow_policy.csv"))),
        }

    def save_inventory(self, data: dict) -> dict:
        free = [str(c).strip() for c in data.get("columns", []) if str(c).strip()]
        rows = data.get("rows", [])
        text = mf.inventory_text(free, rows)
        err = mf.check_inventory(text)
        if err:
            raise ValueError(err)
        used = {str(r.get("zone") or "").strip() for r in rows}
        with LOCK:
            fp = data.get("fp", {})
            check_fingerprints({self.file(n): fp.get(n, "") for n in ("inventory.csv", "zones.csv")})
            write_file(self.file("inventory.csv"), text)
            write_file(self.file("zones.csv"), mf.zones_text(data.get("zones", []), used))
            return self.fps()

    def rename(self, kind: str, old: str, new: str, fp: dict) -> dict:
        """Rename a Zone or a Machine in every file naming it, all or nothing."""
        new = new.strip()
        if kind not in ("zone", "machine") or not old or not new or ";" in new:
            raise ValueError("Invalid rename")
        names = ["inventory.csv", "flow_policy.csv"] + (["zones.csv"] if kind == "zone" else [])
        with LOCK:
            check_fingerprints({self.file(n): fp.get(n, "") for n in names})
            field = "zone" if kind == "zone" else "name"
            inv, n_inv = mf.rename_in_inventory(self.text("inventory.csv"), field, old, new)
            pol, n_pol = mf.rename_in_policy(self.text("flow_policy.csv"), old, new)
            write_file(self.file("inventory.csv"), inv)
            if self.file("flow_policy.csv").is_file():
                write_file(self.file("flow_policy.csv"), pol)
            if kind == "zone" and self.file("zones.csv").is_file():
                write_file(self.file("zones.csv"), mf.rename_in_zones(self.text("zones.csv"), old, new))
            msg = f"Renamed {old} → {new}: {n_inv} Interface(s), {n_pol} Flow Policy field(s) rewritten"
            return {"fp": self.fps(), "message": msg}

    # ---- Scan Profiles
    def groups(self) -> tuple[dict, dict[str, str]]:
        """(Port Groups as port sets, as raw specs), shipped defaults overridden by the Mission's."""
        specs = {}
        for path in (GROUP_DEFAULTS, self.file("port_groups.csv")):
            for row in mf._rows(path.read_text(encoding="utf-8-sig") if path.is_file() else ""):
                if row[0].lower() != "group" and len(row) > 1:
                    specs[row[0]] = row[1]
        mission_groups = self.file("port_groups.csv")
        try:
            sets = load_port_groups(str(mission_groups) if mission_groups.is_file() else None)
        except SystemExit:
            sets = load_port_groups(None)
        return sets, specs

    def profiles(self) -> dict:
        return {
            "fp": fingerprint(self.file("scan_profiles.csv")),
            "profiles": [vars(p) for p in sp.read_profiles(self.text("scan_profiles.csv"))],
            "groups": self.groups()[1],
            "denied": sp.DENIED,
            "sources": self.source_ips() or [r["ip"] for r in self.rows()[:1]],
        }

    def save_profiles(self, data: dict) -> str:
        profiles = [
            sp.Profile(str(p["name"]).strip(), str(p["ports"]).strip(), str(p["options"]).strip())
            for p in data.get("profiles", [])
        ]
        sets = self.groups()[0]
        errors = [e for p in profiles for e in sp.validate(p, sets)]
        names = [p.name for p in profiles]
        errors += [f"two profiles named {n}" for n in sorted({n for n in names if names.count(n) > 1})]
        if errors:
            raise ValueError("; ".join(errors))
        return save_file(self.file("scan_profiles.csv"), sp.profiles_text(profiles), data.get("fp", ""))

    def preview(self, data: dict) -> dict:
        p = sp.Profile(
            str(data.get("name") or "profile"), str(data.get("ports", "")), str(data.get("options", ""))
        )
        sets = self.groups()[0]
        errors = sp.validate(p, sets)
        src = str(data.get("src") or "")
        if errors:
            return {"errors": errors, "commands": [], "counts": {}, "warnings": []}
        targets = self.targets(src)
        cmds = sp.commands(p, sets, f"scans/{src or '<source>'}", f"targets/{src or '<source>'}-{p.name}.txt")
        c = sp.counts(p, sets)
        warnings = []
        if "-Pn" not in p.options.split():
            warnings.append(
                "Without -Pn, hosts that drop discovery are reported BLOCKED and never port-scanned."
            )
        if c["udp"] > 50:
            warnings.append(
                f"{c['udp']} UDP ports × {len(targets)} targets: expect hours. Keep UDP to a short list."
            )
        return {
            "errors": [],
            "commands": [
                {"label": label, "cmd": " ".join(shlex.quote(a) for a in argv)} for label, _, argv in cmds
            ],
            "counts": {**c, "targets": len(targets)},
            "warnings": warnings,
        }

    # ---- Flow Policy
    def policy(self) -> dict:
        rules = mf.read_policy(self.text("flow_policy.csv"))
        inv = self.rows()
        zones = list(dict.fromkeys([r["zone"] for r in inv if r.get("zone")]))
        zones += [z["name"] for z in mf.read_zones(self.text("zones.csv")) if z["name"] not in zones]
        return {
            "fp": fingerprint(self.file("flow_policy.csv")),
            "rules": rules,
            "errors": self.rule_errors(rules),
            "zones": zones,
            "machines": sorted({r.get("name") or r["ip"] for r in inv}),
            "groups": sorted(self.groups()[1]),
            "observed": self.observed(),
        }

    def rule_errors(self, rules: list[dict]) -> list[str]:
        """The CLI's message for each rule ('' when it loads), so the editor flags rules inline.

        Stricter than the CLI on one point: an undecided rule (no action) is checked too, so a draft
        never turns into a refused rule the day someone picks its action.
        """
        try:
            inv = load_inventory(str(self.file("inventory.csv")))
        except SystemExit:
            inv = {}
        sets = self.groups()[0]
        empty = {z["name"] for z in mf.read_zones(self.text("zones.csv"))} - {h.zone for h in inv.values()}
        out = []
        for r in rules:
            try:
                action = r["action"].lower()
                if action not in ("", "allow", "deny"):
                    raise SystemExit(f"[!] x: action must be allow or deny, not {r['action']!r}")
                for end in (r["src"], r["dst"]):
                    if end in empty:
                        raise SystemExit(f"[!] x: Zone {end!r} has no Interface yet: the CLI would refuse it")
                    policy_kind(end, inv, "x")
                policy_ports(r["ports"], sets, "x")
                out.append("")
            except SystemExit as e:
                out.append(str(e.code).removeprefix("[!] x: "))
        return out

    def save_policy(self, data: dict) -> dict:
        """Write flow_policy.csv if every rule loads; else return the per-rule errors, nothing written."""
        rules = [{k: str(r.get(k) or "").strip() for k in mf.POLICY_COLUMNS} for r in data.get("rules", [])]
        errors = self.rule_errors(rules)
        if any(errors):
            return {"fp": data.get("fp", ""), "errors": errors}
        text = mf.policy_text(rules, self.text("flow_policy.csv"))
        return {"fp": save_file(self.file("flow_policy.csv"), text, data.get("fp", "")), "errors": errors}

    def observed(self) -> dict[str, str]:
        """Ports observed open per Zone pair ('src;dst' -> '22,443'), from observed_zone_flows.csv."""
        self.refresh()
        text = self.text("report/observed_zone_flows.csv")
        if self.error and self.fallback[0] == self.state:
            text = self.fallback[1]
        elif self.error:  # e.g. a rule the CLI refuses: the flows are still wanted to fix the policy
            groups = self.file("port_groups.csv")
            with tempfile.TemporaryDirectory() as tmp:
                args = argparse.Namespace(
                    inventory=str(self.file("inventory.csv")),
                    scans=str(self.file("scans")),
                    port_groups=str(groups) if groups.is_file() else None,
                    policy=None,
                    out=tmp,
                    pn=False,
                    host_graph=False,
                )
                try:
                    cli.run(args)
                    text = Path(tmp, "observed_zone_flows.csv").read_text(encoding="utf-8-sig")
                except (SystemExit, Exception):  # broken inventory or Port Groups: nothing to show
                    text = ""
            self.fallback = (self.state, text)
        out: dict[str, list[str]] = {}
        for row in mf._rows(text):
            if row[0].lower() != "src" and len(row) > 2:
                out.setdefault(f"{row[0]};{row[1]}", []).append(row[2])
        return {k: ",".join(v) for k, v in out.items()}

    # ---- Auditor Kits
    def kits(self) -> dict:
        dirs = kits.read_dirs(self.config)
        return {
            "dirs": [str(d) for d in dirs],
            "kits": kits.list_kits(dirs),
            "mission": [n for n in kits.FILES if self.file(n).is_file()],
        }

    def kit_zip(self, kit_dir: str, name: str) -> bytes:
        return kits.export_zip(kits.kit_path(kits.read_dirs(self.config), Path(kit_dir), name, write=False))

    def set_kit_dirs(self, dirs: list[str]) -> dict:
        bad = [d for d in dirs if d.strip() and not Path(d.strip()).expanduser().is_absolute()]
        if bad:
            raise ValueError(f"Kit folders must be absolute paths: {', '.join(bad)}")
        with LOCK:
            kits.write_dirs(self.config, dirs)
        return self.kits()

    def kit_action(self, action: str, d: dict, blob: bytes = b"") -> dict:
        """save / apply / preview / import a kit; the kit is named by its folder and name."""
        dirs, kit_dir, name = kits.read_dirs(self.config), Path(str(d.get("dir", ""))), str(d.get("name", ""))
        overwrite = bool(d.get("overwrite"))
        with LOCK:
            if action == "save":
                kits.save_kit(self.path, dirs, kit_dir, name, overwrite)
                return {**self.kits(), "message": f"Saved as kit {name}"}
            if action in ("apply", "preview"):
                kit = kits.kit_path(dirs, kit_dir, name, write=False)
                # what the preview showed is what gets applied: neither side may change in between
                watched = [p / n for p in (self.path, kit) for n in kits.FILES]
                if action == "apply":
                    fp = d.get("fp") or {}
                    check_fingerprints({p: fp.get(str(p), "") for p in watched})
                files = d.get("files")  # None: every file the kit has
                files = None if files is None else [str(f) for f in files]
                out = kits.apply_kit(self.path, dirs, kit_dir, name, files, dry=action == "preview")
                return {**self.kits(), **out, "fp": {str(p): fingerprint(p) for p in watched}}
            if action == "import":
                kits.import_zip(blob, dirs, kit_dir, name, overwrite)
                return {**self.kits(), "message": f"Kit {name} imported"}
        raise ValueError(f"Unknown kit action {action}")

    # ---- Sources, targets, Scans
    def rows(self) -> list[dict]:
        return [r for r in mf.read_inventory(self.text("inventory.csv"))[1] if r.get("ip")]

    def source_ips(self) -> list[str]:
        scans = self.file("scans")
        return sorted(d.name for d in scans.iterdir() if d.is_dir()) if scans.is_dir() else []

    def targets(self, src: str) -> list[str]:
        """Every inventory Interface minus the Source's own Machine (Self)."""
        rows = self.rows()
        machine = next((r.get("name") or r["ip"] for r in rows if r["ip"] == src), src)
        return [r["ip"] for r in rows if (r.get("name") or r["ip"]) != machine]

    def scans(self) -> dict:
        rows = {r["ip"]: r for r in self.rows()}
        sets = self.groups()[0]
        out = []
        for ip in self.source_ips():
            d = self.file("scans") / ip
            files = [
                {"name": str(f.relative_to(d)), "excluded": f.parent != d}
                for f in sorted(d.rglob("*"))
                if f.is_file() and f.suffix.lower() in SCAN_EXT_PRIORITY
            ]
            r = rows.get(ip, {})
            out.append(
                {
                    "ip": ip,
                    "name": r.get("name", ""),
                    "zone": r.get("zone", ""),
                    "known": ip in rows,
                    "files": files,
                }
            )
        profiles = [
            {"name": p.name, "expected": sp.expected_files(p, sets)}
            for p in sp.read_profiles(self.text("scan_profiles.csv"))
        ]
        candidates = [
            {"ip": ip, "name": r.get("name", ""), "zone": r.get("zone", "")}
            for ip, r in rows.items()
            if ip not in self.source_ips()
        ]
        return {"sources": out, "profiles": profiles, "candidates": candidates}

    def source_dir(self, src: str) -> Path:
        ipaddress.ip_address(src)  # ValueError on anything else: no path tricks
        return self.file("scans") / src

    def add_source(self, src: str) -> None:
        if src not in {r["ip"] for r in self.rows()}:
            raise ValueError(f"{src} is not an inventory IP")
        self.source_dir(src).mkdir(parents=True, exist_ok=True)

    def upload(self, src: str, name: str, stream, length: int) -> str:
        name = Path(name).name
        if Path(name).suffix.lower() not in SCAN_EXT_PRIORITY or name.startswith("."):
            raise ValueError(f"{name}: expected an nmap output ({', '.join(SCAN_EXT_PRIORITY)})")
        d = self.source_dir(src)
        d.mkdir(parents=True, exist_ok=True)
        target = d / name
        if target.exists():
            raise ValueError(f"{name} already exists for {src}: rename it or exclude the old one first")
        tmp = d / f".{name}.part"
        with open(tmp, "wb") as fh:
            left = length
            while left > 0:
                chunk = stream.read(min(left, 1 << 20))
                if not chunk:
                    break
                fh.write(chunk)
                left -= len(chunk)
        os.replace(tmp, target)
        return name

    def move_scan(self, src: str, name: str, exclude: bool) -> None:
        d = self.source_dir(src)
        f = (d / name).resolve()
        if not f.is_relative_to(d.resolve()) or not f.is_file():
            raise ValueError(f"no such Scan {name}")
        dest = d / "excluded" / f.name if exclude else d / f.name
        if dest.exists():
            raise ValueError(f"{dest.relative_to(d)} already exists")
        dest.parent.mkdir(exist_ok=True)
        os.replace(f, dest)

    def script(self, src: str, profile: str) -> str:
        p = next((p for p in sp.read_profiles(self.text("scan_profiles.csv")) if p.name == profile), None)
        if p is None:
            raise ValueError(f"no Scan Profile {profile}")
        self.source_dir(src)
        r = next((r for r in self.rows() if r["ip"] == src), {})
        label = f"{src} ({r['name']})" if r.get("name") else src
        return sp.script(p, self.groups()[0], self.path.name, src, label, self.targets(src))

    def scripts_zip(self, profile: str) -> bytes:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for src in self.source_ips():
                info = zipfile.ZipInfo(f"segowl-{src}-{profile}.sh")
                info.external_attr = 0o755 << 16
                zf.writestr(info, self.script(src, profile))
        return buf.getvalue()

    # ---- client exchange
    def client_zip(self) -> bytes:
        return _zip({n: self.file(n) for n in ("inventory.csv", "flow_policy.csv") if self.file(n).is_file()})

    def mission_zip(self) -> bytes:
        files = {}
        for root, _, names in os.walk(self.path):
            for n in names:
                p = Path(root, n)
                files[str(p.relative_to(self.path))] = p
        return _zip(files)

    def import_client(self, blob: bytes, apply: bool) -> dict:
        """Check (and with apply=True write) the inventory and Flow Policy of a client zip."""
        try:
            zf = zipfile.ZipFile(io.BytesIO(blob))
            texts = {
                n: zf.read(n).decode("utf-8-sig", errors="replace")
                for n in ("inventory.csv", "flow_policy.csv")
                if n in zf.namelist()
            }
        except zipfile.BadZipFile:
            raise ValueError("Not a zip file") from None
        if "inventory.csv" not in texts:
            raise ValueError("The zip has no inventory.csv at its root")
        report = {}
        inv_err = mf.check_inventory(texts["inventory.csv"])
        n_rows = len(mf.read_inventory(texts["inventory.csv"])[1])
        report["inventory.csv"] = inv_err or f"{n_rows} Interface(s)"
        if "flow_policy.csv" in texts and not inv_err:
            report["flow_policy.csv"] = self._check_policy(texts["inventory.csv"], texts["flow_policy.csv"])
        errors = bool(inv_err) or report.get("flow_policy.csv", "").startswith("[!]")
        if apply and not errors:
            with LOCK:
                for n, t in texts.items():
                    write_file(self.file(n), t)
        return {"report": report, "ok": not errors, "applied": apply and not errors}

    def _check_policy(self, inv_text: str, pol_text: str) -> str:
        with LOCK:
            tmp_inv, tmp_pol = self.file(".import-inv.tmp"), self.file(".import-pol.tmp")
            groups_file = self.file("port_groups.csv")
            try:
                tmp_inv.write_text(inv_text, encoding="utf-8")
                tmp_pol.write_text(pol_text, encoding="utf-8")
                groups = load_port_groups(str(groups_file) if groups_file.is_file() else None)
                rules = load_policy(str(tmp_pol), load_inventory(str(tmp_inv)), groups)
                return f"{len(rules)} rule(s)"
            except SystemExit as e:
                return (
                    str(e.code)
                    .replace(str(tmp_pol), "flow_policy.csv")
                    .replace(str(tmp_inv), "inventory.csv")
                )
            finally:
                tmp_inv.unlink(missing_ok=True)
                tmp_pol.unlink(missing_ok=True)


def _zip(files: dict[str, Path]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for arc, p in files.items():
            zf.write(p, arc)
    return buf.getvalue()


# ---------------------------------------------------------------- pages
NAV = [
    ("mission", "Mission"),
    ("inventory", "Inventory & Zones"),
    ("policy", "Flow Policy"),
    ("profiles", "Scan Profiles"),
    ("scans", "Scans"),
    ("kits", "Kits"),
    ("report", "Report"),
]


def asset(name: str) -> str:
    return (ASSETS / name).read_text(encoding="utf-8")


def page(title: str, body: str, *, mission: Path | None = None, user="", active="", head="") -> bytes:
    nav = ""
    if mission is not None:
        links = "".join(f'<a href="/{k}" class="{"on" if k == active else ""}">{t}</a>' for k, t in NAV)
        nav = f"<nav>{links}</nav>"
    who = f'{html.escape(user)}<a href="/logout">log out</a>' if user else "local"
    where = ""
    if mission is not None:
        name, path = html.escape(mission.name), html.escape(str(mission))
        where = f'<div class="mission">Mission <b>{name}</b> · {path}</div>'
    return (
        f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f"<title>{html.escape(title)} · SegOWL</title>"
        '<link rel="icon" href="/static/logo.svg"><link rel="stylesheet" href="/static/app.css">'
        f"{head}</head><body>"
        f'<header><img src="/static/logo.svg" alt=""><div class="brand">Seg<b>OWL</b></div>{where}'
        f'<div class="user">{who if mission is not None else ""}</div></header>{nav}{body}'
        f'<div id="toast"></div></body></html>'
    ).encode()


def mission_body(m: Mission) -> str:
    gen = (
        f'<p class="err">{html.escape(m.error)}</p>'
        if m.error
        else f"<pre>{html.escape(chr(10).join(m.lines))}</pre>"
    )
    files = ", ".join(sorted(p.name for p in m.path.iterdir() if p.is_file() and not p.name.endswith(".tmp")))
    return f"""<main>
<div class="card"><b>Report generation</b>{gen}</div>
<div class="card"><b>Files</b><p class="small">{html.escape(files or "none")}</p></div>
<div class="card"><b>Exchange with the client</b>
  <p class="small muted">The client's part of a Mission is its inventory and Flow Policy.</p>
  <div class="toolbar"><a class="btn" href="/api/export/client.zip">Download client zip</a>
  <a class="btn" href="/api/export/mission.zip">Download the whole Mission</a><span class="sep"></span>
  <label class="btn">Import a client zip…<input type="file" id="imp" accept=".zip" hidden></label></div>
  <div id="impres"></div></div>
</main><script src="/static/app_mission.js"></script>"""


LOGIN_FORM = (
    '<main class="login"><div class="card"><h2>Sign in</h2>{err}'
    '<form method="post" action="/login">'
    '<label>Login<input type="text" name="login" autofocus required></label>'
    '<label>Password<input name="password" type="password" required></label>'
    "<button>Sign in</button></form></div></main>"
)


# ---------------------------------------------------------------- HTTP
def make_handler(mission: Mission, users_file: Path, secure: bool, allowed_hosts: set[str]):
    sessions: dict[str, str] = {}  # in memory: a restart signs everyone out

    class Handler(BaseHTTPRequestHandler):
        server_version = "SegOWL"
        user = ""

        def log_message(self, fmt, *args):
            sys.stderr.write(f"[{self.address_string()}] {fmt % args}\n")

        def _send(self, code: int, body: bytes, ctype="text/html; charset=utf-8", headers=()):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "SAMEORIGIN")
            self.send_header("Cache-Control", "no-store")
            for k, v in headers:
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        def _json(self, obj, code=200):
            self._send(code, json.dumps(obj).encode(), "application/json")

        def _redirect(self, to: str, headers=()):
            self._send(303, b"", headers=[("Location", to), *headers])

        def _auth_on(self) -> bool:
            return bool(load_users(users_file))

        def _user(self) -> str | None:
            """Signed-in login, '' when auth is off, None when a login is required."""
            if not self._auth_on():
                return ""
            c = http.cookies.SimpleCookie(self.headers.get("Cookie", ""))
            return sessions.get(c[COOKIE].value) if COOKIE in c else None

        def _host_ok(self) -> bool:
            # Without login, only answer to the address we listen on: blocks DNS rebinding from a web page.
            return self._auth_on() or self.headers.get("Host", "") in allowed_hosts

        def _page(self, title, body, active, head=""):
            self._send(200, page(title, body, mission=mission.path, user=self.user, active=active, head=head))

        def do_GET(self):
            if not self._host_ok():
                return self._send(421, b"unexpected Host header", "text/plain")
            url = urllib.parse.urlsplit(self.path)
            name = url.path.removeprefix("/static/")
            if name in STATIC:
                return self._send(200, (ASSETS / name).read_bytes(), STATIC[name])
            if url.path == "/login":
                return self._send(200, page("Sign in", LOGIN_FORM.format(err="")))
            user = self._user()
            if user is None:
                return self._redirect("/login")
            self.user = user
            if url.path == "/logout":
                c = http.cookies.SimpleCookie(self.headers.get("Cookie", ""))
                if COOKIE in c:
                    sessions.pop(c[COOKIE].value, None)
                return self._redirect("/login", [("Set-Cookie", f"{COOKIE}=; Max-Age=0; Path=/")])
            tabulator = '<link rel="stylesheet" href="/static/tabulator.min.css">'
            q = urllib.parse.parse_qs(url.query)

            def search(text):
                _, specs = mission.groups()
                return sp.search_ports(text, specs, sp.load_labels(mission.file("port_labels.csv")))

            routes = {
                "/api/inventory": lambda: self._json(mission.inventory()),
                "/api/export/client.zip": lambda: self._download("client.zip", mission.client_zip()),
                "/api/export/mission.zip": lambda: self._download(
                    f"{mission.path.name}.zip", mission.mission_zip()
                ),
                "/api/file/inventory.csv": lambda: self._download(
                    "inventory.csv", mission.text("inventory.csv").encode(), "text/csv; charset=utf-8"
                ),
                "/api/policy": lambda: self._json(mission.policy()),
                "/policy": lambda: self._page("Flow Policy", asset("policy.html"), "policy"),
                "/api/profiles": lambda: self._json(mission.profiles()),
                "/api/ports": lambda: self._json(search(q.get("q", [""])[0])),
                "/api/scans": lambda: self._json(mission.scans()),
                "/api/script": lambda: self._download(
                    f"segowl-{q.get('src', [''])[0]}-{q.get('profile', [''])[0]}.sh",
                    mission.script(q.get("src", [""])[0], q.get("profile", [""])[0]).encode(),
                    "text/x-shellscript; charset=utf-8",
                ),
                "/api/scripts.zip": lambda: self._download(
                    f"segowl-{q.get('profile', [''])[0]}.zip", mission.scripts_zip(q.get("profile", [""])[0])
                ),
                "/profiles": lambda: self._page("Scan Profiles", asset("profiles.html"), "profiles"),
                "/scans": lambda: self._page("Scans", asset("scans.html"), "scans"),
                "/kits": lambda: self._page("Kits", asset("kits.html"), "kits"),
                "/api/kits": lambda: self._json(mission.kits()),
                "/api/kits/export": lambda: self._download(
                    f"{q.get('name', ['kit'])[0]}.zip",
                    mission.kit_zip(q.get("dir", [""])[0], q.get("name", [""])[0]),
                ),
                "/inventory": lambda: self._page(
                    "Inventory",
                    (ASSETS / "inventory.html").read_text(encoding="utf-8"),
                    "inventory",
                    tabulator,
                ),
            }
            if url.path in routes:
                try:
                    return routes[url.path]()
                except ValueError as e:
                    return self._json({"error": str(e)}, 400)
            mission.refresh()
            if url.path in ("/", "/report"):
                body = '<iframe src="/report/report.html" title="Report"></iframe>'
                return self._page("Report", mission_body(mission) if mission.error else body, "report")
            if url.path == "/mission":
                return self._page("Mission", mission_body(mission), "mission")
            if url.path.startswith("/report/"):
                return self._static(mission.file("report"), urllib.parse.unquote(url.path[len("/report/") :]))
            self._send(404, page("Not found", "<main><p>Not found.</p></main>"))

        def _download(self, filename: str, data: bytes, ctype="application/zip"):
            self._send(200, data, ctype, [("Content-Disposition", f'attachment; filename="{filename}"')])

        def _static(self, root: Path, rel: str):
            target = (root / rel).resolve()
            if not target.is_relative_to(root.resolve()) or not target.is_file():
                return self._send(404, b"not found", "text/plain")
            types = {
                ".html": "text/html; charset=utf-8",
                ".csv": "text/csv; charset=utf-8",
                ".md": "text/markdown; charset=utf-8",
                ".mmd": "text/plain; charset=utf-8",
            }
            self._send(200, target.read_bytes(), types.get(target.suffix, "application/octet-stream"))

        def do_POST(self):
            if not self._host_ok():
                return self._send(421, b"unexpected Host header", "text/plain")
            url = urllib.parse.urlsplit(self.path)
            n = int(self.headers.get("Content-Length") or 0)
            if url.path == "/api/scans/upload":
                return self._upload(url, n)
            if n > MAX_BODY:
                return self._json({"error": "Upload too large"}, 413)
            body = self.rfile.read(n)
            if url.path == "/login":
                return self._login(body)
            if self._user() is None:
                return self._json({"error": "Signed out: sign in again"}, 401)
            if self.headers.get("X-SegOWL") != "1":  # a cross-site form cannot set it: CSRF guard
                return self._json({"error": "Missing X-SegOWL header"}, 403)
            try:
                if url.path == "/api/inventory":
                    return self._json({"fp": mission.save_inventory(json.loads(body))})
                if url.path == "/api/rename":
                    d = json.loads(body)
                    return self._json(
                        mission.rename(d.get("kind"), d.get("old"), d.get("new", ""), d.get("fp", {}))
                    )
                if url.path == "/api/parse/inventory":
                    free, rows = mf.read_inventory(body.decode("utf-8-sig", errors="replace"))
                    return self._json({"columns": free, "rows": rows})
                if url.path == "/api/policy":
                    return self._json(mission.save_policy(json.loads(body)))
                if url.path == "/api/profiles":
                    return self._json({"fp": mission.save_profiles(json.loads(body))})
                if url.path == "/api/profiles/preview":
                    return self._json(mission.preview(json.loads(body)))
                if url.path == "/api/scans/source":
                    mission.add_source(json.loads(body).get("ip", ""))
                    return self._json(mission.scans())
                if url.path == "/api/scans/move":
                    d = json.loads(body)
                    mission.move_scan(d.get("src", ""), d.get("name", ""), bool(d.get("exclude")))
                    return self._json(mission.scans())
                if url.path == "/api/kits/dirs":
                    dirs = [str(x) for x in json.loads(body).get("dirs", [])]
                    return self._json(mission.set_kit_dirs(dirs))
                if url.path == "/api/kits/import":
                    q = {k: v[0] for k, v in urllib.parse.parse_qs(url.query).items()}
                    return self._json(mission.kit_action("import", q, body))
                if url.path.startswith("/api/kits/"):
                    return self._json(mission.kit_action(url.path.rsplit("/", 1)[-1], json.loads(body)))
                if url.path == "/api/import/client":
                    return self._json(mission.import_client(body, apply="dry=1" not in url.query))
            except (Conflict, FileExistsError) as e:
                return self._json({"error": str(e), "exists": isinstance(e, FileExistsError)}, 409)
            except (ValueError, KeyError, TypeError, AttributeError) as e:
                return self._json({"error": str(e)}, 400)
            self._json({"error": "Not found"}, 404)

        def _upload(self, url, n: int):
            if self._user() is None:
                return self._json({"error": "Signed out: sign in again"}, 401)
            if self.headers.get("X-SegOWL") != "1":
                return self._json({"error": "Missing X-SegOWL header"}, 403)
            q = urllib.parse.parse_qs(url.query)
            try:
                with LOCK:
                    name = mission.upload(q.get("src", [""])[0], q.get("name", [""])[0], self.rfile, n)
                return self._json({"saved": name, **mission.scans()})
            except ValueError as e:
                self.close_connection = True  # the unread body must not be parsed as a next request
                return self._json({"error": str(e)}, 400)

        def _login(self, body: bytes):
            form = urllib.parse.parse_qs(body[:10_000].decode(errors="replace"))
            login, password = form.get("login", [""])[0], form.get("password", [""])[0]
            stored = load_users(users_file).get(login)
            if stored is None or not check_password(password, stored):
                err = '<p class="err">Wrong login or password.</p>'
                return self._send(401, page("Sign in", LOGIN_FORM.format(err=err)))
            token = secrets.token_urlsafe(32)
            sessions[token] = login
            flags = "; HttpOnly; SameSite=Strict; Path=/" + ("; Secure" if secure else "")
            self._redirect("/", [("Set-Cookie", f"{COOKIE}={token}{flags}")])

    return Handler


def is_loopback(host: str) -> bool:
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return host == "localhost"


def make_server(
    mission_dir: str,
    host="127.0.0.1",
    port=8000,
    config: Path | None = None,
    cert: str | None = None,
    key: str | None = None,
) -> ThreadingHTTPServer:
    config = config or Path.home() / ".config" / "segowl"
    users_file = config / "users"
    if not is_loopback(host) and not load_users(users_file):
        raise SystemExit(
            f"[!] Refusing to listen on {host} without authentication: create a user first "
            f"(segowl user add <login> --config {config})"
        )
    mission = Mission(Path(mission_dir).resolve(), config)
    ensure_skeleton(mission.path)
    allowed: set[str] = set()
    server = ThreadingHTTPServer((host, port), make_handler(mission, users_file, bool(cert), allowed))
    real_port = server.server_address[1]
    allowed.update(f"{h}:{real_port}" for h in {host, "127.0.0.1", "localhost", "[::1]"})
    if cert:
        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ctx.load_cert_chain(cert, key)
        server.socket = ctx.wrap_socket(server.socket, server_side=True)
    return server


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(prog="segowl")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sv = sub.add_parser("serve", help="Web app on a Mission folder (created if missing)")
    sv.add_argument("mission")
    sv.add_argument("--host", default="127.0.0.1", help="Listen address; non-loopback needs a users file")
    sv.add_argument("--port", type=int, default=8000)
    sv.add_argument("--cert", help="TLS certificate (PEM): serve HTTPS")
    sv.add_argument("--key", help="TLS private key (PEM)")
    sv.add_argument("--config", type=Path, help="Server config dir [~/.config/segowl]")
    us = sub.add_parser("user", help="Manage the users file")
    us.add_argument("action", choices=["add"])
    us.add_argument("login")
    us.add_argument("--config", type=Path, help="Server config dir [~/.config/segowl]")
    args = ap.parse_args(argv)
    config = args.config or Path.home() / ".config" / "segowl"
    if args.cmd == "user":
        pw = getpass.getpass(f"Password for {args.login}: ")
        if not pw or pw != getpass.getpass("Again: "):
            raise SystemExit("[!] Empty or mismatching passwords")
        add_user(config / "users", args.login, pw)
        print(f"[+] {args.login} saved in {config / 'users'}")
        return
    if bool(args.cert) != bool(args.key):
        raise SystemExit("[!] --cert and --key go together")
    server = make_server(args.mission, args.host, args.port, config, args.cert, args.key)
    scheme = "https" if args.cert else "http"
    auth = "login required" if load_users(config / "users") else "no login (loopback only)"
    if not args.cert and not is_loopback(args.host):
        print("[!] Plain HTTP on a network address: passwords travel in clear, use --cert/--key")
    print(
        f"[+] SegOWL on {scheme}://{args.host}:{args.port}/ · {auth} · Mission {Path(args.mission).resolve()}"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
