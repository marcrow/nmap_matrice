# Select every port of a search at once, kept readable in the profile

Status: done

Vocabulary: `GLOSSARY.md` (Port Group, Port Label, Scan Profile). Idea raised by the user on 2026-11-05, out of the scope of `app-navigation`; noted for later.

## Idea

In the port search of the scan builder (Scans › build the scan), typing e.g. `veeam backup` lists ~15 Veeam ports tagged backup. Today you click them one by one, and the profile ends up with a long list of numbers that nobody can read. A **Select all the results** button would add them all at once, and the profile would keep one readable token such as `@~veeam_backup` (a "simulated group") instead of the numbers.

## Notes for triage

- There is already a partial version: `search_ports` (`segowl/scan_profiles.py`) offers "all N ports tagged 'x'" when the query is exactly **one tag**. It adds the numbers literally, so readability is lost.
- A query with several words is a plain substring match on the product today. Checked on 2026-11-05: `veeam` returns 40 results, `veeam backup` only 7 (the products whose name contains "Veeam Backup"). The "Veeam B&R…" ports tagged backup are missed. Searching every word (AND across port, product, tags, vendor) comes first, otherwise "select all" selects the wrong set.
- The main question: should `@~veeam_backup` be **live** (a saved search resolved again each time scripts are generated) or **frozen** (the result set at the moment of the click)?
  - Live: readable, but the same profile scans other ports after a Port Labels or kit update, so the first test and the retest no longer match without anyone noticing. Also, the GLOSSARY says Port Labels "filter nothing" and the Flow Policy cannot reference them: a live `@~` token would make them select ports.
  - Frozen: **Save the results as a Port Group** (`@veeam_backup`) reuses what already exists: the Port Groups editor, `@` syntax in profiles and the Flow Policy, kits. It stays readable and reproducible. It needs no new token or syntax, only a button and a name prompt (prefilled from the query).
- Whatever the choice, show how many ports the token stands for and which ones (hover or expand), like Port Groups in the builder today.

## Decision (user, 2026-11-05)

No token, live or frozen, and no automatic Port Group. **Select all the results** only adds the port numbers the search returned to the profile, like clicking them one by one. Best practice: create a Port Group only when it is really useful (reused across profiles, in the Flow Policy or in a kit), by hand in the Port Groups editor. This rule belongs in the user guide (`.scratch/user-guide/`).

Scope:
1. A multi-word query matches **every word** (AND) across port, product, tags and vendor, so `veeam backup` also finds the "Veeam B&R…" ports tagged backup.
2. A **Select all the results** button adds every port of the current result list (Port Labels hits) at once; ports already in the profile are not added twice.
3. The existing "all N ports tagged 'x'" entry stays as it is.

## Done (2026-11-05)

- AND search across port, product, tags and vendor (`search_ports`).
- A first result **all · select all N ports listed ⚠ check them first** (plus the ranges it holds, e.g. `2500-3300`); N counts the ports once ranges are expanded. Not offered for a typed port (its completions) nor a tag (the "all N ports tagged" entry does it).
- When it is offered, every matching Port Label is listed (no 60-row cut), so what you add is what you see.
