# Fill inventory names from the names resolved in the Scans

Status: ready-for-agent

Vocabulary: `GLOSSARY.md` (Interface, Machine, Scan, Source, Zone, Flow Policy, Pivot Machine, verdicts). Decisions: `docs/adr/0003` (Mission folder is the only state). Idea raised by the user on 2026-11-04 (out of the scope of `app-navigation`). Grilled on 2026-11-06.

## Problem

Auditors fill the `name` column of the inventory by hand, or leave it empty. An empty name makes each Interface its own Machine (named by its IP), so the Machines spanning several Zones, and with them the Pivot Machines, go unseen. Yet a Scan run with name resolution (nmap without `-n`) already carries the name of each target, and SegOWL throws it away: `segowl/nmap.py` reads no `<hostnames>`.

The Scans come after the inventory in the audit order (Inventory is the 2nd tab, Scans the 4th), so the names arrive when the auditor has left the Inventory; then the Flow Policy (5th tab) is written against Machines that are about to change.

## Decisions

**Reading the names (server)**

- The parser reads the name nmap reports, in the three formats: XML `<hostname name=… type=…>` (PTR preferred over `user`), gnmap `Host: ip (name)`, `.nmap` `Nmap scan report for name (ip)`. XML is the common case. Targets come from the inventory as IPs, so in practice the name is a PTR.
- Names are compared without case and without a trailing dot, and kept lower case without it (`DC01.Corp.local.` → `dc01.corp.local`).
- The API gives, per IP, the names each Source resolved, and the IPs found in the Scans but absent from the inventory, only those with a verdict ALIVE or better (a CIDR or `-Pn` Scan would otherwise bring hundreds of silent hosts). Nothing is stored: it is recomputed from the Mission's Scans (ADR-0003), and the names never go into a kit.

**Inventory editor (`/inventory`)**

- A toolbar button **"Names from Scans"** opens an inline panel above the grid (when nothing is to propose: a toast "No name to fill from the Scans"). Four **tabs** with a count each (prototype verdict: tabs stay readable with many results):
  1. **To fill**: `ip → name`, with the Machine merges it causes ("joins Machine `fw-01`, 3 Interfaces"; Self and the Pivot Machines may change). A name equal to an existing Machine's name joins it: the DNS name only proposes, the panel is that proposal.
  2. **Conflicts**: two Sources (or two Scans of one Source) resolved the IP to *different* names. One radio button per candidate with the Sources that saw it, plus "don't decide" (the default): not filled. A Source that resolved no name (`-n`, no PTR) is not a conflict.
  3. **Skipped**, each with its reason, written plainly, and a way out on the row itself (prototype verdict: the auditor does not know where "Rename everywhere" lives):
     - the name is a Zone's name: a field "Use instead", prefilled with the FQDN, editable; a valid name (not a Zone) is applied with the rest, inside the same undo step;
     - the fill would break the Flow Policy (it names the Machine that the IP or the current name stands for, and that Machine would disappear): a field prefilled with the proposed name and a "Rename everywhere" button that renames the Machine in the inventory and the Flow Policy at once (the existing `/api/rename`), applied immediately; the row says it is not undone by Ctrl+Z (undo stops there, as today).
  4. **Not in the inventory**: one checkbox per IP with its name (if any) and verdict, all / none. Rows are added without Zone and without type; the existing "row(s) without Zone" warning leads the auditor to sort them. The Zone is not guessed from the subnet: a Zone is an intent, not a subnet (GLOSSARY).
- **Short name or FQDN**: a switch in the panel, short name by default (FQDNs take too much room in the diagrams). In short mode, two different FQDNs giving the same short name (`dc01.corp.local`, `dc01.lab.local`) keep their FQDN, and the panel says so; identical FQDNs merge in both modes, which is what finds the Pivot Machines.
- **What the button may write**: empty names, and names carrying the `DNS` badge (still "owned" by the Scans), so running it again in the other mode converts them all at once, without Ctrl+Z nor 1000 hand edits. A name that differs from the DNS one (typed or changed by the auditor) is never touched. The Flow Policy rule above applies to replacements too.
- **Apply** is one undoable change (Ctrl+Z, the bottom bar), then the autosave writes `inventory.csv` like any edit. No new server write path; "Rename everywhere" is not involved.
- **`⇄ DNS` badge** (dashed outline, prototype verdict) in the name cell, next to the existing `n ifs` pill: computed, not stored. It shows when the name equals the resolved name (FQDN or short form); its tooltip gives the FQDN and the Sources. Editing the name away from it drops the badge by itself.

**Scans page (`/scans`)**

- One line, only when something waits: "N resolved names · M IPs not in the inventory · K conflicts to settle. Update the inventory →". The link opens the Inventory with the panel unfolded.
- **What "waits"** (this line and the Flow Policy modal): empty names to fill, conflicts on empty names, IPs not in the inventory. A `DNS` name in the other form (short / FQDN) is the auditor's choice, not news, so it never counts (otherwise one of the two modes would always nag). Conflicts alone do not bring the line back: "don't decide" is an answer.

**Flow Policy page (`/policy`)**

- A styled modal on opening (centred, dimmed background; closes on outside click, Escape or ✕; never a browser `alert`), with "Update the inventory →" and "Continue anyway", when the inventory has Interfaces and:
  - (a) no Scan is imported yet: it recommends running the Scans then taking the names from them; shown once per Mission;
  - (b) something still waits (as defined for the Scans line): "N names and M IPs wait in the inventory". On close, the set of proposals is remembered in `localStorage` per Mission; the modal comes back only when a **new** proposal appears (new Scans filling cells still empty, for example).
- `localStorage` is a per-browser display convenience, not Mission state (ADR-0003).

**Process documentation**

- The step "Scans → names into the inventory → Flow Policy" appears in the documented audit path, in a short and a detailed version (tutorial `work-process.svg`, `.scratch/user-guide/`).

## Out of scope

- A rule that picks a name among conflicting ones (most frequent, same-Zone Source): the auditor decides.
- Guessing the Zone or type of an IP added from the Scans.
- Rewriting the Flow Policy when a name changes ("Rename everywhere" stays the tool for that).
- Suggesting that two different names are one device: `.scratch/machine-identity/`.
- A button on the Scans page that writes the inventory from there, or anything in the report.
