# Shared Web / Android playback improvements

Current ADAPT-001 / WEB-127 / HLS-005 supersedes the historical measured-network
policy below: one optional FFmpeg/MIM Java controller owns buffer-only decisions
for both consumers. Startup min/max, subsequent reserve/eligibility reports,
producer-output health and existing rate/frame-ACK paths are shared; no measured
bandwidth prerequisite. MCP-ADAPT-TEST-001 adds exact-session leased override/
clear so the same MIM targets can test either client. Historical passes below
remain evidence of their recorded builds, not qualification of this new policy.

User-approved scope2026-11-15: evaluate ALL applicable Web043..055 changes for
Android transcoding and remote use, not just browser controls. This is an
ownership/compatibility map, not a second task list or certification claim.
Authoritative tasks remain Web050..055 and Android EXPERIENCE-001..005.

Current audit500: Android003 previews and005 applicability are COMPLETE to
available Non-Pro/Linux scope, not physical WAN/phone/Windows certification.
Android artifacts/results/EXPERIENCE-005/RESULT.md records043..055 disposition
and actual Direct source0/42s independently decoded first segments, full VAAPI
processing and2219/2437ms readiness. Web's forced-QSV-keyframe correction is
not blindly applied to a different Direct command; no Direct QSV claim follows.
Android002's actual measured down/up/failure/fallback/caption/seek/pause gates
and five preview consumer rows retain their separate compact evidence.
Web050..055 affected browser batch is now complete on manager042532/web055.5:
Chrome/WebKit17-row optional-DVD acceptance includes settled cue-after-seek
timing/restoration/native fallback. Web-only bounded menu-state freshness and
SPU composition do not replace Android native clocks/commands. User-owned
iPhone HDMI and distinct physical-WAN/historical parity remain open.

| Improvement | Android applicability and existing evidence | Owning boundary |
| --- | --- | --- |
| QSV first independently decodable segment (043) | Direct uses bounded GOP30 without the Web forced-keyframe request. Actual source0/42s first segments have a key packet and independently decode four frames, full VAAPI, ready2219/2437ms. No Direct QSV certification or forced-IDR default change. Push/Pull do not wait for HLS publication. | FFmpeg/MIM owns mapped encoder policy; Web owns its HLS command. |
| Short segments (044) | Compare Direct startup/seek before changing its2s segments. Continuous TS has no such segment gate. Preserve subtitle PIDs and live/growing handling. | Existing FFmpeg Plugin Direct session service, not a second producer. |
| Completed-source metadata reuse (045) | MIM already has a completed-file probe cache and bypasses active files (`sagetv_ffmpeg_mim.cpp`). Compare identity/invalidation/bounds rather than adding another Android metadata cache. | Existing MIM cache; Web's embedded inventory cache stays browser-service-local. |
| Separate startup readiness / ongoing reserve (046) | Android STARTUP-001 already measured first-frame callbacks: cutting500ms to250ms did not help. Preserve those defaults. Review Direct publication/attach independently. | Existing player callbacks and FFmpeg/MIM producer. |
| tmpfs (047) | Isolated comparison showed no useful gain; no production RAM switch for either client. | Container storage only if a later measurement justifies it. |
| Rendered-STV frame pacing (048) | Android has a different native graphics reader/renderer, not the Web HTTP GFX queue. Reuse diagnostic concepts; do not add browser acknowledgements to stock MiniClient. | Browser bridge/client only unless Android evidence identifies its own defect. |
| Fast accepted seek vs displayed frame (049..051) | Android already has stock-native clock/seek custody and bounded callback traces. Extend those callbacks; do not transplant the Web HLS bridge or replace Android clocks. | Each client, with optional existing provider state. |
| Network quality (052) | Current Direct24/Android115 qualify measured Media3/legacy down/up, affected GSY recovery, actual-frame ACK, failure/seek/STOP/native/Copy and settled captions. Web actual measured down/up plus six negative profiles pass Chrome/WebKit. Saved defaults remain unchanged. Physical WAN/growing-writer/resolution acceptance stays distinct; Android adaptation is bitrate-only. | Shared FFmpeg Plugin Direct service; client policy/explicit opt-in. |
| Previews / markers (053) | FFmpeg24 bounded source-image/cache/expiry provider passes; Android115 Non-Pro/Linux affected Media3/legacy/Copy/GSY/off rows pass. Web053 consumer is installed for actual Chromium/WebKit gates. Preserve existing Comskip/chapter navigation; source images never seek or start another playback stream. Physical phone/WAN remains separate. | Shared FFmpeg/MIM provider; each client's optional UI. |
| Phase diagnostics (054) | Reuse Android's existing callback ring and on-demand `MediaTransportDiagnostics`. Requested, locally accepted, producer ready and renderer presented are different observations. No continuous background player polling. | Existing client diagnostics + provider status, bounded and redacted. |
| Optional DVD integration (055) | Android already negotiates the Client Extension's navigator/transform lease. Web should consume the same owner with version/per-load custody; no second navigator. | Existing optional Client Extension and FFmpeg/MIM. |

## Optionality and fallback

Android must never depend on this Web Client WAR, its HTTP endpoints, or MCP.
Missing, disabled, old, incompatible or failing optional services leave the
established native stock path available. Capabilities are explicit/versioned;
an accepted request is not proof of a presented frame. Normal playback never
uses test controls. No stock Sage.jar, FFmpeg or bundled native is modified.

For Web050..052 the existing MiniClient bridge owns its browser producer and
therefore exposes its own state and session-only quality operation. Android
must use its existing native callbacks/shared Direct provider, not call that
Web-specific service. Shared policy invariants should match; HLS, continuous
TS, native Push/Pull and rendered graphics are not interchangeable transports.

## One steady-state stream, bounded producer-owned handoff

Latest user clarification2026-11-15 permits a temporary second producer while
switching streams. This supersedes the earlier strict one-encoder constraint,
not the prohibition on a permanent pre-encoded rendition ladder. The existing
FFmpeg/MIM owner reserves a bounded replacement, keeps old alive until the
client reports presentation from the EXACT new lease, then retires old. Timeout,
failed preparation, stale ownership and explicit abort clean only the candidate;
capacity refusal leaves existing playback alone. One pending replacement and
a finite deadline prevent accumulation. Client source/seek/STOP supersedes it.
Clients measure existing transfers, not bandwidth-test transcoders.

Historical FFmpeg18 revision1 and Web144638 used break-before-make; those
results prove that earlier behavior only. Installed FFmpeg19 advertises the new
Direct handoff1 contract; API gates pass with synthetic ACK, not Android video.
Web manager163819 now has its own optional owner-managed handoff1: real host
WebKit captioned/full-QSV switch uses actual frame ACK, and explicit abort
restores the original. Physical phone/WAN and Android acceptance remain open.
The new Direct
qualityHandoffRevision1 is a separate optional contract; old /quality callers
must not silently acquire acknowledgement obligations. Readiness/API acceptance
is NOT displayed video. Implementation/consumer/physical gates remain open.

Legacy Placeshifter provides another possible optimization: MiniPlayer measures
Push delivery/client buffer and FFMPEGTranscoder writes `videorateadapt <delta>`
to one running patched FFmpeg process. Its implementation changes encoder bitrate,
not resolution. MIM already forwards this optional control and its compatibility
layer updates bitrate fields, but that is not proof every GPU encoder honors it.
Qualify actual measured output bitrate, timebase/captions and recovery per encoder
before preferring this route; bounded replacement remains the fallback. No stock
Core, original FFmpeg, shared INI or proprietary firmware modification is needed.

Web170738 implements default-off bounded two-way policy: an increase needs
ten spaced samples with sustained measured headroom,
a longer stability window than a decrease, a user-selected ceiling, a bounded
session change budget and the same bounded-handoff/position/caption custody.
Unknown native-Safari bandwidth cannot be treated as positive headroom.
Host-WebKit1000->700->900 after actual60s cooldown with frame ACK/CEA/full QSV
passes, using explicitly synthetic recommendations, not measured WAN. Policy
unit tests cover measured headroom/ceiling/hysteresis/budget; physical phone/
WAN and Android two-way consumption remain open. No live encoder reconfiguration
or all-device resolution claim follows from that gate. Copy stays copy.

## Focused validation

Compile/unit/source-contract/packaging gates precede affected stock232 browser
and Non-Pro rows. Include rapid/superseded seeks, pause, captions, source/STOP,
Copy/DVD refusal and missing/old/off providers. Preserve saved settings and
stock hashes. Actual phone/WAN and physical playback are separate from mocked
Chromium/WebKit checks. No blanket replay of unrelated matrices or publication.
