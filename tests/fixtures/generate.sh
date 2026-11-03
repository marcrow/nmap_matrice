#!/usr/bin/env bash
# Regenerates the real nmap fixtures against throwaway Docker containers.
# Nothing from the host leaks into the outputs: -n (no DNS), relative output names,
# isolated network. The UDP scan needs root: the script asks sudo for that step only
# (SKIP_UDP=1 to skip it).
#
#   app   172.31.250.10  tcp/22 (nc), tcp/6379 (redis), tcp/8443 (nc), udp/161 (nc echo)
#   db    172.31.250.20  tcp/5432 (redis)
#   ghost 172.31.250.30  nothing there -> filtered
#   scans run from the host, i.e. the bridge gateway 172.31.250.1 (the Source)
set -euo pipefail

NET=segfx
IMG=redis:7-alpine
SRC=172.31.250.1
OUT="$(cd "$(dirname "$0")" && pwd)/mission/scans/$SRC"

cleanup() { docker rm -f segfx-app segfx-db >/dev/null 2>&1 || true; docker network rm $NET >/dev/null 2>&1 || true; }
trap cleanup EXIT
cleanup

docker network create --subnet 172.31.250.0/24 --gateway $SRC $NET >/dev/null
docker run -d --name segfx-app --network $NET --ip 172.31.250.10 $IMG sh -c '
  nc -lk -p 22 -e cat & nc -lk -p 8443 -e cat & nc -lk -u -p 161 -e cat &
  exec redis-server --protected-mode no' >/dev/null
docker run -d --name segfx-db --network $NET --ip 172.31.250.20 $IMG \
  redis-server --port 5432 --protected-mode no >/dev/null
sleep 2

mkdir -p "$OUT"
cd "$OUT"
rm -f ./*.xml ./*.gnmap ./*.nmap
# Broad sweep: 22 open, closed elsewhere, ghost filtered. -oA also gives the legacy .gnmap.
nmap -sT -Pn -n -p 1-1000 -oA broad 172.31.250.10 172.31.250.20 172.31.250.30 >/dev/null
rm -f broad.nmap
# Targeted follow-up with extra ports the broad sweep did not cover.
nmap -sT -Pn -n -p 5432,6379,8443 -oX targeted.xml 172.31.250.10 172.31.250.20 >/dev/null
# After a "fix": port 22 on app no longer listens (open -> closed, for merge and diff).
docker exec segfx-app sh -c 'pkill -f "nc -lk -p 22"' || true
sleep 1
nmap -sT -Pn -n -p 22 -oX after_fix.xml 172.31.250.10 >/dev/null
if [ "${SKIP_UDP:-0}" != 1 ]; then
  sudo nmap -sU -Pn -n -p 53,161 -oX udp.xml 172.31.250.10 172.31.250.20 >/dev/null
  sudo chown "$(id -u):$(id -g)" udp.xml
fi

for f in ./*.xml; do xmllint --noout --dtdvalid /usr/share/nmap/nmap.dtd "$f"; done
echo "[+] fixtures in $OUT: $(ls | tr '\n' ' ')"
