# Inventory: "Names from Scans" panel and DNS badge

Status: done
Blocked by: 01, 02
Spec: ../spec.md

## What

In `/inventory` (`app_inventory.js`), as validated by the prototype (01):

- the button, the inline panel and its four tabs (To fill with merges, Conflicts, Skipped with reasons and a way out per row, Not in the inventory);
- Skipped: "Use instead" field for a Zone-name skip (applied with the rest); name field + "Rename everywhere" (`/api/rename`, check it accepts a Machine named by its IP) for a Flow Policy skip;
- short name (default) / FQDN switch, with FQDN kept when two different FQDNs share a short name;
- writes only empty names and names carrying the `DNS` badge; skips what would break the Flow Policy or equal a Zone name;
- Apply = one `changed(…)` step of `undoable`, then the usual autosave;
- the computed `⇄ DNS` badge (dashed) with its tooltip;
- opening with the panel unfolded from a link (e.g. `/inventory#names`).

## Acceptance

- on the demo Mission: fill, switch to FQDN and back by running the button again, Ctrl+Z restores the previous names in one step
- a conflict left on "don't decide" fills nothing; a chosen candidate fills it
- a name typed by hand survives every run
- a fill that would remove a Machine named by the Flow Policy is listed under Skipped and the Mission still loads
- added IPs appear without Zone and trigger the "row(s) without Zone" warning

## Comments

2026-11-06 done: shared computation `namesProposal` / `namesPending` / `namesWaiting` in `app_common.js` (one logic for the three pages); panel with the four tabs, short / FQDN switch, Skipped way out ("Use instead"; "Rename everywhere" through `renameEverywhere`), Apply = one `changed()` step, `⇄ DNS` badge, `/inventory#names` opens it; name column widened to 260 px so a FQDN and its badges fit. Found on the way and fixed: `/api/rename` did not rename a Machine named by its IP (empty name) in the inventory, while rewriting the Flow Policy (`mission_files.rename_in_inventory`, test `test_a_machine_named_by_its_ip_is_renamed_everywhere`). Checked in the real app on a copy of `demo/` with names emptied: 32 filled + 1 row added, saved, Ctrl+Z / Ctrl+Y, FQDN re-run (34 renamed), Rename everywhere on an IP-named Machine of the Flow Policy, the CLI loads the result.
