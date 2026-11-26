#!/usr/bin/env python3
"""One real stock232 DVD seek with settled presented/title-clock evidence.

Public MCP Seek is setup, not production dependency. No metadata/settings/Core
edits, retries of ordered controls, time writes or fake browser frames.
"""
import importlib.util,json,os,time,shlex
from pathlib import Path
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
engine=os.environ.get('SAGETV_BROWSER_ENGINE','webkit')
if engine not in ('webkit','chromium'):raise RuntimeError('Unsupported engine')
identity='da92a86446be';owned=None;page=None;browser=None;context=None;pw=None
reconfigure=os.environ.get('SAGETV_DVD_RECONFIGURE_PROBE')=='1'
configured_before=None;restore_params=None;configuration_intent=False
current_position=os.environ.get('SAGETV_DVD_RECONFIGURE_CURRENT')=='1'
paused_probe=os.environ.get('SAGETV_DVD_RECONFIGURE_PAUSED')=='1'
production_apply=os.environ.get('SAGETV_DVD_RECONFIGURE_APPLY')=='1'
profile_encoder=os.environ.get('SAGETV_DVD_RECONFIGURE_ENCODER','software')
if profile_encoder not in ('software','qsv'):raise RuntimeError('Unsupported field encoder')
if production_apply and not (reconfigure and current_position):raise RuntimeError('Production Apply requires same-position profile probe')
if (current_position or paused_probe) and not reconfigure:raise RuntimeError('Profile probe required')
out=ROOT/'artifacts/active'/('WEB-108' if reconfigure else 'WP08-004');out.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());report=dict(passed=False,realStock232=True,physicalIPhone=False,engine=engine,rows=[],samples=[],errors=[],cleanup=[])
def mcp(action,**v):return C.request(cfg,'/v1/control',dict(action=action,**v),mcp=True,timeout=60 if action=='media.seek' else 10)
def api(action,**v):
 params=dict(action=action,session=owned,**v)
 # A POST streamSettings with no profile is a WRITE of server defaults, not a
 # read. Keep observations read-only; only explicit edits use the POST path.
 if action in ('status','contentState') or (action=='streamSettings' and not v):
  return C.request(cfg,'/SageTVWebPlayer/api/miniclient?'+urlencode(params))
 return C.request(cfg,'/SageTVWebPlayer/api/miniclient',params)

def encoder_target(producer):
 if not isinstance(producer,str) or len(producer)!=32 or any(c not in '0123456789abcdef' for c in producer):
  raise RuntimeError('Invalid producer identity')
 with C.ssh(cfg) as client:
  rows=C.remote(client,'docker exec '+shlex.quote(cfg['unraid_container_name'])+' ps -eww -o args').splitlines()
 # The MIM bridge and its real encoder legitimately expose the same arguments.
 # Count the actual FFmpeg child, not the forwarding bridge as a second encode.
 matches=[shlex.split(row) for row in rows if '/'+producer+'/stream.m3u8' in row and ' -c:v ' in row and row.split()[0].endswith('/ffmpeg.real')]
 if len(matches)!=1:
  report['encoderDiagnostic']=dict(matchingProducerRows=sum(producer in row for row in rows),encoderRows=[row[-1600:] for row in rows if producer in row or ' -c:v ' in row])
  raise RuntimeError('Expected one exact owned DVD encoder')
 command=matches[0]
 values=[command[i+1] for i,x in enumerate(command[:-1]) if x=='-b:v']
 # WebKit reports DVD display dimensions (PAR-corrected), not necessarily the
 # encoded raster. Probe one existing owned segment, not a guessed CSS size.
 playlist=command[-1]
 if not playlist.endswith('/'+producer+'/stream.m3u8'):raise RuntimeError('Encoder output identity mismatch')
 probe=command[0].rsplit('/',1)[0]+'/ffprobe'
 segment=playlist.rsplit('/',1)[0]+'/seg_00002.ts'
 with C.ssh(cfg) as client:
  encoded=json.loads(C.remote(client,' '.join(shlex.quote(x) for x in ('docker','exec',cfg['unraid_container_name'],probe,'-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','json',segment))))
 sizes={(s.get('width'),s.get('height')) for s in encoded.get('streams',[])}
 if len(sizes)!=1:raise RuntimeError('Ambiguous owned encoded raster')
 width,height=sizes.pop()
 return dict(videoTarget=values[0] if len(values)==1 else None,encoder=command[command.index('-c:v')+1],encodedWidth=width,encodedHeight=height)
def state():
 n=mcp('ui.state',context=identity)
 if not n.get('dvd') or (n.get('media') or {}).get('mediaFileId')!=20819:raise RuntimeError('Canonical DVD owner changed')
 return n
def wait(test,label,seconds=45):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  if test():return
  page.wait_for_timeout(150)
 raise RuntimeError('Timed out: '+label)
def observe(response):
 global owned
 if '/api/miniclient' not in response.url or response.request.method!='POST':return
 try:
  r=response.json()
  if r.get('session') and r.get('clientId','').replace(':','').lower()==identity:owned=r['session']
 except Exception:pass
def video():return page.evaluate('()=>({time:videoPlane.currentTime,frames:DVD_CLOCK.frames,last:DVD_CLOCK.last,newSource:videoPlane.currentSrc!==DVD_CLOCK.source,paused:videoPlane.paused,ready:videoPlane.readyState,width:videoPlane.videoWidth,height:videoPlane.videoHeight,error:videoPlane.error?.code||null,blocked:!autoplayBtn.hidden,message:osdMessage.textContent})')
def activate():
 if page.locator('#autoplayBtn').is_visible():page.locator('#autoplayBtn').click()
try:
 a=C.activity(cfg)
 if a.get('recordingCount')!=0 or a.get('connectedClientCount')!=0 or mcp('ui.list').get('contexts'):raise RuntimeError('Require independent idle server')
 pw=sync_playwright().start();browser=pw.webkit.launch(headless=True) if engine=='webkit' else pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
 context=browser.new_context(viewport={'width':852,'height':393},service_workers='block',http_credentials={'username':cfg['web_username'],'password':cfg['web_password']})
 context.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify({player:'hls',videoMode:'transcode',encoder:'software',videoKbps:1200,resolution:'480',deinterlace:'on',allowFallback:false,companionDvd:false}));")
 page=context.new_page();page.on('response',observe);page.on('pageerror',lambda error:report['errors'].append(type(error).__name__))
 page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
 wait(lambda:owned and api('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'),'owned native frame')
 original=page.evaluate('JSON.stringify(localStorage)')
 page.evaluate("()=>{const s=window.DVD_CLOCK={source:'',frames:0,last:0};function arm(){const src=videoPlane.currentSrc;videoPlane.requestVideoFrameCallback((n,m)=>{if(src&&src===videoPlane.currentSrc&&src!==s.source){s.frames++;s.last=m.mediaTime}arm()})}arm()}")
 if not api('watchContent',mediaId=20819).get('accepted'):raise RuntimeError('One production Watch rejected')
 wait(lambda:api('contentState',mediaId=20819).get('ready'),'exact loaded source')
 layout=api('contentState',mediaId=20819).get('layout')
 if layout=='preview':
  if not api('showContent',mediaId=20819).get('ok'):raise RuntimeError('One fullscreen request refused')
 elif layout!='fullscreen':raise RuntimeError('Unknown native layout')
 wait(lambda:video()['width']>0 and isinstance(state().get('dvdMenu'),bool),'decoded authored source')
 activate()
 if state().get('dvdMenu'):
  page.evaluate('()=>{DVD_CLOCK.source=videoPlane.currentSrc;DVD_CLOCK.frames=0;DVD_CLOCK.last=0}')
  page.locator('#stage').focus();page.keyboard.press('Enter')
  wait(lambda:state().get('dvdMenu') is False and video()['newSource'] and video()['frames']>=30 and video()['time']>2 and not video()['paused'],'moving feature')
 else:
  # A normal plugin reload can preserve stock's resume bookmark. Do not send
  # Select into an already-playing feature or clear persistent watched state.
  report['stockResumedFeature']=True
  wait(lambda:state().get('dvdMenu') is False and video()['frames']>=30 and video()['time']>2 and not video()['paused'],'stock resumed feature')
 if reconfigure:
  report['stage']='prepare-next-generation-profile'
  previous=api('streamSettings');configured_before=previous['configured'];old_producer=previous['session'];old_generation=previous['dvd']['generation']
  # Preserve the exact existing native request, including capability flags.
  # Re-probing can change capabilities and would not isolate the bitrate edit.
  restore_params={'stream_'+key:value for key,value in configured_before.items()}
  candidate=dict(restore_params,stream_videoKbps='700',stream_resolution='480')
  if profile_encoder=='qsv':candidate.update(stream_encoder='qsv',stream_allowFallback='true')
  # Save only the disposable UI's next-generation configuration. The single
  # existing public DVD Seek below asks stock Core to own the actual FLUSH/
  # NAV source reconstruction, rather than guessing ordinary-file byte input.
  if not production_apply:
   configuration_intent=True;report['stage']='save-next-generation-profile'
   saved=api('streamSettings',applyNow='false',**candidate)
   if saved.get('session')!=old_producer:raise RuntimeError('Saving future DVD configuration replaced current playback')
   report['rows'].append(dict(gate='saved-next-generation-profile-leaves-current-producer',passed=True))
 page.evaluate('()=>{DVD_CLOCK.source=videoPlane.currentSrc;DVD_CLOCK.frames=0;DVD_CLOCK.last=0}')
 if paused_probe:
  if not mcp('media.control',context=identity,operation='pause').get('accepted'):raise RuntimeError('One Pause rejected; no replay')
  wait(lambda:video()['paused'],'native pause')
 seek_target=state().get('rawMediaTimeMs') if current_position else 20000
 if not isinstance(seek_target,int) or seek_target<0:raise RuntimeError('Unknown native title clock')
 report['seekTargetMs']=seek_target;report['samePositionProbe']=current_position;report['pausedProbe']=paused_probe
 if production_apply:
  report['applySubmitted']=True;report['stage']='one-production-native-DVD-apply';configuration_intent=True
  # Deliberately wrong browser-relative time must not override the public
  # native title clock. This is the actual production servlet, not MCP Seek.
  applied=api('streamSettings',applyNow='true',expectedHlsSession=old_producer,timeMs='1',**candidate)
  if applied.get('stale') or applied.get('configured',{}).get('videoKbps')!='700':raise RuntimeError('One production Apply rejected/unknown; no replay')
 else:
  report['seekSubmitted']=True;report['stage']='one-public-native-DVD-seek'
  if not mcp('media.seek',context=identity,target_ms=seek_target).get('accepted'):raise RuntimeError('One Seek rejected/unknown; no replay')
 if paused_probe:
  # Stock correctly withholds DVD Push/FLUSH processing while paused. Verify
  # it stays paused, then require the new generation/pictures after one Play.
  before_pause=video();page.wait_for_timeout(2000);after_pause=video()
  if not before_pause['paused'] or not after_pause['paused'] or abs(after_pause['time']-before_pause['time'])>.15:
   raise RuntimeError('Stock DVD Seek did not preserve pause intent')
  report['rows'].append(dict(gate='same-position-profile-recreation-retains-native-pause',passed=True))
  if not mcp('media.control',context=identity,operation='play').get('accepted'):raise RuntimeError('One Play rejected; no replay')
 wait(lambda:video()['newSource'] and video()['frames']>=15 and video()['time']>.5 and not video()['paused'],'new decoded seek output',60)
 # Outlast Core's temporary seek guess; old anchors must not look correct only
 # during command acknowledgement. Observe pictures for at least eight seconds.
 began=time.monotonic();first=None
 while time.monotonic()-began<14:
  v=video();n=state();row=dict(v,nativeRawMs=n.get('rawMediaTimeMs'),readerChapter=n.get('dvdChapter'),nativeMenu=n.get('dvdMenu'))
  row['differenceMs']=round(n.get('rawMediaTimeMs',-999999)-(seek_target+v['time']*1000));report['samples'].append(row)
  if v['error'] or v['blocked'] or n.get('dvdMenu'):raise RuntimeError('Seek did not retain playable feature')
  if first is None:first=row
  if time.monotonic()-began>=8 and v['last']>=first['last']+5:
   if abs(row['differenceMs'])>2000:raise RuntimeError('Settled title clock disagrees with native seek plus decoded output')
   report['rows'].append(dict(gate='settled-eight-second-seek-clock',passed=True,differenceMs=row['differenceMs']));break
  page.wait_for_timeout(350)
 else:raise RuntimeError('No sustained post-seek pictures')
 if reconfigure:
  active=api('streamSettings');requested=(active.get('active') or {}).get('requested') or {}
  target=encoder_target(active.get('session'));report['encoderObservation']=target
  if profile_encoder=='qsv' and target.get('encoder')!='h264_qsv':raise RuntimeError('Requested QSV field did not use GPU encoding')
  state_reply=C.request(cfg,'/SageTVWebPlayer/api/hls?'+urlencode(dict(session=active['session'])))
  report['producerObservation']={key:state_reply.get(key) for key in ('encoder','hardware','hardwareDecode','hardwareFilters','decodeAccelerator','fallbackStage','dvdGeneration','running','error')}
  if active.get('session')==old_producer or video()['height']<=0 or target['encodedHeight']!=480 or requested.get('videoKbps')!='700' or target['videoTarget']!='700k':
   report['reconfigureResult']=dict(height=video()['height'],requested=requested,target=target)
   raise RuntimeError('Public stock DVD Seek did not recreate converter with saved profile')
  report['rows'].append(dict(gate='public-stock-DVD-seek-recreates-converter-at-700kbps-480p',passed=True,encodedHeight=480,displayHeight=video()['height'],videoTargetKbps=700))
  restored=api('streamSettings',applyNow='false',**restore_params)
  if restored.get('configured')!=configured_before:raise RuntimeError('Disposable UI next-generation profile restoration differs')
  restore_params=None;report['configuredProfileRestored']=True
 if page.evaluate('JSON.stringify(localStorage)')!=original:raise RuntimeError('Saved ephemeral profile changed')
 if report['errors']:raise RuntimeError('Unhandled browser errors')
 report['passed']=True
except Exception as error:
 detail=str(error).splitlines()[0]
 report['failure']=dict(type=type(error).__name__,message=detail[:220] if isinstance(error,RuntimeError) or detail.startswith('Page.evaluate:') else 'Bounded observer unavailable; no replay')
 if page:
  try:
   report['lastVideo']=video()
   report['buffered']=page.evaluate('()=>Array.from({length:videoPlane.buffered.length},(_,i)=>[videoPlane.buffered.start(i),videoPlane.buffered.end(i)])')
   active=api('streamSettings');report['lastStream']=dict(session=active.get('session'),configured=active.get('configured'),active=active.get('active'))
   if active.get('session'):
    state_reply=C.request(cfg,'/SageTVWebPlayer/api/hls?'+urlencode(dict(session=active['session'])))
    report['lastProducer']={key:state_reply.get(key) for key in ('running','exitCode','encoder','error','segments','hlsSeconds','durationMs','startSeconds','endList','fallbackStage')}
  except Exception:report['failureObservationUnavailable']=True
finally:
 if owned and configuration_intent and restore_params is not None:
  try:
   restored=api('streamSettings',applyNow='false',**restore_params)
   if restored.get('configured')!=configured_before:raise RuntimeError('Restore differs')
   report['configuredProfileRestored']=True
  except Exception:report['cleanup'].append('Disposable UI configuration restoration unknown')
 if page:
  try:page.screenshot(path=str(out/(stamp+'-'+engine+'-dvd-clock.png')))
  except Exception:pass
 if owned:
  try:api('stop')
  except Exception:report['cleanup'].append('Stop outcome unknown; not replayed')
 if context:context.close()
 if browser:browser.close()
 if pw:pw.stop()
 end=time.monotonic()+90
 while time.monotonic()<end:
  try:
   if identity not in mcp('ui.list').get('contexts',[]):break
  except Exception:pass
  time.sleep(.3)
 else:report['cleanup'].append('Native retirement unverified')
 report['passed']=report['passed'] and not report['cleanup']
 target=out/(stamp+'-'+engine+'-dvd-clock.json');target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(passed=report['passed'],samples=len(report['samples']),failure=report.get('failure'),cleanup=report['cleanup']))+'\n'+str(target),flush=True)
raise SystemExit(0 if report['passed'] else 1)
