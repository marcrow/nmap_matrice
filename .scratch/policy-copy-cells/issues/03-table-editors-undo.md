# Undo / redo in the table editors

Status: ready-for-agent
Blocked by: –
Spec: ../spec.md

## What

Undo / redo (Ctrl+Z / Ctrl+Y) in the Tabulator editors that save automatically, with Tabulator's `history` module (already in the vendored `tabulator.min.js`): Inventory first, then Port Groups and Port Labels. The Inventory's own paste handler (`app_inventory.js`, the `paste` listener) and its row add / delete must be undoable too. Each undo or redo saves like an edit. Same look for the Undo control as the one validated for the Flow Policy (ticket 01), if the prototype settles one before this ticket starts.

## Acceptance

- in the Inventory: edit a cell, paste a block of rows, delete a row; three Ctrl+Z bring `inventory.csv` back to its starting content; Ctrl+Y redoes
- the same for a cell edit in Port Groups and in Port Labels
- Ctrl+Z inside a cell being edited still undoes the typing, not the table

## Comments
