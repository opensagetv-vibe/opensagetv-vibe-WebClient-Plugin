# Changelog

## 3.3.0 beta (2026-11-26)

- User authorized coordinated GitHub publication and SageTV catalog submission.
- Public release assets and exact-head CI verified; eight-manifest catalog
  PR132 merged on explicit admin approval; official355-entry catalog/checksum
  refreshcf367959 published. Android0.5.115 issue4 reply posted without closing it.
- Publish the stock-compatible MiniClient/PWA, mobile browsing, playback recovery,
  caption, shared adaptation and compact settings work documented below.
- Full local Java/Node/generated validation passes. WEB-133's installed
  Chromium/WebKit layout checks remain applicable: release WAR909573ad is
  unchanged; public metadata/date and reviewed Android inventory are refreshed.
- Client Extension remains optional. Native-Safari adaptation, receiver casting,
  original starred observations and platform-specific limitations remain explicit;
  this beta does not certify every phone, receiver or DVD.

## WEB-133 compact settings tabs (unreleased development)

- Restore six tabs with single-row horizontal scrolling, keyboard navigation
  and one active panel. Preserve existing profile keys and shortcut routing.
- Remove lengthy static descriptions and duplicated selected-value rows.
  Compact phone labels/controls remain aligned; dynamic errors/status and a
  concise diagnostic privacy notice remain. Save/Apply is shared by Playback
  and Transport. No playback, encoder or server Core changes.

## WEB-132 Android-style settings and refill (unreleased development)

- Reorganize existing controls into collapsible light-blue General, Playback,
  Transport, Input, Diagnostics and Recovery branches; preserve settings and
  Save/Apply. Use one adjustment selector backed by the existing two flags.
- Independent adjacent graph/information icons keep the remote menu open.
  Preserve legacy full statistics on upgrade and independent profile choices.
- Wake an idle completed-source HLS loader earlier near80% reserve; retain live,
  DVD, unknown, native Safari, healthy-request, memory and startup guards.
  MPEG-TS refill retains the earlier of80% and its existing target-minus15s.
  No new bandwidth decision, encoder, Core or provider change.
- Focused host/browser/installed stock232 validation is recorded in WEB-132's
  compact result. No physical iPhone/WAN or public release claim.

## WEB-131 Hardware Encoder naming (unreleased development)

- Align Hardware Encoder label and named accelerator/OS choices with Android;
  preserve Auto, Software, Copy, saved fallback profiles and the validated native
  Web encoding command. No new player or server Core path.
- Shared-choice checks and25DOM/profile rows per Chromium/WebKit pass. Normal
  manager123221/038f3a7e installs verified75assets/225Java8classes/18served files,
  stock20 preserved. Android independently qualifies QSV/VAAPI4routes/8seeks/
  2FF/2negative rows and HDMI; no Web-to-Android certification inference.
  No new phone/vendor-wide/Windows/publication claim; WEB-127 scope unchanged.

## WEB-130 compact diagnostics (development)

- Narrow diagnostic bars to112px maximum and6.4px thickness, with tighter
  spacing in stats and Diagnostics. Labels, values and accessibility retained.
- Both-engine desktop/mobile geometry and PWA tests pass; normal-manager020715
  installs exact WAR971c654d on stock232. Served18/package75assets match;
  stock20 unchanged. No publication or physical-phone claim.

## WEB-127/128/129 shared adjustment and STV-only entry (development)

- Send min/max once with source settings; report buffer state to shared MIM
  instead of making JavaScript bitrate decisions or estimating bandwidth.
- Simplify Fixed (Adjusted), with Fixed using Maximum and HLS chosen for
  adjustment. Retain native Safari, optional provider fallback and handoff.
- Add labeled diagnostic bars for browser/server reserve and active target.
- Route old desktop bookmarks to the STV MiniClient; remove legacy/Wasm UI
  and its PWA pre-cache entries. Saved settings and normal STV controls remain.

## WEB-126 mobile landscape and X-menu refresh (development)

- Follow the supplied mobile landscape reference; align playback with the
  D-pad middle row and put Back under Home. Keep44px targets with narrow-width
  utility wrapping, portrait/desktop restoration and the same bound controls.
- Add Force refresh webpage to X's menu, not a new icon. Share App reload,
  cache-busting navigation, settings preservation and playback confirmation.
  Include all three menu buttons in keyboard/gamepad traversal; default Cancel.
- Separate qualified provider minima (Linux0.1.32, Windows0.1.35) instead of
  requiring Windows-only fixes on Linux. No provider upgrade. Normal-manager
 224732 installs WARc6b7808c on stock232; affected local/installed Chrome and
  WebKit layout/reload, package/served/stock checks pass. No server restart,
  physical iPhone or publication claim.

## WEB-125 desktop Watch live placement (development)

- Move the existing Watch live button into the desktop playback row, directly
  before Skip back (bar-and-arrow). Restore that order after phone rotation;
  keep mobile positions, one source-owned handler and playback behavior intact.
- Refresh main/CSS/service-worker cache revisions. Chromium/WebKit layout,
  click ownership, mobile input and PWA checks pass. Stock232 installation is
  pending its active recording/session guard; no publication or physical claim.

## MIM-WIN-001 stock Windows recording URL (development)

- Accept stock STV media URLs containing literal Windows backslashes, and
  remove the URI-only slash before an absolute drive path. Preserve literal
  plus/percent decoding, malformed-escape refusal and the existing authorized
  MediaFile/import-root resolver. No arbitrary filesystem or Core changes.
- New recording URLs differ from the previously imported forward-slash
  fixture; strict URI parsing rejected OPENURL before any browser decoder or
  FFmpeg startup. Exact failed-before/PASS7 parser regression joins the native
  path/disc gates. Normal-manager WAR9c4cecb7 passes actual growing Windows
  Chromium/Auto and WebKit/Software plus fresh WebKit/Auto seek/pause/cleanup.
  A prior intermittent QSV device failure remains documented, not fixed by
  relabeling its interrupted test or a successful retry. Stock37/INI intact.

## MIM-WIN-001 completed MSE tail (development)

- Wake the same HLS loader for a final subsecond fragment only when the file
  is independently completed, its clean ENDLIST matches the source duration,
  and no producer error exists. Preserve cooldown, pause intent, native HLS,
  DVD, live/unknown/truncated sources and encoder ownership.
- The focused regression fails before and passes after;108 playback tests
  pass. Installed stock185 public-HLS gates reach real decoderEOF and clear
  captions in WebKit/software and Chromium/Auto QSV, without seek/producer
  replay. Native Core terminal Pause remains distinct; no physical-iPhone or
  starred-failure cure is inferred. Growing Windows rows stay MIM-WIN-001.

## MIM-WIN-001 Java8 Windows shared process lifecycle (development)

- Reuse the FFmpeg provider's additive owned-start API when available, letting
  its verified Windows native Job safely release Java8 blocked pipes. Older
  Java9 providers retain the existing ProcessBuilder/public-handle path.
- Retire an ordinary HLS producer on fresh native INIT before admitting DVD
  input. A delayed INIT test fails before the fix;46 focused native-seek checks
  plus affected DVD/browser contracts pass afterward.
- Actual Windows recording startup, seeks, pause/resume, visible captions,
  recording-to-DVD transition, root/feature/chapter and Stop/cleanup pass in
  Chromium/WebKit. Stock native terminal Pause and the separately observed
  isolated HLS tail failures remain scoped investigation, not decoderEOF PASS.
  No physical iPhone, universal Windows or release claim.

## WEB-124 optional in-place QSV adaptation (development,2026-11-24)

- Reuse the optional FFmpeg plugin controller, absolute idempotent targets,
  immutable ceiling and uncertain-result hold; no decoder/producer replacement.
- Add default-off client opt-in and shared synthetic test Run/Refresh actions.
  Measured fragment-body bandwidth/reserve EWMA drives bounded down/up changes;
  missing native Safari timings abstain honestly. Unsupported providers retain
  ordinary playback/qualified handoff; Windows/NVENC remain unqualified.
- Pace only opted-in eligible input after a six-second startup burst so GPU
  run-ahead cannot leave minutes of immutable old-bitrate output queued.
- Actual stock232 WebKit QSV test measures4101.918→520.631→612.651kbps,
  unchanged PID/start/GPU descriptor/720p/source and91new decoded frames.
  Local settings/layout/PWA/captions/recovery gates pass in both engines.
  Chromium final fresh-three-segment measurement passes541.168→609.249kbps
  for550→650 targets, same PID/start/GPU descriptor and91new decoded frames.
  Non-Pro shared in-place checks pass; no physical iPhone/VPN or publication
  claim. Broader local Web suites pass; stale fixture icon-count/URL-base,
  neutral-settings-focus and async new-source-reset oracles were corrected
  without changing production UI/playback to satisfy them.

## WEB-121 live buffering recovery and server recorder (development,2026-11-22)

- Repair native Safari loader starvation using the same producer and actual
  playback position; protect Pause/source/seek/AirPlay ownership and bound retries.
- Let clean exhausted native physical pieces advance through stock EOS instead
  of repeatedly recovering against a longer wall-clock duration. Whole-library,
  growing, failed and unknown-source truncation checks remain intact.
- Preserve an established live decoder when the recording writer has no new
  bytes; resume refill automatically on source growth instead of cold-starting
  at a tail lacking PAT/GOP data. No fabricated media or timestamp jumps.
- Add bounded passive server history, rotating journal, authenticated inspection
  and hash-verified report exports surviving session cleanup. No Core changes.

## WEB-120 live recording rollover (development, 2026-11-22)

- Preserve the authorized OPENURL recording segment instead of resetting to
  zero. Native Pull feeds/clocks only that segment; stock SageTV owns subsequent
  segment/programme continuation. Direct-library concatenation is unchanged.
- Growing duration stays unknown until completion; near-live requests beyond
  captured PTS get a bounded proven-tail preroll, not a long empty discard.
- Add source-scoped long-press Watch live using public stock Seek/Play, with
  stale/DVD/non-TV/completed guards and responsive portrait/landscape controls.
- Advance package timestamps and reject changed WAR staging with an old epoch,
  preventing Jetty from silently retaining extracted old code. Installed195253,
  affected unit/CPU/browser and actual QSV segment/Watch-live tests pass. New
  physical iPhone/VPN confirmation is not claimed. Stock Core remains unchanged.

##3.3.0 development —2026-11-20 P15 stock contracts

- Stop advertising an unimplemented private MEDIA_STATE_URL notification.
  Reject unsupported DVD_DISC_*, MEDIA_STATE_URL and capability-property rate
  setters instead of falsely acknowledging success. Implemented media-command
  forward rates and all ordinary stock properties retain their existing path.
- Add versioned capability diagnostics that distinguish the optional per-load
  companion profile from unavailable private-Core/transformed DVD contracts.
  Keep authored native DVD as the stock default, without a new navigator,
  transcoder or required Client Extension dependency.
- Add17 functional contract assertions and real TCP negative GET/SET coverage;
  strengthen packaging against bundled/shadowed Core and optional providers.
- `[*]` observations remain possibly fixed/not repeatable, not verified fixes.
  P17 publication remains on hold; this is not a public release.

##3.3.0 development —2026-11-20 WEB-118 tooling

- Correct the parity verifier to recognize explicit user-removed tasks without
  treating them as passes, and use the same logical UTF-8 source hashing policy
  as the source-manifest generator. Pinned binary/evidence hashes stay exact.
  Four regression tests added; no playback/runtime or server change.

##3.3.0 development —2026-11-20 WEB-116

- Normal diagnostic reports include passive video-element state, at most16
  ranges per buffer category, and optional browser frame-quality counters.
  Actual paused state is separate from playback intent. Unsupported/transient
  APIs remain unavailable, without breaking the report or changing playback.
- No media URLs, caption text or guessed decoder/GPU attribution are added.
  99 playback-controller tests and22 support/profile tests pass. Development
  035714 installed through the normal plugin manager; publication stays on hold.
- WEB115's eight ordinary and eight synthetic150ms-delay replacements pass.
  Reader chapter is read-ahead, not a presented-position oracle; initial cached
  native clocks require paired advancing observations after replacement.
  These verifier corrections do not prove the original startup failure fixed.

##3.3.0 development —2026-11-20 WEB-113

- Fullscreen DVD FF/RW now uses stock Time Scroll search: repeated moves do
  not rebuild the converter, Select accepts, Play/Back cancels. Held keyboard
  transport repeats until release. Native STV step sizes apply; not256x video.
- Keep Play/arm/move ordered as one source-owned input batch. Rejection, source
  replacement and cancelled intent cannot leak the remainder into a new DVD.
- Fix stock-STV OSD-only paint frames incorrectly disabling DVD key ownership.
  Only fresh DVD-feature state plus exact fullscreen/popup-free menu identity
  can override the paint heuristic. Other content/dialog guards stay unchanged.
- Input21groups/26both-engine transport DOM cases and existing special-key,
  touch/mobile/DVD regressions pass. Normal-manager development024257 installed;
  actual installed-browser acceptance is recorded in the owning result ledger.

##3.3.0 development —2026-11-20 WEB-112

- The actual input editor now offers Search/Delete actions and BrowserSearch,
  Delete/Insert, colour and channel DOM key names. All new defaults stay inert;
  Backspace retains Back. Existing context/hold/disable/persistence rules apply.
-18portable input groups,26both-engine production-DOM assertions and56existing
  mobile control checks pass. Installed normally013627; exact package/clean/
  served bytes verified. No real recording deletion, Core change or publication.
- WEB110 establishes stock9.2.17 angle213 is unimplemented; existing optional
  owner passes real branch pictures. WEB111 desktop caption-tail checks pass
  without proving a fix for the separate old native-Safari stall.

##3.3.0 development —2026-11-20 WEB-108

- Explicit active DVD transcoding-profile Apply uses one public native-title
  Seek with exact UI/file/title/modal/rate/HLS-generation guards. No ordinary
  file seek, Core change or MCP playback dependency. Paused source processing
  waits for Resume; the UI reports submission, not already-presented video.
- Both-engine playing/paused production fields pass actual700k/480p/new frames/
  settled clock/profile restoration; real software→QSV encoding switch passes.
  QSV used software decode/filter fallback, not full-hardware certification.
- Installed normally005411/WAR3867eaf2; stock20 unchanged. No phone access or
  publication. Broader DVD scan/all-disc/Windows/physical rows remain separate.

##3.3.0 development —2026-11-19 WEB-101

- Retire ordinary broadcast/file caption presentation after verified actual
  native EOF and clean completed-source receipts; never on read-ahead, unknown
  growth, a stale generation, pause/recovery or DVD menu EOF.
- Installed manager202559: actual phone language/PMT/seek/EOF/reconnect/reopen,
  original UK captions and ordinary90s EOF pass. Fullscreen HDMI red subtitle
  placement reviewed. All borrowed profiles restore; no stock Core change.
- Preserve the separate unclassified203329 native tail stall; successful later
  rows do not establish its cause. Publication and Windows remain separate.

##3.3.0 development —2026-11-19 WEB-100

- Keep PMT-driven DVB subtitle clears on source presentation time rather than
  clearing immediately when the independent source reader reaches a later PMT.
  Supply the missing source-time selection metadata; browser caption offset,
  explicit user Off/selection and legacy peers retain their existing behavior.
- Real phone reproduces English clearing11.517s instead of16s before the fix;
  installed manager200758/controller100.1 now passes English/Spanish/timed
  removal/restoration and original UK Teletext/DVB/Off. All borrowed settings
  restore; stock Core, authoritative INI and FFmpeg engines remain unchanged.
- WTTW natural full-GPU D/F/E recording completion passes960s/28640native frames,
  producerexit0/ENDLIST and exact owned cleanup on paired FFmpeg0.1.27/MIM0.4.14.
  The original failed Odd Squad file is absent; exact full-input replay is not
  claimed. No publication or new Windows/receiver/gamepad certification.

##3.3.0 development —2026-11-19 WEB-097 (field qualification pending)

- Reuse FFmpeg Plugin0.1.26's versioned Process-only stop API instead of calling
  Process.destroy on the HTTP thread while a feeder may own buffered stdin.
  Retain the exact process/registry/output until shutdown is confirmed; refuse
  overlapping replacements and expose incomplete stop in runtime status.
- Bound lifecycle waits and isolate a failed owner's reaper cleanup so other
  sessions are not silently abandoned. Older/missing protocol1 or Java8-only
  runtime reports managed transcoding unavailable rather than an unsafe kill;
  stock Core and normal UI are unchanged. Required plugin minimum is0.1.26.
- Affected local absent-provider, actual blocked-pipe, ownership/admission,
  DVD pacing/fallback/wire, growing/HLS10, streaming17, quality4, recovery11,
  playback92 and field-contract9 checks pass. Server installation and original
  live1080i/natural-completion requalification are still pending.

##3.3.0 development —2026-11-19 WEB-099

- Bound DVD QSV encoding to one in-flight frame, retaining GPU encoding and
  the selected bitrate/FPS/filters. An isolated real-source comparison
  reproduced libmfx-gen exit139 at the default depth and completed130s at
  depth1. Ordinary TV/recordings and other encoders retain their old queue.
- Stop futile recording-style Seek retries after an exact DVD converter has
  failed; show a useful title/encoder recovery message instead. Healthy and
  clean-drained cells, unknown status and newer producers remain untouched.
- Guardedly switch a native DVD first-picture stall to MSE on the same producer;
  preserve strict fallback/pause/remote/menu/generation policy and source state.
- Focused40command/92playback/both browser DVD11 checks pass. Real iPhone
 600s motion/pixel/HDMI and120s same-producer engine-transition checks pass;
  user confirms current playback is smooth. Earlier intermittent half-rate
  cause remains unproven and unique evidence retained. No all-DVD/full-GPU claim.

##3.3.0 development —2026-11-19 WEB-098

- Forward the existing stock basic Pull end-of-stream sentinel after the exact
  browser generation actually ends a successfully completed HLS stream. Keep
  the real clock internally; stock SageTV owns live programme continuation and
  normal recording completion. No automatic channel retune or Core change.
- Exclude read-ahead EOF, active/failed/stopping producers, stale/untagged
  browser reports, pending seeks and DVD drains. Preserve four-byte framing.
  Fail-before regression and focused unit/socket/seek/DVD tests pass; physical
  recording-tail and actual live11.1 programme handoff pass on iPhone/stock232.

##3.3.0 development —2026-11-19 WEB-095/096

- Clear the owning local text/bitmap queue when existing explicit source state
  reports a retired broadcast service; keep unknown legacy metadata and newer
  generations safe. WEB095 actual original-source host/phone fields qualify.
- For an ordinary native-HLS decode/source error before the first picture,
  allow one same-producer MSE attachment when fallback is enabled. Preserve
  Pause, original representation offset, settings and remote playback ownership;
  strict/late/network/DVD/unknown cases do not trigger it. No encoder/Core change.
  WEB096 unit87/clean189-input build, actual cold/visibility/warm recovery and
  updated iPhone native/ordinary/caption/PAL controls pass stated scope. Strict
  negatives, one unclassified prior HTTP timeout and unobservable Linux-WebKit
  background remain explicit; no blanket transport/device certification.
- Commissioning tests now verify complete capped-catalogue coverage, actual
  5.5h source offsets/tail on hosts and phone, missing-language fallback policy,
  source-safe diagnostics destination/spool and exact environment restoration.
  No publication or all-format/device/acoustic certification.

##3.3.0 development —2026-11-19 WEB-094

- Clear old CEA text/metadata when selecting a service without due captions;
  preserve per-service memory, paused clocks, Off and idempotent state updates.
- Add23generated service vectors and real controller/DOM checks; actual stock
  Chrome/WebKit CEA startup/seek/service changes preserve the same video stream.
- Independent build and CI metadata distinguish compiler-specific WAR bytes
  from same-toolchain reproducibility and exact commissioned-artifact checks.
  Unpublished development update only; no stock Core/native/engine replacement.

## Unreleased — bounded native DVD feature-loader recovery

- A completed DVD feature can stall in native Safari after one short segment,
  although its clean final producer already contains several seconds more.
  For that exact source/generation/empty-buffer/12s no-progress condition,
  permitted fallback reattaches the SAME HLS bytes through supported MSE once
  at the last observed position. No server seek, re-encode, fabricated EOS,
  global change or saved-profile rewrite. Pause/strict/unknown menu/source/
  live/running/error/healthy cases remain untouched; remote-playback setting
  restores on Stop/new source. Installed033113 actual iPhone reproduces the
  stall, switches SAME producer to MSE, advances new frames with zero producer
  recoveries and returns to a new root; Stop/profiles restore. Affected ordinary
  source/seek/20s/Pause/Stop also passes. Safari-internal cause is not claimed.

## Unreleased — active idle browser ownership

- An idle desktop/Android browser event stream now acknowledges actually
  received bytes at most once per15s through the existing producer-mismatched
  state route. This prevents its connected menu session expiring after90s.
  No video-clock write, event-queue drain, timer/status heartbeat or Core change;
  stopped/disconnected pages cannot keep the lease alive. iPhone long-poll and
  playing-media ownership remain unchanged. Installed actual105s idle/five
  receipts and lost-beacon automatic native/UI retirement70.19s pass, along
  with both-engine23DOM/lease/lifecycle/PWA guards. No public release yet.

## Unreleased — installed-plugin DVD title inspection

- Reuse the existing FFmpeg plugin probe resolver for read-only DVD title/
  chapter inspection. The old sibling/PATH-only lookup failed on stock232,
  despite its plugin supplying ffprobe. Preserve existing explicit override
  and ordinary source probing. No binary/PATH/Core/settings change. Nonfirst
  generated disc and failing-before resolver guard reproduce the defect.
  Manager025903 and actual stockWebKit/Chromium five rows each now pass title2,
  its duration/three relative chapters, native feature/root and teardown.

## Unreleased — stock-compatible browser-local speed

- Add explicit per-recording0.5/1/1.5/2× speed in long-press Video settings.
  It changes the browser clock only, without rate/seek/transcoding commands
  to stock SageTV. Same-recording seek/quality retains it; Stop/new source/DVD
  resets normal speed and DVD keeps native controls. Actual speed appears in
  status; unsupported setters report failure without replay. No persisted
  default, reverse/frame-step promise, native STV key change or Core update.
  Both-engine22DOM cases and actual iPhone forward-rate/Pause/reset/teardown
  pass after normal-manager022105 installation. File-clock errors stay within
  173ms in the four measured samples. Affected actual stock WebKit DVD menu/
  Select/feature/root passes. This is browser-local speed, not native Pull-rate
  support, a precision-clock guarantee or reverse/frame-step support.

## Unreleased — original broadcast primary-audio selection

- Recognize an exact NAR audio-language tag as narration even when the source
  provides no title or visual-impaired flag. Automatic selection prefers the
  primary track; an explicitly selected NAR track/language still wins. The
  original Breakfast recording reproduces the old policy error on the iPhone.
  Failing-before/seven corrected policy cases and actual iPhone Auto/NAR/Auto
  restoration pass after normal-manager013709 installation. A125s sustained
  preview/fullscreen phone check also passes. No Core or saved-profile change.

## Unreleased — browser transport ownership

- WEB088 candidate bounds orphan native UI/media/GFX lifetime when pagehide
  Stop is lost.30s detached reconnect grace/90s half-open idle; real browser
  state/event requests and successful HLS/continuous-media delivery renew it,
  diagnostic status does not. Old stream completion cannot detach a newer
  stream, normal reload/reconnect/background media retain their ownership.
  No stock Core change. Local policy/wire/servlet guards pass; normal manager
  and repeated physical-field teardown qualification follow before closure.

## Unreleased — native Safari one-picture DVD compatibility

- Client-only one-shot HLS/MSE handoff for a current completed one-picture
  DVD menu that native HLS exposes as1us/metadata-only/no buffered picture.
  Reuses the same encoded stream without seeking/restarting/transcoding it.
  Respects fallback policy, user pause, stale epochs, cancellation and source
  changes; restores the temporary remote-playback attribute on Stop/failure.
  Selected Native remains distinct from actual browser MSE fallback in
  diagnostics.76playback/6fixture guards and affected package/browser checks
  pass. Installed145838 actual phone two4row menu/feature/new-root/Stop passes;
  host WebKit/Chrome four rows each. WEB087 and stated WP08-006 scope complete,
  not all-disc certification. See compact WEB087RESULT for exact evidence.

## Unreleased — one-picture DVD HLS compatibility

- WP08-006 identifies a separate Linux MIM raw-stdin EOF loss, corrected in
  required test dependency FFmpeg0.1.25/MIM0.4.13 through the normal plugin
  manager. Engines, INI and protected stock bytes are unchanged.
- A one-picture cell produces a zero HLS target bound rejected before segment
  loading on the test iPhone. Candidate serving normalization raises only that
  bound to1; real EXTINF, media bytes, frame count and completion are unchanged.
  Physical qualification remains open; no blanket still-menu PASS.

## Unreleased — VobSub palette and file subtitle timing

- Require verified IDX or exact-associated IFO palette rather than guessed
  colors; preserve sparse physical substream IDs. Apply forced-only decoder
  filtering for DVD/PGS and retain original file cue/clear timing plus offsets.
  Genuine external sample/production worker and both host renderers pass;
  stock-manager integration passes22actual assertions on Linux232 and closes
  WP06-004's stated scope, not physical iPhone/all-source/forced-positive proof.
  Token-owned old-worker retirement preserves replacement seek cues rather
  than clearing the shared queue; actual server before/after confirms the fix.

- Development WEB082/084: normal library Play recognizes qualified stock and
  SageMC public menu identity when a DVD emits no video rectangle. The normal
  exact-source completion requests fullscreen once from proven preview.
  Confirmed local native DVD menus route Select through the supported public
  DVD control, avoiding SageMC's generic Select listener ambiguity on return.
  Unknown STVs, ordinary playback and modal dialogs retain normal input; no
  Core modifications, test-MCP playback dependency or uncertain-input replay.

- Development WEB081: completed recordings drain their decoded final samples
  instead of waiting for rounded segment reserve. Native Safari manages its
  own decoded-buffer transitions without an MSE-style client pause. Requires
  genuine completion/source-end truth for the finite-tail exception; no fake
  ended/timestamps/seek/recovery or user-pause/autoplay override.

- Development WEB079/080: portrait defaults to a content browser with series,
  category and import-relative folder navigation; Guide gains sticky channel
  logos/time headings, duration-based cells and two-axis scrolling. Selection
  exposes explicit live Play/future Record and native-STV Info, also on media
  lists. Info uses qualified public stock/SageMC menu/context operations without
  Watch, Core edits or a Client Extension dependency. Unknown STVs fail safely.
  Physical iPhone acceptance remains separate while the phone is disconnected.
  Correct actual guide logo delivery through public station/MetaImage APIs,
  keep selected-program details accessible on short phones, and distinguish
  asynchronous Record acceptance from confirmed scheduling without replay.

## Physical iPhone input/DVD corrections (development,2026-11-17)

- Add explicit Reload webpage in App settings, distinct from Reconnect and
  list Refresh. Confirm loaded video interruptions and preserve saved settings
  without autoplay bypass or automatic reload loops (WEB-078).

- Gate legacy event225 A53 captions with the exact producer-relative clock,
  preserving encoded data. Fixes ahead-of-video/blank captions after a seek;
  no stock Core or browser-local caption change (WEB-072).

- App settings adds Portrait top spacing (px),0..160/default24 beyond the
  automatic safe area. Live browser-only stage adjustment, saved/profiled,
  landscape unchanged; actual iPhone y83→107→83 verified (WEB-077).

- Keep optional DVD negotiation fast, but allow a bounded explicit-action
  acknowledgement window. Report uncertain outcomes honestly without replaying
  mutations; actual BLE Start/Save/Resume/Clear feedback and restoration pass062.

- Derive DVD SPU/highlight480/576line canvas from the authored MPEG-2 sequence,
  not INIT's monitor-aspect flag. Correct actual iPhone yellow menu-box
  alignment without changing authoring or stock SageTV (WEB-061).
- Preserve queued next-cell DVD bytes after a proven drained decoder and
  reopen an internal consumer generation when stock sends no FLUSH (WEB-060).
  Actual native and optional no-FLUSH EOF/menu plus real FFmpeg continuation pass.

- Exact BUTTON/A ownership fixes MAIN-stage Enter/Space routing (WEB-057).
- Completed, freshly confirmed native DVD menus retain their decoded picture
  without an endless Buffering message; real feature stalls remain visible058.
- Fresh Safari native DVD generations can join their actual small initial
  buffered timestamp once, correcting subtitle-switch startup at time0 before
  a4s playable range. No TV/ongoing gap jumps or encoder restart059. Actual
  phone feature/SPU on/off/chapter/menu gate passes with optional Extension off.
- Actual both-STV timeline markers now measured before replacement video on
  the phone through BLE, with unchanged stock Core/settings. Not all-format,
  WAN, gamepad, acoustic or physical-finger certification/publication.

## WEB-037 iPhone STV frame-delivery follow-up (development)

- Arm one Fetch reader pull before parsing/scheduling the current graphics
  chunk. This addresses the withheld-final-chunk failure modeled after WebKit
  bug322545 without dropping commands, changing UI resolution or bypassing
  native frame pacing. Cancellation, bounded queueing and error handling remain.
- Actual iPhone baseline showed fast command HTTP acknowledgements but repeated
  1500ms redraw gaps/late rejected frame ACKs. Physical candidate qualification
  remains separate from the passing Chrome/WebKit modeled regression.
- Read-ahead alone did NOT satisfy actual iPhone acceptance. Use finite,
  cancellable long-poll STV event delivery automatically on iPhone/iPad through
  the existing endpoint. Keep ordered rendering, queue bounds and native frame
  ACKs; allow next-poll media Stop while image decoding is pending. Reconnect
  aborts the old outstanding poll. Video/HLS delivery is unchanged.

## WEB-050..055 shared experience (development, in progress)

- Correct DVD keyboard Time Scroll from event15 (TV) to stock event10 for
  enter/commit. Custom mappings now label10 as Time Scroll and15 as TV;
  correct Live TV63 versus Library42 labels too. Existing user-selected event
  numbers are not silently rewritten. Authored
  menus and explicit non-default mappings retain normal directional keys.
- Recognize SageMC's actual MC MediaPlayer OSD hint for fullscreen playback
  keys, while named popups/text inputs/unknown menus retain normal arrows.
- Do not erase a still-fresh, exact-generation DVD-menu answer when a state
  response is temporarily unavailable. Unknown replies never extend the
  existing1.5s deadline; actual menu/source changes still invalidate it.
- Interpret stock DVD subtitle slots/HD flags as physical SPU streams, clear
  old queued selection pictures, and preserve menu highlights when subtitles
  are Off. No Core change or second subtitle owner.
- Map decoder-relative DVD cue requests through the existing read-only title
  clock anchor after chapters/seeks; retired HLS generations cannot drain a
  replacement subtitle queue. Cue polling never changes the playhead.
- Retain bounded decoded SPU history while Off and select the current frame
  at presentation time. Repeated identical NAV selection is idempotent, so
  read-ahead metadata cannot erase pending cues before their display time.

- Fix automatic network adaptation being disabled by the player's own
  rebuffering pause. User Pause remains authoritative; an internally paused
  element with PLAY intent can use sustained measured delivery for downshift.
  Buffering never permits upshift or invented throughput. Actual paced-body
  down/up and six healthy/transient/default-off profiles now pass both host
  browser engines; previous forced recommendations proved handoff only.

- Optional source-image previews reuse shared FFmpeg24 read-only leases for
  known completed single-file recordings. Explicit scrub only, small bounded
  images/cache and source-generation cancellation; no extra playback stream,
  playback seek or background capture. Native/viewed-frame fallback remains.
- User acceptance order is Chromium and WebKit first, then user-owned physical
  iPhone HDMI tests. Host results do not certify native Safari/touch/audio/WAN.

- Add versioned source-owned state, responsive local timeline and bounded
  requested/accepted/presented diagnostics without changing stock STV graphics.
- Add default-off measured quality guidance/bounded downshift. One steady-state
  output with a single bounded temporary replacement when live GPU adjustment
  is unavailable/unverified. Keep old producer until exact new presented frame;
  abort/expiry/failed preparation preserve it. Retain captions/source position,
  saved settings and Copy/DVD/stale-owner refusal; no permanent rendition ladder.
  Recover gradually within saved quality after sustained headroom/reserve and
  cooldown; optional recovery1 negotiation protects old servers. A decoder
  attach can briefly interrupt playback; not a universal seamless-ABR claim.
- Add opt-in bounded previously viewed previews/available Comskip markers and
  optional negotiated existing Client Extension DVD controls with native fallback.
- Manager013345 installed on stock232; affected Chrome153 and host WebKit
  source previews/no extra playback stream, native stock/SageMC timeline,
  optional DVD/fallback, diagnostic ZIP and captioned startup,
  seek,1000->700->900 full-GPU presented-ACK switches after real cooldown,
  explicit abort and pause/resume PASS.
  Physical phone/WAN and
  remaining wider shared Android acceptance remain open; no public release claim.

## WEB-048 — SageMC timeline responsiveness (development)

- Negotiate browser-completed frame acknowledgements so the Web bridge cannot
  acknowledge native drawing indefinitely ahead of the actual renderer.
- Preserve ordered graphics, original queue bounds, independent media/input
  handling and the unchanged stock SageTV protocol. Legacy clients default off;
  lost acknowledgements time out and session closure releases pending waits.
- Include timeline click/key/text/seek timing and bounded event-backpressure
  counters in diagnostics. This is not an optimistic or locally guessed seek.
- Installed on stock232 through its normal plugin manager; physical iPhone/WAN
  acceptance remains distinct from the affected host-browser playback gates.

## WEB-044..047 — focused startup improvements (development)

- Use actual short HLS targets for regular local transcoding; preserve Copy,
  DVD/remote pipe, concat and continuous-TS policies.
- Reuse validated completed-source embedded metadata with bounded identity/
  mutation guards and fresh per-session tracks, sidecars and service inventory.
- Discover ready segments sooner during a bounded startup-only phase and show
  metadata/cache/readiness/library/attach timings in Video information/stats.
- Compare disk and RAM with the same real GPU command; RAM showed no useful
  startup benefit, so production storage/memory configuration stays unchanged.

## WEB-043 — QSV HLS startup keyframes (development)

- Request IDR frames for forced QSV HLS keyframes. On the affected Intel
  pipeline, ordinary forced I-frames left the first segment open for34s;
  isolated same-command testing with IDR closes it at the normal HLS boundary.
- Preserve selected bitrate/GOP interval, full GPU decode/filter/encode,
  caption extraction, Copy, continuous TS and non-QSV encoder options.

## WEB-042 — retained SageMC landscape composition surfaces (development)

- Track a bounded history of native UI sizes so delayed screen-surface
  allocations and retained handles follow the current landscape canvas, rather
  than clipping a popup at an earlier narrow width. Preserve small surfaces,
  ordinary image textures and original native copy bounds.
- Add delayed-allocation and repeated-rotation pixel regressions in both browser
  engines. Physical iPhone acceptance remains separate from synthetic coverage.

## WEB-041 — two Android-grouped tools columns (2026-11-14)

- Split expanded tools into four-row columns: info/diagnostics/test/stats above
  gear, Aspect/Video/Audio/Subtitles-CC immediately left. Keep all44px targets
  visible without scrolling underneath gear; preserve040 Back spacing.

## WEB-040 — empty column between Back and arrows (2026-11-14)

- Shift the phone bottom band/Back one column left; leave an empty column
  before the bottom Down arrow. Keep gear and expanded tools in one column.
- Reserve an extra wrapped row on very narrow portrait screens without
  shrinking touch targets or overlapping the arrow pad.

## WEB-039 — bottom gear and aligned single-column tools (2026-11-14)

- Move gear to the bottom row before Help/Keyboard. Open all tools in one
  column above it; scroll when needed without shrinking44px controls.
- Align bottom Back with the D-pad Left column, including wrapped portrait
  rows. Preserve toggle/keyboard focus, settings return and desktop layout.

## WEB-038 — collapsible phone settings/diagnostic gear (2026-11-14)

- Replace the always-open left tools rail with one gear. Tap to show the eight
  existing icons and tap again to hide them. Reset collapsed when reopening.
- Keep44px targets, compact short-landscape expansion, keyboard/Escape and
  settings-parent focus. Desktop, transport, playback and saved settings stay
  unchanged. Add the existing Android gear vector to the PWA offline shell.

## WEB-037 — STV graphics scheduling and timing (Nov12, installed development)

- Keep ordered GFX and the8ms responsiveness budget, but increase the count-only
  yield threshold128→1024 for small commands. Controlled bursts use4 timer
  yields instead of25 with identical pixels; no DPI/quality/frame dropping.
- Add bounded command send-queue/HTTP, frame queue, image decode and scheduling
  timings to diagnostics/stats. Failed input requests are counted separately
  from acknowledgements. This does not eliminate cellular/VPN latency or claim
  physical iPhone acceptance before installation/measurement.

## WEB-036 — Help beside Keyboard (2026-11-12)

- Move the phone overlay's question-circle Help immediately left of Keyboard.
  Shift the remaining bottom controls right, retaining44px targets and the
  existing tool rail/aligned D-pad. Portrait wraps; desktop restores Help.

## WEB-034 — fixed-width upward broadcast captions (2026-11-12)

- Keep CEA608 at32 columns with a fixed roll-up writing row; don't recenter
  growing text. Preserve blank CR row and2/3/4-line limits; repeated PAC does
  not scroll. Only consecutive duplicated controls are suppressed.
- Roll a full CEA708 window upward on CR and bound text to its columns;
  fixed-size anchored windows do not move as characters arrive.
- Clear stale CEA after16s of source-time inactivity when broadcasters omit
  erase commands. Pausing does not expire captions; explicit erase is immediate.
- Ordinary SRT/DVD subtitles, Teletext pages and DVB bitmap cues stay separate.

## WEB-035 — intentional client exit (2026-11-12)

- Long-press X opens an exit confirmation with Cancel selected; green arrow
  continues to hide controls. Modal arrows/Enter/Escape do not leak to SageTV.
- Confirmation retires only this client's A/V and connection. Show a browser-
  appropriate disconnected page with Reconnect rather than pretending to close
  an iOS app. Foreground return does not undo an intentional exit.

## WEB-033 — supplied mobile control layout (2026-11-12)

- Follow the user's ICONS_LAYOUT_MOBILE reference with existing assets:8-tool
  left rail; Keyboard/transport/Home/Info/Menu/Back bottom row; arrow pad
  bottom-right and pages above; Help/Close retained top-right.
- Use consistent44px targets and safe-area spacing rather than pasted image
  fragments. Narrow portrait wraps bottom controls and lifts the pad/pages;
  no overlaps, cloned controls, setting changes or desktop rearrangement.
- Align Up/Center/Down with Page/Last controls; shift the iPhone pad one icon
  right while retaining a screen-edge margin and an unclipped Right button.
-8 focused Chromium/WebKit geometry/safe-area/restore rows and affected56
  mobile/8 PWA/4 Settings-entry/15 input groups pass. Physical installation
  evidence and stock hashes are recorded separately in the task result.

## WEB-030/031/032 — phone Settings and remote layout (2026-11-12)

- Open Settings on Back, not the first native picker/editor; preserve all
  values and parent focus without implicit Save/Apply.
- Add Automatic maximum video height, with current device limit in its label.
  Derive an orientation-neutral physical screen limit, retain Auto in portable
  profile, and resolve only supported existing wire heights. Keep manual/
  Source defaults and explicit video Copy behavior; no new server protocol.
- Phone Home/Menu/Back follow bottom transport controls; Info leads the left
  information/diagnostics column. Retain31 unique existing buttons,44px touch
  targets, portrait navigation-group wrapping, sparse focus and desktop layout.
- Targeted unit/profile/Chromium/WebKit input/geometry/Settings/PWA gates pass.
  Actual phone/stock232 evidence is recorded per task; no Core change.

## WEB-027/028 — browser-only iPhone clarity/Controls (2026-11-12)

- Increase automatic native UI raster density on high-DPI devices with2x and
  1920x1080 caps; retain exact fixed resolutions and media geometry. User
  confirms sharper actual STV output; no native HDMI scene or Core changes.
- Hide persistent Controls launcher by default. App settings can opt it back
  in; preserve long-press menu, preference/profile and PWA persistence, and
  independent connection-recovery actions.
- Affected Chromium/WebKit/DPR3, core/profile, PWA, orientation and recovery
  gates pass. Installed stock232 manager155136,6 served assets and20 protected
  stock files verified; actual phone synthetic long-press opens/closes menu.

## WEB-026 — landscape native surface correction (2026-11-12)

- Resize retained screen-sized offscreen graphics surfaces along with the main
  canvas, preserving handles and ordinary image/preview caches.
- Map exact whole-screen copies using stale allocation bounds to current
  screen dimensions; retain partial-copy and negative-height blend behavior.
- Reproduced actual iPhone394x794 offscreen target clipping852x394 landscape;
  Chromium/WebKit orientation regression and affected display/recovery pass.
  Normal stock232 manager153547 update, fresh landscape pixels span screen;
  user physically rotated portrait/back and confirmed the screen now fills.

## WEB-025 — iPhone close/reopen recovery (2026-11-12)

- Fix compact layout hiding the only Reconnect action. Add stage-owned44px
  reconnect/diagnostic controls visible in mobile/standalone/render-only layouts.
- Validate the exact session when returning; recreate expired/retired sessions
  once, preserve healthy sessions, and support return without BFCache flag.
- Guard concurrent attempts and late old HTTP404 responses; no remote keys,
  seeks or playback requests replayed; failed replacement stays manual.
-26 focused recovery cases and affected lifecycle/diagnostic/viewport gates
  pass. Installed through stock232 plugin manager151605; actual iPhone fallback
  verified and user confirms automatic recovery after real close/reopen.

## WEB-024 — physical iPhone usability iteration (2026-11-12)

- Replace the phone settings category grid with a horizontally scrollable
  strip; full-width portrait controls and wrapping long selected values keep
  native pickers readable without changing saved option values.
- Enforce44px minimum Back/select/action targets and16px text controls; retain
  parent/focus return and existing31-icon playback overlay.
- Add real-iPhone layout/session probes and8 Chromium/WebKit usability rows.
  Existing56 mobile/8 PWA and22 display scenarios plus affected input/core/
  profile helpers pass; physical post-install acceptance is tracked in TASKS.
- Detect a successful manager update serving stale Jetty extracted assets;
  advance the reviewed deterministic build epoch and verify served byte hashes,
  rather than overwriting live WAR/extracted files. No stock Core modification.
- Physical follow-up: iOS native selects ignored min-height; explicit44px
  height preserves the native picker and passes the actual393x793 phone gate.
  Updated stock232 manager snapshot3.3.0.20261112.143931/asset tokenweb024.2;
  target size, full values, category strip, Back/focus and media-state checks
  pass. Broader trusted gestures/audio/PWA/controller acceptance stays separate.

## 3.3.0 development — current Vibe / mobile PWA

- Compare current Android source/dev (268 preference entries), not only the
  archived0.5.95 plan; record adaptations, platform limits and portable gaps.
- Current31-icon overlay, Last, spatial focus, compact nested settings, robust
  toolbar/IME keyboard ownership and configurable tap/hold/touch mappings.
- Actual MiniClient Home Screen manifest/Apple metadata, safe areas, optional
  wake lock, Media Session and explicit/native HLS routing where supported.
-25ms audio slider, diagnostics destination/share choices, normalized schema2
  profile backup with schema1 migration, exact-source bounded Apply custody.
- Virtual DVB slots/English-first resolution, stock public STV readback,
  independent caption epochs/recording clock and paced source-only readers.
- Standard gamepad button/stick mappings with modal ownership and focus-loss
  cancellation; explicit Auto/YADIF/BWDIF server filters and profile round-trip.
- User-facing server-generated MPEG-2/AC-3 ball calibration through the shared
  FFmpeg audio-offset path. Local measured output shifts exactly ±500ms.
- Carry quality, audio offset and filter preferences into native DVD conversion;
  stock public authored-menu readback guards Time Scroll and held chapters.
- Local/browser tests are separate from real232, physical iPhone and the
  existing open DVD matrix. No Core changes or new public release yet.

- 2026-10-21: rename source repository to opensagetv-vibe-WebClient-Plugin;
  update canonical metadata, preserving installed IDs and beta3.2.30 assets.
  Affected local build/package/source checks only; no playback changes.

- 2026-10-09: verified the already-public3.2.30 beta and merged platform
  catalog entries against independent downloads/GitHub digests/catalog MD5.
  WEB-017 closes; remaining field gates stay open and runtime is unchanged.

## 3.2.30 — 2026-09-29

- Imported the owner-supplied 3.2.29 P14/DVD-startup-recovery tree into the
  `opensagetv-vibe-web-client-plugin` project without discarding its historical
  parity and validation evidence.
- Added the standard Vibe workflow, governance, release metadata, security,
  licensing, handoff, task, and repository-check contracts.
- Made the platform-matching OpenSageTV Vibe FFmpeg Plugin an installation
  dependency and changed production discovery to its `SageTVTranscoder`
  bridge. SageTV's stock `ffmpeg` remains untouched and is no longer selected
  directly by this web plugin.
- Retained explicit transcoder/legacy FFmpeg overrides for bounded regression
  fixtures and diagnostics.
- Added deterministic Linux/Windows plugin packages and unified build-image
  commands, then passed the complete Java, JavaScript, real-FFmpeg, package,
  Playwright, and Chromium validation suite.
- Normalized WAR and plugin-ZIP entry timestamps to `SOURCE_DATE_EPOCH` and
  added a repeat-build gate; two consecutive builds must now be byte-identical.
- Commissioned the canonical WAR on `.232` and proved plugin-owned FFmpeg 9.0.1
  discovery, QSV capability gates, generated hls.js/mpegts.js playback, real
  MPEG-2/AC-3 playback and seek, CEA, Teletext, DVB bitmap, and redacted/hash-
  verified diagnostic export.
- Kept unavailable H.265/file-subtitle/live-recording field rows and the
  unsuccessful physical DVD SPU/menu matrix explicitly open; see
  `docs/VALIDATION-3.2.30.md`.

## 3.2.29 — 2026-09-26

- DVD startup now uses the same staged recovery policy as ordinary HLS: full hardware decode/VPP/encode, then hardware encode with software decode/filters, then libx264 when fallback is allowed.
- A bounded 16 MiB MPEG-PS startup replay prefix survives failed DVD decoder starts, so fallback does not lose the short title/menu cell already consumed by the failed FFmpeg process.
- DVD diagnostics now expose fallback stage/reason and replay byte/truncation state.
- Fix native DVD menus that showed only the SPU/button highlight over a black background. The old browser path captured a menu still only when FLUSH arrived, which is too late for one-picture cells after Chrome has already released the decoded frame.
- Maintain a generation-scoped browser frame cache for DVD playback and promote the last proven decoded frame to the retained DVD still canvas at the native FLUSH/menu boundary.
- Keep the previous menu image visible while the next DVD generation is attaching or contains only SPU/no playable video; never replace a good retained menu image with black because a replacement cell produced no decoded frame.
- Release the retained still only after an actual decoded frame from the replacement generation has been copied. Late timeupdate/ended events from the frozen generation cannot erase the menu background.
- Tag the native DVD freeze event with its generation and expose DVD menu-frame cache/promote/miss state in support diagnostics.
- Preserve the 3.2.27 full hardware DVD MPEG-2 -> H.264/AAC transcoding path unchanged.

# DVD hardware HLS transcode startup fix 3.2.27 — 2026-09-25

- Fix the DVD FFmpeg command so hardware decode options (`-hwaccel`, hardware output format and device selection) are emitted before the MPEG-PS `-i pipe:0` input, as required by FFmpeg.
- This fixes the field failure where SageTV successfully entered native DVD mode and filled the bounded MPEG-PS ring, but no HLS session was created and playback never started.
- DVD-Video always transcodes MPEG-2 video to H.264 and audio to AAC for browser playback; an ordinary-recording `Copy` preference cannot accidentally turn DVD into MPEG-2 copy.
- Honor the browser-selected encoder (Auto/QSV/NVENC/VAAPI/AMF/VideoToolbox/Software) for DVD transcoding. Hardware-first continues to prefer hardware decode + processing + encode when the backend probe succeeds.
- Add regression coverage for DVD input-option ordering, forced H.264/AAC DVD output, encoder preservation, and the existing real FFmpeg DVD A/V/drain path.

# Native DVD role default fix 3.2.26 — 2026-09-25

- Enable the completed stock MiniDVDPlayer capability role by default so unchanged SageTV can select DVD playback without an extra JVM flag.
- Default MiniClient capability negotiation now omits `MOUSE` from `INPUT_DEVICES` and advertises `MPEG2-PS` push, which is the stock role used by the existing native DVD wire/HLS/SPU backend.
- Keep `-Dsagetv.webplayer.nativeDvdProtocol=false` as an explicit troubleshooting escape hatch that restores the ordinary browser/PULL identity. Browser mouse events continue through the explicit web input endpoint; `TOUCH` remains advertised.
- Add regression coverage for default-on, explicit-off and explicit-on DVD role negotiation.
- Retain 3.2.25 STV caption control and 3.2.24 full hardware transcoding unchanged.

# STV-controlled browser captions 3.2.25 — 2026-09-25

- Fix STV/SageTV caption authority on the web MiniClient: the STV `VIDEO_CC_STATE` now drives the already-proven browser CEA-608 decoder instead of relying solely on the legacy event-225 path to become visible through stock STV graphics.
- STV Off clears/disables local captions; STV CC1..CC4 select the matching local CEA service immediately without changing the saved caption-authority mode.
- Preserve property-absent fallback as CC1 for older peers, and keep explicit local CC1/CC2/DVB modes unchanged.
- Add diagnostics for STV-controlled browser rendering and a dedicated regression for STV Off/CC1/CC2 transitions.
- Retain the full hardware decode/process/encode pipeline from 3.2.24 unchanged.

# OpenSageTV Vibe Web Client 3.2.30 — 2026-09-29

- Established the standalone stock-SageTV-compatible Vibe Web Client project
  from the preserved 3.2.29 baseline and synchronized runtime version 3.2.30.
- Uses the separately installed OpenSageTV Vibe FFmpeg Plugin 0.1.4 or newer
  through `SageTVTranscoder`; the WAR contains no FFmpeg/MIM executable and
  does not replace stock SageTV `ffmpeg` or require a modified `Sage.jar`.
- Includes browser MiniClient/SageMC playback, MPEG-2/H.264 HLS, hardware and
  software fallback, CEA/Teletext/DVB/ordinary subtitles, DVD menu/SPU
  navigation, seeking, diagnostics, and responsive Vibe controls.
- Complete local Java, JavaScript, deterministic package, generated-media,
  DVD/caption/recovery, and Chromium gates pass. Remaining physical long-run,
  multi-device, full DVD-title, Safari, and second-GPU rows stay explicitly
  open in `TASKS.md` and `docs/VALIDATION-3.2.30.md`.

# Full hardware transcode pipeline 3.2.24 — 2026-09-25

- Hardware-first now means hardware decode + hardware encode for every supported GPU backend, not encoder-only.
- NVIDIA tries NVDEC/CUDA → CUDA VPP → NVENC; Intel tries QSV decode → QSV VPP → QSV encode; VAAPI tries VAAPI decode/VPP/encode; AMD AMF tries D3D11VA/DXVA2 (or VAAPI where available) decode + AMF encode; VideoToolbox tries VideoToolbox decode + encode.
- Auto prefers a backend that can initialize both decode and encode over an encode-only backend.
- Startup fallback is now staged: full hardware → same hardware encoder with software decode/filters → libx264.
- Diagnostics expose decode accelerator, hardware-filter state, fallback stage, and whether the stream is end-to-end GPU.
- Add command-level coverage for all GPU backends and preserve the v3.2.23 MPEG-2 cadence/codec tests.

# Real-parameter MPEG-2/HLS field test 3.2.23 — 2026-09-25

- Keep MPEG-2 → H.264 compatibility fallback at source resolution and source frame cadence. For progressive sources, **Deinterlace = Automatic** no longer inserts an unnecessary `yadif` filter.
- Extend `/codec-test.html` with D/E fixtures matching the known real recording parameters: MPEG-2 Main, 1280×720 progressive, 60000/1001 (59.94) fps, ~6.3 Mb/s video with 19.4 Mb/s VBV ceiling, English AC-3 5.1 384 kb/s and Spanish AC-3 stereo 192 kb/s.
- D copies MPEG-2 video and converts the selected English AC-3 track to 48 kHz stereo AAC; E transcodes the exact same synthetic source to H.264 at 1280×720p59.94 and AAC.
- Retain the original A/B/C 360p30 codec controls. The real-parameter fixture remains synthetic and does not reproduce programme picture content or caption payloads.
- Add real-FFmpeg assertions that D remains MPEG-2 1280×720p59.94 and E becomes H.264 1280×720p59.94.

# Source probe fallback 3.2.22 — 2026-09-25

- Try `ffprobe` first for structured source metadata using the configured override, an executable next to FFmpeg, or PATH.
- If `ffprobe` is unavailable/fails/returns no tracks, automatically fall back to a bounded `ffmpeg -i` input probe using the same FFmpeg executable that performs playback.
- Parse video/audio/subtitle codec, source PID, language, resolution, field order, frame rate and channel count from FFmpeg input metadata when the fallback is used.
- Expose `probeMethod` in source diagnostics so reports show whether metadata came from `ffprobe` or FFmpeg fallback.
- Keep Auto/Copy playback policy unchanged; this only prevents missing `ffprobe` from forcing source codec metadata to Unknown.

# Copy passthrough policy fix 3.2.21 — 2026-09-25

- Explicit **Video processing = Copy** no longer uses a codec allow-list before FFmpeg starts. It now attempts `-c:v copy` for the source video stream, including when ffprobe metadata is unavailable.
- **Auto** remains conservative: it only copies codecs already considered browser-compatible by the existing policy.
- HLS Copy fallback is now codec-agnostic. If the browser timeline advances but no video dimensions are produced and **Allow fallback** is enabled, playback restarts at the same position as H.264.
- This fixes normal playback rejecting a source before FFmpeg could try the same stream-copy path exercised by `/codec-test.html`.

# Copy selector persistence fix 3.2.21 — 2026-09-25

- Fix **Video processing → Copy** not persisting when the settings panel was closed/reopened before the old explicit Save/Apply workflow completed.
- Selecting **Copy** now immediately saves the browser streaming profile when idle.
- When media is active, selecting **Copy** goes through the existing debounced Apply path and restarts only the media stream at the current reported position; native MiniClient/GFX remains connected.
- Keep Auto conservative, keep the 3.2.19 MPEG-2/H.264/HEVC Copy policy unchanged, and retain the guarded MPEG-2 0×0-video fallback to H.264.
- Add a Chromium regression that selects Copy, verifies local persistence, closes/reopens Settings, and confirms Copy remains selected.

# Copy video mode with MPEG-2 HLS checkpoint 3.2.19 — 2026-09-25

- Make **Copy** the single explicit no-video-transcode option; normal Auto remains conservative.
- Permit `mpeg2video` to use the existing FFmpeg `-c:v copy` HLS path when **Copy** is selected. H.264/HEVC remain supported by the same Copy option.
- Treat Deinterlace Auto as source pass-through in Copy mode. Resize/FPS changes or Deinterlace On are rejected because those operations require a video encode.
- Add one guarded automatic H.264 fallback when HLS time/audio advances but the browser reports 0×0 video after eight seconds. The restart preserves the absolute playback position and obeys **Allow fallback**.
- Bump browser streaming-profile schema to 8 and retain the 3.2.18 isolated codec-test page.
- Add policy and browser-lifecycle regressions for MPEG-2 Copy, incompatible processing rejection, same-position H.264 fallback, successful native decode with no fallback, and migration of the temporary `mpeg2copy` profile value to `copy`.

# Native HLS codec field-test checkpoint 3.2.18 — 2026-09-25

- Add an isolated `/codec-test.html` page for testing Apple/native HLS without changing normal SageTV playback.
- Generate fixed 8-second synthetic MPEG-2/AAC and H.264/AAC fixtures with the plugin-configured FFmpeg; no recording path or user FFmpeg arguments are accepted.
- Compare MPEG-2 video copied unchanged into HLS TS, the same MPEG-2 source transcoded to H.264, and H.264 copied unchanged into HLS TS.
- Keep the browser test native-HLS-only (no hls.js) so iPhone/iPad/Safari results measure the Apple media stack directly.
- Add bounded temp output, 30-minute reuse, strict media-path allowlisting, traversal rejection, and real-FFmpeg smoke coverage.
- This is a P14-derived diagnostic/field-test build; it does not start optional P15 Core/provider work or alter stock playback policy.

# P14 diagnostics/profiles/server-destination checkpoint 3.2.17 — 2026-09-25

- Replace the old observation-only playback check with an explicit bounded current-video test covering cadence/buffering, pause/resume and reversible seek on safe completed media; restore position/pause/mute/volume/rate and guard interrupted recovery by media ID.
- Add bounded redacted diagnostic ZIP export with SHA-256 report hash, terminal failure snapshot, recent test context, effective transcode mode, caption/subtitle timing/queue counters and DVD state without media/subtitle payloads or recognized credentials.
- Keep automatic terminal-failure capture default-off; manual browser download remains available even when external writes are disabled.
- Add schema-v1 saved-default profile export/import with preview, bounded unknown-key handling and explicit Apply. Client identity, current track/PID/page selections and administrator settings are excluded.
- Add administrator-configured mounted diagnostic destination support with explicit enable flag, bounded write/read/hash/delete test, atomic save, 10-file/10-MiB local spool, explicit retry and cooperative cancellation between file steps.
- Keep SMB/share credentials and full destination paths out of the browser, including redaction of configured destination/spool paths from filesystem failure details. Diagnostic output is independent of recording/media paths.
- Add P14 Java/Node/Chromium regression gates and narrow-window nested settings/D-pad focus checks.
- Real mounted-share failure/spool/retry remains WP14-006 field acceptance; earlier phase field gates are unchanged.

# P13 GFX/input/lifecycle checkpoint 3.2.16 — 2026-09-25

- Add an auditable GFX opcode ledger: implemented, negotiated-off and unknown opcodes are distinguishable in session diagnostics.
- Add default-off, per-session `GFX_YUV_IMAGE_CACHE=UNIFIED` negotiation and real format-256 Y/interleaved-UV browser conversion.
- Centralize pointer and video/overlay geometry so Fit/Fill/Stretch/Cover use one coordinate model across video, captions and DVD overlays.
- Add explicit physical-keyboard D-pad repeat ownership with keyup/blur/visibility cancellation.
- Add session-scoped pagehide retirement and bfcache fresh-generation reconnect; stale tabs cannot stop replacement sessions.
- Expand the service-worker shell to every current MiniClient module and report requested-vs-observable media worker behavior plus main-thread GFX truthfully.
- Keep unimplemented transforms/font/textured-diffuse/texture-batch/offline-cache contracts negotiated off. Stock UNIFIED DVB/Push OFF/ON A/B remains field acceptance.

# P12 audio/control/quality checkpoint 3.2.15 — 2026-09-25

- Prefer requested-language primary/default audio over commentary/NAR/descriptive tracks while preserving explicit track selection and configurable fallback.
- Expand signed audio delay to ±4000 ms / 25 ms and verify both signs with generated decoded-output calibration.
- Debounce live audio/quality changes and restart at the same reported position without reconnecting native GFX.
- Report requested/effective pipeline stages truthfully; CPU decode/filter + GPU encode is not end-to-end GPU.
- Add bounded keyframe interval/B-frame controls; copied video ignores encode-only settings.
- Advertise only proven 0.5–2.0x forward native rate; reverse/frame-step remain unsupported.
- Real broadcast PMT/layout transitions and receiver/ARC audibility remain field acceptance.

# P11 timeline/buffering checkpoint 3.2.14 — 2026-09-25

- Replace proportional pipe-source byte seeks with bounded MPEG-TS video PES PTS indexing and a post-input FFmpeg residual timestamp seek; unindexable sources never receive a guessed byte offset.
- Add seek diagnostics (`seekStrategy`, requested/anchor/residual/error, sample count and packet size) for field verification.
- Hold unexplained same-generation browser clock regressions at the last proven time and ignore browser-local DVD SEEK mutation because stock MiniDVDPlayer VM owns DVD navigation.
- Add bounded final-tail settle after recording completion and reject source shrink/replacement so stale byte identities cannot be reused.
- Suppress producer restart while source reads continue, classify recovery failures, preserve pause-time reserve filling and keep quota-reduced buffer caps.
- Serialize Comskip seek ownership to prevent duplicate EDL skips from overlapping timer ticks.
- P11TimelineSmoke passes a deliberately VBR TS seek, fail-closed unindexed source, final-tail growth and source replacement checks. Existing 240-second sustained HLS reserve remains PASS. WP11-008 multi-hour real-source acceptance remains field-gated.

# P10 source/metadata checkpoint 3.2.13 — 2026-09-25

- Require every MiniClient media path to resolve to one SageTV-authorized MediaFile; remove unsafe basename-first fallback and fail closed on duplicate names.
- Add safe literal-plus/percent/Unicode path decoding and unique stale-root suffix matching.
- Add disc taxonomy for VIDEO_TS, parent/mounted roots, ISO, physical DVD drive, VOB, imported MKV and BDMV with exact supported/unsupported stages.
- Add read-only `/api/disc?id=<MediaFileID>[&title=N]` inspection; no arbitrary path endpoint is introduced.
- Separate SageTV library/recording duration from explicit DVD-title duration and title-relative chapters.
- Probe installed FFmpeg for `dvdvideo`, `libdvdread` and `libdvdnav` before exposing an explicitly selected non-interactive movie-only title plan.
- Detect implausible imported duration/stream metadata without rewriting SageTV data or watch history.
- Keep ISO mounting server-owned and Blu-ray/BDMV/BD-J/encrypted/DRM outside the proven DVD scope.
- Six of seven P10 rows pass locally; WP10-004 remains field-gated on a representative multi-title authored DVD with a known non-first intended feature.

# P08 runtime checkpoint 3.2.12 — 2026-09-25

- Consume P07 native DVD MPEG-PS PUSH generations with real FFmpeg conversion to short-segment H.264/AAC HLS instead of treating accepted bytes as protocol-only data.
- Preserve cell/title decoder boundaries by starting a distinct converter epoch after each post-data FLUSH; do not concatenate unrelated DVD cells/VOBs into one demuxer state.
- Map SageTV DVD audio selectors by physical MPEG/private substream identity (AC-3/DTS/LPCM/MPEG) and fail unsupported/missing selectors visibly rather than selecting the wrong language.
- Map browser cell-relative playback back onto the server-owned DVD clock; keep SPU-only PES from consuming an A/V rebase and preserve the logical title timeline across discontinuities.
- Preserve authored PAL/NTSC cadence without a fixed 30 fps conversion rule.
- Add explicit one-picture menu still presentation and support tiny/audio-only cells; keep the previous authored frame visible across FLUSH until replacement video appears.
- Use a DVD-specific one-segment startup profile with bounded 6-second startup and 12-second steady reserve while retaining ordinary recording buffer behavior.
- Require both converter/input completion and browser consumption before reporting the native DVD drain sentinel. P09 still owns SPU subtitles, highlights and interactive menu navigation.

# P07 runtime checkpoint 3.2.10 — 2026-09-25

- Add lazy stock MiniDVDPlayer INIT-without-OPENURL state and distinguish synthetic startup bandwidth probes from real MPEG-PS/metadata/drain traffic.
- Own real DVD PUSH bytes in a bounded 4 MiB generation-aware ring with whole-payload acceptance, truthful free-space backpressure and exact lifetime/epoch accounting.
- Add commands 32-37 with bounded payload parsing and mandatory four-byte success/error replies while preserving the zero-byte MiniPlayer SEEK reply.
- Add 45 kHz NEWCELL/STC to 90 kHz DVD-clock conversion with 33-bit PTS wrap handling.
- Add transient 0x80 segment EOS, 0x100 drain/-2 state, harmless pre-data FLUSH suppression and post-data FLUSH reader generations; equal-sized replacement cells are distinct generations.
- Add an explicit stock native-DVD role gate. Normal P07 releases retain the browser/MOUSE/PULL identity; `-Dsagetv.webplayer.nativeDvdProtocol=true` enables the stock MiniDVDPlayer negotiation contract for field/protocol development while P08 remains responsible for visible A/V.
- Add direct bounded-state and real-socket wire regression tests. WP07-001 stock negotiation capture remains open; visible DVD playback is not claimed in P07.

# P06 runtime checkpoint 3.2.9 — 2026-09-25

- Added independent ordinary subtitle Off/Auto/Selected-track policy with language, delay and forced-only controls (profile schema 6).
- Added embedded and exact-basename sidecar discovery for supported text, PGS and DVD/VobSub tracks without browser-selected filesystem paths.
- Added sanitized Unicode text cues with overlap, authored basic WebVTT positioning and independent expiration; ASS/SSA advanced styling is flattened by the WebVTT adapter.
- Added PGS/DVD bitmap adaptation through FFmpeg into the existing DVB bitmap decoder and `LOCAL_FILE` straight-alpha RGBA browser canvas.
- Added a separate ordinary subtitle cue queue under the shared playback epoch, preserving coexistence with P05 broadcast captions and atomic seek/flush/source invalidation.
- Added production Chromium ordinary-subtitle smoke plus generated PGS-bearing MKV and embedded DVD-subtitle FFmpeg validation.
- WP06-004 remains external field acceptance for a genuine palette-bearing standalone IDX/SUB pair; prior phase field gates remain open.

# P05 runtime checkpoint 3.2.8 — 2026-09-25

- Added SageTV caption-authority modes OFF / CC1 / CC2 / STV / DVB with persistent virtual CC1/CC2 profiles.
- Added evidence-based Auto resolution for Teletext/CEA services while keeping DVB bitmap selection physically separate.
- Added negotiated legacy event-225 caption callbacks with presentation-clock gating, CEA reset/flush semantics, and stock property-absent CC1/CC2 fallback.
- Enforced single renderer ownership so STV callback captions and local browser captions do not duplicate each other.
- Bumped streaming profile schema to 5 while preserving schema-4 settings and defaulting new authority state safely to OFF.

# P04 runtime checkpoint 3.2.7 — 2026-09-25

- Add per-playback DVB bitmap subtitle decoding with descriptor 0x59 PID/language/composition/ancillary-page discovery and a bounded original-source reader.
- Decode DVB display-definition/page/region/CLUT/object state, 2/4/8-bit RLE pixel strings, transparency and timed page clears into straight-alpha RGBA cues.
- Render DVB on a dedicated browser canvas using the same Fit/Fill/Stretch/fullscreen video transform while leaving MiniClient GFX/video bounds unchanged.
- Add explicit DVB mode plus discovered service/PID/page/language controls; keep DVB outside Teletext, CEA virtual caption slots and ordinary file/DVD subtitle paths.
- Add ordinary-video media command 36/type 1 source-PID control with on-demand startup, late discovery, fail-closed unknown PIDs and disable sentinel 8192.
- Keep DVB decoding outside FFmpeg video encoding; no default subtitle burn-in is added.
- Generated Java and browser-controller acceptance passes. WP04-007 real unchanged UK DVB-bitmap visible/timing field acceptance remains pending and is not claimed.

# P03 runtime checkpoint 3.2.6 — 2026-09-24

- Add per-playback DVB Teletext Level-1 decoding adapted from the pinned Apache-2.0 Vibe Java core without its process-global active-session state.
- Discover descriptor 0x56 service types 2/5 with PID/language/page identity and handle 188/192/204-byte transport framing, PES/data-unit reassembly, Hamming-protected headers/rows and erase-page clears.
- Decode from the original authorized source independently of video copy/QSV/NVENC/VAAPI/software encoding; no second video stream is delivered to the browser.
- Present timed text from the browser video clock even while SageTV GFX/OSD is idle; seek/FLUSH/source generations clear stale page/cue state.
- Add Teletext mode, discovered service/page/language controls, schema-3 profile migration and staged payload-free diagnostics.
- Generated parser/controller/Chromium and inherited regression groups pass in split execution. WP03-008 real unchanged UK broadcast field acceptance remains pending and is not claimed. P04 is not started.

# P02 runtime checkpoint 3.2.5 — 2026-09-24

Implemented P02 shared playback/track/subtitle infrastructure. See `docs/parity/p02/ARCHITECTURE.md` and `VALIDATION.md`. No P03/P04/P06 decoder is advertised yet.

# P01 audit completion checkpoint r3 — 2026-09-24 (runtime unchanged)

- Reconciled all 1,066 top-level entries in the frozen Android changelog with zero unclassified scope records; retained 248 normalized functional fix records for browser disposition/task mapping.
- Inventoried 102 relevant regression-source files from 162 frozen-tree test files.
- Established the supplied live stock-server identity as SageTV 9.2.10.1054 with active SageTV7 STV path; preserved the no-extended-Core stock gate and documented missing binary hashes.
- Retained the untouched successful 3.2.4 baseline and fixture evidence.
- Resolved pinned release metadata for mpegts.js 1.8.0 and hls.js 1.7.3, but left real vendor MSE playback explicitly external-pending because this environment could not obtain/run those assets.
- Marked P01 exit gate complete locally with WP01-004 still not PASS. No runtime source/WAR/installer/server/user-setting changes. P02 is next.

---

# Parity checkpoint r2 — P01 audit, baseline and fixtures (2026-09-24)

- Kept runtime 3.2.4 and every original source/resource/test/build/deployable byte.
- Added248 normalized change dispositions and 68 named upstream-task mappings.
  Strict exhaustive literal fix/test intake remains PARTIAL, not falsely done.
- Freshly built and ran the untouched baseline with 235 counted scenarios,
  including 71 Chromium; real vendor MSE and live stock Core remain blocked.
- Added isolated baseline/source-delta/preflight/manifest tooling and synthetic
  Teletext/DVB/PGS/text/CEA/A-V/HLS/reserve fixtures with hashes and safe use rules.
- Retained independent reference-decoder proof and rejected initial fixture
  evidence separately; no browser subtitle or DVD support is claimed.
- Updated permanent task/evidence state:11/127 complete, P01 five complete,
  one partial, two external gates blocked. No GitHub/server/profile writes.

---

# Planning revision 1 — Android parity phases (2026-09-24; runtime unchanged)

- Add permanent P00–P17/WP task phases, dependencies and acceptance criteria
  for Teletext, DVB bitmap, native DVD and the remaining relevant Android fixes.
- Add reviewed gap/source/decision/test matrices, a frozen upstream/base lock,
  an exhaustive-intake ledger template and machine-readable task mirror.
- Keep optional extended-Core/provider work, Android-only features and upstream
  unresolved acceptance explicitly separate from stock-compatible requirements.
- Preserve every original runtime source, browser resource, test, build script,
  WAR and installer byte-for-byte. Keep runtime/build version 3.2.4.
- Regenerate the complete project manifest and verify documentation-only scope.
  No playback tests were rerun and no new runtime support is claimed.

---

# 3.2.4 — Vibe overlay and full-browser video

- Port actual Vibe Android edge layout and 30 source icon assets; package source
  provenance and license notices. Browser tools are in Help, not a giant grid.
- Connect video/audio/CC/diagnostic/statistics/aspect icons to working actions.
- Fix clear/fill mask operations changing video destination when OSD hides.
- Browser-owned full video with native small-preview and exact-native options.
- Fill default and one-time Source migration; Fit/Stretch remain selectable.
- Preserve translucent OSD, pointer mapping, cached images and native startup gate.
- 14 new display and 22 new browser scenarios, including real local H.264 decode.
- All required groups passed in split runs; live SageTV/GPU/MSE still untested.

# 3.2.3 — First-frame UI-event ordering (2026-09-24)

- Diagnose the server log's pre-frame MiniUIClientReceiver NPE; crypto query was a later symptom.
- Gate unsolicited UI events until the first FLIPBUFFER reply; keep initialization replies live.
- Coalesce startup resize/repaint/media updates and drop early user input, never replay at login.
- Preserve latest window dimensions, runtime resize, image handles, native recovery and encryption.
- Add first-frame/event-gate diagnostics and 13 real-TCP synthetic-server startup cases.
- Reproduce original 3.2.2 premature resize/repaint against its untouched WAR.
- No auth policy, Sage.jar, media configuration, FFmpeg/MIM, or installed plugin metadata changes.
- Live SageTV/SageMC verification remains required; see current validation evidence.

# 3.2.2 — Native authentication handshake

- Implement native RSA/Blowfish authentication handshake instead of returning empty CRYPTO_ALGORITHMS.
- Preserve binary public/session keys; encrypt nonempty reply/event bodies with original plaintext header lengths.
- Serialize old-mode enable/disable acknowledgements with input and property replies.
- Respect server authentication settings; do not change target host, credentials, or login policy.
- Suppress type-5 recovery while event encryption is active; retain diagnostics without exporting keys.
- Add 14 real-JCA/loopback authentication scenarios and reproduce the 3.2.1 failure with a synthetic auth-required peer.
- Live server reason/policy and physical SageMC login/playback remain unverified.


# 3.2.1 — 2026-09-24

Fixed native GFX recovery negotiation and type-5 reconnect, partial-frame handling,
worker startup ordering, socket cleanup/cancellation, and same-client-ID in-plugin
replacement. Terminal browser failures no longer endlessly reopen a dead native
session's HTTP stream. Recovery/diagnostics controls remain visible in render-only
and fullscreen views. Added bounded connection metadata and failure snapshot.
Added 11 real-loopback/fake-server and 10 production-browser/mock-HTTP regression
scenarios. This does not identify the source of the original server reset and is
not a live SageTV/GPU validation claim. Existing streaming settings are unchanged.

# Changelog

## 3.2.0 — 2026-09-24

Continuous MPEG-TS/mpegts.js, validated quality/encoder controls, source audio track/language/codec/channels/delay and original-video A/53 extraction with browser-local CEA-608/708. Reference: opensagetv-vibe/opensagetv-vibe-android-client/source/dev. Retains stock Sage.jar/Jetty/GFX/remote/HLS. Adds byte-resume/idle/output guards and regression tests. Vendor assets are server-cached, not bundled. Actual vendor/MSE and physical GPU/SageTV remain untested; full Android subtitle/CC parity is not claimed. See docs/RELEASE-v3.2.0.md.

## 3.1.1 — 2026-09-24

### Browser window and native graphics

Remove the 1280-pixel display cap. Default UI resolution follows the usable window (bounded at 1920×1080 render pixels); fixed 720p/1080p modes remain available and are contained without cropping. Notify SageTV with native resize/repaint at INIT and subsequent size changes. Keep cached image/surface handles when resizing. Canvas, video bounds and pointer mapping use one display rectangle.

### Fast start and continuous reserve

Automatic startup now waits for the first published segment regardless of producer rate. The HLS loader starts with a six-second forward target, then promotes to the configured reserve after the first append/progress (180 seconds default, 30–600 configurable). Low-delay mode no longer forces a small reserve. EVENT playlists retain recording position instead of finite live-edge catch-up. A no-progress loader wakeup works before starvation and while paused; available server data is not mistaken for a producer failure. Respect memory-pressure reductions and keep only 30 seconds of backward buffer.

### Scheduling and diagnostics

Media lifecycle events bypass the GFX image-decode queue. Ordered GFX work yields every 128 commands or approximately 8 ms; this is cooperative main-thread scheduling, not a GFX worker. Queue overflow is explicit, not silent command loss. Producer monitoring runs beyond startup, final snapshots are forced at EOF, and diagnostics include current targets, refill wakeups, native/display geometry and server thread activity. Hardware-first FFmpeg and stock Sage.jar remain unchanged.

### Validation boundaries

27 core/gesture tests, 31 playback tests, native loopback protocol test, 10 file/FFmpeg checks, and 27 offline Chromium checks; legacy tests retained. A 240-second synthetic recording verifies continued production beyond 180 seconds. Browser HLS buffering tests use mocks, not real MSE network playback; no user SageTV/SageMC/GPU/Safari field test or Python startup benchmark is claimed.


## 3.1.0 — 2026-09-23

### Python behavior port

Automatic 1–4 published-segment startup, HLS position zero, local 575-ms hold remote, double/middle/right trigger options, native click modes, repeat controls, Guide assist, side-button Back, literal keyboard entry, render-only view, full-duration timeline, aspect choices, mask/preview compositing and expanded buffer diagnostics.

### Correctness fixes

Undefined rebuffer pause variable; stale startup/status/seek events; duplicate and out-of-order mouse clicks; click leakage after holds/drags; premature ENDLIST recovery; recovery counters resetting indefinitely; overlapping status polling; native-browser timer binding; short completed clips waiting for nonexistent segments; old PWA shell masking upgrades.

### Server streaming

Cached keyed encoder probes; active files follow appended bytes rather than opening as finite files; dynamic segment rollover; final-byte drain and recording-completion duration; process identity and stop ordering; TS/PS stdin autodetection. Existing hardware-first behavior, stock Sage.jar and one browser-facing Jetty port are retained.

### Validation and boundaries

See the saved test transcript and port audit. Live SageTV/SageMC, Windows, hardware encoding, native Safari and measured comparison with Python remain unverified. Advanced Python backend controls and alternate Video.js pipelines are not all ported.

## 3.0.3 and earlier

Historical notes remain in `docs/README-v3.0.3-history.md`, `docs/handoff-v3.0.3-history.md` and the local-plugin manifest release history.

## v3.2.12 - 2026-09-25
- P09: added platform-neutral native DVD SPU assembly/RLE decode and straight-alpha browser overlay.
- Added DVD CLUT/alpha and SPUCTRL selected-button highlight recomposition without resetting queued future SPUs.
- Kept DVD physical subpicture selection independent from broadcast DVB/CC and ordinary file subtitles.
- Added generation-safe SPU lifecycle across DVD FLUSH and shared Fit/Fill/Stretch geometry; the overlay is pointer-transparent.
- Native D-pad/Select/Back/Menu/chapter commands continue through SageTV's existing MiniClient input path. Pointer DVD hit-testing remains field-gated.
