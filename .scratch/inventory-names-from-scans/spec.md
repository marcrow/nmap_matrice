# Fill inventory names from the names resolved in the Scans

Status: needs-triage

Vocabulary: `GLOSSARY.md` (Interface, Machine, Scan, Source). Idea raised by the user on 2026-11-04, out of the scope of `app-navigation`; traced for later.

## Idea

When a Scan ran with name resolution (nmap without `-n`), its results carry the name of each target. For every inventory Interface whose `name` is empty, offer that name. A button in the Inventory editor ("Reload names from the Scans") fills the empty names again after new Scans arrive.

## Notes for triage

- Today the parser ignores names: `segowl/nmap.py` does not read `<hostnames>` (XML: `<hostname name=… type="PTR|user"/>`; gnmap: `Host: 10.0.0.1 (name)`). Reading them is the first step.
- Only empty names are filled; a name the auditor typed is never overwritten. Show what would be filled before writing (same pattern as the client zip import preview).
- A name groups Interfaces into a Machine (GLOSSARY): two Interfaces resolving to the same name become one Machine, which changes Self (script targets) and the Source View. The preview should say so.
- Several Sources may resolve the same IP differently (different DNS views per Zone): pick a rule (most frequent, or the Source in the same Zone) and show the conflict.
- PTR names are often FQDNs (`dc01.corp.local`): keep them as they are, or offer the short name.
- The names are the client's data: they stay in the Mission (ADR-0003), never in a kit.
