#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build/manual/test-classes
cp=build/manual/classes:build/manual/test-classes:/usr/share/java/servlet-api.jar
for test in StreamHealthSmoke P14DiagnosticSupportSmoke HlsEmptySeekSmoke ShellCachePolicySmoke; do
  javac --release 8 -cp "$cp" -d build/manual/test-classes "tests/$test.java"
  java -cp "$cp" "org.opensagetv.webplayer.$test"
done
bash scripts/test-web120.sh
