#!/usr/bin/env python3
"""Actual phone native HLS at5h and natural5.5h-file tail; no Core Watch.

Temporary muted visible video, original page/profiles restored. No finger,
audibility, native STV timeline or elapsed-multi-hour soak claim.
"""
import argparse,asyncio,importlib.util,json,logging,sys,time
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
sys.path.insert(0,str(BRIDGE/'tools/native_inspector'))
import wireless_inspect as W
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration()
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--profile-smoke',action='store_true',help='WEB104 explicit1Mbps/480p native output only; do not repeat completed tail matrix')
options=parser.parse_args()
out=ROOT/'artifacts/active'/('WEB-104' if options.profile_smoke else 'WP11-008');out.mkdir(parents=True,exist_ok=True)
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
report=dict(passed=False,physicalPhone=True,physicalFingerGesture=False,acoustic=False,
    nativeCoreWatch=False,elapsedMultiHourSoak=False,mediaId=1444,rows=[],cleanup=[])
original=W.evaluate
class Trigger:
    def read_text(self,**_):return '__IPHONE_LONG_SOURCE__'
def api(action,**values):
    return C.request(cfg,'/SageTVWebPlayer/api/hls',dict(action=action,**values),timeout=60)
async def evaluate(session,expression):
    if expression!='__IPHONE_LONG_SOURCE__':return await original(session,expression)
    async def ev(code):return await original(session,code)
    async def sample():return await ev("(()=>{const s=__longPhone,v=s.video;return{time:v.currentTime,frames:s.frames,width:v.videoWidth,height:v.videoHeight,paused:v.paused,ready:v.readyState,error:v.error?.code||null,ended:v.ended,sourceCurrent:s.frameSource===v.currentSrc,nativeHls:!!v.currentSrc&&!v.currentSrc.startsWith('blob:'),blocked:s.blocked}})()")
    installed=False;owned=None;stop_intent=False
    try:
        if not (await asyncio.to_thread(C.activity,cfg)).get('safeToRestart'):raise RuntimeError('Require independently idle server')
        before=await asyncio.to_thread(C.request,cfg,'/SageTVWebPlayer/api/media?id=1444')
        if before.get('title')!='Reconstruction: America After the Civil War' or before.get('duration')!=19800000:
            raise RuntimeError('Exact long recording changed')
        await ev("(()=>{if(document.visibilityState!=='visible'||window.__longPhone||videoPlane.getAttribute('src')||videoPlane.srcObject||videoPlane.readyState>0)throw Error('Require visible exact stopped phone');const keys=['sagetvWebMiniClientSettings.v1','sagetvWebStreaming.v1','sagetvWebCaptionAuthority.v1'];const v=document.createElement('video');v.muted=true;v.playsInline=true;v.style.cssText='position:fixed;inset:0;width:100%;height:100%;object-fit:contain;background:black;z-index:2147483000';const s=window.__longPhone={video:v,keys,saved:keys.map(k=>localStorage.getItem(k)),frames:0,frameSource:'',done:false,blocked:false};document.body.append(v);function f(){const source=v.currentSrc;v.requestVideoFrameCallback(()=>{if(s.done)return;if(source&&source===v.currentSrc){s.frames++;s.frameSource=source}f()})}f();return true})()");installed=True
        for target,seconds in (((18000,20),) if options.profile_smoke else ((18000,20),(19785,0))):
            if not (await asyncio.to_thread(C.activity,cfg)).get('safeToRestart'):raise RuntimeError('Other native activity appeared')
            profile=dict(stream_profileSchemaVersion=8,stream_player='hls',stream_videoMode='transcode',
                stream_videoKbps=1000,stream_resolution='480') if options.profile_smoke else {}
            produced=await asyncio.to_thread(api,'start',id=1444,start=target,segment=0,audio=0,**profile)
            owned=produced.get('session');stop_intent=False
            if not owned or produced.get('mediaId')!=1444 or produced.get('startSeconds')!=target:raise RuntimeError('Producer identity/origin mismatch')
            if options.profile_smoke:
                settings=produced.get('streamSettings') or {};report['profile']=settings
                requested=settings.get('requested') or {};effective=settings.get('effective') or {}
                if str(requested.get('videoKbps'))!='1000' or str(requested.get('resolution'))!='480' or effective.get('videoTargetKbps')!=1000:
                    raise RuntimeError('Explicit public HLS profile not honored')
            # Actual owned native Safari element, not a fake clock or HLS stub.
            url=cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/'+produced['playlistUrl']
            await ev("(()=>{const s=__longPhone,v=s.video;s.frames=0;s.frameSource='';s.blocked=false;v.src="+json.dumps(url)+";v.load();v.play().catch(()=>{s.blocked=true});return true})()")
            deadline=time.monotonic()+65;first=None;last=None
            while time.monotonic()<deadline:
                last=await sample()
                if last['error']:raise RuntimeError('Actual native Safari media error')
                if last['blocked']:raise RuntimeError('Muted playback blocked; no synthetic user activation claim')
                if last['sourceCurrent'] and last['frames']>=10 and last['time']>.25 and not last['paused']:
                    first=last;break
                await asyncio.sleep(.2)
            if first is None:report['last']=last;raise RuntimeError('No actual native pictures; no replay')
            if seconds:
                await asyncio.sleep(seconds);last=await sample()
                if last['error'] or last['frames']<first['frames']+30 or last['time']<first['time']+seconds*.8:
                    report['last']=last;raise RuntimeError('Native large-offset pictures stopped')
            else:
                deadline=time.monotonic()+40
                while time.monotonic()<deadline:
                    last=await sample()
                    if last['error']:raise RuntimeError('Native tail media error')
                    if last['ended']:break
                    await asyncio.sleep(.2)
                else:report['last']=last;raise RuntimeError('Actual native tail did not end')
            if not first['nativeHls'] or not last['nativeHls']:raise RuntimeError('Not actual native HLS')
            if options.profile_smoke and (first['height']!=480 or last['height']!=480):raise RuntimeError('Requested480p not reflected in actual decoded dimensions')
            report['rows'].append(dict(gate='native-large-offset20s' if seconds else 'native-actual-source-tail-ended',passed=True,targetSeconds=target,first=first,last=last))
            await ev("(()=>{const v=__longPhone.video;v.pause();v.removeAttribute('src');v.load();return true})()")
            stop_intent=True
            if not (await asyncio.to_thread(api,'stop',session=owned)).get('stopped'):raise RuntimeError('Owned producer Stop rejected')
            owned=None
        after=await asyncio.to_thread(C.request,cfg,'/SageTVWebPlayer/api/media?id=1444')
        if any(before.get(k)!=after.get(k) for k in ('watched','watchedCompletely','serverResumeSeconds')):raise RuntimeError('Original watch state changed')
        report['originalWatchStateUnchanged']=True;report['passed']=True
    finally:
        if installed:
            try:
                restored=await ev("(()=>{const s=__longPhone;s.done=true;const v=s.video;v.pause();v.removeAttribute('src');v.load();v.remove();const same=s.keys.every((k,i)=>localStorage.getItem(k)===s.saved[i]);delete window.__longPhone;return{profiles:same,unloaded:v.paused&&v.readyState===0&&!v.getAttribute('src')&&!v.srcObject}})()")
                report['restoration']=restored
                if not all(restored.values()):report['cleanup'].append('Phone restoration mismatch')
            except Exception:report['cleanup'].append('Phone restoration observation unavailable')
        if owned and not stop_intent:
            try:
                stop_intent=True
                await asyncio.to_thread(api,'stop',session=owned)
            except Exception:report['cleanup'].append('Owned Stop unknown; not replayed')
        report['passed']=report['passed'] and not report['cleanup']
    return dict(passed=report['passed'],rows=len(report['rows']))
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,page_id=None,verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,screenshot=None)
async def run():
    async def attached(rsd,data):await W.inspect(rsd,data,args)
    await W.probe(args,report,on_rsd=attached)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
try:asyncio.run(asyncio.wait_for(run(),240))
except Exception as e:report.update(passed=False,errorType=type(e).__name__,error=str(e)[:200] if isinstance(e,RuntimeError) else 'Bounded inspection unavailable; no replay')
finally:
    W.evaluate=original
    path=out/(stamp+'-iphone-long-source.json');path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(passed=report['passed'],rows=len(report['rows']),path=str(path),error=report.get('error'),cleanup=report['cleanup'])));raise SystemExit(0 if report['passed'] else 1)
