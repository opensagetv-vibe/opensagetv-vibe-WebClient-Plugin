# P13 field acceptance

2026-11-19 qualified stock-Linux scope: original TT/DVB OFF/ON7rows each,
DVD MPEG-PS Push OFF/ON5rows each, actual diagnostic OFF/ON/OFF3rows PASS
with no unknown opcodes/frame timeouts/queues. Same stock232/hostWebKit/
ephemeral identity; saved settings/Core unchanged. Repeated Y/UV colors,
unload and HD300 handle fallback use controlled production-DOM inputs in
Chrome/WebKit12cases each, not claimed emitted by the physical stock runs.
See `artifacts/results/WP13-003/RESULT.md`. Default staysOFF; scoped task is
complete, not physical iPhone/all-source/vendor video-surface certification.
The original protocol below remains as reproducible test guidance.

## WP13-003 — stock UNIFIED OFF/ON A/B

Required before calling unified graphics fully accepted:

1. Use an unchanged stock SageTV server and the same WebPlayer client/device/browser for both runs.
2. Run with **Experimental unified Y/UV graphics surfaces OFF** and record normal MiniClient GFX, DVB bitmap caption and Push playback behavior.
3. Reconnect with the setting ON and prove the server negotiated `GFX_YUV_IMAGE_CACHE=UNIFIED` for that session only.
4. Exercise repeated format-256 Y and interleaved-UV line updates. Prove visible images update more than once; a one-frame/static success is insufficient.
5. Exercise stock DVB/Push content in both modes. Video, audio, captions, GFX and input must remain functional.
6. Exercise a server request containing an HD300-style video-plane handle. Browser playback must remain on its ordinary video element/rectangle path; the unsupported handle must not blank or reposition video.
7. Disable UNIFIED, reconnect, and prove negotiation returns to the historical empty/off behavior.
8. Capture the session diagnostic opcode ledger and browser report for both runs. No unexpected opcode may be silently accepted.

Record server version, browser version, WebPlayer version, content type, OFF/ON property replies, observed format-256 updates, and any fallback/error. Do not close this gate using generated YUV rows alone.
