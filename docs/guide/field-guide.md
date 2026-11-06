# Field guide

Best practices for using SegOWL, step by step. How you run your engagement stays yours.

## Don't scan before this is reliable

!!! warning "The inventory and the ports first"
    An incomplete inventory or a port list that misses the client's products means running the Scans again.
    Settle both before the first Scan.

- **The inventory**: every Interface, in the Zone it is *meant* to be in. A target missing from the inventory
  is never scanned.
- **The ports**: search the Port Labels for what you know of the environment (`veeam`, `vmware`, `ilo`,
  `siemens`, `backup`, `oob`…). A product you know is there but cannot find? Add its label to your kit
  (**Auditor Kit › Port Labels**): it will be found on the next Mission too.
- **The Sources**: declare them all up front. A Source without a Scan shows as a gap of the Mission.

## Build the scan

- Start from a Scan Profile of your kit; tune it on **Scans**, then save it as a new version to keep the
  improvement.
- **Create a Port Group when it is reused**: in several profiles, in a kit, and above all **in the Flow
  Policy**, where `@admin` or `@backup` keeps a rule short and readable. To scan the ports of a search once,
  select the results instead.
- Keep `-Pn`, keep the XML output, never `--open` (see [Scanning](scanning.md#good-scans-make-good-views)).
- Fragile OT network: timing T2.
- Leave out `-n`: the names nmap resolves fill the inventory afterwards.

## On site

- Run the script the app generated, as is, from each Source: the same command everywhere is what makes the
  Sources comparable.
- Something deserves a closer look? Add a Scan to that Source (more ports, `-sV`, one target): it joins the
  Source View, nothing to redo.

## Names before the Flow Policy

Take the names from the Scans (**Inventory › Names from Scans**) **before** writing the Flow Policy:
Interfaces sharing a name become one Machine, the Pivot Machines appear, and rules are written against the
real Machines.

!!! tip "Forgot?"
    If a name would break a rule already written, **Rename everywhere** renames the Machine in the inventory
    and in the Flow Policy at once.

## A logical Flow Policy

Rather than transcribing the client's matrix, write the policy a sane segmentation would have, then adjust it
Finding by Finding. A starting point, to adapt to the Mission's Zones:

```
src;dst;ports;action;comment
users;servers;@web;allow;business applications
users;servers;*;deny;
users;admin;*;deny;users never reach the admin tier
admin;*;*;allow;administration
dmz;servers;@db;deny;the DMZ never reaches the databases directly
*;oob;*;deny;out-of-band only from admin
admin;oob;*;allow;
```

**Bootstrap from observed flows** fills the Zone pairs you observed with undecided rules: decide them one by
one, the undeclared flows shrink as you go.

## After the fix

Drop the new Scan next to the old one, in the Source's folder: the **Diff** tab compares any two Scans
or Source Views, cell by cell. A Scan that disagrees with the others? Move it to `excluded/` rather than
deleting it: it stays listed.
