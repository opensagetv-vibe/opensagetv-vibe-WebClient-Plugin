#!/usr/bin/env python3
"""Actual production phone player: three generated test-source changes.

Existing public stock controls, no user recordings/settings, synthetic clocks
or replay. Canonical fixture watch state is test-owned; no acoustic claim.
"""
import asyncio,importlib.util,json,logging,sys,time
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlencode
from field_candidate import playback_revision
ROOT=Path(__file__).resolve().parents[1];BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
EXPECTED_PLAYBACK=playback_revision(ROOT)
sys.path.insert(0,str(BRIDGE/'tools/native_inspector'))
import wireless_inspect as W
from field_hid import InputOwner
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration();identity='123c8282e1ee'
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
out=ROOT/'artifacts/active/WP11-008'/(stamp+'-iphone-recording-changeover.json');out.parent.mkdir(parents=True,exist_ok=True)
report=dict(passed=False,physicalPhone=True,physicalFingerGesture=False,nativeCoreWatch=True,acoustic=False,rows=[],cleanup=[])
original=W.evaluate
class Trigger:
 def read_text(self,**_):return '__PHONE_RECORDING_CHANGEOVER__'
async def evaluate(session,expression):
 if expression!='__PHONE_RECORDING_CHANGEOVER__':return await original(session,expression)
 async def ev(code):return await original(session,code)
 async def request(path,values=None):return await asyncio.to_thread(C.request,cfg,path,values,timeout=30)
 async def mcp(action,**kw):return await asyncio.to_thread(C.request,cfg,'/v1/control',dict(action=action,**kw),mcp=True,timeout=30)
 async def guard():
  a=await asyncio.to_thread(C.activity,cfg)
  if a.get('recordingCount') or a.get('connectedClientCount') or (await mcp('ui.list')).get('contexts')!=[identity]:raise RuntimeError('Require exact phone-only idle recordings')
 async def sample():return await ev("(()=>{const s=__changePhone,v=videoPlane;return{time:v.currentTime,frames:s.frames,current:s.source===v.currentSrc,source:v.currentSrc,paused:v.paused,ready:v.readyState,width:v.videoWidth,error:v.error?.code||null,prompt:!autoplayBtn.hidden,player:s.player?.snapshot()||null}})()")
 installed=False;watched=False;stop_intent=False;previous=None
 try:
  await guard()
  if (await mcp('ui.state',context=identity)).get('fullyLoaded'):raise RuntimeError('Phone source already loaded')
  revision=await ev("(()=>[...document.scripts].find(e=>e.src.includes('miniclient-playback.js'))?.src.split('?')[1])()")
  if revision!=EXPECTED_PLAYBACK:raise RuntimeError('Wrong installed playback candidate')
  report['verifiedPlaybackRevision']=revision
  for mid,token in ((20905,'VibeCaptionTest'),(84231,'VibeAudio-PMT-Mono-to-51.ts')):
   info=await request('/SageTVWebPlayer/api/media?id='+str(mid))
   if info.get('recording') or not info.get('files') or not all('/OpenSageTV_Vibe_Tests/' in f['path'] and token in f['path'] for f in info['files']):raise RuntimeError('Canonical generated fixture identity changed')
  await ev("(()=>{if(document.visibilityState!=='visible'||window.__changePhone||videoPlane.getAttribute('src')||videoPlane.srcObject||videoPlane.readyState>0)throw Error('Require visible unloaded exact phone');const keys=['sagetvWebMiniClientSettings.v1','sagetvWebStreaming.v1','sagetvWebCaptionAuthority.v1'],s=window.__changePhone={keys,saved:keys.map(k=>localStorage.getItem(k)),frames:0,source:'',player:null,done:false};s.original=SageMiniPlayback.prototype.start;s.wrap=function(...args){s.player=this;return s.original.apply(this,args)};SageMiniPlayback.prototype.start=s.wrap;function f(){const source=videoPlane.currentSrc;videoPlane.requestVideoFrameCallback(()=>{if(s.done)return;if(source&&source===videoPlane.currentSrc){s.frames++;s.source=source}f()})}f();return true})()");installed=True
  configured=None
  for mid in (20905,84231,20905):
   await guard();first_before=await sample();watched=True
   if not (await mcp('media.watch',context=identity,media_id=mid,wait_ms=0)).get('accepted'):raise RuntimeError('One public Watch rejected; no replay')
   deadline=time.monotonic()+70;activated=False
   while time.monotonic()<deadline:
    v=await sample()
    if v['error']:raise RuntimeError('Actual production decoder error')
    if v['prompt'] and not activated:
     await ev("(()=>{if(autoplayBtn.hidden||autoplayBtn.disabled)throw Error('Activation unavailable');autoplayBtn.focus();return document.activeElement===autoplayBtn})()")
     owner=InputOwner('192.168.10.113',(BRIDGE/'build/native-inspector/token.txt').read_text(encoding='ascii').strip())
     try:await owner.arm();await owner.send('key',key='enter');activated=True
     finally:await owner.close()
    if v['source']!=first_before['source'] and v['current'] and v['frames']>first_before['frames']+12 and v['ready']>=2 and not v['paused']:break
    await asyncio.sleep(.2)
   else:report['last']=v;raise RuntimeError('No new source presented; no replay')
   first=v;await asyncio.sleep(8);last=await sample();native=await mcp('ui.state',context=identity)
   if (native.get('media') or {}).get('mediaFileId')!=mid or last['frames']<first['frames']+25 or last['source']!=first['source'] or last['error']:raise RuntimeError('Native/source presentation ownership failed')
   snap=last['player'] or {};origin=snap.get('startSeconds');raw=native.get('rawMediaTimeMs')
   if not isinstance(origin,(int,float)) or not isinstance(raw,(int,float)) or abs(raw-(origin+last['time'])*1000)>2000:raise RuntimeError('Native file clock differs from actual owned presentation')
   hls_id=snap.get('session') or snap.get('hlsSession') or snap.get('id')
   if not hls_id:raise RuntimeError('Producer identity unavailable')
   if previous==hls_id:raise RuntimeError('Source change retained old producer')
   if previous:
    try:
     old=await request('/SageTVWebPlayer/api/hls?session='+previous)
     if old.get('running'):raise RuntimeError('Previous producer retained after source change')
    except RuntimeError as e:
     if not str(e).startswith('HTTP 404: HLS session not found'):raise
   previous=hls_id
   if snap.get('recoveries') or snap.get('clockRegressions'):raise RuntimeError('Production recovery/clock loop')
   report['rows'].append(dict(gate='actual-source-change-and-native-file-clock',passed=True,mediaId=mid,first=first,last=last,nativeFileTimeMs=raw));print('PASS phone source change '+str(mid),flush=True)
  await guard();stop_intent=True
  if not (await mcp('media.control',context=identity,operation='stop')).get('accepted'):raise RuntimeError('One Stop rejected')
  deadline=time.monotonic()+20
  while time.monotonic()<deadline:
   unloaded=await ev("({paused:videoPlane.paused,ready:videoPlane.readyState,assigned:!!(videoPlane.getAttribute('src')||videoPlane.srcObject)})")
   if unloaded['paused'] and unloaded['ready']==0 and not unloaded['assigned']:break
   await asyncio.sleep(.2)
  else:raise RuntimeError('Production decoder did not unload')
  report['rows'].append(dict(gate='production-Stop-and-decoder-retirement',passed=True));report['passed']=True
 finally:
  if watched and not stop_intent:
   try:
    await guard();stop_intent=True
    if not (await mcp('media.control',context=identity,operation='stop')).get('accepted'):raise RuntimeError()
   except Exception:report['cleanup'].append('Owned Stop unknown; never replay')
  if installed:
   try:
    restored=await ev("(()=>{const s=__changePhone;s.done=true;const same=s.keys.every((k,i)=>localStorage.getItem(k)===s.saved[i]);if(SageMiniPlayback.prototype.start!==s.wrap)throw Error('Observer ownership changed');SageMiniPlayback.prototype.start=s.original;delete window.__changePhone;return same})()")
    if not restored:report['cleanup'].append('Saved profile mismatch')
   except Exception:report['cleanup'].append('Observer restoration unknown')
  report['passed']=report['passed'] and not report['cleanup']
 return dict(passed=report['passed'],rows=len(report['rows']))
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,page_id=None,verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,screenshot=None)
async def run():
 async def attached(rsd,data):await W.inspect(rsd,data,args)
 await W.probe(args,report,on_rsd=attached)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
try:asyncio.run(asyncio.wait_for(run(),290))
except Exception as e:report.update(passed=False,errorType=type(e).__name__,error=str(e)[:200] if isinstance(e,RuntimeError) else 'Bounded observation unavailable; no replay')
finally:
 W.evaluate=original
 report['passed']=report['passed'] and len(report['rows'])==4 and not report['cleanup']
 out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(passed=report['passed'],rows=len(report['rows']),report=str(out),error=report.get('error'),cleanup=report['cleanup'])));raise SystemExit(0 if report['passed'] else 1)
