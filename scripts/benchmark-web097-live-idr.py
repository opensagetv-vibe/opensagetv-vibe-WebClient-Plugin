#!/usr/bin/env python3
"""Bounded exact-prefix encoder comparison; not a physical/live-source gate.

Replay the captured default HLS command against the canonical owned prefix,
keeping its raw stdin open after the prefix like temporary growing-file EOF.
Only an optional QSV forced-IDR argument changes between cases. No server
settings, source, plugin installation, Core, recording or playback mutation.
"""
import argparse,importlib.util,json,re,shlex,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--original-completion',action='store_true',help='One full retained owned recording/raw-pipe completion,600s bound; no A/B')
a=p.parse_args()
out=ROOT/'artifacts/active/WEB-097';out.mkdir(parents=True,exist_ok=True)
path=out/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-held-raw-idr-ab.json')
baseline=json.loads((ROOT/'tests/fixtures/web097-default-hls-command.json').read_text())
fixture='/var/media/OpenSageTV_Vibe_Tests/WEB097_LIVE_WTTW_STARTUP.ts'
expected='a73042ed73a4514c76e2a18449298f842e9ecca8c780e09b371e2191f7771d9c'
wrapper='/opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffmpeg_MIM'
rows=[];report=dict(passed=False,syntheticHeldInput=True,physicalPhone=False,fixture=fixture,rows=rows)
if a.original_completion:
 fixture='/var/media/tv/OddSquad-ItTakesGootoMakeaFeudGoRightFriendsofOddSquad-43057-0.ts'
 report.update(fixture=fixture,syntheticHeldInput=False,originalOwnedRecording=True)

def save():
 path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')

def idle(client):
 a=C.activity(cfg)
 if a['recordingCount'] or a['connectedClientCount']:raise RuntimeError('Require no recordings or other clients')
 contexts=C.request(cfg,'/v1/control',dict(action='ui.list'),mcp=True)['contexts']
 if contexts not in ([],['123c8282e1ee']):raise RuntimeError('Unrelated native UI')
 if contexts and C.request(cfg,'/v1/control',dict(action='ui.state',context=contexts[0]),mcp=True).get('fullyLoaded'):raise RuntimeError('Phone media loaded')
 lines=C.remote(client,'docker exec '+shlex.quote(cfg['unraid_container_name'])+' ps -eo comm').splitlines()
 if any(x.strip() in ('ffmpeg.real','ffmpeg_MIM','SageTVTranscoder','ffmpeg-mim') for x in lines):raise RuntimeError('Another encoder active')

try:
 base=shlex.split(baseline['encoderCommand']);old=base[-1].rsplit('/',1)[0]
 if base[0]!=wrapper or old!='/tmp/sagetv-webplayer-hls/<test-session>' or '-forced_idr' in base or base[base.index('-c:v')+1]!='h264_qsv':raise RuntimeError('Captured default command identity changed')
 if base[base.index('-i')+1]!='/var/media/tv/OddSquad-ItTakesGootoMakeaFeudGoRightFriendsofOddSquad-43057-0.ts':raise RuntimeError('Unexpected captured source')
 base[base.index('-i')+1]='pipe:0'
 container=shlex.quote(cfg['unraid_container_name'])
 with C.ssh(cfg) as client:
  idle(client)
  if a.original_completion:
   media=C.request(cfg,'/SageTVWebPlayer/api/media?id=84256')
   if media.get('id')!=84256 or media.get('recording') or len(media['files'])!=1 or media['files'][0]['path']!=fixture or media['files'][0]['streamSize']!=1279502996:raise RuntimeError('Retained exact source identity changed')
   report['sourceBytes']=media['files'][0]['streamSize']
   probe=['docker','exec',cfg['unraid_container_name'],'/opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffprobe','-v','error','-show_entries','format=duration','-of','json',fixture]
   report['sourceDurationMs']=float(json.loads(C.remote(client,' '.join(map(shlex.quote,probe))))['format']['duration'])*1000
   if not 1200000<report['sourceDurationMs']<1400000:raise RuntimeError('Original actual duration changed; airing duration is not a file oracle')
   available=int(C.remote(client,'docker exec '+container+' df -PB1 /tmp/sagetv-webplayer-hls').splitlines()[-1].split()[3])
   report['availableOutputBytesBefore']=available
   if available<report['sourceBytes']*2+268435456:raise RuntimeError('Insufficient safe temporary output headroom; no disk-pressure test')
  elif C.remote(client,'docker exec '+container+' sha256sum '+shlex.quote(fixture)).split()[0]!=expected:raise RuntimeError('Canonical source checksum changed')
  for label in (('original-forced-idr',) if a.original_completion else ('baseline','forced-idr')):
   idle(client)
   directory=C.remote(client,'docker exec '+container+' mktemp -d /tmp/sagetv-webplayer-hls/web097-held.XXXXXXXX').strip()
   if not re.fullmatch(r'/tmp/sagetv-webplayer-hls/web097-held\.[A-Za-z0-9]{8}',directory):raise RuntimeError('Unexpected temporary root')
   command=[v.replace(old,directory) for v in base]
   if label!='baseline':
    index=command.index('-c:v')+2;command[index:index]=['-forced_idr','1']
   # No output duration cap: early encoder flush would hide the boundary defect.
   # GNU timeout owns only this new shell/pipeline group, never a server process.
   feed='cat -- '+shlex.quote(fixture)
   if not a.original_completion:feed='('+feed+'; sleep 22)'
   shell=feed+' | '+' '.join(map(shlex.quote,command))
   limit=600 if a.original_completion else 32
   started=time.monotonic();first=None;error_tail=b'';next_progress=20
   _,stdout,stderr=client.exec_command('docker exec '+container+' timeout --signal=TERM --kill-after=3s '+str(limit)+'s sh -c '+shlex.quote(shell),timeout=limit+8)
   while not stdout.channel.exit_status_ready() and time.monotonic()-started<limit+6:
    while stdout.channel.recv_stderr_ready():error_tail=(error_tail+stdout.channel.recv_stderr(8192))[-4000:]
    while stdout.channel.recv_ready():stdout.channel.recv(8192)
    if first is None:
     try:
      C.remote(client,'docker exec '+container+' test -s '+shlex.quote(directory+'/stream.m3u8'))
      first=round((time.monotonic()-started)*1000)
     except RuntimeError:pass
    if a.original_completion and time.monotonic()-started>=next_progress:
     print(json.dumps(dict(observingOriginalRaw=True,elapsedSeconds=round(time.monotonic()-started,1),firstPlaylistMs=first)),flush=True)
     next_progress+=20
    time.sleep(.2)
   if not stdout.channel.exit_status_ready():raise RuntimeError('Owned timeout did not settle; preserve '+directory)
   code=stdout.channel.recv_exit_status();error=(error_tail+stderr.read()).decode(errors='replace')[-4000:]
   playlist=C.remote(client,'docker exec '+container+' cat '+shlex.quote(directory+'/stream.m3u8')) if code==0 else ''
   row=dict(case=label,exit=code,elapsedMs=round((time.monotonic()-started)*1000),firstPlaylistMs=first,
    segmentSeconds=[float(x) for x in re.findall(r'#EXTINF:([0-9.]+)',playlist)],stderr=error,directory=directory)
   rows.append(row);save();print(json.dumps(row),flush=True)
   if code:raise RuntimeError('Owned comparison failed; retain exact root '+directory)
   names=C.remote(client,'docker exec '+container+' find '+shlex.quote(directory)+' -maxdepth 1 -type f -printf '+shlex.quote('%f\n')).splitlines()
   if any(not re.fullmatch(r'(seg_[0-9]{5,}\.ts|stream\.m3u8)',n) for n in names):raise RuntimeError('Unexpected output; preserve exact root '+directory)
   if names:C.remote(client,'docker exec '+container+' rm -- '+' '.join(shlex.quote(directory+'/'+n) for n in names))
   C.remote(client,'docker exec '+container+' rmdir -- '+shlex.quote(directory))
   row['ownedTemporaryOutputRemoved']=True;save()
  report['passed']=len(rows)==(1 if a.original_completion else 2) and all(r['exit']==0 and r['segmentSeconds'] for r in rows)
  if a.original_completion:
   report['outputSeconds']=sum(rows[0]['segmentSeconds'])
   report['passed']=report['passed'] and abs(report['outputSeconds']-report['sourceDurationMs']/1000)<2
  else:report['idrImprovesPreTimeoutBoundary']=bool((rows[0]['firstPlaylistMs'] is None or rows[0]['firstPlaylistMs']>15000) and rows[1]['firstPlaylistMs'] is not None and rows[1]['firstPlaylistMs']<15000)
except Exception as e:report.update(errorType=type(e).__name__,error=str(e)[:300])
finally:save()
print(json.dumps(dict(passed=report['passed'],report=str(path),error=report.get('error'))))
raise SystemExit(0 if report['passed'] else 1)
