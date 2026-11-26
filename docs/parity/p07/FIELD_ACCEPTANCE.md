# P07 stock-server field acceptance

## Current completion2026-11-17

WP07-001 is closed to the stated stock-role scope on unchanged stock Linux232,
normal-manager111206/Web3.3.0. Actual phone122221Z observes server GETs for
INPUT_DEVICES/VIDEO_CODECS/PUSH_AV_CONTAINERS, current native-role replies
IR,KEYBOARD,TOUCH,TV and MPEG2-PS, completed first GFX frame, six native INITs
and178,063,360pushed bytes. Current PS has1273video PES and one SPU PES; actual
DVD presentation is independently qualified in WEB-014/063/064. Actual trusted
BLE Down/native5 and WEB-049 pointer/timeline controls preserve SageMC input.
Capability-off/required reply alignment negatives pass focused protocol tests.
20stock protected hashes remain unchanged. No JVM/Core edit or restart used.
See ../2026-11-17-ACCEPTANCE.md. This is not all-disc/P08/P09 certification.

The instructions below are the original P07 protocol-only checkpoint. Native
DVD now defaults on with the implemented A/V/SPU backend; do not add/remove
the historical JVM opt-in just to repeat this gate.

This checklist closes **WP07-001 only**. It does not turn P07 into a visible DVD-playback pass; P08 is required for that.

1. Use an unchanged stock SageTV server/STV and the 3.2.10-P07 WAR.
2. Add JVM system property `sagetv.webplayer.nativeDvdProtocol=true` and restart SageTV/Jetty. How the JVM option is supplied depends on the SageTV installation/service wrapper.
3. Connect the browser MiniClient and capture native property negotiation. Verify `INPUT_DEVICES=IR,KEYBOARD,TOUCH,TV`, `PUSH_AV_CONTAINERS=MPEG2-PS`, and MPEG-2 remains present in `VIDEO_CODECS`.
4. Verify ordinary browser D-pad/touch/mouse-generated commands still reach SageMC. The browser event implementation remains present even though the stock-role property omits the literal `MOUSE` token.
5. Start a DVD only long enough to capture stock role selection and early protocol diagnostics. Export diagnostics immediately. Expected P07 evidence is `dvd.pending=true`, an INIT count, four-byte media replies and optional early metadata/PUSH activity.
6. Do **not** score lack of visible DVD A/V as a P07 regression. P08 has not yet connected queued MPEG-PS to the browser renderer. Avoid prolonged playback with the P07 opt-in role because the bounded input will truthfully apply backpressure when no P08 consumer drains it.
7. Remove the JVM property after the negotiation capture unless actively developing P08. The default P07 release retains the existing browser/MOUSE role.

Required evidence to close WP07-001: stock server/version identity, negotiated property values, proof the stock DVD player path selected MiniDVDPlayer/native push, and a browser input check.
