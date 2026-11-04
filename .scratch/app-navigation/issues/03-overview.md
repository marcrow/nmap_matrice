# Overview page

Status: needs-triage
Blocked by: 02
Spec: ../spec.md

## What

Replaces the Mission page. Per step a computed state and the next action (nothing new is stored: ADR-0003), the client exchange block, the work-process tutorial. Details per the verdict of 01.

## Acceptance

- an empty Mission shows every step "not started" and points to the inventory first
- a broken input file (inventory, Flow Policy) shows ⚠ on its step with the CLI's message, the page still loads
- "same as kit X" appears only when the Mission's kit files match kit X byte for byte
