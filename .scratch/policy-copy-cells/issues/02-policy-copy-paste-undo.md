# Flow Policy: selection, copy / paste, undo

Status: ready-for-agent
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
