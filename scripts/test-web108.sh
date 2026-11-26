#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
bash scripts/build-local.sh
mkdir -p build/manual/test-classes
cp=build/manual/classes:build/manual/test-classes:/usr/share/java/servlet-api.jar
javac --release 8 -cp "$cp" -d build/manual/test-classes tests/MediaUrlPathSmoke.java tests/DiscSourceSmoke.java
java -cp "$cp" org.opensagetv.webplayer.MediaUrlPathSmoke
java -cp "$cp" org.opensagetv.webplayer.DiscSourceSmoke /usr/bin/ffmpeg
javac --release 8 -cp "$cp" -d build/manual/test-classes tests/MiniClientProtocolSmoke.java
for test in StockDvdReconfigureSmoke StockClientPlaybackSmoke StockClientInfoSmoke MiniClientNativeSeekSmoke; do
  javac --release 8 -cp "$cp" -d build/manual/test-classes "tests/$test.java"
  java -cp "$cp" "org.opensagetv.webplayer.$test"
done
bash scripts/prepare-process-control-tests.sh
javac --release 8 -cp "$cp" -d build/manual/test-classes tests/MiniClientDvdWireSmoke.java
java -cp "$cp" org.opensagetv.webplayer.MiniClientDvdWireSmoke /usr/bin/ffmpeg
node --check src/main/webapp/js/miniclient.js
node --check src/main/webapp/sw.js
python3 tests/test-dvd-field-clock.py
for engine in chromium webkit; do
  SAGETV_BROWSER_ENGINE="$engine" /opt/opensagetv-vibe/web-python/bin/python3 tests/browser-dvd-smoke.py
  SAGETV_BROWSER_ENGINE="$engine" SAGETV_ARTIFACT_DIR=artifacts/active/WEB-108 /opt/opensagetv-vibe/web-python/bin/python3 tests/browser-streaming-smoke.py
done
