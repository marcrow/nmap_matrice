# Navigation shell and Auditor Kit tab

Status: needs-triage
Blocked by: 01
Spec: ../spec.md

## What

Main menu in audit order (Overview · Inventory & Zones · Auditor Kit · Scans · Flow Policy · Report), Auditor Kit tab with its sub-navigation hosting today's Scan Profiles and Kits pages, `/` lands on the Overview, old URLs (`/mission`, `/profiles`, `/kits`) redirect. Final layout per the verdict of 01.

## Acceptance

- every existing screen is reachable in at most two clicks from any page
- old URLs redirect to the new ones
- the existing editors behave exactly as before (tests unchanged)
