#!/usr/bin/env python3
"""Installed settings tabs/UI (optional completed HLS), not physical iPhone proof."""
import argparse,importlib.util,json,time
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--run-stock232',action='store_true');p.add_argument('--ui-only',action='store_true');p.add_argument('--task',default='WEB-133');a=p.parse_args()
if not a.run_stock232:raise SystemExit('Explicit stock232 commissioning required')
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
identity='da92a86446be';out=ROOT/'artifacts/active'/a.task;out.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());rows=[];report={'passed':False,'rows':rows,'physicalPhone':False};owned=None
def mcp(action,**values):return C.request(cfg,'/v1/control',{'action':action,**values},mcp=True)
def observe(response):
 global owned
 if '/api/miniclient' in response.url and response.request.method=='POST':
  try:
   data=response.json()
   if data.get('session') and data.get('clientId','').replace(':','').lower()==identity:owned=data['session']
  except Exception:pass
def retire():
 global owned
 if owned:
  token=owned;owned=None
  try:C.request(cfg,'/SageTVWebPlayer/api/miniclient',{'action':'stop','session':token})
  except RuntimeError as e:
   if not str(e).startswith('HTTP 404:'):raise
 deadline=time.monotonic()+90
 while not C.activity(cfg).get('safeToRestart'):
  if time.monotonic()>deadline:raise RuntimeError('Independent owned retirement unverified')
  time.sleep(.5)
try:
 if not C.activity(cfg).get('safeToRestart'):raise RuntimeError('Preserve existing recordings/clients')
 if not a.ui_only:
  media=mcp('media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/VibeSeekTest-1080i-MPEG2-AC3-CC.ts')
  if not media.get('mediaFileId'):raise RuntimeError('Canonical completed fixture missing')
 with sync_playwright() as pw:
  for engine in ('chromium','webkit'):
   browser=getattr(pw,engine).launch(headless=True,**({'executable_path':'/usr/local/bin/vibe-chromium','args':['--no-sandbox']} if engine=='chromium' else {}))
   context=browser.new_context(viewport={'width':1280,'height':900},http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block')
   page=context.new_page();page.on('response',observe);errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
   page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify({player:'hls',videoMode:'transcode',encoder:'auto',videoKbps:2000,resolution:'480',deinterlace:'auto'}));localStorage.setItem('sagetvWebMiniClientSettings.v1',JSON.stringify({mute:true,maxBufferSeconds:30}));")
   try:
    page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html?_vibeReload=web133.1',wait_until='domcontentloaded')
    page.wait_for_function("connectionStatus.textContent.toLowerCase().startsWith('connected')",timeout=45000)
    page.wait_for_function("gfxCanvas.width>0",timeout=15000)
    page.locator('#settingsToggle').click()
    assert page.locator('#settingsCategories [role=tab]').count()==6
    page.locator('#settings-tab-diagnostics').click()
    assert page.locator('#downloadReport').is_visible()
    page.locator('#settings-tab-transcoding').click()
    assert page.locator('#automaticBitrateAdjustment').input_value()=='off'
    assert page.locator('#stream_audioCodec').is_visible()
    layout=[];preferences=page.evaluate('JSON.stringify(localStorage)')
    for width,height in ((1280,900),(393,852),(852,393),(320,568)):
     page.set_viewport_size({'width':width,'height':height})
     for key in ('app','playback','transcoding','input','diagnostics','recovery'):
      page.locator('#settings-tab-'+key).click()
      assert page.locator('#settingsTree>[role=tabpanel]:visible').count()==1
      assert page.locator('#'+page.locator('#settings-tab-'+key).get_attribute('aria-controls')).is_visible()
     assert page.locator('.mc-setting-choice').count()==0
     page.locator('#settings-tab-transcoding').click()
     assert page.locator('#saveStreaming').is_visible()
     tops=page.locator('#settingsCategories [role=tab]').evaluate_all('(tabs)=>tabs.map(t=>t.offsetTop)')
     assert len(set(tops))==1,tops
     assert page.evaluate('document.documentElement.scrollWidth')<=width+1
     page.screenshot(path=str(out/(stamp+'-'+engine+'-'+str(width)+'-installed-tabs.png')))
     layout.append({'viewport':[width,height],'singleRowTabs':True,'singlePanel':True,'duplicateValues':0})
    assert page.evaluate('JSON.stringify(localStorage)')==preferences,'Tab navigation changed saved preferences'
    page.set_viewport_size({'width':1280,'height':900})
    page.locator('#closeSettings').click()
    if a.ui_only:
     page.locator('#stage').focus();page.keyboard.press('ContextMenu')
     page.locator('#remoteStats').click();page.locator('#remoteStatsInfo').click()
     assert page.locator('#stats').is_visible() and page.locator('#statsGauges').is_visible() and page.locator('#remotePanel').is_visible()
     page.locator('#remoteStats').click();assert page.locator('#stats').is_visible() and page.locator('#statsGauges').is_hidden()
     rows.append({'engine':engine,'installedTabsAndIndependentStats':True,'layout':layout,'preferencesPreserved':True,'uiOnly':True,'errors':errors})
     assert not errors,errors
     continue
    # Exact owned public UI, never the only/first unrelated context.
    deadline=time.monotonic()+30
    while identity not in mcp('ui.list').get('contexts',[]):
     if time.monotonic()>deadline:raise RuntimeError('Exact owned UI not registered')
     page.wait_for_timeout(200)
    page.wait_for_timeout(2000)
    mcp('media.clear_watched',media_id=media['mediaFileId'],confirm='true') # generated fixture only
    if not mcp('media.watch',context=identity,media_id=media['mediaFileId'],wait_ms=0).get('ok'):raise RuntimeError('Watch refused')
    page.wait_for_function('videoPlane.videoWidth>0&&videoPlane.currentTime>1&&!videoPlane.paused',timeout=90000)
    samples=[]
    for _ in range(10):
     page.wait_for_timeout(2000)
     samples.append(page.evaluate("()=>{const v=videoPlane;let ahead=0;for(let i=0;i<v.buffered.length;i++)if(v.buffered.start(i)<=v.currentTime+.1&&v.buffered.end(i)>=v.currentTime)ahead=v.buffered.end(i)-v.currentTime;return{time:v.currentTime,ahead,frames:v.getVideoPlaybackQuality?.().totalVideoFrames??null,width:v.videoWidth,error:v.error?.code??null}}"))
    if samples[-1]['time']<=samples[0]['time']+10 or any(s['error'] or not s['width'] for s in samples):raise RuntimeError('Actual decoded HLS did not advance')
    page.locator('#stage').focus();page.keyboard.press('ContextMenu');page.locator('#remoteStats').click()
    assert page.locator('#statsGauges').is_visible() and not page.locator('#stats').is_visible()
    page.locator('#remoteStatsInfo').click();assert page.locator('#stats').is_visible() and page.locator('#remotePanel').is_visible()
    page.locator('#remoteStats').click();assert page.locator('#statsGauges').is_hidden() and page.locator('#stats').is_visible()
    page.screenshot(path=str(out/(stamp+'-'+engine+'-installed-stats.png')))
    page.locator('#remoteStatsInfo').click();assert page.locator('#statsPanel').is_hidden()
    assert not errors,errors
    rows.append({'engine':engine,'installedTreeAndIndependentStats':True,'actualHls':True,'samples':samples,'physicalPhone':False})
   finally:
    retire();context.close();browser.close()
  report['passed']=True
except Exception as error:
 report['error']=str(error)[:500];raise
finally:
 if owned:retire()
 report['finalActivity']=C.activity(cfg)
 path=out/(stamp+'-installed-settings.json');path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'passed':report['passed'],'report':str(path.relative_to(ROOT))}),flush=True)
