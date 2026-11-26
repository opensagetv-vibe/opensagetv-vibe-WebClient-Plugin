#!/usr/bin/env python3
"""WP08-008 actual stock232 DVD disconnect/reload cleanup; not phone proof.

Only the exact disposable authored fixture and owned browser ID. Existing
public MCP sets up one Watch per cycle. No control retries, Core changes,
preference edits, forced process kills or cleanup that conceals orphan jobs.
"""
import importlib.util,json,os,re,shlex,time
from pathlib import Path
from urllib.error import URLError
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
identity='da92a86446be';fixture=20819
engine=os.environ.get('SAGETV_BROWSER_ENGINE','webkit')
if engine not in ('webkit','chromium'):raise RuntimeError('Unsupported browser')
modes=os.environ.get('SAGETV_DVD_LIFECYCLE_MODES','explicit-exit,reload,page-close').split(',')
if not modes or len(set(modes))!=len(modes) or any(m not in ('explicit-exit','reload','page-close') for m in modes):raise RuntimeError('Explicit unique lifecycle modes required')
out=ROOT/'artifacts/active/WP08-008';out.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
report=dict(passed=False,realStock232=True,physicalPhone=False,engine=engine,modes=modes,rows=[],cleanup=[])
owned=None;page=None;context=None;browser=None;ssh=None;errors=[]

def mcp(action,**values):
    for attempt in range(3 if action in ('ui.list','ui.state') else 1):
        try:return C.request(cfg,'/v1/control',dict(action=action,**values),mcp=True,timeout=8)
        except (URLError,TimeoutError) as error:
            if action not in ('ui.list','ui.state') or attempt==2:raise
            report['readOnlyMcpRetries']=report.get('readOnlyMcpRetries',0)+1
            report['lastReadRetry']={'action':action,'errorType':type(error).__name__,'reasonType':type(getattr(error,'reason',None)).__name__,'errno':getattr(getattr(error,'reason',None),'errno',None)}
            time.sleep(.2)
def api(action,session=None,**values):return C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action=action,session=session or owned,**values),timeout=8)
def guard(idle=False):
    a=C.activity(cfg);names=mcp('ui.list').get('contexts',[])
    if a.get('recordingCount')!=0 or a.get('connectedClientCount')!=0 or any(n!=identity for n in names):raise RuntimeError('Unrelated activity; refuse mutation')
    if idle and names:raise RuntimeError('Independent idle proof required')
def wait(test,label,seconds=60):
    until=time.monotonic()+seconds
    while time.monotonic()<until:
        if test():return
        if page is not None and not page.is_closed():page.wait_for_timeout(200)
        else:time.sleep(.2)
    raise RuntimeError('Timed out: '+label)
def observed(response):
    global owned
    if '/api/miniclient' not in response.url or response.request.method!='POST':return
    try:
        r=response.json()
        if r.get('session') and r.get('clientId','').replace(':','').lower()==identity:owned=r['session']
    except Exception:pass
def no_encoders():
    data=C.remote(ssh,'docker exec '+shlex.quote(cfg['unraid_container_name'])+' ps -eo comm')
    return not any(x.strip() in ('ffmpeg','ffmpeg.real','SageTVTranscoder','ffmpeg-mim') for x in data.splitlines())
def spool_states(producers):
    if not producers or any(not re.fullmatch('[0-9a-f]{32}',p) for p in producers):raise RuntimeError('Exact observed producer identities required')
    # Commissioned Linux image has the default java.io.tmpdir root. Refuse an
    # explicit alternate root rather than pretending to inspect the real spool.
    data=json.loads(C.remote(ssh,'docker inspect '+shlex.quote(cfg['unraid_container_name'])))[0]
    if any(v.startswith('SAGETV_WEBPLAYER_HLS_DIR=') and v.split('=',1)[1] for v in data['Config']['Env']):raise RuntimeError('Alternate spool root needs explicit commissioning')
    checks='; '.join('if [ -d '+shlex.quote('/tmp/sagetv-webplayer-hls/'+p)+' ]; then echo present; else echo absent; fi' for p in producers)
    states=C.remote(ssh,'docker exec '+shlex.quote(cfg['unraid_container_name'])+' sh -c '+shlex.quote(checks)).splitlines()
    return states
def spool_absent(producers):return spool_states(producers)==['absent']*len(producers)
def native_retired(session):
    try:return api('status',session=session).get('alive') is False
    except (URLError,TimeoutError):
        # This is a read-only observation, not a Stop retry or a PASS. The
        # outer deadline still requires an actual closed/404 witness.
        report['readOnlyStatusUnavailable']=report.get('readOnlyStatusUnavailable',0)+1
        return False
    except RuntimeError as e:
        if str(e).startswith('HTTP 404:'):return True
        raise
def explicit_exit():
    page.locator('#closeRemote').evaluate('e=>e.click()')
    if not page.locator('#exitClientDialog').evaluate('e=>e.open'):raise RuntimeError('Missing Exit confirmation')
    page.locator('#confirmClientExit').click()
    page.wait_for_function('clientExitStatus.textContent.includes("confirmed")',timeout=15000)
    page.wait_for_timeout(700)
    before=page.evaluate('LIFECYCLE.stateRequests')
    page.wait_for_timeout(1200)
    if page.evaluate('LIFECYCLE.stateRequests')!=before:raise RuntimeError('Browser clock pump continued after Exit')
    if not page.evaluate('videoPlane.paused&&videoPlane.readyState===0&&!videoPlane.getAttribute("src")'):raise RuntimeError('Decoder survived Exit')

try:
    guard()
    wait(lambda:identity not in mcp('ui.list').get('contexts',[]),'prior exact commissioning UI retirement',75)
    guard(idle=True)
    if mcp('media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/OpenSageTV_Vibe_Test_DVD').get('mediaFileId')!=fixture:raise RuntimeError('Canonical authored fixture mismatch')
    ssh=C.ssh(cfg)
    if not no_encoders():raise RuntimeError('Preserve existing encoders')
    with sync_playwright() as pw:
        browser=pw.webkit.launch(headless=True) if engine=='webkit' else pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
        for cycle,mode in enumerate(modes,1):
            report['activeMode']=mode;report['stage']='start-cycle'
            blocked_beacons=[]
            guard(idle=True);owned=None
            context=browser.new_context(viewport={'width':852,'height':393},http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block')
            page=context.new_page();page.on('response',observed);page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('console',lambda message:blocked_beacons.append(True) if message.text=='TEST_DROPPED_OWNED_PAGEHIDE_STOP' else None)
            page.add_init_script("""localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify({player:'hls',videoMode:'transcode',videoKbps:1000,resolution:'480',deinterlace:'off',companionDvd:false}));window.LIFECYCLE={stateRequests:0};const lf=fetch;window.fetch=function(u,o){if(new URL(u,location.href).searchParams.get('action')==='state')LIFECYCLE.stateRequests++;return lf.apply(this,arguments)};""")
            page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
            wait(lambda:bool(owned) and api('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'),'native first frame')
            page.add_script_tag(path=str(ROOT/'tests/fixtures/one-picture-frame-observer.js'))
            page.evaluate("()=>{window.DVD_LIFE=observeOnePictureFrames(videoPlane);const p=SageMiniPlayback.prototype,o=p.start;window.LIFE_PRODUCERS=[];p.start=function(e){if(e.hlsSession&&!LIFE_PRODUCERS.includes(e.hlsSession))LIFE_PRODUCERS.push(e.hlsSession);return o.apply(this,arguments)}}")
            if not mcp('media.watch',context=identity,media_id=fixture,wait_ms=0).get('accepted'):raise RuntimeError('One Watch rejected')
            wait(lambda:page.evaluate('DVD_LIFE.frames>=1&&videoPlane.readyState>=2&&videoPlane.videoWidth>0'),'new decoded authored source')
            initial=mcp('ui.state',context=identity)
            if not initial.get('dvd') or initial.get('media',{}).get('mediaFileId')!=fixture:raise RuntimeError('Owned authored identity changed')
            wait(lambda:api('contentState',mediaId=fixture).get('ready'),'public layout readiness',15)
            layout=api('contentState',mediaId=fixture).get('layout')
            if layout=='preview':
                if not api('showContent',mediaId=fixture).get('ok'):raise RuntimeError('Fullscreen rejected')
            elif layout!='fullscreen':raise RuntimeError('Unknown layout; no guessed toggle')
            # Stock resumes this disposable disc after an earlier disconnect.
            # That is valid, not a missing-menu bug. Do not clear watched data
            # or send Select against an already playing resumed title.
            if initial.get('dvdMenu'):
                page.evaluate('()=>{DVD_LIFE.before=videoPlane.currentSrc;DVD_LIFE.frames=0;}')
                page.locator('#stage').focus();page.keyboard.press('Enter')
            def moving():
                if page.locator('#autoplayBtn').is_visible():page.locator('#autoplayBtn').click()
                return not mcp('ui.state',context=identity).get('dvdMenu') and page.evaluate('DVD_LIFE.frames>=8&&videoPlane.currentTime>.3&&!videoPlane.paused&&!videoPlane.error')
            wait(moving,'actual moving feature')
            guard();producers=page.evaluate('LIFE_PRODUCERS.slice()');old=owned
            report['stage']='live-resource-witness'
            live_spools=spool_states(producers)
            if live_spools!=['present']*len(producers):raise RuntimeError('Exact producer spool root was not observed before disconnect')
            if no_encoders():raise RuntimeError('Require active encoder before disconnect, not an already completed converter')
            report['stage']='disconnect-'+mode
            if mode=='explicit-exit':explicit_exit()
            elif mode=='reload':
                page.reload(wait_until='domcontentloaded')
                wait(lambda:bool(owned) and owned!=old and api('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'),'new native session after reload')
                wait(lambda:native_retired(old),'old session retired after reload')
                explicit_exit()
            else:
                # Fault injection belongs only to this ephemeral test context
                # and captured session. Real page-close events still execute;
                # deliberately lose its best-effort Stop, never another client.
                armed=page.evaluate("""id=>{const send=navigator.sendBeacon;const drop=function(url,body){const u=new URL(url,location.href);if(u.origin===location.origin&&u.pathname.endsWith('/api/miniclient')&&u.searchParams.get('action')==='stop'&&body instanceof URLSearchParams&&body.get('session')===id){console.log('TEST_DROPPED_OWNED_PAGEHIDE_STOP');return false}return send.apply(this,arguments)};navigator.sendBeacon=drop;return navigator.sendBeacon===drop}""",old)
                if not armed:raise RuntimeError('Owned lost-beacon injection unavailable')
                page.close(run_before_unload=True)
                if not page.is_closed():page.wait_for_event('close',timeout=10000)
                # run_before_unload returns before asynchronous close; never
                # use that retiring page as the polling delay clock.
                page=None
                report['blockedOwnedBeacons']=len(blocked_beacons)
            report['stage']='observe-native-retirement'
            disconnect_at=time.monotonic()
            wait(lambda:native_retired(old),'closed native session',120 if mode=='page-close' else 60)
            retired_seconds=time.monotonic()-disconnect_at
            wait(lambda:identity not in mcp('ui.list').get('contexts',[]),'native UI retired',75)
            wait(no_encoders,'no orphan encoders',20)
            report['stage']='observe-owned-spools'
            wait(lambda:spool_absent(producers),'exact owned spool removal',40)
            if mode=='page-close' and not blocked_beacons:raise RuntimeError('Lost-beacon fault did not execute; no expiry PASS')
            row=dict(cycle=cycle,mode=mode,initialMenu=initial.get('dvdMenu'),actualMovingFeature=True,encoderObservedBeforeDisconnect=True,ownedSpoolsObservedBeforeDisconnect=len(producers),nativeRetired=True,nativeRetiredSeconds=round(retired_seconds,3),lostOwnedBeacons=len(blocked_beacons),noEncoders=True,ownedSpoolsRemoved=len(producers),browserClockPumpStopped=True if mode!='page-close' else None,browserPageClosed=mode=='page-close')
            report['rows'].append(row);print(json.dumps(row),flush=True)
            context.close();context=None;page=None
        if errors:raise RuntimeError('Browser JS errors')
        report['passed']=True;browser.close();browser=None
except Exception as e:
    report.update(errorType=type(e).__name__,error=str(e)[:200] if isinstance(e,RuntimeError) else 'Bounded observation unavailable')
    report['failureReasonType']=type(getattr(e,'reason',None)).__name__
    report['failureErrno']=getattr(getattr(e,'reason',None),'errno',None)
finally:
    # Cleanup only a still-existing exact owned session, never repeat a Stop
    # whose result is uncertain or kill an encoder to manufacture acceptance.
    if context:
        try:context.close()
        except Exception:pass
    if browser:
        try:browser.close()
        except Exception:pass
    if ssh:ssh.close()
    target=out/(stamp+'-'+engine+'-lifecycle.json')
    with target.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
    print(json.dumps(dict(passed=report['passed'],rows=len(report['rows']),error=report.get('error'),report=str(target))))
raise SystemExit(0 if report['passed'] else 1)
