# Undo / redo in the table editors

Status: done
Blocked by: –
Spec: ../spec.md

## What

Undo / redo (Ctrl+Z / Ctrl+Y) in the Tabulator editors that save automatically, with Tabulator's `history` module (already in the vendored `tabulator.min.js`): Inventory first, then Port Groups and Port Labels. The Inventory's own paste handler (`app_inventory.js`, the `paste` listener) and its row add / delete must be undoable too. Each undo or redo saves like an edit. Same look for the Undo control as the one validated for the Flow Policy (ticket 01), if the prototype settles one before this ticket starts.

## Acceptance

- in the Inventory: edit a cell, paste a block of rows, delete a row; three Ctrl+Z bring `inventory.csv` back to its starting content; Ctrl+Y redoes
- the same for a cell edit in Port Groups and in Port Labels
- Ctrl+Z inside a cell being edited still undoes the typing, not the table

## Comments

2026-11-06 done, with a change of means: not Tabulator's `history` module. It records only edits and row adds / deletes made through its own API, while the Inventory also changes through `row.update()` (paste, type-to-fill, Ctrl+D, fill handle), the Zones sidebar and the extra columns; "paste a block, then Ctrl+Z" would have failed. Instead the Flow Policy's snapshot history moved into `app_common.js` as `undoable(get, set)` (the bottom bar, Ctrl+Z / Ctrl+Y, a snapshot of the editor's state before each change), used by the four editors: Inventory (rows, Zones, extra columns; every `changed()` now names the change), Port Groups and Port Labels (this Mission's groups / labels), Flow Policy (its rules). Ctrl+Z inside a field or a cell being edited stays the browser's. A rename the server applies to several files (Zone or Machine renamed everywhere, a used Port Group renamed) clears the history: undo cannot cross it. Checked end to end in headless Chrome on a copy of the demo, files read from disk after each autosave: Inventory, an ip edited, two rows pasted, a row deleted, three Ctrl+Z give back `inventory.csv` step by step to the start, Ctrl+Y redoes; Ctrl+Z while typing in a cell keeps the editor open and the table untouched; Port Groups, a shipped group's ports edited (the Mission's replacement written), Ctrl+Z and Ctrl+Y; Port Labels, Complete (a Mission row written), Ctrl+Z and Ctrl+Y; the Flow Policy checks of ticket 02 still pass. Seen while testing: text sent with CDP `Input.insertText` into a Tabulator list editor (type, name, zone) is dropped on Enter, real key presses keep it; a headless artifact, not an app bug.
