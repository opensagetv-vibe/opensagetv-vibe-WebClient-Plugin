#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
field_python=/opt/opensagetv-vibe/web-python/bin/python3
test -x "$field_python"
if [[ -n "${SAGETV_FIELD_SSH_WHEELHOUSE:-}" ]]; then
  test -d "$SAGETV_FIELD_SSH_WHEELHOUSE"
  "$field_python" -m pip install --require-hashes --no-index --find-links "$SAGETV_FIELD_SSH_WHEELHOUSE" -r "$root/requirements-field-ssh.txt"
else
  "$field_python" -m pip install --require-hashes --no-cache-dir -r "$root/requirements-field-ssh.txt"
fi
"$field_python" -m pip check
"$field_python" -c 'import importlib.metadata as m; assert m.version("paramiko")=="5.0.0"; print("PASS optional stock-field SSH dependency: paramiko5.0.0; no phone/server input")'
