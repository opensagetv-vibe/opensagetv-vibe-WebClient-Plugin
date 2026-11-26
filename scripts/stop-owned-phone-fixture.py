#!/usr/bin/env python3
"""One exact public Stop for a completed canonical phone test, no replay."""
import argparse,importlib.util,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--media-id',type=int,choices=(20819,20905,84231,2504),required=True)
p.add_argument('--task',choices=('WEB-023','WEB-098','WEB-099','WP04-007'),help='Explicit owning task for a new affected gate')
a=p.parse_args()
def mcp(action,**kw):return C.request(cfg,'/v1/control',dict(action=action,**kw),mcp=True)
activity=C.activity(cfg)
if activity['recordingCount'] or activity['connectedClientCount'] or mcp('ui.list')['contexts']!=['123c8282e1ee']:raise RuntimeError('Require exact test phone only')
before=mcp('ui.state',context='123c8282e1ee')
if (before.get('media') or {}).get('mediaFileId')!=a.media_id:raise RuntimeError('Not exact canonical test source; preserve it')
info=C.request(cfg,'/SageTVWebPlayer/api/media?id='+str(a.media_id))
if a.media_id==20819:
    if info.get('recording') or before.get('dvd') is not True or (before.get('media') or {}).get('paths')!=['/var/media/OpenSageTV_Vibe_Tests/OpenSageTV_Vibe_Test_DVD/VIDEO_TS']:raise RuntimeError('Not exact canonical authored phone fixture')
elif a.media_id==2504:
    if info.get('recording') or before.get('dvd') is not True or (before.get('media') or {}).get('paths')!=['/var/media/videos/Aidens_Movies/ALADDIN/VIDEO_TS']:raise RuntimeError('Not exact approved ALADDIN phone test')
elif info.get('recording') or not all(x['path'].startswith('/var/media/OpenSageTV_Vibe_Tests/') for x in info['files']):raise RuntimeError('Not completed generated fixture')
folder=ROOT/'artifacts/active'/(a.task or ('WEB-099' if a.media_id==2504 else 'WEB-098'));folder.mkdir(parents=True,exist_ok=True)
path=folder/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-fixture-stop.json')
report=dict(intent=True,mediaId=a.media_id,before=before)
with path.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
report['receipt']=mcp('media.control',context='123c8282e1ee',operation='stop')
path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(accepted=report['receipt'].get('accepted'),report=str(path))))
