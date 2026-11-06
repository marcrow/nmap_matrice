# Navigation shell and Auditor Kit tab

Status: done
Blocked by: 01
Spec: ../spec.md

## What

Main menu in audit order (Overview · Inventory & Zones · Auditor Kit · Scans · Flow Policy · Report). Auditor Kit as a **section header** (prototype variant C): "Auditor Kit ▾" opens a dropdown of its four screens with a one-line description each; the tab's pages open with a sticky header of four large tabs (name, count, description) and the line "this Mission's copies, never a kit folder · same as kit X". Hosts today's Scan Profiles editor and Kits page until tickets 06 and 03 move them. `/` lands on the Overview (today's Mission page until 03); `/mission`, `/profiles`, `/kits` redirect.

## Acceptance

- every existing screen is reachable in at most two clicks from any page
- old URLs redirect to the new ones
- the existing editors behave exactly as before (tests unchanged)

## Comments

2026-11-04 done: menu in audit order; "Auditor Kit ▾" opens on hover or keyboard focus (CSS only) and links `/kit/profiles`; the four tabs live under `/kit/<profiles|groups|labels|kits>`. `/mission` → `/`, `/profiles` → `/kit/profiles`, `/kits` → `/kit/kits`, `/kit` → `/kit/profiles` (303). The copies line names the kit whose files the Mission's equal (a kit file the Mission lacks makes it a partial match). Port Groups and Port Labels tabs show a "edited by hand" card until tickets 04 and 05. Review leftovers, not done: tab counts are shipped + Mission merged (04/05 may split them), redirects drop the query string (no caller passes one).
