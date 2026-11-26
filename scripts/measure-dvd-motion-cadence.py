#!/usr/bin/env python3
"""Bounded read-only gray-frame changes in the task-owned physical HDMI video.

This measures capture cadence, not acoustic sync or subjective motion quality.
No source, device, playback settings or installed runtime is modified.
"""
import argparse,json,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('capture')
a=p.parse_args()
source=Path(a.capture).resolve(strict=True)
folder=(ROOT/'artifacts/active/WEB-099').resolve(strict=True)
if source.parent!=folder or source.suffix!='.mp4' or source.is_symlink():
    raise RuntimeError('Require exact task-owned WEB-099 MP4')
ffmpeg=ROOT.parent/'opensagetv-vibe-ffmpeg-mim/output/windows-x64/ffmpeg.real.exe'
# Exclude letterboxing, AssistiveTouch and overlay; downscale for robust motion
# differences rather than counting lossy capture re-encoding noise as changes.
command=[str(ffmpeg),'-hide_banner','-nostdin','-v','error','-i',str(source),
    '-t','30','-an','-vf','crop=1664:576:128:256,scale=96:32,format=gray',
    '-fps_mode','passthrough','-f','rawvideo','pipe:1']
r=subprocess.run(command,capture_output=True,timeout=45,check=True)
size=96*32
if not r.stdout or len(r.stdout)%size:raise RuntimeError('Incomplete frames')
frames=[r.stdout[i:i+size] for i in range(0,len(r.stdout),size)]
probe=ffmpeg.with_name('ffprobe.exe')
if not probe.is_file():probe=ffmpeg.with_name('ffprobe.real.exe')
if not probe.is_file():raise RuntimeError('Explicit sibling ffprobe required for actual capture timestamps')
timing=json.loads(subprocess.run([str(probe),'-v','error','-select_streams','v:0',
    '-show_entries','frame=best_effort_timestamp_time','-of','json',str(source)],capture_output=True,timeout=30,check=True).stdout)
timestamps=[float(v['best_effort_timestamp_time']) for v in timing['frames'] if 'best_effort_timestamp_time'in v]
duration=timestamps[-1]-timestamps[0] if len(timestamps)>1 else 0
differences=[sum(abs(x-y) for x,y in zip(a,b))/size for a,b in zip(frames,frames[1:])]
report=dict(physicalHDMI=True,audio=False,source=source.name,frameCount=len(frames),
    captureSpanSeconds=duration,timestamps=timestamps,
    meanAbsoluteDifferences=differences,
    changedByThreshold={str(t):sum(v>t for v in differences) for t in (.1,.25,.5,1,2)},
    note='30fps capture; differences measure changing image, not smoothness qualification')
out=folder/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-capture-cadence.json')
with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(path=str(out),frames=len(frames),changedByThreshold=report['changedByThreshold'],first90=[round(x,2) for x in differences[:90]])))
