# P05 report — Stock SageTV CC authority and virtual CC1/CC2

## Current2026-11-19 audit

WP05-006 is complete within its documented audit acceptance: real original
broadcast708service1/absent2/return/seek passes four actual iPhone rows on Web
202559;23generated608CC1-4/708standard+extended service vectors plus18authority/
18service-loss and both-engine12DOM cases pass. Original stock608/callback
evidence below remains valid. Compact results/WP05-006/RESULT.md documents the
exact source/hash/build, field scope and partial708SWA/delay/styles/characters.
No all-service/all-style certification. WP05-005 remains open solely for an
unavailable property-present real peer; do not fabricate Core negotiation.
Historical implementation/checkpoint claims below remain dated evidence.

Runtime checkpoint: **3.2.8-P05**.

Implemented locally:
- OFF / CC1 / CC2 / STV / DVB authority model with persisted virtual CC profiles.
- Virtual CC resolution is limited to Teletext, CEA-608 and CEA-708. DVB bitmap remains explicit and ordinary file/DVD subtitle preferences are not consulted.
- Auto resolution prefers observed PMT services over metadata-only placeholders, is English-first for CC1, and can select a distinct described CC2 service. CEA-608 language remains unknown.
- Stock `GFX_SUBTITLES` / `SUBTITLES_CALLBACKS` negotiation and event-225 wire output.
- A/53 cc_data -> extender callback records with 45 kHz PTS, duplicate suppression, playback-clock gating and reset/flush records.
- STV Teletext -> CEA-608 callback records. Observed Teletext suppresses A/53 fallback in STV mode to keep one renderer.
- `VIDEO_CC_STATE` is honored when present; peers that omit it retain callback fallback behavior.
- Existing DVB command-36 physical PID control remains independent.

Not field-certified here:
- Real stock SageTV/STV Off/CC1/CC2 behavior.
- Property-present versus property-absent peer behavior on a physical server.
- Real seek/flush ghost-caption check and 708 service/style coverage.
## 3.2.25 field correction
A real web-MiniClient field test showed that selecting `Captions (CC1)` in the stock STV did not make captions visible even though explicit browser-local CC1 worked. The web client had been logging `VIDEO_CC_STATE` without applying it to the local decoder. 3.2.25 keeps STV/SageTV as the authority/control plane but mirrors state 0/1..4 into the browser CEA decoder so the stock STV menu controls the visible captions. The legacy callback producer remains available; local explicit CC/DVB modes are unchanged.

## 2026-11-17 WEB-072 actual stock legacy adapter qualification

Unpublished3.3.0, normal manager223312, stock Linux232/SageTV7; browser-local
caption rendering explicitly disabled only in the ephemeral test UI. Stock
omits VIDEO_CC_STATE; exact public STV CC selection remains authoritative.
Serialized16KiB callbacks/one batch per clock preserve all complete encoded
records and FLUSH ordering. A53 tap PTS is replacement-relative, unlike the
browser file clock: subtract the exact producer start only for read/drain
gating. Teletext's file-relative cue queue is unchanged. Before: captions20s
visible atvideo16.283s and blank after30sseek. New real-bridge negative fails
old code by prematurely emitting future1s/8s records atfile30s.

16bridge/26native-seek/10GFX and public-state guards pass. Actual no-trace
CEA223556Z14rows and Teletext223738Z13rows pass callback/cleanup, followed by
explicit screenshot review: CEA CC1 readable before/afterseek (video36.670s,
rows32/34/36), channel1-only CEA correctly blank on CC2; real unchanged UK
Teletext CC1 AND CC2 readable, preserved afterseek. Off yields0alpha pixels;
local text0 throughout. Original SageMC STV, configured profile and native UI
retirement verified. No Core, stock FFmpeg, source or trace setting changed.
This closes WP05-003, not every708 service/style, property-present physical
peer, physical iPhone or broader WP05-005/006 scope. Historical checkpoint
statements above remain dated; compact WEB-072 result owns build hashes.

