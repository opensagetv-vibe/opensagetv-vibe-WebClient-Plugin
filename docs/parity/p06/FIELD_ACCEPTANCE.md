# P06 field acceptance checklist

## Completed scoped2026-11-18 — stock Linux/genuine external sample

Normal-manager113129 on unmodified232 passes22actual assertions: WebKit and
Chromium normal/fullscreen/100s seek/genuine visible bitmap/clear6each, WebKit
forced-only exclusion5, Chromium missing-palette with moving A/V5 and exact
IFO restoration/hash. Sample's actual image has1612alpha204pixels and authored
103603ms cue/104501ms clear; not a fabricated generated DVD-subtitle positive.
The underlying A/V is generated, subtitle IDX/SUB/associated IFO is genuine.
No forced-positive entries available; negative filtering is verified by actual
decoder image counter. Not physical iPhone/audio/all-OS/all-source certification.
WP06-004 closes to its stated palette-present/missing/forced-only acceptance.

Required production fixes: bounded palette/IFO validation, sparse physical-ID
selection, packet forced filtering, original file time/offset and token-owned
old-worker cleanup. Local24worker/context,32DVB/34architecture, old-worker
failing-before regression and both browser9assertions also pass. Details/hashes/
source provenance/repro/retirement: artifacts/results/WP06-004/RESULT.md.
Use scripts/stage-vobsub-fixture.py and tests/stock-vobsub-field.py only on the
exact owned fixture; no Core or original-recording edits. Optional field SSH
setup/trust is documented in WORKFLOW.md, never disable certificate checks.

## Historical checklist — retained broader follow-up guidance

Use v3.2.9-P06 on a real SageTV server/media library. Capture the diagnostics export immediately after any failure.

1. Text: play an embedded or exact-basename SRT/WebVTT recording. Verify Off, Auto, explicit track, language, positive/negative delay, pause/resume, forward/back seek, file end and rapid recording switch. Confirm no stale cue remains after seek/stop.
2. Coexistence: intentionally enable an ordinary file subtitle and a broadcast CC mode. Confirm both are independently controllable and changing CC does not silently change ordinary subtitle selection.
3. PGS: use a real PGS-bearing MKV. Verify palette/alpha, authored placement, clear/end and seek behavior. This is file-subtitle validation only and is not Blu-ray menu/BD-J validation.
4. VobSub palette-present: use a real `.idx/.sub` pair with known language/palette and, if available, forced entries. Verify the selected language/substream, visible colors/alpha and forced-only filtering.
5. VobSub palette-missing: remove or rename the IDX and confirm the `.sub` is not offered as a working track. Do not accept guessed colors from a concatenated VOB.
6. Lifecycle: repeat text/PGS/VobSub tests during video copy and transcode modes where applicable, then reconnect the WebPlayer. Confirm no orphan FFmpeg subtitle process and no ghost subtitle surface.

Do not close WP06-004 from generated embedded `dvd_subtitle` alone; retain the genuine external IDX/SUB field evidence.
