# Port Labels editor and "+ label this port"

Status: needs-triage
Blocked by: 02, Port Label metadata (vendor, cleartext: work in progress, uncommitted on 2026-11-04)
Spec: ../spec.md

## What

Auditor Kit › Port Labels: grid `port;product;tags;vendor;cleartext`, shipped rows greyed and read-only, Mission rows editable; several services per port; completing a shipped label creates a Mission row with the same port + product that replaces it (`load_labels` merges by port + product instead of appending); tags with autocomplete from the tags in use, new tags accepted and flagged, near-duplicates suggested, normalised on save (spec, "Tag vocabulary"), cleartext yes / no / empty, port syntax validated inline; filters. "+ label this port" in the Scan Profiles port search opens a pre-filled row.

## Acceptance

- a Mission row with the port + product of a shipped label replaces it in the port search (no duplicate)
- two products on one port stay two labels
- a 3-column `port_labels.csv` written by hand still loads and is rewritten without losing anything
