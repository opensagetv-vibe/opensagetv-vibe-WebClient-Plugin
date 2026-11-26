#!/usr/bin/env python3
"""Read-only exact owned capture/producer after a field failure; no replay."""
import importlib.util,json,time,shlex
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration()
r=json.loads((ROOT/'artifacts/active/WP11-008/20261119T120802Z-iphone-growing-recording.json').read_text(encoding='utf-8'))
mid=r['ownership']['mediaId'];producer=r['startup']['session'];air=r['baseline']['source']['airingId']
result=dict(readOnly=True,mediaId=mid,producer=producer,airingId=air)
with C.ssh(cfg) as ssh:
 command='docker exec '+shlex.quote(cfg['unraid_container_name'])+' ps -eo pid,ppid,comm,args'
 lines=C.remote(ssh,command).splitlines()
 result['ownedProcessCandidates']=[line for line in lines if producer in line or line.strip().split()[:1] in (['7468'],['7474'])]
 result['ownedExecutableLinks']=C.remote(ssh,'docker exec '+shlex.quote(cfg['unraid_container_name'])+' readlink -f /proc/7468/exe /proc/7474/exe /opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffmpeg_MIM /opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffmpeg.real').splitlines()
 result['ownedProcessIdentity']=C.remote(ssh,'docker exec '+shlex.quote(cfg['unraid_container_name'])+' ps -o uid,pid,ppid,comm -p 7468,7474')
for name,path in (('activity',None),('media','/SageTVWebPlayer/api/media?id='+str(mid)),('recordingOptions','/SageTVWebPlayer/api/recording-options?airingId='+str(air)),('reservation','/SageTVWebPlayer/api/guide?action=recordStatus&airingId='+str(air)),('hls','/SageTVWebPlayer/api/hls?session='+producer),('guide','/SageTVWebPlayer/api/guide?hours=1')):
 try:
  value=C.activity(cfg) if path is None else C.request(cfg,path,timeout=8)
  if name=='hls':value={k:value.get(k) for k in ('session','mediaId','running','activeRecording','endList','exitCode','error','bytesInput','hlsSeconds','durationMs','threading','hardware','hardwareDecode','hardwareFilters','stderrTail')}
  if name=='guide':value=[{k:x.get(k) for k in ('airingId','mediaId','title','channelNumber','start','end','manualRecord','currentlyAiring')} for x in value['airings'] if x.get('currentlyAiring')]
  result[name]=value
 except Exception as e:result[name]=dict(readUnknown=True,error=str(e)[:180] if isinstance(e,RuntimeError) else type(e).__name__)
out=ROOT/'artifacts/active/WP11-008'/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-owned-completion-readback.json')
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='guide'}));print(str(out))
