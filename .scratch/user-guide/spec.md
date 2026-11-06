# User guide: tips and tricks, best practices, philosophy

Status: needs-triage

Vocabulary: `GLOSSARY.md`. Raised by the user on 2026-11-05: as the app grows, the README is not enough; the auditor needs a real guide.

## Idea

A guide for the auditor (not the developer), with:

- **Philosophy**: why SegOWL works the way it does (rigour, visibility, quality of restitution; the Mission folder is the only state, ADR-0003; undeclared by default, ADR-0002; most permissive wins, ADR-0001).
- **Best practices**: what to do and what to avoid on a Mission.
- **Tips and tricks**: shortcuts and gestures that save time in the editors.

## Entries noted so far

- Create a Port Group only when it is really useful (reused across profiles, in the Flow Policy or in a kit). To scan the ports of a search once, select the results; do not make a group for it (see `.scratch/select-search-results/`).
- Flow Policy comments: a rule's comment is edited in the cell popover (click a cell of the Flow Policy matrix: each rule has its comment field); the matrix itself does not show comments. Noted 2026-11-06 while reviewing the report; whether the matrix should show them is left open.

## Questions for the grilling

- Where does it live: `docs/guide/*.md` in the repo, a page inside the app (offline, served by the local server), or both from the same source?
- What moves out of the README (Workflow, Port Groups, Flow Policy, Verdicts…), and what stays as a short entry point?
- How is it kept up to date: every spec that changes a gesture or a rule adds or updates its entry?
