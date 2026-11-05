# Global zone diagram in Cytoscape, Mermaid out of the report

Status: ready-for-agent
Blocked by: 05, 06, 07
Spec: ../spec.md

## What

Draw the Global view zone → zone diagram in Cytoscape with the shared look, then remove `mermaid.min.js` from the report (about 3.3 MB less) and its loading code from `report.js`. The `.mmd` text exports written by `cli.py` (`segmentation.mmd`, per Source) stay: they need no JS and auditors paste them in documents.

## Acceptance

- `report.html` contains no Mermaid code and every diagram still renders offline
- the `.mmd` files are still written and their tests pass
