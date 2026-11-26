#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
provider=/workspace/ffmpeg-plugin/build/process-api-test-classes
test -f "$provider/org/opensagetv/vibe/ffmpeg/OwnedProcessControl.class"
mkdir -p build/process-control-test-classes
javac --release 8 -cp "$provider" -d build/process-control-test-classes \
  src/main/java/org/opensagetv/webplayer/OwnedProcessControlBridge.java tests/OwnedProcessControlSmoke.java
java -cp "build/process-control-test-classes:$provider" org.opensagetv.webplayer.OwnedProcessControlSmoke
