#!/usr/bin/env python3
"""Actual phone Guide Watch(current airing) across natural live programme end.

No Record reservation, simulated EPG, clock edit or repeated tune. Observe stock
Core rollover and production player, then Stop only this exact phone's stream.
"""
import argparse,asyncio,importlib.util,json,logging,sys,time
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
from field_candidate import playback_revision
ROOT=Path(__file__).resolve().parents[1];BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
sys.path.insert(0,str(BRIDGE/'tools/native_inspector'))
import wireless_inspect as W
from field_hid import InputOwner
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration();identity='123c8282e1ee'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--channel',choices=('7.1','11.1'),default='7.1')
options=parser.parse_args()
out=ROOT/'artifacts/active/WEB-098';out.mkdir(parents=True,exist_ok=True)
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');path=out/(stamp+'-iphone-live-handoff.json')
report=dict(passed=False,physicalPhone=True,nativeCoreWatch=True,physicalFingerGesture=False,rows=[],cleanup=[],watchReplayed=False)
original=W.evaluate
class Trigger:
 def read_text(self,**_):return '__PHONE_LIVE_HANDOFF__'
def save():path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
async def evaluate(session,expression):
 if expression!='__PHONE_LIVE_HANDOFF__':return await original(session,expression)
 async def ev(code):return await original(session,code)
 async def request(endpoint,values=None):return await asyncio.to_thread(C.request,cfg,endpoint,values,timeout=15)
 async def mcp(action,**kw):return await asyncio.to_thread(C.request,cfg,'/v1/control',dict(action=action,**kw),mcp=True,timeout=20)
 async def ui():return await mcp('ui.state',context=identity)
 async def guard(initial=False):
  a=await asyncio.to_thread(C.activity,cfg)
  if a['connectedClientCount'] or (await mcp('ui.list')).get('contexts')!=[identity]:raise RuntimeError('Unrelated clients; preserve them')
  if initial and a['recordingCount']:raise RuntimeError('Initially busy tuner/recording')
 async def sample():return await ev("(()=>{const s=__livePhone,v=videoPlane;return{time:v.currentTime,frames:s.frames,current:s.source===v.currentSrc,source:v.currentSrc,ready:v.readyState,width:v.videoWidth,paused:v.paused,ended:v.ended,error:v.error?.code||null,prompt:!autoplayBtn.hidden,player:s.player?.snapshot()||null}})()")
 installed=owner_created=watch_intent=stop_intent=False;air=None;baseline=None;first_mid=None
 try:
  await guard(True)
  current=await ui()
  if current.get('fullyLoaded'):raise RuntimeError('Require stopped phone before one live Watch')
  guide=await request('/SageTVWebPlayer/api/guide?hours=2');now=int(time.time()*1000)
  candidates=[x for x in guide['airings'] if x.get('channelNumber')==options.channel and x.get('currentlyAiring') and now+90000<x['end']<now+1800000 and not x.get('manualRecord') and not x.get('mediaId')]
  if len(candidates)!=1:raise RuntimeError('Require exact free chosen-channel airing within30minute boundary')
  air=candidates[0];next_rows=[x for x in guide['airings'] if x.get('channelNumber')==options.channel and x['start']==air['end']]
  if len(next_rows)!=1:raise RuntimeError('Exact next guide programme unavailable')
  baseline=(await request('/SageTVWebPlayer/api/dvr'))['scheduled'];report['airing']=air;report['nextAiring']=next_rows[0];report['baselineSchedule']=baseline;save()
  if not await ev('!!window.__iphoneGate'):
   await ev((ROOT/'tests/iphone-field-owner.js').read_text(encoding='utf-8'));owner_created=True
  deadline=time.monotonic()+32
  while not await ev('!!window.__iphoneGate?.done'):
   if time.monotonic()>deadline:raise RuntimeError('Fresh production session not observed; no Watch')
   await asyncio.sleep(.2)
  revision=await ev("(()=>[...document.scripts].find(e=>e.src.includes('miniclient-playback.js'))?.src.split('?')[1])()")
  if revision!=playback_revision(ROOT):raise RuntimeError('Wrong installed playback candidate')
  report['playbackRevision']=revision
  await ev("(()=>{if(window.__livePhone||document.visibilityState!=='visible'||videoPlane.getAttribute('src')||videoPlane.srcObject||videoPlane.readyState>0)throw Error('Require visible unloaded phone');const keys=['sagetvWebMiniClientSettings.v1','sagetvWebStreaming.v1','sagetvWebCaptionAuthority.v1'],s=window.__livePhone={keys,saved:keys.map(k=>localStorage.getItem(k)),frames:0,source:'',player:null,done:false};s.original=SageMiniPlayback.prototype.start;s.wrap=function(...args){s.player=this;return s.original.apply(this,args)};SageMiniPlayback.prototype.start=s.wrap;function f(){const src=videoPlane.currentSrc;videoPlane.requestVideoFrameCallback(()=>{if(s.done)return;if(src&&src===videoPlane.currentSrc){s.frames++;s.source=src}f()})}f();return true})()");installed=True
  watch_intent=True;report['watchIntent']=True;save()
  await ev("(()=>{const s=__livePhone;s.pending=true;s.receipt=null;s.failed=false;__iphoneGate.api('watchContent',{airingId:"+str(air['airingId'])+"}).then(r=>s.receipt=r).catch(()=>s.failed=true).finally(()=>s.pending=false);return true})()")
  deadline=time.monotonic()+25
  while await ev('__livePhone.pending'):
   if time.monotonic()>deadline:raise RuntimeError('Watch receipt unknown; no replay')
   await asyncio.sleep(.1)
  receipt=await ev('__livePhone.receipt')
  if not receipt or not receipt.get('accepted'):raise RuntimeError('One production live Watch unacknowledged')
  activated=False;deadline=time.monotonic()+75
  while time.monotonic()<deadline:
   v=await sample();n=await ui();mid=(n.get('media') or {}).get('mediaFileId')
   if v['error']:raise RuntimeError('Initial live decoder error')
   if v['prompt'] and not activated:
    await ev("(()=>{if(autoplayBtn.hidden||autoplayBtn.disabled)throw Error('Activation changed');autoplayBtn.focus();return document.activeElement===autoplayBtn})()")
    owner=InputOwner('192.168.10.113',(BRIDGE/'build/native-inspector/token.txt').read_text(encoding='ascii').strip())
    try:await owner.arm();await owner.send('key',key='enter');activated=True
    finally:await owner.close()
   if mid and v['current'] and v['frames']>15 and v['ready']>=2 and not v['paused']:
    info=await request('/SageTVWebPlayer/api/media?id='+str(mid))
    if info['channelNumber']!=options.channel or not info['recording']:raise RuntimeError('Not actual chosen-channel live capture')
    first_mid=mid;first=v;report['rows'].append(dict(gate='one-production-live-Watch-new-recording-and-actual-frames',passed=True,mediaId=mid,first=v,native=n));save()
    # Same source-scoped fullscreen completion as the production mobile Play
    # action. This is synthetic setup, never another Watch/tune or finger claim.
    await ev("(()=>{const s=__livePhone;s.showPending=true;s.showReceipt=null;__iphoneGate.api('showContent',{airingId:"+str(air['airingId'])+"}).then(r=>s.showReceipt=r).finally(()=>s.showPending=false);return true})()")
    print('PASS actual production live pictures',flush=True);break
   await asyncio.sleep(.2)
  else:report['last']=v;raise RuntimeError('No new actual live pictures')
  deadline=air['end']/1000+150;last_note=0;handoff=None
  while time.time()<deadline:
   await asyncio.sleep(5);v=await sample();n=await ui();mid=(n.get('media') or {}).get('mediaFileId')
   report['last']=dict(utc=datetime.now(timezone.utc).isoformat(),video=v,native=n);save()
   if v['error']:raise RuntimeError('Actual live decoder error at handoff')
   if time.monotonic()-last_note>50:
    print(json.dumps(dict(liveHandoffPending=True,frames=v['frames'],mediaId=mid,remainingSeconds=round(max(0,air['end']/1000-time.time())))),flush=True);last_note=time.monotonic()
   if time.time()*1000>=air['end'] and mid and mid!=first_mid and v['source']!=first['source'] and v['current'] and v['ready']>=2 and not v['paused']:
    info=await request('/SageTVWebPlayer/api/media?id='+str(mid))
    if info['channelNumber']!=options.channel or info['start']!=report['nextAiring']['start']:raise RuntimeError('Unexpected next programme identity')
    handoff=dict(video=v,native=n,mediaId=mid);await asyncio.sleep(10);after=await sample()
    if after['source']!=v['source'] or after['error'] or after['frames']<v['frames']+40 or after['paused']:raise RuntimeError('Next programme did not sustain pictures')
    report['rows'].append(dict(gate='natural-live-programme-handoff-next-native-file-and-moving-source',passed=True,handoff=handoff,after=after));report['passed']=True;break
  if not handoff:raise RuntimeError('No actual live handoff within150s after boundary; no retune replay')
 finally:
  if watch_intent and not stop_intent:
   try:
    await guard();n=await ui()
    if n.get('fullyLoaded'):
     mid=(n.get('media') or {}).get('mediaFileId');info=await request('/SageTVWebPlayer/api/media?id='+str(mid))
     if info['channelNumber']!=options.channel:raise RuntimeError('Foreign media; preserve it')
     stop_intent=True;report['stopIntent']=True;save()
     if not (await mcp('media.control',context=identity,operation='stop')).get('accepted'):raise RuntimeError('Stop rejected')
   except Exception:report['cleanup'].append('Exact phone Stop unconfirmed; no replay')
  if installed:
   try:
    same=await ev("(()=>{const s=__livePhone;s.done=true;const same=s.keys.every((k,i)=>localStorage.getItem(k)===s.saved[i]);if(SageMiniPlayback.prototype.start!==s.wrap)throw Error('Observer replaced');SageMiniPlayback.prototype.start=s.original;delete window.__livePhone;return same})()")
    if not same:report['cleanup'].append('Saved profiles changed')
   except Exception:report['cleanup'].append('Observer restoration unknown')
  if owner_created:
   try:await ev("(()=>{__iphoneGate.cleanup();delete window.__iphoneGate;return true})()")
   except Exception:report['cleanup'].append('Field-owner restoration unknown')
  if baseline is not None and (await request('/SageTVWebPlayer/api/dvr'))['scheduled']!=baseline:report['cleanup'].append('Original schedule mismatch')
  save()
 return dict(passed=report['passed'],rows=len(report['rows']))
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,page_id=None,verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,screenshot=None)
async def run():
 async def attached(rsd,data):await W.inspect(rsd,data,args)
 await W.probe(args,report,on_rsd=attached)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
try:asyncio.run(asyncio.wait_for(run(),2100))
except Exception as e:report.update(passed=False,errorType=type(e).__name__,error=str(e)[:200] if isinstance(e,RuntimeError) else 'Bounded observation unavailable; no replay')
finally:
 W.evaluate=original;report['passed']=report['passed'] and len(report['rows'])==2 and not report['cleanup'];save()
print(json.dumps(dict(passed=report['passed'],rows=len(report['rows']),report=str(path),error=report.get('error'),cleanup=report['cleanup'])));raise SystemExit(0 if report['passed'] else 1)
