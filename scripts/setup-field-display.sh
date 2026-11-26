#!/usr/bin/env bash
# Optional browser-test display only, never a SageTV server/image change.
set -euo pipefail
if [[ ! -f /.dockerenv || "${SAGETV_WORKSPACE:-}" != /workspace/web-client-plugin || ! -f /workspace/web-client-plugin/dev.sh ]]; then
  echo 'Run only inside the reusable Vibe dev container at /workspace/web-client-plugin.' >&2
  exit 2
fi
if ! command -v Xvfb >/dev/null || ! command -v openbox >/dev/null || ! command -v xdotool >/dev/null; then
  if [[ "$(id -u)" != 0 ]]; then echo 'Run this optional dev-container setup as container root.' >&2; exit 2; fi
  apt-get install -y --no-install-recommends xvfb openbox xdotool
fi
echo 'PASS optional dev-container Xvfb/Openbox/window controls available; no server access'
