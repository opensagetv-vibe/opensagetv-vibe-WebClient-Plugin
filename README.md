# OpenSageTV Vibe Web Client Plugin

Repository: https://github.com/opensagetv-vibe/opensagetv-vibe-WebClient-Plugin

Repository naming does not change the installed plugin IDs, WAR or settings.

Development WEB-133 restores compact General, Playback, Transport, Input,
Diagnostics and Recovery tabs, removes verbose descriptions and duplicate
selected-value rows, and keeps narrow phone titles in one scrollable row. Existing
saved profiles are preserved; one Automatic Bitrate Adjustment selector replaces
two competing visible switches. Independent adjacent graph/info icons keep the
long-press menu open. Completed-source HLS idle refill and short-target MPEG-TS
refill start earlier without raising maximum/startup or overriding native Safari.
See [Browser settings](docs/SETTINGS.md) for exact controls and platform limits.
The [3.3.0 beta is published](https://github.com/opensagetv-vibe/opensagetv-vibe-WebClient-Plugin/releases/tag/v3.3.0);
validation is recorded in TASKS.md. SageTV catalog PR132 awaits upstream merge.

Current development uses only the **STV/SageMC MiniClient**. Old index/client
bookmarks redirect there; legacy/Wasm players are no longer offered or cached.
Transcoding has a simpler **Fixed (Adjusted)** switch with adjacent Minimum/
Maximum bitrate. Off uses Maximum; On starts at Maximum, uses HLS and reports
buffer state to shared MIM ADAPT-001. MIM decides changes within the supplied
range; no bandwidth estimate is required, including native Safari. Missing
capability retains Fixed playback. Changes use existing Save/Apply semantics.
Diagnostics and the stats overlay have buffer, published-reserve and video-
target bars; unavailable values are labeled, not invented as zero or CPU data.
WEB-127/128/129 track qualification; no publication/physical-WAN claim.

Current beta version: **3.3.0**. This stock-SageTV-compatible
Jetty WAR provides a browser MiniClient, recording player, captions/subtitles,
DVD playback, diagnostics, and HTML5 compatibility transcoding.

WEB-125/126 are installed on stock232 (development snapshot224732). Desktop
**Watch live** is immediately left of **Skip back** (bar-and-arrow). Mobile
landscape follows the supplied reference: Gear/Help/Keyboard/Live/playback/
Info/Menu/Home align with the D-pad center; Back sits below Home. Narrow phones
wrap the first three utilities, preserving44px targets. Portrait stays unchanged.
The X menu includes **Force refresh webpage**, using the App reload without
clearing saved settings, with confirmation before interrupting playback. There
is no extra refresh icon. Reload the webpage once to load main/CSS/SW126.1.
Both installed host browser engines pass; no new physical iPhone claim.

WEB-124 adds a default-off **Prefer in-place hardware bitrate control** setting
and Run/Refresh server bitrate-test actions. It reuses FFmpeg Plugin0.1.30 /
MIM0.4.16's optional Linux-QSV controller; the site's separate opt-in is required.
The current shared MIM controller uses buffer fill/trend to reduce bitrate
and recover gradually without changing resolution, producer or decoder. This
mode paces input with a short startup burst so a fast GPU cannot encode minutes
ahead of the decision. Already-buffered segments retain their previous rate.
Native Safari reports its playback buffer too; transfer timing is not required
by the current policy. The earlier WEB-124 measured-policy results describe
that older implementation only. Unsupported encoders
and older providers retain ordinary playback/qualified bounded handoff.
No Windows/NVENC/physical-iPhone or universal network qualification is implied.
The settings test is synthetic, guards active playback and saves its report
on the server; it is not required for playback. Publication remains held.

WEB-122 replaces Watch live with an accessible broadcast icon, immediately
left of the gear in phone landscape. Portrait places a video-only Cast icon
beside Watch live. It opens Safari's AirPlay picker or the browser's supported
Remote Playback picker directly from the user tap; it never mirrors the STV,
exports credentials/URLs, starts another encoder or retunes the programme.
No video/unsupported browser/remote-disabled playback keeps Cast disabled.
The OS/receiver owns actual discovery and routing; an opened picker is NOT
receiver qualification. Browser-rendered STV/caption overlays are not included
in video-only casting. Physical AirPlay/Chromecast/Fire TV acceptance remains
WEB-123. Google Web Sender does not support iOS, and Fire TV Matter Casting
requires separate sender/receiver integration. A server-side casting bridge
is another possible architecture, not an already-implemented feature.
Installed stock232 snapshot3.3.0.20261123.032112; reload the webpage to load
main/CSS/cast/SW122.1. Playback121.4/transcoding and stock Core are unchanged.

WEB-121 adds automatic recovery for a depleted native Safari HLS loader even
when playable output still exists on the server. After12s without progress,
repair reuses the exact producer and observed playback position (MSE when
supported/permitted, otherwise one native reload), not a new encoder or live
edge jump. Clean completed native recording-piece EOF now reaches stock piece
advance instead of exhausting retries against an inaccurate wall-clock duration.
A proven growing-source EOF waits for input and resumes refill when bytes
return; it does not repeatedly discard its established decoder at an empty tail.
Recovery prepares off the native media-control monitor, so a slow replacement
cannot block clock/Pause replies. It is exact-source scoped, rejects duplicate
pending requests and preserves Stop/Pause and the bounded retry budget.
Missing/zero-byte HLS files cannot masquerade as playable segments. Only a
clean, metadata-qualified empty seek on a completed native piece may report
decoder EOF without a nonexistent browser frame; real encoder/input failures
remain failures. The original iPhone/VPN incident remains under investigation.
An explicit producer-preparation state also prevents browser retries racing
the same producer's hardware fallback; process liveness remains independent.
App Reload now uses a fresh same-origin navigation without clearing settings;
mutable app files revalidate and service-worker network reads bypass HTTP
cache. Offline shell fallback remains available. This improves delivery of
updates, not proof of the still-open iPhone/VPN buffering incident's cause.

The server-side passive stream recorder captures source length/read position,
input age, encoder progress, HLS output, delivery requests, disk space and
source-tagged browser buffer/recovery feedback, loaded playback revision and
separate native-socket/input error categories (not raw error content). It samples independently of
browser polling, retains bounded metadata after session close and automatically
rotates two1MiB files under `plugins/SageTVWebPlayer/diagnostics/` relative to
the server working directory. No content, credentials or client identity is
recorded. `api/support?action=streamHealth` returns recent metadata;
`api/support?action=streamJournal` downloads the journal. Normal diagnostic ZIPs
include both plus hashes, even after playback closes. These endpoints retain
the existing Web server authentication. Classifications are evidence, not a
claim that a network/decoder cause was proven. Disable with JVM property
`sagetv.webplayer.streamDiagnostics.enabled=false`; optional `.dir` sets the
administrator-owned local journal path. External diagnostic-share writes remain
separately opt-in. The recorder never keeps a playback lease alive or issues
Watch/Seek/Record commands. No stock Core changes or MCP playback dependency.

WEB-120 corrects live recording rollover: the native MiniClient now opens only
the authorized physical segment with its segment-relative clock, rather than
reopening segment zero or concatenating future pieces behind stock SageTV.
The long-press menu includes **Watch live**, a source-scoped public stock seek
to the available live edge. It does not create a Record reservation or require
Client Extension/MCP for normal playback. Older recordings/DVDs are not retuned.

Commissioned iPhone acceptance now includes the actual cellular/VPN route:
HDMI/ESP32 menu redraw, recording/CEA/seek/EOF, resumed pictures/audio and
authored DVD activation/chapter replacement. See
`artifacts/results/WEB-023/CELLULAR_VPN_2026-11-20.md` for exact scopes and
limits. User-approved `*` marks the historical DVD-start/caption-tail cases as
possibly fixed and not repeatable on the current build, not proven corrections;
this is not universal all-disc/device/bandwidth certification or a new release.

Local development WEB-104 adds opt-in per-session profiles to `POST api/hls`
through `stream_profileSchemaVersion=8` and the existing `stream_*` settings.
Delivery remains HLS; bitrate/height/Copy/audio/fallback policy is validated by
the same planner as the MiniClient. Unmarked requests retain legacy behavior.
This does not raise disk limits or change saved/browser/server defaults.
Deployment/physical acceptance is recorded separately in the owning task.

WEB-116 adds passive video-element readiness/network/pause/seeking state,
bounded buffered/seekable/played ranges and optional frame-quality counters to
normal diagnostic downloads. Reports distinguish the element from playback
intent; they do not expose media URLs or infer GPU/decoder identity. These
readouts do not change playback. The intermittent DVD chapter-start failure
remains under investigation; successful repeat tests are not a proven fix.

WEB-113 routes fullscreen DVD FF/RW through native STV Time Scroll search.
Repeated moves retain the converter; Select accepts once and Play/Back cancels.
The STV owns the step size (SageMC defaults to150 seconds). This is not native
256x/reverse video decoding. Authored menus, popups, preview, stale state and
ordinary recordings retain normal input. No Client Extension or MCP dependency.

WEB-108 adds explicit active DVD profile Apply using one guarded public stock
title seek, not ordinary-file reconstruction. Paused DVD playback stays paused;
the new converter starts on Resume. Both desktop engines pass actual profile/
clock/new-frame tests, including a real QSV encoding switch. Physical iPhone
acceptance remains separate. Save still applies only to the next source epoch.

Multiple clients are supported with independent playback/caption ownership.
Short actual Chromium/WebKit coexistence checks pass on stock Linux .232;
adequate compute/spool resources are still required. Playback does not require
an idle server; updates/restarts retain separate recording/client guards.
User2026-11-19 removed multi-hour elapsed testing from required validation.

The current DVD input correction uses qualified public stock/SageMC menu
identity when no video rectangle is emitted: normal library Play reaches
fullscreen once, and confirmed native DVD menus receive the public DVD Select
control. Actual iPhone feature→root→Select→feature passes. Other input, unknown
STVs and dialogs retain the ordinary path; no Core or MCP playback dependency.
Broader title/chapter clock and representative-disc gates stay separate.

Current stock232 development installation is normal-manager
3.3.0.20261122.223956, main120.1/input117.1/mobile079.3/CSS120.1/SW121.5,
app121.5/support077.1/core121.2/playback121.4/streaming066.1
(experience062.1). The default public HLS path now requests QSV IDR
boundaries too: exact held-input A/B publishes first playlist1.718s rather
than waiting for finite EOF. This is not a universal startup-time guarantee.
FFmpeg Plugin minimum0.1.27 includes MIM0.4.14 bounded raw duplex forwarding
and the shared owned-process teardown API. Stock Core/engines remain unchanged.
Actual phone CBS natural494s completion/ENDLIST/Stop and affected DVD/caption
rows pass; WTTW full-GPU natural end also passes960s/28640actual phone frames,
clean producer exit/ENDLIST and restored owned test state. Source-timed DVB
PMT removal/restoration now avoids a proven4.4s-early clear caused by source
read-ahead. Controller100.1 and actual phone English/Spanish/absence/return plus
original UK Teletext/DVB/Off pass. Available generated language/PMT/seek/EOF/
reconnect/reopen lifetime rows now pass on the actual phone, including physical
fullscreen HDMI review. Confirmed clean ordinary playback EOF retires captions
without stopping media or clearing DVD menu graphics. Unclassified older
native stalls and all-source/device caption coverage remain separate.
Portrait now keeps the STV full-width at TV aspect,
with searchable Recordings/Guide/Videos below it and optional Controls. Portrait
starts on Recordings, with series/category/import-relative folder browsing and
breadcrumbs. The Guide is a two-axis channel/time grid with channel logos,
live Play, future Record and selected-content Info in the native STV. These
use the connected server's guide/library and public APIs, not a second player
or separate EPG feed. Chrome/WebKit model/DOM acceptance is separate from the
remaining physical iPhone tests. Actual phone393x793 content-first folders,
Guide/logos, all three Info types and fullscreen Play pass through real BLE;
852x393 landscape correctly hides the dock and opens long-press controls.
The App Reload action also passes actual-phone preference preservation.
See compact WEB-023/PORTRAIT_20261117.md; not a finger/WAN/audio certification.
Final actual stock232 WebKit/SageMC and
Chromium/SageTV7 runs each pass12rows, including the correct selected Info
screens,107 decoded channel logos, fullscreen Play and active rotation.
Future Record has production-DOM/Java receipt tests, not a real scheduled
recording acceptance claim; that requires an owned future-airing fixture.
Play
uses this exact STV's stock public API, not another player or MCP. Landscape
remains unchanged. App settings now offers Portrait top spacing (px),0..160,
default24 extra below the automatic system inset. Actual iPhone stage moves
y83→107→83 for24→48→24, retaining16:9 and unchanged playback profiles. Content
Play's native fullscreen transition passes actual stock WebKit/Chrome and
scoped iPhone BLE input. See docs/PORTRAIT_BROWSER.md for exact scopes.
App settings also offers Reload webpage (not Reconnect); loaded video asks
for confirmation, and saved preferences are preserved. Legacy caption callbacks
now use the exact producer-relative A53 clock after a seek; actual no-trace
CEA/Teletext field comparisons pass without stock Core changes (WEB-072).
Explicit iPhone Exit now acknowledges
exact server-session closure. MPEG-TS retains worker transmuxing but uses
main-thread MSE to avoid the demonstrated worker-detach seek race. Actual
original UK QSV/software/allowed-fallback TS/HLS caption/lifecycle rows are
recorded separately. Current-video diagnostics cannot restore onto a different
recording; native callback counters are payload-free. Confirmed Copy decode
failures may request one permission-aware H.264 representation instead of
restarting undecodable video. Older/default TS transport fallback preserves
Copy; strict no-fallback stays explicit and saved defaults are not rewritten.
Affected field qualification continues; see `docs/COPY_DECODE_RECOVERY.md`.
Actual iPhone native HLS passes stock-native and
optional-owned natural DVD EOF→new menu, independent audio/SPU selection,
available PAL/sparse/ALADDIN playback, and optional genuine angle1/2/3/1
pictures/terminal completion. Saved profiles and temporary hooks are restored.
See [dated acceptance](docs/parity/2026-11-17-ACCEPTANCE.md) for exact scope.
This supersedes earlier candidate/access checkpoints below, not their historical
measurements. All-disc, long-run drift, WAN/controller/acoustic rows remain
separate; this is not a blanket full-parity certification.

Current WEB-037 candidate uses the existing bounded long-poll graphics event
endpoint automatically on iPhone/iPad. The first read-ahead-only candidate did
not eliminate the user's physical redraw delay. A temporary same-phone poll
comparison showed prompt highlight movement/complete animation and accepted
frame ACKs. Desktop streaming retains one pending read before parsing. Neither
path changes video quality, STV graphics resolution, keys or stock Sage.jar.
User reports the home-Wi-Fi SageMC redraw symptom looks fixed after the second
update. That scoped observation is recorded in WEB-037; WAN/long-run and other
physical iPhone acceptance are not implied complete.

The current shared-experience browser batch is qualified on stock `.232`
through normal manager `3.3.0.20261116.042532` (cache/input/main `web055.5`).
Chrome and host WebKit pass actual measured quality adaptation, affected
timeline/preview/diagnostic checks and the17-row optional DVD gate, including
settled caption-after-seek frames and native fallback. See
[`browser evidence`](artifacts/results/WEB-055/BROWSER_ACCEPTANCE.md) and the
[`user iPhone checklist`](docs/IPHONE_HDMI_ACCEPTANCE.md). This is not physical
Safari/WAN/audio or blanket full-feature/all-disc certification.

Development playback-experience work adds a local recording timeline that
distinguishes requested, accepted and actually displayed positions, bounded
diagnostics, opt-in bounded source/viewed-frame previews and available Comskip
markers. Optional Client Extension DVD actions keep native controls available
when that plugin is absent, disabled or incompatible.

Source previews reuse the optional shared FFmpeg Plugin24 capability for known
completed single-file recordings. They are small192x108 images requested only
while explicitly scrubbing, not another playback stream or seek. Missing/old/
off providers keep native controls and previously viewed previews available.
Live/growing/DVD/multi-segment sources do not use this source-image contract.

Network quality adaptation is default off. It reduces quality after sustained
measured slow delivery/low buffer and can recover gradually after ten spaced
headroom samples with at least15s reserve, within the saved quality ceiling.
Changes have a60s cooldown and a two-attempt/source budget. It uses one
steady-state stream, not a permanent ladder of quality renditions. When live
GPU bitrate adjustment is unavailable or unverified, the owning producer
prepares one bounded replacement while retaining the old stream. An exact
new-stream presented-frame acknowledgement retires the old producer; abort,
failed preparation or timeout preserves/restores the original. Browser attach
can briefly interrupt playback; this is not certified seamless switching.
Saved quality
settings, Copy, native Push/Pull and DVD are not automatically changed.
Host-WebKit two-way/frame-ACK/caption/full-GPU gates pass; physical phone/WAN
and Android qualification remain separate. Unknown native-HLS timing disables
automatic recommendations, not normal playback. See
[`shared playback ownership`](docs/SHARED_PLAYBACK_EXPERIENCE.md) for boundaries.

Current development also corrects QSV HLS startup: forced encoder keyframes
are requested as IDR frames so HLS can publish an independently decodable
segment promptly. Copy, continuous MPEG-TS and other encoders are unchanged.
This addresses an observed34s first GOP, not a promise of a fixed startup
time on every browser/GPU. Browser/player buffering and source probing still
contribute; see the WEB-043 task for measured and physically verified scope.

Further development uses actual1s segments for ordinary local transcodes,
bounded unchanged-completed-source metadata reuse and separate startup-phase
timings in Video information/stats. Copy/DVD pipe/concat/continuous TS retain
their cadence; steady buffering is not reduced. Stock232 host WebKit warm
starts measured~1.8s, cold~4.7s; not a physical native Safari or universal speed
promise. RAM comparison showed no useful gain, so production storage remains
disk-backed. See `artifacts/results/WEB-044/RESULT.md` for affected gates/limits.

STV menus are server-rendered, unlike the local long-press controls. Cellular/
VPN latency and GFX traffic can delay navigation independently of the selected
video bitrate. Current development negotiates rendered-frame acknowledgements
with the Web bridge to avoid replaying thousands of obsolete SageMC graphics
commands ahead of a timeline seek. Stock Core/protocol are unchanged; legacy
browsers stay compatible and a missing acknowledgement has a bounded timeout.
This can limit animation FPS on a high-latency WAN; it is not a promise of
instant seeks or physical iPhone qualification. It also adds bounded input send-queue/HTTP,
frame-queue and image-decode timing counters; these are not end-to-end visual
latency measurements. The WEB-037 scheduler change preserves high-DPI quality,
all native commands and the8ms work budget; physical WAN qualification is open.

Current mobile/PWA work is described in
[`docs/MOBILE_VIBE_CLIENT.md`](docs/MOBILE_VIBE_CLIENT.md) and the
[current Android feature comparison](docs/parity/CURRENT_FEATURE_MATRIX.md).
The current269-entry source inventory is not a claim of complete physical parity.
Current development captions use fixed-width CEA roll-up windows rather than
recentering each growing line. Stale CEA clears after16 seconds of advancing
source time without an update (explicit erase is immediate); pausing does not
expire a caption. SRT/DVD subtitles and Teletext/DVB remain independent.
The long-press X confirms client exit (Cancel by default); the green arrow only
hides the overlay. On iOS, Exit disconnects playback and shows Reconnect—it
cannot terminate the Home Screen app or browser itself.
Historical 3.2.30 build and `.232` commissioning evidence is in
[`docs/VALIDATION-3.2.30.md`](docs/VALIDATION-3.2.30.md). Generated/local and
physical results are reported separately; the full authored/physical DVD
menu-SPU matrix remains open.

The platform-matching **OpenSageTV Vibe FFmpeg Plugin is required**. Production
discovery uses its `SageTVTranscoder` bridge and never selects SageTV's stock
`ffmpeg` directly. The explicit transcoder/legacy FFmpeg override exists only
for isolated regression tests and commissioning diagnostics.

The approved3.2.30 beta is published on GitHub and listed in the SageTV plugin
catalog. Its open DVD/long-run/additional-browser gates remain explicit; beta
publication is not a claim that the full physical matrix is complete.

## 3.2.29 imported baseline


## 3.2.29 DVD startup recovery

DVD HLS startup now retries full hardware -> hardware encode/software decode+filters -> full software when fallback is enabled. The plugin retains a bounded 16 MiB replay prefix of the current MiniDVDPlayer MPEG-PS generation so a failed hardware startup cannot consume the authored DVD cell before the retry. This is especially important for short DVD menu/still cells. Diagnostics report `fallbackStage`, `dvdFallbackReason`, `dvdReplayBytes`, and `dvdReplayTruncated`.

DVD menu video/still backgrounds are now retained independently from the short-lived HLS cell. The browser caches decoded DVD frames per native DVD generation, promotes the cached authored frame when SageTV FLUSHes a menu cell, keeps that image through SPU-only/no-video generations, and releases it only after a real decoded frame arrives from the replacement DVD generation. This fixes the field symptom where only the colored DVD SPU button highlight remained over a black screen.

The 3.2.27 DVD hardware transcoding fix remains unchanged: DVD-Video is converted from MPEG-2/PS to H.264/AAC HLS with full hardware decode/process/encode when supported. The 3.2.26 default-on MiniDVDPlayer role and 3.2.25 STV caption control also remain in place. Stock SageTV server/JAR behavior is unchanged.

## Real-file parameter codec A/B test (3.2.23)

`/codec-test.html` now retains the original 360p30 A/B/C controls and adds D/E using the known parameters of the tested SageTV recording: MPEG-2 Main, 1280×720 progressive at 60000/1001 fps, ~6.3 Mb/s video, English AC-3 5.1 384 kb/s plus Spanish AC-3 stereo 192 kb/s. D performs video Copy while converting the selected English AC-3 track to AAC stereo. E uses the exact same synthetic source but converts video to H.264 while preserving 1280×720p59.94. This isolates native MPEG-2 decoding from resolution, cadence, scan type, HLS segmentation and source-audio format.

For normal playback, MPEG-2 → H.264 fallback continues to use Source resolution/FPS. Deinterlace Automatic now skips `yadif` when probing identifies the source as progressive, avoiding unnecessary filtering of 720p59.94 broadcasts.

## Source metadata probe fallback (3.2.22)

Source codec discovery now tries `ffprobe` first (configured path, FFmpeg sibling, then PATH). If `ffprobe` is missing, cannot start, exits unsuccessfully, or returns no tracks, the plugin falls back to the configured FFmpeg executable and parses its bounded input probe output. Diagnostics expose `probeMethod` as `ffprobe` or `ffmpeg`, so Copy/Auto decisions no longer lose codec metadata solely because `ffprobe` is absent.

## Explicit Copy passthrough (3.2.21)

`Video processing = Copy` now attempts FFmpeg video stream copy without a codec allow-list. Auto remains conservative. If copied HLS advances without decoded video dimensions, Allow fallback can restart the same position as H.264. This aligns normal MiniClient playback with the codec-test page: explicit Copy tests actual FFmpeg/browser behavior instead of rejecting the source in policy first.

## Copy video mode (3.2.21)

Settings → **Streaming and transcoding → Video processing** now has a single explicit **Copy** mode. Selecting **Copy** now persists immediately: with active media it uses the same-position Apply/restart path; with no active media it is saved for the next recording. Closing and reopening Settings no longer restores the prior mode. **Auto / Transcode when needed** remains conservative and continues to convert MPEG-2 video to H.264. **Copy** keeps the source video codec with FFmpeg `-c:v copy` and remuxes/resegments it for delivery without a server video decode/encode. This applies to MPEG-2, H.264, and browser-supported HEVC.

For **Copy**, Source resolution/FPS must remain selected and **Deinterlace On** must not be forced, because copied video cannot be resized, frame-rate converted, or deinterlaced. **Deinterlace Auto** is pass-through in Copy mode so interlaced ATSC MPEG-2 can remain unchanged. Incompatible processing choices are rejected instead of silently changing the meaning of Copy.

When **Allow fallback** is enabled and Copy is carrying MPEG-2, the browser watches for the field-test failure signature: HLS playback time advances beyond 0.5 seconds for at least 8 seconds while the video element still reports `0×0`. If that happens, the MiniClient requests one guarded compatibility restart at the same absolute playback position with H.264 video. If the browser actually decodes MPEG-2 and reports video dimensions, playback remains on Copy. Automatic fallback can be disabled for strict testing. Streaming profile schema remains 8; the temporary `mpeg2copy` value from the codec-test checkpoint migrates automatically to `copy`.

## Native HLS codec field test (3.2.18)

Open `codec-test.html` from the deployed WebPlayer context (normally `/SageTVWebPlayer/codec-test.html`). Click **Generate / refresh streams**, then **Run all native playback tests** on the iPhone/iPad/Safari device being evaluated. The page intentionally does not load hls.js. FFmpeg creates three fixed synthetic HLS VOD cases: MPEG-2 video copied unchanged, the same MPEG-2 source transcoded to H.264, and H.264 copied unchanged. AAC audio is used in all cases so audio support does not confound the video-codec result. Use **Copy result JSON** to capture the browser/device evidence. No SageTV recording is read or modified.

**Test Current Video** is now a real explicit test: normal completed recordings check cadence/buffering, pause/resume and a reversible seek, then restore position, pause intent, mute, volume and rate. Growing/live, short/unknown and DVD/menu sessions skip unsafe mutation with a reason. Interrupted restoration is media-ID guarded so a different recording never receives the old seek.

Schema-v1 profile export/import is previewed and limited to browser-saved defaults; identity, per-session track/PID/page choices and administrator settings are excluded. Server report writes are available only to an administrator-configured mounted filesystem path with writes explicitly enabled. The browser never receives SMB credentials or opens `smb://`; failed writes use a bounded 10-file/10-MiB plugin spool with explicit retry and cooperative cancellation between file steps. See `docs/parity/p14/` for report, validation, security design and field acceptance. Next phase is optional P15 extended-Core/provider integration, while earlier field gates remain unchanged.

## P15 stock-compatible extension boundary

The optional Client Extension remains off by default and is not required for
ordinary authored DVD. Four P15 stock-alternative gates are qualified; the
private transformed-DVD input profile remains unavailable, not silently
substituted for native playback. Unsupported private capabilities are not
advertised/accepted. See [contract mapping](docs/parity/P15_STOCK_CONTRACTS.md)
and [affected installed results](artifacts/results/WP15-001/RESULT.md).
P16 retains the two user-starred non-repeatable observations. P17 local build
and package are current; publication still requires explicit approval.

## Vibe Android overlay

Long-press the SageTV picture or select Remote. The centered text-button card
has been replaced by the transparent full-screen edge layout from
`opensagetv-vibe/opensagetv-vibe-android-client/source/dev`:

- Home at the upper left; Help and Close at the upper right.
- Options / Info / Back above the left-side D-pad, with the original circular
  Select icon. Hide and Page Up/Down on the right.
- Keyboard at the lower left; playback icons along the bottom; information,
  diagnostics, playback check, stats, aspect, Video, Audio and Subtitles/CC
  tools at the lower right. Last channel sits between Page Up and Page Down.

The vector drawables retain their source paths/colors as SVG. The Home and
Close PNGs are the original bytes. All 31 icons are bundled in the WAR and
listed in the offline shell: no icon CDN or font is required. Original button
background is #A0000000; the overlay does not dim the entire video.

The arrangement above remains the desktop layout. On phones, a single gear
first in the bottom row toggles the settings/diagnostic icons, collapsed by
default. Tap again or press Escape to hide the icons without closing the menu.
Returning from a tool's settings restores that tool and focus. Expanded tools
use two four-icon columns: video info/diagnostics/playback test/stats above the
gear, Aspect/Video/Audio/Subtitles-CC immediately left, matching Android's two
utility-row groups. All44px targets fit without scrolling or covering CC.
Back sits one column left of the D-pad Left
arrow, leaving a blank bottom-row column before the Down arrow.
This adds the existing Android gear vector to the31
original controls; no SageTV commands or playback changes are sent by toggling.
The supplied
`ICONS_LAYOUT_MOBILE.png` reference uses an eight-tool left rail (video info,
diagnostics, playback test, stats, aspect, Video, Audio, CC). The bottom row
starts with Help immediately left of Keyboard, then transport and
Home/Info/Menu/Back. The row shifts right to make room. The arrow pad stays
bottom-right with page controls above it; X Exit stays top-right.
Consistent44px targets and safe-area margins replace the reference's pasted
spacing/graphics; portrait wraps the bottom controls without overlaps.

The `?` Help drawer keeps browser-only keypad, guide/recordings, volume/channel,
full-duration timeline and Render-only controls. The aspect icon cycles Fill,
Fit and Stretch. Video/audio/caption icons open the existing working browser
settings. The test icon performs the bounded P14 current-video check. Normal completed media can exercise cadence, pause/resume and a reversible seek; unsafe live/DVD/short cases are skipped and original browser playback state is restored. The green
Hide button dismisses the overlay; X asks for confirmation before disconnecting
this client, without claiming to close the browser tab or iOS app.

Hold-to-repeat, text entry and suppression of the opening click are retained.
Narrow screens reflow the bottom rows; short stages reduce icon size. These
responsive adaptations are not a claim of pixel identity to every Android DPI.

## Video display

Normal full-playback video owns the entire stage below the toolbar, regardless
of native overscan/near-fullscreen destination insets. In render-only/fullscreen
mode it owns the full content area. Automatic UI resolution also uses every
stage CSS pixel; fixed 720p/1080p UI modes still preserve their logical aspect.

Black CLEAR_RECT/FILL_RECT operations are now masks, not position commands.
They no longer move or shrink fullscreen video when SageTV's OSD disappears.
Recognized opaque full-playback edge mattes are cleared from the graphics plane;
translucent OSD panels are retained. Explicit small native/color-key previews
still use the same coordinate mapping as the UI. Native-placement override is
available for STVs that need exact server rectangles.

**Default: Fill browser.** This preserves source proportions and removes added
letterbox/pillarbox bars, but crops edges when the source/window aspects differ.
Fit shows every source edge with bars as needed. Stretch shows every edge
without added bars but changes proportions. Bars encoded into the recording
are not automatically detected or removed. No mode can preserve aspect, show
every edge AND fill a differently shaped window simultaneously.

Settings -> Video display mode / Video placement control this policy. The old
implicit Source default migrates to Fill once; an explicit Fit selection after
this update is saved and respected. Legacy Stretch/Zoom selections are kept.
Native Source notifications no longer override this browser preference.

## Install

The authoritative installation procedure is under **Install and first use**
below. Historical checkpoint instructions in this section are retained only as
version history; a current installation must report `3.2.30` from
`/SageTVWebPlayer/api/health`. The development 3.3.0 package is installed only
through SageTV's plugin manager; it has not replaced the public beta yet.

## Retained startup safety and verification

The 3.2.3 first-FLIPBUFFER native-event gate is unchanged. There are no new
native events sent from INIT and no authentication-policy changes. This checkpoint changes only streaming policy/fallback selection: the FFmpeg command builder already supports stream copy, and explicit **Copy** now permits MPEG-2 HLS as well as the existing H.264/HEVC cases.

14 new display-policy checks and 22 new Chromium scenarios pass. All inherited
validation groups also pass across split executions, including the 13 native
startup-ordering tests. See `docs/VALIDATION.md` for counts and limitations.
A controlled test against the original 3.2.3 WAR reproduces the black-clear
video shrink. Real local H.264 decoding and the shipped icon bytes were tested;
SageTV/vendor transport was simulated, not live SageMC or GPU playback.

Diagnostics now include `videoLayout`: native/source rectangles, effective
presentation, stage/CSS dimensions, server aspect and selected browser mode.
Native startup, encryption, recovery, stream and buffer diagnostics are retained.

## Retained streaming reference


Java 8 / existing Jetty WAR with real SageTV MiniClient GFX/media for SageMC/STVs, continuous MPEG-TS via mpegts.js, and configurable video/audio/browser-local captions.

Settings reference: **opensagetv-vibe/opensagetv-vibe-android-client/source/dev**, not the older OpenSageTV MiniClient. No Android repository changes were made. See [source mapping](docs/VIBE_STREAMING_PORT.md).

## Install and first use

Install the platform-matching OpenSageTV Vibe FFmpeg Plugin first, then install
or update this plugin through SageTV's plugin manager. For development, stage
the matching ZIP/XML in `SageTVPluginsDev.d` and use the same manager; do not
copy a WAR over the installation or edit its plugin registry. Coordinate any
manager-required restart with recordings/viewers. Open the existing
`/SageTVWebPlayer/miniclient.html`, then refresh. Confirm the expected installed
version in the toolbar and `/SageTVWebPlayer/api/health`. No changed port,
replacement Sage.jar, stock FFmpeg or Python service is required.

The full ZIP includes the development descriptor/package under
`dist/local-install/SageTVPluginsDev.d`. Keep installed IDs and package ownership
unchanged. Preserve recordings, properties, stock files and the vendor cache.

For iPhone, open the MiniClient in Safari and choose Share → Add to Home Screen.
The app launches the real MiniClient in standalone mode, not a separate demo.
App settings explain sign-in/storage differences and HTTPS requirements for
service-worker caching and supported wake-lock APIs. Offline means the shell
only; live SageTV and media still require the server. Physical iPhone acceptance
is not replaced by WebKit emulation.

Open **Settings → Streaming and transcoding**. Use **Prepare player assets** before testing to put pinned mpegts.js and hls.js into the server cache. This build does not embed those third-party bundles: the server requires outbound HTTPS to version-pinned jsDelivr/npm URLs on a cache miss, or an administrator can pre-seed the cache. Browsers then load assets from the plugin's same-origin vendor endpoint. Failed downloads are reported, not disguised as a successful mpegts.js installation.

## Controls wired to playback

| Group | Implemented controls |
| --- | --- |
| Player | Automatic (native HLS when supported, otherwise MPEG-TS preferred), explicit continuous MPEG-TS, HLS/MSE or Native HLS; optional fallback |
| Video | When-needed / always transcode / Copy; encoder; 250–50,000 kbps target; source or maximum height 480/720/1080/2160; source or 23.976–60 fps; deinterlace Auto/On/Off, Auto hardware preference or explicit YADIF/BWDIF Software filters |
| Encoder | Auto, Intel QSV, NVIDIA NVENC, Linux VAAPI, AMD AMF, Apple VideoToolbox, software libx264; optional software fallback |
| Audio | Actual source track index; preferred language; Auto/AAC/AC-3/strict copy; 64–640 kbps; source/mono/stereo/5.1;25ms delay steps ±4s; server-generated A/V calibration |
| Broadcast CC | Off, virtual CC1/CC2, STV or DVB; CEA-608/708, Teletext, DVB by language/type/service; independent delay ±5s, separate from file/DVD subtitles |
| Buffer | Existing 30–600-second forward reserve, 180 seconds default; minimal TS startup stash; automatic refill |

**Save for next recording** stores the profile in this browser and updates the current MiniClient's next-recording defaults, without changing existing playback. **Apply now / restart stream** creates a new stream at the current reported timestamp while retaining pause intent and the native GFX connection. The selected audio index is per recording; future recordings return to automatic/preferred-language selection. **Refresh tracks** lists ffprobe-discovered audio streams. Invalid combinations fail visibly before replacing an active stream.

Choose **Always transcode** to enforce a video bitrate/encoder. When compatible video is copied, those settings do not apply. Requested settings and effective output are reported separately. Bitrate is an encoder target, not a measured constant transmission rate.

The new pipeline encodes video to H.264. Compatible H.264, or browser-advertised HEVC, can instead be copied into MPEG-TS. New HEVC/AV1 encoding is not implemented. AAC is the compatibility audio target; AC-3 requires browser support. Browser capability checks are preliminary, not proof of physical decoding or surround-output support. This is not Android HDMI bitstream-passthrough control.

## Continuous delivery and buffering

FFmpeg produces a growing `stream.ts`, served as one continuous HTTP response without waiting for an HLS segment to close. mpegts.js starts without its large IO stash, then fills toward the reserve. At the target it may close the HTTP reader normally; its next request resumes at the exact `bstart` byte offset in the same file without restarting FFmpeg. Time seeks are different: the plugin creates a new media session through its existing timeline/seek controls.

The mpegts.js source is deliberately configured `isLive:false` even for a growing DVR recording. Its v1.8.0 loading controller bypasses lazy-load limiting for `isLive:true`; DVR mode enables a bounded forward reserve and avoids live-latency chasing that could skip recording content. The Java input follower still follows a recording source. Filling can continue while paused without resuming playback. At the live edge there is no future content to buffer. Changing the TS reserve applies on the next stream start/seek or Apply now; HLS can change its target in place.

FFmpeg can run faster than playback and finish a completed recording early; that is normal. Browser memory limits can reduce the achievable reserve. The server spool has periodic safeguards: 8 GiB per-session output default, 128 MiB free-space threshold, and 120-second idle expiry. These are not pre-reserved disk quotas. Multiple clients need adequate disk and compute resources. Limit failures are reported and do not alter the original recording.

## Hardware, threads and captions

Encoder selection uses bounded FFmpeg capability/runtime probes, cached per
encoder/executable. Full hardware decode/filter/encode is requested when the
selected backend and processing chain pass; failures can fall back to
encode-only or Software when allowed. Explicit YADIF/BWDIF filters use CPU.
Diagnostics report the actual chain, not just GPU availability. QSV full-chain
playback has been observed on stock Linux232; that is not all-GPU/Windows
certification. Audio encoding/caption parsing use CPU. Video Copy uses neither
a server video decoder nor encoder.

mpegts.js worker and MSE-worker modes are requested, subject to browser support/fallback. SageMC/GFX remains the main-thread Canvas renderer with cooperative yielding. Server native media/GFX, input following, stderr/producer monitoring, caption extraction and continuous HTTP delivery use separate threads where applicable. FFmpeg is a separate process. Worker-enabled configuration is not proof that a physical worker/GPU actually ran.

The selected CEA channel/service is **browser-local**, not Android's STV-controlled event-225 caption path. An independent stream-copy output from the same FFmpeg process carries original compressed video to the server's A/53 extractor; only small timed caption packets reach the browser. This does not create a second encode and does not depend on the GPU encoder retaining caption metadata. Select a service present in the source. Unsupported source-caption formats or absent packets cannot create captions.

Teletext and DVB bitmap subtitles are implemented as separate browser-local paths. PGS/DVD bitmap and SRT/WebVTT file subtitles are implemented in P06; genuine external VobSub IDX/SUB palette-present/missing/forced-negative acceptance passes on stock Linux232 (22actual browser assertions). This is not all-source/physical-iPhone/positive-forced certification. Virtual CC1/CC2 mapping and stock STV caption authority are implemented in P05, with broader property-present/services field rows still pending. Existing CEA/Teletext/DVB rendering is not certification of every broadcast styling/control-code variant.

## Test evidence and remaining limits

See `docs/VALIDATION.md` and `docs/VIBE_STREAMING_PORT.md` for current and retained evidence. Tests include actual FFmpeg video/audio conversion, two-language source probing, continuous file growth/byte resume, MPEG-2/H.264/HEVC A/53 parser fixtures, original-video side-copy during encoding, actual JS CEA decoding, mock-servlet async delivery, and production Chromium settings/GFX DOM tests.

The complete local browser suite includes mocked edge cases, and `.232`
commissioning additionally exercised the real cached mpegts.js and hls.js
bundles, real SageTV/SageMC media, and QSV capability/runtime paths. Native
Safari, Windows/macOS browsers, unindexed H.265/file-subtitle fixtures, a live
growing recording, and the full physical/authored DVD menu matrix remain
untested or open as listed in `docs/VALIDATION-3.2.30.md`.

Direct-file FFmpeg seeks use time-based input seeking; copied video remains
keyframe-limited. Pipe/MediaServer MPEG-TS seeks use observed PTS anchors plus
FFmpeg timestamp residuals, never guessed proportional byte offsets. If an
index cannot be proven, input starts at byte zero with timestamp seeking.
Automatic transport fallback is bounded to one transition per recording;
strict Copy and disabled-fallback policies remain strict.

Field acceptance: test the same recording with MPEG-TS and HLS; inspect Buffer info; pause until the reserve fills; resume/seek; change bitrate/audio with Apply now; test real CC1 and a known 708 service; then test a growing recording through completion. Capture Remote → Download diagnostics immediately after a failure. Review reports before sharing: addresses, client IDs and media paths may be included.

## Retained UI and deployment boundaries

The 3.1.1 full-window native resize/repaint, negative-texture geometry, preview/mask placement, full-duration timeline and long-press remote remain. Hold the picture about 0.6 seconds to open the local remote. Its Options button sends SageTV's own menu command. Remove any old `?ui=1280x720` / `?ui=1920x1080` override for Match browser window. Fixed-size modes preserve aspect and may leave bars; video aspect is separate.

The full settings are in **miniclient.html**. `index.html` retains the simple
player and `client.html` the API Web Admin. Public HLS callers may explicitly
opt into validated per-session profiles (WEB104); unmarked legacy requests
keep their old defaults. Existing Jetty authentication/access controls remain
necessary; do not expose an unprotected server to the Internet. No independent
authentication system is added.

## Server configuration

Keep the known-working FFmpeg/MIM executable; it must accept standard FFmpeg arguments. FFmpeg/ffprobe are external. Install matching ffprobe beside FFmpeg, on PATH or explicitly configure it. Missing probe metadata produces a warning and compatibility defaults; strict copy cannot guess codec safety.

| JVM property | Environment equivalent / default |
| --- | --- |
| `sagetv.webplayer.transcoder` | `SAGETV_WEBPLAYER_TRANSCODER` — optional explicit Vibe plugin bridge override; production auto-discovers `SageTVTranscoder` |
| `sagetv.webplayer.ffmpeg` | `SAGETV_WEBPLAYER_FFMPEG` — legacy isolated-test override only |
| `sagetv.webplayer.ffprobe` | `SAGETV_WEBPLAYER_FFPROBE` — matching ffprobe |
| `sagetv.webplayer.hlsDir` | `SAGETV_WEBPLAYER_HLS_DIR` — writable session output, including TS |
| `sagetv.webplayer.cacheDir` | `SAGETV_WEBPLAYER_CACHE_DIR` — writable vendor cache |
| `sagetv.webplayer.vaapiDevice` | `/dev/dri/renderD128` |
| `sagetv.webplayer.streamMaxBytes` | `8589934592` (8 GiB periodic output guard) |
| `sagetv.webplayer.streamIdleMs` | `120000` (120 seconds; minimum 30 seconds) |
| `sagetv.webplayer.maxStreams` | `8` producer admission limit |

The continuous HTTP pool allows 16 concurrent readers. Closing a full-buffer reader does not terminate its producer; Stop/disconnect/idle expiry does. Deletion is delayed for in-flight reads. The admission/output checks do not reserve GPU resources or disk space.

For offline installation, pre-seed valid upstream bundles under the cache base:

```text
<cache-base>/libmedia-1.3.1/mpegts-1.8.0/mpegts.min.js
<cache-base>/libmedia-1.3.1/hlsjs/hls.min.js
```

`GET api/assets` reports the versioned root (already including `libmedia-1.3.1`). The inherited directory name does not mean mpegts.js runs through libmedia. Exact pinned URLs are in AssetCache.remoteUrl and THIRD_PARTY.md. These are version pins, not embedded checksum-verified vendor binaries. Do not save a GitHub HTML page as JavaScript.

## Build/test

Developer dependencies: JDK supporting --release 8; javax.servlet 3.1+ API JAR; Node; Python for packaging/tests; FFmpeg/ffprobe; optional Playwright and Chromium. No Python service is deployed.

```sh
bash scripts/build-local.sh
python scripts/package-local-plugin.py
RUN_BROWSER_TESTS=1 bash scripts/validate.sh
```

Overrides: SERVLET_API_JAR, TEST_FFMPEG, CHROMIUM_PATH. Java class target is 52. Full source, compiled WAR, local installer, tests and handoff are included. No GitHub changes were pushed.
