# Flow Policy: "update the inventory first" modal

Status: ready-for-agent
Blocked by: 01, 02
Spec: ../spec.md

## What

On opening `/policy`, a styled modal (centred, dimmed background, closes on outside click / Escape / ✕, no browser dialog), buttons "Update the inventory →" and "Continue anyway", when the inventory has Interfaces and:

- (a) no Scan is imported: recommend running the Scans then taking the names; once per Mission;
- (b) the Scans still propose something: "N names and M IPs wait in the inventory"; on close, remember the proposal set in `localStorage` per Mission and show again only when a new proposal appears.

`localStorage` read / write wrapped in try / catch: without it the modal simply shows each time the condition holds.

## Acceptance

- (a) and (b) each shown once, then not again on reload; dropping a new Scan that brings a new name shows (b) again
- nothing shows on an inventory already up to date with the Scans

## Comments
