# Presentation diagrams as static SVG files, reused in the README

Status: done
Blocked by: 01
Spec: ../spec.md

## What

Turn the prototype's generated diagrams (round 4) into static SVG files under `segowl/assets/tutorial/`: Zone view, Source view, work process, Zone matrix, several Sources, retest, benefit icons. Each file stands alone: inline styles, its own white background (readable on GitHub's dark theme), system fonts, no script, no external reference (offline: see the report's constraint). The app's Overview (ticket 03) serves them under `/static/`; `README.md` shows the main ones with `<img src="segowl/assets/tutorial/…svg">` (as it already does for the logo), next to a short "Why SegOWL" section in the same words as the app.

## Acceptance

- the SVG files render identically in the app, in a browser opened on the file, and on GitHub (light and dark themes)
- the views match what the report draws (palette of `render/common.py`, edge colours of `render/mermaid.py`)
- no file loads anything external

## Comments

2026-11-04 done: 13 files in `segowl/assets/tutorial/` (zone-view, source-view, work-process, zone-matrix, several-sources, retest, seven `benefit-*` icons), rendered once from the prototype's round-4 generators by a throwaway script (not committed: the SVG files are the source now). Classes became inline `style`, fonts the system stack, each diagram has its own white rounded background; the only `url()` are the arrow markers inside the file. Served at `/static/tutorial/<name>.svg` (`image/svg+xml`, name checked by pattern) and shipped as package data. README gains the message, the three pillars, both views, the work process and a short "Why SegOWL" with the matrix and the retest. Checked: every file is well-formed XML (a raw `&` had broken work-process.svg), renders opened as a file and on a dark page; GitHub itself not checked from here.
