#!/usr/bin/env python3
"""Owned iPhone WAN menu check: real BLE keys plus physical HDMI, no Wi-Fi inspector.

Run only after reviewing HDMI's SageMC main menu with My TV selected. This is
not a finger/long-press-control or calibrated input-to-photon timing claim.
"""
import argparse,importlib.util,json,subprocess,sys,time,tomllib
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
sys.path.insert(0,str(BRIDGE/'tools/native_inspector'))
from ios_toolbox import Toolbox
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--keys',nargs='+',default=['down','down','down','up','up','up'])
parser.add_argument('--task',choices=('WEB-023','WEB-037'),default='WEB-023')
parser.add_argument('--seconds',type=int,choices=range(8,31),default=16)
parser.add_argument('--interval',type=float,default=1.25)
parser.add_argument('--media-id',type=int,help='Exact already-loaded authorized media; never start or replace playback here')
parser.add_argument('--audio',action='store_true',help='Capture only the configured HDMI electrical audio input, not acoustic certification')
parser.add_argument('--audio-device',choices=('Digital Audio Interface (USB Digital Audio)',),help='Explicit commissioned HDMI input override; never changes saved configuration')
args=parser.parse_args()
allowed={'escape','enter','space','up','down','left','right','tab','shift_tab'}
if not 1<=len(args.keys)<=12 or any(k not in allowed for k in args.keys):parser.error('Require1..12 explicit non-text page keys')
if not .3<=args.interval<=2 or len(args.keys)*args.interval+4>args.seconds:parser.error('Keys must fit the bounded capture')
if args.audio_device and not args.audio:parser.error('Explicit audio input requires --audio')
activity=C.activity(cfg);contexts=C.request(cfg,'/v1/control',{'action':'ui.list'},mcp=True).get('contexts')
if activity.get('recordingCount')!=0 or activity.get('connectedClientCount')!=0 or contexts!=['123c8282e1ee']:
    raise RuntimeError('Require exact phone and no recordings/other clients')
native=C.request(cfg,'/v1/control',{'action':'ui.state','context':contexts[0]},mcp=True)
if args.media_id is None:
    if native.get('fullyLoaded'):raise RuntimeError('Require reviewed stopped main menu')
elif not native.get('fullyLoaded') or (native.get('media') or {}).get('mediaFileId')!=args.media_id:
    raise RuntimeError('Require the exact reviewed loaded test media')
settings=tomllib.loads((BRIDGE/'config/toolbox.local.toml').read_text(encoding='utf-8'))
box=Toolbox(settings);capture=settings['capture']
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
out=ROOT/'artifacts/active'/args.task;out.mkdir(parents=True,exist_ok=True)
video=out/(stamp+'-cellular-vpn-menu.mp4');log=video.with_suffix('.ffmpeg.log')
report={'route':'User-confirmed cellular/VPN','physicalHDMI':True,'realBLE':True,
        'physicalFingerGesture':False,'calibratedInputToPhoton':False,'keys':[],
        'video':str(video),'nativeBefore':native,'passed':False}
process=None
try:
    command=[str(capture['ffmpeg']),'-hide_banner','-nostdin','-n','-loglevel','error',
             '-f','dshow','-rtbufsize','256M','-vcodec','mjpeg','-video_size','1920x1080',
             '-framerate','30']
    source='video='+capture.get('video_device','USB Video')
    if args.audio:
        audio=args.audio_device or capture.get('audio_device')
        if audio!='Digital Audio Interface (USB Digital Audio)':raise RuntimeError('Require commissioned HDMI electrical audio input')
        source+=':audio='+audio
    command+=['-i',source,'-t',str(args.seconds)]
    command+=['-c:a','aac','-b:a','128k'] if args.audio else ['-an']
    command+=['-c:v','libx264','-preset','ultrafast','-pix_fmt','yuv420p',str(video)]
    with log.open('xb') as stream:
        began=time.monotonic();process=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=stream)
        time.sleep(3)
        state=box.bridge('ble_hid',{'action':'status'})
        if not(state.get('connected') and state.get('secure') and state.get('bondCount')==1):
            raise RuntimeError('Require one encrypted phone bond')
        lease=box.bridge('ble_hid',{'action':'arm','confirmed':True})['lease']
        for sequence,key in enumerate(args.keys,1):
            if process.poll() is not None:raise RuntimeError('Capture ended before input')
            sent=time.monotonic()-began
            result=box.bridge('ble_hid',{'action':'key','lease':lease,'sequence':sequence,'key':key})
            if result.get('sequence')!=sequence or not result.get('reportSubmitted'):
                raise RuntimeError('Unknown key receipt; do not replay')
            report['keys'].append({'key':key,'submittedAfterCaptureLaunchSeconds':sent})
            time.sleep(args.interval)
        box.close()
        if process.wait(timeout=args.seconds+10)!=0:raise RuntimeError('HDMI capture failed')
    report['nativeAfter']=C.request(cfg,'/v1/control',{'action':'ui.state','context':contexts[0]},mcp=True)
    report['deliveryAndCaptureCompleted']=True
    report['status']='AWAITING_VISUAL_REVIEW_NOT_AUTOMATIC_PASS'
except Exception as error:
    report['errorType']=type(error).__name__
    if isinstance(error,RuntimeError):report['error']=str(error)
finally:
    box.close()
    if process and process.poll() is None:process.terminate();process.wait(timeout=5)
    path=out/(stamp+'-cellular-vpn-menu.json');path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'report':str(path),'captured':report.get('deliveryAndCaptureCompleted',False)}))
raise SystemExit(0 if report.get('deliveryAndCaptureCompleted') else 1)
