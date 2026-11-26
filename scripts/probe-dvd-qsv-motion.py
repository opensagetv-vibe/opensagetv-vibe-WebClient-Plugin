#!/usr/bin/env python3
"""Bounded standalone encoder comparison, not stock-DVD/browser playback proof.

Reads one unchanged ALADDIN VOB, writes only the null muxer, and records the
diagnostic locally. No source, server settings, installed runtime or controls
are changed. Requires the independently observed failed phone HLS generation.
"""
import argparse,importlib.util,json,shlex,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--case',choices=('baseline','progressive','async-one','no-forced-idr'),required=True)
a=p.parse_args()
activity=C.activity(cfg)
state=C.request(cfg,'/v1/control',dict(action='ui.state',context='123c8282e1ee'),mcp=True)
peers=C.request(cfg,'/v1/control',dict(action='ui.list'),mcp=True)
if activity['recordingCount'] or activity['connectedClientCount'] or peers['contexts']!=['123c8282e1ee'] or not state.get('dvd') or (state.get('media') or {}).get('mediaFileId')!=2504:raise RuntimeError('Require only exact phone/ALADDIN ownership')
status=C.request(cfg,'/SageTVWebPlayer/api/hls?session=15fa27bb92354136a769cd97824239d6')
if status.get('running') or status.get('exitCode')!=139 or not status.get('dvd'):raise RuntimeError('Require observed stopped DVD producer')
with C.ssh(cfg) as client:
    processes=C.remote(client,'docker exec '+shlex.quote(cfg['unraid_container_name'])+' ps -eo comm').splitlines()
    if any(x.strip() in ('ffmpeg.real','ffmpeg_MIM','SageTVTranscoder','ffmpeg-mim') for x in processes):raise RuntimeError('Do not compete with an active encoder')
    vf="scale=w=-2:h='min(ih,480)':force_divisible_by=2,fps=24000/1001,format=nv12,setpts=PTS-STARTPTS"
    if a.case=='progressive':vf+=',setfield=prog'
    args=['docker','exec',cfg['unraid_container_name'],'timeout','60s','/opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffmpeg.real',
      '-hide_banner','-loglevel','warning','-nostdin','-nostats','-progress','pipe:1',
      '-thread_queue_size','1024','-fflags','+genpts+discardcorrupt','-err_detect','ignore_err',
      '-analyzeduration','2000000','-probesize','4000000','-f','mpeg','-i',
      '/var/media/videos/Aidens_Movies/ALADDIN/VIDEO_TS/VTS_01_1.VOB',
      '-t','130','-map','0:v:0?','-map','0:i:0x80?','-sn','-dn','-vf',vf,'-c:v','h264_qsv','-preset','veryfast',
      '-b:v','1000k','-maxrate','1250k','-bufsize','2000k','-bf','0','-g','15','-force_key_frames','expr:gte(t,n_forced*0.5)']
    if a.case!='no-forced-idr':args+=['-forced_idr','1']
    if a.case=='async-one':args+=['-async_depth','1']
    args+=['-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-af','aresample=async=1000:first_pts=0','-f','null','-']
    started=time.monotonic()
    _,stdout,stderr=client.exec_command(' '.join(shlex.quote(x) for x in args),timeout=80)
    progress=stdout.read().decode(errors='replace');error=stderr.read().decode(errors='replace')
    code=stdout.channel.recv_exit_status()
    report=dict(standalone=True,physicalPlaybackProof=False,case=a.case,exitCode=code,elapsedSeconds=round(time.monotonic()-started,3),command=args,progressTail=progress[-6000:],stderrTail=error[-6000:])
out=ROOT/'artifacts/active/WEB-099';out.mkdir(parents=True,exist_ok=True)
path=out/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-qsv-'+a.case+'.json')
with path.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(path=str(path),exitCode=code,elapsedSeconds=report['elapsedSeconds'],progress=progress[-450:],stderr=error[-1500:])))
