# Flow Policy: selection, copy / paste, undo

Status: done
Blocked by: 01
Spec: ../spec.md

## What

In `/policy` (`policy.html`, `app_policy.js`), as validated in the prototype (ticket 01 Comments win over this text): spreadsheet selection on the Zone × Zone matrix, Ctrl+C / Ctrl+V and popover Copy / Paste here, paste replaces each target cell's rules (comments included), one cell fills the selection, a block keeps its shape from the active cell, an empty cell or Delete empties the targets, system clipboard as `ports;action;comment` lines, refused text changes nothing, toast and highlight after a paste. Undo / Redo for every change of the page (Ctrl+Z / Ctrl+Y and a button), in memory, each step saved like an edit. Exception rules are not copied or pasted.

## Acceptance

- copying "only @web then deny the rest" from one cell and pasting it on a whole row writes those two rules in every cell of the row, and nothing else, in `flow_policy.csv`; the CLI loads the file without error
- pasting a copied row onto another row reproduces it cell for cell
- Ctrl+Z after that paste brings `flow_policy.csv` back to its previous content; Ctrl+Y applies it again
- pasting garbage text shows a message and leaves the file untouched
- exception rules are untouched by any paste or Delete on the matrix
- keyboard only: select, copy, paste, undo work without the mouse

## Comments

2026-11-06 done: `app_policy.js` takes the prototype's selection (ranges; Shift+click / Shift+arrows extend, Ctrl+click and Ctrl+header add, corner / Ctrl+A all), copy / paste (`copySel`, `parseText`, `pasteClip`, `writeCells`), Delete (`emptySel`) and the history (`changed` pushes the rules before each change, `step` undoes / redoes and saves like an edit, bottom bar `#undobar`). The real save is untouched (fingerprints, server errors, 409). The port check is `Ports.tokOk` (`app_ports.js`, now loaded by `policy.html`), as the standard asks. `app.css`: frame per range, dashed amber copied cells, flash, `body.picking .pop` (clicks pass through the popover while Ctrl / Shift is held), bottom bar, and amber toasts for the whole app. Checked end to end in headless Chrome on a copy of the demo, with real mouse and key events and `flow_policy.csv` read from disk after each autosave: "only @web then deny the rest" copied onto the audit row writes the two rules in each of its 5 cells, and the CLI's `load_policy` reads the file (21 rules); the users row pasted on the admin row reproduces it; Ctrl+Z puts the file back, Ctrl+Y again; garbage and an unknown `@group` leave the file untouched with a toast; 3 Ctrl+clicked cells get a pasted cell, Delete empties them; Shift+arrow selection by keyboard; exception rules unchanged; Ctrl+Z all the way back gives the starting rules. No JS test harness in the repo: the check is a scratch script, not committed. Note: an open popover still covers the cells under it for a plain click (as before this ticket); Ctrl / Shift clicks go through.
