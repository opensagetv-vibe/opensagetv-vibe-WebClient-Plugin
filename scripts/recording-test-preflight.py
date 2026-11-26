#!/usr/bin/env python3
"""Read-only candidates/schedule checkpoint before explicitly authorized tests."""
import importlib.util,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration()
activity=C.activity(cfg)
if not activity.get('safeToRestart'):raise RuntimeError('Independent idle server required')
schedule=C.request(cfg,'/SageTVWebPlayer/api/dvr')
guide=C.request(cfg,'/SageTVWebPlayer/api/guide?hours=2')
active=C.request(cfg,'/SageTVWebPlayer/api/recordings?active=true&limit=500')
now=guide['now'];occupied={x['airingId'] for x in schedule['scheduled']}
candidates=[]
for row in guide['airings']:
    if row.get('manualRecord') or row.get('mediaId') or row['airingId'] in occupied:continue
    if row.get('channelNumber') not in ('2.1','5.1','7.1','9.1','11.1','32.1'):continue
    candidates.append({k:row.get(k) for k in ('airingId','mediaId','title','channelNumber','start','end','manualRecord','currentlyAiring')})
out=ROOT/'artifacts/active/WEB-080';out.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
report=dict(readOnly=True,now=now,activity=activity,scheduled=schedule['scheduled'],
    conflicts=schedule['conflicts'],activeRecordings=active.get('recordings'),candidates=candidates)
path=out/(stamp+'-recording-preflight.json')
with path.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(path=str(path),now=now,scheduledCount=len(schedule['scheduled']),
    activeCount=len(active.get('recordings',[])),candidates=candidates),indent=2))
