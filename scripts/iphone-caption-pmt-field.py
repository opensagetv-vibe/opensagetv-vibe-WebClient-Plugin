#!/usr/bin/env python3
"""Actual iPhone generated DVB language/PMT lifetime; original UK stays separate.

One public Watch, real decoder/video/bitmap output, scoped normal settings Save
and exact restoration. No Core/private controls, cue injection or input replay.
"""
import argparse,asyncio,importlib.util,json,logging,re,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
sys.path.insert(0,str(BRIDGE/'tools/native_inspector'))
import wireless_inspect as W
from field_hid import InputOwner
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration();identity='123c8282e1ee'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--lifecycle',action='store_true',help='Add explicit generated-source seeks, actual EOF and idle reconnect/reopen')
parser.add_argument('--eof-only',action='store_true',help='Affected EOF/reconnect rows only; do not repeat qualified PMT transitions')
parser.add_argument('--seek-bounce',action='store_true',help='Targeted 48s ->5s ->60s new-picture sequence before EOF; requires --eof-only')
parser.add_argument('--fullscreen',action='store_true',help='Complete the known native preview through the existing guarded public showContent API')
parser.add_argument('--capture-visible',action='store_true',help='One3s physical HDMI capture while actual fullscreen Spanish pixels are visible')
options=parser.parse_args()
if options.capture_visible and not options.fullscreen:parser.error('--capture-visible requires --fullscreen')
if options.seek_bounce and not options.eof_only:parser.error('--seek-bounce requires --eof-only')
if options.eof_only:options.lifecycle=True
out=ROOT/'artifacts/active/WP04-007';out.mkdir(parents=True,exist_ok=True)
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');path=out/(stamp+'-iphone-caption-pmt.json')
report=dict(passed=False,physicalPhone=True,physicalFingerGesture=False,generatedSource=True,inputReplayed=False,lifecycle=options.lifecycle,rows=[],samples=[],cleanup=[])
original=W.evaluate
class Trigger:
 def read_text(self,**_):return '__CAPTION_PMT_PHONE__'
def save():path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
def mcp(action,**v):return C.request(cfg,'/v1/control',dict(action=action,**v),mcp=True,timeout=30)
def guard():
 a=C.activity(cfg)
 if a['recordingCount'] or a['connectedClientCount'] or mcp('ui.list')['contexts']!=[identity]:raise RuntimeError('Require exact phone/no unrelated activity')
 return mcp('ui.state',context=identity)
async def evaluate(session,expression):
 if expression!='__CAPTION_PMT_PHONE__':return await original(session,expression)
 async def ev(code):return await original(session,code)
 async def sample():
  v=await ev("(()=>{const s=__captionPmt,v=videoPlane,c=dvbCaptions,p=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let pixels=0,red=0,white=0;for(let i=0;i<p.length;i+=4)if(p[i+3]){pixels++;if(p[i]>200&&p[i+1]<130&&p[i+2]<80)red++;if(p[i]>200&&p[i+1]>200&&p[i+2]>200)white++;}return{time:v.currentTime,frames:s.frames,sourceCurrent:s.source===v.currentSrc,paused:v.paused,ready:v.readyState,error:v.error?.code||null,prompt:!autoplayBtn.hidden,pixels,red,white,metadata:s.metadata}})()")
  v.update(await ev("(()=>{const s=__captionPmt,v=videoPlane,c=dvbCaptions,r=c.getBoundingClientRect(),st=getComputedStyle(c);return{source:v.currentSrc,assigned:!!v.getAttribute('src'),endedEvents:s.endedEvents||0,bitmapVisible:document.visibilityState==='visible'&&r.width>0&&r.height>0&&r.right>0&&r.bottom>0&&r.left<innerWidth&&r.top<innerHeight&&st.visibility!=='hidden'&&st.display!=='none'&&Number(st.opacity)>0,bitmapBounds:{x:r.x,y:r.y,width:r.width,height:r.height}}})()"))
  report['samples'].append(v);save();return v
 async def wait(predicate,label,seconds=45):
  end=time.monotonic()+seconds
  while time.monotonic()<end:
   v=await sample()
   if v['error']:raise RuntimeError('Actual native decode error: '+label)
   if predicate(v):return v
   await asyncio.sleep(.25)
  raise RuntimeError('Timed out '+label+'; no replay')
 async def save_form(restore=False):
  await ev("(()=>{const s=__captionPmt,N=SageMiniStreaming.normalize;if("+str(restore).lower()+"&&(JSON.stringify(N(JSON.parse(localStorage.getItem('sagetvWebStreaming.v1')||'{}')))!==JSON.stringify(s.borrowed)||localStorage.getItem(s.keys[0])!==s.saved[0]||JSON.stringify(SageMiniCaptionAuthority.normalize(JSON.parse(localStorage.getItem(s.keys[2])||'{}')))!==JSON.stringify(s.borrowedAuthority)))throw Error('Preserve changed profile');const v="+('s.originalStream' if restore else 's.borrowed')+",a="+('s.originalAuthority' if restore else 's.borrowedAuthority')+";for(const k of Object.keys(SageMiniStreaming.DEFAULTS)){const e=document.getElementById('stream_'+k);if(e){if(e.type==='checkbox')e.checked=!!v[k];else e.value=String(v[k]);}}for(const k of Object.keys(SageMiniCaptionAuthority.DEFAULTS)){const e=document.getElementById(k==='mode'?'captionAuthorityMode':k);if(e)e.value=String(a[k]);}if(saveStreaming.disabled)throw Error('Save busy');saveStreaming.click();return true})()")
  end=time.monotonic()+15
  while time.monotonic()<end:
   okay=await ev("(()=>{const s=__captionPmt;return!saveStreaming.disabled&&JSON.stringify(SageMiniStreaming.normalize(JSON.parse(localStorage.getItem('sagetvWebStreaming.v1')||'{}')))===JSON.stringify("+('s.originalStream' if restore else 's.borrowed')+")})()")
   if okay:return
   await asyncio.sleep(.1)
  raise RuntimeError('Profile Save receipt unknown; no replay')
 owner=InputOwner('192.168.10.113',(BRIDGE/'build/native-inspector/token.txt').read_text().strip())
 installed=False;borrowed=False;watched=False;stopped=False;activation=False;mid=None;before_cc=None
 try:
  n=await asyncio.to_thread(guard)
  if n.get('fullyLoaded'):raise RuntimeError('Preserve loaded source')
  fixture='/var/media/OpenSageTV_Vibe_Tests/WP04-Caption-PMT/VibeCaptions-English-Spanish-PMT.ts'
  resolved=await asyncio.to_thread(mcp,'media.resolve_exact_path',path=fixture);mid=resolved.get('mediaFileId')
  if not mid:raise RuntimeError('Canonical generated source not imported')
  info=await asyncio.to_thread(C.request,cfg,'/SageTVWebPlayer/api/media?id='+str(mid))
  if info.get('recording') or len(info['files'])!=1 or info['files'][0]['path']!=fixture or info['files'][0]['streamSize']!=17576496:raise RuntimeError('Canonical generated media identity changed')
  report['generatedFixtureResetIntent']=True;save()
  if not (await asyncio.to_thread(mcp,'media.clear_watched',media_id=mid,confirm='true')).get('ok'):raise RuntimeError('Exact generated fixture reset unknown; no replay')
  report['mediaId']=mid;report['originalCaptionState']=before_cc=(await asyncio.to_thread(mcp,'captions.get',context=identity))['state']
  if not await ev('!!window.__iphoneGate'):await ev((ROOT/'tests/iphone-field-owner.js').read_text())
  end=time.monotonic()+32
  while not await ev('!!window.__iphoneGate?.done'):
   if time.monotonic()>end:raise RuntimeError('No fresh owned poll')
   await asyncio.sleep(.2)
  await ev("(()=>{if(document.visibilityState!=='visible'||window.__captionPmt||videoPlane.getAttribute('src')||videoPlane.readyState)throw Error('Require exact visible unloaded phone');const keys=['sagetvWebMiniClientSettings.v1','sagetvWebStreaming.v1','sagetvWebCaptionAuthority.v1'],s=window.__captionPmt={keys,saved:keys.map(k=>localStorage.getItem(k)),frames:0,done:false,source:'',metadata:null};s.originalStream=SageMiniStreaming.normalize(JSON.parse(s.saved[1]||'{}'));s.originalAuthority=SageMiniCaptionAuthority.normalize(JSON.parse(s.saved[2]||'{}'));s.borrowed=SageMiniStreaming.normalize({...s.originalStream,videoMode:'transcode',fps:'source',deinterlace:'off',captionAuthority:'stv',captions:'608',captionService:1});s.borrowedAuthority=SageMiniCaptionAuthority.normalize({...s.originalAuthority,mode:'stv',cc1Type:'dvb',cc1Language:'eng',cc2Type:'dvb',cc2Language:'spa'});function f(){const src=videoPlane.currentSrc;videoPlane.requestVideoFrameCallback(()=>{if(s.done)return;if(src&&src===videoPlane.currentSrc){s.frames++;s.source=src;}f()})}f();s.realFetch=window.fetch;s.fetch=function(...a){const r=s.realFetch.apply(this,a);if(String(a[0]?.url||a[0]).includes('/api/subtitles')||String(a[0]).startsWith('api/subtitles'))r.then(x=>x.clone().json()).then(j=>{if(!s.done&&j.dvbBitmap)s.metadata=j.dvbBitmap}).catch(()=>{});return r};window.fetch=s.fetch;return true})()");installed=True
  checkpoint=await ev('({keys:__captionPmt.keys,saved:__captionPmt.saved,borrowed:__captionPmt.borrowed,borrowedAuthority:__captionPmt.borrowedAuthority})')
  with (out/(stamp+'-caption-checkpoint.private.json')).open('x',encoding='utf-8') as f:json.dump(checkpoint,f)
  if options.lifecycle:
   await ev("(()=>{const s=__captionPmt;s.endedEvents=0;s.endedListener=()=>s.endedEvents++;videoPlane.addEventListener('ended',s.endedListener);s.startSessions=[];s.observedFetch=window.fetch;s.startFetch=function(...a){const r=s.observedFetch.apply(this,a);if(String(a[0]?.url||a[0]).includes('action=start'))r.then(x=>x.clone().json()).then(j=>{if(!s.done&&j.session&&s.startSessions.length<4)s.startSessions.push(j.session)}).catch(()=>{});return r};window.fetch=s.startFetch;return true})()")
  borrowed=True;await save_form()
  watched=True
  if not (await asyncio.to_thread(mcp,'media.watch',context=identity,media_id=mid,wait_ms=0)).get('accepted'):raise RuntimeError('One Watch rejected')
  end=time.monotonic()+70
  while time.monotonic()<end:
   v=await sample()
   if v['prompt'] and not activation:
    activation=True;await ev('autoplayBtn.focus();true');await owner.arm();await owner.send('key',key='enter');await owner.close()
   if v['error']:raise RuntimeError('Initial native decode error')
   if v['sourceCurrent'] and v['frames']>12 and not v['paused']:break
   await asyncio.sleep(.2)
  else:raise RuntimeError('No advancing native pictures')
  if options.fullscreen:
   async def view_request(action):
    if action not in ('contentState','showContent'):raise RuntimeError('Unexpected view action')
    await ev("(()=>{const s=__captionPmt;s.viewPending=true;s.viewResult=null;s.viewError=null;__iphoneGate.api("+json.dumps(action)+",{mediaId:"+str(mid)+"}).then(j=>s.viewResult=j).catch(e=>s.viewError=e.name).finally(()=>s.viewPending=false);return true})()")
    deadline=time.monotonic()+20
    while True:
     result=await ev('({pending:__captionPmt.viewPending,result:__captionPmt.viewResult,error:__captionPmt.viewError})')
     if not result['pending']:
      if result['error']:raise RuntimeError('View action receipt unavailable; no replay')
      return result['result']
     if time.monotonic()>deadline:raise RuntimeError('View receipt unknown; no replay')
     await asyncio.sleep(.2)
   before=await view_request('contentState')
   if not before.get('ready') or before.get('layout') not in ('preview','fullscreen'):raise RuntimeError('Unknown/modal native layout; preserve it')
   if before['layout']=='preview':
    report['showContentIntent']=True;save()
    if not (await view_request('showContent')).get('ok'):raise RuntimeError('Guarded native view changed; no replay')
   deadline=time.monotonic()+12
   while True:
    state=await view_request('contentState')
    if state.get('ready') and state.get('layout')=='fullscreen':break
    if time.monotonic()>deadline:raise RuntimeError('Native fullscreen not observed')
    await asyncio.sleep(.2)
   report['nativeFullscreen']=state;save()
  if not (await asyncio.to_thread(mcp,'captions.set',context=identity,state='CC1')).get('ok'):raise RuntimeError('CC1 rejected')
  white=await wait(lambda v:v['white']>=400,'actual English white bitmap',12);report['rows'].append(dict(gate='English-visible',sample=white))
  if options.fullscreen and not white['bitmapVisible']:raise RuntimeError('English bitmap not visible in viewport')
  if not options.eof_only:await wait(lambda v:v['time']>=5,'first language point',12)
  if not (await asyncio.to_thread(mcp,'captions.set',context=identity,state='CC2')).get('ok'):raise RuntimeError('CC2 rejected')
  red=await wait(lambda v:v['red']>=400,'actual Spanish red bitmap',10);report['rows'].append(dict(gate='Spanish-language-selection',sample=red))
  if options.fullscreen and not red['bitmapVisible']:raise RuntimeError('Spanish bitmap not visible in viewport')
  if options.capture_visible:
   report['physicalCaptureTrigger']=red;save()
   capture=await asyncio.to_thread(subprocess.run,['py','-3.12',str(ROOT/'scripts/capture-phone-hdmi.py'),'--task','WP04-007','--seconds','3'],capture_output=True,text=True,timeout=29,check=True)
   report['physicalHdmi']=json.loads(capture.stdout);save()
  if not options.eof_only:
   await wait(lambda v:v['time']>=8,'English return point',10)
   if not (await asyncio.to_thread(mcp,'captions.set',context=identity,state='CC1')).get('ok'):raise RuntimeError('English return rejected')
   await wait(lambda v:v['white']>=400,'English returns',8)
   while True:
    v=await sample()
    if v['time']>=17:break
    if v['time']<15 and v['pixels']==0:raise RuntimeError('Selected English bitmap cleared before PMT source time16s')
    await asyncio.sleep(.25)
   clear=await wait(lambda v:v['pixels']==0,'removed English clears',8);report['rows'].append(dict(gate='English-PMT-removal-timed-clear',sample=clear))
   if not (await asyncio.to_thread(mcp,'captions.set',context=identity,state='CC2')).get('ok'):raise RuntimeError('Remaining Spanish rejected')
   await wait(lambda v:v['red']>=400,'remaining Spanish pixels',10)
   while True:
    v=await sample()
    if v['time']>=33:break
    if v['time']<31 and v['pixels']==0:raise RuntimeError('Spanish bitmap cleared before PMT source time32s')
    await asyncio.sleep(.25)
   await wait(lambda v:v['pixels']==0,'all PMT services removed',8)
   restored=await wait(lambda v:v['time']>=48 and v['red']>=400,'actual Spanish service restoration',24)
   report['rows'].append(dict(gate='none-to-restored-Spanish',sample=restored))
  if options.lifecycle:
   if options.seek_bounce:
    old=await sample();report['seekLateIntentMs']=48000;save()
    if not (await asyncio.to_thread(mcp,'media.seek',context=identity,target_ms=48000)).get('accepted'):raise RuntimeError('One generated late seek rejected')
    late=await wait(lambda v:v['source']!=old['source'] and v['sourceCurrent'] and v['frames']>old['frames']+12 and v['red']>=400,'late-source new-picture Spanish pixels',50)
    report['rows'].append(dict(gate='late-source-new-picture-Spanish',sample=late))
   if not options.eof_only or options.seek_bounce:
    old=await sample();report['seekBackIntentMs']=5000;save()
    if not (await asyncio.to_thread(mcp,'media.seek',context=identity,target_ms=5000)).get('accepted'):raise RuntimeError('One generated seek back rejected')
    back=await wait(lambda v:v['source']!=old['source'] and v['sourceCurrent'] and v['frames']>old['frames']+12 and v['red']>=400,'new seek-generation Spanish pixels',50)
    report['rows'].append(dict(gate='seek-FLUSH-new-picture-Spanish',sample=back))
   old=await sample();ended_before=old['endedEvents'];report['seekTailIntentMs']=60000;save()
   if not (await asyncio.to_thread(mcp,'media.seek',context=identity,target_ms=60000)).get('accepted'):raise RuntimeError('One generated tail seek rejected')
   tail=await wait(lambda v:v['source']!=old['source'] and v['sourceCurrent'] and v['frames']>old['frames']+12 and v['red']>=400,'actual new tail pictures and visible Spanish bitmap',50)
   ended=await wait(lambda v:v['endedEvents']>ended_before,'actual native generated-source EOF',45)
   clear=await wait(lambda v:v['pixels']==0,'EOS clears caption surface',12)
   report['rows'].append(dict(gate='actual-EOF-clears',tail=tail,sample=clear,ended=ended))
   n=await asyncio.to_thread(guard)
   if n.get('fullyLoaded'):
    if (n.get('media') or {}).get('mediaFileId')!=mid:raise RuntimeError('Preserve other media before reconnect')
    stopped=True;report['preReconnectStopIntent']=True;save()
    if not (await asyncio.to_thread(mcp,'media.control',context=identity,operation='stop')).get('accepted'):raise RuntimeError('Pre-reconnect Stop receipt unknown; no replay')
   await wait(lambda v:not v['assigned'] and v['ready']==0 and v['pixels']==0,'idle before one reconnect',30)
   report['reconnectIntent']=True;save()
   await ev("(()=>{const b=document.getElementById('reconnectBtn');if(!b||b.disabled||videoPlane.getAttribute('src')||videoPlane.readyState)throw Error('Require idle production reconnect');b.click();return true})()")
   deadline=time.monotonic()+40
   while True:
    ready=await ev("(()=>({starts:__captionPmt.startSessions.length,connected:document.getElementById('connectionStatus').textContent.startsWith('connected'),pixels:__captionPmt.done}))()")
    activity=await asyncio.to_thread(C.activity,cfg)
    contexts=(await asyncio.to_thread(mcp,'ui.list'))['contexts']
    if activity['recordingCount'] or activity['connectedClientCount'] or any(x!=identity for x in contexts):raise RuntimeError('Unrelated activity during reconnect; preserve it')
    if ready['starts']==1 and ready['connected'] and contexts==[identity]:break
    if time.monotonic()>deadline:raise RuntimeError('Reconnect receipt unknown; no replay')
    await asyncio.sleep(.2)
   if (await asyncio.to_thread(guard)).get('fullyLoaded'):raise RuntimeError('Unexpected loaded source after idle reconnect')
   reopened_clear=await wait(lambda v:v['pixels']==0 and not v['assigned'],'new connection has no stale bitmap',10)
   report['rows'].append(dict(gate='idle-reconnect-no-stale-bitmap',sample=reopened_clear))
   report['reopenGeneratedFixtureResetIntent']=True;save()
   if not (await asyncio.to_thread(mcp,'media.clear_watched',media_id=mid,confirm='true')).get('ok'):raise RuntimeError('Reopen generated reset unknown; no replay')
   old=await sample();stopped=False;report['reopenWatchIntent']=True;save()
   if not (await asyncio.to_thread(mcp,'media.watch',context=identity,media_id=mid,wait_ms=0)).get('accepted'):raise RuntimeError('New Watch after completed reconnect rejected')
   activation=False;deadline=time.monotonic()+70
   while True:
    v=await sample()
    if v['prompt'] and not activation:
     activation=True;await ev('autoplayBtn.focus();true');await owner.arm();await owner.send('key',key='enter');await owner.close()
    if v['error']:raise RuntimeError('Reopened source decode error')
    if v['source']!=old['source'] and v['sourceCurrent'] and v['frames']>old['frames']+12 and not v['paused']:break
    if time.monotonic()>deadline:raise RuntimeError('No new reopened pictures; no Watch replay')
    await asyncio.sleep(.2)
   if not (await asyncio.to_thread(mcp,'captions.set',context=identity,state='CC1')).get('ok'):raise RuntimeError('New connection CC1 rejected')
   reopened=await wait(lambda v:v['white']>=400,'reopened English bitmap',12)
   report['rows'].append(dict(gate='reopen-new-picture-English',sample=reopened))
  report['passed']=True
 finally:
  if installed and watched and not report['passed']:
   try:
    report['failureNative']=await ev("(()=>{const v=videoPlane,r=v.buffered;return{source:v.currentSrc,time:v.currentTime,duration:Number.isFinite(v.duration)?v.duration:null,paused:v.paused,ended:v.ended,ready:v.readyState,width:v.videoWidth,error:v.error?.code||null,visibility:document.visibilityState,ranges:Array.from({length:r.length},(_,i)=>[r.start(i),r.end(i)]),stats:document.getElementById('stats').textContent.slice(0,4000),message:document.getElementById('osdMessage').textContent}})()")
    source_id=re.search(r'/hls/([a-f0-9]{32})/',report['failureNative']['source'])
    if source_id:
     h=await asyncio.to_thread(C.request,cfg,'/SageTVWebPlayer/api/hls?session='+source_id.group(1))
     report['failureProducer']={k:h.get(k) for k in ('session','dvd','durationMs','running','activeRecording','endList','exitCode','error','hlsSeconds','segments','bytesInput','startSeconds','hardware','hardwareDecode','hardwareFilters','fallbackStage','stderrTail')}
    save()
   except Exception:report['failureObservationUnknown']=True;save()
  if watched:
   try:
    n=await asyncio.to_thread(guard)
    if n.get('fullyLoaded') and (n.get('media') or {}).get('mediaFileId')!=mid:raise RuntimeError('Preserve changed native source and caption state')
    if not stopped and (n.get('media') or {}).get('mediaFileId')==mid and n.get('fullyLoaded'):
     stopped=True
     if not (await asyncio.to_thread(mcp,'media.control',context=identity,operation='stop')).get('accepted'):raise RuntimeError('Stop not acknowledged')
    if before_cc is not None and not (await asyncio.to_thread(mcp,'captions.set',context=identity,state=before_cc)).get('ok'):raise RuntimeError('Caption state not restored')
   except Exception:report['cleanup'].append('Exact Stop/caption restore unknown; no replay')
  if borrowed:
   try:
    await save_form(True)
    report['profilesRestored']=await ev("(()=>{const s=__captionPmt;for(let i=0;i<s.keys.length;i++){if(s.saved[i]===null)localStorage.removeItem(s.keys[i]);else localStorage.setItem(s.keys[i],s.saved[i]);}return s.keys.every((k,i)=>localStorage.getItem(k)===s.saved[i])})()")
   except Exception:report['cleanup'].append('Profile restoration unknown; preserve checkpoint/no replay')
  if installed:
   try:report['observerRestored']=await ev("(()=>{const s=__captionPmt;s.done=true;if(s.endedListener)videoPlane.removeEventListener('ended',s.endedListener);if(window.fetch===s.startFetch||window.fetch===s.fetch)window.fetch=s.realFetch;if(s.startSessions?.length===1&&window.__iphoneGate){window.__iphoneGate.cleanup?.();delete window.__iphoneGate;}delete window.__captionPmt;return true})()")
   except Exception:report['cleanup'].append('Observer restoration unknown')
  await owner.close();report['passed']=report['passed'] and not report['cleanup'];save()
 return dict(passed=report['passed'],rows=len(report['rows']))
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,page_id=None,verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,screenshot=None)
async def run():
 async def attached(rsd,data):await W.inspect(rsd,data,args)
 await W.probe(args,report,on_rsd=attached)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
try:asyncio.run(asyncio.wait_for(run(),420 if options.lifecycle else 240))
except Exception as e:report.update(passed=False,errorType=type(e).__name__,error=str(e)[:250] if isinstance(e,RuntimeError) else 'Bounded observation unavailable; no replay')
finally:W.evaluate=original;save()
print(json.dumps(dict(passed=report['passed'],rows=len(report['rows']),report=str(path),error=report.get('error'),cleanup=report['cleanup'])));raise SystemExit(0 if report['passed'] else 1)
