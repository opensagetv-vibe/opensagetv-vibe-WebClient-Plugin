#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build/manual/test-classes
bash scripts/prepare-process-control-tests.sh
for test in HardwarePipelineSmoke DvdReadAheadRuntimeSmoke DvdStartupFallbackSmoke MiniClientDvdWireSmoke; do
  javac --release 8 -cp build/manual/classes -d build/manual/test-classes "tests/$test.java"
  java -cp build/manual/classes:build/manual/test-classes "org.opensagetv.webplayer.$test" /usr/bin/ffmpeg
done
node tests/test-miniclient-playback.js
python3 tests/test-dvd-field-clock.py
python3 tests/test-dvd-audio-field-contract.py
for engine in chromium webkit; do
  SAGETV_BROWSER_ENGINE="$engine" /opt/opensagetv-vibe/web-python/bin/python tests/browser-dvd-smoke.py
done
python3 scripts/verify-mobile-package.py
