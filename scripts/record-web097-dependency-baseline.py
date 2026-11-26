#!/usr/bin/env python3
"""Read-only stock/INI/engine baseline before normal-manager lifecycle update."""
import hashlib,importlib.util,json,shlex,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration()
activity=C.activity(cfg)
if not activity.get('safeToRestart'):raise RuntimeError('Require independently idle test server')
paths=['/opt/sagetv/server/JARs/SageTVFFmpegPlugin.jar','/opt/sagetv/server/jetty/webapps/SageTVWebPlayer.war']
paths+=['/opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/'+name for name in ('ffmpeg.real.ini','ffmpeg.real','ffprobe','ffmpeg_MIM')]
with C.ssh(cfg) as client:
    container=shlex.quote(cfg['unraid_container_name'])
    protected=C.remote(client,'docker exec -w /opt/sagetv/server '+container+' sha256sum -c /usr/local/share/sagetv-stock/protected.sha256')
    if protected.count(': OK')!=20:raise RuntimeError('Protected stock mismatch')
    hashes=C.remote(client,'docker exec '+container+' sha256sum '+' '.join(map(shlex.quote,paths))).splitlines()
report=dict(readOnly=True,activity=activity,stockFiles=20,hashes={row.split()[1]:row.split()[0] for row in hashes})
folder=ROOT/'artifacts/active/WEB-097';folder.mkdir(parents=True,exist_ok=True)
path=folder/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-dependency-baseline.json')
with path.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(path=str(path),protectedStockFiles=20,files=len(paths))))
