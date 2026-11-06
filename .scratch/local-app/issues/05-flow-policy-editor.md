# Flow Policy editor

Status: done
Blocked by: 03
Spec: ../spec.md

## What

Rule grid as validated in 01: dynamic dropdowns (Zones, Machines, Port Groups, `*`), port syntax validation, "bootstrap from observed flows" (observed_zone_flows draft). Writes `flow_policy.csv` in the existing format (ADR-0002 unchanged).

## Acceptance

- a rule on an unknown Zone is flagged inline
- bootstrap then save produces a file the CLI loads without error

## Comments

2026-11-04: built as prototype variant **B** (verdict in 01), not the rule grid: Zone × Zone matrix (click or Enter on a
cell: deny all / allow what's observed / undeclared / "only … then deny the rest" / per-rule edits) + an
exceptions panel for Machine, `*` and unknown names. Each rule is validated with the CLI's own loader and flagged
inline; a save is refused while any rule is flagged. "Bootstrap" adds one undecided rule (empty action, skipped by
the CLI) per observed Zone pair without a rule. Observed flows still show when the policy breaks the report.
Comment lines of a hand-edited file are kept but moved to the top.
