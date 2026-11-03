# Package layout

Status: done
Blocked by: 02
Stage: Stage 1 (see ../spec.md)

## What

Split `segowl.py` into a package: parsers / model (Scan, Source View, verdicts) / render (md, mermaid, html) / cli. Add `pyproject.toml` (console script `segowl`, dev extras pytest + ruff), type hints. Move the self-check to pytest. No behaviour change.

## Acceptance

- `ruff check` and `ruff format --check` clean
- `pytest` green
- `segowl` entry point produces the same report as before
