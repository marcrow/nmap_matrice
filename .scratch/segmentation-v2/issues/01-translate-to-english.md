# Translate to english

Status: done
Stage: Stage 0 (see ../spec.md)

## What

Translate code identifiers, comments, CLI messages, README and HTML report to English. `NON-VU` becomes `UNSEEN`, `nom` becomes `name` (accept both CSV headers). No behaviour change.

## Acceptance

- `python3 test_seg_matrix.py` passes
- no French left in code, README or report output
- report on the same inputs is identical apart from wording
