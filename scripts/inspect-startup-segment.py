#!/usr/bin/env python3
"""Read only a current, exact WEB-043 fixture generation via host SSH identity."""
import argparse,importlib.util,json,re,shlex,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
p=argparse.ArgumentParser();p.add_argument('--stamp',required=True);p.add_argument('--task',choices=['WEB-043','WEB-044'],default='WEB-043');args=p.parse_args()
if not re.fullmatch('[0-9]{8}T[0-9]{4,6}Z',args.stamp):raise SystemExit('Invalid stamp')
out=ROOT/'artifacts/active'/args.task;marker=out/(args.stamp+'-probe-request.json');destination=out/(args.stamp+'-probe-result.json')
if destination.exists() or marker.exists():raise SystemExit('Require fresh marker/result paths')
deadline=time.monotonic()+60
while not marker.exists() and time.monotonic()<deadline:time.sleep(.25)
if not marker.exists():raise SystemExit('No fresh owned probe request')
request=json.loads(marker.read_text(encoding='utf-8'))
if request.get('client')!='da92a86446be' or request.get('fixture')!='/var/media/OpenSageTV_Vibe_Tests/VibeCaptionTest-1080i-CEA608-90s-2s.ts':raise SystemExit('Unexpected probe scope')
for key in ('nativeSession','hlsSession'):
    if not re.fullmatch('[a-f0-9]{32}',request.get(key,'')):raise SystemExit('Invalid session')
if not time.time()<request.get('expiresAt',0)<time.time()+46:raise SystemExit('Expired/invalid marker')
cfg=C.configuration()
active=C.request(cfg,'/SageTVWebPlayer/api/miniclient?action=streamSettings&session='+request['nativeSession'])
if active.get('session')!=request['hlsSession']:raise SystemExit('Owned HLS generation changed')
hls=request['hlsSession'];directory='/tmp/sagetv-webplayer-hls/'+hls
with C.ssh(cfg) as client:
    container=shlex.quote(cfg['unraid_container_name'])
    # Capture the actual bridge/FFmpeg commands while the first GOP is still
    # encoding, not after playback has already consumed the entire short file.
    commands=C.remote(client,'docker exec '+container+' ps -eo args')
    deadline=min(time.time()+25,request['expiresAt']-5)
    while time.time()<deadline:
        status=C.request(cfg,'/SageTVWebPlayer/api/hls?session='+hls)
        if status.get('playlistReady'):break
        time.sleep(.25)
    else:raise SystemExit('First playlist not published during probe lease')
    playlist=C.remote(client,'docker exec '+container+' cat '+shlex.quote(directory+'/stream.m3u8'))
    if len(playlist)>16384:raise SystemExit('Playlist exceeds fixture bound')
    probe=['docker','exec',cfg['unraid_container_name'],'/opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffprobe',
      '-v','error','-skip_frame','nokey','-select_streams','v:0','-show_frames','-show_streams','-show_entries',
      'frame=best_effort_timestamp_time,key_frame,pict_type:stream=codec_name,start_time,duration,r_frame_rate',
      '-of','json',directory+'/seg_00000.ts']
    data=json.loads(C.remote(client,' '.join(shlex.quote(s) for s in probe)))
    metadata=['docker','exec',cfg['unraid_container_name'],'/opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffprobe',
      '-v','error','-show_entries','format=start_time,duration:stream=codec_name,start_time,r_frame_rate,field_order','-of','json',request['fixture']]
    result={'playlist':playlist,'firstSegmentProbe':data,
      'sourceMetadata':json.loads(C.remote(client,' '.join(shlex.quote(s) for s in metadata))),
      'encoderCommands':[s.replace(hls,'<test-session>') for s in commands.splitlines() if hls in s]}
if time.time()>request['expiresAt']:raise SystemExit('Probe lease expired')
destination.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
