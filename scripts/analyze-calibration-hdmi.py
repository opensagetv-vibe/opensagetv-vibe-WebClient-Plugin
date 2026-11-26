#!/usr/bin/env python3
"""Offline WEB-023 capture analysis; never connects to phone or server.

ROI is the explicitly observed yellow calibration fixture, not production UI
geometry. Measures capture-path audio versus red impact line at captured frame
resolution; it does not certify TV/speaker/lip sync or alter any offset.
"""
import argparse, hashlib, json, re, subprocess
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

def onset_times(times,maximum_gap):
    return [float(t) for i,t in enumerate(times) if i==0 or t-times[i-1]>maximum_gap]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--roi',required=True,help='Explicit observed calibration x,y,width,height')
    p.add_argument('--ffmpeg',type=Path,default=ROOT.parent/'opensagetv-vibe-ffmpeg-mim/output/windows-x64/ffmpeg.real.exe')
    a=p.parse_args();source=a.input.resolve();out=a.output.resolve()
    if not source.is_relative_to((ROOT/'artifacts/active/WEB-023').resolve()) or not source.is_file() or source.stat().st_size>100*1024*1024:raise ValueError('Require bounded owned WEB-023 capture')
    if not out.is_relative_to((ROOT/'artifacts/results/WEB-023').resolve()) or out.exists():raise ValueError('Use a fresh owning compact result')
    x,y,w,h=map(int,a.roi.split(','))
    if min(x,y)<0 or not 32<=w<=640 or not 32<=h<=360:raise ValueError('Invalid bounded fixture ROI')
    common=[str(a.ffmpeg.resolve()),'-hide_banner','-nostdin','-i',str(source),'-t','15']
    video=subprocess.run(common+['-an','-vf',f'crop={w}:{h}:{x}:{y},showinfo','-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],capture_output=True,timeout=45,check=True)
    pts=np.array([float(v) for v in re.findall(r'\bn:\s*\d+.*?pts_time:([\d.-]+)',video.stderr.decode('utf-8',errors='replace'))])
    frames=np.frombuffer(video.stdout,dtype=np.uint8).reshape((-1,h,w,3))
    if len(frames)!=len(pts) or len(frames)>1000 or len(frames)<30:raise ValueError('Captured video timestamp/frame bound mismatch')
    red_on=[];line_rows=[];ball_y=[]
    for timestamp,frame in zip(pts,frames):
        red=(frame[:,:,0]>150)&(frame[:,:,1]<110)&(frame[:,:,2]<140)
        counts=red.sum(axis=1);row=int(np.argmax(counts))
        if counts[row]>w*.5:red_on.append(timestamp);line_rows.append(row)
        white=(frame[:,:,0]>190)&(frame[:,:,1]>190)&(frame[:,:,2]>190)
        yy,xx=np.where(white)
        if len(yy)>3:ball_y.append(float(np.mean(yy)))
    audio=subprocess.run(common+['-v','error','-vn','-af','aresample=48000:first_pts=0','-ac','1','-ar','48000','-f','f32le','pipe:1'],capture_output=True,timeout=30,check=True)
    samples=np.frombuffer(audio.stdout,dtype='<f4')
    if not 1<=len(samples)<=15*48000:raise ValueError('Captured audio outside bound')
    bursts=onset_times(np.flatnonzero(np.abs(samples)>.06)/48000,.05)
    impacts=onset_times(np.array(red_on),.4)
    pairs=[]
    for impact in impacts:
        if not bursts:break
        nearest=min(bursts,key=lambda t:abs(t-impact));delta=nearest-impact
        if abs(delta)<.4:pairs.append({'redOnsetSeconds':impact,'audioOnsetSeconds':nearest,'audioMinusRedMs':round(delta*1000,2)})
    report={'input':source.name,'inputSha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'scope':'Offline original iPhone HDMI capture; observed fixture ROI only',
        'roi':[x,y,w,h],'capturedFrames':len(frames),'firstVideoPts':float(pts[0]),'lastVideoPts':float(pts[-1]),
        'audioSamples':len(samples),'audioPeak':float(np.abs(samples).max()),'audioBurstOnsets':bursts,
        'redImpactOnsets':impacts,'lineRows':sorted(set(line_rows)),
        'whiteBallObservedFrames':len(ball_y),'whiteBallYRange':[min(ball_y),max(ball_y)] if ball_y else [],
        'matchedImpacts':pairs,'medianAudioMinusRedMs':float(np.median([r['audioMinusRedMs'] for r in pairs])) if pairs else None,
        'captureFrameIntervalMs':float(np.median(np.diff(pts))*1000),
        'limits':['HDMI capture latency and frame quantization included','Not TV speaker or acoustic microphone evidence',
                  'Not lip-sync or no-blur certification','No phone access, offset change, new generation or server mutation'],
        'analysisComplete':True,'audibleSyncCertified':False}
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
