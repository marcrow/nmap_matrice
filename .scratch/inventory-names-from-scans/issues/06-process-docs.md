# Process: "Scans → names → Flow Policy" in the short and detailed audit path

Status: done
Blocked by: 03
Spec: ../spec.md

## What

The documented audit path gains the step "after the Scans, take the names into the inventory, then write the Flow Policy". Two versions, as the user asked: a short path (the steps at a glance) and a detailed one (each step explained). Touches the tutorial (`segowl/assets/tutorial/work-process.svg`, the Overview steps) and `.scratch/user-guide/`.

## Acceptance

- both versions show the step in the right place; the Overview checklist and the tutorial agree

## Comments

2026-11-06 done: short version = `work-process.svg`, now seven steps (5 "Names from the Scans", ⇄ DNS icon); detailed version = the Overview step list, new step "Take the names from the Scans" linking to `/inventory#names`; README (figure alt, Workflow step 2, Web app paragraph); Overview checklist: the Scans step adds "N empty name(s) resolved by the Scans: Inventory › Names from Scans"; `.scratch/user-guide/spec.md` notes the two versions.
