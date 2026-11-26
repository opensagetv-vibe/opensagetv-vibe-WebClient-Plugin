# Mobile Vibe client modernization

WEB-018/019, 2026-11-10. Reference: current sibling Android source/dev,
especially navigation.xml and ActivePlayerAdjustmentsDialog, not the historical
0.5.95 snapshot. Keep independent Web Client versioning; do not label browser
engines as Android Media3/IJK or claim their hardware APIs exist in Safari.

## Implementation scope

WEB-041 replaces039's scrolling column with two four-row columns, transposing
Android's utility rows: info/diagnostics/test/stats above gear and Aspect/Video/
Audio/CC immediately left. Both end above gear, so CC remains visible and
hit-testable. Portrait reserves the left column; all44px targets retained.

WEB-040 refines039: Back/bottom band shifts one44px column left, leaving the
bottom Left-arrow column empty before Down. Bottom gear retained. Very narrow
portrait reserves four rows to avoid overlap; tools layout superseded by041.

WEB-039 refines038: gear first in bottom row, one scrollable column above it
on every phone orientation (Back alignment superseded by040). All original
44px tools remain reachable by touch/keyboard without moving the STV viewport.

WEB-038 supersedes the always-open phone left tool rail only: one gear toggles
the original eight tools, initially collapsed; short landscape uses two columns,
portrait one. Keep44px targets, toggle/Escape/focus/parent return, bottom Help/
Keyboard and right D-pad. Desktop remains unchanged. This is a local browser
control; it neither emits SageTV commands nor modifies streaming settings.

WEB-036 refinement: Help is now immediately left of Keyboard in the phone
bottom band. The remaining controls shift right to fit13 buttons without
moving the tool rail/aligned D-pad or reducing44px targets. Help drawer and
focus return remain intact; X stays top-right with WEB-035 confirmation.
Original desktop Help placement restores across the breakpoint.

WEB-033 operator layout reference supersedes the older phone arrangement below:
video info/diagnostics/test/stats/aspect/Video/Audio/CC down the left, Keyboard
then transport/Home/Info/Menu/Back along the bottom, arrows bottom-right with
page controls above. Keep original31 icons and44px targets. Reserve safe-area
space for the right pad rather than overlap it with the transport row; narrow
portrait wraps controls and places the pad above the bottom band. Desktop
arrangement and saved settings remain unchanged. Up/Center/Down align with the
Page/Last column; actual landscape iPhone x749/44px, Right ends837 within852px.
Verified stock232 manager165714; compact artifacts/results/WEB-033/RESULT.md.

Earlier WEB-032 arrangement (superseded by WEB-033): Home/Menu/Back sit after the transport controls; Info/video
information/diagnostics/test/stats form the left column, Info first. Narrow
portrait wraps the navigation group to retain44px targets; desktop retains
its previous arrangement. Settings opens on Back, without entering a picker.
Automatic maximum video height shows the physical device limit, keeps Auto
portable and resolves existing supported server heights only at start/Apply.
It does not upscale smaller sources or discover independent iOS HDMI output.

External HDMI boundary (user chose browser-only,2026-11-12): fill the viewport
provided by Safari/PWA and render sharper bounded high-DPI UI, but do not claim
independent full-TV display resolution or removal of OS mirroring bars. A
separate native UIKit display scene is required for the whole app on HDMI;
no ScreenCommand dependency or native companion was authorized. Reference:
[Apple external displays](https://developer.apple.com/documentation/uikit/presenting-content-on-a-connected-display).

- One key owner: editable/IME/native controls, local modal, then SageTV input.
  Toolbar focus must not disable remote arrows. Local overlay arrows navigate
  visible icons geometrically; Enter activates only the focused local control.
  Cancel held commands on blur, hide, modal open and connection retirement.
- Current Vibe icon ordering, Last between page controls, comfortable touch
  targets and responsive portrait/landscape layouts. Compact grouped settings
  return to their parent/focused icon rather than dismissing all menus.
- Manifest and Apple metadata belong on miniclient.html, which is the PWA
  launch target. Reuse existing owned icons. No native app wrapper or app-store
  requirement; Safari Share > Add to Home Screen launches standalone. HTTP LAN
  can be usable as a home-screen web app, but service workers/install prompts/
  wake lock and other secure-context APIs require browser support and HTTPS
  (localhost exceptions do not make a remote LAN IP secure). Do not weaken TLS
  or authentication. Installation can have separate cookies/storage; sign in
  again if required. Offline shell is not offline SageTV/media playback.
- Transcoding is per session through the existing FFmpeg Plugin bridge. Copy
  does not mean GPU encoding. Apply preserves the observed position and pause
  intent; reject stale sessions instead of replaying on another recording.
  Missing transcoder and unsupported browser codecs remain explicit failures.

## Validation boundary

WEB-025: actual iPhone close/reopen automatic recovery confirmed by user after
stock232 manager151605 update. Expired foreground session recreates once;
healthy session retained, failed attempt offers reachable stage retry and
diagnostics.26 mocked-transport Chromium/WebKit rows and actual phone controlled
failure/retry pass; stable identity/preferences preserved, no key/seek replay.
This is not seamless media restart or general lock/background audio acceptance.

2026-11-12 WEB-024 physical baseline393x852/852x393: portrait selected values
clip inside native pickers, three category rows consume space, and Back/actions/
selects measured31-37px high. Focused correction uses a horizontally scrolling
category strip, full-width portrait fields,44px controls and wrapping long-value
notes while preserving native pickers and stored option values. No media Apply,
preference migration or changed SageTV native coordinates merely for opening a
menu. Phone output aspect/resolution by itself is not a clipping defect.

Physical follow-up now PASS on actual393x793 phone after manager snapshot
3.3.0.20261112.143931/CSSweb024.2: explicit select height44px is necessary
because native iOS ignored min-height. Native picker retained; full-width,
wrapping value, single category strip, Back/focus and media-state preservation
verified. User-enabled Guided Access kept the display visible beyond5min.
These synthetic operations on real phone are not physical touch/audio/PWA/
controller acceptance. See WEB-024 compact result; WEB-023 remains open.

Target affected input/UI/profile/session tests and browser viewport/device
emulation, then unchanged-stock232 service/playback/transcode tests. Chromium
mobile emulation is not an iPhone; Playwright WebKit is not physical Safari.
Real Home Screen install, native HLS audio and background/lock-screen behavior
remain device acceptance if an actual iPhone is unavailable. Do not rerun or
close unrelated caption/DVD/receiver matrices merely because the UI changed.

## Full-current-client comparison (WEB-020)

`scripts/audit-android-features.py --write` pins every current preference screen,
the navigation layout, active-player dialog and CaptionSlotPolicy in
`docs/parity/CURRENT_ANDROID_INVENTORY.json`. Its check detects source drift;
inventory is NOT certification. Android-only settings are adapted to browser
capabilities rather than copied as inert controls. The existing WP01..17
backlog retains unpassed browser/media/platform acceptance.

The current comparison has already driven virtual DVB slots, English-first
language/type ranking, exact-current-stream STV state via stock public API,
caption selection without A/V re-encoding, and separated native/file subtitles.
Source-adapter and real field gates remain necessary; no all-format claim.

The unified environment's optional WebKit setup is
`bash /workspace/release-manifest/scripts/setup-webkit.sh`; `/project` can be
another invoking component. It reuses pinned
web-python/Playwright, leaves ADB keys/server untouched and validates launch.
WebKit's Linux test engine uses its own GStreamer libraries; deployed media
conversion still uses FFmpeg/MIM, not a GStreamer replacement.

Primary platform references: [WebKit home-screen web apps](https://webkit.org/blog/13878/),
[Apple web-app configuration](https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/SafariWebContent/ConfiguringWebApplications/ConfiguringWebApplications.html),
[Apple home-screen app storage](https://developer.apple.com/videos/play/wwdc2023/10120/).
