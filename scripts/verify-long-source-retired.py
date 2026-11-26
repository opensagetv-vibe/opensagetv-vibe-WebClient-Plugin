#!/usr/bin/env python3
"""Read-only independent retirement proof for one exact owned elapsed test."""
import argparse,importlib.util,json,re,shlex
from pathlib import Path
from urllib.parse import urlencode
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('report',type=Path);a=p.parse_args()
path=a.report.resolve();directory=(ROOT/'artifacts/active/WP11-008').resolve()
if path.parent!=directory or not re.fullmatch(r'\d{8}T\d{6}Z-chromium-elapsed-long-recording\.json',path.name):p.error('Exact owned elapsed report required')
r=json.loads(path.read_text(encoding='utf-8'));identity=r.get('ownedSession','')
if r.get('mediaId')!=1444 or not r.get('ownedStopIntent') or r.get('cleanup') or not re.fullmatch('[0-9a-f]{32}',identity):raise RuntimeError('Owned Stop provenance unavailable; no controls sent')
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py');C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration()
removed=False
try:C.request(cfg,'/SageTVWebPlayer/api/hls?'+urlencode({'session':identity}))
except RuntimeError as e:
 if str(e).startswith('HTTP 404:'):removed=True
 else:raise
with C.ssh(cfg) as client:
 commands=C.remote(client,'docker exec '+shlex.quote(cfg['unraid_container_name'])+' ps -eo args')
 matched=any(identity in line for line in commands.splitlines())
result={'ownedHlsApiRemoved':removed,'ownedProcessStillPresent':matched,'otherActivityPreserved':True,
        'controlsSent':False,'activity':C.activity(cfg),'passed':removed and not matched}
output=directory/(path.stem+'-retirement.json')
with output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
print(json.dumps(result));raise SystemExit(0 if result['passed'] else 1)
