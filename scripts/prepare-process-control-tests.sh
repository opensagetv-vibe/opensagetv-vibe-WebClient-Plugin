#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
provider="${SAGETV_FFMPEG_PLUGIN_JAR:-../opensagetv-vibe-FFmpeg-Plugin/dist/dev/SageTVFFmpegPlugin.jar}"
if [[ ! -f "$provider" && -f /workspace/ffmpeg-plugin/dist/dev/SageTVFFmpegPlugin.jar ]]; then
  provider=/workspace/ffmpeg-plugin/dist/dev/SageTVFFmpegPlugin.jar
fi
test -f "$provider" || { echo 'Build the required FFmpeg plugin first (or set SAGETV_FFMPEG_PLUGIN_JAR).' >&2; exit 2; }
provider="$(realpath "$provider")"
for name in OwnedProcessControl OwnedProcessStop WindowsJobProcessStop RuntimePaths; do
  jar tf "$provider" | grep -qx "org/opensagetv/vibe/ffmpeg/$name.class" || { echo 'Provider lacks protocol1 lifecycle API.' >&2; exit 2; }
done
mkdir -p build/manual/test-classes
(cd build/manual/test-classes && jar xf "$provider" \
  org/opensagetv/vibe/ffmpeg/OwnedProcessControl.class org/opensagetv/vibe/ffmpeg/OwnedProcessStop.class \
  org/opensagetv/vibe/ffmpeg/WindowsJobProcessStop.class org/opensagetv/vibe/ffmpeg/RuntimePaths.class)
# Dependency classes belong to the test classpath only, never WAR/main classes.
