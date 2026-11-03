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
import ipaddress
import os
import secrets
import ssl
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from segowl import cli

ASSETS = Path(__file__).parent / "assets"
LOCK = (
    threading.Lock()
)  # ponytail: one lock for report regeneration and saves, per-file locks if it ever bites
COOKIE = "segowl_session"
INVENTORY_HEADER = "ip;zone;type;name\n"


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


def save_file(path: Path, content: str, expected: str) -> str:
    """Write `content` only if the file still has the fingerprint the editor loaded; return the new one."""
    with LOCK:
        if fingerprint(path) != expected:
            raise Conflict(f"{path.name} was modified by someone else since you loaded it: reload.")
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, path)  # atomic: a reader never sees half a file
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
    def __init__(self, path: Path):
        self.path = path
        self.state: tuple | None = None
        self.lines: list[str] = []
        self.error = ""

    @property
    def report(self) -> Path:
        return self.path / "report"

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


# ---------------------------------------------------------------- pages
CSS = """
:root{--navy:#0B1F33;--navy2:#12304D;--cyan:#00C8FF;--amber:#FFB020;--slate:#6B7C93;--mist:#E6EDF5;
--bg:#EEF3F8;--ink:#1c2430;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-size:14px}
header{background:var(--navy);color:#fff;display:flex;align-items:center;gap:14px;padding:10px 18px}
header img{width:34px;height:34px}.brand{font-weight:700;font-size:19px}.brand b{color:var(--cyan)}
.mission{margin-left:18px;font-size:13px;opacity:.8}.user{margin-left:auto;font-size:12px;opacity:.8}
.user a{color:#cbd5e6;margin-left:8px}
nav{background:var(--navy2);display:flex;gap:2px;padding:0 10px}
nav a{color:#cbd5e6;text-decoration:none;padding:10px 14px;font-size:13px;border-bottom:3px solid transparent}
nav a:hover{color:#fff}nav a.on{color:#fff;border-bottom-color:var(--amber);font-weight:600}
nav span{color:#cbd5e6;opacity:.4;padding:10px 14px;font-size:13px}
main{padding:16px 18px}
.card{background:#fff;border:1px solid #d9e1ea;border-radius:10px;padding:14px 16px;margin-bottom:12px}
.err{background:#fde8e8;border:1px solid #f5b5b5;color:#8a1a1a;border-radius:8px;
padding:9px 12px;white-space:pre-wrap}
pre{font-size:12px;white-space:pre-wrap;margin:0}
iframe{width:100%;height:calc(100vh - 110px);border:0;display:block}
.login{max-width:340px;margin:12vh auto}.login input{width:100%;padding:8px 10px;margin:6px 0 10px;
border:1px solid #c3cad6;border-radius:6px;font-size:14px}.login button{width:100%;padding:9px;border:0;
border-radius:6px;background:var(--navy);color:#fff;font-size:14px;cursor:pointer}
"""
NAV = [
    ("mission", "Mission"),
    ("inventory", "Inventory"),
    ("zones", "Zones"),
    ("policy", "Flow Policy"),
    ("profiles", "Scan Profiles"),
    ("scans", "Scans"),
    ("kits", "Kits"),
    ("report", "Report"),
]
READY = {"mission", "report"}  # the other pages arrive with tickets 03-06


def page(title: str, body: str, *, mission: Path | None = None, user: str = "", active: str = "") -> bytes:
    nav = ""
    if mission is not None:
        nav = (
            "<nav>"
            + "".join(
                f'<a href="/{k}" class="{"on" if k == active else ""}">{t}</a>'
                if k in READY
                else f"<span>{t}</span>"
                for k, t in NAV
            )
            + "</nav>"
        )
    who = f'{html.escape(user)}<a href="/logout">log out</a>' if user else "local"
    where = (
        f'<div class="mission">Mission <b>{html.escape(mission.name)}</b> · {html.escape(str(mission))}</div>'
        if mission is not None
        else ""
    )
    return (
        f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f"<title>{html.escape(title)} · SegOWL</title>"
        f'<link rel="icon" href="/static/logo.svg"><style>{CSS}</style></head><body>'
        f'<header><img src="/static/logo.svg" alt=""><div class="brand">Seg<b>OWL</b></div>{where}'
        f'<div class="user">{who if mission is not None else ""}</div></header>{nav}{body}</body></html>'
    ).encode()


def mission_body(m: Mission) -> str:
    out = '<main><div class="card"><b>Report generation</b>'
    if m.error:
        out += f'<p class="err">{html.escape(m.error)}</p>'
    else:
        out += f"<pre>{html.escape(chr(10).join(m.lines))}</pre>"
    files = ", ".join(sorted(p.name for p in m.path.iterdir() if p.is_file())) or "none"
    return out + f'</div><div class="card"><b>Files</b><p>{html.escape(files)}</p></div></main>'


LOGIN_FORM = (
    '<main class="login"><div class="card"><h2 style="margin-top:0">Sign in</h2>{err}'
    '<form method="post" action="/login"><label>Login<input name="login" autofocus required></label>'
    '<label>Password<input name="password" type="password" required></label>'
    "<button>Sign in</button></form></div></main>"
)


# ---------------------------------------------------------------- HTTP
def make_handler(mission: Mission, users_file: Path, secure: bool):
    sessions: dict[str, str] = {}  # in memory: a restart signs everyone out

    class Handler(BaseHTTPRequestHandler):
        server_version = "SegOWL"

        def log_message(self, fmt, *args):  # quieter than the default, still on stderr
            sys.stderr.write(f"[{self.address_string()}] {fmt % args}\n")

        def _send(self, code: int, body: bytes, ctype="text/html; charset=utf-8", headers=()):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "no-store")
            for k, v in headers:
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        def _redirect(self, to: str, headers=()):
            self._send(303, b"", headers=[("Location", to), *headers])

        def _user(self) -> str | None:
            """Signed-in login, '' when auth is off, None when a login is required."""
            if not load_users(users_file):
                return ""
            c = http.cookies.SimpleCookie(self.headers.get("Cookie", ""))
            return sessions.get(c[COOKIE].value) if COOKIE in c else None

        def do_GET(self):
            url = urllib.parse.urlsplit(self.path)
            if url.path == "/static/logo.svg":
                return self._send(200, (ASSETS / "logo.svg").read_bytes(), "image/svg+xml")
            if url.path == "/login":
                return self._send(200, page("Sign in", LOGIN_FORM.format(err="")))
            user = self._user()
            if user is None:
                return self._redirect("/login")
            if url.path == "/logout":
                c = http.cookies.SimpleCookie(self.headers.get("Cookie", ""))
                if COOKIE in c:
                    sessions.pop(c[COOKIE].value, None)
                return self._redirect("/login", [("Set-Cookie", f"{COOKIE}=; Max-Age=0; Path=/")])
            mission.refresh()
            if url.path in ("/", "/report"):
                body = (
                    '<iframe src="/report/report.html" title="Report"></iframe>'
                    if not mission.error
                    else mission_body(mission)
                )
                return self._send(200, page("Report", body, mission=mission.path, user=user, active="report"))
            if url.path == "/mission":
                return self._send(
                    200,
                    page("Mission", mission_body(mission), mission=mission.path, user=user, active="mission"),
                )
            if url.path.startswith("/report/"):
                return self._static(mission.report, urllib.parse.unquote(url.path[len("/report/") :]))
            self._send(404, page("Not found", "<main><p>Not found.</p></main>"))

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
            if urllib.parse.urlsplit(self.path).path != "/login":
                return self._send(404, b"not found", "text/plain")
            n = int(self.headers.get("Content-Length") or 0)
            form = urllib.parse.parse_qs(self.rfile.read(min(n, 10_000)).decode())
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
    mission = Mission(Path(mission_dir).resolve())
    ensure_skeleton(mission.path)
    server = ThreadingHTTPServer((host, port), make_handler(mission, users_file, secure=bool(cert)))
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
