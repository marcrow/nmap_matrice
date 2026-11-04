# Scan builder on Scans, Scan Profiles catalogue, profile description

Status: done
Blocked by: 02
Spec: ../spec.md

## What

Move today's Scan Profile editor (port search, options, command preview; local-app 04) onto the **Scans** page as step ① "Build the scan", above today's Sources grid (step ② "Run it from each Source"). The builder edits a draft of the chosen profile; when it differs from the saved one, a bar lists the changes and offers **Save as a new profile version…** (`<profile>-v2`, description "Variant of …" prefilled, original untouched), **Update `<profile>`** (warns when Scans were already imported for it) and **Discard**; a modified profile's scripts cannot be downloaded until saved. Auditor Kit › Scan Profiles becomes the **catalogue**: name, description edited in place, ports, options, Scans imported, Open in Scans / Duplicate / Delete / + New profile. `scan_profiles.csv` gains an optional 4th column `description`.

## Acceptance

- a 3-column `scan_profiles.csv` still loads; saving keeps descriptions and adds none that were not typed
- "Save as a new profile version" adds a profile and leaves the original byte-identical
- the script of a modified, unsaved profile cannot be downloaded
- applying a kit whose profiles carry descriptions shows them in the diff and the catalogue

## Comments

2026-11-04 done: the builder (`app_profiles.js`) is step ① of `/scans` and edits a draft; the profile picker is locked while the draft differs ("save or discard first"); the bar offers Save as a new profile version (name `<p>-v2` made unique, description "Variant of p: +x −y options changed"), Update (asks first when `imported` > 0) and Discard. While a profile is modified, its column in step ② shows no script link and the zip refuses it. `/scans?profile=<name>` opens a profile, `/scans?new=1` a new one (catalogue's + New profile). `/kit/profiles` is the catalogue (`app_catalogue.js`). `scan_profiles.csv` gets the 4th column only when a description exists; `/api/profiles` adds `imported` (Sources holding at least one Scan of the profile). The kit diff already showed every column, description included (test added).
