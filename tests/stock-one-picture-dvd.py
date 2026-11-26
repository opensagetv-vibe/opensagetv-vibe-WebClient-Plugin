#!/usr/bin/env python3
"""Actual stock232 one-picture DVD through Chrome/WebKit, not iPhone proof.

Public MCP sets up the one exact generated disc. Real browser media/canvas
and public production fullscreen/Select are observed, never synthesized.
"""
import importlib.util,json,os,time
from pathlib import Path
from urllib.error import URLError
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
fixture=os.environ.get('SAGETV_DVD_FIXTURE','one-picture')
if fixture not in ('one-picture','nonfirst'):raise RuntimeError('Unknown canonical DVD fixture')
nonfirst=fixture=='nonfirst'
identity='da92a86446be';media_id=83871 if nonfirst else 78957;owned=None;page=None;context=None;browser=None
engine=os.environ.get('SAGETV_BROWSER_ENGINE','webkit')
if engine not in ('chromium','webkit'):raise RuntimeError('Unsupported browser')
hold_seconds=int(os.environ.get('SAGETV_DVD_STILL_HOLD_SECONDS','10'))
if not 10<=hold_seconds<=120:raise RuntimeError('Still hold must remain10..120seconds')
unified=os.environ.get('SAGETV_UNIFIED_GRAPHICS')
if unified not in (None,'off','on'):raise RuntimeError('Explicit unified mode must be off/on')
out=Path(os.environ.get('SAGETV_ARTIFACT_DIR',str(ROOT/'artifacts/active'/('WP10-004' if nonfirst else 'WP13-003' if unified is not None else 'WP08-006')))).resolve()
if not out.is_relative_to((ROOT/'artifacts/active').resolve()):raise RuntimeError('Physical artifacts must remain under this project artifacts/active')
out.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());report=dict(passed=False,realStock232=True,physicalPhone=False,engine=engine,holdSeconds=hold_seconds,rows=[],cleanup=[])
def mcp(action,**values):
    # Read-only terminal snapshots can race native teardown. Never replay an
    # accepted Watch, Select, Stop or other ordered control on uncertainty.
    for attempt in range(3 if action in ('ui.list','ui.state') else 1):
        try:return C.request(cfg,'/v1/control',dict(action=action,**values),mcp=True,timeout=8)
        except (URLError,TimeoutError):
            if action not in ('ui.list','ui.state') or attempt==2:raise
            report['readOnlyObservationRetries']=report.get('readOnlyObservationRetries',0)+1
def api(action,**values):return C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action=action,session=owned,**values))
def guard(loaded=False):
    a=C.activity(cfg);contexts=mcp('ui.list').get('contexts',[])
    if a.get('recordingCount')!=0 or a.get('connectedClientCount')!=0 or any(x!=identity for x in contexts):raise RuntimeError('Preserve unrelated activity')
    n=mcp('ui.state',context=identity) if contexts else {}
    if loaded and (not n.get('dvd') or n.get('media',{}).get('mediaFileId')!=media_id):raise RuntimeError('Exact source changed')
    return n
def observed(response):
    global owned
    if '/api/miniclient' in response.url and response.request.method=='POST':
        try:
            j=response.json()
            if j.get('session') and j.get('clientId','').replace(':','').lower()==identity:owned=j['session']
        except Exception:pass
def sample():
    if page.locator('#autoplayBtn').is_visible():page.locator('#autoplayBtn').click()
    return page.evaluate("""()=>{const v=videoPlane,c=dvdSpuCanvas,p=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let pixels=0;for(let i=3;i<p.length;i+=4)if(p[i])pixels++;return{time:v.currentTime,ready:v.readyState,paused:v.paused,width:v.videoWidth,frames:ONE_PICTURE.frames,frameSourceCurrent:ONE_PICTURE.active===v.currentSrc,frameTime:ONE_PICTURE.frameTime,changed:v.currentSrc!==ONE_PICTURE.before,still:!dvdStillFrame.hidden,pixels,error:v.error?.code||null,message:osdMessage.textContent}}""")
def wait(test,label,seconds=40):
    until=time.monotonic()+seconds
    while time.monotonic()<until:
        v=sample();report['last']=v
        if v['error']:raise RuntimeError('Actual browser media error')
        if v['frameSourceCurrent'] and test(v):return v
        page.wait_for_timeout(100)
    raise RuntimeError('Timed out: '+label)
try:
    report['stage']='preflight-activity'
    if not C.activity(cfg).get('safeToRestart'):raise RuntimeError('Independent idle proof required')
    report['stage']='resolve-fixture'
    fixture_path='/var/media/OpenSageTV_Vibe_Tests/'+('WP10-NonFirst' if nonfirst else 'WP08-OnePicture')+'/VIDEO_TS'
    if mcp('media.resolve_exact_path',path=fixture_path).get('mediaFileId')!=media_id:raise RuntimeError('Canonical fixture changed')
    with sync_playwright() as pw:
        report['stage']='browser-connect'
        browser=pw.webkit.launch(headless=True) if engine=='webkit' else pw.chromium.launch(executable_path='/usr/local/bin/vibe-chromium',headless=True,args=['--no-sandbox'])
        context=browser.new_context(viewport={'width':852,'height':393},http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block')
        page=context.new_page();page.on('response',observed)
        page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify({player:'hls',videoMode:'transcode',videoKbps:1000,resolution:'480',fps:23.976,deinterlace:'off'}));")
        if unified is not None:
            page.add_init_script("localStorage.setItem('sagetvWebMiniClientSettings.v1',JSON.stringify({unifiedGraphics:"+str(unified=='on').lower()+"}));")
        page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
        page.wait_for_function("document.querySelector('#connectionStatus').textContent.toLowerCase().startsWith('connected')",timeout=30000)
        if not owned:raise RuntimeError('No owned native session')
        if unified is not None:
            actual=C.request(cfg,'/SageTVWebPlayer/api/miniclient?action=status&session='+owned).get('connection',{}).get('unifiedGraphics')
            if actual is not (unified=='on'):raise RuntimeError('Unified graphics negotiation mismatch')
            report['unifiedGraphics']=actual
        page.add_script_tag(path=str(ROOT/'tests/fixtures/one-picture-frame-observer.js'))
        page.evaluate('()=>{window.ONE_PICTURE=observeOnePictureFrames(videoPlane)}')
        guard()
        # A fresh native UI can inherit the last test's non-playback STV menu.
        # Establish the ordinary public Home intent before Watch instead of
        # guessing a fullscreen toggle from an unqualified library/setup menu.
        if not api('command',command=89).get('ok'):raise RuntimeError('Public Home setup rejected')
        page.wait_for_timeout(700);report['publicHomeSetup']=True
        report['stage']='watch-submit';report['watchSubmitted']=True
        if not mcp('media.watch',context=identity,media_id=media_id,wait_ms=0).get('accepted'):raise RuntimeError('One Watch rejected; no replay')
        report['watchAccepted']=True;report['stage']='watch-loading'
        # Accepted Watch is asynchronous. An unloaded initial snapshot is not
        # evidence of a user changing source; only wait/read, never replay it.
        until=time.monotonic()+45
        while True:
            n=guard();actual=(n.get('media') or {}).get('mediaFileId')
            if actual not in (None,media_id):raise RuntimeError('Another source became active')
            if n.get('fullyLoaded') and n.get('dvd') and actual==media_id:break
            if time.monotonic()>=until:raise RuntimeError('Exact DVD did not finish loading')
            page.wait_for_timeout(150)
        first=wait(lambda v:guard(True).get('dvdMenu') and v['frames']>=1 and v['width']>0 and v['pixels']>100,'one decoded menu picture/highlight')
        report['stage']='decoded-menu'
        report['rows'].append(dict(gate='one-picture-decoded',sample=first))
        until=time.monotonic()+15
        while True:
            layout=api('contentState',mediaId=media_id)
            if (layout.get('ready') and layout.get('layout') in ('preview','fullscreen')) or time.monotonic()>=until:break
            page.wait_for_timeout(150)
        report['viewBefore']=dict(ready=layout.get('ready'),layout=layout.get('layout'),evidence=layout.get('viewEvidence'))
        if layout.get('ready') and layout.get('layout')=='preview':
            if not api('showContent',mediaId=media_id).get('ok'):raise RuntimeError('Qualified fullscreen completion rejected')
        elif not layout.get('ready') or layout.get('layout')!='fullscreen':raise RuntimeError('Unknown DVD layout; no guessed toggle')
        page.wait_for_timeout(hold_seconds*1000)
        held=sample();guard(True)
        if held['pixels']<100 or held['message'] or not (held['still'] or held['width']>0):raise RuntimeError('One-picture menu blanked/buffering')
        report['rows'].append(dict(gate='held'+str(hold_seconds)+'s-without-audio',sample=held))
        page.screenshot(path=str(out/(stamp+'-'+engine+'-still.png')))
        page.evaluate('()=>{ONE_PICTURE.before=videoPlane.currentSrc;ONE_PICTURE.frames=0}')
        page.locator('#stage').focus();page.keyboard.press('Enter')
        report['stage']='feature-after-select'
        feature=wait(lambda v:not guard(True).get('dvdMenu') and v['changed'] and v['frames']>=15 and v['time']>.5 and not v['paused'],'new feature after production Enter')
        report['rows'].append(dict(gate='select-new-feature',sample=feature))
        if nonfirst:
            n=guard(True)
            title={k:n.get(k) for k in ('dvdTitle','dvdChapter','durationMs','rawMediaTimeMs')}
            if title['dvdTitle']!=2 or title['dvdChapter'] not in (1,2,3):raise RuntimeError('Authored Main did not select explicit title2/valid chapter')
            if not isinstance(title['durationMs'],(int,float)) or abs(title['durationMs']-12012)>500:raise RuntimeError('Native title duration conflated with total library duration')
            disc=C.request(cfg,'/SageTVWebPlayer/api/disc?id='+str(media_id)+'&title=2',timeout=20)
            report['discInspection']=disc
            probe=disc.get('titleProbe',{})
            if probe.get('available'):
                chapters=probe.get('chapters',[])
                if probe.get('title')!=2 or abs(probe.get('durationSeconds',0)-12.012)>.5 or len(chapters)!=3:raise RuntimeError('Explicit IFO probe title/duration/chapters mismatch')
                if any(abs(chapters[i].get('startSeconds',-999)-i*4)>.6 for i in range(3)):raise RuntimeError('Explicit chapter starts not title-relative')
            else:raise RuntimeError('Explicit title probe unavailable; native title alone is not chapter-list qualification')
            report['rows'].append(dict(gate='authored-nonfirst-title-duration-chapter',sample=title,probeAvailable=probe.get('available')))
        if unified is not None:
            dvd=C.request(cfg,'/SageTVWebPlayer/api/miniclient?action=status&session='+owned).get('connection',{}).get('dvd',{})
            pushed={k:dvd.get(k) for k in ('totalPushedBytes','epochPushedBytes','pushCommands','mediaPushes')}
            if not isinstance(pushed['totalPushedBytes'],int) or pushed['totalPushedBytes']<=0 or not pushed['mediaPushes']:raise RuntimeError('No actual stock DVD Push evidence')
            report['rows'].append(dict(gate='actual-stock-dvd-Push-with-unified-selection',sample=pushed))
        page.evaluate('()=>{ONE_PICTURE.before=videoPlane.currentSrc;ONE_PICTURE.frames=0}')
        report['stage']='natural-root'
        root=wait(lambda v:guard(True).get('dvdMenu') and v['changed'] and v['frames']>=1 and v['width']>0 and v['ready']>=2 and v['pixels']>100 and not v['message'],'natural one-picture root')
        report['rows'].append(dict(gate='natural-root-new-picture',sample=root))
        if not mcp('media.control',context=identity,operation='stop').get('ok'):raise RuntimeError('Stop rejected')
        report['passed']=True
except Exception as error:
    report.update(passed=False,errorType=type(error).__name__,error=str(error)[:250] if isinstance(error,RuntimeError) else 'Bounded observation unavailable',observationStage=report.get('stage','startup'))
    report['reasonType']=type(getattr(error,'reason',None)).__name__
    report['reasonErrno']=getattr(getattr(error,'reason',None),'errno',None)
finally:
    if owned:
        try:api('stop')
        except Exception:report['cleanup'].append('Owned native Stop unverified')
    if context:
        try:context.close()
        except Exception:pass # sync_playwright already retires its browser.
    if browser:
        try:browser.close()
        except Exception:pass
    until=time.monotonic()+60
    while time.monotonic()<until:
        if identity not in mcp('ui.list').get('contexts',[]):break
        time.sleep(.3)
    else:report['cleanup'].append('Owned native retirement unverified')
    report['passed']=report['passed'] and not report['cleanup']
    path=out/(stamp+'-'+engine+'-one-picture.json')
    with path.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
    print(json.dumps(dict(passed=report['passed'],rows=len(report['rows']),error=report.get('error'),report=str(path))))
raise SystemExit(0 if report['passed'] else 1)
