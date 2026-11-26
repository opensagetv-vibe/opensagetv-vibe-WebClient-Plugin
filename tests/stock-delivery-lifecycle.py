#!/usr/bin/env python3
"""Real stock232/vendor delivery, cold/warm decoder and browser visibility.

Only canonical generated20905 is watched/reset; no Core/household settings.
Headless browser visibility is not physical iPhone/OS-background certification.
"""
import argparse, base64, importlib.util, json, signal, subprocess, time
from pathlib import Path
from urllib.parse import urlencode, urlparse
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--engine',choices=('chromium','webkit'),required=True)
p.add_argument('--transport',choices=('mpegts','hls','native'),required=True)
p.add_argument('--headed',action='store_true',help='Use existing Xvfb to observe real tab visibility; never synthesize document.hidden')
p.add_argument('--allow-native-fallback',action='store_true',help='Native-only compatibility row: permit same-producer client MSE after explicit native rejection')
a=p.parse_args();identity='da92a86446be';owned=None;page=None;context=None;browser=None
if a.allow_native_fallback and a.transport!='native':p.error('Native compatibility option requires native transport')
rows=[];errors=[];cleanup=[];passed=False;failure=None;launcher=None;wm=None;last_video=None
last_request=None;phase='preflight'
pw=None;capabilities=None;unsupported=False
class UnsupportedTransport(RuntimeError):pass
out=ROOT/'artifacts/active/WP16-002';out.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
def mcp(action,**kw):
    global last_request
    last_request='mcp:'+action
    return C.request(cfg,'/v1/control',dict(action=action,**kw),mcp=True,timeout=30)
def api(action,**kw):
    global last_request
    last_request='api:'+action
    if action in ('status','streamSettings'):
        return C.request(cfg,'/SageTVWebPlayer/api/miniclient?'+urlencode(dict(action=action,session=owned,**kw)))
    return C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action=action,session=owned,**kw))
def wait(test,label,seconds=45):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        if test():return
        page.wait_for_timeout(100)
    raise RuntimeError('Timed out '+label+'; ordered controls are not replayed')
def observed(response):
    global owned
    if '/api/miniclient' not in response.url or response.request.method!='POST':return
    try:
        d=response.json()
        if d.get('session') and d.get('clientId','').replace(':','').lower()==identity:owned=d['session']
    except Exception:pass
def sample():
    global last_video
    def expired(signum,frame):raise TimeoutError('Browser video inspection RPC exceeded10s')
    previous=signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,10)
    try:
      last_video=page.evaluate("""()=>({frames:FIELD.frames,time:videoPlane.currentTime,
      width:videoPlane.videoWidth,ready:videoPlane.readyState,paused:videoPlane.paused,
      blocked:!document.getElementById('autoplayBtn').hidden,
      error:videoPlane.error?.code||null,visibility:document.visibilityState,
      sourceKind:videoPlane.srcObject?'object':videoPlane.currentSrc.startsWith('blob:')?'blob':'direct',
      sourceObjectType:videoPlane.srcObject?.constructor?.name||null,
      hlsVersion:window.Hls?.version||null,hlsSupported:!!(window.Hls&&Hls.isSupported()),appends:FIELD.appends,
      vendorReads:performance.getEntriesByType('resource').filter(e=>new URL(e.name).pathname.includes('/vendor/')&&new URL(e.name).pathname.endsWith('.js')).length})""")
      return last_video
    finally:signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,previous)
def retire():
    global context,owned
    if owned and identity in mcp('ui.list').get('contexts',[]):api('stop')
    if context:
        try:context.close()
        except Exception:cleanup.append('ContextCloseUnavailableAfterDriverExit')
        context=None
    end=time.monotonic()+95
    while time.monotonic()<end:
        if identity not in mcp('ui.list').get('contexts',[]):owned=None;return
        time.sleep(.3)
    raise RuntimeError('Exact owned UI retirement not confirmed')
try:
    initial=C.activity(cfg)
    if not initial.get('safeToRestart') or mcp('ui.list').get('contexts'):raise RuntimeError('Require independent idle server')
    fixture=mcp('media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/VibeCaptionTest-1080i-CEA608-90s-2s.ts')
    if fixture.get('mediaFileId')!=20905:raise RuntimeError('Canonical fixture identity changed')
    if a.headed:
        wm=subprocess.Popen(['openbox','--sm-disable','--config-file','/etc/xdg/openbox/rc.xml'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    pw=sync_playwright().start()
    if pw:
        options={'headless':not a.headed}
        if a.engine=='chromium':options.update(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox']+(['--enable-automation','--remote-debugging-port=0'] if a.headed else []))
        launcher=getattr(pw,a.engine).launch(**options);browser=launcher
        if a.headed and a.engine=='chromium':
            # Public connection option suppresses Playwright's otherwise forced
            # focus/visibility. Only this disposable default test context.
            session=launcher.new_browser_cdp_session()
            args=session.send('Browser.getBrowserCommandLine')['arguments'];session.detach()
            directory=next(arg.split('=',1)[1] for arg in args if arg.startswith('--user-data-dir='))
            port=(Path(directory)/'DevToolsActivePort').read_text(encoding='utf-8').splitlines()[0]
            browser=pw.chromium.connect_over_cdp('http://127.0.0.1:'+port,no_defaults=True)
            context=browser.contexts[0]
            auth='Basic '+base64.b64encode((cfg['web_username']+':'+cfg['web_password']).encode()).decode()
            allowed=urlparse(cfg['web_base_url'])
            def restricted(route):
                target=urlparse(route.request.url)
                if (target.scheme,target.netloc)!=(allowed.scheme,allowed.netloc):route.abort();return
                route.continue_(headers={**route.request.headers,'authorization':auth})
            context.route('**/*',restricted)
        else:
            context=browser.new_context(viewport={'width':852,'height':393},http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block')
        page=context.new_page();page.on('response',observed);page.on('pageerror',lambda e:errors.append(str(e)))
        capabilities=page.evaluate("""()=>{const v=document.createElement('video');return {
          nativeHls:v.canPlayType('application/vnd.apple.mpegurl'),
          nativeHlsAlternative:v.canPlayType('application/x-mpegURL')}}""")
        if a.transport=='native' and not any(capabilities.values()):
            raise UnsupportedTransport('This browser build advertises no native HLS support; no native UI or Watch created')
        if a.headed and a.engine=='chromium':page.set_viewport_size({'width':852,'height':393})
        settings={'player':a.transport,'videoMode':'transcode','encoder':'qsv','allowFallback':a.allow_native_fallback,'videoKbps':1000,'resolution':'480','deinterlace':'on'}
        page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify("+json.dumps(settings)+"));")
        page.add_init_script("window.FIELD={frames:0,appends:0};if(window.SourceBuffer){const append=SourceBuffer.prototype.appendBuffer;SourceBuffer.prototype.appendBuffer=function(b){FIELD.appends++;return append.apply(this,arguments)}};document.addEventListener('DOMContentLoaded',()=>{const v=document.getElementById('videoPlane');const f=()=>{if(v.readyState>=2&&v.videoWidth)FIELD.frames++;v.requestVideoFrameCallback(f)};v.requestVideoFrameCallback(f)});")
        page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
        wait(lambda:owned is not None and api('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'),'owned first UI')
        profile=page.evaluate("[localStorage.getItem('sagetvWebMiniClientSettings.v1'),localStorage.getItem('sagetvWebStreaming.v1')]")
        configured=api('streamSettings').get('configured')
        for phase in ('cold','warm'):
            mcp('media.clear_watched',media_id=20905,confirm='true')
            before=sample();began=time.monotonic()
            reply=mcp('media.watch',context=identity,media_id=20905,wait_ms=0)
            if not reply.get('accepted'):raise RuntimeError('One Watch rejected')
            clicked=False;native_failure_at=None;native_failure_producer=None
            def moving():
                global clicked,native_failure_at,native_failure_producer
                s=sample()
                if s['blocked'] and not clicked:
                    clicked=True;page.locator('#autoplayBtn').click(timeout=3000)
                if s['error']:
                    if a.transport=='native' and a.allow_native_fallback and s['error'] in (3,4) and s['frames']==before['frames']:
                        if native_failure_at is None:
                            native_failure_at=time.monotonic();native_failure_producer=api('streamSettings').get('session')
                        if time.monotonic()-native_failure_at<12:return False
                    raise RuntimeError('Actual decoder error '+str(s['error']))
                return s['frames']>=before['frames']+12 and s['time']>.4 and not s['paused']
            wait(moving,phase+' decoded output',70)
            active=api('streamSettings');producer=active.get('session')
            hls=C.request(cfg,'/SageTVWebPlayer/api/hls?'+urlencode({'session':producer}))
            if hls.get('encoder')!='h264_qsv' or not all(hls.get(k) for k in ('hardware','hardwareDecode','hardwareFilters')):raise RuntimeError('Requested full QSV pipeline not observed')
            state=sample();row={'gate':phase,'passed':True,'firstFrameSeconds':time.monotonic()-began,'decoded':state,'requestedPlayer':a.transport,'planPlayer':hls.get('streamSettings',{}).get('requested',{}).get('player'),'actualLoader':page.locator('#stats').text_content().split('Loader ',1)[-1].split('\n',1)[0]}
            if phase=='warm' and state['vendorReads']!=cold_reads:raise RuntimeError('Warm source fetched another vendor library')
            if native_failure_at is not None:
                page.evaluate('videoInfoBtn.click()')
                playback=json.loads(page.locator('#videoInfoText').text_content()).get('playback',{})
                page.evaluate('closeVideoInfo.click()')
                if native_failure_producer!=producer or playback.get('nativeHlsFallbackResult')!='attached' or playback.get('recoveries')!=0 or playback.get('browserEngine')!='HLS / MSE':
                    raise RuntimeError('Native decoder rejection did not retain same producer with client-only MSE')
                row['nativeFirstPictureRejected']=True;row['sameProducerMseFallback']=True
                row['serverRecoveries']=playback.get('recoveries');row['actualBrowserEngine']=playback.get('browserEngine')
            cold_reads=state['vendorReads'];rows.append(row);print('PASS '+a.engine+'/'+a.transport+' '+phase+' actual frames/fullQSV',flush=True)
            if phase=='cold':
                cdp=None;other=None;window=None
                try:
                    if a.engine=='chromium' and a.headed:
                        cdp=context.new_cdp_session(page);window=cdp.send('Browser.getWindowForTarget')
                        cdp.send('Browser.setWindowBounds',{'windowId':window['windowId'],'bounds':{'windowState':'minimized'}})
                    else:
                        other=context.new_page();other.goto('about:blank');other.bring_to_front()
                    page.wait_for_timeout(1000);hidden=sample();page.wait_for_timeout(3000)
                finally:
                    if cdp and window:
                        cdp.send('Browser.setWindowBounds',{'windowId':window['windowId'],'bounds':{'windowState':window['bounds'].get('windowState','normal')}})
                        cdp.detach()
                    if other:other.close()
                    page.bring_to_front()
                anchor=sample();wait(lambda:sample()['frames']>anchor['frames']+8 and not sample()['paused'],'foreground new decoded frames',15)
                after=sample()
                if api('streamSettings').get('session')!=producer:raise RuntimeError('Visibility cycle replaced healthy producer')
                rows.append({'gate':'background-foreground','passed':hidden['visibility']=='hidden','status':'PASS' if hidden['visibility']=='hidden' else 'BROWSER_BACKGROUND_NOT_OBSERVED','foregroundProgressPassed':True,'hiddenObserved':hidden['visibility']=='hidden','before':state,'background':hidden,'after':after,'sameProducer':True,'physicalOSBackground':False})
            if not mcp('media.control',context=identity,operation='stop').get('accepted'):raise RuntimeError('Stop rejected')
            wait(lambda:page.evaluate('videoPlane.paused&&videoPlane.readyState===0&&!videoPlane.getAttribute("src")'),'decoder Stop',15)
        if profile!=page.evaluate("[localStorage.getItem('sagetvWebMiniClientSettings.v1'),localStorage.getItem('sagetvWebStreaming.v1')]") or configured!=api('streamSettings').get('configured'):raise RuntimeError('Saved/configured profiles changed')
        if errors:raise RuntimeError('Unhandled browser errors')
        retire()
        if browser.is_connected():browser.close()
        if launcher.is_connected():launcher.close()
        browser=launcher=None
        passed=True
except UnsupportedTransport:unsupported=True
except Exception as e:
    failure={'type':type(e).__name__,'message':str(e)[:300],'lastVideo':last_video,'phase':phase,'lastRequest':last_request}
    if owned:
        try:
            state=C.activity(cfg)
            contexts=C.request(cfg,'/v1/control',{'action':'ui.list'},mcp=True,timeout=8).get('contexts')
            if state.get('recordingCount')==0 and state.get('connectedClientCount')==0 and contexts==[identity]:
                diagnostic=C.request(cfg,'/v1/control',{'action':'diagnostics.threads'},mcp=True,timeout=8)
                if diagnostic.get('ok') and diagnostic.get('schemaVersion')==1:
                    dest=out/(stamp+'-'+a.engine+'-'+a.transport+'-threads.json')
                    dest.write_text(json.dumps(diagnostic,indent=2)+'\n',encoding='utf-8')
                    failure['boundedThreadSnapshot']=str(dest.relative_to(ROOT))
        except Exception:failure['threadSnapshotUnavailable']=True
finally:
    try:
        if owned or context:retire()
    except Exception as e:cleanup.append(type(e).__name__);passed=False
    if browser:
        try:browser.close()
        except Exception:cleanup.append('BrowserLoopAlreadyClosed');passed=False
    if launcher:
        try:launcher.close()
        except Exception:pass
    if pw:
        try:pw.stop()
        except Exception:cleanup.append('PlaywrightStopUnavailable');passed=False
    if wm:
        wm.terminate()
        try:wm.wait(timeout=5)
        except subprocess.TimeoutExpired:wm.kill();wm.wait(timeout=5);cleanup.append('DisplayManagerForcedExit');passed=False
    complete=passed and all(r.get('passed') for r in rows)
    status='PASS' if complete else 'UNSUPPORTED_NATIVE_HLS' if unsupported and not cleanup else 'PARTIAL_VISIBILITY_UNAVAILABLE' if passed else 'FAIL'
    report={'passed':complete,'functionalChecksPassed':passed,'status':status,'engine':a.engine,'transport':a.transport,'allowFallback':a.allow_native_fallback,'headed':a.headed,'realStock232':True,'physicalPhone':False,'capabilities':capabilities,'rows':rows,'errors':errors,'cleanup':cleanup,'failure':failure}
    path=out/(stamp+'-'+a.engine+'-'+a.transport+'.json');path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':complete,'functionalChecksPassed':passed,'status':status,'rows':len(rows),'failure':failure,'report':str(path)}),flush=True)
raise SystemExit(0 if complete else 77 if passed or unsupported and not cleanup else 1)
