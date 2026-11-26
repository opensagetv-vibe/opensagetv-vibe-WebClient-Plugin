#!/usr/bin/env python3
"""Explicit task-owned physical HDMI capture using the existing local toolbox.

No phone input, install, capture-driver/config change or automatic unlock.
"""
import argparse,json,subprocess,time,tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--task',choices=('WEB-014','WEB-023','WEB-080','WEB-098','WEB-099','WP04-007','WP11-008','WP16-003','WP16-004'),required=True)
p.add_argument('--seconds',type=int,default=0);p.add_argument('--audio',action='store_true')
p.add_argument('--audio-device',choices=('Digital Audio Interface (USB Digital Audio)','Microphone (HD Pro Webcam C920)'),help='Explicit commissioned capture input; does not edit persistent configuration')
a=p.parse_args()
if not 0<=a.seconds<=30:p.error('Bounded0..30s capture required')
if a.audio_device and not a.audio:p.error('Audio input selection requires --audio')
cfg=tomllib.loads((BRIDGE/'config/toolbox.local.toml').read_text(encoding='utf-8'))['capture']
exe=Path(cfg['ffmpeg'])
if not exe.is_file():raise RuntimeError('Existing explicit local FFmpeg required')
folder=ROOT/'artifacts/active'/a.task
if any(x.is_symlink() or (hasattr(x,'is_junction') and x.is_junction()) for x in (folder,*folder.parents)):
    raise RuntimeError('Reparse output path rejected')
folder.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());out=folder/(stamp+'-physical-hdmi'+('.mp4' if a.seconds else '.png'))
source='video='+cfg.get('video_device','USB Video')
if a.audio:
    audio_device=a.audio_device or cfg.get('audio_device')
    if not a.seconds or not audio_device:raise RuntimeError('Explicit recording/audio configuration required')
    source+=':audio='+audio_device
command=[str(exe),'-hide_banner','-nostdin','-n','-loglevel','error','-f','dshow','-rtbufsize','256M',
    '-vcodec','mjpeg','-video_size','1920x1080','-framerate','30','-i',source]
command+=['-t',str(a.seconds),'-c:v','libx264','-preset','ultrafast','-pix_fmt','yuv420p','-fps_mode','passthrough'] if a.seconds else ['-frames:v','1','-update','1']
command+=['-c:a','aac','-b:a','128k'] if a.audio else ['-an']
command.append(str(out));result=subprocess.run(command,capture_output=True,timeout=a.seconds+25)
with out.with_suffix('.ffmpeg.log').open('xb') as f:f.write(result.stderr[-65536:])
if result.returncode or not out.is_file():raise RuntimeError('HDMI capture failed; task-owned log retained')
print(json.dumps(dict(path=str(out),bytes=out.stat().st_size,physicalHDMI=True,audio=a.audio,audioDevice=audio_device if a.audio else None)))
