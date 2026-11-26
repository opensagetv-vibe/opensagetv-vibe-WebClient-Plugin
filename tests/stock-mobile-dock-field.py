#!/usr/bin/env python3
"""WEB-074 real stock232 lists -> exact STV Watch -> presented video. No iPhone claim."""
import importlib.util,json,os,time
from pathlib import Path
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
engine=os.environ.get('SAGETV_BROWSER_ENGINE','chromium');identity='da92a86446be'
stock_info=os.environ.get('SAGETV_INFO_STV')=='stock'
guide_only=os.environ.get('SAGETV_GUIDE_ONLY')=='1'
if engine not in ('chromium','webkit'):raise ValueError('Unsupported engine')
OUT=Path(os.environ.get('SAGETV_ARTIFACT_DIR',ROOT/'artifacts/active/WEB-079')).resolve()
if not OUT.is_relative_to((ROOT/'artifacts/active').resolve()):raise RuntimeError('Task-owned output required')
OUT.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());owned=None;page=None;context=None;browser=None;pw=None;rows=[];errors=[];cleanup=[];passed=False;failure=None;phase='independent-idle'
def mcp(action,**values):return C.request(cfg,'/v1/control',dict(action=action,**values),mcp=True)
def mini(action):return C.request(cfg,'/SageTVWebPlayer/api/miniclient?'+urlencode(dict(action=action,session=owned)))
def observe(response):
 global owned
 if '/api/miniclient' not in response.url or response.request.method!='POST':return
 try:
  data=response.json()
  if data.get('session') and data.get('clientId','').replace(':','').lower()==identity:owned=data['session']
 except Exception:pass
def wait(predicate,label,seconds=45):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  if predicate():return
  page.wait_for_timeout(150)
 raise RuntimeError('Timed out: '+label)
def state():return page.evaluate('()=>({frames:DOCK_FIELD.frames,time:videoPlane.currentTime,paused:videoPlane.paused,width:videoPlane.videoWidth,error:videoPlane.error?.code,prompt:!autoplayBtn.hidden})')
def moving():
 before=state();clicked=False;end=time.monotonic()+60
 while time.monotonic()<end:
  actual=state()
  if actual['error']:raise RuntimeError('Media decode error')
  if actual['prompt'] and not clicked:page.locator('#autoplayBtn').click();clicked=True
  if not actual['paused'] and actual['width'] and actual['frames']>before['frames']+8:return actual
  page.wait_for_timeout(150)
 raise RuntimeError('No new presented pictures')
try:
 activity=C.activity(cfg)
 if activity.get('recordingCount')!=0 or activity.get('connectedClientCount')!=0 or mcp('ui.list').get('contexts'):raise RuntimeError('Stock server is not independently idle')
 # Only select a pre-existing canonical generated fixture; never import files,
 # allocate a tuner, reset metadata or start media using MCP.
 fixture=mcp('media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/VibeCaptionTest-1080i-CEA608-90s-2s.ts')
 if fixture.get('mediaFileId')!=20905:raise RuntimeError('Canonical fixture changed')
 pw=sync_playwright().start();kwargs={'headless':True}
 if engine=='chromium':kwargs.update(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
 browser=getattr(pw,engine).launch(**kwargs)
 context=browser.new_context(viewport={'width':393,'height':852},device_scale_factor=3,has_touch=True,service_workers='block',http_credentials={'username':cfg['web_username'],'password':cfg['web_password']})
 context.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify({player:'hls',videoMode:'transcode',encoder:'qsv',videoKbps:1000,resolution:'480',deinterlace:'on',allowFallback:false}));")
 page=context.new_page();page.on('response',observe);page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
 wait(lambda:owned is not None and mini('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'),'native first frame')
 if stock_info:
  if not mcp('captions.get',context=identity).get('stvFile','').endswith('/SageMC_Vibe.xml'):raise RuntimeError('Unexpected initial STV')
  page.set_viewport_size({'width':1280,'height':800})
  for x,y in ((740,543),(750,542),(158,317)):
   page.locator('#gfxCanvas').click(position={'x':x,'y':y});page.wait_for_timeout(1000)
  wait(lambda:mcp('captions.get',context=identity).get('stvFile','').endswith('/SageTV7.xml'),'qualified stock STV route',20)
  page.wait_for_timeout(1500);page.set_viewport_size({'width':393,'height':852})
  page.wait_for_timeout(400)
 page.locator('#mobileTab-controls').click()
 page.locator('#keyboardToggle').click()
 if page.locator('#keyboardPanel').is_hidden():raise RuntimeError('Portrait Keyboard did not open')
 page.locator('#mobileTab-recordings').click()
 if not page.locator('#keyboardPanel').is_hidden():raise RuntimeError('Hidden drawer retained ownership')
 page.locator('#mobileTab-controls').click()
 page.screenshot(path=str(OUT/(stamp+'-'+engine+'-stock-controls.png')))
 rows.append(dict(gate='actual-portrait-drawer-tab-retirement',passed=True))
 original=page.evaluate('JSON.stringify(localStorage)');configured=mini('streamSettings').get('configured')
 page.evaluate('()=>{window.DOCK_FIELD={frames:0};function next(){DOCK_FIELD.frames++;videoPlane.requestVideoFrameCallback(next)};videoPlane.requestVideoFrameCallback(next)}')
 for key in (('guide',) if guide_only else ('recordings','guide','videos')):
  phase='list-'+key
  page.locator('#mobileTab-'+key).click()
  wait(lambda:'Loading' not in page.locator('.mc-mobile-list-status').inner_text(),'list '+key)
  if 'Unable' in page.locator('.mc-mobile-list-status').inner_text():raise RuntimeError('List failed: '+key)
  rows.append(dict(gate='real-'+key+'-list',count=page.locator('.mc-mobile-program' if key=='guide' else '.mc-mobile-folder,.mc-mobile-item').count(),passed=True));print('PASS '+rows[-1]['gate'],flush=True)
  if key=='guide':
   wait(lambda:page.locator('.mc-mobile-channel img').evaluate_all('a=>a.some(i=>i.complete&&i.naturalWidth>0)'),'real channel logo bytes',20)
   rows.append(dict(gate='real-guide-channel-logo-decoded',count=page.locator('.mc-mobile-channel img').count(),passed=True))
   page.screenshot(path=str(OUT/(stamp+'-'+engine+'-real-guide.png')))
   phase='guide-program-selection'
   page.locator('.mc-mobile-program').first.click();target=page.locator('.mc-mobile-guide-details [data-content-action]').last
  elif key=='recordings':
   if page.locator('.mc-mobile-folder').count():page.locator('.mc-mobile-folder').first.click()
   target=page.locator('.mc-mobile-item [data-content-action]').first
  else:continue
  phase=key+'-Info-click-and-response'
  with page.expect_response(lambda r:'/api/miniclient' in r.url and 'infoContent' in r.url) as detail:target.click()
  if not detail.value.json().get('ok'):raise RuntimeError('Native '+key+' Info refused')
  if mcp('ui.state',context=identity).get('fullyLoaded'):raise RuntimeError('Info unexpectedly played '+key)
  page.wait_for_timeout(1400);page.screenshot(path=str(OUT/(stamp+'-'+engine+'-'+key+'-info.png')))
  rows.append(dict(gate='production-'+key+'-Info-native-menu-no-playback',passed=True))
 if not guide_only:
  # The canonical clip is a video import, not a TV recording. Filter via the
  # production search, assert the selected row's actual exact media ID on wire.
  page.locator('.mc-mobile-browse select').select_option('all')
  page.locator('.mc-mobile-search input').fill('VibeCaptionTest-1080i-CEA608-90s-2s')
  page.locator('.mc-mobile-search').evaluate('e=>e.requestSubmit()')
  wait(lambda:page.locator('.mc-mobile-item').count()>0,'canonical video result')
  with page.expect_response(lambda r:'/api/miniclient' in r.url and 'infoContent' in r.url) as info:
   page.locator('.mc-mobile-item [data-content-action]').first.click()
  if dict(__import__('urllib.parse',fromlist=['parse_qsl']).parse_qsl(info.value.request.post_data)).get('mediaId')!='20905':raise RuntimeError('Info selected wrong content')
  if not info.value.json().get('ok'):raise RuntimeError('STV Info refused')
  page.wait_for_timeout(1800)
  if mcp('ui.state',context=identity).get('fullyLoaded'):raise RuntimeError('Info unexpectedly started playback')
  page.screenshot(path=str(OUT/(stamp+'-'+engine+'-stock-info.png')))
  rows.append(dict(gate='production-Info-native-menu-no-playback',passed=True))
  C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action='command',session=owned,command=28))
  with page.expect_response(lambda r:'/api/miniclient' in r.url and 'watchContent' in r.url) as response:
   page.locator('.mc-mobile-item [data-content-play]').first.click()
  request=response.value.request
  params=dict(__import__('urllib.parse',fromlist=['parse_qsl']).parse_qsl(request.post_data))
  if params.get('mediaId')!='20905' or params.get('session')!=owned:raise RuntimeError('Wrong Watch owner/content')
  if not response.value.json().get('accepted'):raise RuntimeError('Watch refused: '+str(response.value.json().get('error','Unknown result'))[:120])
  def layout():return C.request(cfg,'/SageTVWebPlayer/api/miniclient?'+urlencode(dict(action='contentState',session=owned,mediaId=20905)))
  wait(lambda:layout().get('ready') and layout().get('layout')=='fullscreen','exact selected content native fullscreen',30)
  rows.append(dict(gate='production-Play-native-fullscreen-not-preview',passed=True))
  picture=moving();rows.append(dict(gate='production-Play-exact-STV-presented-video',passed=True,frames=picture['frames'],width=picture['width']));print('PASS new presented video after exact-STV Play',flush=True)
  for width,height in ((852,393),(393,852)):
   page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(500);picture=moving()
   if height>width:
    stage=page.locator('#stage').bounding_box()
    if abs(stage['width']/stage['height']-16/9)>.02:raise RuntimeError('Portrait aspect changed')
   rows.append(dict(gate='active-video-rotation',width=width,height=height,presentedFrames=picture['frames'],passed=True))
 if page.evaluate('JSON.stringify(localStorage)')!=original or mini('streamSettings').get('configured')!=configured:raise RuntimeError('Saved profiles changed')
 if errors:raise RuntimeError('Browser errors')
 page.screenshot(path=str(OUT/(stamp+'-'+engine+'-stock-portrait.png')))
 passed=True
except Exception as error:
 failure={'type':type(error).__name__,'phase':phase,'message':str(error)[:250] if isinstance(error,RuntimeError) else 'Field assertion failed'}
 if page:
  try:
   failure['mobileState']=page.evaluate('()=>({detailsHidden:document.querySelector(".mc-mobile-guide-details")?.hidden,selectedPrograms:document.querySelectorAll(".mc-mobile-program[aria-pressed=true]").length,detailsActions:[...document.querySelectorAll(".mc-mobile-guide-details [data-content-action]")].map(b=>({disabled:b.disabled,hidden:b.hidden,rect:{x:b.getBoundingClientRect().x,y:b.getBoundingClientRect().y,w:b.clientWidth,h:b.clientHeight}}))})')
   page.screenshot(path=str(OUT/(stamp+'-'+engine+'-failure.png')))
  except Exception:failure['snapshotUnavailable']=True
finally:
 if owned:
  try:
   if stock_info and mcp('captions.get',context=identity).get('stvFile','').endswith('/SageTV7.xml'):
    C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action='command',session=owned,command=28))
    wait(lambda:mcp('captions.get',context=identity).get('stvFile','').endswith('/SageMC_Vibe.xml'),'original STV restored',20)
   if not C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action='stop',session=owned)).get('ok'):cleanup.append('Stop not acknowledged')
  except Exception:cleanup.append('Stop outcome unknown; not replayed')
 if context:context.close()
 if browser:browser.close()
 if pw:pw.stop()
 end=time.monotonic()+90
 while time.monotonic()<end:
  try:
   if identity not in mcp('ui.list').get('contexts',[]):break
  except Exception:pass
  time.sleep(.3)
 else:cleanup.append('Native retirement unverified')
 report=dict(passed=passed and not cleanup,engine=engine,guideOnly=guide_only,realStock232=True,physicalIPhone=False,rows=rows,errors=errors,cleanup=cleanup,failure=failure)
 (OUT/(stamp+'-'+engine+'-stock-mobile.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(report),flush=True)
raise SystemExit(0 if passed and not cleanup else 1)
