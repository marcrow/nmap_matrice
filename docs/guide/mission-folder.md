# The Mission folder

Everything for one engagement lives in one folder: the only state of SegOWL, easy to archive with the
engagement, to copy, to compare (see [ADR 0003](../adr/0003-mission-folder-is-the-only-state.md)).

```
mission/
  inventory.csv            ip;zone;type;name
  port_groups.csv          optional, overrides the default Port Groups
  flow_policy.csv          optional, the expected flows
  scans/<source_ip>/*.xml  any file name, one folder per Source
  report/                  generated
```

## The inventory

One line per **Interface**, `;` separated, optional header. In the app: **Inventory & Zones**, paste the client's
spreadsheet or edit the grid.

```
ip;zone;type;name
10.0.2.1;internal;vm;app-01
```

| Column | Meaning |
|---|---|
| `ip` | One Interface. A duplicate IP is an error. |
| `zone` | The segmentation **intent**: T0, users, DMZ, OOB… Not an observed VLAN or subnet. |
| `type` | Optional, snake_case: `vm`, `ilo`, `switch`… |
| `name` | Optional: the **Machine**. Interfaces sharing a name are one Machine. Without a name, the Machine is the IP. |

### Machines on several Zones

One row per Interface, the same name:

```
10.0.2.1;T1-service;vm;app-01
10.9.0.1;T0-admin;vm;app-01
10.8.0.1;ilo;ilo;app-01
```

A Machine spanning several Zones that a Source reaches is a **Pivot Machine**: a one-hop path from the
Source's Zone to its other Zones. The report lists them.

### Your own columns

Owner, criticality, OS, notes…: extra columns are allowed and shown in the report, with no logic attached. A
header line is then required to name them: `ip;zone;type;name;owner;criticality`.

## Names from the Scans

Without `-n`, nmap resolves the name of each target. Once the Scans are in, **Inventory › Names from Scans**
proposes them for the empty names (short name or FQDN, `⇄ DNS` badge), shows conflicts between Sources and
offers the IPs missing from the inventory.

!!! tip "Before the Flow Policy"
    Take the names first: Interfaces sharing a name become one Machine, the Pivot Machines appear, and the
    Flow Policy is written against the real Machines. Only empty names are filled, never yours. The Flow
    Policy page reminds you if names are waiting.

!!! note
    A name only proposes: one device may carry one name per network. Merging or splitting Machines stays
    your call, by renaming an Interface.
