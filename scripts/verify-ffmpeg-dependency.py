#!/usr/bin/env python3
"""Read-only verification of the normal-manager MIM-STDIN-001 candidate.

Does not install, restart, repair launchers, edit INI or query other servers.
"""
import hashlib,importlib.util,json,shlex
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)

def main():
    cfg=C.configuration()
    before=json.loads((ROOT/'artifacts/results/WP08-006/MIM_DEPENDENCY_STAGE.json').read_text())
    plugin=ROOT.parent/'opensagetv-vibe-FFmpeg-Plugin'
    runtime=ROOT.parent/'opensagetv-vibe-ffmpeg-mim'
    owned={
        '/opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffmpeg_MIM':runtime/'output/linux-x64/ffmpeg_MIM',
        '/opt/sagetv/server/JARs/SageTVFFmpegPlugin.jar':plugin/'output/packages/SageTVFFmpegPlugin.jar',
    }
    expected={line.split()[1]:line.split()[0] for line in before['beforeIniAndEngines']}
    for remote,local in owned.items():
        if not local.is_file():raise RuntimeError('Missing candidate input: '+local.name)
        expected[remote]=hashlib.sha256(local.read_bytes()).hexdigest()
    with C.ssh(cfg) as client:
        container=shlex.quote(cfg['unraid_container_name'])
        protected=C.remote(client,'docker exec -w /opt/sagetv/server '+container+' sha256sum -c /usr/local/share/sagetv-stock/protected.sha256')
        lines=C.remote(client,'docker exec '+container+' sha256sum '+' '.join(shlex.quote(p) for p in expected)).splitlines()
        actual={line.split()[1]:line.split()[0] for line in lines}
        version=C.remote(client,'docker exec '+container+' /opt/sagetv/server/SageTVTranscoder --mim-version').strip()
    matched={path:actual.get(path)==digest for path,digest in expected.items()}
    report=dict(checkedUtc=datetime.now(timezone.utc).isoformat(),passed=all(matched.values()) and version=='SageTV FFmpeg MIM 0.4.13 (linux-x64)' and protected.count(': OK')==20,
                stockFiles=protected.count(': OK'),mimVersion=version,hashes=actual,matches=matched,activity=C.activity(cfg),readOnly=True)
    out=ROOT/'artifacts/active/WP08-006'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-dependency-verification.json')
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
    print(json.dumps(dict(passed=report['passed'],stockFiles=report['stockFiles'],mimVersion=version,matches=matched,report=str(out))))
    raise SystemExit(0 if report['passed'] else 1)

if __name__=='__main__':main()
