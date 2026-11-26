# MPEG-TS source ownership and MSE threading

WEB-066,2026-11-17: actual pinned mpegts.js1.8.0 on Chromium/stock232 displays
UK captions but replacement seeks emit unhandled SourceBuffer.buffered errors:
worker MediaSource attachment is closing. The captured worker stack enters
MSEController.flush. This is not scored as PASS just because video continues.

The pinned [dedicated engine source](https://github.com/xqq/mpegts.js/blob/v1.8.0/src/player/player-engine-dedicated-thread.ts)
posts unload/shutdown/destroy messages while detaching the element. Its
[public player API](https://github.com/xqq/mpegts.js/blob/v1.8.0/src/player/mse-player.ts)
does not expose an awaited teardown completion. A guessed delay or private
worker/member patch cannot establish safe source custody. This is our inference
from source plus the observed replacement stack, not an upstream fix claim.

The client now requests main-thread MSE while retaining enableWorker=true for
transmuxing. Main-thread MSE teardown is synchronous at the public player
boundary; heavy byte parsing remains worker-requested. No vendor bundle, Core,
FFmpeg, GPU processing or server buffering setting changes. Requested threading
is reported separately; a request is not proof that a worker was constructed.

Affected validation: worker-policy failing-before regression,17TS/55playback
checks, production browser streaming/Exit/PWA, package/served hashes, then real
original-source seek/new producer/new presented frames/captions/Off/retirement.
Preserve existing HLS/native DVD evidence; do not replay unrelated matrices.
Actual real-MSE field qualification after deployment remains required.
