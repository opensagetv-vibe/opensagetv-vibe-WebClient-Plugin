# P08 field acceptance checklist

## Teardown/lifetime completion —2026-11-19UTC, stock232/153734

WP08-008 now closes its available Linux scope: five actual host normal cleanup
cycles and two deliberately lost-Stop cycles prove live encoder/exact spool
retirement; actual iPhone010723Z holds a real no-audio one-picture menu105s,
then real BLEEnter/new feature/new root/complete Stop teardown and unchanged
profiles pass four rows.20stock hashes/noencoders verify. Prior clock/audio/
SPU/chapter/Stop/replay evidence remains scoped and valid. WEB085's presented
clock/bounded-read-ahead scope is reconciled complete. Compact WEB088RESULT
retains old invalid-owner/missing-HID observations without inventing a fix.
Windows, all-format discs, WAN and acoustic/controller acceptance are separate.

## Current still-menu completion —2026-11-18, stock232/145838

WP08-006 closes its stated still-menu scope after WEB087: actual iPhone two
four-row passes and actual WebKit/Chromium four rows each verify a genuine
one-picture/no-audio infinite menu,10s retained background/highlight, real
Select to a new moving feature and natural NEW root picture. Selected Native
stays unchanged; bounded browser-only MSE handoff handles its metadata-only
tiny menu and returns Native HLS for the feature. No new producer, duration
padding or synthetic picture. Stop restores remote-playbackfalse/profiles,
decoder ready0/no assigned src; exact native session retires independently.
Prior physical authored audio/SPU/menu rows complement short-cell runtime
tests. See compact WEB087RESULT and WP08-006PROGRESS. Repeated disconnect/
spool/clock cleanup remains WP08-008; no universal-disc/Windows certification.

## Current scoped completion —2026-11-18, stock232/113129

WP08-004/005/007 close their stated available clock/speed/buffering scope.
Actual WebKit/Chromium20s seek+8s pictures each23samples pass (old-18831ms,
new160/192ms); actual iPhone120832Z23observations/11stable samples shows new
chapter pictures+authored20s origin over5s. Reader VM chapter2/3 is explicitly
not presented-frame identity. New no-STC A/V anchor/future-cell/SPU/explicitSTC/
wrap guards preserve stock protocol and fix the reproduced old anchor.

Actual PAL576/sparse480/ALADDIN480 produce150/150/148newframes at measured
speed1.0051/1.0034/1.00689x vs monotonic wall over6s each. Real generated PAL
FFmpeg cadence and local sparse/wrap/drain suites complement physical source
evidence; no Android timestamp patch/forced output FPS or all-telecine claim.
Nine physical authored menu/audio/title/SPU/Stop/replay rows pass; HDMI tones
1000/440/440/1000Hz verify selected streams, not receiver acoustic sync.
Sparse Spanish after30s seek/new frames retains20sPause, resumes/Off and Stop.
Browser12s reserve remains; produced lead14s/input256KiB bounded, real35s
converter hold/refill/FLUSH test passes. Actual122227Z naturalEOF/new decoded
root passes73samples without blind restart or fake ended/time.

One-picture still field and repeated disconnect/teardown remain WP08-006/008;
broader angles/long-run/WAN/Windows stay separate. No blanket all-format DVD
certification. Full dated report in 2026-11-17-ACCEPTANCE.md; compact Web014/
Web085 preserve initial test-oracle/unknown-observation failures and results.

## Historical scope

Dated current update2026-11-17: WP08-002 supported audio identity and WP08-003
software/available QSV output acceptance are complete. See current TASKS ledger,
artifacts/results/WEB-063/RESULT.md and WEB-014/REAL_DISC_ACCEPTANCE.md. The
checklist below is the original P08-era scope, not current environment status.
Presentation-clock/cadence/interactive-buffer/teardown and representative-disc
requirements retain separate acceptance; no blanket P08 closure or need to
enable a new JVM flag is implied (current native role defaults on).

P08 local implementation is complete, but these checks should be captured on an unchanged stock SageTV server before native DVD mode becomes a default release capability.

1. Start the plugin JVM with `-Dsagetv.webplayer.nativeDvdProtocol=true` and confirm stock SageTV selects `MiniDVDPlayer`.
2. Play an authored DVD containing a moving title and at least two audio languages. Confirm visible H.264/AAC browser playback and select each authored audio stream from SageTV.
3. Enter a one-picture or static menu with and without ongoing audio. Confirm the background never blanks during VM waits/cell FLUSH.
4. Exercise PAL and NTSC material plus chapter/title transitions and confirm the logical time does not reset or drift at cell boundaries.
5. Pause/resume, title seek, Stop, replay and disconnect/reconnect repeatedly; confirm no orphan FFmpeg process or stale HLS epoch remains.
6. If a supported physical GPU is present, repeat moving-title playback and capture the reported decode/filter/encode accelerator fields. Do not mark an unavailable vendor as failed.
7. P08 does not validate SPU/highlight/menu-button rendering. Those observations belong to P09 and must not be used to close P08 by playing only the largest VOB/main title.
