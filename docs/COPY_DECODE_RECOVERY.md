# WEB-069 — confirmed Copy decode failure

2026-11-17, unchanged Breakfast broadcast, stock232/manager134049. Real
Chromium HLS rejects interlaced H.264 with MediaError3 despite known dimensions.
Client069 handles that with one existing permitted fallback; strict Copy stops
with explanation and no fallback request. Actual HLS allowed/strict rows pass.

Continuous MPEG-TS demonstrates a different defect: its transport fallback
preserves Copy, HLS fails the same codec, the second fallback is rejected by
the one-shot server budget, and ordinary recovery restarts the undecodable
representation six times. Field141307 retains the exact negative. That is not
a browser decode success or a reason to change stock Core.

## Client-first boundary and bounded owning-plugin correction

The client can detect actual MediaError3/4 and stop retries, but the existing
fallback contract cannot ask the owning media bridge to distinguish a codec
failure from a transport failure. The ordinary TS→HLS operation intentionally
preserves Copy. Reusing it cannot decode unsupported video. Applying normal
stream settings would also change that native session's configured defaults;
a second asynchronous restoration write is unsafe on source change/failure.
Quality handoff explicitly excludes Copy. No existing safe client-only
session-scoped transcode operation satisfies the recovery requirement.

Extend only the existing exact-producer fallback request with an optional
videoDecodeFailure flag. Default/older callers preserve the old TS→HLS Copy
semantics. A current client emits the flag only for a currently owned explicit
Copy representation with actual decode/not-supported MediaError3/4, not network,
abort, user Pause, autoplay denial or retired callbacks. The owning bridge may
then use its existing active-options-only H.264 fallback with the same one-shot
budget. Saved/configured defaults remain untouched. No new test API, Core,
stock FFmpeg/native replacement or normal-playback MCP dependency.

Affected validation: client negative vectors (including failed replacement
stopping without recovery), stream-option policy/stock native ownership tests,
current Java8/package/assets and real Copy allowed/strict HLS/TS tests. Existing
unrelated positive DVD/caption/encoder matrices are not automatically repeated.
