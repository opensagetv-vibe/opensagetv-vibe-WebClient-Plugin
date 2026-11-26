# P12 report — audio, playback controls and quality-policy parity

Version 3.2.15 adapts browser/FFmpeg-supported portions of the Android audio and quality policy without claiming Android AudioTrack/HDMI APIs.

- Audio selection is deterministic: explicit track wins; otherwise preferred-language primary/default audio is scored above commentary, narration, descriptive-audio and visual-impaired tracks. Missing-language fallback is saved as best/default, first, or strict failure.
- Audio track IDs are session-only. Language/fallback/delay defaults persist across recordings.
- Signed audio delay is -4000..+4000 ms in 25 ms steps. Positive means audio later. Audio copy remains strict and is rejected when delay/channel conversion is requested.
- Rapid delay/track/quality edits are debounced for 450 ms before Apply-now stream rebuild. Rebuild uses the current absolute position and existing pause intent while keeping the MiniClient GFX connection alive.
- Effective status separates requested/effective encoder, software/copy decode, filtering, hardware encode/decode and fallback detail. Software decode/filter + hardware encode is not called end-to-end GPU.
- Video bitrate, keyframe interval (1..10 s), B-frames (0..3), resolution, FPS and deinterlace are encoder-only controls. Video copy ignores bitrate/GOP/B-frame settings.
- Browser-local Video speed supports0.5/1/1.5/2x, per recording. Actual phone
  rates, Pause/reset and file-clock agreement pass WEB090. Ordinary stock Pull
  SetPlaybackRate instead becomes a seek; it is not advertised as qualified
  native rate support. The media protocol handler's bounded forward contract
  remains distinct. Reverse/frame-step stay unsupported and unadvertised.

Current2026-11-19 manager022105/main-playback-SW090.1 is qualified for this
local rate scope; compact `artifacts/results/WEB-090/RESULT.md` records original
boundary, exact package, both-engine guards and real phone/affected DVD proof.

Field-only boundaries remain real receiver/ARC audibility/latency and unchanged broadcast PMT/channel-layout transitions.

2026-11-19 bounded source-change continuation: WP12-001 now closes its primary/
fallback/actual output acceptance using the original phone/static language
cases plus a generated CRC-valid PMT/layout/lateNAR fixture in both host engines.
Compact AUDIO_TRANSITION.md distinguishes18functional assertions, a Chromium
cleanup-query timeout and independently confirmed eventual retirement. This is
not unchanged-broadcast/growing-live inventory refresh or receiver/ARC proof;
WP11/WP12-007 and the unclassified operational observation remain separate.
