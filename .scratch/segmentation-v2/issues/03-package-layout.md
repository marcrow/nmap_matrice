# Package layout

Status: ready-for-agent
Blocked by: 02
Stage: Stage 1 (see ../spec.md)

## What

Split `seg_matrix.py` into a package: parsers / model (Scan, Source View, verdicts) / render (md, mermaid, html) / cli. Add `pyproject.toml` (console script `seg_matrix`, dev extras pytest + ruff), type hints. Move the self-check to pytest. No behaviour change.

## Acceptance

- `ruff check` and `ruff format --check` clean
- `pytest` green
- `seg_matrix` entry point produces the same report as before
