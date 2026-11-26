#!/usr/bin/env python3
"""Bounded WEB-043 encoder A/B using the captured plugin FFmpeg command.

Only the known canonical fixture and a12s output under exact owned /tmp roots.
No installation, server settings, Core, source media or user playback changes.
"""
import argparse,importlib.util,json,re,shlex,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
OUT=ROOT/'artifacts/active/WEB-043';stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
captured=json.loads((ROOT/'tests/fixtures/qsv-hls-startup-command.json').read_text(encoding='utf-8'))
base=shlex.split(captured['encoderCommands'][-1]);fixture='/var/media/OpenSageTV_Vibe_Tests/VibeCaptionTest-1080i-CEA608-90s-2s.ts'
if base[0]!='/opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffmpeg.real' or base[base.index('-i')+1]!=fixture:
    raise SystemExit('Unexpected executable/input in captured command')
parser=argparse.ArgumentParser();parser.add_argument('--recording',action='store_true');args=parser.parse_args()
if args.recording:
    fixture='/var/media/tv/Nightline-66287549-0.ts'
    base[base.index('-i')+1]=fixture
if C.activity(cfg).get('recordingCount')!=0:raise SystemExit('Defer while recording')
cases=[('baseline',[]),('forced-idr',['-forced_idr','1']),('closed-gop',['-flags','+cgop']),
       ('idr-closed',['-forced_idr','1','-flags','+cgop']),('frame-counter',[])]
if args.recording:cases=cases[:2]
rows=[];container=shlex.quote(cfg['unraid_container_name'])
with C.ssh(cfg) as client:
  if args.recording:
    metadata=json.loads(C.remote(client,'docker exec '+container+' /opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffprobe -v error -show_entries stream=index,codec_type -of json '+shlex.quote(fixture)))
    streams=metadata.get('streams',[])
    audio=next((s['index'] for s in streams if s.get('codec_type')=='audio'),None)
    if audio is None:raise RuntimeError('Recording has no audio track')
    base[base.index('0:1')]='0:'+str(audio)
  for label,extra in cases:
    directory='/tmp/sagetv-webplayer-hls/web043-gop-'+uuid.uuid4().hex
    if not re.fullmatch('/tmp/sagetv-webplayer-hls/web043-gop-[a-f0-9]{32}',directory):raise RuntimeError('Invalid target')
    C.remote(client,'docker exec '+container+' mkdir -m 700 -- '+shlex.quote(directory))
    command=[x.replace('/tmp/sagetv-webplayer-hls/<test-session>',directory) for x in base]
    output_index=command.index('-f',command.index('-i')+2)
    command[output_index:output_index]=['-t','12']+extra
    if label=='frame-counter':command[command.index('-force_key_frames')+1]='expr:gte(n,n_forced*30)'
    started=time.monotonic();first=None
    _,stdout,stderr=client.exec_command('docker exec '+container+' '+' '.join(shlex.quote(s) for s in command),timeout=90)
    while not stdout.channel.exit_status_ready() and time.monotonic()-started<60:
      if first is None:
        try:
          C.remote(client,'docker exec '+container+' test -f '+shlex.quote(directory+'/seg_00000.ts'))
          first=round((time.monotonic()-started)*1000)
        except RuntimeError:pass
      time.sleep(.15)
    if not stdout.channel.exit_status_ready():raise RuntimeError('Bounded12s benchmark did not finish')
    code=stdout.channel.recv_exit_status();err=stderr.read().decode(errors='replace')[-3000:]
    playlist=C.remote(client,'docker exec '+container+' cat '+shlex.quote(directory+'/stream.m3u8')) if code==0 else ''
    row={'case':label,'exit':code,'elapsedMs':round((time.monotonic()-started)*1000),'firstSegmentObservedMs':first,
      'segmentSeconds':[float(x) for x in re.findall(r'#EXTINF:([0-9.]+)',playlist)],'stderr':err}
    rows.append(row);print(json.dumps(row),flush=True)
    # Remove only enumerated generated files in this exact single-use root.
    # No recursive delete/glob; unexpected files remain for investigation.
    files=C.remote(client,'docker exec '+container+' find '+shlex.quote(directory)+' -maxdepth 1 -type f -printf '+shlex.quote('%f\n')).splitlines()
    if any(not re.fullmatch(r'(?:seg_[0-9]{5}\.ts|stream\.m3u8|progress\.log)',name) for name in files):
      raise RuntimeError('Unexpected benchmark file; preserve exact root '+directory)
    if files:C.remote(client,'docker exec '+container+' rm -- '+' '.join(shlex.quote(directory+'/'+name) for name in files))
    C.remote(client,'docker exec '+container+' rmdir -- '+shlex.quote(directory))
(OUT/(stamp+'-gop-ab.json')).write_text(json.dumps({'fixture':fixture,'outputSeconds':12,'stockCoreUnchanged':True,'cases':rows},indent=2)+'\n',encoding='utf-8')
