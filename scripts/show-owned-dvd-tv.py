#!/usr/bin/env python3
"""One public TV transition after independently verified ALADDIN preview.

No Watch/seek or replay. Intended only for the current physical phone test.
"""
import importlib.util,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration()
def mcp(action,**kw):return C.request(cfg,'/v1/control',dict(action=action,**kw),mcp=True)
a=C.activity(cfg);n=mcp('ui.state',context='123c8282e1ee')
if a['recordingCount'] or a['connectedClientCount'] or mcp('ui.list')['contexts']!=['123c8282e1ee'] or n.get('dvd') is not True or n.get('dvdMenu') is not False or (n.get('media') or {}).get('mediaFileId')!=2504:raise RuntimeError('Require exact approved moving ALADDIN phone test')
path=ROOT/'artifacts/active/WEB-099'/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-one-tv-view.json')
report=dict(intent='One public TV after actual HDMI preview verification',before=n,activity=a)
with path.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
report['receipt']=mcp('ui.command',context='123c8282e1ee',command='TV')
path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(accepted=report['receipt'].get('accepted'),oneTvOnly=True,report=str(path))))
