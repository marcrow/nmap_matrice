# Report readability: matrices like the Flow Policy one, a diagram legend that explains itself

Status: needs-triage

Vocabulary: `GLOSSARY.md` (Finding, Flow Policy, Port Group, Zone). Raised by the user on 2026-11-05 while trying the app on the lab (`lab/`).

## Feedback

1. **The report's matrices are ugly**: align them with the Zone matrix of the Flow Policy editor (`/policy`, `app_policy.js`), which the user finds clean.
2. **The legend of the global diagram is hard to read**: you cannot tell why some port numbers are red and others black. When the user adds a deny for audit → dmz on the admin ports in the Flow Policy, the edge turns red, which reads as "blocked", because the red "blocked" chip comes first. You only understand the edge colours once you reach "denied (Finding)". The first part of the legend means nothing to the user.

## What the legend mixes today (`segowl/render/html.py` `_legend`, `segowl/render/mermaid.py`)

One line of chips, under every diagram, holds three separate codes:

- **Matrix cell states** (`v-open`, `v-reach`, `v-alive`, `v-block`, `v-none`, `conflict`): OPEN service / reachable (closed) / alive (ping/ARP) / blocked / unseen / Scans disagree. They colour the **matrix cells**, not the diagram, but they are shown above the diagram.
- **Edge colour = Flow Policy verdict** of the OPEN flows (only when a Flow Policy exists): red = denied (Finding), orange = undeclared, green = allowed. Without a Flow Policy: red = cross-zone OPEN, green = same-zone. Dashed edge = reachable, no open port.
- **Red bold port number in an edge label = a port of the highlighted Port Group (admin)** (`mermaid.py` line 36, "highlighted (admin) ports in red"). This code appears nowhere in the legend.

So red stands for three things (blocked cell, denied edge, admin port), and the colours of the diagram's edges are explained after the cell states, which do not apply to it.

## Questions for the grilling

- Should each view get its own legend (cell states under the matrices, edge verdicts and the admin port marker under the diagrams)?
- Which colour for the admin ports, so they no longer collide with red = Finding (bold with no colour, an icon, underline…)?
- Should "blocked" keep red now that red means Finding everywhere else?
- How close to the Flow Policy matrix should the report matrices be: same cell layout and colours, or only the same style (spacing, fonts, headers)? The report has to stay offline (`report.html` with no CDN, see memory) and readable when printed or pasted into an audit report.
- Same treatment for the Source diagrams and the per-Zone diagrams, or only the global one?
