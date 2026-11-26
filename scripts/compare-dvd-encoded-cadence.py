#!/usr/bin/env python3
"""Isolated 10-second encode/decode cadence comparison on unchanged ALADDIN.

Requires no recordings/encoders and the exact phone to have stopped its DVD.
Writes no server files. This is diagnostic evidence, not physical playback.
"""
import argparse,importlib.util,json,shlex,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--case',choices=('help','source','qsv','x264','qsv-no-pic-timing','qsv-progressive','qsv-deint'),required=True)
p.add_argument('--offset',type=int,default=50,help='Bounded offset in unchanged first title VOB')
a=p.parse_args()
if not 0<=a.offset<=900:p.error('Require0..900s source offset')
activity=C.activity(cfg)
state=C.request(cfg,'/v1/control',dict(action='ui.state',context='123c8282e1ee'),mcp=True)
peers=C.request(cfg,'/v1/control',dict(action='ui.list'),mcp=True)
if activity['recordingCount'] or activity['connectedClientCount'] or peers['contexts']!=['123c8282e1ee'] or state.get('fullyLoaded') or state.get('loading'):
    raise RuntimeError('Require only exact stopped phone and no recordings')
with C.ssh(cfg) as client:
    container=shlex.quote(cfg['unraid_container_name'])
    processes=C.remote(client,'docker exec '+container+' ps -eo comm').splitlines()
    if any(x.strip() in ('ffmpeg.real','ffmpeg_MIM','SageTVTranscoder','ffmpeg-mim') for x in processes):raise RuntimeError('Do not compete with an active encoder')
    exe='/opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffmpeg.real'
    if a.case=='help':
        print(C.remote(client,'docker exec '+container+' '+exe+' -hide_banner -h encoder=h264_qsv'));raise SystemExit()
    vf="scale=w=-2:h='min(ih,480)':force_divisible_by=2,fps=24000/1001,format=nv12,setpts=PTS-STARTPTS"
    if a.case=='qsv-progressive':vf+=',setfield=prog'
    if a.case=='qsv-deint':vf+=',bwdif=mode=send_frame:deint=all'
    args=[exe,'-hide_banner','-nostdin','-loglevel','warning','-ss',str(a.offset),'-fflags','+genpts+discardcorrupt',
      '-f','mpeg','-i','/var/media/videos/Aidens_Movies/ALADDIN/VIDEO_TS/VTS_01_1.VOB',
      '-t','10','-map','0:v:0','-an','-sn','-dn','-vf',vf,'-c:v','libx264' if a.case=='x264' else 'h264_qsv',
      '-preset','veryfast','-b:v','1000k','-maxrate','1250k','-bufsize','2000k','-bf','0','-g','15',
      '-force_key_frames','expr:gte(t,n_forced*0.5)']
    if a.case!='x264':args+=['-async_depth','1','-forced_idr','1']
    if a.case=='qsv-no-pic-timing':args+=['-pic_timing_sei','0']
    args+=['-f','mpegts','pipe:1']
    decode=[exe,'-hide_banner','-nostdin','-loglevel','error','-f','mpegts','-i','pipe:0',
      '-an','-vf','scale=96:64,format=gray','-fps_mode','passthrough','-f','rawvideo','pipe:1']
    if a.case=='source':
        args=[exe,'-hide_banner','-nostdin','-loglevel','warning','-ss',str(a.offset),'-f','mpeg','-i',
          '/var/media/videos/Aidens_Movies/ALADDIN/VIDEO_TS/VTS_01_1.VOB','-t','10','-map','0:v:0','-an',
          '-vf','scale=96:64,format=gray','-fps_mode','passthrough','-f','rawvideo','pipe:1']
        pipeline=' '.join(map(shlex.quote,args))
    else:pipeline='set -o pipefail; '+' '.join(map(shlex.quote,args))+' | '+' '.join(map(shlex.quote,decode))
    command='docker exec '+container+' timeout 35s bash -c '+shlex.quote(pipeline)
    start=time.monotonic();_,stdout,stderr=client.exec_command(command,timeout=45)
    raw=stdout.read();error=stderr.read().decode(errors='replace');code=stdout.channel.recv_exit_status()
    size=96*64
    if code or not raw or len(raw)%size:raise RuntimeError('Comparison failed '+str(code)+': '+error[-1200:])
    frames=[raw[i:i+size] for i in range(0,len(raw),size)]
    diffs=[sum(abs(x-y) for x,y in zip(a,b))/size for a,b in zip(frames,frames[1:])]
    report=dict(standalone=True,physicalPlaybackProof=False,case=a.case,offsetSeconds=a.offset,frames=len(frames),
      elapsedSeconds=round(time.monotonic()-start,3),command=args,
      changedByThreshold={str(t):sum(v>t for v in diffs) for t in (.1,.25,.5,1,2)},
      differences=diffs,warningCount=error.count('incompatible video parameters'),stderrTail=error[-4000:])
out=ROOT/'artifacts/active/WEB-099';out.mkdir(parents=True,exist_ok=True)
path=out/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-content-cadence-'+a.case+'.json')
with path.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(path=str(path),frames=len(frames),changes=report['changedByThreshold'],warnings=report['warningCount'],first30=[round(v,3) for v in diffs[:30]])))
