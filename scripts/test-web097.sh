#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ "${1:-}" != --from-quality ]]; then
bash scripts/build-local.sh
mkdir -p build/manual/absent-provider
javac --release 8 -cp build/manual/classes -d build/manual/absent-provider tests/OwnedProcessCapabilityAbsentSmoke.java
java -cp build/manual/classes:build/manual/absent-provider org.opensagetv.webplayer.OwnedProcessCapabilityAbsentSmoke
fi
bash scripts/prepare-process-control-tests.sh
cp=build/manual/classes:build/manual/test-classes:/usr/share/java/servlet-api.jar
tests=(OwnedProcessControlSmoke HlsProcessStopSmoke DvdReadAheadRuntimeSmoke DvdStartupFallbackSmoke MiniClientDvdWireSmoke HlsRuntimeSmoke StreamingRuntimeSmoke SingleEncoderQualitySmoke MiniClientRecoverySmoke)
if [[ "${1:-}" == --from-quality ]]; then
  javac --release 8 -cp "$cp" -d build/manual/classes src/main/java/org/opensagetv/webplayer/HlsSessionManager.java
  tests=(SingleEncoderQualitySmoke MiniClientRecoverySmoke)
fi
for test in "${tests[@]}"; do
  javac --release 8 -cp "$cp" -d build/manual/test-classes "tests/$test.java"
  java -cp "$cp" "org.opensagetv.webplayer.$test" /usr/bin/ffmpeg
done
node tests/test-miniclient-playback.js
python3 tests/test-phone-recording-field-contracts.py
