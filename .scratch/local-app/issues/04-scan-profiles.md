# Port reference, Scan Profile editor, export scripts, Scans

Status: done
Blocked by: 03
Spec: ../spec.md

## What

Ship trimmed IANA extract (CC0). Port search over Port Groups, Port Labels (shipped + mission), IANA. Scan Profile editor as validated in 01; `scan_profiles.csv` (`name;ports;options`, `top:N`), option deny list. Export one `.sh` per Source and Profile (targets = inventory minus Self, `-oA scans/<src_ip>/<profile>`) + raw command. Progress grid Source × Profile by file presence; XML drag-and-drop per Source; exclude/re-include via `excluded/`.

## Acceptance

- a profile with `--exclude` or `-iL` is refused
- the exported command for a multi-interface Machine excludes all its Interfaces
- dropping an XML on a Source turns its cell ✓ and the report includes it

## Comments

2026-11-03 (from prototype 01): nmap combines `--top-ports N` with `-p` by taking the top N *within* the `-p` list, not the union. A profile mixing `top:N` with explicit ports must expand top:N to an explicit list (needs a port ranking we don't ship, see NPSL) or emit two commands. Decide before building.

2026-11-03, verified on the local nmap: `--top-ports 10 -p 22,2222,9392` scans only 22,2222 (silent intersection). Prototype answer: a profile with both top:N and explicit ports exports two Scans, `<profile>-top<N>` and `<profile>-ports`, merged by the existing Source View; the progress grid must expect both files. UDP goes with the explicit-ports scan only.
User feedback on the prototype: Port Groups as checkboxes, a dedicated "top ports" control, TCP and UDP scan types as separate controls, -Pn always visible, an NSE script picker (searching script names; --script-args stays refused), a much larger option search.

2026-11-03 done.
- **Files:** `segowl/scan_profiles.py` (profiles, validation, deny list, commands, scripts, port search), `segowl/defaults/iana_ports.csv` (11,628 rows, CC0, refreshed by hand), and the Profiles and Scans pages (`profiles.html`, `app_profiles.js`, `scans.html`, `app_scans.js`).
- **Decision (not in the spec): a Source = a folder `scans/<ip>/`.** "Add Source" creates it empty, and the CLI ignores empty folders. The progress grid rows are those folders.
- **Single implementation:** the command preview is computed by the server, the same code that writes the scripts.
- **Scripts:** a script embeds its target list (inventory minus Self) in `targets/<src>-<profile>.txt` and runs `nmap -iL` on it. Users cannot put `-iL` in a profile; only SegOWL uses it.
- **Progress grid:** a top + explicit-ports profile expects two files, and the grid shows `1/2` until both are there.
- **Uploads:** streamed to disk; a file that already exists is refused rather than overwritten.
