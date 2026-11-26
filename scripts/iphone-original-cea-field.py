#!/usr/bin/env python3
"""Actual iPhone CEA-708 from a byte-verified original broadcast prefix.

One Watch and one seek, normal settings Save, exact profile restoration.
Only counts/geometry are reported; no caption text or generated caption input.
"""
import asyncio, importlib.util, json, logging, sys, time
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]; BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
sys.path.insert(0,str(BRIDGE/'tools/native_inspector'))
import wireless_inspect as W
from field_hid import InputOwner
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration();identity='123c8282e1ee'
out=ROOT/'artifacts/active/WP05-006';out.mkdir(parents=True,exist_ok=True)
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');path=out/(stamp+'-iphone-original-cea.json')
report=dict(passed=False,physicalPhone=True,physicalFingerGesture=False,originalBroadcastPrefix=True,
            exportsCaptionPayload=False,inputReplayed=False,rows=[],cleanup=[])
original=W.evaluate
class Trigger:
 def read_text(self,**_):return '__ORIGINAL_CEA_FIELD__'
def save():path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
def mcp(action,**v):return C.request(cfg,'/v1/control',dict(action=action,**v),mcp=True,timeout=30)
def guard():
 a=C.activity(cfg)
 if a['recordingCount'] or a['connectedClientCount'] or mcp('ui.list')['contexts']!=[identity]:raise RuntimeError('Require exact phone/no unrelated activity')
 return mcp('ui.state',context=identity)
async def evaluate(session,expression):
 if expression!='__ORIGINAL_CEA_FIELD__':return await original(session,expression)
 async def ev(code):return await original(session,code)
 owner=InputOwner('192.168.10.113',(BRIDGE/'build/native-inspector/token.txt').read_text().strip())
 installed=False;borrowed=False;watch_intent=False;stop_intent=False;before_cc=None
 async def sample():
  return await ev("(()=>{const s=__originalCea,v=videoPlane;return{time:v.currentTime,frames:s.frames,currentFrame:s.source===v.currentSrc,source:v.currentSrc,paused:v.paused,ended:v.ended,ready:v.readyState,error:v.error?.code||null,prompt:!autoplayBtn.hidden,captionLength:localCaptions.textContent.trim().length,windows:localCaptions.children.length,authority:captionAuthorityEffective.textContent}})()")
 async def wait(predicate,label,seconds=40):
  deadline=time.monotonic()+seconds
  while time.monotonic()<deadline:
   v=await sample();report['last']=v;save()
   if v['error']:raise RuntimeError('Actual decode error '+label)
   if predicate(v):return v
   await asyncio.sleep(.2)
  raise RuntimeError('Timed out '+label+'; no replay')
 async def profile(service=1,restore=False,active=False):
  await ev("(()=>{const s=__originalCea,N=SageMiniStreaming.normalize;if(s.last&&JSON.stringify(N(JSON.parse(localStorage.getItem(s.keys[1])||'{}')))!==JSON.stringify(s.last))throw Error('Preserve changed stream');const v="+('s.originalStream' if restore else "{...s.borrowed,captionAuthority:'cc1',captions:'708',captionService:"+str(service)+"}")+",a="+('s.originalAuthority' if restore else "{...s.borrowedAuthority,cc1Service:"+str(service)+"}")+";for(const k of Object.keys(SageMiniStreaming.DEFAULTS)){const e=document.getElementById('stream_'+k);if(e){if(e.type==='checkbox')e.checked=!!v[k];else e.value=String(v[k])}}for(const k of Object.keys(SageMiniCaptionAuthority.DEFAULTS)){const e=document.getElementById(k==='mode'?'captionAuthorityMode':k);if(e)e.value=String(a[k])}if(saveStreaming.disabled)throw Error('Save busy');s.last=v;s.expectedAuthority=a;"+('applyStreaming' if active else 'saveStreaming')+".click();return true})()")
  deadline=time.monotonic()+15
  while time.monotonic()<deadline:
   if await ev("(()=>{const s=__originalCea;return!saveStreaming.disabled&&JSON.stringify(SageMiniStreaming.normalize(JSON.parse(localStorage.getItem(s.keys[1])||'{}')))===JSON.stringify(s.last)&&JSON.stringify(SageMiniCaptionAuthority.normalize(JSON.parse(localStorage.getItem(s.keys[2])||'{}')))===JSON.stringify(s.expectedAuthority)})()"):return
   await asyncio.sleep(.1)
  raise RuntimeError('Save receipt unknown; no replay')
 try:
  n=await asyncio.to_thread(guard)
  if n.get('fullyLoaded'):raise RuntimeError('Preserve loaded media')
  info=await asyncio.to_thread(C.request,cfg,'/SageTVWebPlayer/api/media?id=84270')
  if info.get('recording') or len(info['files'])!=1 or info['files'][0]['path']!='/var/media/OpenSageTV_Vibe_Tests/WEB097_LIVE_WTTW_STARTUP.ts' or info['files'][0]['streamSize']!=18800000:raise RuntimeError('Original broadcast prefix identity changed')
  before_cc=(await asyncio.to_thread(mcp,'captions.get',context=identity))['state']
  await ev("(()=>{if(document.visibilityState!=='visible'||window.__originalCea||videoPlane.getAttribute('src')||videoPlane.readyState)throw Error('Require visible unloaded phone');const keys=['sagetvWebMiniClientSettings.v1','sagetvWebStreaming.v1','sagetvWebCaptionAuthority.v1'],s=window.__originalCea={keys,saved:keys.map(k=>localStorage.getItem(k)),done:false,frames:0,source:''};s.originalStream=SageMiniStreaming.normalize(JSON.parse(s.saved[1]||'{}'));s.originalAuthority=SageMiniCaptionAuthority.normalize(JSON.parse(s.saved[2]||'{}'));s.borrowed=SageMiniStreaming.normalize({...s.originalStream,videoMode:'transcode',fps:'source',deinterlace:'off'});s.borrowedAuthority=SageMiniCaptionAuthority.normalize({...s.originalAuthority,mode:'cc1',cc1Type:'cea708',cc1Service:1});function f(){const src=videoPlane.currentSrc;videoPlane.requestVideoFrameCallback(()=>{if(s.done)return;if(src&&src===videoPlane.currentSrc){s.frames++;s.source=src}f()})}f();return true})()");installed=True
  borrowed=True;await profile()
  watch_intent=True;report['watchIntent']=True;save()
  if not (await asyncio.to_thread(mcp,'media.watch',context=identity,media_id=84270,wait_ms=0)).get('accepted'):raise RuntimeError('One Watch rejected')
  deadline=time.monotonic()+60;activation=False
  while time.monotonic()<deadline:
   v=await sample()
   if v['prompt'] and not activation:
    activation=True;await ev('autoplayBtn.focus();true');await owner.arm();await owner.send('key',key='enter');await owner.close()
   if v['error']:raise RuntimeError('Native decode error')
   if v['currentFrame'] and v['frames']>12 and not v['paused']:break
   await asyncio.sleep(.2)
  else:raise RuntimeError('No actual native pictures')
  first=await wait(lambda v:v['captionLength']>0,'real service1 caption')
  report['rows'].append(dict(gate='original-708-service1-visible',sample=first));save()
  report['applyService2Intent']=True;save();await profile(2,active=True)
  clear=await wait(lambda v:v['source']!=first['source'] and v['currentFrame'] and v['frames']>first['frames']+12 and v['captionLength']==0,'absent service2 clears on actual applied generation',45)
  report['rows'].append(dict(gate='absent-708-service2-clears',sample=clear));save()
  report['applyService1Intent']=True;save();await profile(1,active=True)
  back=await wait(lambda v:v['source']!=clear['source'] and v['currentFrame'] and v['frames']>clear['frames']+12 and v['captionLength']>0,'original service1 returns on applied generation',45)
  report['rows'].append(dict(gate='original-708-service1-restores',sample=back));save()
  await asyncio.to_thread(guard);report['seekIntentMs']=0;save()
  if not (await asyncio.to_thread(mcp,'media.seek',context=identity,target_ms=0)).get('accepted'):raise RuntimeError('One seek rejected')
  after=await wait(lambda v:v['source']!=back['source'] and v['currentFrame'] and v['frames']>back['frames']+12 and v['captionLength']>0,'new seek source with real708',50)
  report['rows'].append(dict(gate='seek-FLUSH-real708-new-pictures',sample=after));report['passed']=True
 finally:
  if watch_intent:
   try:
    n=await asyncio.to_thread(guard)
    if n.get('fullyLoaded') and (n.get('media') or {}).get('mediaFileId')!=84270:raise RuntimeError('Preserve changed source')
    if n.get('fullyLoaded'):
     stop_intent=True
     if not (await asyncio.to_thread(mcp,'media.control',context=identity,operation='stop')).get('accepted'):raise RuntimeError('One Stop receipt unknown')
    if before_cc is not None and not (await asyncio.to_thread(mcp,'captions.set',context=identity,state=before_cc)).get('ok'):raise RuntimeError('Caption restore unknown')
    report['ownedStopAccepted']=stop_intent
   except Exception:report['cleanup'].append('Stop/caption restore unknown; no replay')
  if borrowed:
   try:
    await profile(restore=True)
    report['profilesRestored']=await ev("(()=>{const s=__originalCea;for(let i=0;i<s.keys.length;i++){if(s.saved[i]===null)localStorage.removeItem(s.keys[i]);else localStorage.setItem(s.keys[i],s.saved[i])}return s.keys.every((k,i)=>localStorage.getItem(k)===s.saved[i])})()")
   except Exception:report['cleanup'].append('Profile restore unknown; preserve checkpoint')
  if installed:
   try:report['observerRemoved']=await ev('(()=>{__originalCea.done=true;'+('delete window.__originalCea;' if not report['cleanup'] else '')+'return true})()')
   except Exception:report['cleanup'].append('Observer cleanup unknown')
  await owner.close();report['passed']=report['passed'] and not report['cleanup'];save()
 return dict(passed=report['passed'],rows=len(report['rows']))
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,page_id=None,verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,screenshot=None)
async def run():
 async def attached(rsd,data):await W.inspect(rsd,data,args)
 await W.probe(args,report,on_rsd=attached)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
try:asyncio.run(asyncio.wait_for(run(),240))
except Exception as e:report.update(passed=False,errorType=type(e).__name__,error=str(e)[:240] if isinstance(e,RuntimeError) else 'Observation unavailable; no replay')
finally:W.evaluate=original;save()
print(json.dumps(dict(passed=report['passed'],rows=len(report['rows']),report=str(path),cleanup=report['cleanup'],error=report.get('error'))));raise SystemExit(0 if report['passed'] else 1)
