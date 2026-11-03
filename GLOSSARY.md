# Segmentation testing

Measures, from network scans launched inside the perimeter, which flows are actually allowed between segments, so the auditor can judge whether the intended segmentation holds.

## Language

### Perimeter

**Mission**:
One segmentation audit for a client: its inventory, its Scans, its optional Flow Policy and its Port Groups. The unit that is archived, copied and compared.
_Avoid_: engagement, project, audit

**Zone**:
Network segment declared by the auditor in the inventory, representing a segmentation intent, not an observed VLAN or subnet. An administration tier (T0, T1…) or an environment (admin, iLO, monitoring) is expressed as a Zone.
_Avoid_: VLAN, subnet, segment, tier, environment

**Machine**:
Physical or virtual device, identified by its name in the inventory, carrying one or more Interfaces.
_Avoid_: host, server, asset

**Interface**:
One IP of a Machine, attached to exactly one Zone. A Machine whose Interfaces sit in several Zones spans those Zones.
_Avoid_: alias, leg, secondary IP

**Flow Policy**:
The optional, auditor-supplied statement of which flows between Zones (and, by exception, Machines) are allowed or denied, possibly restricted to ports. Often absent: building it is time-consuming, and the tool must stay useful without it.
_Avoid_: rule, expected matrix, zone policy

**Undeclared Flow**:
Observed flow about which the Flow Policy says nothing. Shown apart, never a Finding.

### Scan

**Source**:
The IP a Scan is launched from. In practice it stands for its Machine, since system routing picks the outgoing Interface.
_Avoid_: pivot, origin, source host

**Scan Profile**:
Named, reusable recipe for a Scan: which ports (Port Groups, explicit ports, top-ports) and which nmap options. Carries no target: targets always come from the inventory, so a Scan Profile holds no client data. Exported as one ready-to-run command per Source, so every Source is scanned the same way.
_Avoid_: template, preset, scan config

**Port Label**:
Human description of a port (product, technology) with descriptive tags (admin, backup, oob…), used to find ports when building Port Groups and Scan Profiles. Purely descriptive: unlike a Port Group, it filters nothing and the Flow Policy cannot reference it.
_Avoid_: service, port category

**Auditor Kit**:
Named set of Port Groups, Scan Profiles and Port Labels that an auditor carries from Mission to Mission. Never contains client data (no inventory, no Flow Policy, no Scan, no IP).
_Avoid_: library, settings, config

**Scan**:
One nmap run from a Source, against a set of targets and a set of ports. A Source may have several Scans (e.g. a broad sweep then a targeted follow-up with extra ports); they are combined into its Source View.
_Avoid_: campaign, run, job

**Coverage**:
What was actually tested from a Source towards an Interface: which ports, by which Scans. Distinguishes "tested and not seen" from "never tested".
_Avoid_: scope

**Source View**:
Everything a Source sees, combining all its Scans. When Scans disagree on a port, the most permissive state wins (an open port observed once proves the flow passed), and the disagreement stays visible to the auditor.

**Self**:
All the Interfaces of the Machine carrying the Source. They are excluded from its own Scans.

**Scan Diff**:
Comparison of what two Scans, or two Source Views, observed, either over time (same Source, before/after) or across Sources (what one sees that the other does not). A difference on a port only one side tested is not comparable.
_Avoid_: delta, comparison

### Verdict

Verdict of a Source → Interface pair, from most permissive to most closed:

**OPEN**:
At least one open port: a service is reachable.

**REACHABLE**:
No open port but at least one closed port (RST received), or unfiltered in an ACK Scan (-sA): the L4 flow crosses the segmentation.

**ALIVE**:
The Interface answers host discovery (ping, ARP) but no port gets through, whether filtered or not tested. A lead: scan its ports deeper, or conclude none is open. Counts as passing in the zone matrix (`~`), never as BLOCKED. Does not exist in a -Pn Scan.
_Avoid_: host up, joinable, ICMP reachable (nmap discovery also uses ARP and TCP probes)

**BLOCKED**:
The Interface did not answer host discovery, or, in -Pn, only filtered ports. In -Pn, this does not distinguish filtering from a powered-off or nonexistent Interface.

**UNSEEN**:
The Interface is absent from the Scan output.

### Result

**Finding**:
Observed flow that the Flow Policy explicitly denies. Without a Flow Policy there are no Findings: the auditor reads the views.
_Avoid_: vulnerability, violation

**Pivot Machine**:
A Machine spanning at least two Zones that a Source reaches with an OPEN verdict: from the Source's Zone, it is a one-hop path to the Machine's other Zones.
_Avoid_: bastion, jump host, bridge

**Port Group**:
Named set of ports (e.g. admin, db, web) used to filter and highlight flows, and to express the Flow Policy.
_Avoid_: service class, port list
