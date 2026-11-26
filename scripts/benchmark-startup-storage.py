#!/usr/bin/env python3
"""WEB-044/047 bounded segment/storage comparison; never installs/mounts anything.

Only the canonical completed fixture, plugin FFmpeg,12 seconds of output and
fresh owned ordinary directories. Existing /dev/shm is tested with small output,
not selected as production storage. Always retire exact generated remote files.
"""
import importlib.util,json,re,shlex,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
OUT=ROOT/'artifacts/active/WEB-044';OUT.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
base=shlex.split(json.loads((ROOT/'tests/fixtures/qsv-hls-startup-command.json').read_text())['encoderCommands'][-1])
fixture='/var/media/OpenSageTV_Vibe_Tests/VibeCaptionTest-1080i-CEA608-90s-2s.ts'
assert base[0]=='/opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffmpeg.real' and base[base.index('-i')+1]==fixture
if C.activity(cfg).get('recordingCount')!=0:raise SystemExit('Recording activity; defer')
rows=[];container=shlex.quote(cfg['unraid_container_name'])
with C.ssh(cfg) as client:
  def remote(cmd):return C.remote(client,'docker exec '+container+' '+cmd)
  if any(line.split()[-1] in ('ffmpeg.real','ffmpeg_MIM','SageTVTranscoder') for line in remote('ps -eo comm').splitlines() if line.split()):
    raise SystemExit('Existing encoder active; defer isolated comparison')
  storage=remote('df -B1 /tmp/sagetv-webplayer-hls /dev/shm')
  for iteration in (1,2):
    for label,parent,seconds in [('disk3','/tmp/sagetv-webplayer-hls',3),('disk1','/tmp/sagetv-webplayer-hls',1),('ram1','/dev/shm',1)]:
      if C.activity(cfg).get('recordingCount')!=0:raise RuntimeError('Recording activity changed')
      directory=parent+'/web044-startup-'+uuid.uuid4().hex
      assert re.fullmatch(r'/(?:tmp/sagetv-webplayer-hls|dev/shm)/web044-startup-[a-f0-9]{32}',directory)
      remote('mkdir -m 700 -- '+shlex.quote(directory))
      process=None
      try:
        command=[x.replace('/tmp/sagetv-webplayer-hls/<test-session>',directory) for x in base]
        command[command.index('-hls_time')+1]=str(seconds)
        output_index=command.index('-f',command.index('-i')+2)
        command[output_index:output_index]=['-t','12','-forced_idr','1']
        started=time.monotonic();first=None
        _,stdout,stderr=client.exec_command('docker exec '+container+' '+' '.join(shlex.quote(x) for x in command),timeout=60)
        process=stdout.channel
        while not process.exit_status_ready() and time.monotonic()-started<45:
          if first is None:
            try:remote('test -s '+shlex.quote(directory+'/seg_00000.ts'));first=round((time.monotonic()-started)*1000)
            except RuntimeError:pass
          time.sleep(.05)
        if not process.exit_status_ready():raise RuntimeError('Bounded benchmark timed out; exact job requires investigation '+directory)
        code=process.recv_exit_status();err=stderr.read().decode(errors='replace')[-1500:]
        playlist=remote('cat '+shlex.quote(directory+'/stream.m3u8')) if code==0 else ''
        row={'case':label,'iteration':iteration,'exit':code,'firstSegmentObservedMs':first,
             'elapsedMs':round((time.monotonic()-started)*1000),
             'segmentSeconds':[float(x) for x in re.findall(r'#EXTINF:([0-9.]+)',playlist)],'stderr':err}
        rows.append(row);print(json.dumps(row),flush=True)
        if code:raise RuntimeError('Encoder comparison failed')
      finally:
        # A live process must not have its files removed from underneath it.
        if process is None or process.exit_status_ready():
          names=remote('find '+shlex.quote(directory)+' -maxdepth 1 -type f -printf '+shlex.quote('%f\n')).splitlines()
          if any(not re.fullmatch(r'(?:seg_[0-9]{5}\.ts|stream\.m3u8|progress\.log)',n) for n in names):
            raise RuntimeError('Unexpected owned output preserved: '+directory)
          if names:remote('rm -- '+' '.join(shlex.quote(directory+'/'+n) for n in names))
          remote('rmdir -- '+shlex.quote(directory))
        else:raise RuntimeError('Live owned benchmark preserved: '+directory)
(OUT/(stamp+'-segment-storage.json')).write_text(json.dumps({'fixture':fixture,'outputSeconds':12,'storage':storage,
    'runtimeSettingsChanged':False,'cases':rows},indent=2)+'\n',encoding='utf-8')
