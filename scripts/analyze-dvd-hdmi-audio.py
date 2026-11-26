#!/usr/bin/env python3
"""Offline bounded fixture-tone analysis; no phone/server connection or mutation."""
import argparse,hashlib,json,subprocess
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True)
    p.add_argument('--expected',type=int,choices=(440,1000),required=True);a=p.parse_args()
    source=a.input.resolve();base=(ROOT/'artifacts/active/WEB-014').resolve()
    if not source.is_relative_to(base) or not source.is_file() or source.stat().st_size>100*1024*1024:
        raise ValueError('Bounded owned WEB-014 capture required')
    for parent in (source,*source.parents):
        if parent==ROOT.parent:break
        if parent.is_symlink() or (hasattr(parent,'is_junction') and parent.is_junction()):raise ValueError('Reparse capture rejected')
    ffmpeg=ROOT.parent/'opensagetv-vibe-ffmpeg-mim/output/windows-x64/ffmpeg.real.exe'
    r=subprocess.run([str(ffmpeg),'-hide_banner','-nostdin','-v','error','-i',str(source),
        '-t','6','-vn','-ac','1','-ar','48000','-f','f32le','pipe:1'],capture_output=True,timeout=20,check=True)
    s=np.frombuffer(r.stdout,dtype='<f4')
    if not 48000<=len(s)<=7*48000:raise ValueError('Sample bound')
    s=s-np.mean(s);power=np.abs(np.fft.rfft(s*np.hanning(len(s))))**2;hz=np.fft.rfftfreq(len(s),1/48000)
    bands={tone:float(power[np.abs(hz-tone)<5].sum()) for tone in (440,1000)}
    peak=float(hz[(hz>=300)&(hz<=1200)][np.argmax(power[(hz>=300)&(hz<=1200)])])
    other=440 if a.expected==1000 else 1000;rms=float(np.sqrt(np.mean(s**2)))
    ratio=bands[a.expected]/max(bands[other],1e-30)
    print(json.dumps({'capture':source.name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'hdmiAudioNotAcoustic':True,'samples':len(s),'rms':rms,'peakHz':round(peak,3),
        'expectedHz':a.expected,'expectedOverOther':ratio,
        'passed':abs(peak-a.expected)<=5 and rms>=.0001 and ratio>=10}))
if __name__=='__main__':main()
