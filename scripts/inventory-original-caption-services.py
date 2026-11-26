#!/usr/bin/env python3
"""Read the exact retained broadcast prefix once; export counters, not captions.

No playback, encoder, server settings or source writes. Requires the local
OriginalCaptionInventory Java test to have been compiled in the DEV container.
"""
import hashlib
import importlib.util
import json
import shlex
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('commission', ROOT / 'scripts/commission-mobile.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
SOURCE = '/var/media/OpenSageTV_Vibe_Tests/WEB097_LIVE_WTTW_STARTUP.ts'
SIZE = 18800000
SHA = 'a73042ed73a4514c76e2a18449298f842e9ecca8c780e09b371e2191f7771d9c'


def main():
    cfg = C.configuration()
    report = dict(passed=False, physicalAcceptance=False, source=SOURCE,
                  exportsCaptionPayload=False, serverMutations=False)
    output = ROOT / 'artifacts/active/WP05-006'
    output.mkdir(parents=True, exist_ok=True)
    path = output / (time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()) + '-original-caption-inventory.json')
    try:
        with C.ssh(cfg) as client:
            name = shlex.quote(cfg['unraid_container_name'])
            source = shlex.quote(SOURCE)
            command = ('docker exec ' + name + ' sh -c ' + shlex.quote(
                'test -f ' + source + ' && test ! -L ' + source +
                ' && test "$(stat -c %s -- ' + source + ')" = ' + str(SIZE) +
                ' && sha256sum -- ' + source))
            if C.remote(client, command).split()[0] != SHA:
                raise RuntimeError('Exact retained source identity changed')
            _, stdout, stderr = client.exec_command(
                'docker exec ' + name + ' head -c 20971521 -- ' + source, timeout=35)
            data = stdout.read(20971521)
            error = stderr.read(1024)
            if stdout.channel.recv_exit_status() or error:
                raise RuntimeError('Bounded original source read failed')
        if len(data) != SIZE or hashlib.sha256(data).hexdigest() != SHA:
            raise RuntimeError('Readback identity changed; no parser evidence')
        result = subprocess.run([
            'docker', 'exec', '-i', '-w', '/workspace/web-client-plugin',
            'opensagetv-vibe-dev', 'java', '-cp',
            'build/manual/classes:build/manual/test-classes',
            'org.opensagetv.webplayer.OriginalCaptionInventory'],
            input=data, capture_output=True, timeout=60, check=True)
        inventory = json.loads(result.stdout)
        if inventory['sourceBytes'] != SIZE or inventory['sha256'] != SHA:
            raise RuntimeError('Parser identity mismatch')
        report.update(passed=True, inventory=inventory)
    except Exception as failure:
        report.update(errorType=type(failure).__name__, error=str(failure)[:300])
    path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    print('Report: ' + str(path))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
