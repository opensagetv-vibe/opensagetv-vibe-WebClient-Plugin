#!/usr/bin/env python3
"""Read-only exact phone/ALADDIN encoder and published-frame cadence witness.

No phone inspector, controls, producer restart, source edits or extra encode.
"""
import argparse,importlib.util,json,re,shlex,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration()
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--session',required=True,help='Exact HLS UUID independently observed from the current phone video URL')
args=parser.parse_args()
if not re.fullmatch(r'[a-f0-9]{32}',args.session):parser.error('Invalid observed session UUID')
def mcp(action,**kw):return C.request(cfg,'/v1/control',dict(action=action,**kw),mcp=True)
activity=C.activity(cfg);state=mcp('ui.state',context='123c8282e1ee')
if activity['recordingCount'] or activity['connectedClientCount'] or mcp('ui.list')['contexts']!=['123c8282e1ee'] or not state.get('dvd') or (state.get('media') or {}).get('mediaFileId')!=2504:raise RuntimeError('Require only exact phone/ALADDIN ownership')
with C.ssh(cfg) as client:
 container=shlex.quote(cfg['unraid_container_name'])
 commands=C.remote(client,'docker exec '+container+' ps -eo pid,ppid,args').splitlines()
 hls=args.session;directory='/tmp/sagetv-webplayer-hls/'+hls
 status=C.request(cfg,'/SageTVWebPlayer/api/hls?session='+hls)
 if not status.get('dvd') or status.get('session')!=hls or status.get('mediaId') not in (-1,0,2504):raise RuntimeError('Not observed native DVD HLS')
 playlist=C.remote(client,'docker exec '+container+' cat '+shlex.quote(directory+'/stream.m3u8'))
 files=re.findall(r'(?m)^(seg_[0-9]{5,}\.ts)\s*$',playlist)
 if len(files)<2:raise RuntimeError('Require two atomically published segments')
 def probe(path,frames=False):
  args=['docker','exec',cfg['unraid_container_name'],'timeout','15s','/opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffprobe','-v','error','-analyzeduration','1000000','-probesize','2000000','-select_streams','v:0']
  if frames:args+=['-read_intervals','%+3','-show_frames']
  args+=['-show_entries','stream=codec_name,r_frame_rate,avg_frame_rate,field_order,width,height:frame=best_effort_timestamp_time,pkt_duration_time,repeat_pict,interlaced_frame,top_field_first','-of','json',path]
  return json.loads(C.remote(client,' '.join(shlex.quote(v) for v in args)))
 output=probe(directory+'/'+files[-2],True)
 source=probe('/var/media/videos/Aidens_Movies/ALADDIN/VIDEO_TS/VTS_01_1.VOB',True)
 # Decode a bounded published segment window, never the growing last file.
 # Actual changing pictures are distinct from frame/PTS counters.
 selected=files[-22:-2]
 concat='concat:'+'|'.join(directory+'/'+name for name in selected)
 decode=['docker','exec',cfg['unraid_container_name'],'timeout','15s',
   '/opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffmpeg.real',
   '-hide_banner','-nostdin','-loglevel','error','-i',concat,'-t','10','-an',
   '-vf','scale=96:64,format=gray','-fps_mode','passthrough','-f','rawvideo','pipe:1']
 _,stdout,stderr=client.exec_command(' '.join(map(shlex.quote,decode)),timeout=20)
 raw=stdout.read();error=stderr.read().decode(errors='replace');code=stdout.channel.recv_exit_status()
 size=96*64
 if code or not raw or len(raw)%size:raise RuntimeError('Published-frame decode failed: '+error[-400:])
 frames=[raw[i:i+size] for i in range(0,len(raw),size)]
 diffs=[sum(abs(x-y) for x,y in zip(a,b))/size for a,b in zip(frames,frames[1:])]
 content=dict(frames=len(frames),segments=selected,differences=diffs,
   changedByThreshold={str(t):sum(v>t for v in diffs) for t in (.1,.25,.5,1,2)})
 # No full command environment/credentials; only exact owned encoder argv.
 owned=[line.replace(hls,'<owned-session>') for line in commands if directory+'/' in line]
 report=dict(readOnly=True,actualPhone=True,physicalFingerGesture=False,activity=activity,native=state,hls=status,publishedSegment=files[-2],output=output,source=source,contentCadence=content,ownedEncoderCommands=owned)
out=ROOT/'artifacts/active/WEB-099';out.mkdir(parents=True,exist_ok=True)
path=out/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-dvd-motion.json')
with path.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(path=str(path),outputStreams=output.get('streams'),sourceStreams=source.get('streams'),outputFrames=len(output.get('frames',[])),sourceFrames=len(source.get('frames',[])),effective={k:status.get(k) for k in ('hardware','hardwareDecode','hardwareFilters','encoder','accelerator','decodeAccelerator','fallbackStage')})))
