# Copy cells of the Flow Policy matrix

Status: done

Vocabulary: `GLOSSARY.md` (Flow Policy, Port Group, Zone). Raised by the user on 2026-11-05 while filling the Flow Policy of the lab (`lab/`). Grilled on 2026-11-06.

## Problem

The same decision comes back in many cells, for example "deny the admin ports, allow the rest". Typing it again in each Zone × Zone cell makes filling in the Flow Policy very long. What exists today does not cover it:

- "Bootstrap from observed flows" fills each observed Zone pair without rules with undecided rules; it copies nothing between cells.
- The cell popover's quick actions (Deny all, Allow what's observed, Undeclared, Only … then deny the rest) replace one cell at a time.
- `*` rules do not help: the most specific rule wins, so `*;*;@admin;deny` loses to a Zone rule `allow *`.
- Edits save automatically (700 ms) and there is no undo, so a mass change cannot be taken back.

## Decisions

**Flow Policy editor (`/policy`, `app_policy.js`)**

- **Selection like a spreadsheet**, on the Zone × Zone matrix only: click or arrows move the active cell; Shift+click or Shift+arrows select a rectangle; Ctrl+click adds a cell (again drops it), Ctrl+click on a header adds a row or column; a click on a row or column header selects the whole row or column. A plain click still opens the popover; Ctrl+click and Shift+click never do, and pass through an open popover. Diagonal cells (same Zone) are selectable like any other.
- **Copy / paste**: Ctrl+C and Ctrl+V, plus "Copy" and "Paste here" in the cell popover for mouse users.
- **Paste replaces** the rules of each target cell, comments included (the comment explains the decision, so it travels with it).
- **Shapes**: one copied cell fills every selected cell; a copied block is pasted once with its shape at the top left of each range (each Ctrl+clicked cell), not tiled, and what would fall outside the matrix is dropped. Copy itself takes one cell or one rectangle.
- **Empty cells**: pasting an empty (undeclared) cell empties the targets; Delete or Backspace empties the selection.
- **System clipboard**: Copy writes text, one rule per line `ports;action;comment` (the `flow_policy.csv` columns without src and dst), and a block as `flow_policy.csv` lines `src;dst;ports;action;comment` under a `# SegOWL Flow Policy cells · rows: … · columns: …` header (prototype verdict); lines pasted straight from a `flow_policy.csv` are accepted too. Paste reads that text, so a decision can go from one Mission or tab to another, or come from a text editor. Text that does not parse is refused with a message and nothing changes.
- **Feedback**: after a paste, a toast "Pasted into N cells · Ctrl+Z to undo" and a brief highlight of the changed cells. The selection is drawn as a frame per range, the copied cells with a dashed amber frame. Toasts turn amber in the whole app (navy ones go unnoticed).
- **Undo for the whole page**: Ctrl+Z and the Undo button of a bottom bar ("Last change: …  Undo  Redo") undo the last change of any kind (paste, quick action, rule edited or removed, exception added, bootstrap), several levels deep; Ctrl+Y redoes. The history lives in memory only (lost on reload). Each undo or redo saves like any edit.
- **Not affected**: exception rules (on a Machine, on `*`, on a name the inventory no longer has) are neither copied nor pasted; they keep their own form. Undo covers them.

**Table editors (Tabulator)**

- Undo / redo (Ctrl+Z / Ctrl+Y) in the editors that save automatically: Inventory first, then Port Groups and Port Labels, with Tabulator's `history` module (in the vendored bundle). The Inventory's own paste handler (`app_inventory.js`) must feed the history too.

## Out of scope

- Named reusable decisions picked from a list ("no admin, rest allowed"): the clipboard covers the filling session. Revisit through the Kits if the prototype or later use shows the same two or three decisions copied from Mission to Mission.
- A fill handle to drag over cells.
- Copying exception rules.
- Undo that survives a reload.

## Tickets

- `issues/01-prototype.md`: throwaway prototype of the Flow Policy selection, copy / paste and undo, validated by the user.
- `issues/02-policy-copy-paste-undo.md`: the real thing in `/policy`.
- `issues/03-table-editors-undo.md`: undo / redo in Inventory, Port Groups, Port Labels.

## Done

2026-11-06: tickets 01 (prototype, verdicts recorded), 02 (Flow Policy), 03 (undo in every editor, through a shared `undoable` in `app_common.js` rather than Tabulator's `history`; see the ticket).
