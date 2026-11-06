# Estimate how long a Scan will run

Status: needs-triage

Vocabulary: `GLOSSARY.md` (Scan, Scan Profile, Source). Idea raised by the user on 2026-11-04, out of the scope of `app-navigation`; traced for later.

## Idea

Next to the command preview (Scans › build the scan), show how long one run will take for a Source: **best case** (every target answers fast), **worst case** (nothing answers: every probe times out and is retried) and an **expected** time for a typical internal network, from the nmap options of the profile (timing template, `--max-retries`, `--host-timeout`, `--min-rate` / `--max-rate`, RTT timeouts, parallelism), the number of ports (TCP and UDP apart: UDP is much slower) and the number of targets (inventory minus Self). Gives the auditor an idea of the duration of a run before launching it on site.

## Notes for triage

- nmap's own timing is adaptive (congestion control, RTT estimates): any estimate is a range, not a promise. Say so on screen.
- Worst case is dominated by unanswered probes: targets × ports × (max-retries + 1) × max RTT timeout ÷ parallelism, capped by `--host-timeout` per host.
- UDP: ICMP rate limiting (often 1 reply/s on Linux targets) makes closed UDP ports slow; `--defeat-icmp-ratelimit` changes it.
- Today's preview already warns about long UDP lists (local-app 04): the estimate would replace that rough warning with numbers.
- A calibration knob ("RTT of this network", "share of silent hosts") would let the expected time follow the client's network; the observed durations of past Scans (nmap XML `runstats/finished elapsed`) could seed it.
