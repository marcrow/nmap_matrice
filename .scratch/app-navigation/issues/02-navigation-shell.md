# Navigation shell and Auditor Kit tab

Status: ready-for-agent
Blocked by: 01
Spec: ../spec.md

## What

Main menu in audit order (Overview · Inventory & Zones · Auditor Kit · Scans · Flow Policy · Report). Auditor Kit as a **section header** (prototype variant C): "Auditor Kit ▾" opens a dropdown of its four screens with a one-line description each; the tab's pages open with a sticky header of four large tabs (name, count, description) and the line "this Mission's copies, never a kit folder · same as kit X". Hosts today's Scan Profiles editor and Kits page until tickets 06 and 03 move them. `/` lands on the Overview (today's Mission page until 03); `/mission`, `/profiles`, `/kits` redirect.

## Acceptance

- every existing screen is reachable in at most two clicks from any page
- old URLs redirect to the new ones
- the existing editors behave exactly as before (tests unchanged)
