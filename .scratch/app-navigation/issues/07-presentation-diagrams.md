# Presentation diagrams as static SVG files, reused in the README

Status: ready-for-agent
Blocked by: 01
Spec: ../spec.md

## What

Turn the prototype's generated diagrams (round 4) into static SVG files under `segowl/assets/tutorial/`: Zone view, Source view, work process, Zone matrix, several Sources, retest, benefit icons. Each file stands alone: inline styles, its own white background (readable on GitHub's dark theme), system fonts, no script, no external reference (offline: see the report's constraint). The app's Overview (ticket 03) serves them under `/static/`; `README.md` shows the main ones with `<img src="segowl/assets/tutorial/…svg">` (as it already does for the logo), next to a short "Why SegOWL" section in the same words as the app.

## Acceptance

- the SVG files render identically in the app, in a browser opened on the file, and on GitHub (light and dark themes)
- the views match what the report draws (palette of `render/common.py`, edge colours of `render/mermaid.py`)
- no file loads anything external
