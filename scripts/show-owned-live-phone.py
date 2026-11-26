#!/usr/bin/env python3
"""One explicit public Full Screen On for this already-tuned test phone.

No Watch/retune/record or input replay; proof saved before dispatch.
"""
import argparse,importlib.util,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser();p.add_argument('--command',choices=('Full Screen On','TV'),default='Full Screen On');args=p.parse_args()
r=json.loads((ROOT/'artifacts/active/WEB-098/20261119T124722Z-iphone-live-handoff.json').read_text(encoding='utf-8'))
mid=r['rows'][0]['mediaId'];a=C.activity(cfg)
def mcp(action,**kw):return C.request(cfg,'/v1/control',dict(action=action,**kw),mcp=True)
if a['connectedClientCount'] or mcp('ui.list')['contexts']!=['123c8282e1ee']:raise RuntimeError('Wrong ownership')
if (mcp('ui.state',context='123c8282e1ee').get('media') or {}).get('mediaFileId')!=mid:raise RuntimeError('Live source changed')
m=C.request(cfg,'/SageTVWebPlayer/api/media?id='+str(mid))
if m['channelNumber']!='7.1' or not m['recording']:raise RuntimeError('Not this actual live source')
out=ROOT/'artifacts/active/WEB-098'/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-fullscreen-setup.json')
plan=dict(mediaId=mid,command=args.command,intent=True,syntheticPublicSetup=True,retune=False)
with out.open('x',encoding='utf-8') as f:json.dump(plan,f,indent=2)
plan['receipt']=mcp('ui.command',context='123c8282e1ee',command=args.command)
out.write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
print(json.dumps(plan))
