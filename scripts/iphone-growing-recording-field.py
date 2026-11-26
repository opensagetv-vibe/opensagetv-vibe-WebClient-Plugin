#!/usr/bin/env python3
"""Authorized real HDHR capture -> native Safari growth -> completed EOF.

Public recording/HLS APIs, exact owned reservation only. No Core Watch/live
tuner lease, no synthetic clocks, no native STV/finger/audibility claim.
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
parser.add_argument('--natural-completion',action='store_true',help='Keep owned recording until its real EPG end, at most45minutes; no early CancelRecord')
parser.add_argument('--channel',choices=('2.1','5.1','7.1','9.1','11.1','32.1'),help='Restrict the next independently free owned natural-completion capture')
options=parser.parse_args()
if options.channel and not options.natural_completion:parser.error('Channel restriction requires natural completion')
out=ROOT/'artifacts/active/WP11-008';out.mkdir(parents=True,exist_ok=True)
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');path=out/(stamp+'-iphone-growing-recording.json')
report=dict(passed=False,physicalPhone=True,nativeCoreWatch=False,physicalFingerGesture=False,
 userAuthorizedTestRecording=True,acoustic=False,rows=[],cleanup=[])
original=W.evaluate
class Trigger:
 def read_text(self,**_):return '__IPHONE_REAL_GROWTH__'
def save():path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
def producer_completion_ready(h):
 return h.get('activeRecording') is False and h.get('endList') is True and h.get('running') is False and h.get('exitCode') is not None
async def evaluate(session,expression):
 if expression!='__IPHONE_REAL_GROWTH__':return await original(session,expression)
 async def ev(code):return await original(session,code)
 async def request(endpoint,values=None):return await asyncio.to_thread(C.request,cfg,endpoint,values,timeout=30)
 async def guide():return (await request('/SageTVWebPlayer/api/guide?hours=1'))['airings']
 async def sched():return (await request('/SageTVWebPlayer/api/dvr'))['scheduled']
 async def active():return (await request('/SageTVWebPlayer/api/recordings?active=true&limit=500'))['recordings']
 async def poll(test,label,seconds=45):
  end=time.monotonic()+seconds
  while time.monotonic()<end:
   value=await test()
   if value:return value
   await asyncio.sleep(.25)
  raise RuntimeError('Timed out '+label+'; no ordered input replay')
 installed=False;record_intent=False;cancel_intent=False;producer=None;media_id=None;airing=None;baseline=None
 async def source():return next(x for x in await guide() if x['airingId']==airing['airingId'])
 async def info():return await request('/SageTVWebPlayer/api/media?id='+str(media_id))
 async def status():return await request('/SageTVWebPlayer/api/hls?session='+producer)
 async def cancel():
  nonlocal cancel_intent
  current=await source();reservations=[x for x in await sched() if x['airingId']==airing['airingId']]
  if cancel_intent or not record_intent or not current.get('manualRecord') or len(reservations)>1 or (not options.natural_completion and len(reservations)!=1) or (media_id and current.get('mediaId')!=media_id):
   raise RuntimeError('Exact cancellation ownership absent; never replay')
  cancel_intent=True;report['cancelIntent']=True;save()
  if not (await request('/SageTVWebPlayer/api/dvr',dict(action='cancel',airingId=airing['airingId']))).get('ok'):raise RuntimeError('Cancellation unacknowledged')
 async def sample():
  # Only this exact read-only observation may be retried. A wireless RPC
  # timeout is not evidence that the decoder failed, nor permission to replay
  # Record, Stop, Cancel, Watch or any phone input.
  expression="(()=>{const s=__growingPhone,v=s.video;return{time:v.currentTime,frames:s.frames,width:v.videoWidth,ready:v.readyState,paused:v.paused,ended:v.ended,endedEvents:s.ended,sourceCurrent:s.source===v.currentSrc,nativeHls:!!v.currentSrc&&!v.currentSrc.startsWith('blob:'),error:v.error?.code||null,blocked:s.blocked}})()"
  for attempt in range(3):
   try:return await ev(expression)
   except asyncio.TimeoutError:
    report['readOnlyObservationTimeouts']=report.get('readOnlyObservationTimeouts',0)+1;save()
    if attempt==2:raise
    await asyncio.sleep(.5)
 try:
  initial=await asyncio.to_thread(C.activity,cfg)
  if initial.get('recordingCount') or initial.get('connectedClientCount') or await active():raise RuntimeError('Require independently recording-idle server')
  contexts=await asyncio.to_thread(C.request,cfg,'/v1/control',dict(action='ui.list'),mcp=True)
  if contexts.get('contexts')!=['123c8282e1ee']:raise RuntimeError('Only exact idle phone allowed')
  baseline=await sched();occupied={x['airingId'] for x in baseline};now=int(time.time()*1000)
  allowed=('2.1','5.1','7.1','9.1','11.1','32.1') if options.natural_completion else ('7.1',)
  if options.channel:allowed=(options.channel,)
  candidates=[x for x in await guide() if x.get('channelNumber') in allowed and x.get('currentlyAiring') and now+120000<x['end']<now+2700000 and not x.get('mediaId') and not x.get('manualRecord') and not x.get('watched') and x['airingId'] not in occupied]
  if not candidates:raise RuntimeError('No free current bounded-duration airing; preserve other sources')
  airing=min(candidates,key=lambda x:(x['end'],x['airingId']));report['naturalCompletion']=options.natural_completion
  report['baseline']=dict(activity=initial,source=airing,schedule=baseline);save()
  await ev("(()=>{if(document.visibilityState!=='visible'||(localStorage.getItem('sagetvWebMiniClientId')||'').replace(/:/g,'').toLowerCase()!=='123c8282e1ee'||window.__growingPhone||videoPlane.getAttribute('src')||videoPlane.srcObject||videoPlane.readyState>0)throw Error('Require exact visible unloaded phone');const keys=['sagetvWebMiniClientSettings.v1','sagetvWebStreaming.v1','sagetvWebCaptionAuthority.v1'],v=document.createElement('video');v.muted=true;v.playsInline=true;v.style.cssText='position:fixed;inset:0;width:100%;height:100%;object-fit:contain;background:black;z-index:2147483000';const s=window.__growingPhone={video:v,keys,saved:keys.map(k=>localStorage.getItem(k)),frames:0,source:'',ended:0,done:false,blocked:false};v.addEventListener('ended',()=>s.ended++);document.body.append(v);function f(){const src=v.currentSrc;v.requestVideoFrameCallback(()=>{if(s.done)return;if(src&&src===v.currentSrc){s.frames++;s.source=src}f()})}f();return true})()");installed=True
  record_intent=True;report['recordIntent']=True;save()
  if not (await request('/SageTVWebPlayer/api/guide',dict(action='record',airingId=airing['airingId']))).get('accepted'):raise RuntimeError('Owned record rejected')
  async def captured():
   current=await source();return current if current.get('manualRecord') and current.get('mediaId') else None
  current=await poll(captured,'new recording');media_id=current['mediaId'];m=await info()
  if not m.get('recording') or m['channelNumber']!=airing['channelNumber'] or len(m['files'])!=1 or [x['id'] for x in await active()]!=[media_id]:raise RuntimeError('New capture identity mismatch')
  report['ownership']=dict(mediaId=media_id,path=m['files'][0]['path']);save()
  async def bytes_ready():return (await info())['files'][0]['streamSize']>4000000
  await poll(bytes_ready,'actual capture bytes')
  produced=await request('/SageTVWebPlayer/api/hls',dict(action='start',id=media_id,start=0,segment=0,audio=0));producer=produced.get('session')
  if not producer or produced.get('mediaId')!=media_id:raise RuntimeError('Producer identity mismatch')
  async def startup_ready():
   h=await status()
   # Preserve bounded transition evidence before a replacement clears stderr.
   # Observations never trigger or replay a producer/control request.
   observed={k:h.get(k) for k in ('fallbackStage','error','exitCode','running')}
   stages=report.setdefault('startupTransitions',[])
   if not stages or any(stages[-1].get(k)!=v for k,v in observed.items()):
    observed.update({k:h.get(k) for k in ('bytesInput','hlsSeconds','segments','hardware','hardwareDecode','hardwareFilters','firstSegmentMs')})
    observed['stderrTail']=(h.get('stderrTail') or '')[-2000:]
    if len(stages)<16:stages.append(observed)
   if h.get('error') and not h.get('running') and h.get('fallbackStage',0)>=2:
    report['startupFailure']={k:h.get(k) for k in ('error','stderrTail','exitCode','running','inputMode','bytesInput','hardware','hardwareDecode','hardwareFilters')};save()
    raise RuntimeError('Owned HLS producer failed before attachment')
   report['lastStartupStatus']={k:h.get(k) for k in ('error','exitCode','running','playlistReady','segments','endList','activeRecording','fallbackStage','hardware','hardwareDecode','hardwareFilters')};save()
   return h if h.get('playlistReady') and h.get('segments',0)>0 and not h.get('error') and not (h.get('activeRecording') and h.get('endList')) else None
  report['startup']=await poll(startup_ready,'real playable playlist before native attachment',60);save()
  url=cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/'+produced['playlistUrl']
  await ev("(()=>{const s=__growingPhone,v=s.video;v.src="+json.dumps(url)+";v.load();v.play().catch(()=>s.blocked=true);return true})()")
  async def pictures():
   v=await sample()
   if v['error'] or v['blocked']:raise RuntimeError('Actual native playback error/blocked')
   return v if v['sourceCurrent'] and v['frames']>10 and v['time']>.25 and not v['paused'] else None
  first=await poll(pictures,'actual native Safari pictures',70);samples=[]
  for _ in range(5):
   await asyncio.sleep(5);v=await sample();h=await status();m=await info()
   if v['error'] or v['endedEvents'] or not m['recording'] or not h.get('activeRecording') or h.get('endList'):raise RuntimeError('Premature growing EOF/error')
   samples.append(dict(video=v,bytes=m['files'][0]['streamSize'],inputBytes=h.get('bytesInput'),outputSeconds=h.get('hlsSeconds')))
  if samples[-1]['bytes']<=samples[0]['bytes'] or samples[-1]['video']['frames']<first['frames']+30:raise RuntimeError('No actual capture/frame growth')
  report['rows'].append(dict(gate='real-HDHR-growth-native-Safari-same-producer',passed=True,first=first,samples=samples));save();print('PASS phone real growing recording',flush=True)
  if options.natural_completion:
   report['naturalStartSample']=samples[-1];save()
   while time.time()*1000<airing['end']:
    await asyncio.sleep(min(20,max(.25,(airing['end']/1000)-time.time())))
    v=await sample();h=await status()
    if v['error'] or v['blocked']:raise RuntimeError('Native error during actual sustained recording')
    if time.time()*1000<airing['end']-1000 and (v['endedEvents'] or not h.get('activeRecording')):raise RuntimeError('Premature native live completion')
    report['naturalSamples']=report.get('naturalSamples',0)+1
    report['naturalLastSample']=dict(video=v,inputBytes=h.get('bytesInput'),outputSeconds=h.get('hlsSeconds'));save()
    if report['naturalSamples']%3==0:print(json.dumps(dict(observingNaturalCompletion=True,frames=v['frames'],time=v['time'],remainingSeconds=round(max(0,airing['end']/1000-time.time())))),flush=True)
  else:await cancel()
  async def completed():return not (await info())['recording'] and not await active()
  await poll(completed,'capture completion without live viewer lease',35)
  async def finished():
   h=await status();report['completionStatus']=h;save()
   # Atomic ENDLIST can precede the process-monitor exit receipt. Observe
   # actual termination; never kill a clean flushing producer to satisfy an
   # immediate assertion or infer failure from that short publication race.
   return h if producer_completion_ready(h) else None
  final=await poll(finished,'same producer ENDLIST',50)
  if final.get('exitCode')!=0 or final.get('running'):raise RuntimeError('Producer completion failed')
  async def ended():
   v=await sample()
   if v['error']:raise RuntimeError('Native decoder failed at completion')
   return v if v['ended'] and v['endedEvents'] and v['nativeHls'] else None
  last=await poll(ended,'actual native Safari EOF',100)
  report['rows'].append(dict(gate='real-recording-completion-ENDLIST-native-ended',passed=True,last=last,producer={k:final.get(k) for k in ('durationMs','hlsSeconds','exitCode','activeRecording','endList','hardware','hardwareDecode','hardwareFilters')}));report['passed']=True
 finally:
  if record_intent and not cancel_intent and not report['passed']:
   try:
    if (await source()).get('manualRecord'):await cancel()
   except Exception:report['cleanup'].append('Owned reservation cancellation unknown; no replay')
  if installed:
   try:
    restored=await ev("(()=>{const s=__growingPhone;s.done=true;s.video.pause();s.video.removeAttribute('src');s.video.load();s.video.remove();const ok=s.keys.every((k,i)=>localStorage.getItem(k)===s.saved[i]);delete window.__growingPhone;return ok})()")
    if not restored:report['cleanup'].append('Phone profiles mismatch')
   except Exception:report['cleanup'].append('Phone observer restoration unknown')
  if producer:
   try:
    if not (await request('/SageTVWebPlayer/api/hls',dict(action='stop',session=producer))).get('stopped'):raise RuntimeError()
   except Exception:report['cleanup'].append('Owned producer Stop unknown; no replay')
  if report['passed'] and not report['cleanup']:
   try:
    current=await info()
    if current['recording'] or len(current['files'])!=1 or current['files'][0]['path']!=report['ownership']['path'] or await sched()!=baseline:raise RuntimeError('Exact owned deletion guard')
    if not (await request('/SageTVWebPlayer/api/library',dict(action='unwatched',id=media_id))).get('ok'):raise RuntimeError('Watch restoration failed')
    report['deleteOwnedMediaIntent']=media_id;save()
    if not (await request('/SageTVWebPlayer/api/library',dict(action='deleteWithoutPrejudice',id=media_id,confirm='DELETE'))).get('ok'):raise RuntimeError('Delete unacknowledged')
    exact=await request('/SageTVWebPlayer/api/guide?action=recordStatus&airingId='+str(airing['airingId']))
    if exact.get('ok') is not True or exact.get('scheduled'):raise RuntimeError('Original reservation not restored')
    remaining=[x for x in await guide() if x['airingId']==airing['airingId']]
    if remaining and any(remaining[0].get(k) for k in ('mediaId','manualRecord','watched')):raise RuntimeError('Original airing not restored')
    report['ownedTestMediaRemoved']=True
   except Exception:report['cleanup'].append('Owned cleanup incomplete; retain manifest/no replay')
  report['passed']=report['passed'] and not report['cleanup'];save()
 return dict(passed=report['passed'],rows=len(report['rows']))
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,page_id=None,verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,screenshot=None)
async def run():
 async def attached(rsd,data):await W.inspect(rsd,data,args)
 await W.probe(args,report,on_rsd=attached)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
try:asyncio.run(asyncio.wait_for(run(),3000 if options.natural_completion else 330))
except Exception as e:report.update(passed=False,errorType=type(e).__name__,error=str(e)[:200] if isinstance(e,RuntimeError) else 'Bounded field observation unavailable; no replay')
finally:
 W.evaluate=original
 report['passed']=report['passed'] and len(report['rows'])==2 and not report['cleanup']
 save()
print(json.dumps(dict(passed=report['passed'],rows=len(report['rows']),report=str(path),error=report.get('error'),cleanup=report['cleanup'])));raise SystemExit(0 if report['passed'] else 1)
