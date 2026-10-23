# Open filtered is not open

Status: done
Blocked by: 01
Stage: Stage 0 (see ../spec.md)

## What

`classify` counts `open|filtered` as open (`seg_matrix.py:297`). Treat it as filtered: UDP no-reply and -sF/-sN/-sX scans must not produce OPEN.

## Acceptance

- a port in `open|filtered` alone yields BLOCKED
- test covering it
