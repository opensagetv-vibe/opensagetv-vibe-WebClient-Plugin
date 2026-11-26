# Handoff — OpenSageTV Vibe Web Client 3.3.0 development

## Current publication complete2026-11-26

PUBLISH-001 / WP17-006 completed on explicit user approval. Seven related
repositories are pushed with serial exact-head green CI. Public releases:
MIM0.4.20, FFmpeg0.1.36, MCP0.1.23, optional Extension0.1.29, Android0.5.115
and Web3.3.0 beta. All release assets/tag targets verified. Official SageTV
catalog https://github.com/OpenSageTV/sagetv-plugin-repo/pull/132 contains only
the eight affected manifests/nine verified package URLs; upstream merge and
catalog refresh are pending. Android issue4 comment7203809155 is posted and
issue OPEN. No future publication or background monitoring is authorized.

Web release commit6619d750 / CI45900857621: full clean runner passes after
pinning the real provider test dependency and correcting a video-only fixture
that fitted FFmpeg6's startup queue. Normal DVD A/V hold/refill/FLUSH/Stop
passes both6/8. No production Java/JS change in those CI fixes. WAR909573ad and
installer2ce42385 are unchanged from WEB-133 installed qualification; later
publication-ledger updates are documentation only and do not retag/repack.
Android115/e5969a5d: source1107/five skips, JVM789/one skip, strict APK and
build pass; DEX/native/resource-table match qualified Non-Pro e8f7ec12, only
TV touch navigation.xml/signing differ. Original ONN trigger/HLS drain/native
Safari/Windows/receiver scope limits remain explicit. No server restart, Core
change, device install or new physical-phone certification. Compact publication
and retirement records: artifacts/results/PUBLISH-001. Current task lists and
workspace order are reconciled; independent backlog is not silently closed.

## Current2026-11-26 - WEB-133 compact settings tabs complete

User prefers tabs to WEB-132's tree. Six short, single-row scrollable tabs
replace the tree navigation, with one active panel and keyboard arrows/Home/
End. Long static explanations and duplicate selected-value text are removed;
dynamic status/errors, privacy warning and Playback/Transport Save/Apply remain.
Existing keys and all132 playback/statistics/refill code are retained.
Normal manager201843 installs WAR909573ad/package2ce42385. Focused local
Chromium/WebKit and eight installed desktop/phone-layout rows pass; navigation
preserves preferences, no page errors, final recording/UI/client/provider0.
75assets/225Java8classes/18served/live WAR/stock20 verify. No restart, Core/
provider/Android changes or physical-iPhone/WAN/publication claim. See compact
artifacts/results/WEB-133/RESULT.md; retired raw captures remain recoverable
under root deleteme. WEB-127 native-Safari qualification stays separate.

## Previous2026-11-26 - WEB-132 installed and affected scope complete

Normal-manager190114 installs final WAR1059fbf0/package5c97fbc0 on stock232.
Six collapsible light-blue branches replace navigation-only pages; existing
stored keys/Save/Apply/defaults remain. Adjustment uses one selector backed by
existing flags. Graph/info icons are independent, adjacent and keep remote open.
Earlier completed-source refill retains live/DVD/unknown/native authority and
existing ceilings. docs/SETTINGS.md is the operational layout. Focused Node,
both-engine desktop/phone geometry/settings/PWA tests pass. Actual completed
HLS playback passes Chromium/WebKit on first184451 build; final menu-only
Diagnostics flattening retains identical playback JS and installed UI-only
passes both engines.75assets/225Java8classes/18served/live WAR/stock20 verified.
Final recording/UI/client0; owned context retired. Compact WEB-132 RESULT owns
counts and retirement references. No publication or physical iPhone/native-
Safari claim; WEB-127 remains separate. Android HLS-007 independently qualifies
its affected Non-Pro scope and retains an earlier unproven drain. Never infer
Android PASS from Web evidence or vice versa.

## Current2026-11-26 - WEB-131 / Android SETTINGS-005 complete affected scope

Hardware Encoder label and accelerator names align with Android; existing
Auto/Software/Copy/fallback profiles and native encoder command are unchanged.
Chrome/WebKit each pass25DOM/profile rows plus shared-choice normalization.
Those are mock-vendor/browser UI tests, not new GPU/phone certification.
Normal manager3.3.0.20261126.123221 installs WAR038f3a7e/package21614d01 after
timestamp guard required SOURCE_DATE_EPOCH1795696272.75assets/225Java8classes
and18served files match; guarded restart preserves stock20. Owning provider's
actual QSV/VAAPI12rows and Android four Direct/HLS routes/eight seeks/two FF,
two AMF refusals and independent HDMI pass;210prefs/CC/power restored, final
activity/provider0. No native Web encoding change, iPhone replay,
175/Windows modification or publication. Linked tasks are ledger-complete,
compact results retained and87owned raw files retired recoverably;
preserve independent WEB-127 native-Safari boundary below.

Current follow-up: WEB-127 real constrained-body Chrome test reproduces correct
4000→3000 handoff but no recovery after120s despite~30s reserve. Shared MIM's
adjacent250ms fall check resets every normal segment refill cycle. Bounded
cumulative-window correction passes recorded-refill and sustained-drain
regressions; actual Chrome/WebKit handoffs now pass on Java020729. Non-Pro's
healthy6s reserve exposes an unreachable8s recovery floor; Java023018/8de98633
corrects it. All four supported Non-Pro HLS delegates now pass automatic
down/up/seek/pause/resume/restoration. Current Chrome/WebKit QSV in-place
down/up also pass, including independently measured packets/same encoder;
six off/healthy/transient negative rows pass. Linux WebKit native stalls even
with adaptation disabled/unconstrained delivery; do not claim Safari failure
or PASS. Preserve031237Z/031705Z comparison; WEB-127 native-Safari row remains
separate. Compact AUTOMATIC_TEST.md owns current results. WEB-130 compact graphs
use112px maximum bars/6.4px thickness and pass both-engine desktop/landscape/
portrait geometry/PWA. Normal-manager020715/WAR971c654d is installed and
75assets/225Java8classes/18served/live WAR verify. Guarded restarts preserve
stock20. Keep the compact AUTOMATIC_TEST.md and active failures until closure;
no publication or new physical phone/Windows claim.

## Current2026-11-25 — WEB-127/128/129 and MCP test control

Normal manager3.3.0.20261125.011413 installs exact WAR533293e5 on stock232,
75assets/225Java8classes; served18/source and live WAR hashes match. WEB127
shares MIM ADAPT001 buffer-only policy, startup min/max and optional fallback.
WEB128 adds reserve/target bars; WEB129 redirects old entry points to STV and
removes legacy/Wasm navigation/pre-cache. Both-engine synthetic settings/report/
bars and affected geometry/PWA/reload gates pass. Actual MIM override/clear
passes Chromium/WebKit same-QSV output packets and Non-Pro VAAPI presented
handoffs/restoration. Parent automatic-pressure/recovery remains open; manual
targets are not its PASS. Compact artifacts/results/WEB-127/CONTROL_TEST.md.
Provider Java-only snapshot0.1.36.20261125.011454/JAR87be307c is manager-loaded;
native packages/dependencies unchanged. MCP0.1.23 adds exact-session leased test
control. Each restart verifies20stock hashes. MCP self-update bootstrap records
UNKNOWN immediate pre-restart activity, not zero; pre-update0recordings/ownUI,
post0/0/0 verified. No175/185 mutation, physical phone/WAN claim or publication.

## Current2026-11-24 - WEB-125 / WEB-126 installed controls

Normal manager224732 installs WARc6b7808c on stock232; main/CSS/SW126.1.
Desktop Live remains left of Skip back. Mobile landscape follows root operator
ICONS_LAYOUT_MOBILE.png: Gear/Help/Keyboard/Live/transport/Info/Menu/Home on
the D-pad middle row, Back under Home. Below780px wrap only the utility trio;
44px targets, safe areas, portrait and desktop retained. X menu adds Force
refresh webpage through the unchanged App reload, settings/confirmation/Cancel
and default Cancel ownership. No new icon or native playback commands.
Both-engine local geometry8/Watch-live80/mobile56/portrait6/exit8/reload2/PWA8
and installed desktop/landscape/portrait/X reload pass.75assets/224Java8classes/
18served/live WAR/stock20 match. Manager first refused the globally elevated
Windows FFmpeg floor; platform minima now Linux0.1.32 / Windows0.1.35, justified
by owning provider changelog and existing qualification. No provider upgrade.
Recording guard1795557920829 was preserved; installation waited for actual
idle1795560042121/1795560442781. Just before update1795560573555: recording0,
connected0, sole owned da92a86446be UI; no server restart. After manager update
stock20/encoder0 and idle1795560631159, installed gate also observes teardown.
Only Web updated,185/175/phone untouched. No publication or new physical phone
acceptance. See artifacts/results/WEB-126/RESULT.md; both IDs ledger-complete.

## Current2026-11-24 - MIM-WIN-001 Windows185

Normal manager loads current Web3.3.0 development WAR SHA256
9c4cecb7e900d6d5095ec982cb937ce0008c6add4b51c681641a8ba9b3ee6e7a
with FFmpeg0.1.35/MIM0.4.20/MCP22,
Jetty3.0.3.250/sagex9.2.8.1 on unchanged stock185/Java8u441. A fresh guarded
restart loaded its classes. The additive registered launcher-start API fixes
Java8's missing public process-tree stop boundary without a Java/Core change.
Fresh INIT now closes the previous ordinary HLS owner, allowing recording-to-
DVD handoff. Failed-before INIT regression and affected native/browser suites
pass. Chromium and WebKit actual recording startup/42s+10s seeks, Pause/Play,
visible CEA608, DVD root/feature/chapter/Stop and independent idle cleanup pass.
The epoch-aware DVD motion check does not reuse preceding-source frames.

Strict native recording decoderEOF is NOT passed: stock Core issues terminal
Pause before video.ended; do not ignore that intent or fake clock/ended state.
Installed isolated public-HLS real EOF/caption-clear now passes WebKit/software
and Chromium/Auto QSV after a failed-before bounded final-fragment loader fix.
The offscreen WebKit buffer error was a harness defect; one earlier isolated
QSV exit-5 did not recur and has no proven queue cause. No starred phone cure
or physical-iPhone proof is inferred.

Windows XMLTV3.6.0 now imports the same guide as232,107logos, user-approved
guide-only share and temporary tuner3. Growing qualification continues after
a real Windows0x13A whose matching-symbol dump identifies Portmaster1.1.2/
PMas/free. User directs leave it unchanged. Authorized SYSTEM V: restoration
and exact idle-guarded OpenDCT recovery address post-crash environment faults;
do not patch browser/Core to hide missing capture input.37stock files/INI
remain unchanged. Stock Windows recording backslash OPENURL regression now
passes7cases plus existing DiscSource8/affected suites; normal manager update
and fresh idle-guarded restart load the exact WAR above. Growing71037 actual
Chromium/Auto and WebKit/Software plus fresh WebKit/Auto pass decoded frames,
new-producer10s seek/Pause/Play/Stop/owned cleanup. Earlier WebKit194522Z has
QSV device failure and hung media inspection; its interruption's failure:null
is not PASS. Same-source four file/four Java8 raw comparisons pass; exact
cause/additional cure remains unproven. Keep that limitation/evidence.
Final19:57Z185/232 recording/UI/client0, jobs/claims0,37stock files/INI intact,
136Non-Pro preferences/awake restored, Windows awake released/tuner3 returned.
MIM-WIN-001 is scoped-complete; runtime RESULT/CONSUMER_SUMMARY/FINAL_STATE
own evidence. Not universal Windows hardware or physical phone certification.
No175 SageTV/232 installation change, phone matrix replay or publication.

## Current2026-11-24 — WEB-124 qualification

Manager snapshot3.3.0.20261124.022051/WAR8363371e installed on stock232 with
FFmpeg0.1.30/MIM0.4.16/MCP22. Optional site/client switches default off.
Actual Chromium/WebKit unchanged production-policy QSV in-place down/up pass,
same PID/start/GPU descriptor/source/resolution and decoded continuity.
Final Chromium fresh3segment rates3929.224→541.168→609.249kbps for4000→550→650;
WebKit4101.918→520.631→612.651. Public synthetic settings test passes actual
packets/60fps/decode and playback409 refusal. Full local Java/Node/browser
UI/input/layout/captions/recovery/P13/P14/PWA/package gates pass.75assets/
224Java8classes/18served/live WAR match. See artifacts/results/WEB-124/RESULT.md
and QUALIFICATION.json for exact outcomes and corrected test-only failures.
No current physical iPhone/VPN, native Safari bandwidth, Windows/NVENC,
classic-QSV or universal receiver claim. Existing stars and deferred items
unchanged. Publication remains held; do not push/tag/release without approval.

## Latest2026-11-23 — WEB-122 icons installed; WEB-123 receiver boundary

Normal-manager032112/WARdaa7ca2c installed. Broadcast Watch live icon is directly
left of phone-landscape gear; portrait has44px Live/Cast video cells. Native
Safari AirPlay/Remote Playback picker only, synchronous user gesture; no screen
mirroring, URL/credential export, extra producer or playback command. Disabled
without source/API/when remote disabled; missing cast module is optional-safe.
Main/CSS/cast/SW122.1; Java/playback121.4/provider unchanged. Watch-live DOM40,
mocked picker DOM22/mobile56/actual PWA8 and installed both-engine layout pass.
Exact75assets/223Java8classes/18served/live WAR/stock20 verify. Final033427Z
installed report; activity1795404889440 recording0/UI0/client0/no encoders.
No physical receiver PASS: user requests ALL AirPlay/Chromecast/Fire TV.
Google Web Sender unsupported on iOS; Fire TV Matter needs app integration.
WEB-123 remains pending receiver qualification and wider native/receiver or
stock-compatible server-side bridge architecture, not falsely complete from
mocked pickers. Browser-only preference and stock/auth boundaries remain.
See WEB122RESULT. No restart, publication, APK, receiver app or Core changes.

## Latest2026-11-23 UTC — WEB-121 actual tuner collision

013640Z recurrence on confirmed phone121.4 is NOT stale-client evidence.
Stock232 football104669/5.1 and production175 Marshals66554694/2.1 repeatedly
take the same OpenDCT10703705-0. Source bytes stop; both stock servers log
encoder-halt resets. Stock EOS/SeamToNext does occur after physical advance,
contrary to the initial no-handoff hypothesis. No native/input error recorded.
User explicitly approves separate available232 tuner without touching175.
Stock Setup Video Sources configures network10703705-3 with existingFTA_60177
and removes232's tuner0 source. Readback015128Z:232 provider2 only on3;
175 provider2 on0/1/2, provider0 on3/native inputs, unchanged. Setup returns
to SageMC_Vibe.xml. No file edits/Core/provider update/restart/publication.
Stock20 unchanged. Existing phone returns during setup; do not overwrite it.
Initial read-only continuity check correctly rejects a replaced producer;
fresh exactdfaa40d producer then passes150.06s/11samples: source34,243,372 to
197,934,860bytes, phone93,685 to244,382ms, zero recoveries/errors, reserve>0;
both channels remain on independent tuners at every sample. Real phone
feedback, not HDMI visual or multi-hour proof. Final015554Z production file7
476,429,600bytes; only phone UI/recording1 on232, NOT idle. Seven observer
guards pass. No runner remains. Current collision corrected/qualified;
older pipe origin stays unproven. No new runtime package/commit/publication.
See WEB-121/TUNER_COLLISION_2026-11-23.md. Older pipe origin remains unproven.

## Current2026-11-22 — WEB-121 buffering recovery / server flight recorder

Latest223956/WARf1c2ec79, app/SW121.5/playback121.4/core121.2. New recurrence
223322Z captures99646 source59442404bytes, encoder79.752s/browser39.674s then
feedback missing; no native/input error. Phone revision unknown/fields absent;
bounded access log has no recent phone asset GET. Do not call cache cause
proven. New99647 session later advanced170.974s (223648Z), not a cure.
Cache delivery correction: Reload navigates with a fresh query, preserves
settings/other query/hash; mutable-shell private revalidation and SW fetch
cache:no-store retain offline CacheStorage fallback. Shell15 failed-before/
after, actual host reload2/PWA8/playback106 pass;72assets/223classes/15served,
installed HTML/JS/SW headers, stock20 verify. No Core, restart or publication.
Next verify actual phone revision121.4 after fresh navigation; a user reload
request is pending, not an excuse to claim buffering fixed. Original failure
and minimum current raw snapshots remain; compare this with earlier213922:

Previous normal-manager213922/WAR8289b240; playback/SW121.4/core121.2. Actual
210919Z phone recurrence is retained:99524 piece0 source stopped growing at
65434528bytes/browser71585ms, replacement3attempts with no browser attachment.
Exact broken-pipe origin remains unknown; user reloaded AFTER the incident.
Do not blame cache from missing fields alone. HTTP recovery now uses existing
off-monitor worker, exact producer/pending guards, preserved retry/Pause and
late Stop cancellation. Loaded browser revision plus native/input error
category/time survive cleanup without raw exception content. Zero/missing HLS
files no longer count playable/suppress fallback. A metadata-qualified clean
completed empty seek returns actual decoder EOF, not a fake browser ended;
failed/growing/ordinary/DVD/unknown inputs are excluded. New empty-manifest
failed-before plus17guards and real CPU empty seek pass; health32/seek41/
playback106 and HLS10/DVD6 pass. Earlier213113 Chromium99524 PASS5: zero tail retries,
91new piece1frames, one explicit recovery accepted10ms then91new frames,
45s/20progressing pairs. Original physical iPhone/VPN field incident stays
open. No Core/provider change, server restart or publication.
WebKit213427Z/214148Z actually negotiated MPEG-TS because the harness used an
unsupported container preference. They are NOT HLS qualification; preserve
the observed TS empty-tail retries separately. Harness now selects player=hls
and verifies negotiated transport. Latest213922 also publishes explicit
producerPreparing with a synthetic regression preventing competing browser
retries during hardware fallback; this is not a proven cause of the TS result.
Final explicit HLS213922: WebKit214432Z/Chromium214554Z PASS5 each, zero
automatic tail recoveries,12ms explicit recovery acceptance,91/90new frames,
9progressing pairs/20s each. Loaded121.4/exact15assets/WAR/stock20/retained
ZIP3hashes verified. Final1795384032402 recording0/UI0/client0/no encoders.
Reviewed redundant raw retires with CLEANUP_RECOVERY.json; original210919Z,
final both-engine HLS and minimum unresolved TS214148Z retained. No runner
remains; next boundary is original phone/VPN confirmation, not another matrix.

Earlier205427 scope, preserved as history:
Native Safari loader starvation now repairs the same producer at the actual
position, with no encoder restart/zero replay and Pause/seek/source/AirPlay
guards. Clean exhausted native recording pieces no longer recover repeatedly
against stock wall duration; actual old piece0 reached budget6, new piece0→1
has zero recovery requests. Growing-source EOF waits without throwing away an
established decoder; actual file26 stopped at60198352 bytes, independently stat
verified. New actual120s stock232/Chromium run passes5rows,77new piece1frames,
Watch live→28,25progressing sample pairs and resumed210frames after source gap/
one accepted recovery. This is NOT physical Safari/VPN or uninterrupted-source
proof; original phone confirmation remains WEB121. Source data cannot be
manufactured while the writer is quiet. Do not restart healthy producers to
hide a source gap or treat recorder sampling as moving-picture PASS.

Passive recorder persists two1MiB metadata journals in server-relative
plugins/SageTVWebPlayer/diagnostics; authenticated support streamHealth and
streamJournal plus normal ZIP hashes retain closed-owner evidence. Independent
sampling does not extend playback leases. Health27/support22/live49/EOF33/
seek26/core33/playback104 and synthetic Watch-live DOM24 pass; exact package/
15served assets/stock20/retained report verified. See WEB121RESULT. Last activity
1795381225970 is independently recording0/UI0/client0/no encoders. No restart,
Core/provider modification, commit, push or publication. Use Settings/App/
Reload webpage after installation; the new revision recorder proves loaded
playback code rather than guessing its cache state.

## Current2026-11-22 — WEB-120 live replay / Watch live

Installed through normal manager3.3.0.20261122.195253, WAR4e2292be. Native
OPENURL now honors the authorized physical segment, does not concatenate later
pieces behind stock MiniPlayer, and uses segment-relative clock/EOF/duration.
Growing live-tail requests beyond observed PTS use bounded proven preroll.
Long-press Watch live uses source-scoped public Seek/Play; no Core/provider or
MCP production dependency.49 unit, CPU tail reproduction, EOF33/seek26/wire,
core/playback99,24 live DOM and56 mobile-control rows pass. Actual stock232/
Chromium football99487 segment0→1/sustained pictures and Watch live→growing15
pass with QSV. Fifteen served assets/exact package/stock20 verified. Physical
iPhone/VPN confirmation of this new fix is not claimed; user can close/reopen
the app and test now. No publication/restart. First timestamp-stale install
was NOT qualified: correct package epoch/reinstall and new stage guard prevent
Jetty silently retaining old extracted code. Earlier cold Watch-live gap is
separate from the proven zero replay; CPU reproducer validates preroll, final
real live run used normal PTS index. Compact artifacts/results/WEB-120/RESULT.md.
Final exact test UI retired; read-only1795377493486 proves recording0/UI0/client0.
Prior stars/publication/Windows dispositions remain unchanged.

## Current task-index reconciliation2026-11-20

Latest P15–P17 execution: normal manager151352/WAR4bf65fda installed without
restart,20 protected stock files unchanged. Removed false private metadata GET
claim and rejected unsupported extension SETs; no stock controls altered.
P15 four stock-alternative gates complete; WP15-002 transformed-DVD input
consumer remains unavailable, not implemented or disguised as native playback.
P16 stars retained; P17 local package/clean-build current, remote publication
still held. Both installed host engines10 actual optional/native DVD rows each,
cleanup[];17contract/11companion/8rate/48DOM and exact195-input/14-command build
pass. Current evidence artifacts/results/WP15-001/RESULT.md and
docs/parity/P15_STOCK_CONTRACTS.md supersedes the older "P15 deferred" summary.
No phone/full matrix replay, Core/provider change, commit or publication.
Reviewed completed raw evidence30files/8548199bytes and two clean source
archives retired recoverably; WP15-001RESULT/CLEANUP.json and root cleanup
report retain results/hashes. Final read-only activity1795188638214 confirms
zero recordings/UIs/connected clients; no background runner.65 current tooling
tests pass on Windows/Linux; no original starred-failure evidence moved.

Latest user disposition supersedes older "still open" notes: mark original
203329 caption-tail and024848 DVD-start with `[*]`, might be fixed indirectly
and not repeatable on current build. This is not verified completion/removal
or an active retest queue. Preserve evidence; reopen only on recurrence.
P15 was optional/deferred before the latest execution above; P16 qualified scope with two starred observations,
P17 awaiting publication approval, not three closed phases. Explicit labels,
separate mirror/progress/fix-ledger counts and parser guards preserve this.
The marker reconciliation itself made no playback/runtime change; the separate
P15 correction and installed tests are recorded above. No proven-fix claim for
the two original observations.

Latest original-failure investigation: actual iPhone142713 full PMT/language/
seek5→60/EOF/clear/reconnect/reopen PASS8 and desktop WebKit143247 authored DVD/
chapter/Time Scroll accept/cancel PASS3, cleanup[]. Original203329/024848 causes
remain unproven.133015 HTTP observation timeout is distinct: actual pictures
advanced with ready4/buffer reserve/healthy producer; no demonstrated deadlock.
Four retained logs contain neither original producer ID. Local completed seeks
bypass the byte index; no proven cold-cache mechanism or reason to restart.
Compact artifacts/results/WEB-115/INVESTIGATION_2026-11-20.md. Phone login and
paired exact-page inspection restored; BRIDGE033 map6 qualified, keyboard-first.
No production/Web runtime, server/Core, plugin install, restart or publication.
Final audit also exposed/fixed WEB118 tooling false failures: waiver-aware WP
parser and authoritative logical-source digest, byte-exact binary pins retained.
27P01/9mirror regressions pass on native Windows and DEV Linux; canonical
reconciliation no changes. No task
acceptance is weakened, and neither original playback failure is closed.
Latest teardown: protected stock20 unchanged/no encoders/zero recordings or
native clients, one idle phone UI (not restart-idle proof). Firmware keeper
explicitly OFF/32jiggles/zero input leases, secure bond; no runner remains.
Original-failure evidence is the unresolved boundary, not missing phone access.

Workspace task.md is now one concise current index; its complete former
checkpoint/ledger stream is preserved under artifacts/results/TASK-RECONCILE-001.
Eight stale owning plugin/runtime dependency checkboxes move to their ledgers
using recorded exact Linux/consumer evidence. Original WEB115/DVD and WP16-003
failures remain open, not erased by Markdown cleanup; optional Core, external
catalog aggregation and publication stay separate. New read-only workspace
audit and eight regression tests prevent active/history/parent confusion.
No phone/server/runtime/package/publication changes in this reconciliation.
The prior final phone result/restoration below remains valid; do not repeat it.

Final phone acceptance2026-11-20: user confirms cellular/VPN; WEB023 is now
ledger-complete within commissioned-phone/supported-browser scope. Actual
HDMI/BLE menu redraw, recording preview/fullscreen/seek/CEA/EOF and paused-source
Resume180newframes/6s with electrical audio pass. Authored DVD root/Select and
chapter replacement179newframes/5.973s pass. No Wi-Fi inspector, synthetic input
or forced-bandwidth/full-GPU/acoustic claim. Compact
WEB023/CELLULAR_VPN_2026-11-20.md. Test helper extends bounded existing capture
to exact loaded media/explicit HDMI input;5offline guards pass, no runtime rebuild.
Exact test Stop/Home/original Off restored, actual103333 main menu reviewed;
stock20 unchanged/no encoders/zero recordings/foreign clients/one idle phone UI.
Firmware keeper explicitly OFF/975jiggles/zero leases, no runner/background work.
Only original WEB115/DVD and WP16-003 stalls remain unproven; prior passes are
not a repaired-defect claim. Optional Core/publication remain held. Phone no
longer needed for completed acceptance; earlier VPN-pending notes are history.

Final local teardown2026-11-20: five scopes closed (WEB020/021,
WP16-002/006, WP16-007 disposition only). Actual new caption7/chapter5 rows
pass; original failures remain unresolved. Firmware keeper explicitly OFF,
connected/secure,962jiggles, zero input leases. Phone left on reviewed idle
SageMC main menu; zero recordings/encoders/foreign clients,20 stock hashes
unchanged, one idle phone UI (not restart-idle proof). Final cellular/VPN switch
has not been confirmed. No runner remains and no background testing claimed.
12 reviewed raw files1,417,500B retired recoverably with exact hash journal;
private originals and historical failure evidence preserved. No publication.

Current remaining-scope continuation2026-11-20: WEB020/021 and WP16-002/006
closed within documented scopes; docs/parity/FINAL_SCOPE_2026-11-20.md.
Actual phone093330 caption PASS7/093448 chapter PASS5, exact profiles and
observers restored. Original203329/024848Z still unproven; no speculative
production fix. Test-only session observer fixed to read-only after its old
closeRemote click requested Exit; Cancel/Home restored menu, HDMI093949
verified.2guard tests pass. Compact WEB023/CONTINUATION_2026-11-20.md.
Firmware keeper explicitly ON60s for current authorized run, zero input
leases. Cellular/VPN requested asynchronously LAST; do not infer confirmation.
No runtime rebuild/restart/Core/publication. Older final-OFF note is historical
until the new test session's explicit teardown is recorded.

Scope override2026-11-20: user explicitly removes the five missing-file/
equipment tests. WEB107 original84256 replay, WP17-004 original3.2.4 rollback,
WP05-005 actual property-present caption peer, WP12-007 receiver/acoustic
measurement and WEB021/023 physical gamepad are REMOVED_USER_REQUEST, not
passed. They no longer block parent matrices or require files/equipment.
TASKS.md ledger and task mirror retain history. No media/files deleted, no
runtime changes, no phone/server operation or publication. Earlier dated
missing-source/baseline/peer/controller/receiver blockers below are superseded.
VPN/remote and unrelated original intermittent failures remain unchanged.

Final available-scope audit2026-11-20: WEB117/WEB105/BRIDGE032 complete;
metadata3, task mirror/no changes,248-entry fix ledger/no changes, source
manifest565, bridge portable155/immutable firmware hashes and whitespace
check pass. No staging/commit/push/release. All executable selected LAN/host
rows complete; external cellular/VPN reply still outstanding. Remaining
exact source/baseline/peer/controller/receiver and unreproduced original cases
are not PASS. Firmware keeper explicitly disabled after test teardown; no
active input leases. Re-enable explicitly on a new authorized physical run,
do not assume old ON state. Phone test connection remains retired/no media.

Current2026-11-20 06:13Z: WEB117 COMPLETE in ledger. Final actual installed
WebKit/Chromium × stock STV/SageMC four Enter/search fields PASS14rows, original
SageMC restored/profiles/cleanup[]. Independent final20stock/no encoders/
zero recordings/UI/clients. Normal manager053814/WAR9b4c4718 unchanged.
Phone LAN acceptance complete in available scopes; compact
WEB023/IPHONE_2026-11-20.md and WEB117/RESULT.md. Completed/corrected raw65phone
files5.9MB+62WEB117files12.8MB retired recoverably to matching root deleteme;
cleanup hashes preserved. Unique historical failures, pre-input060417 timeout
and private restoration checkpoints remain. Current bridge qualification after
105s still passes but original cause unknown, no fabricated firmware fix.
Finish final mirror/manifest/workspace task/cleanup audit; final actual
cellular/VPN switch requested asynchronously, not yet received. No publication.

Current2026-11-20 06:06Z: physical LAN continuation complete in available scope.
Input055426 PASS5/exact profiles/draft/observers; caption055627 PASS7/original
Off/restoration; chapter055808 PASS5/actual~1x; one-picture060125 PASS4/105s/
real BLE Select/natural root/Stop and post-still pointer060445 PASS. Original
BRIDGE031/203329/024848Z historical causes remain unknown; no guessed fix.
Phone explicitly pagehide-retired060558 after independent unloaded/stock20/
no encoders/zero recording/other-client proof; independent retirement31.234s.
Now installed WEB117 affected host WebKit/stock STV Enter search is running
in exact disposable da92 UI, restores original SageMC before exit. Remaining
engines/STV rows follow; do not overlap a second server-owned field. Cellular/
VPN requested asynchronously for LAST; no need to stop host work for answer.

Current2026-11-20 05:55Z: final WEB117 normal-manager053814/WAR9b4c4718,
main117.2/input117.1/SW117.2 installed and live15asset exact. Actual iPhone
search054240 PASS4 (repeated BLE Enter/no re-arm/no-rebuild/Select/new pictures/
Play cancel), Apply054358 PASS2 (actual700k/480p/QSV/eight settled seconds/
886ms final paired-clock difference), normal ZIP054646 PASS2 (6962B/hash/live
bounded element/no URL; only OS navigation suppressed). Exact profiles/hooks/
observers restore, cleanup[]. Compact WEB117/RESULT.md; affected host stock/
SageMC fields pending. Original024848Z remains WEB115, not fixed by these.
Phone input/special-key/foreground/idle field now running; Q became uppercase
by ordinary iOS autocapitalization, not lost HID. Corrected test accepts one
q/Q and cleans only that owned draft. A5-unit move at edge gave no page event;
bounded no-click repositioning/actual trusted events are being checked, not
claimed a fix. No firmware flash/bond erase. Firmware keeper remains ON60s.
Next native caption-tail affected phone check, then remaining actual host rows;
VPN last. Publication held, stock Core protected, Windows deferred, no3h soak.

Current2026-11-20 05:27Z: normal manager051733 installed WEB117/WAR6e7b9d20;
Done-OK, exact live WAR/15 served assets and20 protected stock files verified.
Installer SageMC restored and independently retired28.141s; zero recordings,
UIs/clients/encoders. Input23/transport38/mobile56/DVD lifecycle22/clean191input
and7commands/package72assets220Java8/metadata3 pass. Physical phone Apply and
portable search follow; do not claim them before measured results. Phone old
113main remained visible but idle after pagehide; guarded approved reload is
in progress, no playback input replay. Firmware keeper ON60s/secure BLE.
WEB105 actual recovery700/900 and explicit abort pass with exact current-profile
restoration; BRIDGE032 fresh-lease sequence reset fixed,19+22 tests pass.
WEB115 original024848Z remains separate/unproven. No restart/Core/publication.

RESUMED2026-11-20 04:45Z: user reconnects phone/requests whole remaining task
list without checkpoint stops. Actual HDMI landscape/SageMC, paired visible
page852x393/current116.1 and encrypted BLE confirmed. Firmware keeper ON60s.
CAS preflight: old observer absent, current defaults auto/STV/scrubOFF/adaptive
ON differ from old borrowed state; preserve current user defaults. Historical
interrupted restoration receipt cannot be retroactively fabricated. Fresh
WEB105 checkpoint/recovery900/abort runs first, then affected physical rows;
VPN last. Publication hold and stock Core boundaries remain unchanged.

Current2026-11-20 04:12Z: available non-phone batch complete, WEB115 NOT fixed.
WEB116 COMPLETE,
installed through normal manager035714/WAR9e1c9a24, Done-OK/15served exact.
99controller/22support/11DVD DOM per engine/clean190input/72assets/220Java8/
metadata3 pass. Actual installed WebKit040328 and Chromium040502 normal ZIP/
hash/bounded element checks pass after real chapter/new pictures, cleanup[].
No media URL, mutation or decoder/GPU guess. Normal reports now preserve the
buffer/readiness evidence missing from original024848Z. Original SageMC
restored, installer UI independently retired28.062s. No restart/publication.
WEB115 eight ordinary, eight150ms and eight500ms synthetic-delay QSV plus four
libx264 chapter replacements pass; original024848Z remains unresolved. Reader
chapter is read-ahead, initial Core poll can precede new epoch feedback;
corrected test uses paired settled advancing clocks, never changes them.
No safe production correction established; original needs comparable recurrence
with improved normal report evidence. No more identical soak/unattended runner.
Final20stock/no encoders/zero recordings/UI/clients verified. Completed/corrected
owned raw files retired recoverably; compact WEB115/116 results and CLEANUP
journals preserve findings. No phone operation or three-hour test.
Reviewed remaining unchecked work: WEB105 actual-phone restoration/recovery/
abort; WEB107 missing original input; other rows need actual caption peer,
native HLS/background backend, physical receiver/controller/phone, original
rollback WAR, separate optional-Core authorization or publication approval.
These are not PASS and do not authorize phone access/publication automatically.

Current2026-11-20 WEB114 bounded investigation/tooling complete, not repaired
defect. Actual matched QSV/WebKit+Chromium chapter transitions/new source/4s
pictures pass, plus real normal diagnostic-export self-test with producer/
browser/ZIP captured before Stop. Original024848Z does not recur in four later
WebKit chapter transitions; limited original evidence does not justify a
speculative client/producer fix. Keep unique failure active under WEB014/
WP16-004. Runtime unchanged024257; compact WEB114/RESULT.md. No independent
phone access, optional Core or publication authorization has appeared.

Current2026-11-20 02:58Z: WEB113 COMPLETE in available desktop/Linux scope,
installed normal manager024257/WAR7eaa0e32/main-input-SW113.1. Atomic source-
owned FF/RW Time Scroll search, accept/new pictures/native clock, cancellation,
profiles/cleanup pass actual Chromium/WebKit × stock STV/SageMC, plus another
WebKit/SageMC run. Input21/transport DOM26/existing editor/touch/mobile/DVD/
package/clean/live15asset proof passes. Stock no-clear paint ownership defect
corrected with exact fresh feature/hint guards; not256x/reverse decoding.
Final .232 stock20 unchanged/no encoders/zero recordings/UI/clients verified.
Separate024848Z WebKit next-chapter startup failure preceded search, did not
reproduce in two later same-STV runs; it is NOT proven fixed. Keep its raw
JSON/PNG under active WEB113 and broader WEB014/WP16-004. Failure capture now
collects producer/browser diagnostics before Stop. Compact WEB113/RESULT.md
records test-oracle fixes separately; completed/corrected raw artifacts retire
recoverably. Remaining phone/source/peer/receiver/native-capability/rollback/
publication requirements are explicit in NON_PHONE_READINESS.md, not PASS.
No phone use, Core/engine change, restart, .175/Windows or publication.

Current2026-11-20 01:39Z: WEB112 installed normally013627/WAR49d57d87,
input112.1/SW112.1/main108.1/playback101.1. Explicit special-key mappings added,
new defaults inert/Backspace unchanged. Input18/DOM26/mobile56,191input/6command
exact rebuild/72assets/220Java8/metadata3/15served pass. Manager Done-OK; own
SageMC restored, native retirement independently4.953s/zero activity. No Core/
restart/phone/publication. WEB111 both-engine48/5/60s pictures/EOF/clear passes;
old native203329 remains unclassified. Continue remaining non-phone alternatives.

Current2026-11-20: WEB110 native/optional angle comparison COMPLETE, not a
checkpoint stop. Native WebKit012041 stays angle1 with moving video; pinned
official9.2.17 JAR control213 disassembles to no-op/false. Five verifier guards
pass. Same-build optional012151 actual1/2/3/1 RGB/new-frame gate passes with
exact settings/hook restoration/cleanup[]. No production change/phone/Core/
restart/publication. Native-only angle unavailable; not every old timeout is
classified. Compact WEB110/RESULT.md. Continue runnable scan/caption work.

Current2026-11-20 01:14Z: next independent WEB109 investigation completed.
Real private-Xvfb/Openbox headed WebKit window minimizes/restores, but page
stays visible/hidden=false; classify BACKEND_VISIBILITY_NOT_OBSERVED, NOT media
recovery PASS. Parent WP16-002 stays partial. No phone/server access, fake
visibility override, package install or production change. Exact owned display/
browser/WM cleanup verified. Compact WEB109/RESULT.md owns evidence/limits.
No active field runner; WEB108 still installed005411/WAR3867eaf2, no publication.

Current2026-11-20 01:07Z: WEB108 is ledger-complete in bounded desktop/Linux
scope. Installed production Apply WebKit paused010141(-435ms), Chromium playing
010243(-611ms), Chromium paused010354(-127ms) and WebKit software→QSV010510
(-328ms) pass new producer/700k/encoded480p/eight-second moving output/clock/
profile restoration/cleanup. GPU case is encode-only fallbackStage1, not full
D/F/E. DOM settings24each engine; existing DVD11each/ordinary seek26/local
ownership guards and clean193input/11commands exact pass. Final stock20/zero
encoders/recordings/UIs/clients independently verified. No runner remains.
No phone access,3h test, Core/restart/.175/Windows action or publication.
WEB105 phone restoration/recovery/abort, original WEB107 source, broader DVD
capabilities/equipment and original rollback artifact remain explicitly open.
Remaining exact scope: docs/parity/NON_PHONE_READINESS.md. Completed/corrected
owned captures retire recoverably; two minimal unclassified observer/setup
JSONs remain. Do not call them a proven product regression or a fixed root cause.

Current2026-11-20 01:00Z: WEB108 production implementation installed through
normal manager snapshot3.3.0.20261120.005411/WAR3867eaf2/package d705c594.
Live WAR/15served/20stock match;193input/11command Git-less rebuild exact.
Local stock DVD/ordinary native seek26/DOM DVD11+settings23 each engine pass.
Feasibility public Seek passes Chrome and paused/same-position WebKit; actual
production Apply paused WebKit gate running. No phone inspection/input, restart,
Core change, .175/Windows action or publication. Installer UI was exact test
identity only, original SageMC restored, native retirement independently zero.
Earlier WEB108 failures were harness constraints/oracles: POST settings reads,
unsupported360p/boolean conversion, counting MIM+real encoder as two encodes,
display rather than raster height, and requiring FLUSH/pictures while paused.
Do not count those as product regressions or silently rewrite them into PASS.

Current2026-11-20: non-phone implementation continues, not a checkpoint stop.
WEB108 tests public stock DVD Seek as a profile-generation boundary using only
the exact disposable desktop UI/canonical authored source. Initial002558 had
an invalid360p harness parameter before Save dispatch, not a runtime failure.
Supported480p/lowercase wire/profile-intent correction is under live test.
WP17-004 actual byte search355candidates/382archives/8WARs finds no expected
hash;7bound-skipped entries explicit. No phone access, Core edits or publication.

## Current2026-11-19 — no multi-hour testing; short coexistence gates only

User explicitly removed the three-hour test requirement. Do not restart it or
wait for an idle window to satisfy it. Historical42m interruption was an
over-strict harness restart-idle check, not evidence of single-client product
behavior. Ordinary public-HLS playback permits known co-tenants; keep restart
guards unchanged and label shared resource attribution. The field CLI rejects
multi-hour requests. Phone access remains withdrawn; WEB105 awaits return.
No production binary changes or publication are required by this correction.

00:05Z continuation: actual WEB106 Chromium/WebKit coexistence passes; two
native fixture consumers survive a third public-HLS20s stream and owned Stop.
OWN-01 four isolation rows pass. Final source-change000131/000245 passes2each,
new frames/native clocks/caption generations/profiles/producer retirement.
WP11-008 bounded available scope ledger-complete, no3h requirement. Installed
221217 unchanged; phone unavailable/on VPN, no phone action. No publication.
WEB097 proven startup/shutdown scope is now ledger-complete; unresolved exact
missing-tail case split to WEB107 rather than claiming its root cause fixed.
NON_PHONE_READINESS.md lists remaining implementation/capability and missing
phone/source/equipment/rollback boundaries. Independent final stock20 matches,
zero encoders/recordings/UIs/connected clients. No .175/Windows mutation.

## Historical2026-11-19 22:29Z — PHONE-FIRST, WEB105 active

Current23:39Z: no active test runner. Phone withdrawn; no input/inspection,
keeperOFF. WEB104/103 complete, reports audited and short affected gates pass.
Elapsed225500 intentionally interrupted by new phone UI around42m, not a crash
or3h PASS: last checkpoint2514.824s75332frames/0recoveries/regressions. Own HLS
API404/no matching process independently verified, other playback preserved.
Continuous3h/resource qualification waits for an idle232 window; memory growth
in partial run is recorded without a leak/no-leak conclusion. Compact
WP16-006/ELAPSED_20261119.md retains boundaries. Future phone harness now has
cooperative cancellation and private originals saved BEFORE borrowing;8actual
extracted/source guards pass offline. This does not restore the old223249 run.
No commit/push/release, Core/restart/Windows/175 or phone action.

Historical non-phone continuation: WEB104 host Chromium22391820.021s609frames
and WebKit22531420.044s613frames both480p/1Mbps/zero recovery/regression PASS.
WEB103 both-engine strict refusal/one-shot allowed H264 and4hash-verified normal
diagnostic exports PASS; both tasks ledger-complete. Headless audio/backend and
offscreen test-video fixes are harness-only, no production replacement. Actual
3h Chromium elapsed/resource soak running under activity/storage/frame guards;
no competing producer/restart, not PASS yet.17owned raws538715bytes retired to
rootdeleteme with exact per-file hashes/compact results; open failures retained.

SUPERSEDED22:39Z: user withdrew the phone. No more phone inputs/inspection.
WEB105 runner stopped, keeperOFF/zero input leases verified; independently
zero232 UIs/recordings/clients/encoders and protectedstock20 PASS. Interrupted
223249 report has no final profile/observer-restore proof: preserve checkpoint
and CAS-restore only when the same phone returns. Quality700 actual pictures
and failure-state presented ACK observed;900 recovery/abort NOT certified.
Switch to host WEB104 focused profile, WEB103 Copy/report, then real elapsed
soak and independent audits. No publication/commit/push; Windows deferred.

Historical: Normal manager66774 installed221217/WAR8ce7c0d4/DEV packagee980539e; Done-OK,
independent UI retirement, liveWAR/15served/20stock/INI/engines pass221537.
No server restart/Core/engine change. Actual phone public-HLS profile221620
and221750 PASS20s each; latter directly proves852x480/new615class callbacks/
1000kbps target/full-QSV D/F/E, original profiles/watch state and decoder cleanup.
Four focused earlier tail/reconnect5/7/5/7 runs passed; unique203329 unclassified.
Fresh phone reload222004 passes and reconnects idle exact UI. WEB105 newly
audits prior host-only source-preview/quality handoff/recovery/abort on the
actual native phone. Runner25646 ACTIVE: one inspector, keeperON60s, do not
compete/flash/restart. First222517 preview attempt lacked ready-range proof;
cleanup/profiles/observer restored, no new production failure classification.
Harness now explicitly waits range.enabled/max>=45. Host-only WEB103/soak wait.
User says continue TESTING, do NOT publish/commit/push. Windows remains deferred.

## Current2026-11-19 22:09Z — actual phone work continues, no publication

User objects to checkpoint stops and prioritizes every executable phone row.
Paired inspection/HDMI confirmed actual852x393 page, keeper ON60s. Focused
215920EOF5/220050seek-bounce7/220220EOF5/220553seek-bounce7 PASS, cleanup0;
unique203329 did not recur and is NOT declared fixed. Exact original evidence
remains. Compact WEB023/REMAINING_20261119.md reconciles old phone checklists.
Phone explicit Exit runner48203 is retiring the exact idle test UI for normal
manager update; no other inspector until it completes. WEB104 fixes proven
legacy public-HLS profile omission: fail-before validation,12checks nowPASS,
legacy null-options path unchanged. Candidate WAR8ce7c0d4/packagee510b7bd,
epoch1795126000 built. Java/HLS/stream gates5663 running; native phone1Mbps/
480p and normal-manager loaded-WAR proof PENDING. No Core/engine/INI change.
The earlier3h host run retired intentionally at~17min because legacy8Mbps
would hit unchanged8GiB guard; no three-hour PASS. Next WEB103 owned-MPEG2
Copy/report then elapsed soak after dependent fixes. No commit/push/release.

## RESUMED2026-11-19 — finish authorized tasks

User objected to the checkpoint stop; RESUMED remaining-item audit. WEB102
isolated production HLS monitor/private192MiB tmpfs gate22checks PASS: actual
free-space crossing and464ms stop, output-budget484ms stop, unrelated sentinel
survives/healthy new stream ends. Sandbox retired/no server mutation. New
explicit2h/3h elapsed mode starts source0 rather than mislabeling5h seek+600s.
7safety contracts pass; extended3hour Chromium run now starting on stock232,
public HLS source1444 only. No phone inspector/restart/competing producer until
it retires. Other activity aborts only its owned consumer; unknown Stop never
replayed. Prior session-close/keeperOFF state is historical, not task completion.

Current21:25Z available phone acceptance/final audits COMPLETE, no active runner.
Exact live WAR15e888cd/15served/stock20/JAR/wrapper/INI/engines pass212149;
zero recordings/encoders and idle exact phone UI retained. KeeperOFF/zeroinput
sessions. WP112/127complete/15open; no additional available row is marked PASS
without its source/equipment/protocol.61owned raw/tempfiles16,029,557bytes
retired recoverably with per-file hashes in WEB101/CLEANUP{,_FINAL}.json and
root CLEANUP_REPORT. Unique203329 remains; subsequent211729full8PASS is not
its root-cause proof. Compact SESSION_CLOSE.md records current scopes/limits.
No publication/commit/push, Windows/175/Core/INI/engine change. Historical
ACTIVE/next-audit notes below are superseded, not running work.

Current21:22Z: WP05-006 CEA audit ledger-complete, original708service1 real
iPhone211522 PASS4/cleanup0 (service1/absent2 clear/return/Seek0 newframes).
23service/18authority/18loss and both-engine12DOM checks pass; partial708
SWA/DLY/character/style limits explicitly recorded, no all-standards claim.
13phone-harness safety contracts PASS. Final targeted full fullscreen PMT
lifecycle211729 PASS8/cleanup0, unique203329 stall not reproduced and remains
unclassified. No active phone test now. CanonicalWP index112/127complete/15open,
248upstream entries reconciled.55reviewed raw files15,826,083bytes retired to
recoverable rootdeleteme, compact WEB101/CLEANUP.json retains exact paths/hashes.
Final stock/assets/task/manifest audits next. No new runtime/publication.

Current21:13Z supersedes historical ACTIVE notes below: manager80699 retired;
installed202559/WAR15e888cd/packagef900c899/main+playback+SW101.1/controller100.1,
15servedassets/stock20/INI/engines verified. WEB100/101 and WP04-007 available
lifetime gates are ledger-complete. Phone203814 PASS8, EOF204645 PASS5,
seekbounce204933 PASS7, fullscreen205438 PASS4 and205927 PASS5 with actual3s
HDMI/red-strip review. Ordinary90s EOF204331 PASS3. Original UK201504 PASS5.
Unique203329 native tail stall remains unclassified (no actual ended); retain
minimum evidence, don't claim later passes prove its cause. Canonical fixtures
stay. Current next: original broadcast708 service1, found168complete packets
in exact18.8MB prefix; new helper Save observer failed before Watch, known
STV/auto profile restored211304 and corrected helper running serially.
WTTW194346 natural fullGPU960s complete; original84256 tail is absent.
No publication, Windows/Core/engine change or competing phone inspector.

20:28Z: WEB100 complete/ledger, normal-manager200758/7962d389 and actual phone
PMT4+originalUK5 PASS. Lifecycle201908 then reproduces real EOF with480DVB
pixels still visible (seek new-generation row PASS), all cleanup/profiles0.
WEB101 pure browser confirmed presentation-end callback passes95player,
both-engine EOF7/ordinary7/DVD11 and clean194input/13commands. Manager80699
ACTIVE installing202559/WAR15e888cd/packagef900c899; no competing inspector.
Verify served bytes/stock/dependencies, quit/independent retirement, reload
approved idle phone, then lifecycle. Original source84256 and exact file are
absent (public404,exact-path resolve400,remote test absent); original-completion
helper200239 starts no encoder. Preserve old diagnostic/prefix evidence; no
exact failed-file replay claim. No Core/INI/engines/Windows/publication change.

20:02Z: runner7854 FINISHED PASS2, WTTW natural-end/fullGPU D/F/E; actual
nativeended960.392s/28640frames,producerexit0/ENDLIST and exact84501 removal/
profiles/schedule/observer restoration. Independent stock20/zero recording/
encoder proof follows. Fixture84502 guarded staging/readback/public scan PASS;
phone PMT runner93178 ACTIVE, English480white pixels/advancingframes observed.
No competing inspector/encoder. Original full-input replay after phone row.

RESUMED by user 2026-11-19 at19:43Z. Exact phone readiness/stock20 and zero
recording/encoder checks pass. Keeper explicitly ON60s; runner7854 owns WTTW
natural completion through20:00Z, growth already PASS. No competing inspector
or producer. Next prepared PMT/language physical gate and original-input replay.
Local PMT real decoder4phases and recording-harness11contracts PASS again.
No new runtime/package/Core change or publication.

Historical PAUSED by user 2026-11-19 at 18:23Z.
Runner70549 exited, cleanup=[]; owned84396 cancelled for pause. Its report
180242 records premature completion after cancellation: USER INTERRUPTION,
not a demonstrated production failure or natural-ended PASS. Independent
verify-stock: all20 protected files match, zero recordings/UI/client/encoder
processes. Firmware keep-awake OFF and zero input leases. No further testing,
implementation or publication until user resumes. Installed Web174337,
FFmpeg0.1.27/MIM0.4.14 remain. WP04-007 fixture/local decoder PASS; staging and
physical gate NOT RUN. Original full-input replay NOT RUN. Preserve active
failure evidence. Resume with natural WTTW end, prepared PMT field row, replay.

18:02Z: WTTW natural11778 FINISHED growth PASS, completion NOT qualified.
Harness sees ENDLIST before the process monitor's exit receipt, asserts too
early and finally Stops its own producer; it failed to save that final sample.
Independent exact wrapper4088/child4094 log shows12:00:02 child exit rc=0;
stock20/0encoders/0recordings verified. Thus do NOT call this a proven QSV
crash or silently convert it to physical-ended PASS. Own84394 retained.
Harness now saves completionStatus and read-only waits for running=false plus
actual exitCode before validation. No production/runtime change for this
observer race. New natural11.1 final acceptance remains needed; preserve the
failed report174842 and meaningful log result. No active inspector now.

17:48Z: manager79235 installed development174337/WAR2821a856 through ordinary
Update Plugin (WAR reload/old UI retirement, no server restart), then quit.
Live WAR and174758 dependency verification PASS; all20stock files/INI/engines/
MIM0.4.14/FFmpeg0.1.27 unchanged. Independent manager retirement/0recordings
before approved phone reload174800; exact fresh phone UI only at174827.
New natural WTTW11.1 runner ACTIVE through real18:00Z EPG end. Do not start
another phone inspector/encoder or restart. Default-QSV-only IDR fix is now
installed; production browser assets unchanged. Firmware keeper ON60s.

17:44Z: WTTW held-raw exact-command A/B173446 proves missing IDR in the OLD
default HLS builder: no playlist before raw EOF/one20.187s segment versus
forced_idr=1 first playlist1718ms/seven3s-class segments. Regression fails
before/passes after46commands; minimal default-QSV-only correction LOCAL.
25982 focused lifecycle/HLS10/stream17/quality4/recovery11/playback92 PASS;
clean194inputs/12commands exact WAR2821a856 PASS. Packagef4f9e72b, dependency
min0.1.27 now sourced consistently from release.properties. Normal catalog
174337 staged; manager79235 ACTIVE at Setup. DO NOT restart/compete/attach
phone inspector until manager quits and independent retirement is observed.
Phone exited174233; input keeper ON60s. Planned next natural WTTW11.1 gate.
MIM0.4.14 actual one-picture4rows173138, ALADDIN20s/486newpictures/pixels/
clock/Stop173239 and original UK TT/DVB/Off5rows173340 PASS; profiles preserved.
Calibration trusted BLE Play/12s HDMI audio also recorded, capture-path median
audio-leading-red144ms includes capture latency, NOT receiver certification.
Calibration closed/offset0 and decoder retired before phone Exit. No Core,
175/Windows/publication changes. Earlier active-run notes are historical.

17:31Z: natural runner27016 FINISHED PASS2. CBS2.1 owned84391 consumes
415132952bytes, final HLS494.160s/exit0/ENDLIST; native Safari actual ended
493.574s/14708frames, no error. Exact owned test media removed, original empty
schedule/profiles/observer restored, cleanup0. Software fallback, not fullGPU
or original WTTW-stall root-cause proof. Compact WP11-008RESULT updated.
37504 owner/readiness batch is next; affected one-picture/DVD/caption rows
follow, one inspector at a time. Keeper ON60s. Earlier27016 ACTIVE superseded.

17:19Z: FFmpeg0.1.27/MIM0.4.14 installed through the normal manager39001,
Restart Later/manager retirement followed by guarded232 restart171009Z.
171125 dependency verification matches plugin/wrapper packages, unchanged
INI/engines/Web WAR63184ec8 and all20 protected stock files. Media28361 and
package52428 PASS; prior active-session notes below are historical. User
reopened SageTV Vibe/confirmed AssistiveTouch after a premature test reload
hit the restarting server. Actual phone readiness171829 PASS, connected exact
phone123c8282e1ee/landscape852x393. Natural-completion runner27016 ACTIVE;
do not attach another inspector or interrupt its owned recording. Firmware
keep-awake ON60s. No175/Windows/Core/publication changes.

MIM-PIPE-002 implements bounded64KiB/nonblocking raw child input/POLLOUT;
diagnostic drainage and signal handling continue under raw backpressure.
Regression18850 failed before10s;28025 after passes1MiB/17bursts;55623 passes
EOF6/control/isolation plus raw SIGTERM6ms/unrelated preservation. Both0.4.14
wrappers built35651; four engine hashes unchanged. Media28361/package52428
and phone Exit91540 ACTIVE. No other inspector, no server update yet. Candidate
FFmpeg0.1.27 pairs0.4.14. Helper now waits through intermediate hardware-stage
failure, retaining bounded final software failure; sample retries read-only.
Resume physical natural completion only after guarded normal-manager update.

## Historical PAUSED2026-11-19 at15:57Z — explicit user request

All runners40597/5627/37495/18850 and phone inspectors are FINISHED. Firmware
keeper explicitly OFF,0input sessions. Independent232 recording0/encoders0/
connected clients0; one idle phone UI,20protected stock files unchanged.
No more test actions until resume. Installed Web154016/WAR63184ec8 and
FFmpeg0.1.26/JARc234b3d8, unchanged INI/engines/MIM0.4.13; actual health API
protocol1 available, clean194inputs+provider/12commands PASS. No publication.

Natural field154754: actual growth/8014frames268.6s PASS, then read-only WebKit
RPC TimeoutError (not decoder failure). Finally exact reservation cancellation/
observer restoration/public Stop succeed; no orphan. Added three bounded
read-only sample retries, never mutating-control replay. Retry155528 encounters
hardware-stage Broken pipe while fallbackStage1/runningfalse and helper calls
it terminal prematurely; preserve report, fix helper to await final fallback
stage/readiness within its bound BEFORE another field attempt. No final natural
completion PASS. Own partial recordings84285/84287 retained for investigation.

Completed original84256 default API producer starts6.359s/fullQSV and public
Stop62ms/independent0encoders passes. Comparison154709 supplied stream options
to old HlsControlServlet, which ignores them: only duplicate DEFAULT evidence,
NOT a phone-profile pass. Helper now refuses that unsupported profile choice.

New MIM source-independent offline test run_raw_duplex_tests.py reproduces
current Linux wrapper deadlock: child emits >pipe-capacity diagnostic bursts
before reading media; wrapper blocks in raw pin write and cannot drain stderr.
18850 fails boundedly10s, owned temp process group cleaned. This is proven
synthetic defect, still NOT proven original broadcast-stall cause. Proposed
fix: bounded raw pending queue/nonblocking child stdin/POLLOUT, keep draining
stderr and signals, delay child EOF until queued raw bytes drained. Preserve
control-mode/Windows semantics. NO C++ source/version/package change yet.
MIM required README/HANDOFF/TASKS/WORKFLOW+AGENTS fully read this turn. Existing
DEV /project maps MIM source. Continue failing-before regression/EOF/control
gates and normal-plugin-only deployment after resume, not direct binary copy.

Root CLEANUP_REPORT still needs entries for the three clean archives retired
by verify-clean-runtime (153815/153930 failed installer-toolchain comparison,
154004 PASS). Keep meaningful failed-case reports; no broad artifact cleanup
performed at pause. Web manager screenshots097 remain task-owned active.

## Current2026-11-19 — physical iPhone tests FIRST

Current15:46Z: normal manager40597 installed Web154016/WAR63184ec8 then quit;
actual health reports ownedProcessStopAvailable=true/transcoderAvailable=true.
154431 dependency verification PASS: all20stock, both expected plugin hashes,
unchanged INI/FFmpeg/ffprobe/MIM0.4.13, independent activity0. Git-less194inputs
plus test-only provider/12commands PASS. Windows-host ZIP initially differed
only installer bytes (WAR identical); rebuilt package in standard DEV Linux,
restaged154016 and qualified exact7717cf19 installer. No public release.
Phone approved reload154457 completed. Reconnect runner41479 and exact retained
completed1080i HLS comparison50027 now ACTIVE (one producer, bounded Stop).
Do not start another inspector/encoder until those runners finish. Keeper ON60s.

Historical15:33Z: normal manager installed FFmpeg0.1.26; Restart Later selected,
manager retired independently, then one activity-guarded232 restart153119Z
returned. Read-only153248 verification PASS: actual JARc234b3d8, all20stock
files, unchanged INI/FFmpeg/ffprobe/MIM0.4.13 and Web099.2b07ddf. Independent
recording/UI/client counts0. No manager/inspector active. Current Web097 source
adds the shared lifecycle consumer, retained-owner admission fence and health
capability reporting; focused rerun56463 ACTIVE. Do not install the prior local
WAR: rebuild/package current HealthServlet first. Phone remains explicit Exit;
ESP firmware keeper ON60s. No Core/settings/engine changes or publication.

Historical15:27Z: MIM-PROC-0010.1.26 package ready (JARc234b3d8), staged through
normal developer catalog; protected stock20/independent0recordings/UI/encoders
verified before staging. Baseline WEB097/152507 retains six live file hashes.
Phone explicit production Exit152357 confirmed, profiles unchanged; UI retired
independently, no Stop replay. Catalog refresh via allowlisted SageMC read
refreshed all available plugins without restart (FFmpeg ID itself not allowed).
Manager25882 ACTIVE, exact da92a86446be browser, Setup41 submitted once. Inspect
its current screenshot before next input. Do NOT start another manager/restart.
Web097 consumer integration now LOCAL: ownership retention/admission fence/
status/isolated reaper; affected blocked-pipe/DVD/HLS10/Streaming17/quality4/
recovery11/playback92/harness9 pass. Older/missing provider refuses managed
startup; min FFmpeg0.1.26. Web candidate NOT installed; live WAR099.2b07ddf.
Install FFmpeg through current manager, quit/independently idle, guarded restart
to load global JAR, verify INI/engines/stock and then package/install new Web.
No inspector attached; ESP firmware keeper ON60s. WEB099 accepted/ledger/cleanup
94raw files retired; retain only three unclassified half-rate witnesses.

Historical15:08Z: WEB099 current physical motion accepted (user: Now smooth).
Fresh Native/MSE180s, exact580s scene/pixels,209s+600s MSE14392frames/six
pixel windows/later-scene HDMI, and explicit SAME-producer native-to-MSE120s
2893frames all pass scoped gates; exact profiles/property/prototype/Stop
restored. ALL runners finished; no inspector attached. Final0encoders and20
protected stock hashes/liveWARb07ddf verified. Original half-rate142308 HDMI
and141732 raw witness remain unclassified, not retroactively proven cured.
Ledger and WEB099RESULT retain bounded correction/acceptance scope.
Next WEB097 blocked-pipe/natural-recording completion. MIM-PROC-001 public
Process-only facade over existing OwnedProcessStop is LOCAL ONLY; independent
Java8-target blocked-duplex/unrelated preservation test passes. New Web
OwnedProcessControlBridge and local smoke pass optional API/bounded refusal;
NOT YET integrated into HlsSessionManager, packaged or installed. Older/missing
provider must decline safely (Process.destroy can kill wrapper before blocking,
orphaning a child). Retain Process and refuse replacement until confirmed stop;
update dependency/affected lifecycle tests before normal-manager installation.
Live runtime still099.2/FFmpeg0.1.25/MIM0.4.13. No Core/INI/engine change.
Firmware keeper ON60s for remaining phone work; disable when phone work ends.

Historical14:43Z:600s MSE observer33930 completed14400frames/1x/zero recoveries,
but visible motion FAIL remains. HDMI142308 has~12picture changes/s. Fresh
Native HLS180s143333 and production HLS/MSE180s143804 both show~24distinct
pictures/s over HDMI; MSE alone is not proven cause. Player borrow restored
exactly. New runner16029 ACTIVE: exact ALADDIN, one public seek580000ms,
180s observation and bounded decoded-pixel witness; no second inspector.
Capture current stream/HDMI while it runs. Compact WEB099RESULT records scoped
evidence and open motion failure. Runtime/profiles/Core unchanged.

Historical14:27Z:099.2 installed through normal manager141111/WARb07ddf; all20
protected stock files and15 served assets verified. Actual BLE Play141646
activated playback, followed by the guarded SAME-producer MSE startup fallback.
Runner33930 observes600s, with~24 actual frames/s and1x clock through553s,
no error/recovery. User nevertheless reports sluggish/non-smooth motion: this
is an OPEN visual failure, not qualified by counters. Preserve HDMI142308
(30s, video only) and source/output cadence witnesses. Source has progressive
MPEG2 soft-telecine repeat_pict0/1; investigate conversion without assuming
that proves the motion cause. Do not attach a second phone inspector while
runner33930 remains active. It performs one guarded Stop after observation.
Firmware keeper remains ON60s; no new settings/Core/MIM changes.

Historical14:12Z: first099.1 queue fix installed135618/WAR2d1daf/stock20; failed
standalone139 becomes130s hardware PASS at async_depth1. Actual producer
4573f599 stays alive, but native Safari freezes1us with14.164s buffered and no
presented frames after trusted ESP32 Enter140401. No synthetic activation.
One public showContent2504 accepted/fullscreen; still frozen, same producer.
099.2 adds guarded client-only same-producer MSE startup fallback;92tests PASS,
fail-before regression, package72/216/currentWARb07ddf. Staged141111; existing
public plugin.commission_available(SageMC,refresh=true) refreshed catalog
without restart. Manager runner66244 ACTIVE, installing exact Web update via
normal STV UI. Phone exact Stop/explicit Exit141016/profiles preserved. No
inspector attached. Do not start another manager/phone during this install.
After manager success/livehash/idle, reload phone, reconnect after explicit
Exit if necessary, one real BLE Play if requested, then observe-existing600s.
Two prior physical soak attempts are FAILED (autoplay and frozen-startup),
not user-confirmed motion. Clean rebuild rerun15216 underway for099.2.

Current13:51Z: user reports DVD sluggishness; WEB099 is active and FAILED.
Exact ALADDIN2504 phone remains loaded, paused at78.118s after six exhausted
recoveries; current HLS15fa27bb92354136a769cd97824239d6 exited139/noENDLIST.
Kernel libmfx-gen1.2.16 segfault, standalone same-profile QSV source benchmark
reproduces139; setfield=prog does not fix it. Async-depth1 comparison running.
No inspector attached. Firmware keeper ON60s. Optional companion angle test
133558 PASSED actual RGB1→2→3→1; plugin/hook/profiles exactly RESTORED133706.
Do not replay stale ResourceTiming session5c9ef9 or call600s soak PASS.
Preserve active WEB014/133823 failure+134011 HDMI, WEB099/134802 source/status.
No runtime changes since131032 yet; stock Core remains protected.

Current13:34Z: WEB098 CLOSED after real live11.1 Wild Kratts84274→Weather
Hunters84275 at13:30Z,243newframes/10s/fullQSV/no repeated tune/cleanup[].
Normal-manager131032, exact WARfb0de3/stock20. Recording-tail3rows pass.
Now optional companion physical angle test is running; four settings and
exact phone DVD hook temporarily borrowed in
artifacts/active/WEB-023/20261119T133200Z-companion-angle-borrow.json.
Browser form changed ONLY companionDvd=true; owner __iphoneGate remains.
MUST restore plugin hook/settings before retiring phone; then production form
and exact raw profile restoration/observer retirement. No Bridge flash.

Historical13:25Z: normal manager131032 installed exact WARfb0de3/stock20. Actual
phone recording-tail131900 PASS3/native841frames→ended/no stale buffering/
profiles unchanged. Live retry85688 ACTIVE, report WEB098/132126, WTTW11.1
Wild Kratts84274→Weather Hunters13:30Z. HDMI132244 fullscreen verified;
one Watch and source-scoped showContent. No second inspector/tune/install
until boundary+150s and exact runner Stop. Firmware keeper remains ON60s.

Previous13:11Z: live runner18798 FINISHED/FAILED1row, cleanup[]. Actual13:00
boundary stalls native file84259 after browser ended, clean exit0/ENDLIST and
activeRecording=false. No second tune. Fix now forwards existing stock basic
Pull -1 EOS only for exact tagged completed HLS presentation; Core decides live
advance vs recording EOF. Unit/socket/seek/DVD guards are under focused test;
development build/normal-manager install and physical boundary retest next.
No second inspector remains attached. Previous active1252Z note is historical.

Current1252Z LIVE runner18798 active, exact phone only. WEB098 actual public
Watch(Airing38223) on ABC7.1, own live media84259, nextGMA at13:00Z.
Report artifacts/active/WEB-098/20261119T124722Z-iphone-live-handoff.json.
Actual Native HLS/QSV decode+filters+encode, new frames, no second Watch/tune;
observe through boundary+150s then exact phone Stop. DO NOT attach another
inspector or install/restart during this run. Explicit Full Screen On woke
the SageMC screensaver into preview; one distinct TV command then made actual
HDMI125202 fullscreen ABC/weather/timeline. These are public synthetic setup,
not a Guide-finger/BLE claim or another tune. Initial125049HDMI was screensaver
despite decoded video, so frame counters alone were NOT visible-output proof.

Phone production source changes123859 PASS4 (20905→84231→20905, native clocks,
fresh producers, Stop and saved profiles). Native angle124014 initially failed
its stale-session observation. Field owner now observes a FRESH outgoing real
events poll instead of a potentially full/stale ResourceTiming buffer; wait32s,
preserve fetch receiver and restore observer. Actual native angle124247 then
proves red angle1 but one accepted Angle Change never reaches native angle2.
Keep that real failure separate from the corrected test-session oracle. Current
DVD source has naturally ended/unloaded; no companion borrow occurred yet.

After live run, complete optional companion physical angles/remaining available
phone rows. WEB097's real default-HLS end/Stop failure remains open; existing
FFmpeg package-private OwnedProcessStop is a proven reusable implementation.
Its exposure/use needs bounded owning-repo work and normal-manager updates,
not Core or live file edits. FFmpeg AGENTS read; HANDOFF read attempt was
TRUNCATED in orchestration output, so finish required complete reads (README,
STVI_DESIGN, sibling ffmpeg-mim-changes if present) before making source changes.
No production source/package/plugin/engine/firmware change this turn yet.

Current1239Z:96564 finished FAILED at natural completion, not running.
Native Safari advanced~20minutes/36kframes but producer stalled at1236.001s,
noENDLIST despite actual completed1305740ms file. Public Stop deadlocked;
MCP threads123311 proves296stdin-write lock→59Process.destroy.close/flush.
Verified exact owned ffmpeg_MIM7468/ffmpeg.real7474 released123839Z using UID99,
parent/executable/session/start guards; initial cleanup guards refused without
mutation because default Docker UID could not read other-UID exe links.
No API Stop replay. Independent0encoders/recordings,20stock unchanged.
Media84256/1.279GB retained (unwatched/resume0/manualfalse) for open failure.
Current phone inspector runner36543 is production recording source changes,
NOT the old standalone natural-end test; do not attach another inspector.
User asks live TV to continue next programme: WEB098 now owns true live tune/
handoff, distinct from finite recording EOF. WEB097 expanded with proven
cleanup deadlock; FFmpeg plugin already has package-private OwnedProcessStop
for reuse through a bounded public owning-plugin API. No runtime fix yet.

Live runner exec96564:120802Z phone natural-completion test, own media84256/
airing43057 OddSquad/WTTW11.1. Source ends12:30Z. Paired inspector remains
attached; do NOT attach another phone operation client. Actual native frames/
growing input and HDMI120942Z pass; effective software fallback, not fullGPU.
After it finishes, run prepared iphone-recording-changeover-field.py then
current native angle/remaining applicable DVD rows. Phone busy on this real
natural-end observation; no desktop matrix launched. Keep awake60s firmwareON.
Owned prefix18,800,000bytes/20.189767s retained server-side as
OpenSageTV_Vibe_Tests/WEB097_LIVE_WTTW_STARTUP.ts, SHAa73042ed73a4514c76e2a18449298f842e9ecca8c780e09b371e2191f7771d9c.
Probe confirms1920x1080 top-field-first MPEG2/AC3. No library import/Core edit.
First copy receipt timed out; independent observe-existing confirms complete
size/hash, no copy replay. WEB097startup fallback remains a separate open task.

Latest user priority is to finish all available phone tests before desktop-only
work. HDMI, paired wireless inspection and encrypted ESP32 input are working;
firmware-owned keep-awake is enabled60s during testing. Phone Exit reconnect
passed115715Z on096 without changing profiles. Growing-recording testing uses
the actual phone and newly owned capture; no stock Core changes. The prior host
CancelRecord result is inconclusive because its native live viewer retained the
tuner lease. A standalone native Safari HLS completion row isolates that lease;
it must not be described as native-STV rollover or audible/finger certification.

## Current2026-11-19 — recording test authority GRANTED

User explicitly approved finishing all tests, including the requested short
test-only recording creation and removal. Previous unanswered-approval notes
below are historical, not a current blocker. Use an independently free tuner,
checkpoint existing schedules/library, own only new test reservations/media,
dispatch each ordered operation once, and restore/remove only owned test work.
Stock Core/engines, unrelated recordings/profiles and publication remain protected.
Next: actual content-first future Record/status/cancel; real growing recording
playback through completion/changeover, then affected remaining matrix rows.

Final08:51Z: sustained raw65376bytes retired SHAverified to matching rootdeleteme
after compact result; root cleanup report updated. All current15served/liveWAR/
72package assets/216Java8/stock20 exact;3fixture+5field+3metadata tests/mirrors/
565tracked-source manifest/write-check/whitespace audit pass. No completed
checkoffs remain in active project/workspace sections. New helper/source work
remains unstaged; manifest tracks currently tracked565files only, not a claim
that unpublished/untracked helper files were committed. No active processes or
remaining environment restoration. Further required recording growth needs
the unanswered test-recording approval; do not assume it or replay unknown
controls. Keep separate missing-source/equipment/rollback/publication boundaries.

## Current08:49Z — audio and sustained follow-up finished; no active runner

083756600.032s sustained Chromium field PASS:9→17986frames/time0.327→600.340,
zero decoder error/recovery/clock regression, fileclock rounding+0.307ms.
21resource samples: baseline1.541GiB/peak2.105/final1.655, PIDs97/122/94;
Docker multicore CPUpeak210.92%. No CoreWatch or original watched/resume change.
Owned producer/decoder/browser/SSH retired; independent0recordings/UI/clients/
encoders and stock20. Compact WP16-006/SUSTAINED.md; no elapsed-multi-hour,
live-growth/OSD/disk-pressure/acoustic claim. exec42401completed, no process left.

WP12-001 closes bounded original/static/generated PMT/layout/latePID output
acceptance;110/127WPcomplete/17open including5unapproved optional Core proposals.
Minimum083318connection-timeout note/output and083526cleanup-unknown report
remain active. Eventual idle is verified but no timeout-cause/fix claimed.
Fixture/safety3+5/metadata3/mirrors pass; current15served/liveWAR/package match
096/073911exactly (216Java8/72assets), runtime not rebuilt for helper-only work.
13completed/corrected raw audio files +helper14total/1,283,256bytes retired
SHAverified recoverably; canonical source/phases/server fixture preserved.
Phone remains productionExit/firmwarekeeperOFF, no further phone input.

Remaining runnable growth/futureRecord needs the unanswered short test-only
recording approval. Real caption-service/property-peer/receiver/controller and
exact rollback artifacts/publication authority remain separate; Windows deferred.
Do not treat missing approval as no-recording or close unobserved rows. Broad
final matrices follow release-bound dependency stability, not repeated now.
No175/Windows/Core/firmware/commit/Git staging/publication mutation.

## Current08:40Z — audio PMT/layout accepted; sustained field RUNNING

096/manager073911/WAR2e85e0 unchanged. New canonical generated32s audio source
84231/4,901,724bytes/SHA60f1ba4c73f7dc2688439ecda25e232c8a6a4308cd37cef370d1bdf76ee2dea6:
PMT0→1/EnglishAC3PID257mono→5.1/lateNAR1320HzPID258 at16s. Generator, guarded
new-only public-library stage and real-browser/audio-spectrum runner added.
Primary Chromium082918/WebKit083048 each5PASS; explicitlateNAR WebKit083211
4PASS. Chromium0835264functional assertions PASS but overallFALSE due final
read-only retirement-query connection timeout. Independent host/DEV0activity/
UI/encoders/stock20 confirms eventual cleanup, NOT cause/fix.083318same read-only
timeout escaped finally/lostJSON; minimum note/output and083526report retained.
Runner now preserves failed cleanup observation instead of losing report.
Compact WP12-001/AUDIO_TRANSITION + prior static/phone evidence closes bounded
functional WP12-001 in ledger; canonical110/127/17open. Live UI inventory-refresh
is NOT proved by tail-probe discovery; growing/live WP11 and acoustic12-007 open.

Single actual10minute sustained/resource field started: exec42401,
tests/stock-long-recording-field.py --engine chromium --soak-seconds600
--only-soak. One18000s offset, existing5.5h1444, no CoreWatch/watchmetadata
mutation, no repeating completed landing/tail rows. Actual container resources
every30s, production frames/clock/recoveries sampled; final result pending.
No other browser/phone test running. Phone remains productionExit; firmware
keeperOFF, no further BLE/OS/unlock/bond input. Do not start a second producer
or call idle from zeroUI alone: one owned ffmpeg.real is expected during soak.

Short test-recording approval still UNANSWERED; no recording created. All
Core/engines unchanged; no175/Windows/Git staging/commit/publication mutation.
Fixture contracts3 + existing field contracts4 + metadata3 + mirrors pass.
Owned corrected raw retirement/manifest refresh still to finish after compact
record and sustained result. Canonical generated phases are fixtures, preserve.

## Current08:10Z —096 qualified; final source audit complete

LIVE096/manager073911/WAR2e85e0 now QUALIFIED; WEB096 moved to ledger/compact
RESULT. Exact hashes in BUILD_INFO,216Java8/72assets/15served/liveWAR/stock20.
Actual075632 Chromium Native-selected cold4.855/warm2.189 + realhidden/restore
3PASS, SAME producer becomesMSE/0serverrecoveries. Earlier strict Native false-
fallback failures remain unsupported negatives, NOT allow-true failures.
074835has2PASS plus later HTTPtimeout despite warm pictures; unique raw report
kept, no speculative runtime fix or claim later PASS explains it. Request-phase/
bounded-thread diagnostics now available in runner if it repeats. WebKit075833
ordinaryMSE cold/warm functional PASS; background unobservable status retained.

Actual updated phone075221096revision, UK0752335PASS, ordinary07525720s42→524
frames/0.999276x/native+26ms/Pause/Stop/profiles PASS. Initial075335DVD0row was
missing field owner after reload BEFORE Watch, not wireless/decoder failure.
Runner now creates/borrows exact observer and usesasyncHTTPguard, cleanup only
its own. FinalPAL075438151newframes/native2320→7720ms/1.0051x/Stop/profiles/
observer cleanup PASS. Phone075550productionExit/exact3profiles/unloaded.
Firmwarekeeper explicitlyOFF after physical testing:428jiggles/secureBT/
0activeinputs; no keys/unlock/phoneOS/bond changes. Do not silently rearm it.

Actual OWN-01 two-client0800584PASS: CEA50chars and genuineVobSub1612pixels
on distinct canonical sources, Aseek→Bsameproducer/newframes; AStop keepsB.
Both profiles/cleanup; one QSV + one Copy, not adaptive multi-renditions.
Compact WP16-006/OWN-01 records scope; WP16fullservice/stress remain separate.
Six static audio fallback and real5.5h host/phone large offsets/tail recorded;
old source-unavailable blocker removed, no elapsedmulti-hour certification.

After finalverify0recordings/UI/clients/encoders/stock20,41completed rawfiles
6,699,139bytes +3executed helpers8779bytes retired SHAverified to rootdeleteme.
Prior68files13,651,403bytes and WP14scope27files141828bytes also recorded.
Minimum071832codec-pagebuffer/074835HTTP/old132824Off/OSswipe evidence remain.
No original environment restoration pending. Old rootartifacts/temp/web-clean-
source.zip collision still preserved, not overwritten. Remaining cleanup/layout
summary and565currently-tracked-file manifest write/check, metadata3,
task/fix mirrors and whitespace checks all PASS;0completed checkoffs remain in
active project/workspace sections. New/untracked work is preserved, not silently
Git-staged; regenerate manifest at an approved commit after its file selection.
No other running browser/test process. Container repo tracks no source manifest.

Current canonicalWP109/127complete/18open includes5unapproved Core proposals.
Remaining executable recording-creation/growth/futureRecord requires the
asynchronously requested short test-only recording approval (NO ANSWER yet).
Exact PMT/language/full-service/receiver/controller/rollback fixtures and final
publication authority remain separate. Do not fabricate all-done or keep
running unrelated matrices. No175/Windows/Core/release/commit/Git-staging mutation.

## Current07:52Z —096 INSTALLED; native compatibility cold/visibility PASS

Normal manager073911 installed096/epoch1795073780, WAR2e85e08eb8663d2d5f531a002afe38e521449fd5f5473cc5dcf1d943ed735bb7;
ZIP6d4fbc94efdc695a77b8900c35a3f7272addbd5e0009cad0592c11faa490408e,
MD52892d23e5307acb31717fa4b98786da2; LinuxXMLcbf0c88331d940eaa1cc11d11f21a7044ecd1cbad24015d608117819a0110685,
WinXML5b6274b9995d746ab14f2399a459a009c71145f17f1d87a70a90646eba200f49.
15served/liveWAR/package216Java8/72/metadata3 PASS. manager46824tty quit,
native UI independently retired. Unit87 + production mockDOM23perengine PASS.
Clean189inputs/10commands exactWAR PASS,509763byte archiveSHAfa8aec62673e8bad62e7f593cdbf30b1f8f96377f3f92e994ac275e9a94f0d74
retired under rootdeleteme/artifacts/temp/20261119T074234Z-WEB-096-clean-runtime.zip;
DEV extraction removed. Rootcleanup records this move. BUILD_INFO hashes/current
snapshot updated. No runtime change after build; field helpers only.

IMPORTANT: stock-delivery-lifecycle.py originally sets allowFallback=false.
The actual073137 and074655native error4 negatives were STRICT, not evidence
that an allowed handoff failed. Preserve that scope. New --allow-native-fallback
sets true explicitly. Actual074835headedChromium cold now2.402s→14frames,
Native rejected→SAME producerHLS/MSE/0server recoveries. Real hidden/restore
sameproducer/newframes PASS (2rows). Warm also reaches actual50frames/time.408/
ready4, but a subsequent public HTTP observation times out (report not allPASS).
Cleanup empty; independent0recordings/UI/clients now confirmed. Need instrument
which GET/control timed out rather than replaying uncertain input or modifying
runtime speculatively; mcp/watch requests synchronous APIUI despite wait_ms0.
No new field currently running. User-visible cold compatibility corrected,
warm full gate still open. Runtime nativeHlsMse first-picture method is client-
only and excludesDVD/remote/strict/late/network, exact original attachment offset.

Next safe independent work: actual iPhone stopped-page reload via existing
iphone-field-batch.py (one expression then fresh iphone-web096-read.js), then
UK/ordinary --taskWEB096 and one PAL/DVD control. Phone UI is currently NOT
connected, page remains old095 productionExit; latest direct-native longfield
restored/unloaded exactprofiles. FirmwarekeeperON60s. Do not launch hostidle
matrix while phone UI connected; retire exact phone when switching back.
RealDVDhelper now accepts --taskWEB096; ratehelper too. Keep test commands
asyncio.to_thread. Newphone longsource field0729092PASS is in WP11compact.
The one-short-test-recording approval question remains unanswered; NEVER assume
permission or create/stop recordings. No175/Windows/Core/publication change.

## Current07:38Z — WEB096 new actual-native delivery defect; build in progress

Live is STILL095/063133/WAR0ea88e. New096 source NOT installed yet. Actual
Chromium headed native-HLS canonical20905 fails before first picture(error4,
width852/ready1/0frames). Native codec controls had advertised/partly played
HLS, so MIME support is not sufficient. MSE already plays this encoding.
Browser-only one-shot SAME producer MSE attachment now passes fail-before/
87playback tests: explicit first-picture error3/4 only, ordinary HLS, exact
session/path/ready state, allowFallback, no active remote playback. Preserves
Pause/original attachment resume offset/profiles; no server retry/new encoder/
guessed clock. Strict/late/network/DVD/stale/remote/unsupported/async guards
pass. Existing DVD handoffs remain separate. New taskWEB096 active; client-first
boundary satisfied, no dependency/Core change. Playback/SW096.1, epoch1795073780.
Build exec60345 running; recover before packaging/normal-manager update. Other
asset versions unchanged; BUILD_INFO hashes/devsnapshot need update AFTER build.

Updated stock-delivery-lifecycle.py allows bounded12s first-frame native3/4
observation then REQUIRES same producer/MSE/zero server recovery, not false
nativePASS. Run affected real native/mse both engines, updated phone native/
ordinary/DVD controls, build/clean/install/live/stock verification. Do not
replay unrelated completed long-source/audio/GPU matrices or publish/commit.

Prior progress: six original-source audio fallback cases12assertions PASS,
WP12compact owns static-policy scope. Complete573inventory finds original
5.5h1444, ffprobe19800.078s, not a missing fixture. Actual Chromium/WebKit at
3h/5h/back/tail with120s each pass; final Chromium072718 also10%/production
event wiring. WebKit initial codec page preloaded5videos; isolated document
passes, no speculative decoder fix. Chromium fulfilled document couldn't load
scripts, real indexshell resolves without security flags. Actual iPhone072909
nativeHLS5h20s22→624frames and actualtail ended2rows PASS, exact profiles/
source watch state/unload restored. Temporary video removed, no Core Watch.
Compact WP11RESULT needs final phone addition; long-source raw cleanup pending.
User permission for one short test-only recording was requested asynchronously
for futureRecord/growing-to-complete gates; NO response/recording assumed yet.

WEB095/WP03available-source closed, WP14environment exactly restored/defaultoff.
68completed rawfiles13,651,403bytes retired after compact records (rootcleanup
ledger). Two executed cleanup helpers still in rootartifacts/temp for final
retirement. Unique132824Off/OSswipe evidence preserved. Native096failed report
073137 remains unique open evidence until fix verified. Phone original page
is stopped/productionExit, firmwarekeeperON60s; no current media/UI/encoders
after longfields before the native test (which now retired).175/Windows untouched.

## Current07:05Z —095 physical/clean qualification complete; audio follow-up

Installed063133/095 unchanged. Actual iPhone065021 original Breakfast5PASS,
real TT→Off/DVB55,796pixels→Off, profiles/nativeOff/Stop/observer restored.
Ordinary06504620s42→523frames/ratio1.000635/native error−179ms/Pause/Stop/
unload PASS. Corrected async/delayed-activation harness causes are recorded,
not attributed to runtime. Clean187input/9commands exact WAR0ea88e PASS;
archive493567bytes recoverably retired, DEV extraction removed. WEB095 and
WP03 available-source acceptance closed in ledger/compact results. Old132824
unknown and broader WP04/16/language requirements remain explicit.

Read-only recording inventory500of573 shows maximum2.5h; do not claim all573
checked. Current phone070325 productionExit confirms disconnect/paused/no
assigned source/exact3saved profiles. Independent native retirement precedes
new isolated host missing-language default/first/strict gates, no phone input
needed. Firmwarekeeper60s remains enabled for testing; no original environment
restoration outstanding. No175/Windows/Core/publication change. Continue safe
remaining work, not a provider-only stopping point.

## Current06:51Z — phone first-picture requires delayed Safari activation

Corrected async UK064753 now maintains transport/observer cleanup and records
real state: ready4/time1.005/paused/prompt=true/noerror,0frames. Initial prompt
check had occurred BEFORE Safari displayed it; no activation was submitted.
Thus this is a field-harness miss, NOT a runtime decoder/caption failure.
HDMI064928 independently shows Play video. Helper now observes prompt during
initial moving-picture wait and submits at most one real BLE Enter after
explicit button focus, like existing rate gate. Serial corrected UK→ordinary
chain is running; aborts follow-up on failure. Native prior Stop accepted and
observer removed; no unknown Watch/Seek replay. Current095 unchanged.

## Current06:48Z — installed095 host PASS; asynchronous phone harness corrected

Live095/063133 hashes remain exact. Actual WebKit063947 signed/fullscreen/
natural clears25PASS and Chromium064150software MPEGTS focused6PASS, noerrors/
cleanup. Phone064352 shows actual095controller asset after approved reload.
First064404UK attempt verifies095 then wireless timeout before any row; its
Stop is accepted but observer cleanup unknown. Following ordinary run refuses
another-inspector ownership before input. Do NOT count either as a playback
failure/PASS or replay. Fresh read064627 regains exact page/native unloaded.

Cause found in NEW TEST tooling: synchronous MCP/HTTP control inside asyncio
observer can block paired inspector pump during slow Seek. All UK controls/
guards now await asyncio.to_thread; one AST regression enforces this. Explicit
stopped-source observer retirement is added (exact preserved profiles, no
Watch/Seek). New serial chain retirement→UK→ordinary aborts on failed step;
recover running exec before another inspector. No runtime or firmware edit.
After success finish095 compact/ledger, cleanup/mirrors/manifest and remaining
safe acceptance work; current user still requests continuous execution.

## Current2026-11-19 06:42Z —095 INSTALLED; affected qualification in progress

Normal manager063133 installed095, epoch1795069500; main092.1/playback093.1/
CEA094.1 unchanged, broadcast-controller/SW095.1. WAR0ea88ec552fcf02868e2c6a886dc153763c23109d81cb071210b6193ab04774a,
ZIPc19bb897ea6500c1e503c5a72899dd8ade9b4439ce6f111d7ae23e952b5b4f29,
MD5041bcb3bd98bfec77f8852bf72e3ebbb, LinuxXML2f9a38153f6fc98a7870593ae8c62f0673248f2484a3f79e6f2039654ce18483,
WinXMLb4eacded9098444c557533a4bc568d622bfb188b4d2853fd6c4d09279fe5bcad.
216Java8/72assets/package/15served including changed caption controller/
liveWAR/stock20 PASS. Metadata updated; NOT published/committed.

Actual stock plugin manager navigated via SageMC MyMenu→Settings→Manage
Plugins→Installed. Update success observed, only own UI interrupted by WAR
reload. Reconnect/Back/Home restores original SageMC; test UI quit. Initial
063908gate refused while asynchronous manager native retirement remained;
this is NOT a caption failure. Independent wait then063947 WebKit/QSV/HLS/
original Breakfast signed+1000/fullscreen/natural-clear25rows PASS. Current
Chromium/software/MPEGTS focused7rows then phone approved reload chain in
flight. Recover that exec result; after phone reload read actual095asset and
run iphone-uk-caption-life.py plus iphone-rate-field.py --browser-local
--smoke-only --task WEB-095. Do not replay old unsafe native-rate control.

Additional tests:16service-loss incl stale-generation guards, actual generated
CRC PMT decoder4, TT28/DVB32Java, TT5/DVB3/STV10Node, CEA23, both browser TT7/
DVB6 all PASS. Newtestsource fully labels mock DOM vs original-source physical.
After affected phone field, compact095 record/ledger and scoped remaining
acceptance; continue runnable tasks, no checkpoint-only final. Cleanup still
pending for this turn, compact WP14/codec/Off/lifecycle records ready. Keep
original unknown132824 and OS swipe minimum. Phone currently exited old094;
firmware keep-awake ON60s. No original environment restoration outstanding.

## Current2026-11-19 06:27Z — WEB095 client-only PMT retirement correction

Current installed runtime is STILL094/manager040356/WARa9de87. New095 source
is not yet installed: production controller fails explicit service removal
selectedTrack=-1/services=[] retaining old text/future cues. Java generated
valid-CRC PMT removal confirms BOTH actual source decoders emit that existing
state (4PASS); no server protocol gap. Browser-only handler clears own renderer/
queue for explicit numeric retired/off state, preserves legacy missing/unknown
metadata and current positive selection.14regressions pass after failing-before,
Teletext5/DVB3/STV10 retained. Historical132824cause remains unproven.

095 caption asset/cache stamp and epoch1795069500 are set; .\dev.cmd build is
running. Need add stale-generation/deferred-response and payload-free actual
DOM cases, run affected browsers, package/metadata, retire phone test via
production Exit, independent0activity then normal manager stage/install.
Use commission-browser.py interactive exact stock plugin manager, not direct
WAR copy or MCP test-control rewrite. Restore SageMC after manager. Then actual
original UK affected host/phone/CEA gates and compact evidence/ledger. Do NOT
stop at this new provider checkpoint or claim installed095 yet.

Other this-turn progress: WP14-006 and container DIAG-ENV-001 fully closed;
exact environment restored/default-off/browserZIP/stock20 pass. Actual17 ZIPs
reviewed34sensitive named fields, no unredacted values. Codec D/E native Safari/
Chromium comparison ledger complete. Chromium06054632caption rows/5cycles and
WebKit06131014rows/3cycles pass; original132824 remains unique open evidence.
Actual iPhone0619535rows original Breakfast TT/Off/DVB8004pixels/Off/newframes,
exact profiles/nativeOff/Stop/observer cleanup PASS. Phone has connected idle
UI123c, no source; __deliveryField observer still installed and needs cleanup.
Its real visibility records hidden at50.514s, visible211.631s later after USER
reopened Vibe, expired source correctly retired/unloaded; not seamless resume.
BLE pointer move-to061600 works inside current page. OS swipes060010/060050
did not open Search despite receipts; no pointer success inferred. User confirms
AssistiveTouch ON and reopened; no firmware change. Keep minimum open OS evidence.
Firmware keep-awake remains ON60s; disable only after actual physical session.

Before final completion still retire reviewed completed raw artifacts to root
deleteme with SHA/containment/reparse/collision guards and cleanup report;
WP14compact RESULT and CODEC_FIELD/OFF_STRESS preserve results. No cleanup
executed for this turn yet. Private original environment stays server-side.
Root task order must prioritize095 and only affected matrices after stable;
publication still requires final explicit approval, no commit/push/release.

## Current2026-11-19 — home-Wi-Fi continuation and approved diagnostics gate

UPDATE0600Z: WP14-006 COMPLETE;19real rows/12failed writes/newest10/hash-exact
retry/advancing playback PASS. Restored055822 exact original environment and
stock20; defaults-off/write-test-refused/retry-disabled/browserZIP PASS.
There is NO pending temporary configuration restoration. Compact owning
WP14-006RESULT and container DIAG-ENV-001 ledger current. Codec D/E ledger
closed with scoped capability comparison. WP mirror108/127,19open incl5optional.

Focused WebKit Off-cycle follow-up hangs in an unproven browser RPC before
any PASS; native UI independently retires. Exact owned6process tree stopped
after idle proof; active/WP03-008/20261119T060012Z-webkit-inspection-hang.md
records no caption-crash claim. Evaluation/shutdown now12s-bounded; Chromium
counterpart in flight. Continue other runnable phone/lifecycle work afterward.

User requests remaining executable work and explicitly approves test-only
VibeWebDiagnosticTest on232, including unavailability/spool/retry. Guarded
same-image recreation054813 passes exact environment/20stock files. Temporary
JAVAOPTS enables that destination; MUST run commission-diagnostic-destination.py
restore after tests and independently verify disabled/default state. Original
private environment remains server-side .vibe-commissioning/WP14-006; never
export it. No Core/plugin byte changes or publication. Phone remains exited;
firmware keep-awake ON60s during testing, no host keeper.

Actual iPhone053952 and Chromium054239 native codec A–E comparison completes:
MPEG-2 copy has no decoded picture (Safari error3; Chromium width0), all three
H264 controls advance. Profiles restored/test iframe removed. This is codec
boundary evidence, not MPEG-2 browser support. Original UK WebKit053718 signed
seek/clear25rows pass; does not prove the old intermittent132824 fixed.

First destination test055136 write/read/hash/delete passes; export harness
BadZipFile was NOT a broken server archive. Exact saved7213byte ZIP is valid,
SHA96697c94bb4ceb68, preserved locally; only that verified owned server file/
empty test directory removed. Harness now observes actual fetch ArrayBuffer
instead of CDP attachment-body decoding. Focused rerun in flight; inspect its
report before another action. Continue bounded spool/restore, then other
runnable physical/host rows. No checkpoint-only final.

## Historical Final2026-11-19 — available local and remote scope finished

Runtime remains040356/094/WARa9de87. Remote037 is ledger-closed to observed
cellular/VPN HDMI/BLE scope; partial WP16 delivery now has both-engine cold/
warm MSE and real Chromium background. No further runtime fix was indicated.
Independent final package216Java8/72assets,14served/liveWAR/20stock match;
mirror13/metadata3/P01tools23/completion4 and269-input inventory checks PASS.
Final explicit fixture Stop is unloaded, CCOff, original SageMC; phone still
connected1UI,0recordings/other clients/encoders. Firmware keep-awake explicitly
disabled and verified,282jiggles,0input owners; Bluetooth bond/settings remain.

Reviewed29files/7,175,535bytes plus executed helper/3pyc42,342bytes retired
recoverably with verified hashes. Seven final/unique WP16reports and distinctive
post-EOS051911 image remain active. Current source manifest finalization follows
this entry; no staging/commit/push/publication. Root artifacts/temp/
web-clean-source.zip remains because its deleteme path already holds the older
baseline; do not overwrite either or make a duplicate staging workaround.

All remaining canonical unchecked scope is documented in current dated
acceptance: source/PMT/full-service fixtures, physical peer/gamepad/receiver/
finger/native-background rows, representative multi-hour run, opted-in writable
destination, original rollback WAR, unimplemented native/Core-only contracts
and final publication approval. Codec native D/E phone comparison remains
separate; streams generated, field not run. Do not label those as done or
repeat unrelated complete matrices. Windows stays deferred,175 untouched.

## Current2026-11-19 05:21Z — remote-LAST scoped pass, final source/cleanup

Same installed040356/WARa9de87/094; no new runtime after prior qualification.
WP16-002 actual cold/warm HLS+TS MSE both engines passes; Chromium public CDP
no_defaults real window hide/restore passes. WebKit forced-visible background
stays untested; Linux build reports neither native-HLS MIME. Earlier native
startup/inspection timeouts retained, not incorrectly called Safari failures.
Optional Openbox/xdotool installed ONLY reusable DEV container; workflow records
exact setup and focus-emulation boundary. No production image/Core changes.

User explicitly cellular/VPN ready LAST. Real HDMI481frames plus six real BLE
Down/Up keys show0→1→2→3→2→1→0; no missing/late queued highlight. Actual preview
PTS28.896, fullscreen after30sseek31.164, Pause holds52903ms over13.547s,
60sseek/Play→visible76.276 and rolling captions. Natural SageMC Stopped dialog
observed; native fullyLoaded/time-after-EOS is NOT unload/clock accuracy proof.
Explicit final Stop independently unloads; CCOff, stock20/WARmatch/noencoders.
Phone remains connected;1UI is truthful, not zero. CompactWEB037 remote report
and WP16-002RESULT replace reviewed raw data. WEB037 moved to ledger, no broad
parity completion claim. Wi-Fi inspector is unavailable on cellular route.

Still no commit/push/publication. Finish source manifest/mirror checks and owned
artifact retirement, then report exact external fixture/equipment/approval
boundaries; do not repeat unrelated complete matrices. Codec D/E fixtures were
generated through plugin-owned API but physical native D/E was NOT run after
phone switched to VPN. No hidden test PASS. Firmware keep-awake is still ON60s
as of0512; disable when the physical test session ends unless user says leave on.

## Current2026-11-19 04:28Z —094 qualified, remaining boundary reconciliation

Manager040356/epoch1795061100/CEA-SW094.1 now installed; main092.1 and
playback093.1 unchanged. WARa9de87c7ab2d/ZIPad6cf9c917b8,216Java8/72assets/
package/live/14served/stock20 match. Empty-service stale CEA regression fails
before, service23/controllerDOM8each/actualChrome+WebKit7rows each pass.
Actual phone041528loads094.1;041703ordinary20s46→527frames/0.99877x/native
clock+8.46ms/Pause/Stop/profiles PASS. Production Exit042630acknowledges closed
server/paused/no source/exact profiles; final independent idle check pending.

WP16unit/isolation and available-Linux hardware scope close; canonical107/127,
20open incl5optional. Current dated acceptance2026-11-19 lists exact remaining
fixture/equipment/native-protocol/publication boundaries. No blanket all-done.
248ledger entries preserved with scoped current resolution; mirrors13guards,
metadata3exact-current PASS. Android269reference has zero drift, read-only.
Git-less188-input Java25 build matches live; Java11 compiler bytes differ
but its own package/metadata+Disc/cache/lease tests pass. Avoid CI fixed-hash
assumption; --exact-artifacts verifies commissioned bytes, default its own ZIP.
No new runtime changes after094. No Core/engine/175/185 mutation/publication.

Retired106paths/985files/17,975,968bytes with all hashes verified; system temp
OZZKBF699files and aNvsNf706files also recoverably retired under rootdeleteme
before exact source removal. Preserve unknown030640/other open failures and
canonical fixtures/settings/keys. Root web-clean-source.zip remains because
matching deleteme path already contains the earlier baseline; do not overwrite
it or make a new staging copy. Root cleanup ledger records this one collision.
VPN/remote LAST request is now sent asynchronously; continue local docs/manifest
and final idle verification meanwhile, no checkpoint-only completion claim.

## Current2026-11-19 03:55Z —093 physical recovery and clean build PASS

Installed033113/main092.1/playback-SW093.1 remains current, WARca33134a3f42.
Actual phone033423 four rows exercise the reproduced native short-feature
stall: same-producer MSE recovery/new57+frames/zero producer recoveries/new
root/Stop/profiles/remote-playback restoration PASS. Ordinary033747 Watch/
seek/20s47→526frames/0.9986x/nativeclock-59.6ms/Pause/Stop PASS. User confirms
ordinary playback works; initial picture-black report is not a decoder crash.
Phone test Exit completed; independent stock check0UI/clients/recordings and
encoders/20protected hashes unchanged. No active native test to replay.

WP17-003 now passes final186-input Git-less clean build, exact installed/
packagedWARca3313 match and Disc8/cache10/lease10/playback82/profile9/
Chrome23/WebKit23/PWA8, with unedited final transcript. Minimal input archive
is not a full published source handoff. Compact results retain exact hashes.
New ledger reconciler preserves248pinned reasons/statuses while adding scoped
canonical target resolutions; six guard tests pass, no inferred physical PASS.
Continue remaining executable local acceptance/evidence reconciliation before
VPN/remote LAST. Windows175/185 unchanged. No commit/publication.

## Current2026-11-19 03:33Z —093 installed, actual recovery gate next

Normal-manager033113 installed, epoch1795059000/main092.1/playback-SW093.1.
WARca33134a3f423a92b84e516934d46115eb91838a14d499ced0d77ce6d3daa7c4,
ZIP8df52fd0a090cf135f5e7cb6ae8d1db5a9ceefb1f4c0ab0d3a0cde911f359c8b.
216Java8/72assets/package/liveWAR/14served/20stock match, no encoders or
recordings. Manager reconnect/Home/quit running; finish exact native retirement
before phone reload/owner and iphone-one-picture-dvd-gate.py --task WEB-093.
82unit guards/Chrome23/WebKit23/PWA8 pass; extra remote-route guards prevent
either MSE fallback disabling an active/connecting/unknown cast route. Public
WebKit/W3C interfaces checked, no firmware/native cast test claim. No Core
changes, Windows/175 untouched, no publication. Preserve physical before
reports031439(092task) and032316(093task) until corrected field evidence.
Continue all runnable local work; VPN/remote LAST; final cleanbuild/matrix only
after093 runtime stable. Earlier ec6e clean snapshot is NOT final093 proof.

## Current2026-11-19 03:29Z —093 real Safari feature stall, client fix built next

091/WP10-004 closed after actual stockWebKit030512/Chromium031017 five rows
each: authored nonfirst83871 title2/native11978ms/probe11.995s/three chapters/
root/retirement.092 closed installed idle105.39s/five receipts and lost-beacon
auto native/UI retirement70.19s. Both have compact results/ledger. Current live
WARec6e/manager025903. Phone confirmed main092.1 after an idle reload.

NEW093 physical failure:031439 passes menu/10s/realBLE/new22featureframes,
then native HLS stops at1.360/1.418/emptybuffer/noerror. Fresh separate032316
trial after production Exit/reload reproduces1.873/1.919, native4804/title5005,
server clean ended4.963s/TEN segments/ENDLIST/exit0/converterEndedtrue. Captured
exact generated-source manifest:ten~0.5005s segments. Thus server has bytes;
native browser is not loading them. Root cause inside Safari is not claimed.
Preserve both raw failures. First later read after two minutes finds expired
HLS spool; not proof it was missing at initial stall. No decoder crash claimed.

Client-only recovery source now added: exact finite completed DVD feature/
generation/producer/emptybuffer/partial-duration/12s-no-progress condition,
permitted fallback only, one HLS/MSE attach to SAME producer/playlist at last
actual position; no seek/reencode/EOS fake. Retains old actual clock during cold
attach; stop/newsource restores remote playback.82unit cases pass (34negative,
late pause/source/stop/policy/menu/progress/buffer, unsupported/attacherror and
clock/remote restore); failing-before0vs1 MSE proof retained in task context.
Both streamingDOM23 pass earlier092,093 rerun finishing. Build epoch1795059000,
playback/SW093.1/main092.1 running. Not installed/physically qualified yet.
Current exact phone failed fixture78957 stopped via production Exit in flight;
verify native idle then normal-manager install, reload/owner and093 physical
one-picture gate. No command replay/Core changes. Physical helper now records
fresh server status and bounded failure manifest, and accepts --task WEB-093.

WP17 clean archive partial (NOT final):185 all runtime build inputs+selected
tests, Gitless WAR matches ec6e. First missing test-core dependency repaired
within same hash-guarded owned staging/archive EBE49A305570955D0FA132ADAA7B4DF58A1FE7A0A204E1B5178EC29EE145C0EE;
Disc8/cache10/lease10/playback77/profile9/Chrome23 pass. Oneoff image lacks
WebKit cache; don't redownload. Reuse dev-container browser runtime for final
clean extraction after093 stable. New093 source invalidates final cleanbuild;
defer final matrices until code stable. Root temp web-clean-source/extracted/
zip are owned staging, not active projects; preserve on failure, retire after.
Continue local work, VPN/remote LAST; no publication/commit.

## Current2026-11-19 03:02Z —091/092 installed, finish exact affected checks

Normal-manager025903 now installed WAR ec6eb930c1503f06fec693773c700cc79df41094101748f0a4d23527810e6274,
ZIP81aa5c5f0578d1ac65fac6fdd1de35822b961e0a40736ebae05797a9b317ad86,
epoch1795057200/main-SW092.1/playback090.1.216Java8/72assets/package/liveWAR/
14served/20stock proof passes. No restart/Core/native/INI/engine change.
Manager was driven in an explicitly source-routed isolated browser because
the OLD installed desktop client expired at90s with no video. Real manager
update is observed successful; reconnect/Home restores SageMC, owned UI retired.
WEB092 is client-only received-byte receipt through existing state, opaque
nonmatching producer/time-1, <=one15s/in-flight, no timer/diagnostic heartbeat.
Fail-before DOM then bothChrome/WebKit23PASS. Source-routed actual idle105.41s/
6receipts survives, but first lost-beacon oracle checked before async close;
corrected TEST to waitclose. Installed actual105s+lost-beacon gate running.

WEB091 actual nonfirst83871 root→authoredtitle2/chapter1/11978ms/new17frames/
newroot passes, but disc metadata cannot locate ffprobe. Resolver regression
fails expected plugin runtime/actualPATH; now reuse existing MediaProbe
resolver, preserves override. Disc8/cache10/lease10/fixture7 guards pass.
Need actual corrected explicit title2 duration/three chapters and native DVD
after installed WAR before closing091/WP10-004. Canonical local fixture and
remote WP10-NonFirst are hash-verified1116160bytes/sixfiles. Initial one public
scan timed out; --observe-only independently resolves83871, no upload/scan
replay. Do not overwrite canonical fixture or use title1/largestVOB guesses.

WEB090/WP12-006 and WP12-005 now ledger-complete; compact results include
actual phone local-rate/clock/Pause, affected DVD and real3production-plan
quality output/hash proof.64closed raw files/32801722bytes moved recoverably
to root deleteme, same relative paths, hash/containment/no-reparse verified;
root CLEANUP_REPORT current. Preserve open091/092/WP10/HID/caption failures.
Broader local acceptance next; VPN/remote LAST. No publication/commit.

## Current2026-11-19 02:27Z — browser-local rate passes phone; finish affected DVD

WEB090 is installed via normal manager022105/main-playback-SW090.1,
epoch1795054700, WAR66ae99d6333ea8caac281ac0146ac23d9c55b40b125c3bb76a843606103e06bc,
ZIPc4c976f8751da77dda98523b43c2e178420c4f21dddb358f9371c124ed53d73f.
216Java8classes/72assets/package/liveWAR/14served/20stock proof passes.
Manager reconnect/Home restores SageMC, no restart. WebKit/Chrome22DOM cases,
77playback/9profile,4Settings and56mobile/8PWA checks pass. New speed is
explicit per-recording in Video, no native rate/seek/transcode command, no
persisted default; Stop/newrecord/DVD resets, same-source seek preserves.

Actual phone022446 five rows pass0.5/1.5/2/1/Pause/reset/profiles/decoder
teardown.022558 adds file-clock proof: exact new10s consumer; native-vs-
presented errors -49.5/-172.7/-99.3/-25.6ms, all same HLS source/newframes,
native STV rate remains1 as explicitly designed. Observed3s progress ratios
0.356/1.329/1.879/0.771, not a precision/acoustic guarantee. Original public
stock SetPlaybackRate0.5 boundary remains unavailable/seek fallback; do not
claim Core fixed. Preserve original021216failure until090scope is closed.
Phone source stopped; retire exact phone UI then actual affected baseDVD
gate before closure. Broader local tasks follow; VPN/remote LAST.

## Current2026-11-19 02:15Z — rate boundary found; WEB090 next

P13-003 scoped stock-Linux acceptance is complete: actual WebKit TT/DVB7+7,
DVDPush5+5, diagnostic OFF/ON/OFF3 (unknown0/timeouts0/queue0), generated
samehandle updates/unload/HD300 fallback+OFFrestore in Chrome/WebKit12each,
Java10; stock20/noencoder/idle verified. Ledger/compact WP13-003RESULT current.
P12 signed delay002/rapidconfig003 already completed; policy now8+quality10,
playback77 and both streaming DOM17 pass extra quality/rate guards.

Actual phone021216rate gate fails before firstrow: public SetPlaybackRate0.5
causes newsource/seek, browser stays1x; failure cleanupStop accepted. Local
modified-Core source explains a Vibe-only Pull-rate branch; official stock
does not forward rate in ordinary Pull. DO NOT patch Core or call unit support
a physical pass. New WEB090 implements explicit client-only per-recording
Video speed0.5/1/1.5/2; stock STV FF/RW stays unchanged. Need source lifecycle/
Pause/reset/effective/bothengine/manager/phone tests. Phone exact123c stopped,
visible852x393/PWA; no saved settings changed. Preserve unique021216failure
until correction/qualification. No new runtime installed after013709 yet.
Continue other local scope afterward; VPN/remote LAST, no publication.

## Current2026-11-19 01:46Z — playback confirmed; WEB089 qualified

User clarifies they needed to use the phone, confirms playback working and
asks to continue. No spontaneous black-video defect was reproduced; do not
claim a video-code fix. Prior test Stop/independent unloaded preview and new
80s plus125s/noStop/actualHDMI fullscreen observation are compact WEB089RESULT.
Normal manager013709 WAR3b6f3fe7dc6a/ZIP54f67913655d now loaded; live hash,
14served assets/20stock files match, manager Home restores SageMC, no restart.
Actual014106 four-row Autoeng4→NAR1→Autoeng4/new paused consumers/exact saved
and native profiles pass. WEB089 moves ledger; broader WP12-001 PMT/layout
scope stays open. WP12-003 actual rapid6inputs→one700/+250Apply→one1000/0
restore is recorded in its compact PROGRESS; finish scoped local acceptance
before final affected matrices. Current original11224 left playing fullscreen.
No publication; VPN/remote LAST. Do not stop independent executable work.

## Current2026-11-19 01:35Z — investigate user black preview; NAR fix built

User reports picture then black. The preceding012659Z audio policy gate
explicitly stopped the exact phone source after finding Auto=NAR1 rather
than primary eng4. Independent013218Z native state is unloaded; HDMI012839
shows SageMC with an empty preview, not a proven live decoder crash.
Fresh sustained original Breakfast gate013315Z runs80s without Stop: eight
samples, new frames114→1586/time4.75→66.28, ready4/noerror; HDMI013354 shows
real moving news picture. Final native loaded remains true. Do not generalize
this to every user black-screen occurrence or label an unproven runtime fix.

WEB089 recognizes exact NAR tag; failing-before expected4/actual1 proven,
corrected7policy cases pass. New build epoch1795052068 WAR3b6f3fe7dc6a /
ZIP54f67913655d;72assets/216Java8 classes/package match. Not yet installed;
next normal manager and actual Auto/NAR/Auto restoration with unchanged
profiles/Core. PreviousWP12 rapid6inputs→oneApply700/+250→oneRestore1000/0
passes on actual phone012423Z. Keep receiver/PMT/service/WAN scope separate;
VPN/remote LAST. No release or stock server modification.

## Current2026-11-19 01:10Z — phone lifetime complete; continue local work

User resumes all executable work with phone connected; VPN/remote testing LAST.
Fresh page2/standalone852x393/realBLEDown-Up reaches native5/4. Actual010723Z
one-picture gate passes four rows including105s no-audio menu, realBLEEnter/
18new feature frames/new root/full decoder teardown/exact profile restoration.
20stock hashes/noencoders/0recordings verify. WEB088/WP08-008 and qualified
WEB085 scope move to checklist ledger; compact088RESULT preserves prior
stale404/old missing-HID unknowns. No runtime change/restart/publication.
Firmware keep-awake explicitly ON60s after reconnect; no host keeper.
Continue local caption/service/audio/quality/remaining content acceptance,
then affected final matrix. No physical WAN/acoustic/controller claim.

## Current2026-11-18 16:20Z — current host gates settled; phone page required

Run20478 finishes actual161554Z25rows PASS for original Off-after-seek signed
delay path, unchanged profiles/cleanup empty. This does NOT prove old132824
intermittent fixed; old report lacks new Off/owner/pixel fields. Keep original
minimum evidence; no speculative caption source change. Independent final
stock2320recordings/UI/clients/encoders and20protected hashes verify.

Six selected final machine reports move without duplication into owning
results/WEB088 and WP03-008;5obsolete raw/corrected-oracle captures648372bytes
retire recoverably. Summary formatting failed after completed/hash-verified
moves; do not replay the helper. Read-only audit proves6PASS reports33886bytes
and5retired sources absent. Compact WEB088PROGRESS/BRIDGE029RESULT are current.
No active test process remains. WEB088/WP08-008 still need actual iPhone
new-lifetime105s acceptance; phone at Home, exact-page absent, user reopen
request pending. Firmware is ON60s/count100/zero host input sessions; no PC
renewals, keys, code entry or automatic rearm. Do not claim all tasks complete,
publish, repeat unrelated matrices or count host WebKit as physical Safari.

## Current2026-11-18 16:16Z — lost-beacon expiry qualified; caption follow-up

Actual lost-Stop WebKit161107/Chrome161316 each1row PASS, exactly1dropped
owned beacon, actual native expiry37.010/35.868s; live encoder/2spools before,
noencoder/UI/same spool paths absent after. Combined normal5cycles, valid-owner
105s still/new feature/new root and local policy9/servlet19/wire/contracts4
qualify available host scope. Physical phone current page unavailable/user
reopening request pending. Bridge029 firmware ON60/count98/zero host grants,
no PC keeper; real earlier link-drop disarm remains documented. Readiness/
completed manager captures56files27,861,687bytes retired recoverably to root
deleteme; minimum unavailable-page and unknown/fault JSON remain.

Next safe unblocked original Off-clear investigation: exact WebKit/QSV/HLS/
Breakfast +1000ms/fullscreen/natural-clear run20478 is underway on153734.
Old132824failure has no Off/owner/pixel projection, so cannot prove cause.
Current runner records those fields on failure without caption text; no blind
CC/Seek/Play retry or broad unrelated matrix. Do not mark intermittent fixed
merely from another PASS. No new source change/stock Core/release/175/Windows.

## Current2026-11-18 16:09Z — five strong cleanup cycles/105s hold pass

Installed153734 actual WebKit155057 Exit/reload/page-close3rows and Chrome
155427 reload/page-close2rows PASS: live encoder and exact2spools before,
native retirement/noencoder/same paths absent after. One readonly ui.list
timeout retried; no ordered replay. Actual WebKit160455105s no-audio still/
feature/new root/retirement4rows PASS. Deliberately lost owned pagehide-Stop
fault is now95836/WebKit, then targeted Chrome, to ensure normal beacons cannot
hide an unfixed expiry branch. Compact WEB088PROGRESS owns scope/unknowns.

Phone BLE reconnected once (2connections/1drop/ESP_OK), disarming firmware029
as designed; explicitly enabled1557/60s, no host keeper. Phone awake outside
Web Client; real Home/pointer observed, click/swipe did not launch app. Exact
page unavailable; user reopening request pending, no code/input replay. New
phone105s row still needed, independent host work continues. BRIDGE029 and
WEB087 remain completed in their own scope, not a new physical088 PASS.

## Current2026-11-18 15:50Z — WEB088 installed; strong lifecycle in progress

Normal manager153734 installed1544Z, deployed WAR395035c985a9 matches package;
new browser-reaper JVM thread is observed,14served assets and20protected stock
files pass. Reconnected manager/Home verifies SageMC_Vibe.xml then retired.
No server restart or other-client/recording interruption. Initial154619Z
lifecycle helper incorrectly demanded an initial root even when stock resumes
the disc: it timed out on moving feature. This is an invalid test assumption,
not a newly proven menu defect; do not clear user watched data or send Select
against an already resumed feature. Corrected runner accepts either genuine
root or resumed title, requires real frames/live encoder and exact spool paths
present before disconnect. Run28976: first strong Exit cycle PASS (2spools
present→absent, live→noencoder, UI and clock retired); other two pending. Prior
152501Z unique URI/abandonment proof remains active until correction qualified.
Firmware idle60s remains ON with0host input grants/renewals; phone deliberately
exited/awake. After both engines' cycles, actual phone foreground/one-picture/
Stop affected rows and final restoration/stock verification follow.

## Current2026-11-18 15:40Z — WEB088 compiled/packaged; normal manager active

WEB088 Java8 compile216classes/72assets/package PASS; WAR395035c985a9,
ZIPb94ec34e173e, manager catalog3.3.0.20261118.153734 staged. Actual policy9,
protocol+DVD wire, streaming-servlet19, source4 and mocked Exit4viewports each
Chrome/WebKit PASS. Portrait Exit runner's old overlay-Hide assertion was
incompatible with the existing permanent portrait Controls tab: now require
visible dock, all drawers/tools hidden and stage focus. No UI runtime change.
Initial added servlet fixture forgot to retire its tiny playlist; corrected
finally cleanup and all19pass, not a product defect. Selected code keeps actual
continuous and HLS delivery alive, no status renewal. Manager43418 currently
borrowing stock Setup from original SageMC; finish install, restore Home/STV
readback/retire and run strengthened WP08-008 cycles with encoder+exact spools
present before disconnect, then physical phone. Current installed server is
still145838 until manager confirms the153734 update. No checkpoint final.

## Current2026-11-18 15:32Z — WEB087 complete; abandoned native UI reproduced

Phone151514Z, hostWebKit151750/Chrome152044 and packaging pass scoped087;
WEB087/WP08-006 are moved to ledger and parity index reconciled. Firmware029
continues without host renewals. New WP08-008 host lifecycle152501Z passes two
cycles (Exit/reload) but third page-close observation is URLError/UNKNOWN.
Independent1528Z proves owned20819 UI/media+GFX reader threads remain alive;
encoder already stops through existing HLS reaper, not an indefinite encoder
leak. Exact approved da92a86446be replacement/Stop restores0UI without restart.
Unique unknown remains active. WEB088 now owns a bounded plugin-only browser
transport lease:30s disconnected grace/90s half-open, actual state/long-poll/
encoded-media reads, never diagnostic status. No safe closed-browser-only
solution can guarantee a lost pagehide beacon; existing stream endpoint ignores
transport loss. Source candidate pending compile/regression/install/physical
acceptance. Do not call WEB088 or P08 teardown finished. Stock20 unchanged,
no175/Windows/publication work. Current phone deliberately exited but awake.

## Current2026-11-18 15:18Z — firmware independent; native still corrected

BRIDGE029 is ledger-complete: application04e1c87c, firmware-owned idle60s,
zero host leases/renewals, six-minute phone no-lock observation PASS. Left
enabled during authorized testing; reboot/disconnect disables, no auto-rearm.
Android debug GATE001 is complete at502; exact Non-Pro classic Fixed affected
FF/REW/pause/restoration passes without changing production playback.

Web087.1 normal-manager3.3.0.20261118.145838 installed1504Z; WAR1e4b031aee2c,
ZIPa5cb3c257d48,14served assets match and20protected stock hashes pass.
Manager hot redeploy retired its connection; explicit reconnect/Home readback
confirms original SageMC_Vibe.xml, then owned host UI retired. Actual phone
151146Z and enhanced151514Z each pass4one-picture rows: new menu frame held
10s, real BLE Select/new5sfeature, NEW natural root picture. Selected Native
stays unchanged; tiny menus use bounded HLS/MSE, feature returns Native HLS.
Stop proves decoder stopped/id empty/no assigned src/ready0/paused and restores
remote-playback false. Profiles unchanged, no server seek/recovery/new encoder
or fake frame/duration. Phone explicit Exit acknowledged1516Z; independent
1517Z no recordings/UI/clients/encoders. New host WebKit/Chrome affected rows
follow serially before scoped WEB087 closure and further teardown work.
No public release, Core/175installation or Windows physical change.

## Current2026-11-18 14:28Z — firmware idle fixed; native still remains open

Phone reconnected/visible landscape; old test observer API was404, so verified
idle paused state before one reload and fresh owner. Actual142210Z one-picture
gate on131905 has no error4 but only metadata-ready1/width853/ended1us and
zero decoded frames.0BLESelects; do not call Safari corrected. Exact owned78957
Stop then explicit phone Exit preserve profiles; stock232 independently0UI/
recordings/clients before Android follow-up. Keep unique still JSON/HDMI.
Bridge029 adds firmware-owned motion independent of PC renewal, app04e1c87c
installed application-only/bonds and saved key/code retained. Real Chrome+
WebKit shared firmware switch/close-all zero-host-lease4rows each PASS; final
six-minute read-only no-renewal phone idle observation running. Old keeper
planned update interruption is not an unexplained new runtime failure.
Android debug GATE001 candidate9364be19 installed Success/settings-preserved,
byte witness in physical harness; exact Non-Pro/Fixed/Direct-off affected run
21506 underway, FF/REW report recovered video78/68frames so far. Await full
result/restoration, then close only proved scoped tasks and continue Web work.

## CURRENT2026-11-18 13:58Z — installed correction; host still PASS; phone StandBy

Web131905 installed through normal manager, deployed WAR10d1cff840c7 matches;
14served assets/20stock and FFmpeg0.1.25/MIM0.4.13/INI/engines verify. Actual
one-picture WebKit134038Z and Chrome134213Z each4rows PASS including10s no-audio
hold, new moving feature and NEW decoded natural root (width720/ready2/current
frame at0s). Corrected shared7guard observer rejects old/undecoded/stale frames;
old133808root oracle was INVALID.58closed manager/host/corrected-EOF captures
retired recoverably/hash-verified, compact WP08-006/PROGRESS records outcomes.

Actual phone native-HLS row remains pending after keeper timeout/StandBy;
two Escapes/gesture/Space never reveal entry,0codes sent. User unlock request
pending; host work continues.132824Z original-caption Off-clear failure stays
unproven: subsequent focused7 and full133412Z25rows pass, no invented fix.
MIM classic Fixed Non-Pro gate yields real VAAPI/AV, but debug post-seek counter
-1 causes a proven false30s health failure. Owning AndroidGATE-001501 debug-only
baseline correction passes6compiled/43automation guards; build89744 underway.
No production player change or release. Once installed, rerun exact FF/REW/
pause, restore136prefs/power, verify hashes/activity, then remaining unblocked
Web tasks. Windows/WAN/controller/receiver dependencies stay separate.

## Historical2026-11-18 13:24Z — one-picture dependency and serving correction

Normal manager FFmpeg0.1.25/MIM0.4.13 installed, one guarded232 restart130931Z
after independent0recording/UI/client proof. Actual installed wrapper/JAR match
packages;20stock/INI/engines unchanged. Six EOF count/hash, control/media/init/
package gates pass. Phone131215Z now has one HLS segment/highlight2104pixels,
but Safari media error4 before segment requests; exact served target0 with
EXTINF0.041711. New serving-only target0→1 normalization leaves EXTINF/media/
EOS unchanged. Four guards, compile215Java8/72assets/package and both renderer
11DVD-DOM tests PASS. Webcandidate131905 staged WAR10d1cff840c7/ZIPac4336d9f185,
normal manager37647 active; not yet installed/physical PASS. Prior113129
packages retired recoverably; rootcleanup report records hashes. Continue
still/affected nativeEOF/Fixed/caption/teardown, not checkpoint final.

Bridge bounded keeper22511 completed224samples/no failure130328Z; explicit
8077/1800s keeper starts1304Z/idle60, not auto-rearm/unlock. Phone visible
landscape, GuidedAccessOFF, real BLE retry reconnect passes131057Z. Firmware,
bonds/shared key/saved code/phone settings unchanged. No publication/Core/
175installation/Windows work. Old actual still failure kept as unique evidence.

## Historical2026-11-18 12:25Z — affected physical DVD scope qualified

WP08-004/005/007 and WP09-007 close stated available criteria, canonical93/127
complete/34open. Actual120832Z chapter23observations/11stable samples,121146Z
audio/SPU/title/Stop/replay9rows with1000/440/440/1000Hz digital HDMI, PAL/sparse/
ALADDIN measured speed1.0051/1.0034/1.00689x, sparse Spanish postseek/Pause20s/
Off/root/Stop, ALADDIN command-only root/Stop and122227Z native naturalEOF→new
decoded root73samples pass on113129. Exact profiles/stock preserved. Runners
wait new menu pictures/highlight instead of stale pixels/fixed2s; no new runtime
fix was justified by those oracle races. Initial121928Z ALADDIN read timeout
is UNKNOWN, actual read-only continuation passes; preserve unique evidence.

One-picture physical still and repeated disconnect/teardown, native angles,
long-run and broader caption/receiver/WAN/gamepad/publication stay separate.
No blanket all-format closure. Passive70s BRIDGE013 pointer observer14172
runs without input/arm/unlock, to distinguish trusted motion from BLE receipt;
keeper66107 remains bounded through~1227Z, do not silently rearm. GuidedAccess
OFF per user. No commit/push/release or Core/175installation/Windows change.

## Historical2026-11-18 12:01Z — P06 scoped acceptance complete; phone reconnected

WP06-004 closes its stated genuine external palette-present/missing/forced-only
scope:22actual stock assertions, WebKit/Chromium normal6each, forced5, missing5.
Exact owned IFO restored/hash verified; no Core/restart/175 installation change.
Final113129 affected Breakfast QSV/WebKit HLS+1000ms115116Z passes25rows;
Taskmaster software/Chromium MPEG-TS-1000ms114901Z passes16. Natural clears,
new seek pictures/fullscreen/profiles/independent retirement pass, cleanup[].
Broader P03/P04 lifecycle/display/Copy boundaries remain explicitly separate.

User confirms Guided Access OFF and phone connected. Fresh HDMI115558Z shows
deliberate Exit page, paired visible page1 rediscovered. Real BLE Enter on exact
reconnectAfterExit115823Z passes trusted down/click/up, returns SageMC; initial
retryConnectionBtn guard sends0input (different hidden error-screen button).
17helper guards pass after allowlisting exact Exit reconnect target. Existing
test owner's old session is404 after reconnect; refreshing only idle/paused
test state before DVD work, never replaying old Watch/Seek. Explicit bounded
keeper66107 starts1157Z/1800s/idle60, not auto-rearm or no-lock PASS. Recording
78948 finished naturally1030Z; late permission requires no stop. Physical DVD
and remaining unblocked tasks continue; no publication or Windows work.

## Historical2026-11-18 11:42Z — P06 lifecycle correction installed, real WebKit PASS

Normal-manager113129 is installed through SageTV Update, WAR SHA256
63ba258653739b6a824346ddffbd3d3b5797c99b4fa823f79a47ba9897057aac,
ZIPec2998aa94fab4f4faaf2d9e072f2167fc29ec2226d107c799fb70a049ad5634,
MD597b18b6fad652ce338261d430b670868.215Java8/72assets/embeddedWAR/served14/
stock20 pass. Manager60915 closed; exact SageMC restored. No restart/Core.
Actual WebKit113850Z normal VobSub field passes6rows: fullscreen, new Seek
pictures,1612visible genuine pixels at3.835s/118frames, clear4.599s/140frames,
profiles unchanged/no errors/cleanup[]. This verifies the queue correction
against stock playback; genuine subtitle over generated A/V, not iPhone.
Chromium normal, forced-only/missing and final affected captions continue.

Earlier113640Z partial gets bitmap but a transient MCP connection timeout in
cleanup escapes before report serialization; no full PASS. Host independently
verifies0UI/recordings afterward, no Stop/input replay. Driver now preserves
cleanup UNKNOWN and writes a result even if read-only retirement query fails.
Fresh113850run passes; raw earlier evidence stays until parent closure.

## Historical2026-11-18 11:34Z — genuine P06 integration/lifecycle correction

Normal manager110910 installed through SageTV, protected20/WAR hash verified.
Local24genuine palette/ID/forced/timing guards, ordinary workers,32DVB and both
renderers9each pass. Stock fixture78951 has generated120s H.264/AAC plus the
byte-verified genuine IDX/SUB/IFO in established test import root/WP06-VobSub;
one public scan, no new import root/Core changes. Actual stock WebKit normal
112255Z and later diagnostic run get moving new A/V after100sSeek but no
bitmap despite successful worker output. New regression proves old worker
stop clears replacement's shared file queue. clearToken fixes that unit
failure; actual image counter/decoder diagnostics now report meaningful state.
New package staged113129, manager60915 update underway; do not call installed
or corrected field result until verified. Full progress in WP06-004/PROGRESS.

110910 post-update WP03 original QSV/WebKit HLS+1000/fullscreen/natural clears
111815Z passes25rows. Earlier111656Z refuses still-retiring manager context,
0rows/no playback: not a new caption failure. Final affected rows follow P06
lifecycle installation.086 Guide classification closes as NOT REPRODUCED;
42bridge guards/149portable files and104700Z330-sample owner test qualify025B,
not phone no-lock. No keeper remains active after111650Z bounded teardown.
7closed successful raw/helper files2,268,030bytes retired recoverably/hash
verified; unique open failures and canonical fixtures preserved. Phone still
has no authorized page/HDMI signal at last check; no blind code/input/replay.
Continue executable host work, no checkpoint final/publication/175/185 writes.

## Historical2026-11-18 10:55Z —085 installed; affected clock/caption fields pass

Recording78948 finished naturally at1030Z; the unanswered interruption request
is no longer needed. Normal-manager3.3.0.20261118.103154 installs085 through
the plugin manager, without restart/Core changes.20protected stock hashes,
14served assets,214Java8 classes and72assets verify; manager89171 retired.
WAR c420a6edf7c57ffb2b59fb02356497e42d6b35bdb25146d20b6ead92e48e0724.

Actual old-build host DVD clock103054Z fails by-18831ms after20s Seek and
8.77s of new pictures. New installed WebKit103950Z and Chromium104215Z each
pass23samples, final difference160/192ms, no JS errors or cleanup failures.
This closes that reproduced clock comparison, NOT actual iPhone chapter,
representative-disc/cadence or all-DVD acceptance.085 stays open for those.
WP03 original-source QSV/WebKit HLS+1000ms fullscreen/natural-clear run105051Z
passes25rows, including real moving-source Teletext/DVB clear callbacks.

Phone reload104701Z found zero Safari pages; fresh HDMI105147Z shows color
bars, not an unlocked device. No blind input/unlock/reload replay. Async user
notice requests reconnect while independent Guide/caption work continues.
Bridge100410keeper failed OWNER_EXPIRED after heartbeat TimeoutError while
BLE remained secure. New host-only absolute metadata deadline has7+30+5
guards; explicit104700Z keeper runs, not a physical no-lock certificate.
Firmware/bond/key/code/settings unchanged. No publication/175/185 changes.

## Historical2026-11-18 10:25Z — local085 ready, recording blocks install/field

Installed normal manager remains092411, stock20 unchanged.082/084 scoped
actual iPhone Play/fullscreen/returned-menu BLE Select and both host STVs12
rows each are closed in ledger. WP12-004 reporting/strict-policy scope also
reconciled complete from actual QSV/software/fallback/Copy evidence and policy6/
profile9, not every vendor/receiver. Canonical WP count88/127,39open, not stale58.

New085: actual095110Z reader runs chapters ahead of presented0..14s; original
gate waited for chapter1 to recur and sent Next late, so do not certify its
chapter interpretation. Corrected helper now refuses that initial read-ahead.
Separate failing-before no-STC/new-A/V-origin clock regression is proven.
Local candidate latches real new A/V origin, isolates future NEWCELL metadata,
preserves STC/SPU/wrap, bounds producer lead14s and unread native input256KiB
without changing browser12s reserve. Generated35s FFmpeg holds14.52s and
refills/cancels/Stops; protocol/TCP/SPU6/runtime6/fallback2/70playback/both
engines11DVD-DOM+3SPU PASS. Latest package214Java8/72assets byte verified;
hashes/source boundary and required physical gates in compact085PROGRESS.
Not staged/installed. stock-dvd-clock-field.py waits for idle; one earlier
harness used wrong shown key instead of ok (fixed), later attempts refused
activity guards before any playback. No uncertain action replay.

232 records NBC5NewsTodayAt4AM id78948 since1000Z; public recordingCount1,
0UI/clients/encoders remains at1025Z. Do NOT stop/restart/update; asynchronous
question asks leave-running vs exact-recording authority, no answer yet.
Permanent232 restart permission does not authorize interrupting a recording.
Continue independent work; Windows deferred,175 untouched. Phone exact Exit
095545Z sourceclear/ACK/settings preserved, not currently a playback owner.

WP03 signed delay3original-source runs/60rows PASS (QSV/WebKit HLS±1000 and
software/Chromium TS-1000); actual preview images reviewed. Fullscreen/natural
clear follow-up is prepared, not falsely closed. WEB086 retains initial Guide
Timeout, new phase/geometry capture and Guide-only scoped mode. No runtime
Guide change or claim of root cause from later two passing12row runs.

119closed/corrected082/084/025A raw files/helper,47,219,529bytes retire to root
deleteme, every hash checked; compact records remain. Keep086093854JSON/guide,
023084127Timeout/091340/091353/091541/092008chapter witnesses, new095110clock,
WP03active results and older unclassified Copy/041314keeper failures. No
blanket artifact sweep. New explicit keeper39827/1800s/idle60 from100410Z;
prior85338 completed321samples, not a physical no-lock PASS. Firmware/key/
bond/code/OS settings unchanged. No commit/push/public release authorized.

## Historical2026-11-18 09:36Z — WEB-084 installed, actual return-menu gate

Normal manager3.3.0.20261118.092411 installed through stock STV Update;20
protected hashes/14served assets/214Java8/72assets PASS. WARacf6570a07d172087
a20f4072e53eaa044829bbde373167ff197e9c5fdb934ab, ZIPf530a5f7a49b53a352a2b521
5ba69236d9476bac92d9bd41098c52d1cf6e34c5. Frontend tags unchanged081.2etc.
Independent0recordings/UI/clients before phone reload. No restart/Core/175/
185/publication. Manager79774 closed; current phone exactUI123c8282e1ee/page1.

WEB082 actual093252Z normal Watch20819 + production Play completion reads
unknown→preview→fullscreen/one TV/no error/profiles preserved. Real BLE
autoplay093406Z has trusted Enter/click/keyup and advancing native HLS.
WEB084 actual093354Z BLE Enter naturally plays feature→new decoded menu:
69samples PASS.093548Z real BLE Enter20 from that returned root submitted
once; verify actual new feature pictures/native not-menu next, then affected
host mobile-Play rows.13public-layout/9intent/9DVD-Select guard groups PASS.
Public208 only applies exact local nativeDVD/menu/no-modal/known OSD; no MCP
production dependency or generic-event retry after unknown dispatch.

Bridge58269 completes337samples/no failure. Explicit new1800s/idle60 keeper
85338 runs for DVD input validation; no automatic unlock/rearm/no-lock claim.
Guided Access clarification still pending. Continue next safe runnable task,
not a checkpoint final. Prepared WP03 signed timing field follows host guards.

## Historical2026-11-18 09:05Z — resumed full list, WEB-082 active

User explicitly objects to ending at the portrait batch and says never stop
at checkpoints. Continue authorized runnable work, not a final-summary-only
handoff; absent equipment blocks only its own row. Phone is connected852x393
landscape, paired WebKit/BLE secure/bond1. Latest normal-manager installed
085623 contains candidate public-layout evidence, frontend assets unchanged
main080.1/mobile079.3/playback-SW081.2. Do NOT call082 fixed yet.

Actual083200Z one normal Watch20819 is behind native Main Menu; real BLE
autoplay activation083310Z produces trusted Enter/click, then ordinary TV
083605Z visibly opens full DVD root. Server contentState stays unknown:
083822Z opcode ledger has NO GFX130 and no media rectangle. Browser colour-
key placement cannot provide the owning server intent guard with menu identity.
First qualified-ordinary-Main/OSD candidate084448 does not fix actual dynamic
SageMC; retained public read-only viewEvidence in085623 proves090148Z exact
menuName="Dynamic Menu by nielm", menuSymbol=PRQST-1212481. Latest source
now qualifies ONLY that exact pair for SageMC preview as well;13public-layout,
9fullscreen-intent tests PASS, normal build/package completed. Third normal
manager installation and actual iPhone Play still required. New diagnostics
contain only fixed allowlisted public widget metadata, never body/paths/errors.
Stock unknown/custom/modal/foreign guards and one Watch/TV/no replay retained.

Real BLE DVD Enter084127Z starts actual feature (084234Z1568frames/60.857s),
but its observer times out; do not count whole HID gate PASS or replay Enter.
Phone approved Exit084344Z/085532Z preserve all settings; independent0activity
and20stock hashes precede both normal-manager updates. No175/185writes or
publication. At0902:13Z232 independently exits0/notOOM, unknown cause; no
shutdown hint in last100Docker log lines. Prior API showed0recordings. Used
standing test-container start authority, not a claimed Core crash/idle proof;
owned session63018 awaits bounded readiness.090323Zphone Exit source clears
but server ACK remains Disconnecting while offline, not retirement PASS.

Bridge host-only5new keeper/30toolbox guards and148portable package PASS.
Explicit082919Z1800s/idle60 keeper completes085922Z332samples/no heartbeat
failure (physicalNoLockVerified=false). Old041314ZRuntimeError evidence stays.
New explicit bounded DVD follow-up keeper session58269 since~0900Z, no hidden
rearm/unlock; verify live status. Asked whether Guided Access is on, awaiting
reply; do not attribute awake screen to jiggler alone. Bridge firmware/bond/
code/key/OS settings untouched. No web commit/push/publication authorized.

## CURRENT2026-11-18 04:48Z — portrait/landscape batch and081/073 qualified

Current installed stock232 normal manager3.3.0.20261118.042325, main080.1/
mobile079.3/CSS079.2/playback-SW081.2; hashes in compact081RESULT.70playback,
8PWA,11DVD-DOM each Chrome/WebKit,72assets/213Java8/14served/stock20 PASS.
Actual phone content-first portrait10BLE rows, landscape layout/long press
and App Reload preserve profiles;078/079/080A scoped work in ledger.081.2
actual recording042911Z consumes827frames and genuine ended90.1055s without
Buffering, not a clock write. Actual044152Z DVD direct-control decoder gate
passes71samples: feature→new root menu generation4→5/2150frames/4716SPUpixels/
no message. Its first Enter attempt never left SageMC preview, not a changed-
tail failure. Preserve043152Z report and043549/043708/043900Z layout reads for
broader023 list-Play/fullscreen navigation; direct decoder proof is not input
or finger certification. Existing public MCP setup only, no Core changes.

Final host WebKit strict original Breakfast Copy/HLS044504Z16PASS, no errors/
cleanup[] actually exercises Copy initial alignment at source45s/sample0.626333
without producer-origin changes.073 identified reserve deadlock closes; older
unclassified162407/220422/224028 raw traces stay under broader020. Actual
captions/Off/profiles/ownership readouts retain exact scope in compact073/081.
No unrelated matrix replay. No commit/push/publication/restart/175/185writes.

Exact phone Exit044410Z acknowledged/source cleared/profiles preserved;
independent final0recordings/UI/clients/encoders and stock20 verified after
host work. Approved reload044729Z reopens idle phone for user. No test media
left playing. No keeper is currently running:1631 exited04:18:13Z RuntimeError,
36observations/0unlocks, not a no-lock PASS. Keep its bridge failure report;
do not reuse an expired owner or silently rearm. Firmware/bonds/code/key and
OS settings untouched. Portrait content is the default after user rotation.

Completed current-session raw phone/installer/recording/Copy captures retire
recoverably with compact results and workspace cleanup report; unique older
020 and current023 preview/bridge failures remain. Remaining requested actual
future scheduling080 needs an owned future-airing fixture, not a real user's
programme.023 still separates moving-video physical rotation, finger inertia,
background/WAN/acoustic/absent-controller and broader all-disc acceptance.
Do not reopen/automatically rerun passed rows for unrelated future changes.

## Historical2026-11-18 04:25Z — real phone portrait PASS,081.2 EOF test running

Phone is now reconnected and user confirmed landscape. This supersedes the
earlier intentional-disconnect restriction for the resumed authorized session.
Fresh035158Z physical393x793/DPR3 stagey83/16:9/Recordings-Series41folders;
040014Z actual10row BLE folder/Guide107logos/three native Info/Play PASS,
14presented frames/nativefullscreen/profiles unchanged. User040224Z rotation
852x393 hides dock, fills native STV; clip already at EOF, not active-motion
rotation proof.040557Z real762ms canvas long press opens remote once/no native
command.040854Z actual one-BLE-Enter App Reload changes origin/preserves exact
client/stream/top preferences.078 closes;023 broader scopes stay separate.
See compact023/PORTRAIT_20261117.md and078RESULT, not blanket finger/audio/WAN.

New081 actual recording EOF freeze: old clip89.3/89.984 paused/Buffering0.1/
server0.6. Failing-before regression and finite-known-recording-tail fix081.1
passes68tests. Its phone041558Z then exposes separate native buffer deadlock
at4.085s (99frames,ready4,range8.007..89.726).041918Z instance read proves
intentPaused=false/rebuffering=true/recoveries0, completed ENDLIST/exit0.
Another failing-before test reproduces it.081.2 leaves native Safari's
decoded-range/loading transitions browser-managed; no pause/time jump/fake
ended or user Pause override. MSE reserve and bounded completed-tail behavior
remain explicit.70playback/8PWA/11DVD-DOM each Chrome-WebKit/72assets/213Java8/
14served/20stock checks pass. Normal manager3.3.0.20261118.042325 now installed,
main080.1/mobile079.3/CSS079.2, playback-SW081.2. WAR7fe754ea34255924f66383976
ae4e1125fbf306f646716e435385dfd5c34fd65; ZIP24d2449adb45dbb2e1fb414e8fd997aa
14370714621f073e5a98e6a9eda51c9f; MD591a40c7b7879e9fea676b49287fd68c7.
Phone reloaded042518Z; iphone-recording-eof-gate.py is currently running via
session73842, one exact public Watch20905 setup/no Seek/no settings writes,
natural-tail actual ended listener. Do not claim PASS until its final result.
Keeper1631 explicit1800s/idle120 starts~0413Z, no unlocks; verify it remains
active and end only our owned helper at session completion. Prior36461/80909
helpers were stopped by exact verified test-session process tree; firmware
watchdog expires those leases. No phone reset/flash/bond/code changes.

Independent final manager retirement before phone reload:0recordings/clients/
UI/encoders, stock20 pass. No Core/server restart/publication or175/185writes.
After081 qualification, retain compact results and retire completed owned raw
captures; keep unique081gap/EOF evidence until correction is qualified. Other
073Copy issue and080owned-future-Record remain distinct, not silently closed.

## CURRENT2026-11-18 00:40Z - portrait content browser installed; XMLTV fixed

User reaffirms portrait should avoid native-STV navigation; rotate for the
native STV. Normal manager3.3.0.20261118.002951 serves main080.1/mobile079.3/
CSS079.2/SW080.2, app078.2/support077.1/playback073.1/streaming066.1 unchanged.
Portrait defaults Recordings, series/folders/categories/breadcrumbs, two-axis
Guide with real107channel logos and readable bounded selected-program card.
Live Play/future Record/Info are explicit actions, Controls optional. Native
Info works for recordings/guide/videos on actual SageMC and stock SageTV7;
no Watch for Info, private Core edits or required Client Extension/MCP playback.
Record accepts public opaque async receipts, then observes scheduled status
without replay. Its actual future manual-schedule gate remains pending: only
mocked UI/Java receipts are qualified, no real user's programme was scheduled.

Local six new-library/six affected-deck Chrome/WebKit cases,8PWA/4spacing/
2reload, grouping/path/Info/logo/async-receipt Java guards and72assets/213Java8
pass. Actual stock WebKit003241Z/SageMC and Chromium003347Z/SageTV7 each pass
12rows/errors[]/cleanup[]; correct Info titles visually reviewed,107logos
decoded, exact20905 Play/new frames/fullscreen/active rotation, profiles
preserved and original SageMC restored. Final14served assets/20protected
stock hashes pass;0recordings/clients/UI/encoders. No restart/publication.
Compact results/WEB-079/RESULT.md and WEB-080/RESULT.md retain exact scope.

XMLTV-PLUGIN-006 closed: normal plugin Configure + stock source wizard
selects FTA_60177/provider2/shared175 feed, existing HDHR/input and no new scan.
Two imports succeed,107channels/logos and637current4h airings.175 read-only;
XMLTV3.6.0 binary unchanged. See owning XMLTV compact report. Phone intentionally
disconnected; no wake/unlock/reconnect/rearm attempts. Physical023/078, owned
future Record080 and intermittent073 remain accurately separate. Completed
raw079/XMLTV commissioning is retired recoverably with cleanup report.

## Historical2026-11-17 23:43Z - WEB079/080 local, XMLTV setup in progress

User wants portrait content-first, SageMC-like series/category/import folders,
two-axis channel/time Guide with logos and live Play/future Record/STV Info.
079.1 main/mobile/CSS/SW candidate builds with72assets210Java8; six production
DOM new-library and six affected deck cases pass Chrome/WebKit320/393/768.
8PWA/4spacing/2reload, grouping/path models, public relative-path and known-STV
Info Java guards pass. Info uses public scoped context/menu APIs, not Watch/
arbitrary widgets/expressions/Core changes. Candidate not installed yet.
Last installed231106 has playback073.1/app078.2 and strict actual WebKit Copy
231336Z passes16rows/no cleanup faults; no alignment branch fired in that run,
so don't claim intermittent073 fully closed. New raw073230042 evidence retained.

XMLTV-PLUGIN-006 audit proves232 placeholder867507149 defaults missingepgdata.xml.
Read-only175 FTA_60177/id2 uses shared22MB xmltv_60177.xml (107channels/29742
programmes Nov17..26). Existing plugin Configure UI saved managed provider2,
name/feed/Generic/logostrue (no direct config writes); capture-source lineup
still placeholder and needs normal guide setup/import proof.175 unchanged.
Commissioner93584 stopped. Native retirement guard before next manager.
An early079 field invocation accidentally ran against prior231106, so its
missing group-select is a pre-install test, not a regression in installed079.
Phone intentionally disconnected; no further phone/BLE/rearm attempts.

## CURRENT2026-11-17 22:52Z —077/072 closed,078 installed/phone unavailable

User later confirms intentional phone disconnect. Leave phone/BLE alone;
continue host Chrome/WebKit work and defer only physical rows. WEB077's earlier
actual geometry remains valid. Candidate includes073.1 initial Copy-gap client
correction and078.2 compact App-setting field; final packaging/manager/affected
field checks are running, not yet installed/qualified. No publication.

Current normal224414 serves app/SW078.1, main/support/CSS077.1/mobile076.1,
playback069.2.72assets210Java8/14served/stock20 pass. App/Reload webpage actual
Chrome-WebKit same-URL/cancel/accept/persistence and8PWA/4spacing cases pass.
Physical078 pending:224741Z no Wi-Fi endpoint before expression, HDMI no-signal
bars and BLE disconnected/securefalse/bond1retained. No blind key/unlock/rearm.
Keeper81334 exited1after299observations/RuntimeError, no no-lock PASS. Earlier077
physical geometry y83→107→83 and unchanged profiles remains valid. Phone
reconnection requested nonblocking; continue independent host gates.

WEB072 AND WP05-003 closed: real-bridge failing-before regression pinpoints
A53 replacement-relative timestamps compared to absolute file clock. Only
drain/read clock now subtracts producer start; Teletext unchanged.16bridge/
26native-seek/10GFX/publicCC pass. Actual no-trace223556CEA14rows and223738
Teletext13rows reviewed: before/afterseek readable, Off0alpha/localtext0,
CC2blank forchannel1-onlyCEA/visible onTeletext, original STV/profiles restored,
cleanup[]; video36.670 shows32/34/36 rather than old blank/future captions.
Compact072RESULT owns223312hashes/scope;078includes same correction unchanged.
No Core/restart/publication/175/185/Android mutation.

WEB073 still open: corrected producer-relative frame oracle passes222521 and
22485016rows each.224028repeat actually recovers once, new start60.241 vs60.000;
exact-origin guard correctly refuses, underlying reason unproven. A bounded
24-record payload-free production error observer is now locally tested and
installed only in the next ephemeral test browser, not production runtime.
Current next Copy run started~2252Z; wait exact process/retirement before next.
Preserve original162407/220422 and224028failure evidence; do not loosen target
tolerance or infer this independent Copy failure fixed by legacy-only072.
Closed076/077/075comparison70files23,450,066B hash-retired recoverably;072raw
retirement still due after compact review. Remaining all-task continuation
stays active; unavailable phone/gamepad/WAN rows block only those rows.

## CURRENT2026-11-17 22:24Z —077 closed, caption work continues

Normal221742 installs main/app/support/CSS-SW077.1, mobile076.1/playback069.2
unchanged. New App/Portrait top spacing0..160/default24 beyond auto-safe-area,
live common-stage only.22profile/4spacing/6dock/4settings/8PWA/package72/210/
14served/20stock hashes pass. Actual phone page3 (old2retired)222140Z shows
y83→107→83 for24→48→24,393x221.0625/16:9 and exact profiles unchanged. HDMI
222229 reviewed. Compact077RESULT has hashes/scope; ledger/mirror updated.
No restart/Core/publication. Actual phone reloaded3after manager retirement;
explicit keeper81334 runs2219→~2319Z, no no-lock certification. Next073 frame
observer fixes (test-only producer-relative attribution) rerun, then072 no-trace
CEA/Teletext post-seek/Off. Last220422UK Copy fails DVB moving with time4s/
pausedfalse; don't equate it with originalready4/time0failure. Preserve both.
User asked about a Reload webpage button; earlier commentary only offered it,
no dedicated reload button implemented yet. Continue all safe runnable backlog.

## CURRENT2026-11-17 22:04Z —075/076 closed, full backlog continues

Normal214932 serves main/mobile-SW076.1/CSS075.1.9Node/Java/6DOM/8PWA,
72assets210Java8/14served/20stock hashes pass. Actual WebKit2155598rows and
Chromium2203178rows pass native full-screen Play, new pictures/active rotation/
profile preservation/retirement. Actual phone page2 trusted BLE Play220101,
220123ready/exact20905/fullscreen/379frames, advancing video/no busy button,
unchanged profiles and y59/16:9; HDMI220133 reviewed. Both tasks in ledger,
compact075/076 results retain scope/hashes. User's all-tasks continuation stays
active: next073 original UK Copy/HLS rerun21419 (started2204Z), then072 no-trace
CEA/Teletext with added post-seek/Off review. Do not end at this checkpoint.
Phone approved Exit220223 acknowledged/exact profiles/no source; independent
0activity verified before host. Keeper10337 until~22:17Z; don't infer no-lock.
Old intermediate no-code/auth/Home captures47files/13.48MB hash-retired to
rootdeleteme; open caption/Copy raw evidence untouched. No Core/restart/release.

## CURRENT2026-11-17 21:50Z —075 physical PASS,076 normal update staged

User portrait status-overlap fixed in manager213725/CSS-SW075.1. Actual phone
page2 stagey59/393x221.0625,24targets44x44/Controls252pxno-scroll, profiles
preserved and HDMI reviewed. Compact075RESULT owns hashes/scope. All3content
tabs actually click through BLE; Recordings500/Guide48/Videos500, local focus
without native arrows. Synthetic canonical filter/target prepared, no Play yet.
User adds fullscreen-after-list-Play076: browser bounds exact intent/retirement,
public native source/loaded/no-modal read, ordinary TV once from known preview,
wait actual fullscreen, no Watch/TV replay/Core/MCP.9Nodecases/Java exact-source
guards/6Chrome-WebKit DOM rows pass. Build72assets210Java8/packageverified.
Staged214932; normal manager install pending. Phone approved Exit214842Z has
server ACK/no source/exact profiles; independent0activity verified2149Z.
Current keeper10337 remains explicit until~22:17Z; check actual expiry.

## CURRENT2026-11-17 21:28Z — all authorized acceptance resumed

User reconnects phone/resumes all tasks. Installed185813/074.3 unchanged.
Wi-Fi initially OFF/cellular; user restores it21:24Z. Paired endpoint/tunnel/
RSD pass. Real ESP32 Home/Search/Enter opens Vibe to232 Basic Auth; no phone
code submitted (fresh StandBy correctly refused). Keeper10337 explicitly
3600s/idle15s from~21:17Z; verify actual owner, no no-lock claim. Actual portrait
acceptance remains pending. Serial traced stock legacyCEA212323Z now visibly
renders CC1; no-trace run48529 is active, wait full retirement before new host.
WebKit Copy212516Z fails replacement-origin guard at Teletext post-seek after7
rows; native cleanup succeeds/independent idle observed. Original162407Z DVB
freeze stays open. Preserve failure metadata; no blind seek replay/Core edits.
Bridge host os_field_step.py adds bounded explicit reviewed OS actions; must
finish mocked safety tests/docs before commit. No release/publication.

## CURRENT2026-11-17 19:02Z — portrait WEB074 installed; prior work parked

User new portrait request resumed only074 after explicit pause. Normal manager
185813 installs main/CSS-SW074.3/mobile074.2, unchanged playback069.2. Full-width
TV-aspect STV above modeless Controls and scrollable searchable Recordings/
Guide/Videos. Public exact-local Watch is dispatched once, including opaque
async receipts; no normal MCP playback/Client Extension dependency/Core changes.
6final DOM rows/56existing mobile/4landscape/2surface/8PWA and affected Java/
policy gates pass. Actual185251Chrome/185406WebKit6rows each and final190055
WebKit7rows pass: real lists, exact media20905 Play, new presented video,
rotation/profiles/retirement; final drawer/tab check included. No phone input.
72assets210Java8/embeddedWAR/14served bytes pass. WARca99174de015d4a0899e8a09229201dc7f3c729344d8053ad3738ec124dd3863,
ZIP0aadc03b111b7eb2f848a8de5dc59c1556b2d82f7501d640b38202cc6f7b102c,
MD5f1aa4328fb575171304840817c3d7b00/epoch1794942000. See compact074RESULT.
WEB074 available implementation closes; actual phone portrait acceptance is
WEB023, not host-WebKit PASS. No commit/publication/restart/175/185/Android.
Prior caption/Copy backlog remains parked. Pre-pause072 caption adapter is in
these development packages with12Java guards, but legacy CEA visual causality/
correction still OPEN.073 retains unique162407Z UK Copy/DVB post-seek failure.
Pause stopped the owned1601Z keeper; do not restart keep-awake/unlock without
an active phone test. Settings, ESP32 firmware/bonds/passcode and phone unchanged.

## CURRENT2026-11-17 16:07Z —070 closed; legacy stock-caption probe active

070 final18P14 per engine/4actual host rows each and actual phone160250Zplaying/
160433Zpaused PASS: new producer/presented target/twoACKs/restore/no marker,
exact profiles and160529approvedExit. ParentWP14-002 and070 moved to ledger;
compact results/WEB-070/RESULT.md owns hashes/targets/limits. BRIDGE028 closes
its trace-tool scope. Apple autoplay review071 adds3policy tests;62playback
PASS, no runtime forced-mute/sound override or wrapper. docs/SAFARI_AUTOPLAY.md.

Next stock-legacy-caption-field.py uses browser-local captions OFF, intentional
ephemeral stream config, existing stock-STV route/public callbacks only,1280x720
host. It explicitly leaves visualAcceptancePENDING_REVIEW; counters aren't a
caption PASS. First160623run misread absent ok field as rejection, then early
Home restoration unverified; no runtime rejection/visible-caption claim.
Second38066 awaits actual new-STV drawn pixels and fixes response guard; inspect
its process/result BEFORE another native UI. Review failure/corrected screenshot
and original STV restoration/independent retirement. Never replay Home/Stop.
Phonepage4 is exited and profiles unchanged; keeper64450 completed658samples,
explicit12284 runs1601→~1701Z, secure/one owner/keep-awake verified1607Z.
Continue next safe authorized caption/DVD/audio/parity tasks, no checkpoint end.

## CURRENT2026-11-17 15:54Z —070.3 installed; new-producer acceptance active

Normal-manager155038 installed main/SW070.3, unchanged playback069.2. Served13
assets match; package71assets207Java8/embeddedWAR pass. WAR
ffd05ed3d22c1f914b59d869ddcc436b4e09eaa53362a24748eecfd5122d006f,
ZIP7f7d097b3b817709a36613a2218e250c6d89385a349304a8e7a9de77a7d17b0c,
MD59d311a18cbd0dd1d2c446b5a43e0427e; epoch1794930600. Manager90338 exited,
independent activity0 verified1553Z. Actual affected Chromium run29329 active;
wait full process+retirement before WebKit, then physical phonepage4 reload.

070.2 actual phone playing154316Z/paused154436Z both passed with two seek ACKs,
presented forward frame and restore/no marker/exact settings. BRIDGE028 closes
its observation scope. A further local negative then proved old-producer frames
at the target could impersonate replacement completion.070.3 requires changed
producer for forward AND restore. Failing-before negative and18P14 each engine,
8Exit/8PWA pass. Cancellation test resets its deliberately corrupted fixture
between independent scenarios; no corresponding production reset/replay.

Phone approved Exit154949Z acknowledged/no source/all profiles unchanged.
No Core/restart/publication/175/185/Android change. Keeper64450 explicit through
~1600Z; check actual status and expiry before continued physical tests. WEB070
and parentWP14-002 remain open until final host/phone presented-source checks.

## CURRENT2026-11-17 15:38Z —070.2 installed; actual restore failure under investigation

Normal manager152854 installed main/SW070.2, unchanged playback069.2. All13
served assets exactly match. WARdb9fbe31ce14a5d97ab4e2af2773e4b28e1e787ac7e9505080070ad47fef33db,
ZIP279daa1989d1a5746dcd6ccf5b1291953374ea65147d9e81f937d62fa0a5d2f1,
MD51c1536583fa43a254131117b4ca92e14; epoch1794929100. Manager76331 exited;
independent native retirement0 verified1537Z, protected stock20 unchanged.
Actual affected Chromium current-video run26012 is active; playing/paused
presentation rows pass, terminal ZIP/retirement still pending before next UI.

070.1 actual iPhone1518Z passed forward presented-frame seek but restoration
returned ATTENTION/pending. A later videoStart could silently retry that restore;
070.2 now records restoreAttempted/delivery before sending and forbids late
same-session/attempted recovery replay.17P14 cases per engine pass, including
the failing-before delayed-source negative. BRIDGE028 adds one-attachment
payload-free target/anonymous-producer/ACK trace; local15guards pass, actual
trusted traced phone click remains pending. The physical restore defect is
NOT closed by the no-replay guard or host passes. Phonepage4 exited152725Z;
after host retirement, reload/fresh owner/watch exactNightline27166, one setup
seek300000, trusted Play if prompted, then traced playing/paused production test.
Keeper64450 explicit1500→~1600Z; no automatic unlock/rearm/no-lock certification.
No Core replacement, restart, publication,175/185/Android mutation.

## CURRENT2026-11-17 15:11Z — WEB070 installed; actual field29597 active

Normal manager150548 now installs main-SW070.1.13served bytes exactly match;
71assets207Java8/embeddedWAR/stock20 verify. Manager32592 exited; independent
0recordings/UI/clients/encoders before actual tests verified1510Z. Real
stock-current-video-field.py --task WEB-070 runs Chrome→WebKit serially in29597,
requiring each reversible seek's actual presentedMs near target, not only
logical anchor. Need wait process completion AND exact retirement before phone
reload. Do not repeat completed Copy matrix for this test-only client change.
Candidate hashes/epoch remain in15:09 section. Phonepage4 currently exited with
confirmed Stop/unchanged profiles, keeper64450 bounded1500→~1600Z, no unlock.
Continue physical playing/paused current-video, then next runnable parity scope.

## CURRENT2026-11-17 15:09Z — WEB070 staged, manager32592 active

Installed runtime remains143952/main-SW068.2/playback069.2. New main-SW070.1
candidate built/staged150548, WARfc63f163a5cb9611921dd065b54ad129e16186bc4608f8a5d42b787c2353ae73,
ZIP68370b7e692cd94fda173a6c6467af24234705b7e34fa0a8ba14cc03116e749d,
MD5510b08a74c6f355bf87b782577e69a71; epoch1794927600.17P14 each engine/
8Exit/8PWA/package71assets207Java8 pass. Failing-before withheld-frame negative
proved the current-video test accepted logical anchors before any new frame.
070 gates seek/restore on existing exact-producer lastPresentedTime; unavailable
frame API skips unsafe mutation, failed restore retains ATTENTION/marker/no replay.
WP14-002 REOPENED, old source-ownership/export results remain dated. Existing
UI helper default writes under067; new --task WEB-070 owns final affected runs.

Manager32592 has reached installed-plugin disclaimer, accepted OK and clicked
exact Web row at1509Z (read output/latest screenshot before Update). Install
only normal manager, verify exact assets, quit/wait independent native retirement,
then stock-current-video-field.py --task WEB-070 Chrome→WebKit, no unrelated
Copy matrix repeat. Then phonepage4 approved reload/current assets/fresh owner,
real playing/paused test with trusted BLE and presentedMs required. Physical
old143952 playing1456/result145659 and paused1500/result150146 report PASS/exact
saved state, but are NOT withheld-new-frame certification;070 is the follow-up.

Actual phone currently production Exit CONFIRMED150448/no source/exact saved
client/streaming/caption profiles; native context independently absent before
150548 stage. No active companion borrow or temporary profile. Explicit keeper
68115 completed642observations; new64450 runs1500→~1600Z, no automatic unlock.
Current page4 remains fresh authorized, oldpage1 stale. BRIDGE027 CLOSED:14guards,
actual trusted Down/native5, Play/native7, long-press/gear/Test buttons pass.
field_hid.py --page-id4 forwards existing exact URL/nonce/visible guards.
Fresh/rebound phone api observers now use GET for status/streamSettings/
playbackState; NodeVM/Python regression pass, no implicit default-setting writes.

067/068 CLOSED owner/metadata scopes, WP14-001/003 complete; WP14-002 reopen
is explicit in TASKS/mirror/workspace order.49closed067/068 raw files/11,658,397
bytes hash-retired recoverably below root deleteme, written results and source
DIAGNOSTICS.md retain findings.070 and unresolved caption/phone evidence remains
active. Final UK software HLS144536 passes17rows incl bounded reserve observation
and exact browser/native configured defaults. No Core changes, restart, commits,
publication,175/185/Android mutation. Continue next authorized unblocked parity
tasks after070; no checkpoint-only final response.

## CURRENT2026-11-17 14:44Z — final068 retention candidate installed

Manager143952 installed main-SW068.2/playback069.2. Package71/207/embeddedWAR,
served13 and stock20 verify. WAR03abd629c493828584e4a6a82ebeea3df1591706c0659a85c26a07e57fff9115,
ZIP9efe33b244eef3bbbfcb20d1493fdefc0750833a90f980b494cf48ba11f6ea17,
MD50074eb56b9d02b7c80ed677e5c2183b0; epoch1794926400. Manager50923 exited;
independent native activity0 verified. Real current-video/ZIP Chrome→WebKit,
then selected final original UK software HLS repeat run serially in10187.
No test controls replay, Core edits, restart or publication.16P14 each engine/
10Java metadata/26recovery/8PWA pass. Existing state reply piggybacks payload-free
native counters and preserves exact-generation snapshot after terminal404,
without another poll. Failing-before actual ZIP and local regression retained.

WEB069 CLOSED:8real Copy rows pass; compact results and source-controlled dated
acceptance retain details.48closed066/069 raw files/12,073,282bytes hash-verified
retired recoverably to root deleteme/original relative paths.14private incidental
OS recovery captures/3,457,638bytes similarly retired after sanitized record.
Open067/068/caption comparisons preserved. Phonepage4 remains the current
authorized document; its Wi-Fi is restored, explicit Exit was independently
retired. Reload/current assets/actual Safari affected rows follow10187, not
another completed host Copy matrix. Keeper68115 bounded through~1500Z.

## CURRENT2026-11-17 14:24Z — TS Copy follow-up069.2 installed

Normal manager141931 installed playback/SW069.2 (main069.1/streaming066.1).
Package71assets/207Java8/embeddedWAR, served13 and protected stock20 pass.
WAR0d3d96dbf50cf4b6758444ac8eceba99ab79724799c37d611ae65a97caf5334a,
ZIP95199677194ab4f966ad1955d63fc716b145a1de5bdc9af2eca593507632a38f,
MD53e6bcde586d241b10bbbdbf8e7bbc3c3; epoch1794925500.
Manager85973 quit/process exited and independent activity0recordings/UI/clients/
encoders verified1424Z. Actual TS Copy affected retest now starts, not yet PASS.
HLS allowed/strict passed old134049; TS141307 exposed transport fallback that
preserves undecodable Copy then six recovery loops. Existing exact fallback
adds optional videoDecodeFailure only for actual Copy MediaError3/4; default
older callers preserve transport-only semantics. Saved native/browser defaults
are never rewritten. Boundary/alternatives in docs/COPY_DECODE_RECOVERY.md.
59client/17real-FFmpeg/9diagnostic/native protocol/26seek/frame-pacing/16servlet/
8PWA/13streaming/15ChromiumP14 pass. Actual final068 ZIP metadata and clean
current-video Chrome/WebKit rechecks follow Copy, then actual phonepage4 reload.
No server restart, Core mutation, publication or other device changes.

## CURRENT2026-11-17 14:02Z — candidate069 installed; affected field checks active

Normal manager installed3.3.0.20261117.134049. Served13 exact assets match
main/playback/SW069.1 and streaming066.1;71 assets/207 Java8 classes/embedded
WAR verified. WARff4fdea8ff529826ce7478443987fff1b1c85f3f2cb83dba35d51cc54aa2e616,
ZIP1a966f5618b8431434811840495bdb3b88ce327bcfb9cd43526b87cd6bf1e210.
WEB067 current-video source ownership,068 payload-free callback counters and
069 allowed Copy decode-error recovery have local regressions passing; their
actual installed field checks remain OPEN. No publication or Core changes.
Manager process70768 exited; native host UI independently absent1402Z.
User restored home Wi-Fi after cellular/VPN testing. Explicit discovered phone
page4 is current; old page1 is stale, do not reuse its observers. Actual page4
production Exit140109 confirms server disconnect/no source/exact unchanged
client/streaming/caption profiles. Native phone UI independently retired1402Z.
Phone reload/current069 physical checks follow serial host tests. Keeper46877
completed674 observations; new explicit bounded68115 runs1400→~1500Z, no
automatic unlock/rearm, no firmware/bond/key changes. Private incidental Home/
Search captures require sanitized result then recoverable retirement.

## CURRENT2026-11-17 13:24Z — WEB-067 source-owner negative reproduced/fixed

New production-DOM negative fails old code: current-video test seeks a newly
selected recording in its finally block. Client067 binds mutations/restoration
to native session + media identity, serializes tests, skips interrupted recovery
while live owner runs and reports failed restore as ATTENTION/pending marker,
without replay. Both-engine affected regressions/build/manager/real gates next.
Installed candidate remains125000/066.1 until separately verified installation.
UK serial matrix process92583 continues fallback HLS/TS, WebKit and Taskmaster;
copy Breakfast fails Chromium decode3 on both HLS/TS, not auto-transcoded.
Software HLS131254 and TS131431 each15rows pass; earlier short-window stall
is not erased by rerun and final software repeat remains selected. Dashboard
input user-confirmed working; no bond/code/firmware change needed. No publication.

## CURRENT2026-11-17 13:08Z — WEB-066 closed; serial UK matrix active

Manager125000/066.1 loaded/served13/stock20 verified. Actual original Breakfast
Chromium QSV TS130234Z and HLS130508Z each15rows PASS, no JS errors/cleanup.
Worker MSE detach fault closed by main-thread MSE + worker transmuxing. Source
origin/new producer/source/frame and native raw clock concordance are proven;
MCP Seek may return after video already advances, so a frozen-target oracle
was invalid. See compact results/WEB-066/RESULT.md. Wider matrix PowerShell
session41722 runs serially and stops its batch on failure for investigation;
currently software HLS after QSV HLS. No companion borrow or user profile
change. Phone is exited, keeper27164 explicitly interrupted after641samples/
own cleanup (not a PASS); new bounded keeper46877 runs1257→~1357Z. Preserve
bond/code/key; no firmware change, unlock, server restart or publication.
Continue remaining matrix and runnable parity rows; no checkpoint stop.

## ACTIVE2026-11-17 12:50Z — WEB-066 client MSE teardown correction

Original UK HLS/QSV12rows pass; TS/QSV12visible/caption rows expose actual
unhandled worker MSE SourceBuffer.buffered/attachment-closing exceptions on
replacement. Minimum124152/124422JSON+failure screenshots remain active.
Pinned upstream dedicated destroy posts unload/shutdown/destroy while element
detaches; public API has no awaited completion. Client066 requests main-thread
MSE, retaining worker transmuxing; no vendor/Core/server fix or hidden delay.
Failing-before policy test,17TS/55playback/13browser streaming/8PWA pass.
Build/package71assets/207Java8/embeddedWAR pass. Staged manager125000,
WARb3ef2753405368d93c55688ed5c03ca1836ef5b4c560c39b960d110930dd858c,
ZIP1b158d5b31dffd0f0b6f9a3d50312bebb4f8ca9904167f1c79cdbf50301a2b34,
MD5a5671ec8a434f7d81a421f397d489566. Normal manager installation NEXT, then
affected real seek/new-producer/new-source/presented-frame/CC/cleanup before
continuing remaining delivery/encoder rows. Use rawMediaTimeMs, not absolute
TV airing epoch, for file-relative clock checks. Public MCP ordered intent
is never replayed after timeout. No companion borrow/stock mutation/restart.

## CURRENT2026-11-17 12:40Z — WEB-065 closed; real UK field tests underway

Normal-manager123311/main-SW065.1, playback064.1. Actual explicit Exit had left
UI alive>90s on064: new client sends one bounded exact-session acknowledged
Stop, reports outcome and ignores late replies after Reconnect.8exit negative/
viewport,26recovery,8PWA/build/package/served13/stock20 pass. Actual phone
123854Z confirms Stop/no media/exact profiles; independent123936Z activity0.
No server restart/Core change/publication. See results/WEB-065/RESULT.md and
dated acceptance. Current WARcd90885e,ZIP602fab55,MD5354e626e.

WP07-001 real role capture is closed;122242Z sparse physicalSpanish0x22,
seek/20s pause/resumedOff/Stop passes native phone. No companion borrow remains.
Phone intentionally exited for serial host field tests; paused original
profiles intact. Explicit keeper27164 still bounded through~1300Z. Original
UK recordings are AVAILABLE (Breakfast TT+DVB, Taskmaster DVB), despite stale
historical unavailable text. New tests/stock-uk-caption-field.py runs actual
Chromium QSV/HLS first, then other delivery/encoder/engine rows. Do not stop at
provider checkpoints; fix demonstrated defects, preserve minimum open evidence,
and complete reviewed raw retirement/task mirrors/manifests afterward.

## CURRENT2026-11-17 12:00Z — WEB-064 closed; no active companion borrow

Current normal-manager111206/playback064.1. Actual phone stock-native natural
EOF114347Z and optional natural EOF114827Z pass.115259Z actual angle pictures
red/green/blue/red match native1/2/3/1; terminal ACK1/polls1712→1712.115721Z
exact browser client/streaming/captions restore; public1145Z CAS hook/options
restored and fullyLoaded=false verified. No bookmark change. See compact
results/WEB-064/RESULT.md and current acceptance summary. Older ACTIVE borrow
headings below are superseded. Keeper36019 completed672observations; new
explicit bounded27164 keeper starts1200Z through~1300Z for continued tests.
Continue sparse subtitle/native capability and remaining executable parity
rows. No publication, Core edits or server restart; missing field rows are
not a reason to stop independent available work.

## ACTIVE2026-11-17 11:46Z — physical native EOF PASS, optional borrow active

Current normal-manager111206/playback064.1, WAR e5fb9f39ee37b164a2f5b542a5e99d898a5e908c7338c9fafc6f1c584c8f2d19,
ZIP b39d0cb2bf579c9520d962809484623454366808ac6e39a467b9efb0f9abea5a,
MD53407f063adb3322f38a19051196c2884; epoch1794913800.
Both actual host engines terminal END one-ACK/poll-retirement pass. WebKit
10rows include optional AND stock-native natural EOF/new menu, exact restore/
retirement. Actual iPhone114347Z native EOF72samples/new menu PASS. Trusted
BLE Play1143 and Down1140 prove input recovered; no firmware/bond/code change.
Read-only lock-state1133 says unlocked. General Home/Search/reopen and one
actual blank-canvas click re-established page input/focus. Receipts alone and
visible stale SafariViewService were not proof; do not erase/re-pair for that.

ACTIVE public checkpoint artifacts/active/WEB-023/20261117T1145Z-companion-borrow.json
and browser companionForm need exact restore before teardown. No bookmark
change. Finish optional actual phone EOF/angles/terminal, then other available
field rows. Keeper36019 still bounded through~1157Z. Core20 unchanged; no
server restart/commit/publication. P01 actual mpegts1.8/HLS1.7.3 MSE now PASS;
WP01-004/08-002/08-003 in completion ledger. Task-index drift reconciled only
from canonical checkboxes/local statuses; optional approvals not advanced.

## ACTIVE2026-11-17 11:12Z — WEB-064 completed DVD tail

First064 adapter candidate manager104733 installed/71assets/207Java8/served13/
stock20 PASS. Both host engines pass13affected rows. Optional natural EOF
returns a new menu, but terminal angle fixture stalls before drain. Browser
watchdog pauses its last<250ms because EXTINF reserve is rounded0.9s longer.
Added failing-before regression; DVD-only finite decoded buffered-tail fix
now55playback tests PASS. Actual browser ended remains required; no time/end
fabrication. JS playback/SW064.1 and epoch1794913800 need build/install and
terminal/native+optional EOF retests. Native fallback test's initial Select
was sent in SageMC preview; helper now establishes fullscreen first. Do not
call that a Core failure. Stock files and all saved settings stay protected.

Fresh optional angle110038Z real WebKit RGB1/2/3/1 PASS; previous empty source
is not a valid angle-picture failure. Canonical angle-only watched reset and
waiting for queued angle state are explicit helper corrections. Physical phone
input currently emits no trusted browser events despite encrypted BLE receipt;
Wi-Fi/HDMI remain available. Asked operator a nonblocking question, continuing
independent gates. Bluetooth connection-only refresh preserved bond/code/key/
firmware; old keeper74733 gracefully stopped, new36019 runs1057→~1157Z.
Completed/corrected67raw files/61,283,238bytes hash-verified retired to root
deleteme/original-relative paths; compact063/014 reports and minimum open
failures remain. No commit, release, server restart or Core mutation.

## ACTIVE2026-11-17 10:46Z — WEB-064 terminal EOS

The1030Z companion CAS checkpoint and exact browser form were RESTORED1038Z
through public helpers; the older ACTIVE heading below is superseded.
Optional angle comparison never produced PS bytes and polled END5,968times.
The Web adapter returned capacity forever for0x80. Local WEB-064 now returns
terminal-1 for empty or actually decoder/browser-drained epochs, separately
from cell EMPTY-2, retaining reusable state. Failing-before protocol regression
and corrected protocol/TCP/SPU6/real-FFmpeg6 pass. Not installed yet; manager
094759/WEB-063 remains loaded. Rebuild/package/normal manager and affected
physical EOF gates next, then investigate initial empty angle source. Do not
label this an angle fix. No stock files/settings/bookmarks changed.

## ACTIVE2026-11-17 10:30Z — angle companion comparison borrow

New public CAS checkpoint artifacts/active/WEB-023/
20261117T1030Z-angle-companion-borrow.json is ACTIVE. Four plugin options and
exact phone hook temporarily selected; browser companion form opt-in is being
applied. Restore browser original JSON/caption state and public checkpoint
through existing helpers before final teardown. No bookmark operation.
Native angle21029test102555Z produced red angle1, but one Angle Change plus
one3s Seek did not produce a new source/picture; do not call metadata angle
proof. Compare existing optional owned navigator before any new production
fix. WEB-063 is physically CLOSED (9rows101110Z). PAL/sparse/ALADDIN physical
clocks/Stop, PAL576root4716pixels and ALADDIN command-only root all pass.
Fresh normal Audio Change101818Z has actual new consumer/nativebd81 and
HDMI439.967Hz101929Z; it uses stock FLUSH, not a no-FLUSH claim. Keeper74733
explicitly runs1024→~1124Z, no auto-unlock/no-lock guarantee.

## CURRENT2026-11-17 10:02Z — candidate installed, continue real discs

Normal-manager094759 WEB-063 installed without server restart. WARfc333e6a/
ZIP82a31a69e9bf1c9cbe3d335caacc3b3db98ca45490f84c543f7111b4996ff44c,
MD5012db043cf719037f7624795c13ac4e9; epoch1794908700.13served/20stock pass,
71assets/207Java8classes match. Protocol/TCP/SPU6/realFFmpeg6 and13affected
actual stock-browser DVD rows in EACH Chrome/WebKit pass with restored hook/
options/profile and independently retired UI. No production Extension/Core
edit. Actual iPhone gate is NOT rerun yet: phone entered StandBy and paired
endpoint disappeared. Two standalone Escapes/Home/swipe did not prove unlocked;
no passcode was sent on unknown screen. Async user-unlock request sent; do
not stop independent work. Keeper17975 FAILED094758Z (watchdog retirement),
not still active. Explicit replacement27364from0955Z ends~1025Z, no automatic
unlock/no-lock claim. Real-disc host driver now covers PAL/sparse/ALADDIN
through existing public test setup, optional companion OFF; run in progress.

## ACTIVE2026-11-17 09:46Z — WEB-063 before real-disc continuation

WEB-014 actual iPhone094345Z passes seven authored rows: main new frames,
English1000.084Hz/Spanish440.022Hz/restored English HDMI tone identity,
second title and Stop/replay, unchanged profiles. Public MCP navigation is
test setup, not BLE proof. No-FLUSH Audio Change did not produce a changed
native selector; its093736 timeout is not evidence of a successful switch.
New focused regression independently proves subtitle metadata discards audio
selection. WEB-063 separates accepted audio state; protocol/SPU6/runtime6
pass locally (old protocol assertion demonstrably fails). Candidate needs
build/normal-manager install/stock+served proof/affected physical gate.
No stock files/Extension/MCP/firmware changed. Keeper17975 still bounded
until~1027Z. Continue representative available discs afterward, not checkpoint.

## RESUMED2026-11-17 09:27Z — finish executable work, no checkpoint final

User reaffirms permanent continuation rule; root/project AGENTS and WORKFLOW
now explicitly require reviewing unchecked work and advancing next runnable
task. One missing external row never blocks independent work.061/060/062 are
closed, but014authored audio/title/Stop/replay and broader parity remain.
Actual phone/bridge connected; visible SageTV screensaver is NOT iOS lock.
New bounded keeper17975from~0927Z until~1027Z (TTY for gracefulCtrlC), no
automatic unlock. No active companion borrow/bookmark/OS setting change.
Production reconnect invalidated __iphoneGate.api; old150resource buffer is
stale. New transient observer captures NEXT production event request, retires
itself and rebinds test API without changing profiles.093010status now valid;
no runtime defect/extra controls inferred from stale helper404. Continue014.

## Current —2026-11-17 08:48Z

091926Z independent bridge readback verifies0owners/0lease/keep-awakeOFF,
encrypted connection/one bond intact. Watchdog teardown is complete; no
unscoped Stop/rearm, no unlock or settings change during closeout.

0918Z current closeout:061alignment/060native+optional EOF/062action feedback
all CLOSED. Available actual-phone Files/Home/reconnect/portrait-landscape
layout scopes recorded.13served/20stock/565manifest/20experience groups PASS;
bridge portable145files+native package hashes PASS.124completed owned raw
files/34,421,762bytes retired recoverably (root CLEANUP_REPORT). No publication
or commit. Keeper2755 interrupted0918Z; verify its30s watchdog retires owner,
do not claim graceful runner completion (no final keeper JSON was written).
No active companion borrow/bookmark/OS-setting change remains. Remaining full
parent023/WAN/gamepad/acoustic/all-disc requirements stay honestly unchecked.

0914Z latest: actual Home/Search re-entry returns852x393LANDSCAPE. Stage/GFX
fill viewport;32icons/44px/two columns/Video-Audio-CC neutral Back/keyboard
and original profile equality pass actual-page geometry (menu clicks synthetic,
earlier portrait opening/gear trusted BLE). OS rotation-lock is OFF as before.
No active temporary companion/profile/OS setting remains. Current actual
layout/recovery/Files scopes are complete; gamepad/WAN/HTTP-secure/acoustic and
broader all-disc/historical parity requirements remain separately unchecked.

091042Z OS orientation lock RESTORED OFF, native notification/icon verified.
Actual portrait32controls/44px/two columns and short Home/return plus longer
expired-session reconnect PASS to scoped results/WEB-023/
IPHONE_LIFECYCLE_LAYOUT.md. Rotation lock OFF does not itself generate a fresh
landscape sensor event; page remains portrait, not a new sensor-rotation pass.
Native top-right from-current down512 opens Control Center (use a point just
inside right edge); center-top opens notifications. Do not select notifications.

0855Z supersedes active062/borrow statements below: WEB-062 is CLOSED with
five real BLE control acknowledgements, Save7724ms/Resume7941ms/absence restored.
Second Start's immediate old browser picture is NOT settled-target proof.
085345exact browser profiles restore;0844Z public CAS checkpoint RESTORED.
No active companion borrow/bookmark remains. Continue023physical lifecycle/
orientation, compact evidence and owned-raw retirement. No checkpoint stop.

New0844Z optional companion borrow is ACTIVE: artifacts/active/WEB-023/
20261117T0844Z-companion-borrow.json. Original bookmark independently absent;
browser opt-in is the only normalized profile change. Restore this browser
profile plus the public CAS checkpoint after062 controls, not older restored
checkpoints. Keeper2755 is explicit/bounded until~0945Z;55070 ends~0848Z.
Pointer keep-awake still does not establish no-lock reliability.

060AND061are now closed intact in checklist ledger. Actual optional082525EOF
passes44samples: generation10→11, continuation5→6, FLUSH unchanged4, new ROOT
decoded/highlight aligned/no message/error. Compact060/061RESULT.md own proof.
Active WEB-062 fixes100ms optional action acknowledgement: actual Start
Feature plays but UI says unavailable. New action-only bounded HTTP wait,
unknown-vs-rejected/no-replay feedback and delayed-real-HTTP11checks pass;
20experience groups pass. Browser/build/normal-manager install and physical
save/resume/control feedback next. No Core/Extension production code edit.

All three companion borrows0720/0808/0823Z are RESTORED. Latest0823browser
profile equality082927Z verifies exact streaming/client/caption
state; public restore confirms flags/hook restored. No bookmark written yet.
Do not restore these completed checkpoints again. New borrow must use fresh
checkpoint and baseline absence proof. Keeper55070expires~0848Z; read actual
state and start only an explicit new bounded owner if testing outlasts it.

WEB-062 candidate is now installed through normal manager083756: main/experience/
SW062.1, WAR88c9b73f8b30c11fb790eae0d8e5b7d646f5b6219665874870910e6ef8b73cc3,
ZIP2837e7a67ea5e2e91e65caa790ce0fb4c815dd5c1574fc76e202a24433b2323e,
MD5ae84cc3bbd5fe55d40786028b2a024a4.11real/fake optional contract checks,
20experience groups,22DVD DOM/4mobile-experience/8PWA Chrome+WebKit pass.
13served-source/20stock checks pass; installer62879closed.084321exact-phone
approved reload passes. Targeted physical action
feedback/bookmark controls follow installation, no broad matrix repeat.

Actual native Files Share/Save/dismissal completed0832..0837Z through ESP32
mouse/UP512drag; one uniquely named test ZIP remains in Documents. Compact
results/WEB-023/IPHONE_FILES.md records scope (not an independent saved-copy
hash audit). No existing files/contacts selected. Raw native suggestions contain
unrelated OS details and should retire recoverably after compact review.

## Current DVD alignment dependency —2026-11-17 08:12Z

User points out yellow ROOT selection above text. This is a proven Web adapter
bug, not authoring: INIT1 is monitor16:9 (MiniDVDPlayer load/initDriver0), not
PAL. DvdSpuSession incorrectly uses576canvas over authored720x480. WEB-061
derives grid height from actual MPEG-2 sequence headers, including split PUSH
boundaries, retains geometry across cells and resets on a new disc. Focused
SPU6/6 (24geometry combinations)/protocol/TCP/FFmpeg6/6 pass; normal manager
081414is now installed with71package assets/207Java8classes/13served/20stock
proof. WAR3e922065f0ebcd2a4a581b481d171690ac60f16bad477da3aee779caf82af24e,
ZIP8d7a5ddff52a1a69823ca7d294eae7866eee861d3ccda1830a50e1540236249b.
Physical061PASS: actual canvas720x480/yellow4716pixels/first box100..140,
real BLE Down/native5 moves to148..188and visually encloses Languages; Up
restores first.082146five native DVD picture/SPU/Off/chapter/root rows pass.
061and targeted022cold/warm are moved intact to checklist ledger. Compact
results/WEB-061/RESULT.md retains hashes and scope.
No stock Core/authoring/FFmpeg edit. Finish it then resume optionalDVD/Files.

WEB-060 natural native Safari EOF gate080600PASS74samples/one real BLE Enter:
feature generation14→15, actual decoded ROOT/highlight4716pixels/no message.
That stock path uses native FLUSH (continuations0); it is NOT evidence for the
optional no-FLUSH branch yet. Real FFmpeg6/6 does prove queued continuation.
First helper080126failed observer Promise handling,080303attached after EOF;
those are test-oracle failures, not new playback defects. Corrected helper
releases its one input lease immediately and polls read-only status separately.

OPTIONAL borrow checkpoint artifacts/active/WEB-023/
20261117T0808Z-companion-borrow.json was RESTORED0813Z; exact browser profile/
caption/client equality verified081250before installation. No bookmark written.
Earlier0720checkpoint already restored. Do not restore either checkpoint twice.

NEW optional borrow0823Z is ACTIVE at artifacts/active/WEB-023/
20261117T0823Z-companion-borrow.json. Browser opt-in saved and exact fixture
loaded; no bookmark written yet. Restore this current browser profile plus
public hook/settings checkpoint before final teardown/install. Continue
physical optional controls/EOF, then Files/rotation/recovery without a stop.

## Actual DVD fixes/acceptance —2026-11-17 07:20Z

057/049/058/059available scopes closed in checklist ledger. Main058.1/
playback059.1/SW059.1, normal manager070742.13served/71package assets,
207Java8classes/20stock hashes pass, no restart/publication. Native Safari
subtitle-switch replacement was stranded at0 with buffered4..87s; one bounded
client trial restores9.18s on SAME producer. Production startup alignment is
fresh native DVD only, not TV/ongoing gap skip;52unit/22DVD DOM/26recovery pass.
Actual071508BLE/nativeDVD gate passes feature/SPU20452pixels/Off0/chapter/
root4716highlight-clear message with Extension OFF, observer/subtitle restored.

The optional companion attempt exposed WEB-060: native DVD next-cell bytes
remain queued after the previous decoder/browser ends without a native FLUSH.
073006 diagnostics and 072734 HDMI preserve the failure; the root SPU appears
over the last feature picture. A bounded client-adapter continuation is under
focused Java validation, NOT yet installed. Stock Core/FFmpeg are unchanged.
The temporary companion settings, hook and exact saved browser profile were
RESTORED at0734Z; checkpoint artifacts/active/WEB-023/
20261117T0720Z-companion-borrow.json records restoration. No bookmark write yet;
baseline absence was independently verified. Finish060 and optional acceptance,
then Files/rotation/recovery. Do not stop at this checkpoint.

## WEB-057 installed and physically verified —2026-11-17

Normal manager060221/main+SW057.1,13served assets and20stock hashes pass.
Exact MAIN-stage keyboard routing fix closes057: both engines14baseline/fix
rows plus affected input/browser gates; real BLE Enter now sends20 and enters
Settings. Original phone profiles unchanged. Compact results/WEB-057/RESULT.md.
Continue actual stock-STV049 and DVD/Files023, not another provider checkpoint.

## Actual ESP32-controlled continuation —2026-11-17 05:32Z

Phone/BLE/HDMI are resumed, not waiting for an operator to tap Play. Bridge
9f5d8327 qualifies scoped saved one-shot unlock; Home Search/Enter launches
the exact852x393standalone123c8282e1ee page. Real BLE long press, gear, settings
Back/neutral focus and Safari Play pass. Canonical fixture20905 STV-authority
CC1 after30s seek:60/60samples/fixed-width/upward text/full QSV. Paused
1000→700→1000Apply/exact original saved profiles pass. The formerly skipped
warm row now executes:50samples/41with text/235frames/9.83s/no error/fixed
columns. Real BLE calibration Play/Back passes, assigned src cleared/ready0/
paused/offset0, all saved profiles unchanged.12s HDMI+USB audio reproduces
~128–134ms early captured clicks; no acoustic claim/offset change. Compact
results/WEB-023/ESP32_PHYSICAL_CONTINUATION.md owns evidence and remaining
physical scopes. No Core/restart/publish or unrelated matrices. Remaining
native timeline/DVD/recovery/Files/rotation are next, not a provider stop.

## RESUMED —2026-11-16 21:32Z

User confirms ESP32controls working, phone on HDMI, explicitly requests full
Web Client tests using ESP32MCP and required bounded bridge changes. This
supersedes the phone pause below. Bridge0.4.0/011 preserves encrypted BLE bond,
until-Stop session/heartbeat and held-arrow movement; operator confirmed actual
mouse/keyboard. Use existing paired wireless exact-page observation with ESP32
BLE/MCP for trusted input (HDMI occupies phone USB); no direct PC-phone cable.
First live readback: authorized visible standalone WebClient3.3.0, exact phone
123c8282e1ee, saved-profile checkpoint captured through iphone-field-owner.js.
Stock232preflight:0recordings/one exact phone UI/0other connected clients,
20protected stock hashes PASS/no encoders. No restart/publication authorized by
this scope, no unrelated175/185/Android matrix. Continue full applicable phone
023/049/022 and shared browser controls; unavailable gamepad/WAN/HTTPS/OS actions
remain separate, not auto-PASS. Do not stop at bridge/provider checkpoints.

## PAUSED by user —2026-11-16

Offline follow-up is complete while PHONE access remains paused. WEB-056 layout
is now in the checklist ledger/compact CALIBRATION_LAYOUT.md. Saved12s HDMI
analysis finds5clicks100–135ms before red line (median135ms); capture differential
uncalibrated, no automatic offset change or acoustic-pass claim. Original clip/
log retained for comparison; derived/installer raw may retire. Exact-session
pause retirement returned0/0/0 at1794841938122ms, although page cleanup could
not attach. BRIDGE-006A source0.4.0/dashboard/97offline host checks/build ready,
NOT flashed/paired. No live phone connection, new server control or publication.
Next: deploy/physical BLE pairing when user returns, then remaining023/049.

User needs the phone; no further phone interaction until resume. WEB-056
calibration landscape clipping was reproduced in HDMI and production CSS
regression. CSS-only fix installed via normal manager145647;71assets/207Java8
classes/13servedassets match and20stock hashes pass. WAR efc7ed14 /ZIPc1dc44b2,
CSS/SW056.1, unchanged main037.3/input055.5/experience049.2.20ready/error layout,
8updated phone-usability and8PWA host rows PASS. Actual852x393 iPhone confirms
all5actions44px and visible; user taps Play, calibration time6.19→8.28 advances,
offset0/saved profile unchanged.12s HDMI A/V captured150424Z, now analyzed above;
do not claim audible synchronization. Pause page cleanup151125Z could not
attach (0expressions executed); do NOT claim calibration/menus closed by it.
No further phone actions; use only guarded exact-session server retirement.
If audio is still audible, user must close the Web Client. BRIDGE-006
user-requested BLE expansion now local/incomplete/unflashed, see its handoff.
Remaining backward/stock phone timeline, warm captions/rotation/DVD/recovery/
Files gates stay open. No Core/175/185/Android/publication change.

## Actual iPhone acceptance in progress —2026-11-16

User requests finishing all phone tests, not stopping at provider/question
checkpoints. Manager20261116.133942/experience049.2 is loaded;13served assets/
71package assets/207Java8classes verify. Main037.3/input055.5 retained. Actual
phone123c8282e1ee native HLS852x393/DPR3. WEB-049/IPHONE_TIMELINE.md records
trusted-user spinner and MCP21 snapshot: EventRouter waits UI lock while SageMC
links missing legacy IMDb DbObject. Owning SAGEMC-ART-001 migrates13 missed
artwork calls; manager SageMC0.1.1/loaded adapterc70387b5/STV0bbdf202 match.
After-update synthetic phone tap: actual native marker670ms, new frame2761ms,
exact accepted1267838ms. Backward/stock-STV phone rows remain open.

Actual landscape controls/settings/keyboard/source preservation, CEA startup/
30s seek/fixed-width upward text, paused-caption hold and paused700→1000kbps
full-QSV Apply pass. Exact original saved profile restored after normal Save
materializes existing companionDvd=false default. A test guard expecting true
skipped warm-after-quality sampling, not a production caption failure. CC Off
restored. WEB-023/IPHONE_ACCEPTANCE.md records all evidence/boundaries.

Current phone native iOS ZIP preview shows exported7KB diagnostics on HDMI.
User asked asynchronously to dismiss Back/X, optionally Save to Files. Exact
Web page remains listed but guarded evaluation cannot execute behind native
viewer: do not loosen access/replay export/claim saved Files. Continue available
independent checks meanwhile, then warm captions, backward/stock timeline,
portrait/rotation, calibration/teardown, DVD and recovery. No gamepad available;
HTTP lacks secure APIs; WAN remains separate, not synthetic passes. No175/185/
Android/Core/native/original FFmpeg change, commit or publication.

## WEB-037 home-Wi-Fi redraw accepted; WAN/other iPhone checks remain

User2026-11-16 reports "That looks fixes" following the second update. Record
the physical home-Wi-Fi SageMC symptom as user-confirmed, not a new independent
loaded-revision inspection or long-run/WAN pass. Its completed scoped entry
is in TASKS.md's ledger. Continue049/023 physical checks, then distinct037 WAN
acceptance; no replay of completed browser/backend matrices is needed.

User reauthorizes actual phone debugging: home Wi-Fi, long-press arrow controls,
selection moves but redraw is very delayed. This supersedes the earlier
user-owned-phone-only next-step restriction below, not other-device authority.
Baseline phone shows repeated1500ms frame gaps/rejected late ACKs, fast command
HTTP and100 pacing timeouts/1630 waits. Read-ahead candidate037.2 passed the
modeled WebKit322545 regression but user reload/actual revision inspection
proves it did NOT fix physical acceptance. Temporary existing-poll phone trial
improves first highlight to48/67ms and settled animation to282/290ms,26ACKs
accepted/original highlight restored. Trial globals auto-restored. Corrected
037.3 automatically uses finite polling on iPhone/iPad, cancels retired polls
and keeps next-poll Stop independent of compressed-image decode. No server
Java/Core/STV or saved-setting change. Manager055735 installed;71assets/207Java8
package and13served assets verified, stock20 unchanged. WAR272bedc8/ZIPef669e3f,
MD55c2e8463. Host WebKit iOS-policy touch rows pass,41native waits/0timeouts/
queue0/no errors. Final phone reload attempts060026/060138 find no inspectable
page before expression; that independent final phone check was not completed.
The subsequent user confirmation above supplies symptom acceptance only. See
artifacts/results/WEB-037/IPHONE_REDRAW.md for exact scope/evidence. Completed
47installer screenshots/17,829,119bytes retired recoverably to root deleteme.
Only approved exact phone123c8282e1ee stopped after fresh0recording/other-client
proof; independent post-stop activity is0/0/0. No175/185/Android mutation.

## Browser-first batch COMPLETE; physical iPhone handoff next

Current500 supersedes earlier checkpoints below. Stock232 normal manager
3.3.0.20261116.042532 / runtime3.3.0 / web055.5 is installed and qualified.
WAR770200b1 / ZIPb91a4b3b. Chrome043331Z and WebKit043448Z each pass17 actual
DVD rows including settled post-seek frames/matching SPU, native Time Scroll,
bookmark save/resume/clear, Off, exact restoration and unselected native
fallback. A null menu response no longer erases fresh truth; its1.5s bound
is never extended. SPU slots/HD flags, title-clock projection and bounded
read-ahead history are corrected without touching Core. Full compact proof:
artifacts/results/WEB-055/BROWSER_ACCEPTANCE.md.

WEB-050..055 available implementation/browser scope and Android003/005
available Linux scope are in their ledgers. Actual measured Web down/up plus
six negatives, source previews, native stock/SageMC timelines and diagnostics
retain separate evidence; no broad matrix replay. Build,5 SPU/native/wire,
17 input/12 mobile/8 PWA/4 DOM, package/13 served assets pass. Final20 stock
hashes, unchanged plugin engines/INI,0recordings/UI/clients/encoders verify
1794803800613ms UTC. No175/185/Pro/phone mutation or publication.

NEXT: user-owned iPhone HDMI checklist docs/IPHONE_HDMI_ACCEPTANCE.md; do not
operate the phone or certify native Safari/WAN/audio from host tests. Wider
WEB-020/021 parity, WEB-022 warm-caption cause and historical all-disc/Windows
rows remain honest separate work, not implied complete. Keep one small042642
JSON for an unproven transient read-only MCP TCP timeout; controls are never
replayed. Completed/corrected raw retires under root deleteme with compact
results and cleanup ledger. No task should stop merely at a provider checkpoint.

## Earlier continuation checkpoints (historical)

Current499 continuation:050/051/052/053/054 implementation/host-browser scope
and Android003/005 available Linux scope are now in their completion ledgers.
Actual measured Web down/up and six negatives pass both engines; see052
MEASURED_NETWORK, not just historical forced-recommendation proof. MCP20
bookmark inspection is installed/qualified, no playback dependency.
DVD title/chapter/bookmark/seek/menu/fallback pass both engines on032614 after
correcting TimeScroll10 (notTV15) and actual SageMC MediaPlayer OSD hints.
Title-SPU checks then prove missing slot/HD-flag interpretation and a~20s
decoder-versus-title cue-clock mismatch. Manager035137 fixes both; actual
Chrome chapter/title SPU pixels+Off pass, but combined seek/late-enable still
fails because repeated same NAV selection clears read-ahead cues. Candidate
040611/ZIP817089f5 adds bounded256-frame/4MiB SPU history, presentation-time
selection and idempotent NAV selection.5SPU/clock/native-wire regressions pass;
normal manager installation and final actual caption-after-seek gates continue.
Do not stop at a checkpoint. Raw055 failures remain active; corrected052/audit
raw retires recoverably with compact results. Stock Core/engines unchanged;
no175/185/Pro/iPhone mutation, publication or broad matrix replay.
Earlier497/checkpoint paragraphs below are historical and superseded here.

Continuation497: do NOT stop at the browser-forced-recommendation checkpoint.
Actual paced500kbps body transfers produce no automatic action on013345.
Bounded diagnostic snapshot proves intentPaused=false/rebuffering=true but
video.paused=true: main incorrectly ORs the internal reserve pause into user
Pause, resetting the network advisor. Candidate web052.2 separates these
states; explicit Pause/autoplay blockage still refuses changes, buffering
never qualifies an upshift.17 policy/47 playback/four browser viewport gates
PASS; package dcb0bb6f/normal manager022036 staged, installation/real measured
qualification ongoing. No Core/INI change or broad matrix replay. Continue
remaining052,055 and shared005 audit; physical iPhone remains user-deferred.

Browser-first acceptance COMPLETE to scoped affected gates. Chrome for Testing
153.0.8010.12 and pinned host WebKit pass actual232 startup/CEA/seek/source
images/full-QSV down/up frame ACK/abort/pause, BOTH native stock/SageMC timeline
markers, optional DVD/fallback and redacted report export. Local mobile/PWA/
recovery/ordinary subtitles/Teletext/DVB regressions pass. Final stock20 and
zero recordings/UI/NetworkClients/encoders1794794511433ms UTC. No runtime edits
after013345 installation; only test/docs/ledger updates. See compact
results/WEB-053/BROWSER_ACCEPTANCE.md and docs/IPHONE_HDMI_ACCEPTANCE.md.
Physical iPhone HDMI is now the user's next step; do not restart host matrices
unless their observation identifies an affected defect. Measured physical WAN,
native Safari/audio, Windows and all-disc certification remain distinct.
Older 'checks underway' text below is historical. No publication/commit/push.

Current browser-first candidate: normal manager3.3.0.20261116.013345 installed
stock232, no restart; WARc12694f8/package8eeccb72.71 assets/207 Java8 classes,
12 served assets and20 protected Core hashes match. Chromium014238Z actual
startup/seek/source-image/full-QSV handoff/recovery/pause and independent final
zero activity/preview retirement PASS; WebKit follows. Optional source-image
consumer cannot seek/start A/V and retires custody on source/seek/quality/STOP.
User will perform physical iPhone HDMI testing AFTER available Chromium/WebKit
gates; do not operate the phone or claim native Safari/WAN acceptance. Android
115/8f3e6c05 Non-Pro/Linux previews now pass all five affected scopes. See
results/WEB-053/PROGRESS.md. Historical checkpoint wording below is superseded
where contradicted; no publication or other-server/device mutation.

LATEST manager3.3.0.20261115.170738 installed stock232 (no restart),52.3 assets
byte-verified.51 handoff/10 options/13 policy/47 playback/four browser viewport
rows PASS. Actual host-WebKit171545Z1000->700->900 after real60s cooldown,
actual frame ACK/CEA/full QSV/saved ceiling/pause PASS;173044Z explicit abort
restore PASS.171302Z was a bounded headless-WebKit inspection stall before any
passing row; same-build rerun passed, not a diagnosed runtime encoder defect.
Source/build metadata now corrected; exact installed hashes/results in
results/WEB-052/PROGRESS.md. Android source consumer under qualification needs
optional atomic provider seek/commit lineage; no Android APK/install yet.
Physical phone/native Safari/WAN and remaining approved batch stay open.

LATEST2026-11-15: Web manager3.3.0.20261115.163819 implements bounded optional
handoff1, not the historical strict policy below. Real stock232 host-WebKit
20261115T165333Z presents a1000->700kbps replacement with captions/full QSV,
exact frame ACK and preserved settings;165632Z explicit candidate abort
restores original playlist/position/captions, followed by pause/resume.46 Java
handoff,26 native-seek,9 state,47 playback and11 policy checks pass.20 protected
stock hashes match; no restart/175/185/Pro/Android mutation. Actual physical
phone/native Safari/WAN, Android consumer and two-way policy remain open.
See results/WEB-052/PROGRESS.md for exact package/build metadata and test-oracle
corrections. Checkpoint is progress, not permission to stop the active batch.

Earlier checkpoints below are historical and superseded where stated:

LATEST provider checkpoint: FFmpeg19/handoff1 now manager-loaded on stock232;
five production API lifecycle rows PASS with SYNTHETIC presented ACK. Not a
browser/Android rendered/captioned handoff claim. Web still144638/earlier strict
policy; new Web consumer/owner and Android consumers remain open (orders473).
No changes to stock20 hashes/shared INI/engines, final0activity/encoders. Compact
FFmpeg results/REMOTE-001/PROGRESS.md retains hashes/results/limits.

LATEST user clarification permits one temporary replacement stream for a
producer-owned handoff; earlier single-encoder results below are historical,
not proof of the new behavior. FFmpeg candidate19 adds optional presented-
commit/abort/timeout; actual232 remains18. Web consumer/owner integration and
Android consumer/physical qualification remain open. Existing Placeshifter
live bitrate control found in source/MIM compatibility; GPU output-rate proof
is needed before enabling it. No new runtime installation/publication yet.

LATEST shared dependencies now manager-loaded on stock232: FFmpeg18 actual
revision1/seven provider gates pass, Extension29 actual Web profile/menu/button/
native-fallback six rows pass. Both guarded restarts independently0recordings/
UI/native clients; stock20 hashes and shared INI/engines unchanged, final0activity/
encoders. Web remains144638. See owning results/REMOTE-001/PROGRESS.md and this
project results/WEB-055/PROGRESS.md. Two-way quality/Android consumers and final
remaining DVD/phone gates are still open. No publication or Windows pass.

LATEST: stock232 manager `3.3.0.20261115.144638` now includes the newer Web
source described below, single-encoder handoff/previews/optional DVD consumer.
Real host WebKit20261115T145415Z six affected startup/seek/quality/full-QSV/
CEA/pause rows PASS,12 served assets and20 stock hashes match, final0activity/
encoders. No physical phone/WAN claim. See results/WEB-052/PROGRESS.md for exact
package hashes, settings, measured versus unknown timing and corrected autoplay
harness race. FFmpeg18/Extension29 not loaded; Android115 not installed. Batch
tasks remain open, especially two-way quality and optional shared consumers.

Current checkpoint2026-11-15: manager-loaded3.3.0.20261115.134153 on stock232
passed real host WebKit local seek30s, distinct requested/accepted/presented
state, session-only1000->700kbps full-QSV quality replacement, CEA captions,
pause/resume, stale producer rejection and unchanged defaults. All12 served
assets and20 protected stock hashes matched. Stock-STV native touch seeks
showed cursor520/491/503ms before video1522/1462/1428ms; raw run reports FAIL
only for final read-only retirement URLError, followed by independent0activity/
encoder and stock-hash proof. Do not rewrite that raw run as overall PASS.

Newer LOCAL source adds bounded previously-decoded-frame previews/EDL markers,
explicit optional Web DVD profile/actions, stage timing and single-encoder
quality handoff. These later changes are NOT installed yet. User forbids a
multi-rendition quality ladder: stop/confirm old producer before replacement,
keep published segments, expose any failed preparation/brief interruption.
Current policy remains default-off/downshift-only; two-way ramping unfinished.
Focused local single-encoder4/options7/DVD-client7/policy11 groups PASS;
candidate rebuild/latest browser/normal-manager installation and affected live
qualification remain required. Android source115 diagnostics compile/JVM pass,
but its APK is not built/installed. FFmpeg18/Extension29 are unpublished local
candidates, not server-loaded17/28. Windows stays deferred; stock Core protected.

Earlier task-addition checkpoint (superseded by current state above):

User approves all six plugin-experience tasks and ALL useful Android
transcoding/remote counterparts; Client Extension stays optional. Complete
cross-client ownership map: docs/SHARED_PLAYBACK_EXPERIENCE.md. Android Direct
is HLS-MPEGTS (not ordinary continuous TS), so evaluate its QSV/segment policy
separately. Existing MIM probe cache/Android callback diagnostics should be
reused, not duplicated. Android changes so far are task/handoff records only.

New Web candidate (NOT installed at this checkpoint) adds versioned cheap
source-owned state, asynchronous local timeline with requested/accepted/
actually-presented distinction, bounded history and default-off network
quality guidance/session reductions. Copy/DVD refuse adaptation; immutable
active options preserve captions/audio/track offsets and configured defaults.
Measured fragment-body transfer excludes producer first-byte wait and expires;
unknown native Safari timing disables automatic suggestions, not playback.
10 policy groups/45 playback tests/9 Java state checks/7 quality-option checks,
four Chromium/WebKit portrait/landscape timeline DOM rows and26 recovery checks
pass. Four settings-entry rows pass after correcting stale test navigation to
expand the existing phone gear. No physical phone/WAN claim. Build/package/
normal-manager install and real stock232 affected playback checks are next.
053 previews/markers,055 optional DVD integration and Android consumers remain
open; do not mark the batch complete. Prior manager123049 remains installed.

## WEB-049 active — STV cursor latency, not new-video latency

Latest2026-11-15: installed candidate is normal-manager3.3.0.20261115.123049,
not merely staged (MD5dfd5bdcb8775c3af705b30e66b071639). Native seek26 wire/
race/failure checks, protocol and frame-pacing checks pass. User explicitly
requires stock STV as well as SageMC; TASKS/WORKFLOW/root order updated.
Actual stock232 host WebKit SageTV7 TOUCH3 seek rows pass: position marker
569/497/496ms, replacement video1687/1529/1367ms. Full QSV decode/filter/encode,
new exact source anchors, advancing video, pause/resume, zero frame timeouts,
original SageMC restoration and owned UI retirement pass. Earlier mouse
marker305/243/208ms preceded video1343/1287/1199ms, but that run's10s cleanup
deadline failed before eventual retirement; do not call that whole run passed.
SageMC normal-tap mouse white handle1083/718/830ms preceded new video2506/
1955/2323ms. Latest strict SageMC touch3 rows PASS: white marker1011/836/938ms
before video2058/2163/4970ms. Fresh CEA startup/30s source seek/full QSV/pause
PASS. No theme-specific
production coordinates or STV edits. Timing correction in harness: Time Scroll
pins TimeScrollTime; previous gray/green edge was NOT the requested white
handle. Native placement, not browser Fill DOM geometry, establishes VideoOSD.
Invisible-OSD/preview attempts are rejected fixture setup, not runtime passes.
See results/WEB-049/PROGRESS.md; physical phone/WAN acceptance remains open.
Final20 protected hashes pass;0 recordings/UIs/native clients/encoders, only
canonical fixture20905 bookmark cleared.95 superseded captures recoverably
retired to root deleteme (37,292,308bytes);8 minimum open-comparison files stay
active. Root cleanup ledger/owning PROGRESS retain results and path changes.
No further deployment/restart/commit/publication this checkpoint.

Historical initial investigation (superseded by measured checkpoint above):

User confirms048 better but native cursor waits behind spinner. Investigate
tap→stock cursor/drawing independently of HLS first frame. Source inspection:
ordinary SEEK synchronously starts replacement under media-bridge monitor;
same media reader cannot answer following GETMEDIATIME until preparation ends.
Do not claim this measured cause until affected native timing is reproduced.
Prefer browser fix, then bounded owning-plugin correction; no guessed cursor,
Core change or MCP production dependency. Current phone123c8282e1ee is playing
Nightline25387. User now gives standing permission to stop this iPhone test
playback when needed, superseding initial keep-playing answer. Independent
recording/other-client guards remain. Owning TASKS contains race/failure/clock
acceptance criteria; no unrelated stop/restart permission is implied.

## WEB-048 complete to affected available scope —2026-11-15 UTC

User “Yes fix it” approved exact Nightline interruption. Independently verified
zero recordings/native clients and stopped only phone123c8282e1ee; normal manager
installed final048.2 as3.3.0.20261115.034144 without restart. Browser-rendered
native FLIP pacing corrects the producer/browser imbalance; lighter queue and
larger read-ahead trials failed and were reverted. Original4096/8MiB bounds,
independent media/input,1500ms timeout/close wakeup and legacy mode preserved.
Actual stock232/SageMC host WebKit and Chromium each pass11 timeline/redraw/
pause rows, including real forward30/60/back10/post45s-redraw20s canvas taps.
WebKit2.149–2.659s new video vs old6.755s/~10s; Chromium1.469–4.142s. Queued
0–65 commands/zero pacing timeouts; not an instant/universal speed guarantee.
Fresh CEA setup/new30s source seek/full QSV/probe reuse/pause pass. Focused
pacer/native-wire/protocol/11recovery/13startup/14auth/two-browser rendering/
orientation/26browser recovery PASS. Package70assets194Java8/11 served assets/
20 protected stock hashes pass; no Core/FFmpeg/settings changes. MD5
870fd230b4f64d09f4098f5e5b1964fe; full hashes/measurements in
artifacts/results/WEB-048/RESULT.md, superseding the historical PROGRESS.md.
Test setup corrected preview/initial Watch, EOF/TimeScroll-toggle and owner/
teardown failures; rejected attempts are not production passes. WORKFLOW and
owned fixture helpers preserve the repeatable procedure. Final0 recordings/
UIs/native clients/encoders, own fixture bookmark cleared. Resolved raw evidence
retires recoverably to root deleteme; compact result/root cleanup ledger remain.
Phone Wi-Fi pairing/RSD succeeds but0 pages are listed, so no expression or
physical iPhone acceptance this session. Reopen/reload the phone; physical
native-HLS/WAN remains WEB-023/037. Next037/020/021/022/023; no broad matrix
reset. No commit/publication. New source/tests remain untracked in the existing
dirty worktree: include them and regenerate the tracked manifest before a future
authorized commit/source release. Preserve unrelated staged changes.

## WEB-044..047 complete/installed —2026-11-15 UTC

Stock232 normal manager3.3.0.20261115.021832; package9c16f803...14d95, WAR
ce9641dd...50f0d, epoch1794708500, main/playbackJSweb046.1/CSS041.1. Full hashes
in results/WEB-044/RESULT.md. Actual1.001s regular-local transcode segments,
bounded completed-source embedded-probe reuse and startup-only readiness timing.
Copy/DVD pipe/concat/TS preserved, no production RAM switch. Real WebKit
first/repeat/stable4.669/1.762/1.815s; full GPU decode/filter/encode, advancing
video/zero reported drops. Synthetic160ms/4Mbps30s playback passes912 frames,
zero reported drops/first frame2.374s. Original network helper401 was missing
route.fetch HTTP auth, corrected only in exact-origin test helper, not runtime.
Visible CEA startup/exact30s source-replacing seek, cache hit/full-GPU and pause/
resume PASS.10 cache/34 command/43 playback/32 core/34 architecture/18 caption/
stock-state, streaming13/recovery26/PWA8,70 assets/193 Java8/package/11 served/
20 stock hashes pass. User approved exact phone interruption, no restart.
All own UIs/encoders retired,0 recordings; canonical fixture bookmark cleared.
Android STARTUP-001 callback control shows1339ms Push/2663ms Pull versus2691ms
250ms-buffer trial: no default/runtime change;136prefs/power restored, lease
inactive. Both Android orders467 updated. Other devices/servers untouched.
WEB-023 physical iPhone/native HLS/audible/WAN and037 STV timing remain separate;
no blanket matrix/physical-phone certification, commit or publication. Completed
raw task captures retire recoverably to root deleteme; compact044/047/Android
reports and source retain results. Reopen iPhone Web Client for user testing.

## Historical WEB-044..047 implementation checkpoint —2026-11-15 UTC

User authorizes all additional startup improvements/testing and exact phone
Nightline interruption for installation. Web candidate:1s actual segment target
for ordinary local transcoding (Copy/DVD pipe/concat/TS preserve cadence),
bounded64-entry completed-source embedded-probe cache with source/tool identity,
8KiB edge fingerprints, before/after mutation guard and independent tracks;
fresh sidecar/service discovery per call, no active/sample/failed cache.
Startup-only100ms readiness cadence/diagnostic phase timing; steady reserve,
45s deadline and recovery unchanged.33+ command/10 cache/43 playback/32 core,
34 architecture/18 caption selection/stock-state, streaming13/recovery26/PWA8
pass. Epoch1794708500/build70 assets193 Java8 classes candidate built, not yet
installed. Actual WebKit startup/CEA/seek/synthetic delivery gates next.
RAM comparison completes047: disk1s890/875ms vs RAM891/875ms; no useful gain,
retain production disk. Compact047 report; exact bounded benchmark dirs cleaned.
Android profile uses existing APK23/Non-Pro25 and stock232, checkpoint/awake
lease/finally restoration. Fixed old matrix activation's dynamic-vs-push false
mismatch (32 harness tests pass). Broad playback helper includes resume/fullscreen
waits, so profile now uses direct public nonblocking Watch plus actual renderer
counters; do not call old14..17s helper latency decoder startup. Driver active;
do not install/restart while its owned UI is running. No Core/plugin runtime
change outside Web candidate, no Android production change/publication yet.

## WEB-043 complete/installed —2026-11-15 UTC

User approved stopping exact phone Nightline test. Normal SageTV manager
installed3.3.0.20261115.013709, ZIPac743deb...9a69 (full hashes in CANDIDATE.md),
without restart. Actual bridge/ffmpeg.real command contains forced_idr1; first
segment now3.003s with1s keyframes, not old34.034s/one keyframe. Real stock232
host WebKit first/repeat/stable first frames4.787/1.956/2.902s versus earlier
8.069/22.331/8.984s single samples. Full GPU decode/filter/encode confirmed,
8s playback advances with244..246 decoded frames/zero reported drops. Visible
fixed-width CEA startup and after real30s source-replacing seek PASS. Focused
30 command/34 architecture/18 caption-selection/stock-state/build/package/
ten served assets/20 protected stock files PASS. Copy/TS/non-QSV unchanged;
DVD/current fallback command coverage only, not a new full disc matrix.
Native iPhone inspection discovered pairing but zero Safari pages; no phone
expression executed and no physical Safari speed claim. User can reopen the
Web Client to test. No tmpfs/Core/native/FFmpeg binary/settings/publication/
commit/other-server change. All owned UIs/encoders retired,0 recordings.
TASKS/root task/parity index updated; broader WEB-037/021/022/023 remain.
Compact results/WEB-043/RESULT.md supersedes pending checkpoints below.
Resolved owned raw captures retire to root deleteme with original paths.

The following WEB-043 sections are historical pre-install checkpoints,
not the current pending state.

## WEB-043 fix built; installation approval pending —2026-11-15 UTC

User authorized fix. Actual early bridge/FFmpeg command confirmed unchanged
GOP1;12s full-QSV A/B isolates forced_idr=1 (four3s segments vs one12s baseline;
closed GOP/frame-counter alone don't fix). Nightline read-only file succeeds
before/after with already-short3.5→3s first segment; no universal speedup claim.
StreamCommand now adds private IDR option only to QSV HLS transcode, not Copy/
TS/other encoders. Browser cannot fix unpublished bitstream boundaries, so
owning stock-compatible producer change is required, not Core/MCP/MIM rewrite.
30 hardware assertions/34 architecture/18 caption-selection/stock-state,
build70assets190Java8/package pass. Epoch1794706002; compact candidate report
artifacts/results/WEB-043/CANDIDATE.md records hashes. Production still042 with
old producer; candidate NOT installed or runtime-WebKit-qualified. Permission
asked to briefly stop exact phone Nightline test before manager update; no
answer yet, preserve it. Next install through manager then affected WebKit
startup/CEA/seek/segment gates. No restart/settings/other-server/publication.

## WEB-043 measured startup —2026-11-15 UTC

Production unchanged042. Actual stock232/host WebKit hls.js/MSE startup8.069s,
repeat22.331s, stable8.984s; GPU decode/filter/encode confirmed. Linux WebKit has
no Native HLS, so this is not physical iPhone/Safari evidence. Exact generated
playlist and ffprobe: first segment34.034s, only initial keyframe, later1..3s.
Investigate early GOP/IDR/timestamps/options; missing forced_idr is a hypothesis,
not confirmed fix. Repeat also observed first ready late despite earlier server
metric; don't call every22s encode time. /tmp HLS currently disk-backed btrfs,
no tmpfs; /dev/shm64M unsuitable. RAM requires bounded output/full-space handling,
not enabled. Own canonical fixture watched state reset only for repeatability;
phone session/settings untouched. All test UIs retired/zero encoders/20 stock
hashes pass. Compact results/WEB-043/RESULT.md and three active JSON comparisons.
No production code/install/restart/publication; WEB-043 cause/candidate remains
open. Tests use host SSH inspector, not missing container paramiko/known_hosts.

## Latest WEB-042 installed candidate —2026-11-15 UTC

Closure update: user confirms landscape fix works. WEB-042 moves to checklist
ledger. Physical acceptance is user-reported, not an automated post-update
phone capture. WEB-037 stays open. Startup-speed question reviewed read-only;
no startup settings/code changed. Earlier pending details below are historical.

Normal stock232 manager3.3.0.20261115.004318; mainJSweb042.1/CSS041.1.
Bounded16-entry native-size history resizes retained/delayed screen composition
surfaces, preserves handles/native metadata and ordinary textures/small targets.
Actual phone landscape popup clipping captured before; exact stale allocation
is inferred, not traced on phone. Both-engine synthetic before fails/after
passes, focused renderer/orientation/layout/recovery/DPI/phone/PWA/unit/package
checks pass. Real stock232/host WebKit SageMC Options draws fully after multiple
portrait/landscape sizes; not physical phone proof.70 assets/190 Java8/package,
10 served assets/20 protected hashes pass. No restart/Core/settings edits,
publication or commit. Approved exact phone test stopped with zero recordings;
own manager retired. Phone reload failed before evaluation when authorized page
disappeared; asked user reload/open same landscape popup. HDMI only color bars.
WEB-042 remains open for physical check, WEB-037 timing independent. Compact
artifacts/results/WEB-042/PROGRESS.md has hashes/evidence/scope; unique before
and open-failure evidence remains active, redundant raws retire recoverably.

## Latest WEB-040/041 installed —2026-11-14

Stock232 manager3.3.0.20261114.183215, CSSweb041.1/mainJS unchanged039.1.
Back one column left/blank arrow gap; tools transpose Android's utility rows
into two four-row columns: info/diag/test/stats above gear, Aspect/Video/Audio/
CC left. No scroll-under-gear; all32 controls44px/nonoverlapping/hit-tested.
Portrait left margin preserves both columns onscreen,040 wrapped rows retained.
Eight geometry/four high-DPI/56 mobile/eight PWA rows and70assets/190Java8/
embedded WAR/catalog pass. Ten served assets match/20 protected hashes intact.
Epoch1794680909;
WAR114c825de0f5e6287519c12bbf300cdcdf64ad077480c6429997503559c16dc9;
ZIP1ceec4ccab2f2344d64bdde60a2ec428820d74964fb9775ae183bee129181be2.
Earlier loaded CBS Evening News was left alone;18:28/18:31Z exact phone UI
has no media,0 recordings/connected clients. Retired only known idle test UI,
stage independently passed idle guard, normal manager install/own client quit.
No restart/Core/native/stock FFmpeg/settings edits, other servers, publication
or commit. Actual phone probe not run: refresh/reopen, no physical acceptance
claim. Compact results/WEB-040/041 retain boundaries; completed raw captures
retire recoverably to root deleteme. WEB-037 rendering/WAN backlog stays open.

## Previous WEB-040 local checkpoint —2026-11-14

User refines Back position: bottom band shifts44px left, leaving the bottom
Left-arrow column empty before Down. Gear/single tools column/44px retained;
below360px reserve four wrapped rows to avoid pad/page overlap. CSSweb040.1,
mainJS unchanged039.1; epoch1794680580. Eight geometry/four high-DPI/eight PWA
rows, build/package70assets/190Java8 pass; reviewed safe-area WebKit screenshot.
WAR3800af13d693a8fd2c330c6b685f13cb9bc450642a80320d0e7b3b0a11a65948;
ZIPea86b84eca306841839d56ba5f417f3282fe8f81239b52bac9b2c7f3d82ff285.
Stock232 status18:24Z:0 recordings/0 connected clients but exact phone UI
123c8282e1ee has CBS Evening News loaded. Asked permission to disconnect that
test UI before manager install; no answer yet. Do not infer idle or stop it.
Current served installation remains039142917, not040. No live/Core/settings
changes. Remaining rendering/media/physical-phone boundaries unchanged.

## Latest installed WEB-039 —2026-11-14

Stock232 manager3.3.0.20261114.142917, CSS/mainweb039.1. Gear is first in bottom
band; eight tools expand in one column above it, with bounded scrolling rather
than wrapping/shrinking. Back x equals D-pad Left x in landscape and wrapped
portrait.44px/focus/parent return/default collapse/desktop restoration pass.
Eight geometry/four high-DPI/56 mobile/eight Exit/eight PWA rows, syntax/build/
70assets/190Java8/embedded WAR/catalog pass;10 served assets match/20 protected
stock hashes unchanged. Epoch1794666369;
WAR3391daaaf67dcfefdd09626d662ef26faf7557ef4fd3cadb5105577072f7620b;
ZIP988f3db3e03827569899bf3c17039d648935b15daa28af07ab5ceb7195358591.
Approved exact idle phone UI retired; independent zero recordings/UI/clients
before staging and after own manager retirement. Initial404 during expected
WAR reload resolved; do not replay installation. No restart/Core/native/stock
FFmpeg/settings/other-server changes, commit or publication. Phone must refresh/
reopen; emulated WebKit screenshot is not physical phone acceptance. Compact
results/WEB-039/RESULT.md; reviewed completed raws retire to root deleteme.
WEB-037 rendering/WAN backlog and prior media matrix boundaries stay open.

## Previous WEB-038 installed —2026-11-14

Stock232 manager3.3.0.20261114.132449, CSS/mainweb038.1. Phone left rail starts
collapsed to one gear; tap toggles original eight tools, one portrait column/
two short-landscape columns,44px targets. Escape collapses before closing
overlay; settings Back restores expanded origin/focus; desktop unchanged.
Eight geometry/four high-DPI/56 mobile/eight Exit/eight PWA rows pass;70 web
assets/190 Java8/package/catalog,10 served bytes/20 protected hashes pass.
Epoch1794662554, WAR19cf636f4c83d766f00df6872e52802b385d7bea590167ed95ce73d8fec7d870;
ZIP8a37dcb523f505da8c179782207a3fe287810508f4f80a84dc81607abec08353.
Android gear vector/source hashes/license carried in both provenance records;
SW caches new vector. Independent zero recordings/UI/clients before staging,
normal manager install/own client retired; no restart/Core/native/settings/
other-server changes, commit or publication. Actual phone discovery unavailable
before expression; user must refresh/reopen. Do not claim physical phone pass.
Compact results/WEB-038/RESULT.md; raw completed captures retire recoverably.
WEB-037 STV/WAN backlog remains open; no renderer/media matrix changes here.

## Latest WEB-037 installed —2026-11-13 UTC (Nov12 Chicago)

User approved brief test-stream interruption. Independent preflight01:20Z
found0 recordings/UI/connected clients; no phone stream needed stopping.
Normal manager installed3.3.0.20261113.012040; eight served assets match and20
protected stock hashes unchanged. No restart/Core/native/stock FFmpeg changes.
mainweb037.1/CSSweb036.1; same local ZIP178d042cfa59a2defd4e539b9de08c52e7ca6383046a1bb583c1140e1c90cb00/
WAR8a59e1dfd337584052dab7ef8d091d7fe8959133ef47c1109783f24719fe33aa.
Initial served404 occurred during manager's expected WAR reload; subsequent
served proof passed. Own manager client retired, no other sessions touched.

Actual phone discovery still unavailable before expression; cannot remotely
reload/reconnect or claim a fresh phone document. User must refresh/reopen.
Post-install real host WebKit proves loaded037 and timing counters, NOT a speed
pass: image decode max3024ms, frame queue10592ms/4984 queued in sampled stats;
zero final server queue, peak197, no JS errors. This confirms browser backlog
remains in host testing despite fewer forced timer yields. No physical iPhone/
WAN fix certification. Retain minimal JSON timing evidence and keep WEB-037
open for actual reproduction/correction; do not blame only VPN or count the
installation as issue closure. No settings changes/publication/commit.
Compact artifacts/results/WEB-037/PROGRESS.md updated; reviewed manager PNGs
retire recoverably to deleteme, open profile/discovery JSONs remain active.

## WEB-037 local checkpoint before installation —2026-11-12

User clarifies STV animation/rendering slowness on cellular/VPN, not local icons.
Need measure real phone input/network/decode/draw costs, preserving high-DPI
clarity. At23:24/23:35Z paired
Wi-Fi endpoint unavailable before any expression; requested unlocked Wi-Fi
phone. No live reproduction/root cause/production fix claimed. New bounded
iphone-render-start/result helpers trace Canvas methods/rAF for3.5s, restore
automatically, and refuse navigation with any video source. No helper executed
on phone yet. browser-render-performance.py on Chromium/WebKit production
renderer/synthetic transport:24 frames, zero stage layout reads, transparent
pixels correct; repeated black-matte layout hypothesis not confirmed. Do not
optimize that path based solely on static suspicion. Stock232 read-only activity
shows one recording plus phone live TV; leave intact. Current installed build
remains036184029; no server/phone/settings mutation or publication.

Local037 implementation now built/tested: count-only yield128→1024 retains8ms
budget, complete ordered graphics and sharper pixels. Burst3072 small commands
uses4 timer yields vs25 before. Bounded diagnostic/stats counters separate
input queue, successful HTTP ack/failures, frame queue and decode stalls.
Both engines verify identical transparent/color pixels, compressed-image
dependency ordering and immediate media Stop during deferred decoding.2
orientation/4 high-DPI/8 geometry/26 recovery/11 P14/15 graphics smoke pass.
Early new-fixture failures were legitimate toolbar resize frames racing exact
flip counts; fixed fixture geometry, not a runtime workaround. Stock LAN
Chromium/WebKit profiles were baseline036, own absent diagnostic identities/
no media/four Down focus only/finally stop. Native idle UI contexts persist
after socket stop; distinct identity per engine fixed safe next-run refusal.
No takeover of phone. Next flip after key is NOT causal command-to-photon proof.
WebKit host1987ms decode/276ms draw outliers need physical confirmation; do not
blame only VPN or claim local scheduler change fixes all WAN sluggishness.
Epoch1794526959; WAR8a59e1dfd337584052dab7ef8d091d7fe8959133ef47c1109783f24719fe33aa;
ZIP178d042cfa59a2defd4e539b9de08c52e7ca6383046a1bb583c1140e1c90cb00.
69 assets/190 Java8/embedded WAR/catalog pass. Requested permission to briefly
disconnect user's phone test stream for install; no answer yet, do not assume
approval. Current recording left alone. Stock232 still036184029;037 is local
only. Compact artifacts/results/WEB-037/PROGRESS.md; physical WAN task open.

## Latest WEB-036 installed —2026-11-12

Stock232 manager3.3.0.20261112.184029, CSS/mainweb036.1: Help now immediately
before Keyboard; bottom row expands rightward for13 controls without rail/
D-pad overlap. Actual iPhone18:42:33Z fresh revision/snapshot852x393 verifies
Help118/Keyboard162 at y329, all31 targets44px, saved480p/1000 unchanged.
Eight geometry/Help/desktop, eight Exit and eight PWA rows plus build/package/
eight served assets/20 protected stock hashes PASS. Approved phone session
stopped/retired and idle independently verified; no restart/Core/native edit,
other device/server, commit or publication. Compact artifacts/results/WEB-036/
RESULT.md retains hashes/scope; reviewed raws retire recoverably to deleteme.
Broader WEB-020/021/022/023 unchanged; desktop placement and X semantics retained.

## Latest WEB-034/035 installed —2026-11-12

Stock232 manager3.3.0.20261112.182557, CSS/mainweb035.1/parserweb034.1:
fixed32-column608/upward CR rows, bounded708 roll-up,16s source-clock stale
clear/resume (paused captions retained), explicit X confirmation/default Cancel
vs green Hide. Actual iPhone initial old033 document explained unchanged user
retest; explicit approved-source reload proved034. Actual caption DOM x248/
w355.84/h44.33 constant across two texts/video37.52..89s; HDMI upward rows
reviewed. Actual X dialog x202/y108.5/w448/h176, both buttons44px, Cancel focus/
menu/media unchanged. Physical confirmed Exit and natural silent-commercial
are NOT certified. Caption silence injection was not run (endpoint discovery
failed before mutation). Broader WEB-020/021/022/023 remain open.

23 caption unit/8 browser, affected caption-family gates;8 Exit/56 mobile/8 PWA/
8 geometry/26 recovery/input pass.69 assets/190 Java8 classes/embedded WAR,
8 served bytes/20 protected stock hashes pass. Epoch1794507720; final ZIP
e2a7d31757e67e700770fbf50b47df3974bb54d2a75000d3a3e826152fa337b7;
WARc7b85fa2ce48f0a5eb241ef2e6e83670cc19a3c3211203a051b73d3a5c194bdc.
Only approved exact phone/owned test sessions stopped; no restart/Core/native/
stock FFmpeg edit, other devices/servers, commit or publication. Compact results
WEB-034/035 record evidence/limitations; completed/corrected raw captures retire
recoverably to root deleteme per cleanup ledger. No settings cleared/changed.

## Latest WEB-033 installed —2026-11-12

Stock232 manager3.3.0.20261112.165714, CSSweb033.2/mainJSweb033.1 now carries
supplied phone reference layout and right-shifted D-pad. Actual iPhone852x393
Up/Center/Down and Page/Last common x749; Left705/Right793,44px fully visible.
Eight-tool rail and12-button bottom band unchanged by axis refinement; saved
480p/1000 retained. Final actual WebKit screenshot reviewed; eight affected
browser geometry/safe-area/portrait/desktop-restore rows and PWA gates pass.
Seven served assets match/20 protected hashes unchanged, no restart/Core edit,
publication or commit. Compact artifacts/results/WEB-033/RESULT.md records
hashes/scope and commissioning idle-UI guard race; reviewed completed raws
retired recoverably to root deleteme. Broader WEB-020/021/022/023 remain open.

## Latest WEB-030/031/032 installed —2026-11-12

Normal stock232 manager3.3.0.20261112.162446 carries safe initial Back focus,
Auto device video-height option and requested phone overlay. Existing controls
moved (not cloned); Info/video-info/diag/test/stats left column; Home/Menu/Back
after bottom forward controls, portrait navigation wraps, desktop restored.
Actual852x393 iPhone:31 controls,44px; Info x59/y4, navigation x514/558/602 y329.
Screenshot reviewed. Final phone usability gate confirms neutral focus,44px,
full value/category54px, parent return and no media change. Auto label1080p
from screen393x852 DPR3; loaded-source Apply changes480p to source720p under
1080 cap (no upscale), browser paused/native gesture boundary. Restored saved
480p/1000kbps verified after final reload. No audible-playback/touch claim.

7 Auto/9 P12/19 profile/15 input groups,6 phone geometry/breakpoint,4 Settings
entry,8 viewport/56 mobile/8 PWA/13 streaming gates pass. Outdated streaming
test expected invalid CEA5 rejection; existing explicit-caption policy clamps
to4. Corrected that test only, no production caption change. Initial desktop
restore-order failure caught/repaired by sorting original nodes in document
order. Final69 assets/190 Java8 classes/embedded WAR/catalog MD5 pass; seven
served assets byte-match and20 protected stock hashes unchanged, no restart.
ZIP4e45df93f94248916634d7d8bc47254bb88c0c5266a3a752eefe2b58f13a226e;
WAR876c6ca7f7f684dcdb0bae15b22a797ed5ebf4dc07c4dd4698eec2e47a30e3ad.
Epoch1794500427, CSS/mainweb032.1, streamingweb031.1. No publication/commit.
Compact results/WEB-030..032 retain proof; retire reviewed completed raw files
recoverably to root deleteme. WEB-020/021/022/023 remain their original scope.

## Current WEB-027/028 installed —2026-11-12

User chose browser-only: no native iOS companion/ScreenCommand dependency.
Stock232 manager snapshot3.3.0.20261112.155136 installed with user approval to
stop exact Nightline phone session. No recordings/other clients; no restart.
All6 served HTML/CSS/main/core/app/support assets byte-match local source;
20 protected stock files unchanged. Higher-density automatic UI raster is
bounded at2x/1920x1080; fixed choices unchanged. User confirms STV graphics
look much better. Controls default hidden with explicit persisted/profiled
App fallback. Actual phone hidden/synthetic long-press open/close verified.
Affected browser/core/profile/PWA/orientation/recovery gates pass; compact
WEB-027/028 records retain exact build hashes/scope. No publication/commit.

WEB-029 complete: actual saved/form/requested/effective1000kbps match. Full-QSV
Nightline480p23.976 video samples860..1114kbps; output about1293kbps includes
192kbps AAC and TS overhead. MIM/real receive-b:v1000k/maxrate1250k. Reapply
existing1000 via normal input handler replaces HLS owner/resumes current
position with Applied result; new stream packets confirm target. No bitrate
bug demonstrated; no runtime rate-control change or saved setting change.
Compact results/WEB-029/RESULT.md and bounded commission-bitrate.py retain
reproducible supported-MCP/read-only process/packet inspection.

## Current WEB-026 landscape correction —2026-11-12

Manager snapshot3.3.0.20261112.153547 now installed, served assets byte-match,
20 stock-protected hashes unchanged, no restart/Core change. Epoch1794497600,
mainJSweb026.1, CSSweb025.1. Actual phone DOM/canvas fill852x393 but old surface
394x794 was still drawn/copied at portrait bounds (bounded trace proved both).
Client resize now retains handles but resizes exact old-screen render targets
and maps only their exact whole-allocation copies to the main screen. Small
surfaces/textures/partial copies untouched. Both engines repeat orientation
PASS;22 display/16 policy/26 recovery gates PASS.69 web assets/190 Java8 classes
and embedded WAR verified. Fresh actual phone landscape now has nonempty
pixels across all sampled columns0..808, versus empty right side before.
User rotated portrait/back landscape and confirmed **Now fills the screen**,
providing physical return proof separately from a clean landscape reload. No
active media/settings change or publication. Compact WEB-026 result retains
proof and current boundary; Controls button question answered as fallback,
not an instruction to remove it. WEB-025 recovery physically confirmed.

## Current WEB-025 foreground recovery —2026-11-12

User physically closed/reopened updated app and confirmed automatic recovery.
Reproduced actual393x793 standalone “Browser GFX queue overflow” with hidden
Reconnect; fixed entirely in browser. Stage recovery44px retry/diagnostics,
one foreground health/recreation attempt, healthy session preserved, BFCache/
non-BFCache returns and stale-generation/single-flight guards. No key/seek/
playback replay or retry storm. Normal stock232 manager151605 snapshot,
CSS/JS token3.3.0-web025.1, epoch1794496520. Served bytes match local source;
20 protected stock files unchanged; no restart or publication.26 recovery,
7 P13,11 P14,8 viewport gates and21 host wireless tests pass.69 packaged web
assets/190 Java8 classes verified, embedded WAR identical. Actual phone
synthetic return and controlled one-shot failure/retry pass before user's
real close/reopen confirmation. No active media source or preference change.
Bridge optional --page-id2 explicitly selects the previously observed exact
authorized page if hidden duplicate inspection times out; still requires
unique ID, no foreign inspector, fresh visible nonce. Never guess/replay.
Compact report artifacts/results/WEB-025/RESULT.md. Wider WEB-023 remains open.

## Current physical follow-up —2026-11-12 14:43Z

WEB-024/BRIDGE-002 actual source→package→manager→phone iteration now PASS.
Guided Access enabled manually by user; HDMI/WebKit stayed visible past5min
with no host power leases (last expired14:13:10Z). Use that mode for testing;
system-only assertion failed/display assertion remains unproven, not a fix.
Physical iOS still gave37.3px native selects despite min-height44px. Explicit
height44px, native appearance retained, fixes it; focused8 viewport rows pass.
New manager snapshot3.3.0.20261112.143931, CSSweb024.2, epoch1794494100;
served HTML/CSS/JS match exact source and20 protected stock hashes unchanged.
Actual393x793 phone gate: Back/Transcoding/player/Save/Apply44px, category54px,
full selected value, full-width picker, parent/icon focus and media preservation.
Bridge handles two exact authorized pages via sequential read-only visibility
and real socket teardown; wait for fresh release listing before reattach.
20 host wireless regressions pass. Broader WEB-023 physical finger/audio/PWA/
controller rows stay open. No media started/preferences saved/Core changes/
server restart/publication in this follow-up. Older checkpoint below is history.

2026-11-12 WEB-024 current checkpoint: phone393x852 portrait/852x393 landscape
real baseline;31 overlay icons reachable44px, portrait settings31-37px targets
and clipped values corrected. Compact scrollable category strip/full-width
portrait fields/44px controls/wrapping long values; preferences untouched.
8 new usability/56 mobile/8 PWA/22 display plus affected input/profile helpers
pass. Development manager snapshot3.3.0.20261112.140124, packageSHA256
5d3ee744553a795bc37f5eeebb40b7ec0b99093f7501d80d269cd58f859d4b9f installed,
all three served source asset hashes match. The first same-epoch WAR install
stayed stale even after independently idle authorized232 restart; advancing
SOURCE_DATE_EPOCH and normal manager reinstall hot-redeployed correctly.
All20 stock-protected files verified; final0recordings/UIs/clients, no encoders.
No live WAR/cache edits, no175/185/Android changes, no publication/commit.
Owning compact report artifacts/results/WEB-024/RESULT.md preserves evidence.

Bridge now uses paired Wi-Fi independently of ESP32; HDMI connected too.
Physical post-update acceptance remains open: phone locked (system-only power
assertion did NOT prevent it); RSD authentication succeeds but no authorized
page visible. User must unlock/reopen before a real layout/gesture/audio pass.
BRIDGE-005 display-specific temporary lease experiment is not qualified yet.
Do not claim a ping or completed assertion request prevents iOS Auto-Lock.

2026-11-12 connection update: sibling ESP32-IOS-Bridge (renamed2026-11-16) is adopted and ready
for physical iPhone troubleshooting through native ESP32 `.113`/CH343 COM7.
No direct iPhone-PC connection, Windows Apple/Inspect or Android ADB is needed.
Its WORKFLOW.md/Handoff.md and compact BRIDGE-001 result preserve37 live checks
(21 MCP/7 dashboard/9 synthetic real-page menu/reload),20 local tests and real
WebKit screenshot inspection. No app video source was active; WEB-023 physical
audio/gestures/Home Screen/controller and BRIDGE-002 real defect/deploy cycle
remain open. No Web runtime/Core/server installation change or publication was
made for this takeover. Use the normal plugin manager for subsequent app fixes.

## Current request: full current-Android/HTML5 reconciliation

2026-11-10 Chicago/2026-11-11 UTC: WEB-018/019 implementation and available
local/stock232 gates complete; WEB-020/021/022/023 stay open. Real manager
installation is3.3.0.20261111.053116, runtime3.3.0, ZIP SHA256
0df4f6eed6c2dacd985442dccfa8132f6d7d29aa5b0990be7a3598e7fbad6fec.
Uncommitted development, NOT published. Stock Core/native/original FFmpeg
remain unchanged; normal plugin-manager hot deployment, no SageTV restart.
175/185/Android/Pro unchanged. Compact results: artifacts/results/WEB-018/019.

Current268-preference Android source inventory/disposition is NOT a parity
certificate. `audit-android-features.py --require-reference` checks live source;
single-repo CI validates recorded inventory with explicit live-unavailable label.
Implemented:31-icon overlay/Last/spatial focus, compact scoped menus/back,
toolbar/IME ownership, editable press/hold/repeat/gamepad/touch mappings, actual
MiniClient PWA/Apple/standalone target/install help, wake lock/Media Session,
explicit Native HLS, typed per-client transcode Apply,25ms±4s audio slider,
FFmpeg-generated A/V calibration, Auto/YADIF/BWDIF server filters/profiles,
English-first virtual CEA/TT/DVB, exact-UI stock state and caption-only epochs.

Final local56 Chromium/WebKit viewport and8 PWA cases pass (synthetic Sage
transport); display22/lifecycle7/support UI11, input15/profile17, caption policy18/
clock5 and full non-browser Java8/deterministic package validation pass. Pinned
WebKit helper passes in existing dev container at
/workspace/release-manifest/scripts/setup-webkit.sh, NOT arbitrary /project.

Real stock232 Chromium: full-QSV MPEG-2/AC-3 playback, visible CEA before/after
seek and three more64/12/47s generations, paused quality Apply/resume, phone
Audio layout and actual A/V generation(+500ms) pass. BBC Breakfast has TT+DVB;
stock STV CC1→TT,CC2→DVB,Off all pass without A/V restart. ITV Chase has DVB
only; unavailable TT is correct. Affected authored DVD menu/still/Down/Select/
return pass, NOT title/256x/all-disc certification. Real report ZIP parses and
hash verifies after nested-crypto regex corruption was corrected by bounded
JSON redaction. Stock20/20/final0activity/no encoder children verified.

Fixes found by real testing: saved manual CEA was not applied on connection;
explicit no-descriptor CEA now says manual/not-discovered (Auto never invents
UK CEA). Exact state reader rejected real colon-formatted session IDs; fixed
with regression. Report regex replaced only the first part of nested crypto
objects, leaving stray braces; structural redactor/depth/size limits now pass.

Next: WEB-021 title Time Scroll/held chapters/true high scan and safe active-DVD
converter replacement; WEB-022 earlier unproven warm-resume CEA timeout has not
reproduced on current repeat-seek run, so preserve minimum evidence; WEB-023
physical iPhone Home Screen/audio/background and real gamepad. Do not claim full
Android/native-HDMI or all DVD/growing/live parity. Windows stays deferred.
No publication without final approval; a public version must supersede private
3.3.0 snapshots (e.g.3.3.1). Devmode remains false: stage preserves other entries
in normal local catalog and uses separate INTEGER date/time version components.
Manager/source helpers never copy WAR/Core/registry directly. Clean completed
raw captures to root deleteme; preserve minimum open-failure evidence.

## Previous3.2.30 release state (historical)

## 3.2.30 publication checkpoint

2026-10-21 PLUGIN-RENAME-001: canonical GitHub/local source is now
opensagetv-vibe-WebClient-Plugin. PACKAGE_ID follows the source name; installed
plugin IDs, WAR, routes, settings and immutable beta3.2.30 remain unchanged.
Local Java8/JDK11 build, package and automated source/stream contracts are the
affected validation; no new binary publication or physical DVD claim.

2026-10-09 reconciliation: existing public beta3.2.30 and both merged catalog
entries independently verify against downloaded assets/GitHub SHA256 and
catalog MD5. Runtime/package inputs have no newer source changes; no binary
version bump. WEB-017 closes; WEB-014 and all field rows remain open. Historical
approval/pending-publication text below does not override this current state.

The user explicitly approved creation of the public
`opensagetv-vibe/opensagetv-vibe-web-client-plugin` repository and initial
plugin release. The source/privacy audit found no embedded credentials or
private network paths. Complete local Java, JavaScript, deterministic package,
generated fixture, DVD/caption/recovery, and Chromium validation passes.

The public package requires OpenSageTV Vibe FFmpeg Plugin 0.1.4 or newer and
uses its `SageTVTranscoder` bridge. Stock `Sage.jar` and stock SageTV `ffmpeg`
remain unchanged. The release is a beta because the explicitly open physical
long-run, complete DVD-title, Safari, and additional-device rows remain open.

# Historical handoff — v3.2.29 DVD startup recovery fix


## Active OpenSageTV Vibe 3.2.30 work

The supplied `SageTV-WebPlayer-Local-Plugin-v3.2.29-P14-DVDStartupRecovery.zip`
was imported as the baseline. The project now uses the common Vibe root
workflow and requires the platform-matching OpenSageTV Vibe FFmpeg Plugin.
Production transcoding resolves that plugin's `SageTVTranscoder` bridge; stock
`Sage.jar` and stock `ffmpeg` remain unchanged.

Local build/validation and `.232` commissioning are complete for all currently
runnable non-DVD rows. The exact-path authored Vibe DVD now starts hardware
HLS, renders its background and SPU highlight, enters Languages, handles DVD
Return/DVD Menu, and repeats the root-to-submenu path without a browser error.
Generated forced-hardware failure also proves final software fallback waits for
input EOS instead of timing out a valid short cell. Exact results and the still
open title/chapter/audio/subtitle, Stop/replay, physical/menu-less disc, and
long-run rows are in `docs/VALIDATION-3.2.30.md`. Do not publish the plugin or
public catalog entry until the user gives final approval.

## Historical 3.2.29 field fix

The 2026-09-26 field diagnostic showed MiniDVDPlayer pushing/draining MPEG-PS while the browser had no HLS session. DVD startup previously lacked the staged runtime fallback used by ordinary HLS. 3.2.29 adds full-hardware -> encode-only -> software retry and a bounded 16 MiB startup replay buffer. `tests/DvdStartupFallbackSmoke.java` deliberately kills the first full-QSV-style DVD start after bytes are consumed and verifies recovery at fallback stage 1 with playable HLS.

## Field symptom and root cause
- v3.2.27 starts DVD HLS playback with hardware transcoding, but a real DVD menu can show only the colored SPU/button highlight on a black background.
- The menu video is commonly a one-picture MPEG-2 cell. The browser previously sampled the `<video>` element only when SageTV issued FLUSH. By that point the short HLS cell can already be ended/cleared, so the background frame is lost while the independent SPU overlay remains.

## 3.2.29 fix
- Cache decoded DVD frames per native DVD generation while they are actually available.
- At FLUSH/freeze, stop sampling that generation and promote the cached frame to the retained DVD still canvas.
- Keep the prior retained menu background across SPU-only/no-video replacement generations. A cache miss never paints black over a valid retained frame.
- Hide the retained frame only after the replacement DVD generation produces a real decoded frame.
- Native freeze events now include the DVD generation; diagnostics add `dvdMenuFrame` generation/cache/promote/miss/visible state.
- DVD hardware decode/VPP/H.264 encode and AAC output from v3.2.27 are unchanged.

---

# Handoff — v3.2.27 DVD hardware HLS transcode startup fix

## Field failure and root cause
- The 3.2.26 capability fix worked: stock SageTV selected MiniDVDPlayer and pushed MPEG-PS into the browser MiniClient.
- Field diagnostics showed `dvd.active=true`, about 4.8 MiB pushed, the 4 MiB ring almost full, but `stream=null` / no HLS session.
- Root cause: `buildDvdHlsCommand()` appended FFmpeg hardware-decode input options after `-i pipe:0`. FFmpeg input options must precede the input, so the hardware DVD converter could terminate before producing an HLS segment.

## 3.2.27 fix
- Emit QSV/NVDEC/VAAPI/D3D11VA/DXVA2/VideoToolbox decode options before the DVD MPEG-PS input.
- DVD always uses H.264 video + AAC audio output; it never inherits ordinary-media `Video processing = Copy`.
- Preserve the browser encoder selection for DVD (Auto/QSV/NVENC/VAAPI/AMF/VideoToolbox/Software).
- Expected successful field diagnostics: an HLS session appears with `dvd=true`, `encoder=h264_qsv` (on the reported Intel system), `hardwareDecode=true`, `decodeAccelerator=QSV`, `hardware=true`, and `playlistReady=true`.
- The existing stock-JAR native DVD capability role, STV caption control, SPU/menu handling, and bounded push/drain protocol are unchanged.

---

# Handoff — v3.2.26 native DVD role default fix

## 3.2.26 field fix
- The native DVD wire/HLS/SPU implementation already existed, but capability negotiation still defaulted `sagetv.webplayer.nativeDvdProtocol` to false from the old P07/P08 development gate.
- Stock SageTV could therefore reject DVD playback with `ERROR (-19): There is no MediaPlayer that can playback the selected file` before any DVD media commands reached the plugin.
- Native DVD role is now enabled by default: `INPUT_DEVICES=IR,KEYBOARD,TOUCH,TV` and `PUSH_AV_CONTAINERS=MPEG2-PS`.
- `-Dsagetv.webplayer.nativeDvdProtocol=false` remains an explicit rollback/troubleshooting switch.
- Browser mouse input remains available through the web input endpoint; omitting `MOUSE` here is only the SageTV player-role negotiation signal.
- STV caption control from 3.2.25 and full hardware transcoding from 3.2.24 are unchanged.

---

# Handoff — v3.2.25 STV-controlled browser captions

## 3.2.25 field fix
- Stock STV/SageTV caption authority now uses the STV `VIDEO_CC_STATE` as the control plane while rendering CEA-608 locally in the browser.
- This fixes the field case where the SageTV playback menu showed `Captions (CC1)` but the web MiniClient displayed no captions, while explicit local CC1 worked.
- `VIDEO_CC_STATE=0` disables/clears the browser decoder; states 1..4 select CC1..CC4. Property-absent peers retain the existing CC1 fallback.
- Diagnostics report `browser-local-stv-controlled`, the observed STV state, and resolved CC service.
- Hardware decode/VPP/encode work from 3.2.24 is unchanged.


Hardware-first transcoding now attempts both hardware decode and hardware encode on NVIDIA, Intel/QSV, VAAPI, AMD/AMF and Apple VideoToolbox. NVIDIA/QSV/VAAPI also attempt GPU-resident deinterlace/scale where FFmpeg exposes a tested filter chain. If full hardware startup fails, HLS/fMP4 retries the same hardware encoder with software decode/filtering before libx264. Diagnostics now identify decode accelerator, GPU filter use and fallback stage.

For the reported Alder Lake-N case, expected successful diagnostics are `hardwareDecode=true`, `decodeAccelerator=QSV` (or VAAPI), `hardware=true`, and preferably `hardwareFilters=true`.

---

# Handoff — v3.2.23 real-parameter MPEG-2/HLS A/B test

## What changed

v3.2.23 keeps v3.2.22 ffprobe→FFmpeg probing and explicit Copy behavior, then tightens the MPEG-2 compatibility path around the supplied 1280×720p59.94 broadcast example. Progressive sources no longer receive an unnecessary `yadif` filter when Deinterlace is Automatic, and Source FPS/Source resolution continue through H.264 fallback unchanged.

`/codec-test.html` adds two synthetic fixtures generated from one source matching the known recording parameters: MPEG-2 Main 1280×720 progressive 60000/1001 fps, ~6.3 Mb/s video, English AC-3 5.1 384 kb/s and Spanish AC-3 stereo 192 kb/s. Test D uses `-c:v copy` plus AAC stereo audio conversion. Test E uses the exact same source, H.264 video at 1280×720p59.94, and AAC stereo. The original A/B/C controls remain.

## Field test

Open `/SageTVWebPlayer/codec-test.html`, regenerate the fixtures, run all tests, and compare D/E. On normal playback, use Compatibility — HLS + Copy with fallback OFF to prove native Copy behavior, or fallback ON to verify same-position H.264 recovery. Export diagnostics afterward; v3.2.22+ should report `probeMethod=ffprobe|ffmpeg` and the actual source codec.

## Version

3.2.23. Stock Sage.jar remains unchanged.

---

# Handoff — v3.2.22 ffprobe → FFmpeg source-probe fallback

## What changed

v3.2.22 keeps the v3.2.21 Copy passthrough behavior and fixes source metadata discovery when `ffprobe` is not installed alongside FFmpeg. The probe path now tries `ffprobe` first and automatically falls back to parsing bounded `ffmpeg -i` input metadata. Diagnostics report `probeMethod` so field tests can prove which path supplied the source codec.

- `videoMode=copy` now means: attempt `-c:v copy` for `0:v:0`, preserve source resolution/FPS/interlace, and let FFmpeg/HLS plus the browser determine compatibility.
- `videoMode=auto` remains conservative and unchanged.
- Explicit Copy is also allowed when ffprobe cannot identify the source codec.
- The browser's zero-dimension compatibility fallback is no longer MPEG-2-specific; any explicit HLS Copy session can fall back to H.264 at the same position when **Allow fallback** is enabled.
- The legacy `mpeg2Copy` status field remains for diagnostic compatibility.

## Test target

For a clean forced-copy test use **Player = Compatibility — HLS**, **Video processing = Copy**, Source resolution/FPS, and Deinterlace Auto/Off. Disable **Allow fallback** temporarily if you need to prove whether the browser itself decodes the copied codec.

## Version

3.2.22. The isolated `/codec-test.html` page remains available.
