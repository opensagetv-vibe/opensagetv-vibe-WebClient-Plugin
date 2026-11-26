# Browser settings and playback statistics

The Web Client uses compact General, Playback, Transport, Input, Diagnostics
and Recovery tabs. The tab strip scrolls horizontally on narrow screens;
titles stay on one row. Existing
controls are moved, not copied, so saved values, validation and handlers remain
authoritative. Keyboard, touch and remote shortcuts select the owning tab.
Left/Right, Home and End navigate the tab strip. Save/Apply remains available
on Playback and Transport. Long static explanations and duplicated dropdown
values are removed; dynamic status/errors and a concise report privacy notice
remain. Native pickers retain complete choices; no setting values are renamed.

```text
General
  Browser/PWA display, portrait spacing, keep-awake, Reload webpage
Playback Settings
  Browser speed / Video display and placement / SageTV UI resolution
  Audio track, language, delay and A/V sync
  Broadcast CC / File and DVD subtitles / Optional DVD navigator
Transport Settings
  Browser delivery: Auto, MPEG-TS/MSE, HLS/MSE, Native HLS
  Fixed Transcoding Settings
    Processing, Hardware Encoder, Maximum and Minimum video bitrate
    Automatic Bitrate Adjustment: Off / Stream Switching / Prefer In-place
    Video height, FPS, keyframes, deinterlace, fallback
    Audio codec, bitrate and channels
  Browser buffering, startup segments and target
  Unified graphics compatibility
  Save for next recording / Apply now / Load defaults
Input and Remote
  Key, hold, repeat, touch and gamepad mappings
Diagnostics
  Statistics graphs / Statistics information
  Report download/share/server destination, profiles and tests
Recovery
  Restart audio / stream / Reset browser settings
```

Browser-compatible output still requires the existing FFmpeg plugin. Android
Push/Pull/SMB and original-stock-FFmpeg choices are not invented for the browser.
Hardware names remain shared, but browser decoding is browser-managed; absence
of a hardware/software decoder observation remains Unknown. Optional Client
Extension features remain explicitly negotiated and are not required for menus.

The single adjustment selector maps to the existing adaptiveQuality and
runtimeBitrateControl values. No extra competing saved flag is introduced.
Minimum/Maximum and shared MIM's buffer-report controller remain unchanged.
Off uses Fixed Maximum; Prefer In-place falls back only through the established
qualified handoff policy when in-place control is unavailable. Test actions are
under Diagnostics rather than ordinary transport configuration.

Display and browser-buffer choices retain their immediate behavior. Save keeps
next-playback defaults; Apply now restarts only this media stream with its
existing observed position/pause guards. Unified graphics requires reconnect.
Opening and navigating settings alone does not save or restart.
Load defaults edits the draft; Save/Apply is still explicit. Existing browser
keys, identity and credentials are preserved on upgrade.

## Independent statistics

The existing graph icon toggles bars; the information icon immediately to its
right toggles text. Both on show the full view; both off hide it. Either click
keeps the long-press menu open. The toolbar Buffer info action retains a combined
on/off shortcut. Existing saved showStats=true migrates to both views; explicit
new independent choices survive reload and profile export/import. There is no
Graphs only label. Targets and published reserve are not measured network speed;
unknown CPU/decoder/bandwidth observations are not fabricated.

## Keeping a non-live reserve

HLS/MSE normally loads continuously toward the existing selected target. For a
server-confirmed completed source with more published media, an idle loader can
be woken earlier below80% reserve after2s without append/read activity. The
existing8s wake cooldown and20s healthy in-flight request allowance remain.
Live, unknown, DVD and native Safari do not receive that earlier wake policy;
no new timer, seek, encoder or parallel download worker is introduced.

MPEG-TS/DVR lazy loading now refills at no less than80% of its existing maximum,
while retaining any earlier existing target-minus15s threshold. Thus30s refills
at24s instead of15s, whereas180s retains its165s threshold. Maximum storage,
startup, pause and live-edge-chasing policy are unchanged.

Memory-pressure reductions remain authoritative. Native Safari owns its decoded
buffer and cannot be forced full through JavaScript. A persistently insufficient
remote connection still needs a lower bitrate or enabled shared-MIM adaptation;
neither a permanently full buffer nor constant network traffic is guaranteed.
