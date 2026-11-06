# Auditor Kit

Your tooling, carried from Mission to Mission: **Scan Profiles**, **Port Groups** and **Port Labels**. A kit never
contains client data: no inventory, no Flow Policy, no Scan, no IP.

| | What it is | File |
|---|---|---|
| **Scan Profile** | A named nmap recipe: ports + options, no target. One ready-to-run command per Source. | `scan_profiles.csv` |
| **Port Group** | A named set of ports (`admin`, `db`, `web`…), usable in profiles and in the Flow Policy as `@admin`. | `port_groups.csv` |
| **Port Label** | A port described: product, vendor, tags (`admin`, `backup`, `oob`, `risky`…), cleartext. Helps find ports; filters nothing. | `port_labels.csv` |

## Scan Profiles

**Auditor Kit › Scan Profiles** lists the kit's recipes, each with what it is for. You build and adjust a scan
on the **Scans** page: when you change a profile there, it offers to save it as a new version.

## Port Groups

SegOWL ships `admin`, `directory`, `db`, `web` and `file` (grey rows). A Mission's `port_groups.csv`
(`group;ports`, e.g. `admin;22,3389,5985,udp:161`) replaces a group of the same name or adds new ones.

- Edit a shipped group's ports to replace it in this Mission; **Reset** brings the shipped one back.
- Renaming a group rewrites the Flow Policy and the Scan Profiles at once; a group still in use cannot be
  deleted.
- In the ports cell, type a port, a product (`winbox`), `udp:…` or `@group` to insert a copy of that group's
  ports.

In the report, the Port Group chips under the tabs restrict every view to the open flows on that group's
ports. Open `admin` ports are always in **bold**.

## Port Labels

2 700+ labels ship with SegOWL, IT and OT vendors. They feed the port search of the scan builder. **Complete**
copies a shipped label into this Mission to add a vendor, tags or cleartext; the copy replaces it. Several
services may share a port.

## Kits

**Auditor Kit › Kits** saves the Mission's three files as a kit, imports a kit zip, or reads kit folders.
Applying a kit shows a row-by-row diff with the Mission: you pick which of its files replace the Mission's.

!!! tip "Share your method with git"
    Every sub-folder of a kit folder is a kit. Point a kit folder at a private repo, `git pull` it, and the
    whole team runs the same method, improved version after version.
