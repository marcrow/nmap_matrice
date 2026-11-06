# Prototype: Flow Policy selection, copy / paste, undo

Status: ready-for-agent
Blocked by: –
Spec: ../spec.md

## What

Throwaway clickable HTML mockup of the Flow Policy matrix, offline, app palette, fake data (about 6 Zones, a few cells already decided, some observed ports), kept off the main line on branch `prototype/policy-copy-cells`, like ticket 01 of `app-navigation`:

- selection: active cell, Shift+click / Shift+arrows rectangle, row and column header click, visible selection style that does not hide the allow / deny / undecided colours;
- Ctrl+C / Ctrl+V and the popover's "Copy" / "Paste here"; one cell filling a selection, a block pasted with its shape;
- Delete / Backspace emptying the selection;
- the system clipboard text (`ports;action;comment` per line) and how a block is written; pasting text from outside, and a refused paste with its message;
- toast "Pasted into N cells · Ctrl+Z to undo" and the highlight of changed cells;
- Undo / Redo button and Ctrl+Z / Ctrl+Y across every kind of change.

Where a layout choice is open (place of the Undo button, how the selection and the copied cells are drawn, block text format), offer two variants with a switcher.

## Acceptance

- the user fills a Flow Policy of the lab's size with the mockup and gives a verdict on each gesture
- no browser alert / prompt / confirm anywhere
- the verdicts and the settled block format are recorded in this ticket's Comments; they supersede the spec's wording

## Comments
