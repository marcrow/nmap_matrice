# Copy cells of the Flow Policy matrix

Status: needs-triage

Vocabulary: `GLOSSARY.md` (Flow Policy, Port Group, Zone). Raised by the user on 2026-11-05 while filling the Flow Policy of the lab (`lab/`).

## Idea

The same decision comes back in many cells, for example "deny the admin ports, allow the rest". Typing it again in each Zone × Zone cell makes filling in the Flow Policy very long. The user wants to copy a cell into other cells.

## Questions for the grilling

- Which gesture? Copy / paste (Ctrl+C on a cell, select several cells, Ctrl+V), a fill handle like a spreadsheet (drag over a row or a column), or "apply this cell to…" (the whole row, the whole column, every empty cell).
- Does pasting replace what a cell already holds or add to it, and is there an undo?
- Would named reusable decisions (e.g. "no admin, rest allowed"), picked from a list, save more time than copying?
- Is there an existing bootstrap in the editor (`app_policy.js`, "exceptions form, bootstrap") that could already cover part of this? Check before designing.
