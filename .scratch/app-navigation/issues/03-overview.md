# Overview page

Status: done
Blocked by: 02, 07
Spec: ../spec.md

## What

Replaces the Mission page and is the landing page. A **checklist** of the five steps with computed states and the next action (first step with a problem, else first not done); nothing new is stored (ADR-0003). The client exchange block. Below, the presentation as in the prototype's round 4: hero card (message + the two views, switchable), the six-step work process (optional steps dashed) and the same steps in words with links, then "Why SegOWL" and the benefit cards. Diagrams come from ticket 07's SVG files.

## Acceptance

- an empty Mission shows every step "not started" and points to the inventory first
- a broken input file (inventory, Flow Policy) shows its step as a problem with the CLI's message, the page still loads, and that step is the next one
- "same as kit X" appears only when the Mission's kit files match kit X byte for byte

## Comments

2026-11-04 done: `/` renders `overview_body()`: `Mission.overview()` computes the five rows from the folder on each load (nothing stored). Inventory: the CLI's loader (`load_inventory`) and the editor's check (`check_inventory`), Interfaces without Zone. Auditor Kit: profiles, Mission groups and labels, `port_groups.csv` parse error, "same as kit X" now compared byte for byte (a CRLF copy no longer matches). Scans: Sources with at least one Scan file. Flow Policy: the CLI's per-rule check (`rule_errors`), undecided rules. Report: "not started" until a Scan is in (an empty Mission keeps every row ○), then the generation error or the Findings / undeclared counts read from the CLI summary line. Next = first problem, else first not done. The presentation is static (`overview.html`) with the 07 SVG files; the Zone / Source switch is CSS only (radio). The old Mission page body remains only as the Report page's error view.
