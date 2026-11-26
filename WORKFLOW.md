# Common project workflow

DVD read-ahead runtime qualification uses a normal generated MPEG-2/AC-3 DVD
fixture on FFmpeg6 and8. A short video-only fixture can fit entirely inside
the converter's bounded1024-packet input queue before output metrics exist;
that does not exercise application pacing. Do not assert universal time-lead
limits on that startup queue. Retain real14s pacing/refill/FLUSH/Stop checks
and include produced/consumed/readiness/exit/waits/stderr on failure.

Clean CI process-control tests need the real provider lifecycle classes, not
stubs or a sibling checkout assumption. Fetch the pinned public FFmpeg0.1.36
JAR ZIP, verify SHA25660d58439250eec189fd3002088a0f869389bd16a2b901cb3054f9286705a9274,
extract only SageTVFFmpegPlugin.jar into runner temporary storage and set
SAGETV_FFMPEG_PLUGIN_JAR. prepare-process-control-tests.sh imports only the four
bounded lifecycle classes into test-classes, never the WAR. Local reusable DEV
may use its already-built provider. A missing dependency is not a waived gate.

WEB-133 supersedes only WEB-132's settings navigation: use visible
`#settings-tab-{app,playback,transcoding,input,diagnostics,recovery}` controls,
not details.open or hidden legacy aliases. browser-settings-parity.py checks
five desktop/phone sizes per engine, one active panel, single-row tabs,
compact fields, no duplicate selected-value rows and no preference writes on
navigation. Keep dynamic errors, privacy notice and shared Save/Apply available.
Run affected entry/mobile/streaming/PWA tests and installed UI-only on stock232;
unchanged WEB-132 playback JS does not require repeating its playback matrix.
Use task-owned artifacts/active/WEB-133 and normal-manager installation only.

WEB-132 settings/refill validation uses tests/test-settings-parity.js,
test-miniclient-playback.js and test-mpegts-streaming.js, then
browser-settings-parity.py, browser-phone-controls.py, browser-streaming-smoke.py
in both engines, and affected mobile/input/PWA/reload tests. Existing field
helpers expand owning details branches, not the removed category-strip pages.
The legacy data-settings-page programmatic aliases remain for old observers.
Use task-owned artifacts/active/WEB-132, not closed task capture directories.
After normal-manager staging/install and exact75asset/225Java8class/18served
checks, installed-settings-parity.py --run-stock232 verifies real HLS playback
and independent controls on a disposable exact UI. --ui-only reruns only UI
after a later menu-only correction; preserve prior unchanged playback-JS proof.
Host WebKit/MSE is not physical native Safari or remote/WAN certification.

WEB-131 / Android SETTINGS-005 share named Hardware Encoder choices and retain
their path-specific Auto/fallback contracts. Do not count browser hardware
evidence as Android playback qualification. Run tests/test-hardware-encoder-
parity.js and browser-streaming-smoke.py in Chromium/WebKit; set the actual
SAGETV_ARTIFACT_DIR to artifacts/active/WEB-131 for new physical/browser captures
(SAGETV_TASK_ID does not redirect this helper). These DOM/profile tests do not
certify vendor hardware. Preserve the existing native Web encoder command,
Copy/Software behavior and saved profiles. Changed WARs need a newer
SOURCE_DATE_EPOCH before normal-manager staging or Jetty can reuse old classes.

## Shared MIM buffer controller / STV-only shell

WEB-127 uses provider ADAPT-001 through the optional versioned Java bridge.
Only MIM contains bitrate decision logic. Source configuration carries min/max;
subsequent reports carry producer identity, reserve, buffering and eligibility.
Use the existing stats callback, one in-flight report and3s cadence; no probe,
new player poller or measured-transfer decision. Missing/failed provider holds
Fixed; pause/seek/source/Copy/DVD/EOF/ambiguous-rate guards remain mandatory.
WEB-128 bars reuse existing snapshots; unknown values are not zero, and CPU/GPU
or native-Safari bandwidth must never be invented. WEB-129 redirects both old
entry pages to miniclient.html and pre-caches STV assets only. Test actual
Chromium/WebKit settings/reports, active/unknown bars, legacy redirects and PWA.

WEB-127 real automatic testing uses tests/browser-stock-network-quality.py,
artifacts/active/WEB-127 and actual per-session HLS-body pacing, never injected
targets, sample clocks or synthetic buffer reports. SAGETV_BROWSER_ENGINE
selects chromium/webkit; SAGETV_NETWORK_CASE selects adaptive/default-off/
healthy/transient. SAGETV_INPLACE_TEST=1 requires independently idle stock232,
checkpoints/restores the site opt-in and measures real fresh encoded packets.
SAGETV_HLS_PLAYER=native selects a separately labeled host-WebKit native row,
not physical Safari proof. First inspect actual MIME capability; default Linux
WebKit can correctly SKIP. Its real GStreamer opt-in is the test-process-only
WEBKIT_GST_ENABLE_HLS_SUPPORT=1 (WebKit GStreamerRegistryScanner.cpp), never
spoofed canPlayType. If native stalls, run SAGETV_NETWORK_CASE=native-baseline
with adaptation disabled/unconstrained delivery before attributing the failure
to the policy. Neither a host-native failure nor MSE PASS certifies iPhone.
Preserve unrelated UI sessions in non-global tests.
Keep requested/observed bitrate, renderer ACK and encoded measurements distinct.
WEB-130 local geometry/PWA checks plus exact served CSS/SW127.2 and WAR proof
qualify the compact112px by6.4px bars, not a playback-policy change.

## WEB-126 landscape reference and X-menu reload

Mobile landscape follows the operator's root ICONS_LAYOUT_MOBILE.png reference:
Gear/Help/Keyboard/Live/transport/Info/Menu/Home on the D-pad middle row; Back
below Home. Keep44px targets; below780px wrap only the utility trio above the
transport, with no video or native coordinate changes. Portrait dock and
desktop geometry remain separately owned. Test both plain and simulated safe
areas with browser-phone-controls.py, plus browser-watch-live.py,
browser-mobile-vibe.py and browser-mobile-dock.py. The phone geometry test now
counts the existing Live icon (25/33 closed/open), not a new duplicate button.

Force refresh webpage belongs in the X confirmation dialog, NOT a separate
icon. Reuse appReloadPage's distinct same-origin navigation and settings
preservation; keep playback confirmation/Cancel, default Cancel, full three-
button arrow/Tab/gamepad ownership and no command leakage. Run
browser-page-reload.py and browser-client-exit.py, then affected PWA and exact
package gates. installed-live-icon.py --run-stock232 --task WEB-126 checks
actual desktop/phone-landscape/portrait and X-menu reload without media Watch.
No physical-iPhone or playback/transcoder matrix is implied by these gates.

Packaging platform floors are explicit: Linux FFmpeg0.1.32 retains the
qualified Linux QSV queue fix; Windows0.1.35 retains Java8 process ownership
and forced-stop caption custody. Do not apply the Windows floor to Linux or
upgrade a server's native runtime just to install browser-only controls.
tests/test-build-info.py checks both exact provider IDs/minima. Installation
remains through SageTV's normal manager, guarded against recordings/users.

## Windows completed-tail qualification

Stock Windows generated recording URLs can contain literal backslashes even
when an imported fixture uses forward slashes. Run MediaUrlPathSmoke7 and the
existing DiscSourceSmoke8: escape wire backslashes for URI parsing, restore
once, strip only the slash before an absolute drive prefix and keep authorized
MediaFile/import-root resolution. A browser decoder cannot correct a Java
OPENURL rejection occurring before its media event; fix this owning plugin
parser, not Core or arbitrary media access. Verify new code through ordinary
manager installation/restart and exact WAR/served bytes. Wait for the native
GFX firstFrameCompleted before Watch; merely seeing a UI context is not STV
readiness. Observe start responses with action in either query or form body.

Use tests/stock-windows-runtime.py for the actual native STV/recording/DVD
consumer. Its seeks compare the returned absoluteTargetMs, retry only bounded
read-only inspection, and require current-source presented frames. Do not
mistake stock terminal Pause for HTML video.ended or preceding-source frames
for DVD feature motion. Use tests/stock-windows-hls-eof.py separately for the
public-HLS production decoder/caption tail. It labels its isolated DOM harness
and local candidate explicitly; keep its video visibly on-screen for WebKit,
not appended below the legacy page fold. A candidate pass is not an installed
WAR or physical iPhone pass. Never replay an uncertain Watch/Seek/control.
Serialize scripts that rebuild build/manual; test-web108.sh itself builds the
WAR. Package only after the final source/build and verify served asset bytes.

WEB-122 UI-only changes: run scripts/test-web122.sh (both-engine Watch live,
video-only picker DOM, mobile navigation and actual PWA/offline cache checks),
then package/served-asset verification and opt-in installed-live-icon.py
--run-stock232 on its disposable idle UI. Browser picker APIs are mocked in
browser-video-cast.py: do not relabel these as a physical receiver PASS. Preserve
real click activation, cancelled/failed picker behavior, unsupported/remote-
disabled states and the optional-module startup fallback. No URL/credential
export, mirrored canvas, extra stream or hidden reload/seek is permitted.
Installed UI uses isolated render-only settings, ContextMenu for local controls,
and the explicit Controls tab after portrait rotation; default Recordings is
not a missing Cast button. Page close may already retire its session: only404
is benign, and independent UI retirement must be observed before the next run.
Keep every run's captures uniquely named; retain compact reports and retire
completed images after review. Physical/cross-receiver work stays WEB-123.

Live-source preflight (WEB-121): before attributing a stall to VPN, Safari or
MIM, correlate physical source growth with stock encoder-halt logs and the
OpenDCT device/channel requests. Test232 uses only network tuner10703705-3;
production175 uses configured network tuners0/1/2. Verify configured input
providers as well as current hardware status: an idle tuner may still be
scheduled by another server. Do not silently borrow production tuners, retune
their recordings or restart shared OpenDCT. The user-authorized2026-11-23
isolation was performed through stock Setup Video Sources with the existing
FTA_60177 lineup, never property-file edits. No missing broadcast bytes can be
recovered by repeatedly restarting the browser encoder. Observe fresh phone
feedback separately from HDMI visual proof and preserve a changed-owner guard
failure instead of silently following a replacement and claiming continuity.

WEB-121: build then run `scripts/test-web121.sh`; this includes focused health/
redaction/storage, live tail/EOF/seek/wire and playback recovery tests. Preserve
the failed-before assertions for native loader starvation, clean bounded-piece
EOF versus wall-clock duration, and live-source waiting versus repeated decoder
replacement. Never equate a producer-complete classification with browser EOF.
`scripts/capture-stream-health.py` observes current/retired owners without
retuning; use it before resetting a failure. Its one-shot ordinary HLS status
reads use existing lease semantics; the autonomous recorder itself never touches
leases. Do not leave a status-poll helper running to keep a producer alive.
`scripts/verify-stream-diagnostics.py` verifies the installed persistent journal
and normal ZIP hashes without playback commands or external share writes.
The opt-in stock-live test accepts `--health-seconds 1..180` and requires actual
decoded-frame progress; recorder activity alone is not playback PASS. It also
rejects recovery requests during clean physical-piece advance. Report input
gaps honestly: a non-growing file is not a browser delivery failure, and no
decoder restart can create absent bytes. Physical iPhone/VPN confirmation remains
separate from host-browser and injected native-player regressions.
Recovery regressions must deliberately block producer preparation and prove
native GETMEDIATIME/Pause replies remain responsive; preserve exact ownership,
pending rejection, recovery-budget flags and Stop cancellation. Verify the
recorded browserRevision after Reload webpage instead of inferring a stale
page from missing telemetry. Native socket and feeder error categories are
distinct; neither alone proves the user's reported broken-pipe origin.
For the121.5 update-delivery change run ShellCachePolicySmoke (servlet API on
test classpath), browser-page-reload.py and browser-pwa.py. Verify actual
installed HTML/playback-JS/SW Cache-Control and15served assets; reload must
change the navigation query while preserving other query/hash/preferences.
Keep confirmation/Cancel and offline cache behavior. Reconnect is not reload;
missing phone revision/asset GETs alone do not establish a physical cache bug.
The bounded read-only inspect-phone-recovery.py preserves exact phone status
and recent static-asset receipts, without sending inputs or printing credentials.
Missing/empty manifest entries must not count playable or suppress startup
fallback. The clean completed-empty-seek EOS exception requires zero exit,
explicit FFmpeg empty-output receipt, known video metadata and no input error;
never generalize it to encoder failures or ordinary presentation EOF.
Use the explicit stock-live `--recovery-probe` on the disposable owned UI for
one real production recovery request plus decoded output, recording acceptance
latency separately. SAGETV_BROWSER_ENGINE selects chromium/webkit; host WebKit
is not physical Safari/VPN. Keep response/producer failure evidence even when
the gate fails, rather than writing recoveryRequests only on success.

WEB-120 affected validation: `scripts/test-web120.sh`, live-tail CPU reproduction,
`tests/browser-watch-live.py`, mobile controls and exact package/served assets.
`tests/stock-live-rollover.py --run-stock232 --media-id ID` is an explicit actual
stock/browser gate, not physical Safari proof. Watching an in-progress TV file
may resume its stock live capture even without a Record reservation. Stop only
the exact owned UI; never cancel a scheduled recording. A read-only404 during
source replacement may be observed again; never replay an uncertain ordered
Watch/Seek. Preserve normal native segment boundaries and whole-library concat.
Before staging, `commission-mobile.py` now compares the candidate package WAR
timestamp with the installed WAR's inner logical timestamp. Changed bytes with
an old epoch must fail before upload; bump the reviewed deterministic epoch,
rebuild and reinstall through the manager. Verify served bytes AND loaded
nativeSegment diagnostics, not just the on-disk WAR hash.

Task-list upkeep: workspace task.md is one current index, not a chronological
stream of provider checkpoints. Update its current summary/order in place and
retain dated evidence in the owning ledger/handoff. Reconcile completed linked
plugin tasks too, using exact scoped evidence rather than their newer version.
Run scripts/audit-workspace-tasks.py and the existing task/fix-mirror checks.
Keep unclassified failures, deferred work and publication holds visible and
distinct; Markdown cleanup never supplies a missing fix or physical PASS.
User-approved `[*]` means POSSIBLY_FIXED_NOT_REPEATABLE: preserve historical
evidence, count separately from completed/removed/active work, and reopen only
on recurrence. Never repeat passing matrices merely to remove the star. Task,
fix-ledger and workspace-index parsers must retain this separate state. Phase
labels distinguish optional/deferred, qualified-with-observations and pending
publication; completed child checkboxes do not automatically close a phase.

P15 stock-contract changes use P15StockContractsSmoke, the real TCP
MiniClientProtocolSmoke, CompanionDvdSmoke, P12AudioPolicySmoke and native DVD
protocol tests, followed by affected installed optional/native fallback rows.
Keep private DVD_DISC_* and MEDIA_STATE_URL claims absent unless implemented;
reject their SETs instead of false success. The diagnostics profile-supported
field is not a current-load negotiation receipt. P17 clean verification accepts
--task WP15-001 for an isolated195-input/14-command exact rebuild. Run the
package guard against shadowed Core and duplicated optional providers. A
supported stock alternative does not implement a private transformed transport;
keep WP15-002 unavailable rather than checking it off to empty the list.

Final physical VPN scope: use actual reviewed HDMI and the existing encrypted
BLE bond; paired Wi-Fi inspection is unavailable on cellular. The bounded
iphone-remote-hdmi.py helper defaults to owning WEB023, accepts1..12 explicit
non-text keys and8..30s capture. For loaded playback require exact --media-id;
for electrical audio use --audio --audio-device "Digital Audio Interface (USB
Digital Audio)" rather than changing local config or opening a webcam mic.
Before every input inspect the foreground/overlay and exact phone activity.
No capture/transport receipt is an automatic visual PASS. Review advancing
fixture PTS/frame counters; a native reader clock or Space sent after EOF is
not pause/decoded output proof. Keep public stock setup vs real BLE vs actual
HDMI distinct; do not replay uncertain input. A zero-input preflight rejection
may be corrected before a separately planned action. Restore caption Off/test
media and disable the firmware keeper at teardown; keep bonds/profiles intact.

WEB117 physical DVD regression: exercise remote FF/RW with real keyboard
Enter as well as pointer clicks. Local overlay focus/navigation must not
cancel the existing source-owned Time Scroll transaction; stale/public-menu/
editable/modal/source loss still cancels. Verify both native public contentState
and normal browser Video Information presentation before judging DVD-only keys.
An old native thumbnail rectangle can survive a fullscreen OSD transition.
For physical Apply, inspect exact ffmpeg.real child bitrate and actual segment
raster through dvd-field-observations.py on native Python3.12/Paramiko; the
paired PMD virtual environment intentionally does not supply SSH dependencies.
DVD HLS status has no ordinary effective profile field. Observe eight settled
seconds of real pictures/title clocks, restore exact current saved defaults,
and distinguish helper/metadata failures from production defects.
Run verify-clean-runtime.py from the native workspace host, not the DEV alias;
it invokes DEV itself and refuses a false workspace root before staging.

WEB115/116 chapter investigation: use --chapter-only --chapter-transitions 8
(maximum8), optionally --segment-delay-ms 150 (or500) for an explicitly synthetic
segment-request start delay in only the owned browser context. This is not WAN
acceptance. Native reader chapter can lead presented pictures; compare actual
new-source frames against paired advancing native clocks after the current
producer feedback settles. Do not seek/replay chapter inputs or change clocks
to satisfy the oracle. Preserve unique original024848Z until its cause is known.
WEB116 --diagnostic-self-test validates the normal exported report.json/hash
and bounded element fields in both installed engines, without source overrides.
The intentional post-success harness exception is not a playback regression.

WEB114 chapter-only diagnostics use stock-dvd-transport-search.py --task
WEB-114 --chapter-only with the existing exact generated fixture/disposable
UI. Observe one public chapter intent; never replay it because an observation
times out. Before Stop capture public producer status and normal redacted
browser diagnostic ZIP, not just the last screenshot. --diagnostic-self-test
is an intentionally injected harness exception after actual successful
playback; diagnosticSelfTestPassed is NOT a playback-failure/recovery PASS.
Do not patch startup heuristics on the basis of non-reproduction or a current
kernel log that lacks historical failure evidence. Keep unique024848Z active.

WEB113 DVD transport search: run scripts/test-web113.sh for the affected input,
both-engine atomic batch/context/source-retirement and existing control/DVD
guards. stock-dvd-transport-search.py exercises the exact disposable stock232
UI and generated90s DVD, both engines and --stv stock|sagemc. Source-candidate
routes and read-only --diagnostic-probe are diagnostic labels, never installed
byte/performance acceptance. After the normal manager update, run without
either flag; independently observe owner retirement before the next field.
Stock DEFAULT-STV file identity changes before initialization is ready: wait
for its actual rendered menu before Watch, then restore the original SageMC
via its public Home hook before closing. Its absence is UNKNOWN, not restored.
Use second-chapter/forward bounds/rewind before accepting the short fixture;
SageMC's150s native Time Scroll step can otherwise correctly select EOF/root.
No fake256x decoding, unsupported Core flags or optional-extension requirement.

WEB112 special-key mapping is opt-in: new DOM key names have no new default
command. Preserve Backspace=Back, local fields/IME/modifiers and explicit none.
Run test-vibe-input.js, browser-special-key-mappings.py and browser-mobile-vibe.py
for editor/persistence/one-command/ownership guards, then exact package/clean
WEB-112/normal manager/served-byte checks. Browser DOM transport is synthetic;
never delete a real recording or claim physical remote/phone proof for it.
Keep input/SW cache revisions aligned. No Java behavior changed in this batch.

WEB110 native angles: verify-stock-dvd-angle.py reads/disassembles only the
canonical hash-pinned upstream9.2.17 JAR; never modify or load replacement Core.
Native213 is no-op/false on those bytes. stock-dvd-angle.py compares real
branch RGB/new frames, with SAGETV_ANGLE_COMPANION=1 selecting only the existing
optional owned navigator. Restore its exact hook/options before retiring the
owned UI. A native failure is not fixed by the optional PASS; keep the capability
unavailable and don't replay controls/auto-enable hooks/fabricate angle state.

WEB109 real WebKit visibility preflight: run tests/webkit-window-visibility-probe.py
through xvfb-run -a on its own private display. The script validates the private
Xauthority path, owns/retire its window manager, minimizes the uniquely titled
window with native xdotool and separately reads document visibility. Exit77
means actual minimized window but backend page still visible, not media PASS.
Never override document.hidden or protocol visibility to manufacture acceptance.
No server/phone is used; do not rerun media merely to repeat that backend limit.

WEB108: scripts/test-web108.sh is the impact-selected local DVD Apply group.
Use stock-dvd-clock-field.py with SAGETV_DVD_RECONFIGURE_PROBE=1,
SAGETV_DVD_RECONFIGURE_CURRENT=1 and SAGETV_DVD_RECONFIGURE_APPLY=1 for the
installed production API; add SAGETV_DVD_RECONFIGURE_PAUSED=1 for native pause.
Only public MCP fixture setup/Pause/Play is used, never MCP Seek in Apply mode.
Profile/status observations MUST use GET: empty POST streamSettings resets the
client configuration to server defaults. Preserve exact lowercase wire strings.
Count ffmpeg.real, not its MIM forwarding parent as a second encoder; verify
the actual owned output segment raster separately from WebKit display/PAR size.
Paused stock DVD withholds source processing until Resume; never demand new
frames/FLUSH before Play or silently unpause a user's session. Require real
post-resume new-source frames, encoder target, settled native clock and exact
next-source profile restoration. See docs/parity/DVD_PROFILE_APPLY.md.

User2026-11-19: multi-hour/three-hour soaks are NOT required. Do not start or
restart one; the field runner rejects its old elapsed option. Short focused
checks cover affected playback/offset/coexistence behavior. A long-duration
source does not require playing its entire duration. Historical elapsed notes
below retain observations, not a current release requirement.

For non-disruptive playback, validate known activity counts but allow multiple
clients/recordings. Do not use safeToRestart as playback admission. Record
co-tenancy and label container resources shared; require isolation only for an
explicit isolated-resource experiment. Never stop or control foreign sessions.
Unknown activity still fails closed. Actual updates/restarts retain their
existing recording/client guards; this correction does not weaken them.

WEB106 focused command: tests/stock-multiclient-captions.py
--coexistence-check --engine chromium|webkit. It creates exact disposable
fixture UIs, runs one20s profile consumer while both play, then verifies the
same existing producers/settings before retiring only owned sessions. Reject
an already-used field identity. --source-changes selects only generated
recording/caption/native-clock changeovers. Unknown native/UI Stop receipts
must not be retried from finally; bounded offline extracted-method tests cover
that ownership rule. No phone access is involved in these host gates.

Current non-phone review: docs/parity/NON_PHONE_READINESS.md. Do not turn its
missing source/equipment/peer or unsupported/unqualified backend contracts into
PASS, or publish while approval is withheld. Available bounded WP11 scope and
WEB106 are complete; original full-input case remains separately WEB107.

WEB105 future runs publish a unique cancelFile basename in the active report.
Create only that exact owned cancel-request file to request cooperative Stop;
SIGINT also requests cancellation rather than cancelling asyncio's finally.
Wait for profilesRestored/observerRestored/cleanup receipts before saying the
phone is restored. The runner now persists exact originals/configured defaults
BEFORE borrowing in an ignored task-owned *.private.json checkpoint; never
include its contents in support bundles, Git or public results. This protects
future runs only: the interrupted223249 run predates this checkpoint and still
has UNKNOWN restoration. Do not infer or fabricate its original saved values.

When physical phone access is withdrawn, stop its runner, disable the explicit
firmware keeper, verify no input leases and independently check owned server
retirement. An interrupted finally is NOT profile-restoration proof. Preserve
its checkpoint and CAS-restore only when that same phone returns; do not inspect
or send further phone inputs. Continue independent host work immediately.

WEB104 headless WebKit uses build-env's prepare-headless-audio.sh and an
actually viewport-visible test video. Missing Pulse output produces a backend
failure even when muted; an offscreen appended element separately produced
Failed-to-push-buffer after audio readiness. Visible20s real HLS passes with
unchanged production code. Preserve minimum failure evidence and label this
as harness/backend correction, not iPhone/encoder regression or acoustic proof.

Build AND package candidates inside the reusable DEV toolchain. Host Python's
compression output can differ even when the embedded WAR is byte-identical;
that does not satisfy exact installer reproduction. Do not stage a host-built
ZIP then weaken the clean check. Finish same-toolchain package/exact metadata/
clean verification before manager staging, and leave commissioned hashes intact
when merely checking a different compiler/compressor environment.

WEB104 public `/api/hls` accepts the existing validated stream profile only
when `stream_profileSchemaVersion` is explicitly present. Unmarked callers
retain the legacy null-options builder. Normalize delivery to a playlist only,
never silently convert strict Copy/audio policy. Validate before SageTV source
access and use the existing session planner, limits and ownership; no Core or
global encoder settings. The elapsed soak opts into 1000kbps/480p and checks
actual requested/effective values before attachment, aborting only its owned
consumer after45s with no presented-frame progress. Never call an intentionally
cancelled legacy8Mbps setup run an elapsed-three-hour result. Run public-profile,
hardware-command, existing HLS/streaming lifecycle and exact package/clean
checks; qualify live public-HLS actual frames on host and native iPhone.

The225500 elapsed gate later intentionally retired at~42m when the phone UI
became active after withdrawal. Preserve user playback; independent verification
of owned API404/no matching process is read-only via verify-long-source-retired.py.
Do not replay Stop or sum partial runs into a continuous3h result. Treat the
partial resource trend as observations, not proof of leak/no-leak.

WP16 disk-pressure integration uses verify-hls-disk-pressure.py after compiling
HlsDiskPressureSmoke and preparing the actual shared-process test provider.
Reuse the exact local DEV image, --pull never, no network, read-only project/
root, dropped capabilities/UID65534 and a private192MiB tmpfs with bounded
CPU/RAM/PIDs/time. Never fill /tmp, /dev/shm or a server/host filesystem shared
with users/other tests. Verify genuine filesystem pressure and real producer
retirement/recovery, then exact label/image-guarded sandbox absence. This is
isolated integration proof, not physical-browser/server ENOSPC certification.

Historical WP11 elapsed experiment (removed from required scope by user):
elapsed soak is separate from source-duration/large-offset coverage.
stock-long-recording-field.py keeps the default20..600s bound; an explicit
--only-soak --elapsed-soak-seconds7200|10800 starts source0 and records real
wall time, frame/source/clock/resource checkpoints every30s. Require10GiB
initial spool headroom, abort owned consumer below2GiB or unrelated activity.
Never repeat unrelated completed offset/tail rows or mutate original watch
state. Stop intent is set BEFORE dispatch; unknown receipt is never replayed
from finally. Do not restart/update the server while its owned soak runs.

Original CEA field inventory: inventory-original-caption-services.py reads
only the exact bounded/hash-verified retained18.8MB broadcast prefix into
OriginalCaptionInventory (real A53 tap). It exports service counters, never
payload. A source-present service is a candidate, not physical acceptance;
608 field2 may contain non-caption data and is not certified by pair counts.
iphone-original-cea-field.py uses real frames/rendered lengths, normal form
Save before Watch and Apply for a current service change. Save alone explicitly
does not change existing playback. Its expected stored stream must include
caption-authority derivation, and unknown restoration retains the in-page
checkpoint rather than discarding it. No ordered Watch/Apply/Seek/Stop replay.

WP04 focused follow-ups use --eof-only for tail/reconnect, --seek-bounce for
48→5→60generation changes, --fullscreen for supported public view completion,
and --capture-visible for a triggered3s HDMI record while bitmap pixels are
actually in the visible fullscreen viewport. Do not count a capture started
after the source ended as placement proof. Ordinary EOF helper must observe a
fresh production events request after reconnect, not obsolete ResourceTiming.

WEB101 ordinary-caption EOF: do not clear on arbitrary ended, encoder EOF or
rounded duration alone. Require actual video.ended, a decoded picture, exact
current producer, stopped clean exit0/ENDLIST, explicitly non-growing source,
file-tail agreement and no paused/recovering/DVD owner. One generation-scoped
presentationEnded callback stops caption/subtitle presentation only; it never
Stops/seeks/restarts media or touches DVD menu SPU. Health may observe a late
exit receipt after the real ended event; stale replies cannot clear a successor.
Run95player tests, both-engine DVB EOF7/ordinary7/DVD11 DOM checks, package/
clean extraction and actual generated phone EOF/reconnect; preserve profiles.

WP04-007 transition fixture: create-caption-transition-fixture.py owns the
canonical generated64s A/V transport, two visible DVB languages and source PMT
versions0/1/2/3. Validate CRC/PID/descriptors/hash with
tests/test-caption-transition-fixture.py and actual RGBA with
DvbTransitionFixtureSmoke. validate.sh runs the latter only when the canonical
fixture exists; ordinary CI never downloads private media or stages a server.
stage-caption-transition-fixture.py is explicit, idle-only, new-directory-only
and readback-verified before one public scan. After an uncertain staging
receipt use --verify-existing, never replay upload/scan. The physical runner
iphone-caption-pmt-field.py observes real video callbacks and rendered pixels,
borrows/restores exact profiles and distinguishes source read-ahead from the
presentation time at16/32/48s. Local fixtures are not broadcast or phone PASS.

WEB100 PMT retirement must preserve source read-ahead without early display
changes. DvbSubtitleSession emits a source-timed clear plus selectionChangedMs
for PMT-driven removal/restoration; explicit user selection and Off stay
immediate. The browser compares this optional timestamp to sourceTimeMs minus
captionOffsetMs, preserving legacy peers and generation guards. Run actual
DvbPmtTimingSmoke (fail-before11s versus source15960ms), four generated phases,
32DVB/PMT4 vectors,18service-loss/TT5/DVB3 controllers and both engine DOM
offset/Off/render tests. Then normal manager/exact assets/stock and the same
phone transition plus original UK compatibility; no unrelated DVD matrix.

WEB097 default public HLS must share QSV's forced_idr=1 boundary contract
with StreamCommand. Finite EOF can hide a missing-IDR startup problem: use the
canonical owned20s prefix with raw input held open22s and observe the first
atomic playlist before hardware fallback's15s deadline. benchmark-web097-live-idr.py
uses the captured fixed command/exact source/hash, independent idle guards,
bounded owned timeout and enumerated output cleanup, never global process kills.
--original-completion separately validates the complete retained owned file
and actual ffprobe duration, not airing duration or simulated live growth.
Drain SSH stderr while observing long encoder comparisons too; otherwise a
diagnostic tool's own full receive window can manufacture backpressure.
Keep synthetic held input, complete-file replay and actual natural phone
recording completion distinct. Do not rerun unrelated DVD/Caption matrices
for this default-QSV-only option; affected command/HLS/producer gates suffice.
Plugin packaging reads its platform dependency minimum from release.properties;
test-build-info checks both XMLs against it. No hardcoded stale minimum.

Live programme boundaries require actual Watch(Airing), new native MediaFile,
new advancing decoder output and no repeated tune; a standalone HLS recording
completion is not that proof. For basic Pull, stock Core already understands
four-byte signed -1 EOS. Forward only exact-generation successful completed
presentation, never encoder read-ahead, a failed producer or DVD drain. Keep
finite recordings distinct; do not synthesize a channel tune at ordinary EOF.
After a manager update verify the exact live WAR and protected stock hashes;
record development package/revision separately from unchanged browser assets.

When the user prioritizes physical phone work, finish the executable iPhone
rows before desktop-only matrices. Keep HDMI/one paired inspector and the
firmware-owned idle worker; do not run a second inspector or flash the bridge.
During natural recording completion, use the actual EPG end, not CancelRecord:
stock can remove an early-cancelled partial recording, while CoreWatch can keep
a live tuner lease. Neither is proof of a browser completion defect. Own only
the new reservation/media and checkpoint the previous empty/nonempty schedule.
Wait for a usable current HLS playlist before native attachment; transitional
fallback warnings/old killed-producer ENDLIST are not a ready replacement.
Record actual effective hardware stages, never label software fallback fullGPU.
At natural completion ENDLIST can precede the monitor's exit receipt. Save the
observed completionStatus and wait read-only for running=false and a real
exitCode before checking success; do not immediately Stop a flushing producer.
producer_completion_ready's executable regression covers that publication race.
After EPG end the guide's time window can omit the airing: verify exact-ID
recordStatus and owned media deletion independently, rather than requiring a
past airing to remain in the current guide. Unknown mutation receipts are not
permission to repeat Record/Cancel/Delete. Keep failed raw evidence minimal.

For WP12 source-transition checks, retain canonical generated inputs and recipe
separately from raw field output. Validate actual PMT CRC/version/PID/language
and decoded source layouts; distinguish tail-probe discovery from live UI track
refresh. Test actual selected audio from decoded output, not a language label.
Use same-page authenticated fetch for owned HLS segments and FFmpeg duration
`0.5`, not`.5`. A failed final read-only retirement observation must still write
the field report as failed/unknown; independently verified later idle is cleanup
evidence, not proof of timeout cause or permission to replay Watch/Stop.

Sustained playback can use stock-long-recording-field.py --only-soak with an
explicit20..600s duration: one late offset, actual modules/encoder/browser,
resource sampling every30s and no repeated completed landing/tail matrix.
This public HLS producer does not modify the source's watched/resume state.
Zero native UIs does not mean no disposable HLS encoder; stop only the exact
owned producer. Record actual elapsed duration/peaks/frames and final retirement;
ten minutes is not an elapsed multi-hour or live-changeover certification.

For missing-language policy fields, read the public visible osdMessage, not
miniclient.js private closure variables. Strict rejection must create no HLS
producer or presented output; default and first must verify actual effective
audioStreamIndex plus advancing frames. Retire a selected but producer-rejected
native file with one public Stop, then independently observe UI retirement.
Never reinterpret a harness ReferenceError or asynchronous retirement as a
production decoder failure. Use isolated browser profiles, not phone defaults.

The public recordings API caps one response at500. Do not infer no long-source
fixture from that page: inventory-long-recordings.py unions bounded supported
text queries and requires stable total/complete unique-ID coverage. Public
Airing duration is not source duration; verify readability and actual ffprobe
duration before large-offset tests. A5.5h-class file check is not5.5h elapsed
soak. Prefer disposable HLS API producers when they satisfy the gate without
changing original watched/resume state; distinguish that from STV/native tests.
For isolated module tests do not use codec-test.html: that diagnostic page
preloads five other native videos; WebKit Failed to push buffer disappeared
on an isolated document. That comparison is not a proven firmware/encoder
defect. A fulfilled empty document then failed Chromium subresource loading
with net::ERR_FAILED, even after auth priming. Use the real index.html shell
without selecting media, not browser security-disable flags or mocked assets.
All runtime modules/vendor/HLS/status/segments remain real. Mirror production
progress/playing/canplay/ended listeners and label absence of native STV
controls. Record harness failures separately from production playback bugs.

Physical helpers must resolve current playback revision from BUILD_INFO and
the actual HTML script, using scripts/field_candidate.py; never hardcode an
old WEB task revision. Safari may retain video.currentSrc after unload: require
assigned src/srcObject and readyState when checking decoder ownership. An old
currentSrc string alone is neither a live decoder nor a failed teardown.
Keep paired inspection's asyncio pump running during server controls: blocking
HTTP activity/Watch/Seek/caption commands must use await asyncio.to_thread.
A slow synchronous public Seek can otherwise stall and lose the inspector
channel despite successful playback/Stop. Record phase, independently observe
state after timeout, never replay the input or steal an attached inspector.
The standalone DVD field runner must create its exact-session field-owner
observer when a page reload removed it, using tests/iphone-field-owner.js;
borrow an existing owner without replacing it and retire only one it created.
Missing __iphoneGate is a setup failure before Watch, not a wireless/media
crash. Its activity guard also runs off the asyncio transport pump.

Broadcast PMT retirement uses the existing explicit numeric selectedTrack and
service state in the current generation. Clear only the owning local subtitle
surface and its queued retired cues. Missing/string/unknown metadata remains
legacy-compatible, not a fabricated service loss. Run service-loss16/actual
generated decoder PMT4/TT5/DVB3/STV10 and both production browser render suites,
then normal-manager/live WAR+controller asset/real original UK and phone gates.
Never attribute an unclassified older Off failure to this case without evidence.
Interactive manager quit/Stop is not independent native retirement: wait using
wait-owned-ui-retirement.py before the next idle-only test, no Stop replay.

Native HLS MIME reporting is not proof a particular encoded stream decodes.
For WEB096 distinguish requested Native and actual Native versus HLS/MSE.
stock-delivery-lifecycle.py is strict by default (allowFallback=false); use
explicit --allow-native-fallback only for the native compatibility row. Require
the SAME producer, zero server recoveries and actual advancing MSE frames;
never label that a successful native decoder. Strict negatives stay visible.
Only explicit native decode/source errors3/4 BEFORE first picture may trigger
the one-shot ordinary-HLS handoff; remote playback, DVD, old generations,
post-picture failures, network/autoplay and unknown metadata retain their
existing owners. Preserve Pause and original attachment offset, not an
undecoded timestamp. MSE-unavailable/attachment failure cannot retry encoders.

For WP14 real destination tests, the same-origin actual fetch ArrayBuffer is
the binary oracle; Chromium CDP attachment response.body may be text-transcoded.
Check saved ZIP magic/hash independently before blaming runtime export.
Use only the explicitly approved dedicated destination, preserve the original
environment privately server-side, and restore with the container helper's
explicit --unset-env when JAVAOPTS was originally absent. Verify default-off
write/retry refusal and real browser ZIP download after restoration. Never
turn a test destination into a permanent household setting implicitly.

WP16 real visibility tests must observe `document.visibilityState=='hidden'`;
opening another headless tab or waiting is not background proof. Playwright
forces focus by default. For Chromium use the existing reusable dev container:
`docker exec -u 0 -w /workspace/web-client-plugin -e SAGETV_WORKSPACE=/workspace/web-client-plugin opensagetv-vibe-dev bash scripts/setup-field-display.sh`.
This optional Xvfb/Openbox/xdotool setup affects the DEV container only, never
the SageTV image/server. Run stock-delivery-lifecycle.py with `--headed` under
`xvfb-run -a`. Its public CDP `no_defaults=True` attachment uses the owned
default context and origin-restricted authentication, not a second context or
patched Playwright source. Restore the real window and release only its own
display manager. WebKit's forced-visible automation remains unqualified for
background. Check native HLS MIME support before any UI/Watch: this Linux
WebKit build reports neither MIME, unlike physical Safari. Unsupported and
unobserved are separate from FAIL and PASS. Keep physical iPhone proof separate.

For user-confirmed cellular/VPN, Wi-Fi inspection may be absent. Review actual
HDMI foreground before ESP32 input. iphone-remote-hdmi.py records six real keys
on the known stopped SageMC main menu; analyze-remote-menu-hdmi.py checks the
fixed green selection geometry. Neither submission receipts nor capture
startup is a calibrated input-to-photon clock. Preserve review, actual route,
input method and visible content/clock/Pause/seek observations; do not label
keyboard or MCP setup as physical finger/long-press-button evidence. Do not
invent bandwidth estimates for Safari native HLS or silently enable adaptation.

Before reporting parity/release progress, reconcile TASKS.md and the current
upstream ledger: run scripts/reconcile-task-index.py and
scripts/reconcile-fix-ledger.py read-only, review differences, then use their
explicit --write modes and run tests/parity/test_task_index_sync.py and
test_fix_ledger_sync.py. Checked target tasks mean only their documented scope;
never rewrite pinned historical implementation status, references or reasons
into an inferred physical/all-service/WAN PASS. Keep optional Core work out of
the stock release. Update the workspace execution order when dependencies
change; completed tasks belong only in the checklist change ledger.

WP17 clean verification uses every runtime build input plus the selected test
dependencies, no .git/private config/media. Include test-miniclient-core.js
for the playback suite and browser-vibe-display-smoke.py for PWA's INIT import.
Normalize ZIP directory separators and reject absolute/drive/parent paths;
Windows Compress-Archive can emit backslash directory names. Run the clean
extraction in a system-created directory inside the existing dev container,
which owns the pinned WebKit cache; a fresh base image is not that browser
runtime. Do not copy/redownload the browser cache or depend on the source bind
for missing tests. Compare the extracted WAR to packaged and live WAR hashes.
Keep an unedited selected test transcript; label minimal build-input archives
separately from full source/release handoffs. Retire owned staging only after
hash/containment/reparse/collision checks; never overwrite a deleteme collision.
Run tests/test-build-info.py --exact-artifacts when qualifying the recorded
commissioned package. CI's default mode checks version/epoch/hash format and
its OWN freshly built embedded WAR/XML MD5: Java11 and Java25 compiler-emitted
class bytes differ even with --release8. Never overwrite the installed-build
hash record or claim cross-compiler byte identity to hide that distinction.

WEB092 idle ownership: desktop streaming receives NDJSON keepalives but has
no media-state pump while menus are idle. Only actual received bytes may
trigger a bounded producer-mismatched state receipt; no clock/volume/Pause
write, status polling heartbeat, queue-draining side request or background
lease timer. Require actual no-media survival>90s AND lost-beacon/native UI
retirement. page.close(run_before_unload=True) returns before asynchronous
close: wait for its close event before judging console/fault execution, then
poll independently. A source-routed Playwright check is not installed proof.
Use verify-live-web-war.py after normal manager: served JS/health alone cannot
prove new Java classes loaded. Reuse MediaProbe's ffprobe resolver for disc
inspection instead of assuming the stock server PATH or sibling location.

WEB088 browser transport ownership is distinct from native playback clocks.
Status/diagnostics must never renew it. Actual state/long-poll and delivered
HLS/continuous-media bytes keep foreground/background consumers alive; detached
stream grace allows recovery. Old stream completion cannot detach a newer
generation. Pagehide beacons remain best-effort, not cleanup proof. Field-run
three separate Exit/reload/page-close cycles with an actual live encoder and
exact spools observed BEFORE disconnect; require independent native retirement,
no encoders and removal of those SAME spool paths afterward. Do not kill jobs,
replace a leaked session or replay controls to manufacture a PASS. Cleanup
takeover, if required, is separately reported; initial152501Z remains unknown.

BRIDGE029 keep-awake runs on the commissioned ESP32 firmware, independently
of PC/MCP/manual input leases. During authorized phone gates explicitly enable
firmware_keep_awake/idle60s once and read its actual state/counter; do not start
a host renewal loop. It stops on reset/disconnect/BT Off/global Stop/report
failure, never silently rearms or sends keys/unlock. Scoped input Stop leaves
the separately enabled worker alone. Six-minute no-host-input phone evidence
is scoped to this device/session, not an indefinite no-lock guarantee. Disable
it after the testing session unless the user requests otherwise.

WEB087 one-picture native fallback qualifies the exact1us/HAVE_METADATA-only
Safari failure before touching the decoder. Require fresh native menu/owned
HLS+DVD generation, clean ended converter/one tiny segment/no actual frame,
empty browser buffer and permitted fallback. Load HLS/MSE once, recheck policy/
pause/source after await, then reuse the SAME producer. No Core/FFmpeg change,
server seek/recover, synthetic frame or duration inflation. ManagedMediaSource
temporarily disables remote playback on that video element; restore its exact
prior value on Stop/source change/failed attachment. Keep selected Native
separate from actual HLS/MSE in diagnostics. Run76playback guards, affected DVD
DOM, packaging/normal manager and actual iPhone held-menu/Select/new-root gates;
same-source test instrumentation is not installed production acceptance.

WP08-006 one-picture field gates use fixtures/one-picture-frame-observer.js:
count only a current-source decoded callback with ready raster and matching
actual mediaTime. Source URL change, a previous feature's frame count, cached
still or SPU pixels alone is not a new root picture. Do not write clocks/ended
or repeat Watch/Select. Wait read-only contentState readiness before one public
fullscreen completion; known preview/fullscreen only. Run the7observer guards,
HlsOnePictureManifestSmoke and both actual browser one-picture gates. Target0→1
serving normalization changes only the HLS target bound, not EXTINF/media/EOS.
Actual native iPhone remains a separate gate. Keep root-return oracle mistakes
distinct from converter defects and record invalidated provisional results.

WP06 genuine IDX/SUB integration uses only owned fixture78951 beneath the
established test import root. stage-vobsub-fixture.py refuses existing paths,
checks public sample hashes and SFTP readback, then uses one public scan.
stock-vobsub-field.py distinguishes generated A/V from genuine subtitle data,
actual host playback from iPhone, and decoder output from physical sync.
Missing-palette setup moves/restores only the exact hash-guarded fixture IFO;
never rename a user's source or infer successful restore without readback.
Do not stop an old ordinary-subtitle worker with fileCues.clearAll: the new
seek producer may already have queued data. Retire only that worker's token,
and retain the before/after lifecycle regression plus actual server seek gate.
The missing-palette case uses SSH only to move/restore that exact test IFO.
The base browser venv does not include Paramiko. Before that optional gate,
run `bash scripts/setup-field-ssh.sh` inside the reusable dev container at
`/workspace/web-client-plugin`. It installs the pinned commissioning-only
dependency into existing web-python and checks it; no image/server/Core,
ADB identity or phone change. Ordinary browser gates need no SSH dependency.
If the container cannot verify the package CDN certificate, never disable TLS
verification/use trusted-host. Download the locked Linux CPython3.14 wheels
with verified host TLS to workspace artifacts/temp/field-ssh-wheels (pip
download --require-hashes --only-binary=:all: --platform manylinux2014_x86_64
--python-version 314 --implementation cp --abi cp314
--dest ../../artifacts/temp/field-ssh-wheels -r requirements-field-ssh.txt).
Copy that owned wheelhouse once to a system temp path in the existing container
and set SAGETV_FIELD_SSH_WHEELHOUSE to it for the helper. Offline installation
verifies all seven pinned hashes. Retire disposable wheel staging after use;
the source requirements/helper retain the reproducible contract.
SSH commissioning also loads ignored persistent config/ssh_known_hosts.local
in both host/container, in addition to normal user known_hosts. Populate only
from an independently already-trusted host-key record; never fetch/accept a
new key automatically or use AutoAddPolicy. Current exact175ed25519 record was
copied from the Windows user's existing trusted known_hosts. RejectPolicy
remains; keys/credentials are not committed or retired with temporary captures.

WEB081 completed-source tail and native-HLS reserve ownership: keep actual
ended separate from rounded EXTINF/file duration. Never set ended/time or
restart a healthy producer to turn a gate green. Ordinary finite-tail handling
requires stopped ENDLIST, explicit activeRecording=false, decoded real final
samples and file-end agreement<=1s; unknown/live/truncated output stays guarded.
Native Safari owns decoded-buffer/loader transitions, not the MSE pause policy;
observe readyState/buffer ranges/intent separately. Real autoplay denial is not
an encoder failure: use one visible Play button/real BLE key, never synthetic
click/unmute/repeated Watch. iphone-recording-eof-gate.py --observe-existing
continues the exact canonical source without replaying a failed/uncertain
activation or Watch. Capture real ended and cleared feedback;70focused playback,
affected PWA/DVD-DOM, stock-byte and actual native DVD/Copy compatibility gates
are selected by impact, not the full unrelated device matrix.

WEB079/080 portrait is content-first: default Recordings, direct grouped
library/Guide actions; optional Controls, landscape for native STV navigation.
Do not require users to navigate tiny STV menus for ordinary portrait browsing.
Run test-mobile-library.js,
browser-mobile-library.py and affected mobile-dock/PWA/spacing/reload tests.
Mocked actions are not live tuning/scheduling proof. Qualify actual connected
STV Info through the production action and inspect its selected title, with
no Watch or recording side effects. Use only existing owned fixtures for any
mutating recording gate, never schedule real user guide programmes just to
make a test green. Import folders use public relative metadata only; invalid
paths stay omitted and old servers fall back safely to root items. Guide
logos/airings come from this server's viewable lineup. XMLTV setup/lineup/import
is separate XMLTV-PLUGIN-006; do not hide stale/missing EPG behind synthetic
catalog data. Preserve stock Core and175 setup. Phone access resumed2026-11-18;
use fresh exact-page/visible ownership proof rather than historical page IDs.
An explicit later phone pause still takes precedence over test continuation.

WEB078 App/Reload webpage is a deliberate ordinary same-URL navigation, not
Reconnect/list Refresh or an automatic recovery. Preserve local preferences;
loaded video requires the browser-native confirmation (Cancel stays unchanged).
browser-page-reload.py qualifies actual Chrome/WebKit navigation and persistence.
Use the real BLE keyboard on an explicitly prepared visible phone button, then
independently rediscover the page; an unloaded observer cannot prove keyup, and
unknown navigation delivery is never replayed. No autoplay-policy bypass.

WEB072 legacy A53 sidecar timestamps start at zero for every producer. Native
browser reports are file-relative: gate A53 extraction/emission at file clock
minus exact producer start, without rewriting encoded PTS/control bytes.
Teletext queues already use file-relative cue times and must not be rebased.
LegacyCaptionBridgeSmoke includes a failing-before real-bridge30s seek case;
qualify actual no-trace CEA/Teletext CC1/CC2/Off and post-seek pictures. Callback
counts alone are not visual PASS. Keep old wrong-epoch screenshots until a
compact before/after report records the correction, then retire them normally.

WEB077 adds explicit extra portrait spacing, not another assumed device-safe
inset. Settings/App/Portrait top spacing defaults24px,0..160, live browser-only
stage padding. Run browser-portrait-spacing.py and existing mobile-dock/PWA/
settings/profile gates, then package/manager/served bytes and actual phone.
Home Screen adds its OS inset once; ordinary Safari retains its toolbar.
Do not shift canvas/video separately or reinterpret layout as a media restart.

WEB076 list Play completion is browser-owned and bounded: public stock exact
media/airing loaded/no-modal read, known native preview, one ordinary TV, then
observe native fullscreen. No new Core protocol/MCP dependency. Native input,
tab/context/connection retirement cancels; never replay Watch/TV on unknown.
Run mobile-fullscreen-smoke.js, StockClientPlaybackSmoke, mobile-dock DOM/PWA,
actual stock-mobile-dock-field fullscreen row and real BLE iPhone Play. Native
SetFullScreen controls the desktop window, not STV video; do not substitute it.

WEB075 is CSS/PWA safe-area only: affected mobile-dock and PWA fixtures plus
packaging/served bytes and actual standalone iPhone y-offset. Emulated notches
use the explicit test custom-property override, never claim physical env()
support from host WebKit. Actual074 phone proved stagey0 under system icons.
Do not pad the video/canvas independently, duplicate Safari toolbar safe area,
force fixed device offsets or change playback/stream profiles for this fix.

WEB-074 portrait changes use browser-mobile-dock.py plus affected mobile-vibe,
landscape phone-controls, orientation-surfaces and PWA gates. Keep the control
deck modeless: physical keys on the stage still control SageTV; focused deck
buttons/tabs/search own local navigation. stock-mobile-dock-field.py qualifies
existing read lists and one exact media-ID Play through the production plugin,
presented frames, active rotation, unchanged profiles and independent retirement.
It never starts media through MCP or creates a scheduled recording. Run actual
stock host engines serially with the shared test ID; physical phone follows
only when available. See docs/PORTRAIT_BROWSER.md for the plugin boundary.

Real media field observers must preserve native function receivers: capture
fetch in a local and invoke real.apply(this,args), never as an arbitrary
checkpoint object's method (Safari rejects that receiver). Observe cloned
production subtitle responses rather than draining its queue with extra polls.
Physical DVD selectors can be legacy2/direct0x22/HD0x42 for the same sparse
Spanish stream; test physical identity, not one optional flag representation.
An existing menu can retain a valid decoded still without new frame callbacks;
require new frames for moving-feature acceptance, not menu setup. Watch on an
already loaded same disc is not guaranteed to create a new source. Reset only
exact guarded generated fixtures after Stop, never original recordings.

For recording seeks, require a new owned producer, changed browser source and
new presented frames before caption/clock acceptance. Compare the public raw
file-relative clock, not the absolute TV airing epoch. Core clock observation
can lag browser presentation; record bounded fresh samples, never replay Seek
or accept old buffered frames merely because time advances. Unhandled vendor
worker teardown errors remain failures even if playback appears to recover.
Explicit browser Exit now uses acknowledged exact-session Stop; pagehide
beacons remain best-effort. Verify actual native UI retirement independently.

Actual phone commissioning uses ESP32 BLE for input and paired exact-page
Wi-Fi observation only. Prefer one bounded attachment for OSD setup/input/
timing: reconnecting between probes can expire a short-lived native bar.
SageTV7 Info opens details, not SageMC's OSD. Verify current source/native
placement and actual marker before one click; do not blindly reuse TV toggles
or Play while a media-list item is selected. The stock physical helper guards
exact Nightline27166/UI/STV, observes trusted BLE and native marker/new frame
separately; its pixel geometry is test-only. Home restoration is asynchronous:
poll captions.get until the original SageMC STV is independently confirmed.
Physical MAIN Enter/Space now send20/59; do not regress exact tag ownership.

WEB-058: a completed decoded DVD menu with fresh same-generation native truth
can retain its picture without covering controls with Buffering. This does
not certify menu animation/audio or suppress feature/unknown/running-producer
stalls. Qualify those negatives and actual menu→feature→menu on the phone.
DVD browser fixtures must model independent requestVideoFrameCallback owners;
one fake callback slot falsely erases the cache observer when timeline sampling
is added. Load current required Experience/Support modules in old fixtures.

Provider/API checkpoints are intermediate updates, not completion of an active
client task. Answer concurrent user questions in commentary, then continue
authorized client integration and affected end-to-end gates. Do not stop simply
because the provider passed or the question was answered. Explicit pauses,
genuine missing authority/input and completed work remain valid boundaries.

Standing2026-11-17 continuation rule: after each result, review the unchecked
authorized task list and run the next safe available item. A single unavailable
gamepad/WAN/acoustic row does not block authored/real-DVD, client integration
or other independent checks. Do not end with a checkpoint summary while such
work remains executable. Keep commentary, task ordering and handoff accurate;
stop only for actual completion, explicit pause or a genuinely necessary
external input/authority boundary after exhausting safe alternatives.

Run real server/browser gates sequentially and wait for the prior process to
exit with its exact native UI retirement result before reusing the test ID.
P12 streaming DOM tests run in both engines via SAGETV_BROWSER_ENGINE. Mock
native Pause must emit the real `{type:'media',action:'pause'}` event, never
the obsolete ignored videoPause name; assert actual paused state before
claiming Apply preservation. Defer one response to prove bounded latest-
successor behavior and different-source isolation, not merely request counts.
Read-only field observation of streamSettings MUST use GET. POST to that same
action applies configured defaults even without applyNow, so an empty POST is
not a read and can invalidate the intended ephemeral test profile. The three
current field drivers have explicit read-only routing, covered without a live
server by tests/test-field-read-only.py. Require effective requested/profile
truth and unchanged native configured defaults, not only a localStorage value.
Local offline tests may run independently. A success line is not cleanup
completion. Natural END can race a read-only status query; bounded fresh
observation retries are allowed, never playback-command replay. For physical
STV key tests confirm the actual fullscreen DVD context: Watch can leave DVD
in a menu preview. For decoder/EOF setup, existing MCP ui.command Select and
DVD commands use stock public DirectPlaybackControl independently of that
STV focus. Label them setup, not physical-key proof. Do not add another API,
patch Core or infer a playback fault from generic command20 selecting a menu.
Reset watched metadata only for an explicitly guarded generated fixture;
never reset a user's recording/bookmark to manufacture a fresh-start test.

Keep docs/parity/TASK_INDEX.json aligned with canonical TASKS.md through
scripts/reconcile-task-index.py: default audits/read-only, review then --write.
It must never change checkboxes, acceptance or evidence, promote unchecked
local work to field PASS, or advance optional approval. Run the focused sync
tests after a status change. Historical baseline tests verify the frozen P01
record, not an intentionally rebuilt current WAR; verify current packaging
independently. A clean checkout must use sanitized source-controlled acceptance
summaries, not require private ignored phone captures in the task index.

Physical iOS HID troubleshooting: separate encrypted report receipt, OS action,
fresh exact-page focus and actual trusted browser events. A visible retained
SafariViewService can have an expired API observer/session; reload only the
approved idle test page and rebind its owner before use. The1140Z recovery used
observed OS Home/Search/reopen plus one actual blank-canvas focus click, then
fresh Down key events/native command5 and trusted Play. Do not blindly replay
an uncertain input, erase bonds, flash firmware, type a code on an unknown
screen, or declare Bluetooth broken from missing DOM events alone. General
OS input must have fresh HDMI target proof and remain on the owned device.

WEB-014/063 authored audio proof uses the fixture's actual1000Hz English and
440Hz Spanish tones captured from USB HDMI digital audio, not the older local
440/880Hz regression fixture. Menu language selection deliberately jumps to a
new feature epoch; do not call that a no-FLUSH in-place switch. Require changed
native selector before diagnosing an Audio Change command as applied, and
new requestVideoFrameCallback output after a source replacement. DVD_STREAM
type0 audio and type1 subpicture are independent; test their ordering, invalid
selector preservation, FLUSH retention and INIT reset, plus actual converted
audio. A caller's accepted command is never sufficient stream-identity proof.

For DVD keyboard commissioning, verify stock UserEvent numbers (Time Scroll10,
TV15), not a test expectation copied from implementation. Actual SageMC hints
include MediaPlayer OSD/MC MediaPlayer OSD, with named popups retaining normal
arrows. Use stock-companion-dvd.py feature/chapter/bookmark/seek/subtitle flags
for actual frame/clock/SPU-pixel proof. The bookmark gate first requires the
read-only MCP20 absence checkpoint; refuse existing data, preserve a concurrent
change, and restore only the test-created bookmark through public operations.
Receipt alone is not playback. Observe new source generations and bounded
clock convergence without replaying controls. Native SPU controls can carry
legacy slots or HD flags: normalize to the PES ID, retain raw diagnostics and
prove Off clears old queued pictures while menu highlights remain available.
After seek, a changed currentSrc/readyState can still expose a held previous
picture. Require actual requestVideoFrameCallback progress within the settled
replacement generation before accepting subtitle pixels; inspect fixture PTS
and caption text together. Never count a stale frame as new output. Preserve
fresh exact-generation menu truth only inside its existing1.5s deadline;
unavailable observations cannot extend it. Read-only MCP network observations
may use bounded fresh retries; ordered playback controls remain one-shot.
Restore the exact borrowed hook before Stop can retire its UI context.

In a fresh normal-manager browser, inspect/accept SageTV's plugin disclaimer
before selecting the exact installed plugin row. A click blocked by that
disclaimer is not an installer failure. Confirm served input JS as well as
main JS/cache against source; health/version alone does not identify a candidate.

For WEB-052 use bounded replacement whenever live GPU bitrate adjustment is
unsupported or unverified. A forced recommendation qualifies handoff only,
not automatic measured adaptation. Use browser-stock-network-quality.py for
the latter: only owned generated HLS bodies traverse a finite local forwarder;
production policy/clock remain unchanged, no server network configuration is
modified and the listener/session retire in finally. Keep user Pause distinct
from the internal rebuffering video-element pause. Qualify measured reduction
and recovery independently; do not stop at their provider/browser checkpoints.

For WEB-052 use bounded replacement whenever live GPU bitrate adjustment is
unsupported or unverified; accepting a control command is not encoder-output
proof. Run browser-stock-caption-rollup.py with SAGETV_EXPERIENCE_GATE=1 for
the production DOM quality action and actual presented-frame commit. Add
SAGETV_QUALITY_ABORT_GATE=1 for deliberately withheld candidate ACK/explicit
abort and original-playlist resume. Never compare MSE blob URLs for producer
identity: reattaching the original playlist creates a new blob URL. Match the
actual playlist request and its source-relative clock. Host WebKit is not
physical iPhone/native Safari/WAN certification; no permanent rendition ladder.

For real host-WebKit playback gates, explicitly observe the browser's Play
video prompt after stock Watch/Seek. Stock mute events can override a muted
test preference; an untrusted API Play is not user activation. If prompted,
click the existing Play video button once through Playwright and record that
gesture before timing playback. Do not call the wait spent at this prompt
encoder/first-segment delay, or change production autoplay/security policy.
Use bounded timer polling for readiness (not a suspended rAF-only wait), emit
setup progress and retain the actual failure state. Host-browser gestures
still do not certify physical iPhone touch/audio behavior.
Do not accept paused=false as successful activation before play() settles:
the rejection/prompt can arrive asynchronously after that observation. Poll
actual advancing time and the visible prompt together with a host-monotonic
deadline; issue at most one trusted initial click for this test intent and
retain the last actual video state on timeout. Do not silently retry seeks,
restart producers or relabel time waiting for activation as encoder latency.

WEB-050..054 focused implementation gates: test-playback-experience.js,
test-miniclient-playback.js, PlaybackStateSmoke, QualityOptionsSmoke,
CommercialMarkersSmoke and browser-playback-experience.py. Live232 adds
SAGETV_EXPERIENCE_GATE=1 to browser-stock-caption-rollup.py for real local
timeline/700kbps session-quality/CC/full-GPU/pause and settings preservation.
Use the exact owning artifacts/active task directory. browser-stock-timeline.py
accepts WEB-050 for affected stock/SageMC native-marker regression; retry only
read-only retirement observations within its deadline, never replay controls.
Preview cache is explicitly opt-in and stores at most16 small images/512KiB
per source. Explicit scrub INPUT may request one192x108/32KiB source image
through FFmpeg24's optional known-completed-file preview lease; no timer,
queue, background capture, arbitrary path, extra A/V stream or preview seek.
Missing/old/off/stale service retains viewed frames/native controls. Shared
preview leases retire on accepted seek/quality/source/STOP, independently from
HLS ownership. Add SAGETV_SOURCE_PREVIEW_GATE=1 to the real caption driver
to check actual image bytes/decoded display/current-source custody, original
GPU playback and zero extra playback producers. Run sequentially per browser
and independently verify final activity/preview retirement. Comskip reads use
the existing authorized media-ID API with byte/line/count limits. Missing
chapters/source-preview support remain honestly unavailable.

## Task fix and server-boundary policy

Apply this policy to every task workflow, including dependency fixes across
Vibe repositories. Fix and test necessary plugins and update the test-server
plugin without asking again solely for repository-boundary approval.

Prefer browser-client fixes, then the owning stock-compatible plugin.
Both `.232` and `.175` are stock: never replace Sage.jar, stock FFmpeg or
bundled Core natives. Missing capabilities use only supported client/plugin/
container interfaces or remain documented unavailable. Never patch Core.

Stock `.175` installation changes are limited to plugin installation/update.
Do not modify its stock Sage.jar, stock FFmpeg, Core binaries, or server
installation/configuration files. Preserve user settings, recordings and
unrelated clients; reversible supported SageTV playback APIs remain allowed.

Stock `.232` restarts are authorized for task updates without asking
again; coordinate them with active test guards and preserve data/settings.
  Always ask the user before restarting stock `.175`, even when it appears idle,
  unless an explicit user-granted bounded restart window is active. Record
  its UTC expiry in the task/handoff, and check expiry and revocation before
  every restart. After expiry or revocation, ask again; stock files stay protected.

Update owning TASKS.md, linked dependencies and the workspace suggested order
as work changes; move completed checkoffs into the checklist change ledger.
Test only affected gates, preserve unrelated completed matrices, and do not
stop independent authorized work for a status question or a dependency-only
permission request. Unrelated work, publication, destructive actions and
interruption of recordings/other users still require their own authority.

Run `dev.cmd` or `./dev.sh` with `test`, `validate`, `build`, `install`, or
`all`. Commands delegate to the one sibling `opensagetv-vibe-build-env`
container. `install` reports the artifact boundary; `.232` commissioning is a
separate guarded operation.

`test` runs the complete generated/host regression set. `validate` checks
source, package, manifest, dependency, Java 8 bytecode, and browser contracts.
`build` creates the deterministic WAR and local SageTV plugin package. `all`
also enables the offline Chromium suites available in the build container.

The plugin must use the platform-matching OpenSageTV Vibe FFmpeg Plugin. The
legacy explicit FFmpeg property remains only for isolated regression fixtures
and diagnostics. Production discovery must resolve `SageTVTranscoder` and must
not silently select SageTV's stock `ffmpeg`.

Do not publish a plugin catalog entry, GitHub release, or public artifact until
all applicable stock-server and `.232` physical gates pass and the user gives
explicit final approval.

## Current mobile/PWA validation and commissioning

Calibration requires a real visible44px Play button even when Safari rejects
sound autoplay. Run browser-calibration-layout.py for ready and verbose-error
states in short landscape/portrait viewports; let video yield, not the actions.
A DOM click is not trusted activation. Never claim play succeeded until actual
media time/frames advance; preserve offsets and retire the calibration source.

Actual phone diagnostic download may open native iOS ZIP preview, making the
authorized WebKit page unevaluable although still listed. Inspect HDMI; ask
the operator to dismiss Back/X (optionally Save to Files). Do not loosen the
exact-page guard, replay export, or equate ZIP preview with a Files save. Keep
original browser profiles checkpointed. A normal Save can materialize default
companionDvd=false: verify runtime/other fields before restoring exact original
JSON after a temporary quality test, never reset unrelated settings.
Use commission-wait-ready.py after restart: bounded read-only health/activity
observations, not repeated installs/seeks. Packaging tests rewrite output ZIPs;
finish them before staging. A SHA256/ZIP refusal is a setup race, not authority
to bypass validation or copy live files. Keep finite field probes sequential
on the phone and let their hooks retire before starting another fetch trace.


WEB-049 covers BOTH SageMC and unchanged stock SageTV7. The native bridge must
answer SEEK-followed-by-GETMEDIATIME while replacement preparation is blocked;
one worker/latest desired seek, ownership/stop/flush guards, pause and visible
failure are required. MiniClientNativeSeekSmoke includes the actual TCP wire.
Do not move generic timeline pixels or guess a confirmed target in production.
The native event201 wake and ordinary media clock are STV-independent.

Use browser-stock-timeline.py with SAGETV_TIMELINE_TASK=WEB-049 and explicit
SAGETV_TIMELINE_STV=sagemc|stock; SAGETV_TIMELINE_TOUCH=1 exercises the actual
browser touch handler, including its configured double-tap wait. Both pixel
profiles are test-only canonical1280x720 geometry: SageMC white triangles,
stock themed red position line. Require an observed marker BEFORE the new
video frame, not merely a filled progress edge. Never use Time Scroll to
reveal the bar for this normal-tap test: both STVs deliberately pin selection
to TimeScrollTime while it is active. Play/Info or settled Play/Pause reveals
the ordinary bar; verify its actual pixels before tapping.

Stock qualification borrows SageMC's normal Setup/default-STV route in the
exact owned test UI; assert SageTV7.xml, restore SageMC with Home before Exit,
and verify restoration in finally even on failure. No STV/config file edits.
Observe native videoBounds events: browser Fill geometry can remain full-size
behind a main-menu preview and is NOT sufficient VideoOSD readiness proof.
Stock TV is a toggle; send it only after settled native preview placement.
Use bounded first-frame/teardown deadlines and independently verify eventual
owned-UI retirement; retained server contexts can outlast socket close. A
preflight refusal or invisible-OSD tap is not a failed playback gate or pass.
Keep actual iPhone/native HLS/WAN acceptance distinct from host WebKit.

WEB-048: native FLIPBUFFER pacing is an explicit browser/plugin handshake,
not a Core change. Old start requests default frameAcks=false; only marked
FLIP events get a session/sequence-specific POST after renderer completion.
Do not wait under eventLock or the media reader. Lost acknowledgements have
a1500ms limit; close wakes waiters; reject stale/future acknowledgements.
Increasing GFX read-ahead only postponed the reproduced long-run saturation
and is reverted. Keep4096-command/8MiB backpressure and ordered graphics.
Run BrowserFramePacerSmoke, MiniClientFramePacingSmoke, protocol/startup/
recovery/auth and browser-frame-pacing/render-performance/orientation/recovery;
then real stock sustained-animation/DOM-timeline/caption gates. Isolated source
overrides in commission-browser.py are opt-in test contexts, NOT deployment
proof. It can record actual stage-click input/event/first-frame timing and
operate only its canonical fixture/owned UI. Don't count taps after an OSD
expired or without a changed video generation as successful seek evidence.
`browser-stock-timeline.py` requires explicit SAGETV_ALLOW_STOCK_TIMELINE=1,
the WEB-048 artifact path, zero recordings/other clients and its absent owned
UI. Wait for first native frame, settle only the canonical fixture with public
Seek(0), then enter SageMC VideoOSD and assert full-screen video geometry before
tapping. Main-menu preview clicks and its unhandled Full Screen commands are
not valid timeline gates. Pause the90s fixture for45s of native repaint load;
do not repeatedly toggle Time Scroll, which can commit SageMC's old cursor,
or accept an end-of-file Stop dialog as a timeline. Require new source/frame,
the expected anchor, advancing video, bounded queue, unchanged pacing timeouts
and independent pause/resume. Finally Exit/stop only the exact owned session.
Host WebKit HLS-MSE results are not physical iPhone/native HLS acceptance.

WEB-044..047: real1s targets apply only to ordinary local transcodes with1s
keyframes; Copy/DVD pipe/concat keep3s. EVENT with unlimited list does not honor
hls_init_time for a short first segment. Validate actual output, not options.
MediaProbeCache stores only successful ffprobe embedded metadata for completed
local sources: bounded64 entries/source-tool identity/edge fingerprints and
post-read identity. Never cache active sources, remote samples, errors or mutable
subtitle selection; finish service/sidecar discovery afresh on every call.
Run MediaProbeCacheSmoke/affected command/playback/caption/recovery gates.
Stock startup profiler accepts owned WEB-044 directory; host inspector --task
WEB-044 keeps exact fresh owner leases. Its wan case simulates160ms segment RTT/
4Mbps response delivery, not actual iPhone/cellular evidence. Keep the same
steady reserve and report startup-phase timers separately from first-frame.
WebKit browser HTTP-auth cache is not inherited by Playwright route.fetch.
The delivery helper must supply commissioned credentials only to the exact
authorized origin, forbid redirects, and require200/MPEG-TS before delaying.
401 HTML is a helper-auth failure, never an encoder/decode regression. Preserve
failure status/browser evidence before teardown; no production auth bypass.
RAM evaluation is a bounded file-output comparison on existing /dev/shm, never
permission to move unbounded EVENT sessions there. Current comparison shows no
gain; production disk remains selected. No Core or MIM binary modifications.

WEB-043 startup profiling is opt-in real232, not ordinary CI or physical iPhone.
QSV HLS now explicitly requests forced_idr=1: forced I-frames alone were not
IDR boundaries on the measured pipeline. Keep this private option scoped to
transcoding QSV HLS, including current DVD/encode-only fallback; never Copy,
continuous TS, Software or other encoders. HardwarePipelineSmoke checks those
boundaries. The normal producer owns the correction because browser buffering
cannot publish a segment missing an IDR. Same-command bounded12s A/B confirms
one12s segment before vs four3s segments with IDR; closed GOP/frame-counter
alone did not correct it. Run WebKit startup/CEA/seek after normal-manager
installation; do not claim a live candidate pass from command A/B alone.
Use separate exact owned identity/canonical completed fixture; other phone UI
may coexist but must never receive controls. Reset watched state ONLY for that
synthetic fixture. Profile actual first video frame, server segment metric and
browser load timings separately. Linux WebKit has MSE but no native HLS: reject
unsupported Native honestly. Check actual playlist/keyframe cadence, not just
configured GOP. First-segment read-only probing uses host SSH identity through
inspect-startup-segment.py and the bounded fresh owner marker; pinned web-python
doesn't own paramiko/Windows known_hosts. Retire only own browser/native session,
wait for close; bounded exact known-fixture replacement/stop handles stale owned
UI without touching phone. Preserve minimum unresolved timing/segment evidence.
Installed043 result: first segment34.034s/one keyframe becomes3.003s/three
keyframes; host WebKit startup/CEA/seek PASS. This confirms the scoped producer
fix, not all-browser timing, a new full DVD matrix or a physical Safari pass.
No tmpfs change. Caption gate supports SAGETV_BROWSER_ENGINE=webkit and waits
for a changed video source after seek so old-source playback cannot false-pass.
Manager WAR reload may leave the old owned commissioning UI after its session
registry is gone; retire only that exact owned identity, independently verify
zero remaining UIs/encoders, and never mistake a404 for a failed installation.

WEB-042 landscape SageMC clipping: browser-sagemc-surfaces.py exercises a
screen composition surface allocated after multiple intermediate UI sizes,
then reused across another rotation. Verify right-side pixels, retained handle
and unchanged small surfaces in Chromium/WebKit; orientation-surfaces alone
only covers targets allocated before rotation. Keep the UI-size history bounded
and session-local; never resize ordinary image textures to the screen. Run
renderer scheduling/order/Stop, layout/recovery, high-DPI/phone/PWA and package/
served/stock checks. Synthetic wire reproduction is not physical phone proof:
reload the actual phone and reopen the affected landscape popup before closure.

WEB-041 supersedes039's single-column tools: transpose Android's two utility
rows into four-row columns. Diagnostics/info/test/stats above gear, Aspect/
Video/Audio/CC left. Both columns end above gear: no scrolling/clipped caption
icon. Portrait reserves one extra left column via gear margin,44px unchanged.
Phone-controls must hit-test every tool center, assert all32 controls don't
overlap, exact group positions and no scroll; preserve040 Back gap and desktop.

WEB-040 supersedes039's Back alignment: Back x is44px left of D-pad Left x;
the bottom Left column stays empty before Down. Reserve four bottom-band rows
below360px so the shifted band cannot overlap the pad/pages/tools. Run affected
geometry/high-DPI/PWA gates; no input/transport/media logic changes.

WEB-039 introduced bottom-band gear;041 replaces its one-column scrolling
geometry with two fixed columns. Preserve collapse/parent focus and desktop
restoration; no media-matrix reset.

WEB-038 phone tools start collapsed under phoneToolsToggle. Tests must expand
the gear before selecting hidden tool icons, not bypass visibility with JS.
Verify24 collapsed/32 expanded controls,44px targets; WEB-041 now requires
two four-row columns on every phone size, with no scroll-under-gear.
Escape collapses before
closing the overlay. Settings Back expands/restores its tool focus; new menu
opening and breakpoint transitions reset collapse. Desktop restores originals.
Run affected geometry/high-DPI/mobile/Exit/PWA gates, include settings.svg/SW
in served-asset checks and preserve Android vector source/license hashes.
These UI gates do not close WEB-037 STV/WAN rendering failures.

WEB-037 STV slowness: distinguish server-rendered native menus from the local
overlay. User observed it on cellular/VPN. Video bitrate does not bound GFX
traffic. Use bounded input HTTP acknowledgement, frame receive-to-present
queue, image decode last/max and scheduler counters in diagnostics/stats; these
are document-lifetime browser timings, not a server-to-photon latency claim.
Keep ordered GFX/cache commands and the8ms work budget;1024 count cap removes
premature128-command timer yields without dropping frames or reducing UI DPI.
Run browser-render-performance, orientation-surfaces, hidpi-controls, phone-
controls, recovery, P14 and graphics smoke affected gates, not full DVD/device
matrices. browser-stock-render-profile is opt-in: distinct absent test identities
per engine, own no-media Down focus only, finally stop own session; retained
idle native UI contexts are not evidence of an active socket or permission to
replace them. Host WebKit is not physical iPhone/WAN evidence. Keep requested
output paths for every capture, including legacy graphics smoke.
Current home-Wi-Fi report uses touch arrows, so test that path independently
of direct-canvas double-tap timing. browser-remote-touch.py asserts one command
per real browser touch tap. browser-stream-read-ahead.py models withheld idle
Fetch bytes (WebKit322545): baseline must strand the final FLIP, candidate must
present/ACK it with exactly one outstanding read. Keep the read armed BEFORE
parsing/scheduling; do not parallelize rendering, drop GFX or disable pacing.
Check errors/cancellation, compressed-image ordering, immediate Stop and bounded
queues. Actual phone focus-trace is bounded/auto-restored and records band
pixels/ACK times only; synthetic button activation is not physical touch.
Interleaved user taps invalidate a clean paired-navigation timing claim; retain
the observed frame gaps but do not invent restoration. Compare fresh phone
pacing timeout counts and loaded candidate revision after normal installation.
Read-ahead-only037.2 did NOT close the physical phone failure. Actual bounded
poll trial improves the same highlight;037.3 chooses existing finite events
on iPhone/iPad, including desktop-UA iPadOS. Desktop retains streaming. Run
test-event-delivery.js and browser-long-poll-events.py for one outstanding poll,
final-frame pixels/ACK, reconnect abort and next-poll Stop during delayed decode.
Both event modes retain4096/8MiB renderer backpressure; never await the entire
graphics chain before accepting the next poll's independent media controls.
Do not replace window APIs in production. The temporary phone trial is scoped
to the approved exact test identity, in-memory only and auto-restored within90s.


WEB-034 captions: run test-caption-rollup.js and browser-caption-rollup.py in
both pinned engines at852/393/320/desktop widths. Assert fixed text origin and
window dimensions while characters arrive, real CR upward rows, repeated PAC
and consecutive-only control suppression,32/declared column bounds, immediate
erase and16s source-clock stale clearing/resumption without old text. Pausing
must not expire captions. Preserve independent Teletext/DVB/SRT/DVD behavior;
run affected clock/authority/STV/ordinary/TT/DVB tests, not unrelated matrices.
verify-mobile-assets.py now also hashes atsc-captions.js (eight served assets).
HDMI capture can observe a cellular/VPN iPhone even when paired wireless
inspection is unavailable; do not label HDMI as DOM control or fabricate a
successful network connection. Ask the user to reload after install when no
control route exists. Keep new physical captures in artifacts/active/WEB-034.

WEB-035: X is Exit confirmation; use green hideRemote for tests that only hide
the overlay, not closeRemote. browser-client-exit.py covers default Cancel,
Escape/focus return, modal key ownership, own-session retirement, no automatic
foreground reconnect after deliberate exit, and explicit Reconnect in both
engines. Verify actual phone Cancel without interrupting playback. Browsers
cannot terminate an iOS PWA; use an honest disconnected screen, not window.close.
Always inspect loaded query revisions after an update: reconnect/native-session
replacement and OS close/reopen may retain an old document. If an explicitly
approved test source has been closed independently through MCP but an old HLS
buffer keeps playing, iphone-approved-test-reload.js pauses only that exact
test phone's remaining buffer and reloads, preserving preferences. Do not use
it on an unknown/user source. Recheck source state immediately before use.


WEB-025 recovery changes use browser-recovery-smoke.py (Chromium/WebKit), P13
lifecycle/P14 diagnostics and affected iPhone viewport tests, not unrelated
caption/DVD matrices. Legacy tests accept CHROMIUM_PATH; explicitly pass
/usr/local/bin/vibe-chromium in the unified environment. Always pass task-owned
SAGETV_ARTIFACT_DIR. verify-mobile-package.py compares all web source bytes,
embedded WAR/Java8 and catalog MD5; verify-mobile-assets.py proves served bytes.
On an idle test-owned phone page, explicit iphone-foreground-cycle.js tests
retire/return; iphone-recovery-failure.js injects one exact start failure and
restores fetch immediately/within3s; iphone-recovery-click.js checks visible
hit-tested retry. They refuse active video sources. Synthetic phone events
are not physical OS close/reopen: record user confirmation separately (WEB-025
user confirmed automatic reconnect). Never replay actions.

WEB-026 orientation must verify pixels/render targets, not merely CSS canvas
rectangles: browser-orientation-surfaces.py keeps native surface handles across
rotation and tests new AND old allocation copy bounds in both engines. Run
affected overlay/display/policy and recovery gates after a renderer change.
Actual phone check needs portrait→landscape after install, not just reload in
landscape. iphone-canvas-probe.js samples columns without changing preferences;
iphone-draw-probe.js temporarily traces native Canvas draws for1s and sends one
explicit Down only with no video source, restoring the prototype automatically.
iphone-draw-result.js requires confirmed restoration and retires the temporary
probe object. These tools do not edit a live WAR or change server Core.

Use current Android inventory/matrix, not the archived0.5.95 comparison.
`audit-android-features.py` detects reference drift; it does not certify parity.
Run affected local tests, `browser-mobile-vibe.py` and `browser-pwa.py` with
the unified pinned web-python, followed by applicable real stock232 tests
`browser-stock-mobile.py` and `browser-stock-captions.py`. Those opt-in field
tests use only their exact known browser identity and supported MCP controls.
They must never run as ordinary CI against a live household server.

`commission-mobile.py status|verify-stock|catalog-status` is read-only.
On native Windows run SSH commissioning/staging through host `py -3.12`:
it owns paramiko and pinned Windows known_hosts. The container's pinned
web-python owns Playwright/browser execution, not SSH dependencies. Do not
install another Python/SSH stack or weaken host-key checks to move these roles.
`stage` requires independent idle proof and stages only plugin manager input.
Stock devmode=false ignores Dev.d; preserve unrelated entries in the normal
local catalog, back it up and merge only this plugin. Development catalog
versions append separate date/time INTEGER components (avoid Core version
parser overflow); runtime base version and exact ZIP hash are distinct.
Install via the STV manager, never direct WAR copying or registry/Core edits.
`commission-browser.py` drives the existing UI and closes its own client.
Its fixed public command41 is stock Setup (UserEvent.SETUP), not43. Use it
from the owned manager UI to avoid walking/editing SageMC dynamic menus;
inspect the resulting Setup screen, Manage Plugins, disclaimer and exact Web
Client Update row before activation. Canvas click coordinates are disposable
test observations, never production theme navigation or a Core change.
The approved shared-experience batch can stage its two owning dependencies with
`commission-shared-plugins.py ffmpeg|client-extension [--verify-only]`.
Build in each owning repository first. This helper verifies fixed component
IDs/versions/package checksums/ZIP paths/no stock sage classes, refuses link
traversal and merges only that manager catalog entry with a race check and
original backup. It never copies live JARs/engines or edits installed registry
state. Local package checks: `py -3.12 tests/test-shared-plugin-staging.py` after
both candidate packages exist. Installed metadata before a required restart
is NOT loaded-class evidence. SageTV may block a second update until the first
restart completes; do not keep clicking through an unexpected restart dialog.

For a physical DVD sluggishness report, record actual browser frame progress,
native title clock and the CURRENT video URL's producer UUID independently.
Do not infer smooth output from1x clock alone or query the last ResourceTiming
entry (a full buffer can retain an obsolete UUID). Preserve a failed producer's
exit/stderr/input-EOS/ENDLIST and a bounded HDMI capture before restart. Compare
the same profile/source in a bounded isolated encoder test; that is not native
DVD/phone playback proof. WEB099's QSV async-depth1 correction must remain DVD
only and retain hardware encode; qualify actual sustained picture cadence after
normal-manager install, preserving source, user settings and stock Core.
Retire the exact owned UI, independently prove recordings/clients idle, then
use standing232 restart authority. Never count a still-present UI as zero or
reuse a pre-restart health result while the bridge is still booting.
Sync Playwright response callbacks require its event loop to be pumped while
waiting for an owned session: use page.wait_for_timeout, not host sleep behind
an owned=None short circuit. Stop before pagehide can independently stop the
same owner; a duplicate404 is not idle proof. Stock UI contexts can outlast
socket closure beyond30s: use up to90s read-only exact-identity retirement
observation and independently verify stock/encoder/activity state. Never replay
controls, increase playback readiness budgets or reinterpret failure as zero.
REMOTE-001 `commission-direct-quality.py --run-stock232 --handoff` is a provider
lifecycle gate with SYNTHETIC presented ACK, not visible presentation. A new
optional handoff must remain distinct from legacy /quality revision1. Actual
client frame/rollback/caption gates and exact same-input producer attribution
remain required before advertising a seamless/GPU-qualified quality switch.
On native Windows, keep stdin open with an interactive PTY for the commissioning
process; plain pipes may reach EOF immediately after ready and safely retire
the client before any commands. Do not replay install clicks on timeout: inspect
served bytes/manager state first. A brief404 during the owning WAR's normal
manager reload is not a failed-install verdict; verify eventual exact assets.

Label synthetic transport, real server/browser and physical phone evidence
separately. After task closure retain compact results, retire obsolete owned
raw captures/staging to workspace deleteme with cleanup ledger. Do not retire
unique evidence of the still-open intermittent caption result.

## Physical iPhone connection — ESP32 Safari Bridge

WEB-036 supersedes the bottom band's start: Help, Keyboard, transport,
Home/Info/Menu/Back (13 controls). Keep Help drawer/focus behavior and X Exit.
Make room on the right without moving the tool rail or aligned D-pad; never
shrink touch targets or overlap caption/tool controls to fit. The focused
phone-controls gate covers adjacent Help/Keyboard, arrow focus, Help drawer
return, safe areas, portrait wrapping and original desktop Help restoration.
Physical probe must show current036 query revision and all31 unique controls.

WEB-033 operator reference supersedes only WEB-032 phone arrangement, not its
completed historical evidence. Preserve original workspace ICONS_LAYOUT_MOBILE.png.
Use existing icons/nodes:8-tool left rail, Keyboard/transport/Home/Info/Menu/Back
bottom band, arrow pad bottom-right and pages above. Test phone landscape with
real59px horizontal/20px bottom safe areas, portrait320/393, and desktop restore.
browser-phone-controls.py now covers8 Chromium/WebKit rows with31 unique44px
controls/no overlap; phone-controls probe reports exact latest CSS revision,
rail/bottom/pad/page rectangles and unchanged saved settings. Use matching
physical probe revision after manager/served-byte verification, not stale
DOM screenshots from the preceding layout. No caption/media matrix reset.
User's axis refinement: Up/Select/Down share the Page/Last column's x position.
On landscape iPhone, move the pad44px right into available safe-area gutter;
keep a4px minimum screen-edge margin. On unguttered displays move page controls
inboard instead of clipping the pad's Right button. The focused geometry test
must assert common axis, viewport containment and no overlap on both cases.

WEB-030/031/032 follow-up gates: Settings initially focuses Back, never a
native input/select. Verify opening alone leaves saved/form values and media
unchanged. Auto video height stays a browser preference, resolved at start/
Apply through existing numeric stream_resolution; device physical short edge
(CSS screen times DPR) avoids portrait/landscape flips. Show current limit;
Copy+Auto sends Source without filters. Keep defaults/manual choices intact,
and restore prior settings after a temporary Auto test. Browser cannot infer
an independent iOS mirrored HDMI display resolution.

Phone remote placement uses existing nodes/listeners, not cloned controls.
browser-phone-controls.py verifies31 unique44px controls, no overlaps, Info
first in left column, landscape navigation beside transport, portrait group
wrapping, sparse keyboard focus and exact desktop restoration after breakpoint
crossings. Use actual paired phone probe/screenshot after served revision proof.
browser-settings-entry.py and test-auto-resolution.js cover focus/profile/wire/
orientation behavior; mobile/input/PWA suites cover affected shared UI only.
Run verify-mobile-package.py only after build completion; an in-progress WAR
can legitimately differ from the still-old outer package. No private Core
changes or full unrelated caption/DVD matrix reruns for these browser fixes.

Browser-only WEB-027/028 follow-up: qualify DPR3 auto graphics at bounded2x/
1920x1080 without changing explicit fixed UI choices or video resolution.
Use browser-hidpi-controls.py plus affected core/profile/orientation/recovery
tests. Controls defaults hidden; open menus with actual long press or the
visible toolbar Remote action, not a synthetic click on a hidden launcher.
The optional App checkbox restores the launcher and must survive PWA/profile
round trips. verify-mobile-assets.py checks HTML/CSS/main/core/app/support
served bytes. Record actual user clarity acceptance separately from pixel
dimensions; this does not create a native iOS external-display scene.

WEB-029 bitrate investigation: inspect saved/form and active requested/
effective values before changing rate control. Use exact observed HLS owner
with commission-bitrate.py status; packet sizes/timestamps from completed
segments measure video separately from audio/TS overhead. Never infer encoded
bitrate from image quality or short network bursts while HLS buffers ahead.
Use existing bounded MCP media.watch only for the approved exact test UI.
iphone-bitrate-reapply.js reapplies existing1000 without changing preferences;
verify a new HLS owner/current-position continuity and actual output. A retired
paused stale source is not active playback: iphone-retired-reload.js is only
for explicitly stopped test session, independently verified absent on server.
Never use that helper to discard an unknown user session or replay a timeout.

WEB-024 actual phone follow-up: native iOS selects can override min-height.
Keep native appearance and verify explicit44px height on the phone, not just
WebKit emulation. The exact authorized page can have a hidden duplicate:
use bridge sequential read-only visibility probes and confirmed detach,
never close unrelated pages or steal an attached inspector. User-enabled
Guided Access kept HDMI/WebKit visible beyond the5-minute limit without host
power leases. Prefer that operator mode for this test setup; system assertions
failed/display assertions remain unproven. Broader touch/audio/PWA acceptance
is still WEB-023. No permanent device-management/security/Auto-Lock edits.

2026-11-12 update: BRIDGE-003/004 now provide an independent paired Wi-Fi
userspace RSD/WebKit route. The iPhone can stay on HDMI; no ESP32 connection
is needed after pairing. Read sibling WORKFLOW.md's qualified wireless section,
use its pinned .venv and exact-page guard, and supply WEB-023/WEB-024 output
paths. The older native-USB procedure below is fallback/history, not a current
mandatory cable route. BRIDGE-005 temporary power assertions are opt-in and
bounded; do not change Auto-Lock/passcode/management settings or infer that a
network ping or synthetic webpage click resets the iOS idle timer.

WEB-024 targeted gates: browser-iphone-usability.py (portrait/landscape,
44px targets, scrollable categories, full selected text, parent/focus return),
browser-mobile-vibe.py, browser-pwa.py, affected input/display helpers. These
are emulation until verified on the paired phone. Keep selected and effective
playback settings unchanged. Stage/install only via normal plugin manager and
verify served asset digest/cache token before reporting the phone updated.
Whenever runtime package content changes, advance the reviewed deterministic
SOURCE_DATE_EPOCH in release.properties along with the development revision.
Stock installation preserves ZIP-entry WAR timestamps; keeping the previous
WAR timestamp can make Jetty reuse an old extracted application even after
manager success/restart. Never clear live Jetty work files as the first fix:
rebuild/reinstall through the manager with the corrected package metadata and
verify-mobile-assets.py must match served HTML/CSS/JS to exact local bytes.
For commissioning helper captures pass SAGETV_ARTIFACT_DIR under this project's
artifacts/active/<task>; do not leave new captures under an old closed task.

Use sibling `../ESP32-IOS-Bridge/WORKFLOW.md`, TASK.MD and Handoff.md for
WEB-023. The iPhone cannot connect directly to this computer. Route all phone
interaction through the native ESP32 at192.168.10.113, not Windows Apple/Inspect
or Android ADB. Current CH343 is COM7; COM3 is Intel AMT. Reuse the private
per-boot token and preserve pairing/NVS. Read status before any recovery.

BRIDGE-001 verified actual Safari pixels plus synthetic menu/Audio/Transcoding/
Back/reload operations, not app playback or physical touch. Use expression files
and a single browser-operation client; record timed-out/superseded actions as
failures without automatic replay. Put each new capture under its owning
artifacts/active/WEB-023 stable task directory with a unique run filename.

Production fixes still build/package/install through this plugin's manager
workflow. Do not use the bridge's isolated static-file source_cycle.py to write
live WAR/exploded-Jetty files. `.232` is now stock too: protect its Core/native/
original FFmpeg. No server restart is needed merely to operate the bridge.
User activation, actual audible playback, Home Screen and physical gestures/
controller remain separate acceptance; synthetic JavaScript is not that proof.
