#!/usr/bin/env python3
"""Actual iPhone native-DVD portable search/Apply, not native trick decoding.

One exact generated fixture and approved phone. Real BLE activates controls;
synthetic focus/setup is labeled. No Core change, input replay or foreign Stop.
"""
import argparse,asyncio,base64,hashlib,importlib.util,io,json,logging,subprocess,sys,time,zipfile
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlencode
ROOT=Path(__file__).resolve().parents[1];BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
sys.path.insert(0,str(BRIDGE/'tools/native_inspector'))
import wireless_inspect as W
from field_hid import InputOwner
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
spec=importlib.util.spec_from_file_location('dvd_clock',ROOT/'scripts/dvd-field-clock.py')
Clock=importlib.util.module_from_spec(spec);spec.loader.exec_module(Clock)
p=argparse.ArgumentParser(description=__doc__);mode=p.add_mutually_exclusive_group();mode.add_argument('--apply-only',action='store_true');mode.add_argument('--diagnostics-only',action='store_true');mode.add_argument('--chapters-only',action='store_true');a=p.parse_args()
identity='123c8282e1ee';fixture=20819;owned=None
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');out=ROOT/'artifacts/active/WEB-023';out.mkdir(parents=True,exist_ok=True)
path=out/(stamp+('-dvd-apply' if a.apply_only else '-dvd-diagnostics' if a.diagnostics_only else '-dvd-chapters' if a.chapters_only else '-dvd-search')+'-iphone.json')
report=dict(passed=False,physicalPhone=True,physicalFingerGesture=False,nativeTrickDecoding=False,syntheticFocusAndFixtureSetup=True,rows=[],cleanup=[])
def save():path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')

def encoder_target(producer):
 # Paired PMD and SSH have deliberately separate pinned host environments.
 # Only a read-only bounded observation crosses into native Python/Paramiko.
 r=subprocess.run(['py','-3.12',str(ROOT/'scripts/dvd-field-observations.py'),'--producer',producer],capture_output=True,text=True,timeout=65)
 if r.returncode:raise RuntimeError('Read-only encoder observation unavailable')
 return json.loads(r.stdout)
def mcp(action,**values):return C.request(cfg,'/v1/control',dict(action=action,**values),mcp=True,timeout=12)
def guard(loaded=False):
 s=C.activity(cfg)
 if s.get('recordingCount')!=0 or s.get('connectedClientCount')!=0 or mcp('ui.list').get('contexts')!=[identity]:raise RuntimeError('Exact phone/no unrelated activity required')
 n=mcp('ui.state',context=identity)
 if loaded and (not n.get('dvd') or (n.get('media') or {}).get('mediaFileId')!=fixture):raise RuntimeError('Canonical DVD owner changed')
 return n
def api(action,**values):
 v=dict(session=owned,**values)
 if action in ('status','contentState','streamSettings'):return C.request(cfg,'/SageTVWebPlayer/api/miniclient?'+urlencode(dict(action=action,**v)))
 return C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action=action,**v))
original=W.evaluate
class Trigger:
 def read_text(self,**_):return '__PHONE_DVD_PORTABLE__'
async def evaluate(session,expression):
 global owned
 if expression!='__PHONE_DVD_PORTABLE__':return await original(session,expression)
 async def ev(code):return await original(session,code)
 async def sample():return await ev("(()=>{const s=__dvdPortable,v=videoPlane;return{epoch:s.epoch,frames:s.frames,time:v.currentTime,frameTime:s.frameTime,current:s.source===v.currentSrc,paused:v.paused,ready:v.readyState,width:v.videoWidth,error:v.error?.code||null,prompt:!autoplayBtn.hidden,commands:s.commands.slice(),trusted:s.trusted,assigned:!!v.getAttribute('src')}})()")
 async def wait(test,label,seconds=45):
  end=time.monotonic()+seconds
  while time.monotonic()<end:
   v=await sample()
   if v['error']:raise RuntimeError('Actual media error: '+label)
   if test(v):return v
   await asyncio.sleep(.15)
  report['last']=v;raise RuntimeError('Timed out '+label+'; no replay')
 owner=InputOwner('192.168.10.113',(BRIDGE/'build/native-inspector/token.txt').read_text().strip())
 async def button(target):
  await asyncio.to_thread(guard,True)
  focused=await ev("(()=>{const e=document.getElementById("+json.dumps(target)+");if(!e||e.disabled||!e.getClientRects().length)throw Error('Visible enabled button required');e.scrollIntoView({block:'center'});e.focus();return document.activeElement===e})()")
  if not focused:raise RuntimeError('Button focus unknown; no input')
  await owner.arm();await owner.send('key',key='enter');await owner.close()
  await asyncio.sleep(.15)
 installed=watched=borrowed=False;configured=None
 try:
  if (await asyncio.to_thread(guard)).get('fullyLoaded'):raise RuntimeError('Preserve loaded source')
  found=await asyncio.to_thread(mcp,'media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/OpenSageTV_Vibe_Test_DVD/VIDEO_TS')
  if found.get('mediaFileId')!=fixture:raise RuntimeError('Canonical fixture mismatch')
  await ev("(()=>{if(document.visibilityState!=='visible'||window.__dvdPortable||videoPlane.getAttribute('src')||videoPlane.readyState)throw Error('Visible unloaded phone required');const s=window.__dvdPortable={done:false,source:'',epoch:0,frames:0,frameTime:0,commands:[],trusted:0,streamRaw:localStorage.getItem('sagetvWebStreaming.v1'),clientRaw:localStorage.getItem('sagetvWebMiniClientSettings.v1')};s.original=SageMiniStreaming.normalize(JSON.parse(s.streamRaw||'{}'));s.realFetch=window.fetch;s.fetch=function(input,options){const u=new URL(typeof input==='string'?input:input instanceof URL?input.href:input.url,location.href),p=new URLSearchParams(options?.body||u.search),action=u.searchParams.get('action'),id=p.get('session')||u.searchParams.get('session');if(u.origin===location.origin&&u.pathname.endsWith('/api/miniclient')){if(['events','state','status'].includes(action)&&/^[a-f0-9-]{32,36}$/i.test(id||''))s.session=id;if(action==='command'&&s.commands.length<100)s.commands.push(Number(p.get('command')))}return s.realFetch.apply(this,arguments)};window.fetch=s.fetch;s.click=e=>{if(e.isTrusted)s.trusted++};document.addEventListener('click',s.click,true);function f(_,m){if(s.done)return;const src=videoPlane.currentSrc;if(src!==s.source){s.source=src;s.epoch++;s.frames=0}s.frames++;s.frameTime=m.mediaTime;s.frame=videoPlane.requestVideoFrameCallback(f)}s.frame=videoPlane.requestVideoFrameCallback(f);return true})()");installed=True
  end=time.monotonic()+45
  while not (owned:=await ev('__dvdPortable.session||null')):
   if time.monotonic()>end:raise RuntimeError('Fresh native owner not observed')
   await asyncio.sleep(.2)
  configured=(await asyncio.to_thread(api,'streamSettings'))['configured']
  if configured.get('companionDvd')!='false':raise RuntimeError('Native-only field requires existing companion-off profile')
  # A prior DVD Stop may leave SageMC's normal "Stopped" popup on the UI even
  # after the public player Close. Reset this owned idle UI with one Home,
  # rather than treating a popup's normal key routing as fullscreen playback.
  if not (await asyncio.to_thread(api,'command',command=28)).get('ok'):raise RuntimeError('One idle Home setup rejected')
  await asyncio.sleep(.7)
  report['phase']='normal-watch';save();watched=True
  if not (await asyncio.to_thread(api,'watchContent',mediaId=fixture)).get('accepted'):raise RuntimeError('One Watch rejected')
  end=time.monotonic()+25
  while True:
   view=await asyncio.to_thread(api,'contentState',mediaId=fixture)
   if view.get('ready') and view.get('layout') in ('preview','fullscreen'):break
   if time.monotonic()>end:raise RuntimeError('Native content state unavailable')
   await asyncio.sleep(.2)
  report['viewBeforeShow']=view;save()
  if view.get('layout')=='preview' and not (await asyncio.to_thread(api,'showContent',mediaId=fixture)).get('ok'):raise RuntimeError('One fullscreen request rejected')
  activated=False;end=time.monotonic()+60
  while True:
   v=await sample();n=await asyncio.to_thread(guard,True)
   if v['prompt'] and not activated:activated=True;await button('autoplayBtn')
   if v['width'] and v['ready']>=2 and isinstance(n.get('dvdMenu'),bool):break
   if time.monotonic()>end:raise RuntimeError('Initial DVD picture unavailable')
   await asyncio.sleep(.2)
  if not n['dvdMenu']:
   if not (await asyncio.to_thread(api,'command',command=67)).get('ok'):raise RuntimeError('One Root rejected')
   end=time.monotonic()+25
   while not (await asyncio.to_thread(guard,True)).get('dvdMenu'):
    if time.monotonic()>end:raise RuntimeError('Authored Root unavailable')
    await asyncio.sleep(.2)
  await ev("(()=>{for(let i=0;i<4&&!settingsPanel.hidden;i++)closeSettings.click();if(!remotePanel.hidden)hideRemote.click();stage.focus();return document.activeElement===stage})()")
  await asyncio.sleep(.5);await owner.arm();await owner.send('key',key='enter');await owner.close()
  first=await wait(lambda v:v['current'] and v['frames']>20 and v['time']>1 and not v['paused'],'actual feature',65)
  if (await asyncio.to_thread(guard,True)).get('dvdMenu') is not False:raise RuntimeError('Feature menu state unknown')
  # Root/Select can return SageMC to its preview context. Never test DVD-only
  # keys against a main menu and call the intentional normal key path a bug.
  view=await asyncio.to_thread(api,'contentState',mediaId=fixture)
  report['phase']='verify-native-and-GFX-fullscreen';report['featureViewBeforeShow']=view;save()
  if view.get('layout')=='preview':
   if not (await asyncio.to_thread(api,'showContent',mediaId=fixture)).get('ok'):raise RuntimeError('Feature fullscreen request rejected')
  end=time.monotonic()+15
  while True:
   view=await asyncio.to_thread(api,'contentState',mediaId=fixture)
   actual=await ev("(()=>{videoInfoBtn.click();const j=JSON.parse(videoInfoText.textContent);closeVideoInfo.click();return j.layout})()")
   report['lastFullscreenObservation']=dict(native=view,gfx=actual);save()
   if view.get('ready') and view.get('layout')=='fullscreen' and actual.get('presentation',{}).get('kind')=='fullscreen':break
   if time.monotonic()>end:raise RuntimeError('Actual native/GFX fullscreen feature unavailable')
   await asyncio.sleep(.2)
  report['actualFullscreenFeature']=True
  report['rows'].append(dict(gate='real-BLE-authored-Select-new-feature',sample=first));save()
  if a.chapters_only:
   for index in range(4):
    before=await sample();native=await asyncio.to_thread(guard,True);command=Clock.fixture_replacement_command(native)
    if command is None:raise RuntimeError('Safe fixture chapter replacement unavailable')
    report['phase']='single-chapter-'+str(index+1);save()
    if not (await asyncio.to_thread(api,'command',command=command)).get('ok'):raise RuntimeError('One chapter receipt rejected; no replay')
    after=await wait(lambda v:v['epoch']>before['epoch'] and v['current'] and v['frames']>15 and not v['paused'],'chapter pictures',65)
    await asyncio.sleep(1);start=await sample();n1=await asyncio.to_thread(guard,True);began=time.monotonic();await asyncio.sleep(5)
    end=await sample();n2=await asyncio.to_thread(guard,True);elapsed=time.monotonic()-began
    speed=Clock.presentation_speed(start,end,elapsed);native_delta=n2['rawMediaTimeMs']-n1['rawMediaTimeMs'];picture_delta=(end['frameTime']-start['frameTime'])*1000
    if speed is None or not .7<speed<1.3 or abs(native_delta-picture_delta)>2000 or n2.get('dvdMenu'):raise RuntimeError('Settled chapter picture/native clock mismatch')
    report['rows'].append(dict(gate='actual-native-iPhone-chapter-new-pictures-'+str(index+1),command=command,after=after,settled=end,presentationSpeed=speed,nativeDeltaMs=native_delta,pictureDeltaMs=round(picture_delta)));save()
  elif a.diagnostics_only:
   # Observe the normal generated ZIP, suppress ONLY its OS navigation. Native
   # Files/Share was previously qualified separately; this is not that claim.
   await ev("(()=>{const s=__dvdPortable;if(saveDiagnosticsToServer.checked)throw Error('Preserve enabled server export');const z=s.zipExport={create:URL.createObjectURL,click:HTMLAnchorElement.prototype.click};z.createHook=function(b){const u=z.create.apply(this,arguments);if(b.type==='application/zip'){if(z.blob)throw Error('Unexpected second diagnostic ZIP');z.blob=b;z.url=u}return u};z.clickHook=function(){if(this.download.startsWith('SageTV-WebPlayer-diagnostics-')&&this.href===z.url){z.downloaded=true;return}return z.click.apply(this,arguments)};URL.createObjectURL=z.createHook;HTMLAnchorElement.prototype.click=z.clickHook;if(remotePanel.hidden)remoteToggle.click();diagnosticsBtn.click();return true})()")
   await button('downloadReport');end=time.monotonic()+30
   while not await ev('!!(__dvdPortable.zipExport.blob&&__dvdPortable.zipExport.downloaded&&!downloadReport.disabled)'):
    if time.monotonic()>end:raise RuntimeError('Normal diagnostic export unavailable; no replay')
    await asyncio.sleep(.2)
   await ev("(()=>{const z=__dvdPortable.zipExport,b=z.blob;if(b.size>524288)throw Error('ZIP exceeds field bound');b.arrayBuffer().then(raw=>{if(__dvdPortable.zipExport!==z)return;const a=new Uint8Array(raw);let t='';for(let i=0;i<a.length;i+=8192)t+=String.fromCharCode(...a.subarray(i,i+8192));z.encoded=btoa(t)},()=>z.failed=true);return true})()")
   end=time.monotonic()+10
   while not await ev("(()=>{const z=__dvdPortable.zipExport;if(z.failed)throw Error('ZIP read unavailable');return typeof z.encoded==='string'})()"):
    if time.monotonic()>end:raise RuntimeError('Diagnostic byte observation unavailable')
    await asyncio.sleep(.1)
   encoded=await ev('__dvdPortable.zipExport.encoded')
   raw=base64.b64decode(encoded,validate=True)
   with zipfile.ZipFile(io.BytesIO(raw)) as bundle:
    if sum(x.file_size for x in bundle.infolist())>2097152:raise RuntimeError('Diagnostic uncompressed size exceeds bound')
    content=bundle.read('report.json');exported=json.loads(content)
    if hashlib.sha256(content).hexdigest()+'  report.json' not in bundle.read('hashes.sha256').decode():raise RuntimeError('Normal diagnostic hash mismatch')
   element=exported['browser']['playback']['element']
   if not(element['available'] and element['readyState']>=2 and element['videoWidth']>0 and element['paused'] is False and element['buffered']['available'] and 0<len(element['buffered']['ranges'])<=16):raise RuntimeError('Normal actual-phone video evidence unavailable')
   if any(k in element for k in ('src','currentSrc','url','mediaUrl')):raise RuntimeError('Diagnostic element exposes media URL')
   zip_path=out/(stamp+'-iphone-normal-diagnostics.zip')
   with zip_path.open('xb') as f:f.write(raw)
   report['rows'].append(dict(gate='real-BLE-normal-diagnostic-ZIP',zipSha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),reportHashVerified=True,videoElement=element,osDownloadNavigationSuppressed=True));save()
  elif a.apply_only:
   before=await sample();native=await asyncio.to_thread(guard,True)
   await ev("(()=>{const s=__dvdPortable;s.borrowed=SageMiniStreaming.normalize({...s.original,videoMode:'transcode',videoKbps:700,resolution:'480'});if(remotePanel.hidden)remoteToggle.click();remoteSettings.click();document.querySelector('#settingsCategories [data-settings-page=transcoding]').click();for(const[k,v]of Object.entries(s.borrowed)){const e=document.getElementById('stream_'+k);if(e){if(e.type==='checkbox')e.checked=!!v;else e.value=String(v)}}return true})()")
   checkpoint=await ev("(()=>{const s=__dvdPortable;return{original:s.streamRaw,borrowed:s.borrowed,client:s.clientRaw}})()")
   checkpoint['configured']=configured
   with (out/(stamp+'-dvd-apply-checkpoint.private.json')).open('x',encoding='utf-8') as f:json.dump(checkpoint,f)
   borrowed=True;report['phase']='real-BLE-profile-Apply';save();await button('applyStreaming')
   after=await wait(lambda v:v['epoch']>before['epoch'] and v['current'] and v['frames']>15 and not v['paused'],'profile replacement pictures',70)
   n=await asyncio.to_thread(guard,True);profile=await asyncio.to_thread(api,'streamSettings')
   st=await asyncio.to_thread(C.request,cfg,'/SageTVWebPlayer/api/hls?'+urlencode(dict(session=profile['session'])))
   report['producerObservation']={key:st.get(key) for key in ('encoder','hardware','hardwareDecode','hardwareFilters','fallbackStage','running','error')}
   report['encoderObservation']=await asyncio.to_thread(encoder_target,profile['session']);save()
   target=report['encoderObservation'];requested=(profile.get('active') or {}).get('requested') or {}
   if target['videoTarget']!='700k' or target['encodedHeight']!=480 or requested.get('videoKbps')!='700' or not st.get('hardware'):raise RuntimeError('Actual Apply encoder target/GPU/raster mismatch')
   # Outlast Core's temporary seek guess; compare paired advancing native and
   # actually presented clocks, not a nonexistent DVD effective-metadata field.
   began=time.monotonic();report['settledSamples']=[]
   while time.monotonic()-began<14:
    v=await sample();n=await asyncio.to_thread(guard,True)
    difference=n['rawMediaTimeMs']-(native['rawMediaTimeMs']+v['time']*1000)
    report['settledSamples'].append(dict(frames=v['frames'],frameTime=v['frameTime'],nativeMs=n['rawMediaTimeMs'],differenceMs=round(difference)))
    if v['error'] or v['paused'] or n.get('dvdMenu'):raise RuntimeError('Apply did not retain playable feature')
    if time.monotonic()-began>=8 and v['frameTime']>=after['frameTime']+5:
     if abs(difference)>3000:raise RuntimeError('Settled Apply title clock differs from presented output')
     break
    await asyncio.sleep(.35)
   else:raise RuntimeError('No sustained post-Apply pictures')
   report['rows'].append(dict(gate='real-BLE-active-DVD-Apply',before=before,after=v,actualTarget=700,encoder=target['encoder'],encodedHeight=target['encodedHeight'],nativeBeforeMs=native['rawMediaTimeMs'],nativeAfterMs=n['rawMediaTimeMs']));save()
  else:
   if not (await asyncio.to_thread(api,'command',command=65)).get('ok'):raise RuntimeError('One chapter setup rejected')
   chapter=await wait(lambda v:v['epoch']>first['epoch'] and v['frames']>15 and not v['paused'],'chapter new pictures',65)
   await asyncio.sleep(1);before=await sample();native=await asyncio.to_thread(guard,True);producer=(await asyncio.to_thread(api,'streamSettings'))['session'];mark=len(before['commands'])
   await ev('remotePanel.hidden&&remoteToggle.click();true')
   for target in ('nav_media_skip_forward','nav_media_skip_forward','nav_media_skip_back'):await button(target)
   await wait(lambda v:v['commands'][mark:]==[7,10,8,8,9],'atomic search sequence',8)
   if (await asyncio.to_thread(api,'streamSettings'))['session']!=producer:raise RuntimeError('Search rebuilt converter before acceptance')
   report['rows'].append(dict(gate='real-BLE-search-moves-no-rebuild',commands=[7,10,8,8,9]));save()
   await button('nav_select');after=await wait(lambda v:v['epoch']>before['epoch'] and v['current'] and v['frames']>15 and not v['paused'],'accepted search pictures',65)
   n=await asyncio.to_thread(guard,True)
   if abs(n['rawMediaTimeMs']-native['rawMediaTimeMs'])<5000:raise RuntimeError('Accepted native clock did not move')
   report['rows'].append(dict(gate='real-BLE-search-accept-new-pictures',sample=after,nativeBeforeMs=native['rawMediaTimeMs'],nativeAfterMs=n['rawMediaTimeMs'],approximateLanding=True));save()
   producer=(await asyncio.to_thread(api,'streamSettings'))['session'];before=await sample();mark=len(before['commands'])
   await button('nav_media_skip_forward');await button('nav_media_play')
   await wait(lambda v:v['commands'][mark:]==[7,10,8,7] and v['frames']>before['frames']+15,'Play cancel and ongoing pictures',12)
   if (await asyncio.to_thread(api,'streamSettings'))['session']!=producer:raise RuntimeError('Cancelled search replaced producer')
   report['rows'].append(dict(gate='real-BLE-Play-cancels-search-retains-producer'));save()
  report['passed']=True
 finally:
  if installed and not report['passed']:
   try:report['failureSample']=await sample();report['failureNative']=await asyncio.to_thread(guard,watched)
   except Exception:report['failureObservationUnknown']=True
   try:report['failureBrowser']=await ev("(()=>{videoInfoBtn.click();const j=JSON.parse(videoInfoText.textContent);closeVideoInfo.click();return{layout:j.layout,element:j.playback.element,status:j.playback.status}})()")
   except Exception:report['failureBrowserUnavailable']=True
  if watched:
   try:
    await asyncio.to_thread(guard,True)
    # SageMC's UI Stop is intentionally a two-stage popup, not player Close.
    # Use the existing public MCP CloseAndWait test teardown exactly once.
    if not (await asyncio.to_thread(mcp,'media.control',context=identity,operation='stop')).get('accepted'):raise RuntimeError('Close receipt unknown')
    await wait(lambda v:not v['assigned'] and v['ready']==0 and v['paused'],'owned decoder teardown',20)
   except Exception:report['cleanup'].append('Exact fixture Stop unknown; no replay')
  if borrowed:
   try:
    await ev("(()=>{const s=__dvdPortable;if(JSON.stringify(SageMiniStreaming.normalize(JSON.parse(localStorage.getItem('sagetvWebStreaming.v1')||'{}')))!==JSON.stringify(s.borrowed))throw Error('Preserve changed profile');for(const[k,v]of Object.entries(s.original)){const e=document.getElementById('stream_'+k);if(e){if(e.type==='checkbox')e.checked=!!v;else e.value=String(v)}}if(saveStreaming.disabled)throw Error('Save busy');saveStreaming.click();return true})()")
    end=time.monotonic()+20
    while not await ev("(()=>{const s=__dvdPortable;return!saveStreaming.disabled&&JSON.stringify(SageMiniStreaming.normalize(JSON.parse(localStorage.getItem('sagetvWebStreaming.v1')||'{}')))===JSON.stringify(s.original)})()"):
     if time.monotonic()>end:raise RuntimeError('Original Save receipt unknown')
     await asyncio.sleep(.2)
    await ev("(()=>{const s=__dvdPortable;if(s.streamRaw===null)localStorage.removeItem('sagetvWebStreaming.v1');else localStorage.setItem('sagetvWebStreaming.v1',s.streamRaw);return true})()")
   except Exception:report['cleanup'].append('Profile restore unknown; preserve private checkpoint')
  if installed:
   try:
    report['downloadObserversRestored']=await ev("(()=>{const z=__dvdPortable.zipExport;if(!z)return true;if(URL.createObjectURL!==z.createHook||HTMLAnchorElement.prototype.click!==z.clickHook)throw Error('Download observer ownership changed');URL.createObjectURL=z.create;HTMLAnchorElement.prototype.click=z.click;delete __dvdPortable.zipExport;return true})()")
   except Exception:report['cleanup'].append('Download observer restoration unknown')
   try:
    report['exactProfilesRestored']=await ev("(()=>{const s=__dvdPortable;return localStorage.getItem('sagetvWebStreaming.v1')===s.streamRaw&&localStorage.getItem('sagetvWebMiniClientSettings.v1')===s.clientRaw})()")
    if not report['exactProfilesRestored'] or (configured is not None and (await asyncio.to_thread(api,'streamSettings'))['configured']!=configured):report['cleanup'].append('Configured/profile baseline mismatch')
   except Exception:report['cleanup'].append('Profile comparison unavailable')
   try:
    report['observerRestored']=await ev("(()=>{const s=__dvdPortable;s.done=true;videoPlane.cancelVideoFrameCallback(s.frame);if(window.fetch===s.fetch)window.fetch=s.realFetch;document.removeEventListener('click',s.click,true);for(let i=0;i<4&&!settingsPanel.hidden;i++)closeSettings.click();if(!remotePanel.hidden)hideRemote.click();delete window.__dvdPortable;return true})()")
   except Exception:report['cleanup'].append('Observer restoration unknown')
  await owner.close();report['passed']=report['passed'] and not report['cleanup'];save()
 return dict(passed=report['passed'],rows=len(report['rows']))
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,page_id=None,verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,screenshot=None)
async def run():
 async def attached(rsd,data):await W.inspect(rsd,data,args)
 await W.probe(args,report,on_rsd=attached)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
try:asyncio.run(asyncio.wait_for(run(),360))
except Exception as e:report.update(passed=False,errorType=type(e).__name__,error=str(e)[:220] if isinstance(e,RuntimeError) else 'Bounded observation unavailable; no replay')
finally:W.evaluate=original;save()
print(json.dumps(dict(passed=report['passed'],rows=len(report['rows']),error=report.get('error'),cleanup=report['cleanup'],report=str(path))));raise SystemExit(0 if report['passed'] else 1)
