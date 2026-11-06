# Philosophy

## Why SegOWL

**Not another scanner.** nmap does the scanning, and does it well. SegOWL builds the nmap command, then reads
its results to give you what a pile of text files does not: visibility.

An internal segmentation test leaves thousands of nmap answers. Read them by hand and a Finding slips through
because a filter was missing or a grep was not run. SegOWL does not replace reading your nmap outputs: it adds
the global view and the filters that bring up what you would not have seen.

- **Rigour**: the same command from every Source, the whole inventory as targets, the Coverage of every port
  kept. Nothing forgotten, nothing to rerun.
- **Visibility**: one matrix and one diagram per Zone and per Source, Port Group filters across every view.
  The flows that should not exist stand out.
- **Restitution**: diagrams and matrices ready to drop into your pentest or audit report, and an offline HTML
  report on top.

## How to work with it

**Prepare, then scan.** The quality of the views depends on two inputs: a reliable inventory and the right
ports. Scanning before they are settled means scanning again.

**One command, identical everywhere.** Port Labels and Port Groups help you build the best command for this
environment; the app then runs it the same way from every Source. Two Sources compare because they ran the
same scan.

**Dig where it matters.** Add Scans at any time: a deeper scan of one Machine, extra ports for a product you
spotted. They combine into the Source View; nothing breaks.

**Step back.** Zone and Source views, matrices, Port Group filters: look for the flows that should not be
there, not for the lines in a file.

**A logical Flow Policy, adjusted Finding by Finding.** The client's flow matrix is often missing or too long
to transcribe. Write the policy a sane segmentation would have, then adjust it case by case as the Findings
come. Only an explicit deny makes a Finding, so a policy still being written never floods you with false ones.

**Retest and compare.** A fix, a new firewall rule: scan again and the **Diff** tab shows what changed, cell
by cell.

## Everything is configurable

Your method is yours. The port list is fully editable: add Port Labels (product, vendor, tags, cleartext),
create Port Groups, tune Scan Profiles, and carry them from Mission to Mission in an
[Auditor Kit](auditor-kit.md). SegOWL ships with 2 700+ labels, IT and OT; every audit can enrich them, and the
next command is better for it.
