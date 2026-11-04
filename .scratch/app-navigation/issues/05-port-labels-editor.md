# Port Labels editor and "+ label this port"

Status: ready-for-agent
Blocked by: 02, Port Label metadata (vendor, cleartext: work in progress, uncommitted on 2026-11-04)
Spec: ../spec.md

## What

Auditor Kit › Port Labels as in the prototype: grid `port;product;tags;vendor;cleartext`, first column "source" sortable; shipped rows grey and read-only with **Complete** (copies into the Mission; the copy replaces the shipped label: `load_labels` merges by port + product instead of appending); several services per port; **"+ New label" form** (port with autocompletion, product, tags, vendor, cleartext), an existing port + product refused with the way out; tags derived from the data (suggestions, "did you mean", new tags flagged, normalised on save; spec, "Tag vocabulary"); cleartext yes / no / empty; filters by text, tag, vendor, Mission rows only. "+ label this port" in the scan builder's port search opens the same form pre-filled.

## Acceptance

- a Mission row with the port + product of a shipped label replaces it in the port search (no duplicate)
- two products on one port stay two labels
- a 3-column `port_labels.csv` written by hand still loads and is rewritten without losing anything
