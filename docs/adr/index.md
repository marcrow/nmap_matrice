# Design decisions

How SegOWL is built, and why. For contributors and the curious; the auditor's side is in the
[philosophy](../guide/philosophy.md).

- **The Mission folder is the only state.** No database: the folder is archived, copied, versioned and compared
  with the engagement. Edit it by hand or from the app, the report follows. ([0003](0003-mission-folder-is-the-only-state.md))
- **Runs anywhere, offline.** Python standard library only, no install step; the report is one self-contained
  HTML file, its diagram library inlined. ([0004](0004-local-app-on-the-standard-library.md),
  [0005](0005-cytoscape-for-network-diagrams.md))
- **Facts are never hidden.** An open port seen once proves the flow passed; Scans that disagree stay visible.
  ([0001](0001-source-view-most-permissive-wins.md))
- **The auditor decides.** Only an explicit deny makes a Finding; a name from DNS or a Scan only proposes.
  ([0002](0002-flow-policy-undeclared-by-default.md))
- **No client data in a kit.** Scan Profiles carry no target, kits carry no inventory, policy or IP: a method
  can be shared safely.

Each record below states the context, the decision and when to revisit it.
