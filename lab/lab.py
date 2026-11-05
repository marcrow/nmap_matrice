#!/usr/bin/env python3
"""SegOWL lab: a simulated multi-Zone network in Docker, to try the app end to end.

    python3 lab/lab.py up [--mission mission-lab]    start the network, write the client inventory
    python3 lab/lab.py run segowl-<profile>.zip ...  run the app's scripts inside their Source containers
    python3 lab/lab.py down
    python3 lab/lab.py demo                         rebuild demo/ (inventory and Scans) from the running lab

hosts.csv describes the Machines, flows.csv what the firewall lets through between Zones. Each
Zone is a Docker network, each Machine a container listening with busybox nc, fw-01 routes and
filters with iptables, dns-01 serves the PTR records with dnsmasq. Sources resolve through dns-01,
so a profile without -n gets real names. Nothing touches the host network but the Docker bridges.
"""

from __future__ import annotations

import argparse
import csv
import ipaddress
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

LAB = Path(__file__).resolve().parent
TAG = "segowl-lab"  # image, container/network prefix and cleanup label


def rows(name: str) -> list[dict[str, str]]:
    with open(LAB / name, newline="", encoding="utf-8") as fh:
        lines = [line for line in fh if line.strip() and not line.startswith("#")]
    return list(csv.DictReader(lines, delimiter=";"))


def docker(*args: str, stdin: str | None = None, check: bool = True) -> str:
    r = subprocess.run(["docker", *args], input=stdin, text=True, capture_output=True)
    if check and r.returncode:
        sys.exit(f"docker {' '.join(args[:4])}: {r.stderr.strip()}")
    return r.stdout


def ports(spec: str) -> list[str]:
    return [p for p in spec.split(",") if p]


def firewall(hosts: list[dict[str, str]], subnets: dict[str, str]) -> list[str]:
    sh = ["iptables -P FORWARD DROP", "iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT"]
    for f in rows("flows.csv"):
        where = "".join(f" -{flag} {subnets[f[col]]}" for flag, col in (("s", "from"), ("d", "to")) if f[col] != "*")
        if f["ports"] == "all":
            matches = [" -p tcp", ""]
        else:
            matches = [
                f" -p {proto} --dport {port.replace('-', ':')}"
                for part in f["ports"].split()
                for proto, _, plist in [part.partition(":")]
                for port in ports(plist)
            ]
        for m in matches:
            jump = {"accept": "ACCEPT", "drop": "DROP"}.get(f["action"])
            if jump is None:  # reject: a TCP reset reads as closed, like a host with nothing listening
                jump = "REJECT --reject-with tcp-reset" if m.startswith(" -p tcp") else "REJECT"
            sh.append(f"iptables -A FORWARD{where}{m} -j {jump}")
    return sh


def up(mission: str) -> None:
    down()
    hosts = rows("hosts.csv")
    subnets = {h["zone"]: str(ipaddress.ip_network(f"{h['ip']}/24", strict=False)) for h in hosts}
    gateway = {h["zone"]: h["ip"] for h in hosts if h["role"] == "router"}
    dns_ip = next(h["ip"] for h in hosts if h["role"] == "dns")
    print("[*] building the image")
    docker("build", "-q", "-t", TAG, str(LAB))
    for zone, net in subnets.items():
        docker("network", "create", "--label", TAG, "--subnet", net, f"{TAG}-{zone}")
    machines: dict[str, list[dict[str, str]]] = {}
    for h in hosts:
        machines.setdefault(h["machine"], []).append(h)
    for name, ifaces in machines.items():
        role = ifaces[0]["role"]
        if role == "down":
            continue
        tcp = sorted({p for i in ifaces for p in ports(i["tcp"])}, key=int)
        udp = sorted({p for i in ifaces for p in ports(i["udp"])}, key=int)
        sh = []
        if role == "router":
            sh += firewall(hosts, subnets)
        else:
            sh.append(f"ip route replace default via {gateway[ifaces[0]['zone']]}")
        if role == "dns":
            records = " ".join(f"--host-record={h['dns']},{h['ip']}" for h in hosts if h["dns"])
            # --interface lifts dnsmasq's default of answering only its own subnet
            sh.append(f"dnsmasq --no-resolv --no-hosts --interface=eth0 {records}")
            tcp, udp = [p for p in tcp if p != "53"], [p for p in udp if p != "53"]
        if role == "source":
            sh.append(f"echo nameserver {dns_ip} > /etc/resolv.conf")
        sh += [f"nc -lk -p {p} -e cat &" for p in tcp] + [f"nc -lk -u -p {p} -e cat &" for p in udp]
        sh.append("exec tail -f /dev/null")
        first, *others = ifaces
        docker(
            "create", "--name", f"{TAG}-{name}", "--hostname", name, "--label", TAG,
            "--cap-add", "NET_ADMIN",
            "--sysctl", f"net.ipv4.ip_forward={int(role == 'router')}",
            # a Machine on two Zones answers from the other Interface: keep that reply instead of dropping it
            "--sysctl", "net.ipv4.conf.all.rp_filter=0", "--sysctl", "net.ipv4.conf.default.rp_filter=0",
            "--network", f"{TAG}-{first['zone']}", "--ip", first["ip"],
            TAG, "sh", "-c", "\n".join(sh),
        )  # fmt: skip
        for i in others:
            docker("network", "connect", "--ip", i["ip"], f"{TAG}-{i['zone']}", f"{TAG}-{name}")
        docker("start", f"{TAG}-{name}")  # every Interface attached first: the start script sets the route
    inventory = Path(mission) / "inventory.csv"
    if inventory.exists():
        print(f"[=] {inventory} kept as is")
    else:
        write_inventory(inventory)
    sources = ", ".join(f"{h['ip']} ({h['machine']})" for h in hosts if h["role"] == "source")
    print(f"[+] {len(machines)} Machines in {len(subnets)} Zones. Sources: {sources}")
    print(f"    python3 -m segowl serve {mission}   then   python3 lab/lab.py run segowl-<profile>.zip")


def write_inventory(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["ip;zone;type;name"] + [f"{h['ip']};{h['zone']};{h['type']};{h['name']}" for h in rows("hosts.csv")]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[+] client inventory: {path}")


def demo() -> None:
    """demo/ keeps its hand-written scan_profiles.csv and flow_policy.csv; inventory and Scans are redone
    by running, from every lab Source, the scripts the app itself generates for the first profile."""
    if not docker("ps", "-q", "--filter", f"label={TAG}").strip():
        sys.exit("the lab is not running: python3 lab/lab.py up")
    sys.path.insert(0, str(LAB.parent))
    from segowl.app import Mission
    from segowl.scan_profiles import read_profiles

    out = LAB.parent / "demo"
    write_inventory(out / "inventory.csv")
    for f in (out / "scans").glob("*/**/*"):
        if f.is_file():
            f.unlink()
    for h in rows("hosts.csv"):
        if h["role"] == "source":
            (out / "scans" / h["ip"]).mkdir(parents=True, exist_ok=True)
    mission = Mission(out)
    profile = read_profiles(mission.text("scan_profiles.csv"))[0].name
    with tempfile.TemporaryDirectory() as tmp:
        z = Path(tmp) / "scripts.zip"
        z.write_bytes(mission.scripts_zip(profile))
        run([str(z)], str(out))


def run(files: list[str], into: str) -> None:
    scripts = []
    for f in map(Path, files):
        if f.suffix == ".zip":
            with zipfile.ZipFile(f) as z:
                scripts += [(Path(n).name, z.read(n).decode()) for n in z.namelist() if n.endswith(".sh")]
        else:
            scripts.append((f.name, f.read_text(encoding="utf-8")))
    machine = {h["ip"]: h["machine"] for h in rows("hosts.csv") if h["role"] != "down"}
    for name, text in scripts:
        m = re.search(r"· Source (\S+)", text)  # header written by segowl.scan_profiles.script
        src = m.group(1) if m else None
        if src not in machine:
            print(f"[!] {name}: Source {src} is not a running lab Machine, skipped")
            continue
        c = f"{TAG}-{machine[src]}"
        docker("exec", "-i", c, "sh", "-c", f"rm -rf /work && mkdir /work && cat > /work/{name}", stdin=text)
        print(f"[*] {src} ({machine[src]}): {name}", flush=True)
        if subprocess.run(["docker", "exec", c, "sh", f"/work/{name}"]).returncode:
            print(f"[!] {name} failed")
            continue
        out = Path(into) / "scans" / src
        out.mkdir(parents=True, exist_ok=True)
        docker("cp", f"{c}:/work/scans/{src}/.", str(out))
        print(f"[+] {out}: {', '.join(sorted(p.name for p in out.iterdir() if p.is_file()))}")


def down() -> None:
    if ids := docker("ps", "-aq", "--filter", f"label={TAG}").split():
        docker("rm", "-f", *ids)
    if nets := docker("network", "ls", "-q", "--filter", f"label={TAG}").split():
        docker("network", "rm", *nets)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("up").add_argument("--mission", default="mission-lab", help="where to write inventory.csv")
    r = sub.add_parser("run")
    r.add_argument("files", nargs="+", help="scripts zip from the app, or .sh files")
    r.add_argument("--into", default=str(LAB / "out"), help="results go in <into>/scans/<Source>/ (a Mission works)")
    sub.add_parser("down")
    sub.add_parser("demo")
    a = ap.parse_args()
    {"up": lambda: up(a.mission), "run": lambda: run(a.files, a.into), "down": down, "demo": demo}[a.cmd]()


if __name__ == "__main__":
    main()
