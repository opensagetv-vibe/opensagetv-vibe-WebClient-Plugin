#!/usr/bin/env python3
"""One bounded public HLS producer for the exact retained WEB097 recording.

No Core Watch, bookmark/recording mutation, source edit or control replay.
This completed-file comparison is not a growing-file completion certificate.
"""
import argparse,importlib.util,json,shlex,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--profile',choices=('default',),required=True);a=p.parse_args()
out=ROOT/'artifacts/active/WEB-097';out.mkdir(parents=True,exist_ok=True)
path=out/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-completed-hls-'+a.profile+'.json')
report=dict(passed=False,completedSource=True,physicalPhone=False,profile=a.profile,rows=[],cleanup=[]);owner=None
def save():
 with path.open('w',encoding='utf-8') as f:json.dump(report,f,indent=2)
def status():return C.request(cfg,'/SageTVWebPlayer/api/hls?session='+owner)
def encoders(ssh):
 rows=C.remote(ssh,'docker exec '+shlex.quote(cfg['unraid_container_name'])+' ps -eo pid,ppid,comm,args').splitlines()
 return [r for r in rows if len(r.split())>2 and r.split()[2] in ('ffmpeg.real','ffmpeg_MIM','SageTVTranscoder','ffmpeg-mim')]
try:
 activity=C.activity(cfg);ui=C.request(cfg,'/v1/control',dict(action='ui.list'),mcp=True)['contexts']
 if activity['recordingCount'] or activity['connectedClientCount'] or ui not in ([],['123c8282e1ee']):raise RuntimeError('Require no unrelated activity')
 if ui and C.request(cfg,'/v1/control',dict(action='ui.state',context=ui[0]),mcp=True).get('fullyLoaded'):raise RuntimeError('Phone has loaded media')
 media=C.request(cfg,'/SageTVWebPlayer/api/media?id=84256')
 expected='/var/media/tv/OddSquad-ItTakesGootoMakeaFeudGoRightFriendsofOddSquad-43057-0.ts'
 if media.get('id')!=84256 or media.get('recording') or len(media['files'])!=1 or media['files'][0]['path']!=expected or media['files'][0]['streamSize']!=1279502996:raise RuntimeError('Retained source identity changed')
 with C.ssh(cfg) as ssh:
  if encoders(ssh):raise RuntimeError('Another encoder active')
  protected=C.remote(ssh,'docker exec -w /opt/sagetv/server '+shlex.quote(cfg['unraid_container_name'])+' sha256sum -c /usr/local/share/sagetv-stock/protected.sha256')
  if protected.count(': OK')!=20:raise RuntimeError('Stock boundary failed')
 values=dict(action='start',id=84256,start=0,segment=0,audio=0)
 report['startIntent']=True;save();t=time.monotonic()
 result=C.request(cfg,'/SageTVWebPlayer/api/hls',values,timeout=60);owner=result.get('session');report['start']=result;save()
 if not owner or result.get('mediaId')!=84256:raise RuntimeError('Exact producer not acknowledged; no replay')
 while time.monotonic()-t<75:
  h=status();report['rows'].append(dict(elapsed=round(time.monotonic()-t,3),**{k:h.get(k) for k in ('running','segments','hlsSeconds','bytesInput','bytesProduced','error','exitCode','endList','activeRecording','fallbackStage','hardware','hardwareDecode','hardwareFilters','encoder','inputMode')}));save()
  if h.get('playlistReady') and h.get('segments',0)>0:
   report['firstReadySeconds']=round(time.monotonic()-t,3)
   with C.ssh(cfg) as ssh:report['ownedCommands']=[r for r in encoders(ssh) if owner in r]
   time.sleep(5);report['final']=status();report['passed']=report['final'].get('segments',0)>0 and not report['final'].get('error');break
  if not h.get('running') and h.get('exitCode') not in (None,-2147483648):raise RuntimeError('Producer failed before ready')
  time.sleep(.25)
 else:raise RuntimeError('Startup observation timed out')
except Exception as e:report.update(errorType=type(e).__name__,error=str(e)[:250])
finally:
 if owner:
  report['stopIntent']=True;save();started=time.monotonic()
  try:
   stopped=C.request(cfg,'/SageTVWebPlayer/api/hls',dict(action='stop',session=owner),timeout=20)
   report['stopSeconds']=round(time.monotonic()-started,3);report['stopped']=stopped.get('stopped')
   if not report['stopped']:raise RuntimeError('Stop rejected')
   with C.ssh(cfg) as ssh:
    left=encoders(ssh);report['encodersAfter']=left
    if left:raise RuntimeError('Encoder retirement not independently confirmed')
  except Exception as e:report['cleanup'].append(type(e).__name__+': bounded Stop unknown; no replay')
 report['passed']=report['passed'] and not report['cleanup'];save()
print(json.dumps(dict(passed=report['passed'],report=str(path),firstReadySeconds=report.get('firstReadySeconds'),stopSeconds=report.get('stopSeconds'),error=report.get('error'),cleanup=report['cleanup'])))
raise SystemExit(0 if report['passed'] else 1)
