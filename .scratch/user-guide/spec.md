# User guide: tips and tricks, best practices, philosophy

Status: done

Vocabulary: `GLOSSARY.md`. Raised by the user on 2026-11-05: as the app grows, the README is not enough; the auditor needs a real guide.

## Idea

A guide for the auditor (not the developer), with:

- **Philosophy**: why SegOWL works the way it does (rigour, visibility, quality of restitution; the Mission folder is the only state, ADR-0003; undeclared by default, ADR-0002; most permissive wins, ADR-0001).
- **Best practices**: what to do and what to avoid on a Mission.
- **Tips and tricks**: shortcuts and gestures that save time in the editors.

## Entries noted so far

- Create a Port Group only when it is really useful (reused across profiles, in the Flow Policy or in a kit). To scan the ports of a search once, select the results; do not make a group for it (see `.scratch/select-search-results/`).
- Flow Policy comments: a rule's comment is edited in the cell popover (click a cell of the Flow Policy matrix: each rule has its comment field); the matrix itself does not show comments. Noted 2026-11-06 while reviewing the report; whether the matrix should show them is left open.

- The audit path comes in two versions, as the user asked on 2026-11-06 (`inventory-names-from-scans`): a short one (the seven-step figure `work-process.svg`) and a detailed one (the Overview's step list); both include "Names from the Scans" between the Scans and the Flow Policy. The guide should keep the two in step.

## Decided (2026-11-06)

- Lives in `docs/` (Markdown readable on GitHub), published on GitHub Pages at https://marcrow.github.io/segowl/ by Zensical (`zensical.toml`, `.github/workflows/docs.yml`), no custom domain.
- The README is the short visual entry point (what, why, quick start with `git clone` + `python3 -m segowl`); the reference manual moved to `docs/guide/` (getting started, Mission folder, scanning, Auditor Kit, Flow Policy, report, lab).
- Part of the guide also lives in the app's Overview (offline on site); which part is for this grilling.
- Upkeep: every new or changed spec or ticket checks the docs and updates the pages it changes. Enforced by a project hook (`.claude/hooks/spec-doc-check.sh`, PostToolUse on `.scratch/*/spec.md` and `.scratch/*/issues/*.md`).
- Grilled 2026-11-06: `guide/philosophy.md` (why SegOWL: not another scanner, it reads nmap; how to work with it; everything is configurable), `guide/field-guide.md` (how to use the tool, not how to run an engagement: don't scan before the inventory and the ports are reliable, groups when reused above all in the Flow Policy, names before the Flow Policy or Rename everywhere, a logical Flow Policy adjusted Finding by Finding, Diff for retests), `guide/shortcuts.md`; the developer principles open `docs/adr/index.md`.
- The Overview shows one best practice per step of the detailed audit path, and a link to the guide (implemented directly, same layout: user's call).
- The demo opens with its names taken (`lab.py demo` fills empty names from DNS; mission-lab keeps them empty to try Names from Scans).
- Flow Policy comments in the matrix: not a docs subject, dropped from this spec.

## Questions for the grilling

- Where does it live: `docs/guide/*.md` in the repo, a page inside the app (offline, served by the local server), or both from the same source?
- What moves out of the README (Workflow, Port Groups, Flow Policy, Verdicts…), and what stays as a short entry point?
- How is it kept up to date: every spec that changes a gesture or a rule adds or updates its entry?
