#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build/manual/test-classes
cp=build/manual/classes:build/manual/test-classes
for test in LiveRolloverSmoke MiniClientProtocolSmoke MiniClientEndOfStreamSmoke MiniClientNativeSeekSmoke StockClientPlaybackSmoke; do
  javac --release 8 -cp "$cp" -d build/manual/test-classes "tests/$test.java"
  java -cp "$cp" "org.opensagetv.webplayer.$test"
done
javac --release 8 -cp "$cp" -d build/manual/test-classes tests/LiveTailPrerollRuntimeSmoke.java
java -cp "$cp" org.opensagetv.webplayer.LiveTailPrerollRuntimeSmoke /usr/bin/ffmpeg
node tests/test-miniclient-core.js
node tests/test-miniclient-playback.js
