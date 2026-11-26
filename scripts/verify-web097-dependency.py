#!/usr/bin/env python3
"""Read-only comparison against the exact pre-manager stock/INI/engine baseline."""
import argparse,hashlib,importlib.util,json,shlex,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser(description=__doc__);p.add_argument('baseline');p.add_argument('--web-updated',action='store_true');p.add_argument('--runtime-updated',action='store_true');a=p.parse_args()
path=Path(a.baseline).resolve(strict=True);folder=(ROOT/'artifacts/active/WEB-097').resolve(strict=True)
if path.parent!=folder or path.is_symlink() or not path.name.endswith('-dependency-baseline.json'):raise RuntimeError('Require exact owned baseline')
before=json.loads(path.read_text(encoding='utf-8'))
if not before.get('readOnly') or not before['activity'].get('safeToRestart') or before.get('stockFiles')!=20:raise RuntimeError('Unqualified baseline')
expected=dict(before['hashes'])
jar=ROOT.parent/'opensagetv-vibe-FFmpeg-Plugin/output/packages/SageTVFFmpegPlugin.jar'
expected['/opt/sagetv/server/JARs/SageTVFFmpegPlugin.jar']=hashlib.sha256(jar.read_bytes()).hexdigest()
if a.web_updated:expected['/opt/sagetv/server/jetty/webapps/SageTVWebPlayer.war']=hashlib.sha256((ROOT/'dist/SageTVWebPlayer.war').read_bytes()).hexdigest()
expected_version='0.4.13'
if a.runtime_updated:
 runtime=ROOT.parent/'opensagetv-vibe-ffmpeg-mim'
 expected['/opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffmpeg_MIM']=hashlib.sha256((runtime/'output/linux-x64/ffmpeg_MIM').read_bytes()).hexdigest()
 expected_version=dict(line.split('=',1) for line in (runtime/'release.properties').read_text().splitlines() if '=' in line)['VERSION']
with C.ssh(cfg) as client:
    container=shlex.quote(cfg['unraid_container_name'])
    protected=C.remote(client,'docker exec -w /opt/sagetv/server '+container+' sha256sum -c /usr/local/share/sagetv-stock/protected.sha256')
    rows=C.remote(client,'docker exec '+container+' sha256sum '+' '.join(map(shlex.quote,expected))).splitlines()
    actual={row.split()[1]:row.split()[0] for row in rows}
    version=C.remote(client,'docker exec '+container+' /opt/sagetv/server/SageTVTranscoder --mim-version').strip()
matches={name:actual.get(name)==value for name,value in expected.items()}
report=dict(readOnly=True,stockFiles=protected.count(': OK'),matches=matches,hashes=actual,mimVersion=version,activity=C.activity(cfg))
report['passed']=all(matches.values()) and report['stockFiles']==20 and version=='SageTV FFmpeg MIM '+expected_version+' (linux-x64)'
output=folder/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-dependency-verification.json')
with output.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(passed=report['passed'],report=str(output),stockFiles=report['stockFiles'],matches=matches,mimVersion=version)))
raise SystemExit(0 if report['passed'] else 1)
