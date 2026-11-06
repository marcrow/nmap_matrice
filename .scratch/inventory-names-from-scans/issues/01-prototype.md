# Prototype: names-from-Scans panel, DNS badge, Scans line, Flow Policy modal

Status: done
Blocked by: –
Spec: ../spec.md

## What

Throwaway clickable HTML mockup, offline, app palette and `app.css`, fake data (the lab's size: about 6 Zones, 40 Interfaces, 3 Sources), on branch `prototype/inventory-names-from-scans`, like ticket 01 of `policy-copy-cells`:

- Inventory grid with the `DNS` badge (and its tooltip) next to the `n ifs` pill;
- the "Names from Scans" button and the inline panel: To fill (with merges), Conflicts (radio per candidate, "don't decide"), Skipped (reasons), Not in the inventory (checkboxes, all / none); the short / FQDN switch and its disambiguation; Apply as one undo step; running it again in the other mode;
- the Scans page line and its link that opens the panel;
- the Flow Policy modal, cases (a) and (b), and its "comes back only on a new proposal" rule (a control simulates new Scans).

Where a layout choice is open (panel layout, badge wording), offer two variants with a switcher.

## Acceptance

- the user goes through a fill, a conflict, a mode switch, an undo, an added IP and the modal, and gives a verdict on each
- no browser alert / prompt / confirm anywhere
- the verdicts are recorded in this ticket's Comments; they supersede the spec's wording

## Comments

2026-11-06 prototype ready: branch `prototype/inventory-names-from-scans` (worktree `../nmap_matrice-proto-names`), open `prototype_names/index.html` by double-click. Fake Mission of 30 Interfaces, 6 Zones, 3 Sources, covering every case: fw-01 merging into the auditor's `fw-01`, dc01.corp.local / dc01.lab.local keeping their FQDN in short mode, `DB-01.corp.local.` vs `db-01.corp.local` not a conflict, two real conflicts, `backup.corp.local` skipped in short mode (Zone name), a Machine named by the Flow Policy by IP (10.30.0.40) and by FQDN (files.corp.local) skipped, `jump-admin` typed by hand kept, 3 IPs not in the inventory (ALIVE / OPEN / REACHABLE). Switcher: panel A stacked sections vs B tabs; badge A `DNS` vs B `⇄ DNS` dashed. Controls: "No Scan imported yet" (modal case a), "Simulate a new Scan" (modal case b comes back), "Forget the modal's memory". Checked headless: fill 12 + conflict picked + 3 rows added (warning "3 row(s) without Zone"), Ctrl+Z back to 30 rows in one step, Ctrl+Y, FQDN re-run renames the 12 DNS names and keeps jump-admin, modal (b) once then not again, back after a new Scan, outside click / Escape close it, case (a). Found while testing and fixed in the spec: a DNS name in the other form counted as waiting, so the Scans line and the modal would have nagged forever; now only empty names, conflicts on empty names and missing IPs count. Waiting for the user's verdicts.

2026-11-06 user verdicts: "les pop-up géniales, très bien fait, process bien expliqué".
- **Panel: B tabs**: with many results it stays readable.
- **Badge: B `⇄ DNS`** dashed.
- **Skipped needs a way out on the row**: the user does not know where "Rename everywhere" is. Added: a Zone-name skip gets a "Use instead" field prefilled with the FQDN, applied with the rest (same undo step); a Flow Policy skip gets a name field and a "Rename everywhere" button renaming the Machine in the inventory and the Flow Policy at once, applied immediately, saying it is not undone by Ctrl+Z. Checked headless: a Zone name typed is refused ("still a Zone name"), `bkp-srv` applied with the rest, files.corp.local → files renamed on both Interfaces and in the Flow Policy, Skipped down from 4 to 2. Spec updated. Waiting for the user's look at the Skipped tab.

2026-11-06 user: "parfait". Ticket closed; tickets 02-06 build it, the prototype (variants B, Skipped way out) is the reference for layout and wording.
