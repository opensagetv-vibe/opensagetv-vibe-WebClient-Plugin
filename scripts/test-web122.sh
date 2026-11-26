#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export SAGETV_ARTIFACT_DIR="${SAGETV_ARTIFACT_DIR:-$PWD/artifacts/active/WEB-122}"
python=/opt/opensagetv-vibe/web-python/bin/python
"$python" tests/browser-watch-live.py
"$python" tests/browser-video-cast.py
"$python" tests/browser-mobile-vibe.py
"$python" tests/browser-pwa.py
