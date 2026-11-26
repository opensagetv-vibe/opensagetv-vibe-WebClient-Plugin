#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 tests/test_project_manifest.py
SERVLET_JAR="${SERVLET_API_JAR:-/usr/share/java/servlet-api.jar}"
node --check src/main/webapp/js/app.js
node --check src/main/webapp/js/advanced-ui.js
node --check src/main/webapp/js/session-state.js
node --check src/main/webapp/js/library-utils.js
node --check src/main/webapp/js/atsc-captions.js
node --check src/main/webapp/js/wasm-decoder-adapter.js
node --check src/main/webapp/js/performance-watchdog.js
node --check src/main/webapp/js/fmp4-fallback.js
node --check src/main/webapp/js/commercial-skip.js
node --check src/main/webapp/js/remote-navigation.js
node --check src/main/webapp/js/pwa.js
node --check src/main/webapp/js/miniclient-core.js
node --check src/main/webapp/js/miniclient-input.js
node --check src/main/webapp/js/miniclient-streaming.js
node --check src/main/webapp/js/miniclient-caption-authority.js
node --check src/main/webapp/js/miniclient-captions.js
node --check src/main/webapp/js/miniclient-subtitles.js
node --check src/main/webapp/js/miniclient-dvd-spu.js
node --check src/main/webapp/js/miniclient-playback.js
node --check src/main/webapp/js/miniclient-experience.js
node tests/test-playback-experience.js
node tests/runtime-quality.test.js
node --check src/main/webapp/js/miniclient-support.js
node --check src/main/webapp/js/miniclient.js
node --check src/main/webapp/js/miniclient-mobile.js
node tests/mobile-fullscreen-smoke.js
node tests/test-mobile-library.js
node --check src/main/webapp/js/miniclient-app.js
node tests/test-mobile-input.js
node tests/test-event-delivery.js
node tests/test-vibe-input.js
node tests/test-caption-clock.js
node --check src/main/webapp/sw.js
node tests/test-captions608.js
node tests/test-captions708.js
node tests/test-caption-services.js
node tests/test-caption-rollup.js
node tests/test-performance.js
node tests/test-session-state.js
node tests/test-session-state-v2.js
node tests/test-library-utils.js
node tests/test-commercial-skip.js
node tests/test-miniclient-core.js
node tests/test-settings-parity.js
node tests/test-miniclient-display.js
python scripts/verify-vibe-icons.py
node tests/test-miniclient-playback.js
node tests/test-caption-authority.js
node tests/test-stv-caption-control.js
node tests/test-ordinary-subtitles.js
node tests/test-p14-support.js
python3 tests/test-field-read-only.py
python3 tests/test-stock-dvd-angle-capability.py
python3 tests/test-baseline-war-search.py
python3 -m unittest discover -s tests/parity -p 'test_*_sync.py'
node tests/test-field-read-only.js
node tests/test-one-picture-observer.js
node tests/test-auto-resolution.js
python3 scripts/audit-android-features.py
python - <<'PY'
import hashlib, pathlib, xml.etree.ElementTree as ET, zipfile, re
root=pathlib.Path('.')
ET.parse(root/'src/main/webapp/WEB-INF/web.xml')
import json
json.loads((root/'src/main/webapp/manifest.webmanifest').read_text())
index=(root/'src/main/webapp/index.html').read_text()
for removed in ['Server Watch History','Tuners / Encoder Health','SageTV Favorites / Recording Rules','DVR Schedule']:
    assert removed not in index, removed
assert "location.replace('miniclient.html'+location.search+location.hash)" in index
assert 'simple-recording-listbox' not in index
assert 'src="js/advanced-ui.js"' not in index
mc=(root/'src/main/webapp/js/miniclient.js').read_text()
assert 'dw=wholeResizedSurface?uiW:Math.abs(w),dh=wholeResizedSurface?uiH:Math.abs(h)' in mc
playback=(root/'src/main/webapp/js/miniclient-playback.js').read_text()
assert 'async waitServerBuffer' in playback and 'async hlsHealth' in playback and 'async recover' in playback
assert "requestJson('api/hls'" in mc
assert "Core.logicalSize(rect.width,rect.height,settings.uiResolution,window.devicePixelRatio)" in mc
assert "queueInput('resize'" in mc
assert 'function layoutStage()' in mc
assert "Core.stageRect(sr.width,sr.height,uiW,uiH," in mc
assert "visible.style.width=d.width+'px'" in mc
css=(root/'src/main/webapp/css/miniclient.css').read_text(); assert 'max-width:1280px' not in css and 'height:100dvh' in css
assert "c.scale(w<0?-1:1,h<0?-1:1)" not in mc
assert "if(h<0){" in mc and "globalCompositeOperation='copy'" in mc
manifest_path=root/'dist/local-install/SageTVPluginsDev.d/sagetv-webplayer.xml'
ET.parse(manifest_path)
manifest=manifest_path.read_text()
windows_manifest_path=root/'dist/local-install/SageTVPluginsDev.d/sagetv-webplayer-windows.xml'
ET.parse(windows_manifest_path)
windows_manifest=windows_manifest_path.read_text()
m=re.search(r'<Version(?:\s+[^>]*)?>([^<]+)</Version>',manifest); assert m and m.group(1)=='3.3.0'
m2=re.search(r'<MD5>([0-9a-f]+)</MD5>',manifest)
pkg=root/'dist/local-install/SageTVPluginsDev.d/sagetv-webplayer-3.3.0.zip'
actual=hashlib.md5(pkg.read_bytes()).hexdigest()
assert m2 and m2.group(1)==actual,(m2.group(1) if m2 else None,actual)
with zipfile.ZipFile(pkg) as z:
    assert 'jetty/webapps/SageTVWebPlayer.war' in z.namelist()
with zipfile.ZipFile(root/'dist/SageTVWebPlayer.war') as z:
    names=set(z.namelist())
    for required in ['index.html','miniclient.html','css/miniclient.css','js/miniclient.js','js/miniclient-core.js','js/miniclient-input.js','js/miniclient-app.js','js/miniclient-playback.js','js/miniclient-streaming.js','js/miniclient-caption-authority.js','js/miniclient-captions.js','js/miniclient-subtitles.js','js/miniclient-dvd-spu.js','js/miniclient-support.js','js/app.js','js/advanced-ui.js','js/session-state.js','js/library-utils.js','js/atsc-captions.js','js/wasm-decoder-adapter.js','js/performance-watchdog.js','js/fmp4-fallback.js','js/commercial-skip.js','js/remote-navigation.js','js/pwa.js','sw.js','codec-test.html','manifest.webmanifest','icons/icon-192.png','icons/icon-512.png','WEB-INF/web.xml']:
        assert required in names, required
    for cls in ['MiniClientCrypto','ContinuousStreamServlet','StreamOptions','StreamPlan','StreamCommand','A53CaptionTap','CaptionsServlet','MediaProbe','ContinuousFilePump','PlaybackSessionContext','SubtitleCue','SubtitleCueQueue','SubtitleClock','SubtitleCapabilities','SubtitleSourceBranch','TsServiceInventoryProbe','SubtitleCueServlet','SubtitleLimits','SubtitleWorkBudget','TeletextSubtitleSession','TeletextSourcePump','DvbBitmapDecoder','DvbSubtitleSession','DvbSourcePump','LegacyExtenderCaptionBridge','TeletextCea608Bridge','OrdinarySubtitleSession','DvdPtsClock','DvdPushBuffer','DvdNativeSession','DvdAudioStreamCode','DvdPsInspector','MiniClientCapabilityPolicy','MediaUrlPath','AuthorizedPathMatcher','AuthorizedMediaResolver','DiscCapabilityProbe','DiscSourceInfo','DiscMetadataHealth','DiscTitleProbe','DiscInspection','DiscInfoServlet','MpegTsSeekIndex','AudioTrackPolicy','GfxOpcodeLedger','DiagnosticSupport','DiagnosticSupportServlet','CodecHlsTestManager','CodecHlsTestServlet','CodecHlsTestMediaServlet']:
        assert 'WEB-INF/classes/org/opensagetv/webplayer/'+cls+'.class' in names,cls
    assert '3.3.0' in z.read('miniclient.html').decode()
    assert '<Plugin>SageTVFFmpegPluginLinux</Plugin>' in manifest
    assert '<OS>Linux</OS>' in manifest
    assert '<Plugin>SageTVFFmpegPluginWinx64</Plugin>' in windows_manifest
    assert '<OS>Windows</OS>' in windows_manifest
print('XML/package/WAR/MD5/new streaming classes OK')
with zipfile.ZipFile(root/'dist/SageTVWebPlayer.war') as z:
    for name in ['StockCaptionState','SubtitlePumpPosition','AvSyncManager','AvSyncServlet','DiagnosticJson']:
        assert 'WEB-INF/classes/org/opensagetv/webplayer/'+name+'.class' in z.namelist(),name
PY
first_artifact_hashes="$(sha256sum \
  dist/SageTVWebPlayer.war \
  dist/local-install/SageTVPluginsDev.d/sagetv-webplayer-3.3.0.zip \
  dist/local-install/SageTVPluginsDev.d/sagetv-webplayer.xml \
  dist/local-install/SageTVPluginsDev.d/sagetv-webplayer-windows.xml)"
python3 tests/test-build-info.py
bash scripts/build-local.sh >/dev/null
python3 scripts/package-local-plugin.py >/dev/null
second_artifact_hashes="$(sha256sum \
  dist/SageTVWebPlayer.war \
  dist/local-install/SageTVPluginsDev.d/sagetv-webplayer-3.3.0.zip \
  dist/local-install/SageTVPluginsDev.d/sagetv-webplayer.xml \
  dist/local-install/SageTVPluginsDev.d/sagetv-webplayer-windows.xml)"
if [[ "$first_artifact_hashes" != "$second_artifact_hashes" ]]; then
  echo 'Artifact reproducibility check failed.' >&2
  diff <(printf '%s\n' "$first_artifact_hashes") <(printf '%s\n' "$second_artifact_hashes") >&2 || true
  exit 1
fi
echo 'PASS deterministic WAR, plugin ZIP, and Linux/Windows manifests'
javap -verbose build/manual/classes/org/opensagetv/webplayer/HealthServlet.class | grep 'major version: 52'
mkdir -p build/manual/test-classes
bash scripts/prepare-process-control-tests.sh
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/OriginalCaptionInventory.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.OriginalCaptionInventory --self-test
javac --release 8 -cp build/manual/classes:build/manual/test-classes -d build/manual/test-classes tests/HlsDiskPressureSmoke.java
# Actual private-tmpfs execution is explicit: scripts/verify-hls-disk-pressure.py.
# Ordinary CI must never pressure its shared filesystem or contact a server.
for test in StockCaptionStateSmoke StockClientPlaybackSmoke StockDvdReconfigureSmoke StockClientInfoSmoke MobileLibrarySmoke ChannelLogoSmoke CaptionSelectionSmoke HlsOnePictureManifestSmoke; do
  javac --release 8 -cp build/manual/classes:"$SERVLET_JAR" -d build/manual/test-classes "tests/$test.java"
  java -cp build/manual/classes:build/manual/test-classes:"$SERVLET_JAR" "org.opensagetv.webplayer.$test"
done
if [[ -x "${TEST_FFMPEG:-/usr/bin/ffmpeg}" ]]; then
  javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/AvSyncRuntimeSmoke.java
  java -Djava.awt.headless=true -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.AvSyncRuntimeSmoke "${TEST_FFMPEG:-/usr/bin/ffmpeg}"
fi
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/PlaybackArchitectureSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.PlaybackArchitectureSmoke
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/HardwarePipelineSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.HardwarePipelineSmoke
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/MediaProbeCacheSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.MediaProbeCacheSmoke
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/TranscoderPluginResolutionSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.TranscoderPluginResolutionSmoke
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/DiscSourceSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.DiscSourceSmoke "${TEST_FFMPEG:-/usr/bin/ffmpeg}"
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/MediaUrlPathSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.MediaUrlPathSmoke
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/P11TimelineSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.P11TimelineSmoke "${TEST_FFMPEG:-/usr/bin/ffmpeg}"
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/P13GfxLifecycleSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.P13GfxLifecycleSmoke
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/CopyFallbackPolicySmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.CopyFallbackPolicySmoke
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/P14DiagnosticSupportSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.P14DiagnosticSupportSmoke
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/CodecHlsTestSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.CodecHlsTestSmoke "${TEST_FFMPEG:-/usr/bin/ffmpeg}"
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/P12AudioPolicySmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.P12AudioPolicySmoke
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/P15StockContractsSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.P15StockContractsSmoke
node tests/test-p12-streaming.js
if [[ -x "${TEST_FFMPEG:-/usr/bin/ffmpeg}" ]]; then
  javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/P12AvCalibrationSmoke.java
  java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.P12AvCalibrationSmoke "${TEST_FFMPEG:-/usr/bin/ffmpeg}"
  javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/P12QualityRuntimeSmoke.java
  java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.P12QualityRuntimeSmoke "${TEST_FFMPEG:-/usr/bin/ffmpeg}" "artifacts/active/WP12-005/generated-$(date -u +%Y%m%dT%H%M%SZ)"
fi
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/DvdNativeProtocolSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.DvdNativeProtocolSmoke
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/DvdPresentedClockSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.DvdPresentedClockSmoke
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/DvdSpuSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.DvdSpuSmoke
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/MiniClientDvdWireSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.MiniClientDvdWireSmoke "${TEST_FFMPEG:-/usr/bin/ffmpeg}"
if [[ -x "${TEST_FFMPEG:-/usr/bin/ffmpeg}" ]]; then
  javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/DvdPlaybackRuntimeSmoke.java
  java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.DvdPlaybackRuntimeSmoke "${TEST_FFMPEG:-/usr/bin/ffmpeg}"
  javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/DvdReadAheadRuntimeSmoke.java
  java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.DvdReadAheadRuntimeSmoke "${TEST_FFMPEG:-/usr/bin/ffmpeg}"
  javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/DvdStartupFallbackSmoke.java
  java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.DvdStartupFallbackSmoke "${TEST_FFMPEG:-/usr/bin/ffmpeg}"
else
  echo 'SKIP P08 DVD A/V runtime: FFmpeg missing'
fi
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/LegacyCaptionBridgeSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.LegacyCaptionBridgeSmoke
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/MiniClientProtocolSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.MiniClientProtocolSmoke
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/BrowserFramePacerSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.BrowserFramePacerSmoke
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/BrowserTransportLeaseSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.BrowserTransportLeaseSmoke
python3 tests/test-browser-transport-lifetime.py
javac --release 8 -cp build/manual/classes:build/manual/test-classes -d build/manual/test-classes tests/MiniClientFramePacingSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.MiniClientFramePacingSmoke
javac --release 8 -cp build/manual/classes:build/manual/test-classes -d build/manual/test-classes tests/MiniClientNativeSeekSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.MiniClientNativeSeekSmoke
javac --release 8 -cp build/manual/classes:build/manual/test-classes -d build/manual/test-classes tests/MiniClientEndOfStreamSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.MiniClientEndOfStreamSmoke
javac --release 8 -cp build/manual/classes:build/manual/test-classes -d build/manual/test-classes tests/LiveRolloverSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.LiveRolloverSmoke
if command -v ffmpeg >/dev/null 2>&1; then
  javac --release 8 -cp build/manual/classes:build/manual/test-classes -d build/manual/test-classes tests/LiveTailPrerollRuntimeSmoke.java
  java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.LiveTailPrerollRuntimeSmoke "$(command -v ffmpeg)"
fi
javac --release 8 -cp build/manual/classes:build/manual/test-classes -d build/manual/test-classes tests/PlaybackStateSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.PlaybackStateSmoke
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/SharedSourcePreviewSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.SharedSourcePreviewSmoke
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/QualityOptionsSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.QualityOptionsSmoke
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/SingleEncoderQualitySmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.SingleEncoderQualitySmoke
javac --release 8 -cp build/manual/classes:build/manual/test-classes -d build/manual/test-classes tests/WebQualityHandoffSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.WebQualityHandoffSmoke
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/CompanionDvdSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.CompanionDvdSmoke
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/MiniClientRecoverySmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.MiniClientRecoverySmoke
javac --release 8 -cp build/manual/classes:build/manual/test-classes -d build/manual/test-classes tests/MiniClientStartupSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.MiniClientStartupSmoke
javac --release 8 -cp build/manual/classes:build/manual/test-classes -d build/manual/test-classes tests/MiniClientAuthenticationSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.MiniClientAuthenticationSmoke
if [[ -x "${TEST_FFMPEG:-/usr/bin/ffmpeg}" ]]; then
  javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/HlsRuntimeSmoke.java
  java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.HlsRuntimeSmoke
else
  echo 'SKIP HLS runtime integration: set TEST_FFMPEG to an executable FFmpeg'
fi
SERVLET_JAR="${SERVLET_API_JAR:-/usr/share/java/servlet-api.jar}"
javac --release 8 -cp "build/manual/classes:$SERVLET_JAR" -d build/manual/test-classes tests/CommercialMarkersSmoke.java
java -cp "build/manual/classes:build/manual/test-classes:$SERVLET_JAR" org.opensagetv.webplayer.CommercialMarkersSmoke
javac --release 8 -cp "build/manual/classes:$SERVLET_JAR" -d build/manual/test-classes tests/StreamingServletSmoke.java
java_profile_cp="build/manual/classes:build/manual/test-classes:$SERVLET_JAR"
javac --release 8 -cp "$java_profile_cp" -d build/manual/test-classes tests/HlsControlProfileSmoke.java
java -cp "$java_profile_cp" org.opensagetv.webplayer.HlsControlProfileSmoke
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/RuntimeRateCommandSmoke.java
mkdir -p build/manual/runtime-rate-stubs
javac --release 8 -d build/manual/runtime-rate-stubs tests/stubs/runtime-rate/org/opensagetv/vibe/ffmpeg/RuntimeBitrateControl.java
java -cp build/manual/runtime-rate-stubs:build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.RuntimeRateCommandSmoke
java -cp "build/manual/classes:build/manual/test-classes:$SERVLET_JAR" org.opensagetv.webplayer.StreamingServletSmoke
if [[ -x "${TEST_FFMPEG:-/usr/bin/ffmpeg}" ]]; then
  javac --release 8 -cp "build/manual/classes:$SERVLET_JAR" -d build/manual/test-classes tests/StreamingRuntimeSmoke.java
  java -cp "build/manual/classes:build/manual/test-classes:$SERVLET_JAR" org.opensagetv.webplayer.StreamingRuntimeSmoke
else
  echo 'SKIP real TS/CC integration: FFmpeg missing'
fi
node tests/test-mpegts-streaming.js

javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/TeletextSubtitleSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.TeletextSubtitleSmoke
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/ConcurrentSubtitleSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.ConcurrentSubtitleSmoke
node tests/test-teletext-controller.js
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/DvbSubtitleSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.DvbSubtitleSmoke
python3 tests/test-caption-transition-fixture.py
if [ -f artifacts/test-media/VIBE_CAPTION_PMT/fixture.json ]; then
  javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/DvbTransitionFixtureSmoke.java tests/DvbPmtTimingSmoke.java
  java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.DvbTransitionFixtureSmoke
  java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.DvbPmtTimingSmoke
fi
node tests/test-dvb-controller.js
node tests/test-caption-service-loss.js
javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/PmtServiceRetirementSmoke.java
java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.PmtServiceRetirementSmoke
if [[ -x "${TEST_FFMPEG:-/usr/bin/ffmpeg}" ]]; then
  javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/OrdinarySubtitleSmoke.java
  java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.OrdinarySubtitleSmoke tests/parity/fixtures "${TEST_FFMPEG:-/usr/bin/ffmpeg}"
  javac --release 8 -cp build/manual/classes -d build/manual/test-classes tests/VobSubPaletteSmoke.java
  java -cp build/manual/classes:build/manual/test-classes org.opensagetv.webplayer.VobSubPaletteSmoke
else
  echo 'SKIP P06 ordinary subtitle integration: FFmpeg missing'
fi
if [[ "${RUN_BROWSER_TESTS:-0}" == 1 ]]; then
  python tests/browser-settings-parity.py
  # Unified DEV supplies its pinned Chrome wrapper, not /usr/bin/chromium.
  # Honor an explicit caller override and retain portable system fallback.
  if command -v vibe-chromium >/dev/null 2>&1; then
    export CHROMIUM_PATH="${CHROMIUM_PATH:-$(command -v vibe-chromium)}"
  fi
  SAGETV_ARTIFACT_DIR="$ROOT/artifacts/active/WEB-023" python tests/browser-calibration-layout.py
  python tests/browser-iphone-usability.py
  python tests/browser-mobile-vibe.py
  python tests/browser-special-key-mappings.py
  python tests/browser-dvd-transport-search.py
  python tests/browser-mobile-dock.py
  python tests/browser-pwa.py
  python tests/browser-smoke.py
  python tests/browser-layout-smoke.py
  python tests/browser-streaming-smoke.py
  python tests/browser-caption-services.py
  python tests/browser-teletext-smoke.py
  python tests/browser-dvb-smoke.py
  python tests/browser-ordinary-subtitles-smoke.py
  python tests/browser-dvd-smoke.py
  python tests/browser-recovery-smoke.py
  python tests/browser-frame-pacing.py
  SAGETV_ARTIFACT_DIR="${SAGETV_ARTIFACT_DIR:-$ROOT/artifacts/active/WEB-037}" python tests/browser-stream-read-ahead.py
  SAGETV_ARTIFACT_DIR="${SAGETV_ARTIFACT_DIR:-$ROOT/artifacts/active/WEB-037}" python tests/browser-long-poll-events.py
  SAGETV_ARTIFACT_DIR="${SAGETV_ARTIFACT_DIR:-$ROOT/artifacts/active/WEB-037}" python tests/browser-remote-touch.py
  python tests/browser-playback-experience.py
  python tests/browser-runtime-rate-settings.py
  python tests/browser-vibe-display-smoke.py
  python tests/browser-p13-smoke.py
  python tests/browser-p14-smoke.py
else
  echo 'SKIP offline Chromium smoke: use RUN_BROWSER_TESTS=1 with playwright/Chromium installed'
fi
echo 'Validation OK'
