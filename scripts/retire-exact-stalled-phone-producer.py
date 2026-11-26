#!/usr/bin/env python3
"""Release only the proven test-owned pipe deadlock, never replay API Stop."""
import importlib.util,json,shlex,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration()
job=json.loads((ROOT/'artifacts/active/WP11-008/20261119T120802Z-iphone-growing-recording.json').read_text(encoding='utf-8'))
producer=job['startup']['session']
if producer!='d32809033c0f4f08bdd567bf146482d3' or job['ownership']['mediaId']!=84256 or 'Owned producer Stop unknown; no replay' not in job.get('cleanup',[]):raise RuntimeError('Exact owned deadlock proof absent')
a=C.activity(cfg);contexts=C.request(cfg,'/v1/control',dict(action='ui.list'),mcp=True)['contexts']
if a['recordingCount'] or a['connectedClientCount'] or contexts!=['123c8282e1ee']:raise RuntimeError('Unrelated current activity; no cleanup')
script=r'''
import os,signal,time,json,hashlib
from pathlib import Path
token=b'/tmp/sagetv-webplayer-hls/d32809033c0f4f08bdd567bf146482d3/'
root,child=7468,7474
expected={root:b'/opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffmpeg_MIM',child:b'/opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffmpeg.real'}
proof={}
for pid,exe in expected.items():
 p=Path('/proc')/str(pid);cmd=(p/'cmdline').read_bytes();stat=(p/'stat').read_text();tail=stat[stat.rfind(')')+2:].split()
 if cmd.split(b'\0')[0]!=exe or token not in cmd or (pid==child and int(tail[1])!=root):raise RuntimeError('PID/path/parent ownership changed; preserved')
 proof[pid]=dict(start=tail[19],sha256=hashlib.sha256(cmd).hexdigest())
os.kill(child,signal.SIGKILL)
time.sleep(2)
p=Path('/proc')/str(root)
if p.exists():
 stat=(p/'stat').read_text();tail=stat[stat.rfind(')')+2:].split()
 if tail[19]!=proof[root]['start']:raise RuntimeError('Parent PID identity changed; preserved')
 os.kill(root,signal.SIGKILL)
print(json.dumps(dict(ownedProcessTreeReleased=True,pids=[child,root],publicStopReplayed=False,proof=proof)))
'''
out=ROOT/'artifacts/active/WP11-008'/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-exact-stalled-producer-cleanup.json')
plan=dict(producer=producer,mediaId=84256,pids=[7468,7474],intent=True)
with out.open('x',encoding='utf-8') as f:json.dump(plan,f,indent=2)
with C.ssh(cfg) as ssh:
 shell=r'''
set -eu
test "$(cat /proc/7468/comm)" = ffmpeg_MIM
test "$(cat /proc/7474/comm)" = ffmpeg.real
test "$(awk '{print $4}' /proc/7474/stat)" = 7468
test "$(readlink /proc/7468/exe)" = /opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffmpeg_MIM
test "$(readlink /proc/7474/exe)" = /opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffmpeg.real
for pid in 7468 7474; do
 case "$(tr '\000' ' ' < /proc/$pid/cmdline)" in
  *'/tmp/sagetv-webplayer-hls/d32809033c0f4f08bdd567bf146482d3/'*) ;;
  *) exit 61 ;;
 esac
done
start=$(awk '{print $22}' /proc/7468/stat)
kill -KILL 7474
sleep 2
if test -e /proc/7468/stat; then
 test "$(awk '{print $22}' /proc/7468/stat)" = "$start"
 kill -KILL 7468
fi
printf '{"ownedProcessTreeReleased":true,"pids":[7474,7468],"publicStopReplayed":false}'
'''
 result=json.loads(C.remote(ssh,'docker exec -u 99 '+shlex.quote(cfg['unraid_container_name'])+' sh -c '+shlex.quote(shell)))
plan['result']=result;out.write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(result=result,report=str(out))))
