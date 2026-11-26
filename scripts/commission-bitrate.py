#!/usr/bin/env python3
"""Bounded WEB-029 stock232 test on the already approved iPhone test UI.

Use existing MCP public Watch, never Core/private commands. Status inspects
only this exact UI's transcoder process and completed output segments. No
credentials or session bearer values are emitted; no other session is stopped.
"""
import argparse, importlib.util, json, re, shlex
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('commission', ROOT/'scripts/commission-mobile.py')
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
p = argparse.ArgumentParser(); p.add_argument('action', choices=['watch', 'status'])
p.add_argument('--session'); args = p.parse_args(); cfg = C.configuration()
if args.action == 'watch':
    activity = C.activity(cfg)
    contexts = C.request(cfg, '/v1/control', {'action':'ui.list'}, mcp=True).get('contexts')
    if activity.get('recordingCount') != 0 or activity.get('connectedClientCount') != 0 or contexts != ['123c8282e1ee']:
        raise RuntimeError('Expected only approved iPhone test UI, no recordings/other clients')
    result = C.request(cfg, '/v1/control', {'action':'media.watch', 'context':'123c8282e1ee', 'media_id':25387, 'wait_ms':0}, mcp=True)
    print(json.dumps({'accepted':result.get('accepted'), 'testMediaId':25387}))
else:
    if not args.session or not re.fullmatch('[a-f0-9]{32}', args.session):
        raise ValueError('Exact observed HLS session required')
    st = C.request(cfg, '/SageTVWebPlayer/api/hls?session='+args.session)
    safe = {k:st.get(k) for k in ['running','segments','hlsSeconds','bytesProduced','encoder','hardware','hardwareDecode','hardwareFilters','streamSettings','error']}
    profile = st.get('streamSettings') or {}
    safe['streamSettings'] = {
        'requested':{k:(profile.get('requested') or {}).get(k) for k in ['videoKbps','videoMode','encoder','resolution','fps','audioKbps']},
        'effective':{k:(profile.get('effective') or {}).get(k) for k in ['video','videoTargetKbps','audioTargetKbps','decode','filters','hardwareEncode','hardwareDecode','endToEndGpu']}}
    safe['outputMuxAverageKbps'] = round((st.get('bytesProduced') or 0)*8/1000/st['hlsSeconds'], 1) if st.get('hlsSeconds',0)>0 else None
    with C.ssh(cfg) as client:
        # Restrict process evidence to this observed session's generated output.
        processes = C.remote(client, 'docker exec '+shlex.quote(cfg['unraid_container_name'])+' ps -eo args')
        rows = [line.strip() for line in processes.splitlines() if args.session in line and 'ffmpeg' in line]
        safe['encoderCommands'] = [line.replace(args.session, '<test-session>') for line in rows]
        samples = []
        for number in (5, 25, 50):
            if number >= (st.get('segments') or 0)-1:
                continue
            segment = '/tmp/sagetv-webplayer-hls/'+args.session+'/seg_'+str(number).zfill(5)+'.ts'
            command = ['docker','exec',cfg['unraid_container_name'],
                       '/opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffprobe',
                       '-v','error','-select_streams','v:0','-show_packets','-show_streams',
                       '-show_entries','packet=pts_time,duration_time,size:stream=codec_name,width,height',
                       '-of','json',segment]
            data = json.loads(C.remote(client, ' '.join(shlex.quote(s) for s in command)))
            packets = data.get('packets', [])
            starts = [float(row['pts_time']) for row in packets if 'pts_time' in row]
            ends = [float(row['pts_time'])+float(row.get('duration_time',0)) for row in packets if 'pts_time' in row]
            seconds = max(ends)-min(starts) if starts and ends else 0
            samples.append({'segmentNumber':number,'videoPayloadBytes':sum(int(row.get('size',0)) for row in packets),
                            'seconds':round(seconds,6),'videoKbps':round(sum(int(row.get('size',0)) for row in packets)*8/1000/seconds,1) if seconds>0 else None,
                            'streams':[{k:row.get(k) for k in ['codec_name','width','height']} for row in data.get('streams',[])]})
        safe['completedSegmentVideoSamples'] = samples
    print(json.dumps(safe, indent=2))
