#!/usr/bin/env python3
"""Real stock232 DVD Time Scroll transport, not native trick-video/phone proof.

Optional same-origin source routes qualify a candidate only; installed-byte
acceptance must run again without that explicit switch. No MCP Seek/Play/Stop
or optional companion setup: production Watch/fullscreen/keys own playback.
"""
import argparse,hashlib,importlib.util,json,time,zipfile
from pathlib import Path
from urllib.parse import parse_qs,urlencode,urlsplit
from playwright.sync_api import sync_playwright
from playback_activity import observe_idle_phone_field
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
clock_spec=importlib.util.spec_from_file_location('dvd_clock',ROOT/'scripts/dvd-field-clock.py')
Clock=importlib.util.module_from_spec(clock_spec);clock_spec.loader.exec_module(Clock)
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--engine',choices=('chromium','webkit'),required=True)
p.add_argument('--source-candidate',action='store_true');p.add_argument('--encoder',choices=('qsv','software'),default='qsv')
p.add_argument('--stv',choices=('sagemc','stock'),default='sagemc')
p.add_argument('--task',choices=('WEB-113','WEB-114','WEB-115','WEB-116','WEB-117'),default='WEB-113')
p.add_argument('--chapter-only',action='store_true',help='Observe one chapter replacement, no transport search')
p.add_argument('--chapter-transitions',type=int,choices=range(1,9),default=1,help='Bounded normal chapter source replacements, reader chapter is not a presentation oracle')
p.add_argument('--segment-delay-ms',type=int,choices=(0,150,500),default=0,help='Synthetic start delay only for this isolated browser context segment requests; not WAN acceptance')
p.add_argument('--diagnostic-self-test',action='store_true',help='Intentional post-chapter harness failure to verify normal diagnostic export, not a playback failure')
p.add_argument('--diagnostic-probe',action='store_true',help='Read-only Chromium debugger observation; never performance acceptance')
p.add_argument('--allow-idle-phone',action='store_true',help='Preserve only the exact commissioned phone after independent unloaded-state proof; not restart authority')
args=p.parse_args()
if args.diagnostic_probe and args.engine!='chromium':p.error('Diagnostic probe requires Chromium')
if args.diagnostic_self_test and not args.chapter_only:p.error('Diagnostic self-test requires chapter-only scope')
if args.chapter_transitions>1 and not args.chapter_only:p.error('Multiple chapter transitions require chapter-only scope')
identity='da92a86446be';owned=page=context=browser=pw=None;activated=False;borrowed_stock=False
out=ROOT/'artifacts/active'/args.task;out.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
report=dict(passed=False,realStock232=True,physicalPhone=False,nativeTrickVideo=False,sourceOverride=args.source_candidate,
            engine=args.engine,stv=args.stv,requestedEncoder=args.encoder,diagnosticProbe=args.diagnostic_probe,chapterOnly=args.chapter_only,chapterTransitions=args.chapter_transitions,segmentDelayMs=args.segment_delay_ms,diagnosticSelfTest=args.diagnostic_self_test,commands=[],rows=[],cleanup=[],errors=[])
class ChapterComplete(Exception):pass
report_path=out/(stamp+'-'+args.engine+'-search.json')
if report_path.exists():raise RuntimeError('Refuse field report overwrite')
def checkpoint(stage):
 report['stage']=stage;report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(stage,flush=True)

def mcp(action,**values):return C.request(cfg,'/v1/control',dict(action=action,**values),mcp=True,timeout=20)
def api(action,**values):
 params=dict(action=action,session=owned,**values)
 if action in ('status','streamSettings','contentState'):return C.request(cfg,'/SageTVWebPlayer/api/miniclient?'+urlencode(params))
 return C.request(cfg,'/SageTVWebPlayer/api/miniclient',params)
def state():
 result=mcp('ui.state',context=identity)
 if not result.get('dvd') or (result.get('media') or {}).get('mediaFileId')!=20819:raise RuntimeError('Canonical DVD owner changed')
 return result
def observed(response):
 global owned
 if '/api/miniclient' not in response.url:return
 try:
  value=response.json()
  if value.get('session') and value.get('clientId','').replace(':','').lower()==identity:owned=value['session']
  values=parse_qs(urlsplit(response.url).query)
  values.update(parse_qs(response.request.post_data or ''))
  if values.get('action')==['command']:
   report['commands'].append(dict(command=int(values['command'][0]),ok=value.get('ok')))
   checkpoint('native-command-'+values['command'][0])
  if values.get('action')==['state'] and isinstance(value.get('dvdMenu'),bool):
   report['lastNativeMenu']=dict(value=value['dvdMenu'],at=time.monotonic(),producer=values.get('expectedHlsSession',[''])[0])
 except Exception:pass
def sample():return page.evaluate('''()=>({time:videoPlane.currentTime,frames:DVD_SEARCH.frames,
  source:videoPlane.currentSrc,current:DVD_SEARCH.source===videoPlane.currentSrc,frameTime:DVD_SEARCH.frameTime,
  paused:videoPlane.paused,ready:videoPlane.readyState,width:videoPlane.videoWidth,
  ended:videoPlane.ended,seeking:videoPlane.seeking,network:videoPlane.networkState,
  buffered:Array.from({length:videoPlane.buffered.length},(_,n)=>[videoPlane.buffered.start(n),videoPlane.buffered.end(n)]),
  quality:videoPlane.getVideoPlaybackQuality?{total:videoPlane.getVideoPlaybackQuality().totalVideoFrames,dropped:videoPlane.getVideoPlaybackQuality().droppedVideoFrames}:null,
  events:DVD_SEARCH.events.slice(-40),error:videoPlane.error?.code||null,message:osdMessage.textContent})''')
def wait(check,label,seconds=40):
 global activated
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  page.wait_for_timeout(150)
  if check():return
  if page.locator('#autoplayBtn').is_visible() and not activated:
   activated=True;page.locator('#autoplayBtn').click()
 raise RuntimeError('Timed out '+label+'; no ordered input replay')
def fresh_feature():
 observed=report.get('lastNativeMenu',{})
 return observed.get('value') is False and time.monotonic()-observed.get('at',0)<1.1
def settled_title_clock(producer):
 # Core's displayed clock can still contain the previous epoch's cached poll
 # at the very first new picture. Observe a current-producer report and an
 # actual advancing paired clock interval; never alter/replay a chapter key.
 wait(lambda:fresh_feature() and report['lastNativeMenu'].get('producer')==producer,'current producer native state')
 baseline=dict(video=sample(),native=state(),wall=time.monotonic());end=time.monotonic()+15
 while time.monotonic()<end:
  page.wait_for_timeout(200);now=dict(video=sample(),native=state(),wall=time.monotonic())
  if now['video']['source']!=baseline['video']['source']:raise RuntimeError('Chapter source superseded during clock observation')
  elapsed=now['wall']-baseline['wall'];dv=now['video']['frameTime']-baseline['video']['frameTime'];dn=(now['native']['rawMediaTimeMs']-baseline['native']['rawMediaTimeMs'])/1000
  if dn<0 or dv<0:baseline=now;continue
  if elapsed>=1.5 and dv>=.5 and dn>=.5 and abs(dv-dn)<1:
   return dict(before=baseline,after=now)
  if elapsed>4:baseline=now
 raise RuntimeError('Current chapter picture/native clocks did not settle')
def commands(mark):return [v['command'] for v in report['commands'][mark:]]
def tap(selector):
 if args.task=='WEB-117' and selector in ('#nav_media_skip_forward','#nav_media_skip_back','#nav_select','#nav_media_play'):
  page.locator(selector).focus();page.keyboard.press('Enter')
 else:page.locator(selector).click()
 page.wait_for_timeout(120)
def restore_stv():
 global borrowed_stock
 if not borrowed_stock:return
 if not api('command',command=28).get('ok'):raise RuntimeError('Original STV restore intent rejected')
 wait(lambda:mcp('captions.get',context=identity).get('stvFile','').endswith('/SageMC_Vibe.xml'),'original SageMC restoration',20)
 borrowed_stock=False;report['rows'].append(dict(gate='original-SageMC-restored',passed=True))

try:
 checkpoint('independent-preflight')
 report['preflight']=observe_idle_phone_field(C.activity(cfg),mcp('ui.list').get('contexts'),
   lambda name:mcp('ui.state',context=name),args.allow_idle_phone)
 pw=sync_playwright().start();browser=getattr(pw,args.engine).launch(headless=True,**(dict(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox']) if args.engine=='chromium' else {}))
 context=browser.new_context(viewport=dict(width=1280,height=800),service_workers='block',http_credentials=dict(username=cfg['web_username'],password=cfg['web_password']))
 profile=dict(player='hls',videoMode='transcode',encoder=args.encoder,videoKbps=1200,resolution='480',allowFallback=args.encoder=='qsv',companionDvd=False)
 context.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebStreaming.v1',"+json.dumps(json.dumps(profile))+");")
 if args.segment_delay_ms:
  def delay_segment(route,request):
   # An ephemeral browser context created above owns every request. Never
   # change a server proxy/interface, another client or unrelated URL.
   if request.method=='GET' and urlsplit(request.url).path.endswith('.ts'):
    time.sleep(args.segment_delay_ms/1000);report['delayedSegmentRequests']=report.get('delayedSegmentRequests',0)+1
   route.continue_()
  context.route(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/hls/*/*.ts*',delay_segment)
 if args.source_candidate:
  for filename in ('miniclient-input.js','miniclient.js','miniclient-playback.js'):
   source=ROOT/'src/main/webapp/js'/filename
   report.setdefault('candidateSha256',{})[filename]=hashlib.sha256(source.read_bytes()).hexdigest()
   context.route(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/js/'+filename+'*',lambda route,request,source=source:route.fulfill(path=str(source),content_type='application/javascript'))
 page=context.new_page();page.on('response',observed);page.on('pageerror',lambda error:report['errors'].append(str(error)))
 page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html'+('?ui=1280x720' if args.stv=='stock' else ''),wait_until='domcontentloaded')
 if args.diagnostic_probe:
  probe=context.new_cdp_session(page);probe.send('Debugger.enable')
  def paused(event):
   try:
    result=probe.send('Debugger.evaluateOnCallFrame',dict(callFrameId=event['callFrames'][0]['callFrameId'],expression="JSON.stringify({command,context:inputContext(),suspended:videoPresentationSuspended,presentation:videoPresentation.kind,dvd:playback.dvd,hasPlayback:!!playback.id,menuHint:currentMenuHint,dvdMenuState,stateAge:Date.now()-dvdMenuStateAt,settingsHidden:settingsPanel.hidden,scrolling:dvdKeys.scrolling})",returnByValue=True))
    value=result.get('result',{}).get('value');report.setdefault('diagnosticInput',[]).append(json.loads(value) if value else result)
    checkpoint('diagnostic-input-context')
    if len(report['diagnosticInput'])>=4:probe.send('Debugger.setSkipAllPauses',dict(skip=True))
   finally:probe.send('Debugger.resume')
  probe.on('Debugger.paused',paused)
  source=(ROOT/'src/main/webapp/js/miniclient.js').read_text(encoding='utf-8').splitlines()
  line=next(n for n,v in enumerate(source) if 'const dvdFeature=!calibrationOwner' in v)
  probe.send('Debugger.setBreakpointByUrl',dict(lineNumber=line,urlRegex=r'/js/miniclient\.js(?:\?|$)'))
 checkpoint('page-loaded')
 wait(lambda:owned and api('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'),'owned UI')
 saved=page.evaluate('JSON.stringify(localStorage)');configured=api('streamSettings')['configured']
 if args.stv=='stock':
  if not mcp('captions.get',context=identity).get('stvFile','').endswith('/SageMC_Vibe.xml'):raise RuntimeError('Preserve unexpected original STV')
  borrowed_stock=True
  if not api('command',command=28).get('ok'):raise RuntimeError('One Home setup rejected')
  page.wait_for_timeout(700)
  # Existing qualified SageMC DEFAULT-STV route, exact disposable UI only.
  # No server properties/STV files or another client's setup is changed.
  for x,y in ((740,543),(750,542),(158,317)):
   box=page.locator('#gfxCanvas').bounding_box()
   page.locator('#gfxCanvas').click(position=dict(x=x*box['width']/1280,y=y*box['height']/720))
   page.wait_for_timeout(1000)
  wait(lambda:mcp('captions.get',context=identity).get('stvFile','').endswith('/SageTV7.xml'),'default stock STV',20)
  # File identity can change before the new STV's initialization/render.
  # Waiting for its actual default-theme gray navigation rail avoids Watch
  # interrupting LoadSTVFile while the old SageMC/black transition is active.
  # This is a fixed test-theme witness, not production pixel navigation.
  wait(lambda:page.locator('#gfxCanvas').evaluate('''c=>{const x=c.getContext('2d');return [120,220,320].every(y=>{const p=x.getImageData(10,y,1,1).data;return p[0]>20&&p[0]<160&&Math.abs(p[0]-p[1])<10&&Math.abs(p[1]-p[2])<10})}'''),'actual stock Main Menu raster',20)
  report['stockMainMenuRasterObserved']=True
  checkpoint('stock-SageTV7-qualified')
 page.evaluate("()=>{const s=window.DVD_SEARCH={frames:0,source:'',frameTime:0,events:[]};for(const name of ['loadstart','loadedmetadata','loadeddata','canplay','playing','waiting','stalled','pause','seeking','seeked','ended','error'])videoPlane.addEventListener(name,()=>{s.events.push({event:name,at:performance.now(),source:videoPlane.currentSrc,time:videoPlane.currentTime,ready:videoPlane.readyState});if(s.events.length>100)s.events.shift()});const f=()=>{const source=videoPlane.currentSrc;videoPlane.requestVideoFrameCallback((_,metadata)=>{if(source&&source===videoPlane.currentSrc){s.frames++;s.source=source;s.frameTime=metadata.mediaTime}f()})};f()}")
 if not api('watchContent',mediaId=20819).get('accepted'):raise RuntimeError('One production Watch rejected')
 checkpoint('production-watch-submitted')
 wait(lambda:api('contentState',mediaId=20819).get('ready'),'loaded source')
 content=api('contentState',mediaId=20819)
 report['contentStateBeforeFullscreen']=content
 checkpoint('native-layout-observed')
 if content.get('layout')=='preview':
  if not api('showContent',mediaId=20819).get('ok'):raise RuntimeError('One fullscreen request rejected')
 elif content.get('layout')!='fullscreen':raise RuntimeError('Unknown native layout')
 wait(lambda:sample()['width']>0 and isinstance(state().get('dvdMenu'),bool),'decoded source')
 if not state().get('dvdMenu'):
  # Stock legitimately resumes its generated fixture. Exercise the authored
  # root once instead of clearing saved/watch metadata or seeking through MCP.
  if not api('command',command=67).get('ok'):raise RuntimeError('One authored Root request rejected')
  wait(lambda:state().get('dvdMenu') is True,'authored root before fresh feature')
  checkpoint('authored-root-for-fresh-fixture')
 if state().get('dvdMenu'):
  wait(lambda:report.get('lastNativeMenu',{}).get('value') is True,'browser receives authored menu state')
  page.locator('#stage').focus();page.keyboard.press('Enter')
 wait(lambda:fresh_feature() and sample()['current'] and sample()['frames']>20 and sample()['time']>1 and not sample()['paused'],'moving feature',60)
 checkpoint('moving-feature')
 # SageMC's default Time Scroll step is150s, longer than this90s fixture.
 # Start in its second chapter, exercise forward bounds/repeat then rewind
 # before committing, instead of declaring legitimate EOF->menu a failure.
 for transition in range(args.chapter_transitions):
  before_chapter=sample();native_before=state()
  chapter_command=Clock.fixture_replacement_command(native_before) if args.chapter_only else 65
  if chapter_command is None:raise RuntimeError('Preserve unexpected fixture title/menu/chapter')
  report['chapterBefore']=dict(video=before_chapter,native=native_before,producer=api('streamSettings').get('session'),transition=transition+1,command=chapter_command)
  checkpoint('before-one-native-chapter-'+str(transition+1))
  if not api('command',command=chapter_command).get('ok'):raise RuntimeError('One production chapter intent rejected')
  wait(lambda:sample()['source']!=before_chapter['source'] and sample()['current'] and sample()['frames']>before_chapter['frames']+15 and not sample()['paused'] and state().get('dvdMenu') is False,'chapter replacement '+str(transition+1),60)
  wait(fresh_feature,'fresh chapter feature');checkpoint('native-chapter-presented-'+str(transition+1))
  if args.chapter_only:
   report['settledClock']=settled_title_clock(api('streamSettings')['session'])
   chapter_after=sample();native_after=state();page.wait_for_timeout(4000);later=sample();native_later=state()
   report['holdWitness']=dict(beforeVideo=chapter_after,beforeNative=native_after,afterVideo=later,afterNative=native_later)
   checkpoint('chapter-clock-hold-observed-'+str(transition+1))
   if not later['current'] or later['source']!=chapter_after['source'] or later['time']<chapter_after['time']+2 or later['frames']<chapter_after['frames']+40 or later['paused'] or later['error']:raise RuntimeError('Chapter replacement did not sustain moving pictures')
   if native_later['rawMediaTimeMs']<native_after['rawMediaTimeMs']+2000:raise RuntimeError('Native title clock did not advance with chapter pictures')
   report['rows'].append(dict(gate='one-native-chapter-new-source-sustained-pictures',transition=transition+1,command=chapter_command,after=chapter_after,later=later,nativeBeforeHold=native_after,native=native_later,readerChapterIsPresentedOracle=False))
   checkpoint('native-chapter-sustained-'+str(transition+1))
 if args.chapter_only:
  producer_state=C.request(cfg,'/SageTVWebPlayer/api/hls?'+urlencode(dict(session=api('streamSettings')['session'])))
  report['actualProducer']={key:producer_state.get(key) for key in ('encoder','hardware','hardwareDecode','hardwareFilters','fallbackStage','running','dvdGeneration')}
  if args.encoder=='qsv' and (producer_state.get('encoder')!='h264_qsv' or producer_state.get('hardware') is not True):raise RuntimeError('Requested GPU encoding is not active')
  if page.evaluate('JSON.stringify(localStorage)')!=saved or api('streamSettings')['configured']!=configured:raise RuntimeError('Disposable profile changed')
  if report['errors']:raise RuntimeError('Unhandled browser errors')
  if args.diagnostic_self_test:raise RuntimeError('Intentional diagnostic harness self-test after successful chapter')
  report['passed']=True;raise ChapterComplete()
 before=sample();native_before=state();producer=api('streamSettings')['session'];mark=len(report['commands'])
 tap('#remoteToggle');tap('#nav_media_skip_forward');tap('#nav_media_skip_forward');tap('#nav_media_skip_back');checkpoint('forward-bound-repeat-and-rewind-intents')
 wait(lambda:commands(mark)==[7,10,8,8,9],'one arm/two forward/one reverse moves')
 if api('streamSettings')['session']!=producer or sample()['source']!=before['source']:raise RuntimeError('Search rebuilt the video before acceptance')
 report['rows'].append(dict(gate='native-search-three-moves-no-converter-restart',commands=commands(mark),beforeRawMs=native_before['rawMediaTimeMs']))
 tap('#nav_select');wait(lambda:commands(mark)==[7,10,8,8,9,10],'single native accept')
 wait(lambda:sample()['source']!=before['source'] and sample()['current'] and sample()['frames']>before['frames']+15 and not sample()['paused'],'new accepted DVD pictures',60)
 after=sample();native_after=state()
 producer_state=C.request(cfg,'/SageTVWebPlayer/api/hls?'+urlencode(dict(session=api('streamSettings')['session'])))
 report['actualProducer']={key:producer_state.get(key) for key in ('encoder','hardware','hardwareDecode','hardwareFilters','fallbackStage','running','dvdGeneration')}
 if args.encoder=='qsv' and (producer_state.get('encoder')!='h264_qsv' or producer_state.get('hardware') is not True):raise RuntimeError('Requested GPU encoding is not active')
 if abs(native_after['rawMediaTimeMs']-native_before['rawMediaTimeMs'])<5000:raise RuntimeError('Accepted search did not move the actual title clock')
 report['rows'].append(dict(gate='accept-new-picture-and-native-title-change',before=native_before['rawMediaTimeMs'],after=native_after['rawMediaTimeMs'],sample=after,approximateDvdLanding=True))
 # Forward end selection then Play cancellation must retain the producer.
 wait(fresh_feature,'fresh accepted feature');producer=api('streamSettings')['session'];before=sample();mark=len(report['commands'])
 tap('#nav_media_skip_forward');wait(lambda:commands(mark)==[7,10,8],'one forward search')
 tap('#nav_media_play');wait(lambda:commands(mark)==[7,10,8,7],'one Play cancellation')
 wait(lambda:sample()['frames']>before['frames']+20 and not sample()['paused'],'cancelled search still presents pictures')
 if api('streamSettings')['session']!=producer:raise RuntimeError('Cancelled search rebuilt video')
 report['rows'].append(dict(gate='forward-end-selection-Play-cancel-preserves-producer',sample=sample()))
 if page.evaluate('JSON.stringify(localStorage)')!=saved or api('streamSettings')['configured']!=configured:raise RuntimeError('Disposable profile changed')
 if report['errors']:raise RuntimeError('Unhandled browser errors')
 report['passed']=True
except ChapterComplete:pass
except Exception as error:
 report['failure']=dict(type=type(error).__name__,message=str(error).splitlines()[0][:240])
 if page:
  try:report['last']=sample();page.screenshot(path=str(out/(stamp+'-'+args.engine+'-search-failure.png')))
  except Exception:pass
 if owned:
  try:
   report['native']=state();report['server']=api('streamSettings')
   producer_id=report['server'].get('session')
   if producer_id:report['failureProducer']=C.request(cfg,'/SageTVWebPlayer/api/hls?'+urlencode(dict(session=producer_id)))
  except Exception:report['failureObservationUnavailable']=True
  try:report['failureThreads']=mcp('diagnostics.threads')
  except Exception:report['failureThreadsUnavailable']=True
 if page:
  try:
   def diagnostic(request):
    if '/api/support' in request.url and request.post_data:
     values=parse_qs(request.post_data)
     if values.get('browserJson'):report['failureBrowser']=json.loads(values['browserJson'][0])
   page.on('request',diagnostic)
   if page.locator('#settingsPanel').is_hidden():page.locator('#settingsToggle').click()
   page.locator('#settings-tab-diagnostics').click()
   if not page.locator('#downloadReport').is_visible():page.locator('#supportPreferences summary').click()
   if page.locator('#saveDiagnosticsToServer').is_checked():raise RuntimeError('Refuse diagnostic server write')
   with page.expect_download(timeout=25000) as pending:page.locator('#downloadReport').click()
   pending.value.save_as(str(out/(stamp+'-'+args.engine+'-failure-diagnostics.zip')))
   if args.task=='WEB-116':
    with zipfile.ZipFile(out/(stamp+'-'+args.engine+'-failure-diagnostics.zip')) as bundle:
     encoded=bundle.read('report.json');exported=json.loads(encoded)
     if hashlib.sha256(encoded).hexdigest()+'  report.json' not in bundle.read('hashes.sha256').decode():raise RuntimeError('Diagnostic ZIP hash mismatch')
    e=exported['browser']['playback']['element']
    if not(e['available'] and e['readyState']>=2 and e['networkState']>=0 and e['videoWidth']>0 and e['paused'] is False and e['buffered']['available'] and e['buffered']['ranges'] and len(e['buffered']['ranges'])<=16):raise RuntimeError('Normal exported video element evidence unavailable')
    if any(k in e for k in ('src','currentSrc','url','mediaUrl')):raise RuntimeError('Media URL must not appear in element diagnostics')
    report['normalVideoDiagnosticExportVerified']=dict(readyState=e['readyState'],networkState=e['networkState'],paused=e['paused'],bufferRanges=len(e['buffered']['ranges']),quality=e['quality'],hashVerified=True)
  except Exception as observation:report['diagnosticDownloadUnavailable']=str(observation).splitlines()[0][:180]
finally:
 if owned:
  try:restore_stv()
  except Exception:report['cleanup'].append('Original SageMC STV restoration unknown')
  try:api('stop')
  except Exception:report['cleanup'].append('Stop receipt unknown; no replay')
 if context:context.close()
 if browser:browser.close()
 if pw:pw.stop()
 end=time.monotonic()+90
 while time.monotonic()<end:
  try:
   if identity not in mcp('ui.list').get('contexts',[]):break
  except Exception:pass
  time.sleep(.3)
 else:report['cleanup'].append('Independent native retirement unavailable')
 report['passed']=report['passed'] and not report['cleanup']
 if args.diagnostic_self_test:
  report['diagnosticSelfTestPassed']=bool(report.get('failure',{}).get('message')=='Intentional diagnostic harness self-test after successful chapter' and report.get('failureBrowser') and report.get('failureProducer') and (out/(stamp+'-'+args.engine+'-failure-diagnostics.zip')).is_file() and not report['cleanup'] and (args.task!='WEB-116' or report.get('normalVideoDiagnosticExportVerified')))
 report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(passed=report['passed'],engine=args.engine,sourceCandidate=args.source_candidate,rows=len(report['rows']),failure=report.get('failure'),diagnosticSelfTestPassed=report.get('diagnosticSelfTestPassed'),cleanup=report['cleanup'])),flush=True)
raise SystemExit(0 if report['passed'] or report.get('diagnosticSelfTestPassed') else 1)
