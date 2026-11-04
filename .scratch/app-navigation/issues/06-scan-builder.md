# Scan builder on Scans, Scan Profiles catalogue, profile description

Status: ready-for-agent
Blocked by: 02
Spec: ../spec.md

## What

Move today's Scan Profile editor (port search, options, command preview; local-app 04) onto the **Scans** page as step ① "Build the scan", above today's Sources grid (step ② "Run it from each Source"). The builder edits a draft of the chosen profile; when it differs from the saved one, a bar lists the changes and offers **Save as a new profile version…** (`<profile>-v2`, description "Variant of …" prefilled, original untouched), **Update `<profile>`** (warns when Scans were already imported for it) and **Discard**; a modified profile's scripts cannot be downloaded until saved. Auditor Kit › Scan Profiles becomes the **catalogue**: name, description edited in place, ports, options, Scans imported, Open in Scans / Duplicate / Delete / + New profile. `scan_profiles.csv` gains an optional 4th column `description`.

## Acceptance

- a 3-column `scan_profiles.csv` still loads; saving keeps descriptions and adds none that were not typed
- "Save as a new profile version" adds a profile and leaves the original byte-identical
- the script of a modified, unsaved profile cannot be downloaded
- applying a kit whose profiles carry descriptions shows them in the diff and the catalogue
