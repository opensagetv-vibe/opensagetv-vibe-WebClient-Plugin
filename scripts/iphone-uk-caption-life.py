#!/usr/bin/env python3
"""Actual phone original UK captions: one source, public seek and STV controls.

No saved authority/profile change, synthetic captions, clock edits or replay.
"""
import asyncio,importlib.util,json,logging,sys,time
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
sys.path.insert(0,str(BRIDGE/'tools/native_inspector'))
import wireless_inspect as W
from field_hid import InputOwner
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration();identity='123c8282e1ee'
out=ROOT/'artifacts/active/WP04-007';out.mkdir(parents=True,exist_ok=True)
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');rows=[]
report={'passed':False,'physicalPhone':True,'physicalFingerGesture':False,'inputReplayed':False,'source':'original unchanged Breakfast','rows':rows}
def mcp(action,**kw):return C.request(cfg,'/v1/control',dict(action=action,**kw),mcp=True,timeout=45)
def guard():
 a=C.activity(cfg)
 if a['recordingCount'] or a['connectedClientCount'] or mcp('ui.list')['contexts']!=[identity]:raise RuntimeError('Require exact owned phone/no unrelated activity')
original=W.evaluate
class Trigger:
 def read_text(self,**_):return '__UK_PHONE_LIFETIME__'
async def evaluate(session,expression):
 if expression!='__UK_PHONE_LIFETIME__':return await original(session,expression)
 async def ev(code):return await original(session,code)
 activated=False
 async def sample():return await ev("(()=>{const s=__ukPhone,v=videoPlane,c=dvbCaptions,b=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let n=0;for(let i=3;i<b.length;i+=4)if(b[i])n++;return{time:v.currentTime,paused:v.paused,ready:v.readyState,error:v.error?.code||null,frames:s.frames,currentFrame:s.source===v.currentSrc,captionLength:localCaptions.textContent.trim().length,bitmapPixels:n,prompt:!autoplayBtn.hidden,authority:captionAuthorityEffective.textContent}})()")
 async def wait(test,label,seconds=45):
  nonlocal activated
  end=time.monotonic()+seconds
  while time.monotonic()<end:
   value=await sample()
   if value['error']:raise RuntimeError('Actual media error; '+label)
   if label=='actual initial moving picture' and value['prompt'] and not activated:
    activated=True
    focused=await ev("(()=>{if(autoplayBtn.hidden||autoplayBtn.disabled)throw Error('Activation prompt changed');autoplayBtn.focus();return document.activeElement===autoplayBtn})()")
    if not focused:raise RuntimeError('Actual activation target not focused')
    await owner.arm();await owner.send('key',key='enter');await owner.close()
    report['activation']='one real BLE Enter after observed Play prompt and synthetic exact focus'
   if test(value):return value
   await asyncio.sleep(.2)
  report['last']=value;raise RuntimeError('Timed out '+label+'; no replay')
 installed=False;watched=False;stopped=False;changed=False
 owner=InputOwner('192.168.10.113',(BRIDGE/'build/native-inspector/token.txt').read_text(encoding='ascii').strip())
 try:
  await asyncio.to_thread(guard)
  revision=await ev("(()=>[...document.scripts].find(e=>e.src.includes('miniclient-captions.js'))?.src.split('?')[1])()")
  expected=json.loads((ROOT/'BUILD_INFO.json').read_text(encoding='utf-8'))['asset_versions'].get('broadcast_controller')
  if expected and revision!='v=3.3.0-'+expected:raise RuntimeError('Wrong installed broadcast controller revision')
  report['verifiedCaptionRevision']=revision
  if (await asyncio.to_thread(mcp,'ui.state',context=identity))['fullyLoaded']:raise RuntimeError('Require unloaded test phone')
  before=(await asyncio.to_thread(mcp,'captions.get',context=identity))['state'];report['originalStvCaptionState']=before
  await ev("(()=>{if(document.visibilityState!=='visible'||window.__ukPhone||captionAuthorityMode.value!=='stv')throw Error('Phone/authority unavailable');const s=window.__ukPhone={settings:localStorage.getItem('sagetvWebMiniClientSettings.v1'),stream:localStorage.getItem('sagetvWebStreaming.v1'),captions:localStorage.getItem('sagetvWebCaptionAuthority.v1'),frames:0,done:false,source:''};function f(){const source=videoPlane.currentSrc;videoPlane.requestVideoFrameCallback(()=>{if(s.done)return;if(source===videoPlane.currentSrc){s.frames++;s.source=source;}f();});}f();return true})()");installed=True
  report['phase']='one-Watch'
  if not (await asyncio.to_thread(mcp,'media.watch',context=identity,media_id=11224,wait_ms=0)).get('accepted'):raise RuntimeError('One Watch rejected')
  watched=True;end=time.monotonic()+30
  while time.monotonic()<end:
   n=await asyncio.to_thread(mcp,'ui.state',context=identity)
   if n.get('fullyLoaded') and n.get('media',{}).get('mediaFileId')==11224:break
   await asyncio.sleep(.2)
  else:raise RuntimeError('Original source not loaded')
  report['phase']='one-initial-source-seek'
  if not (await asyncio.to_thread(mcp,'media.seek',context=identity,target_ms=30000)).get('accepted'):raise RuntimeError('One initial seek rejected')
  first=await wait(lambda v:v['currentFrame'] and v['frames']>12 and not v['paused'] and v['ready']>=2,'actual initial moving picture',65)
  rows.append({'gate':'original-native-HLS-picture','passed':True,'sample':first})
  for state,kind in [('CC1','teletext'),('CC2','dvb')]:
   await asyncio.to_thread(guard);changed=True;report['phase']='select-'+kind
   if not (await asyncio.to_thread(mcp,'captions.set',context=identity,state=state)).get('ok'):raise RuntimeError('One caption command rejected')
   selected=await wait(lambda v:v['captionLength']>0 if kind=='teletext' else v['bitmapPixels']>100,'visible '+kind)
   rows.append({'gate':kind+'-actually-visible','passed':True,'sample':selected})
   if not (await asyncio.to_thread(mcp,'captions.set',context=identity,state='Off')).get('ok'):raise RuntimeError('One Off rejected')
   cleared=await wait(lambda v:v['captionLength']==0 and v['bitmapPixels']==0,'Off removes both surfaces',12)
   rows.append({'gate':kind+'-Off-clears','passed':True,'sample':cleared})
  report['profilesPreserved']=await ev("(()=>{const s=__ukPhone;return s.settings===localStorage.getItem('sagetvWebMiniClientSettings.v1')&&s.stream===localStorage.getItem('sagetvWebStreaming.v1')&&s.captions===localStorage.getItem('sagetvWebCaptionAuthority.v1')})()")
  if not report['profilesPreserved']:raise RuntimeError('Saved profiles changed')
  report['passed']=True
 finally:
  try:
   await asyncio.to_thread(guard)
   if changed:report['nativeCaptionRestore']=(await asyncio.to_thread(mcp,'captions.set',context=identity,state=before)).get('ok')
   if watched:stopped=(await asyncio.to_thread(mcp,'media.control',context=identity,operation='stop')).get('accepted')
   report['stopAccepted']=stopped
  except Exception:report['cleanupUnknown']=True;report['passed']=False
  if installed:
   try:report['observerRemoved']=await ev("(()=>{__ukPhone.done=true;delete window.__ukPhone;return true})()")
   except Exception:report['passed']=False;report['observerCleanupUnknown']=True
  await owner.close()
 return {'passed':report['passed'],'rows':len(rows)}
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,page_id=None,verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,screenshot=out/(stamp+'-iphone-UK.png'))
async def run():
 async def attached(rsd,data):await W.inspect(rsd,data,args)
 await W.probe(args,report,on_rsd=attached)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
try:asyncio.run(asyncio.wait_for(run(),210))
except Exception as e:report.update(passed=False,errorType=type(e).__name__,error=str(e)[:200] if isinstance(e,RuntimeError) else 'Observation unavailable; no replay')
finally:
 W.evaluate=original
 path=out/(stamp+'-iphone-UK.json');path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':report['passed'],'rows':len(rows),'report':str(path)}));raise SystemExit(0 if report['passed'] else 1)
