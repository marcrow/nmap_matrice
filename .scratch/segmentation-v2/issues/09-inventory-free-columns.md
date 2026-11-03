# Inventory free columns

Status: done
Blocked by: 05
Stage: Stage 1 (see ../spec.md)

## What

Inventory columns beyond ip;zone;type;name are kept and shown in tables, tooltips and later exports, with no logic. Header row required when more than 4 columns; clear error otherwise.

## Acceptance

- extra column visible in the report
- missing header with 5+ columns exits with an explicit message
