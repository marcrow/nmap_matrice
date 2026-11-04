# Overview page

Status: ready-for-agent
Blocked by: 02, 07
Spec: ../spec.md

## What

Replaces the Mission page and is the landing page. A **checklist** of the five steps with computed states and the next action (first step with a problem, else first not done); nothing new is stored (ADR-0003). The client exchange block. Below, the presentation as in the prototype's round 4: hero card (message + the two views, switchable), the six-step work process (optional steps dashed) and the same steps in words with links, then "Why SegOWL" and the benefit cards. Diagrams come from ticket 07's SVG files.

## Acceptance

- an empty Mission shows every step "not started" and points to the inventory first
- a broken input file (inventory, Flow Policy) shows its step as a problem with the CLI's message, the page still loads, and that step is the next one
- "same as kit X" appears only when the Mission's kit files match kit X byte for byte
