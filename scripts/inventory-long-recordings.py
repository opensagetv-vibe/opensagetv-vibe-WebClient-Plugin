#!/usr/bin/env python3
"""Bounded read-only catalogue coverage despite the public 500-row cap.

Union supported text queries, stop at complete stable inventory or report an
explicit gap. No playback, metadata changes, SSH or source path disclosure.
"""
import importlib.util,json,time
from pathlib import Path
from urllib.parse import urlencode
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration()
rows={};queries=[];initial=C.request(cfg,'/SageTVWebPlayer/api/recordings?limit=500')
expected=initial.get('total');rows.update((r['id'],r) for r in initial.get('recordings',[]))
for query in 'aeiouy0123456789bcdfghjklmnpqrstvwxz':
    if len(rows)==expected:break
    data=C.request(cfg,'/SageTVWebPlayer/api/recordings?'+urlencode(dict(limit=500,q=query)))
    rows.update((r['id'],r) for r in data.get('recordings',[]))
    queries.append(dict(query=query,total=data.get('total'),returned=data.get('count')))
# Categories/years make single-letter searches unexpectedly broad. Existing
# exact title text (still public substring matching) narrows those collections.
for query in sorted({r.get('title','').strip() for r in rows.values()})[:80]:
    if len(rows)==expected:break
    if len(query)<3:continue
    data=C.request(cfg,'/SageTVWebPlayer/api/recordings?'+urlencode(dict(limit=500,q=query)))
    rows.update((r['id'],r) for r in data.get('recordings',[]))
    queries.append(dict(query=query,total=data.get('total'),returned=data.get('count')))
final=C.request(cfg,'/SageTVWebPlayer/api/recordings?limit=1').get('total')
report=dict(readOnly=True,complete=expected==final==len(rows),expected=expected,finalTotal=final,
    covered=len(rows),queries=queries,
    largest=[{k:r.get(k) for k in ('id','title','duration','recording')}
        for r in sorted(rows.values(),key=lambda r:r.get('duration',0),reverse=True)[:10]],
    durationIs='public Airing duration; not an independently probed source-file duration')
out=ROOT/'artifacts/active/WP11-008';out.mkdir(parents=True,exist_ok=True)
path=out/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-catalogue-inventory.json')
path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(complete=report['complete'],covered=len(rows),expected=expected,
    requests=len(queries)+2,largest=report['largest'][:3],path=str(path)),indent=2))
raise SystemExit(0 if report['complete'] else 1)
