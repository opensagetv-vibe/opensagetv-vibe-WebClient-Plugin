#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
node --check src/main/webapp/js/miniclient.js
node --check src/main/webapp/sw.js
node tests/test-vibe-input.js
SAGETV_ARTIFACT_DIR=artifacts/active/WEB-113 /opt/opensagetv-vibe/web-python/bin/python3 tests/browser-dvd-transport-search.py
SAGETV_ARTIFACT_DIR=artifacts/active/WEB-113 /opt/opensagetv-vibe/web-python/bin/python3 tests/browser-special-key-mappings.py
SAGETV_ARTIFACT_DIR=artifacts/active/WEB-113 /opt/opensagetv-vibe/web-python/bin/python3 tests/browser-remote-touch.py
SAGETV_ARTIFACT_DIR=artifacts/active/WEB-113 /opt/opensagetv-vibe/web-python/bin/python3 tests/browser-mobile-vibe.py
for engine in chromium webkit; do
 SAGETV_BROWSER_ENGINE="$engine" /opt/opensagetv-vibe/web-python/bin/python3 tests/browser-dvd-smoke.py
done
