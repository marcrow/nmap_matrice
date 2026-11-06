# The lab

Run real scans without a client network. `lab/` simulates the demo company with Docker: one network per Zone,
one tiny container per Machine, a firewall applying `lab/flows.csv`, a DNS server for the names. The Sources run
the scripts the app generates, so the whole on-site flow can be tried end to end.

Needs Docker only, no root on the host.

```bash
python3 lab/lab.py up                              # ~15 s, writes mission-lab/inventory.csv
python3 -m segowl serve mission-lab/               # add the Sources 10.10.0.10, 10.20.0.50, 10.40.0.10
python3 lab/lab.py run ~/Downloads/segowl-<profile>.zip   # results in lab/out/scans/<Source>/
python3 lab/lab.py down
```

The Machines, Zones and planted cases are described in `lab/hosts.csv`, the firewall rules in `lab/flows.csv`:
change them and run `up` again. `python3 lab/lab.py demo` rebuilds the demo's Scans from the lab.
