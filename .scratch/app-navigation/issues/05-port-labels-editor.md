# Port Labels editor and "+ label this port"

Status: done
Blocked by: 02, Port Label metadata (committed 17c3674)
Spec: ../spec.md

## What

Auditor Kit › Port Labels as in the prototype: grid `port;product;tags;vendor;cleartext`, first column "source" sortable; shipped rows grey and read-only with **Complete** (copies into the Mission; the copy replaces the shipped label: `load_labels` merges by port + product instead of appending); several services per port; **"+ New label" form** (port with autocompletion, product, tags, vendor, cleartext), an existing port + product refused with the way out; tags derived from the data (suggestions, "did you mean", new tags flagged, normalised on save; spec, "Tag vocabulary"); cleartext yes / no / empty; filters by text, tag, vendor, Mission rows only. "+ label this port" in the scan builder's port search opens the same form pre-filled.

## Acceptance

- a Mission row with the port + product of a shipped label replaces it in the port search (no duplicate)
- two products on one port stay two labels
- a 3-column `port_labels.csv` written by hand still loads and is rewritten without losing anything

## Comments

2026-11-04 done: `/kit/labels` (`labels.html`, `app_labels.js`), `GET/POST /api/labels`, `POST /api/labels/add`. `load_labels` merges by port + product (case aside): a Mission row replaces the shipped label in place, new labels come after. The server checks each row (one port token 1-65535, product required, cleartext yes / no / empty) and normalises tags; a rewrite keeps the file's `#` lines (moved under the header). The port autocomplete, tag input and new-label form live in `app_ports.js` (one `Ports` global), shared by Port Groups, Port Labels and the Scan Profiles search, which shows "+ label this port" for a typed port without a Port Label.
