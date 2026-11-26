#!/usr/bin/env python3
"""Bounded native-DVD field playback on stock232, not physical iPhone proof.

Existing public MCP is setup only. No optional companion hooks, saved options,
Core changes, retries of ordered controls, mounts or imported-media repair.
"""
import importlib.util,json,os,time
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
identity='da92a86446be';owned=None;page=None;passed=False;rows=[];errors=[];cleanup=[];failure={}
OUT=Path(os.environ.get('SAGETV_ARTIFACT_DIR',ROOT/'artifacts/active/WEB-014')).resolve()
if not OUT.is_relative_to((ROOT/'artifacts/active').resolve()):raise RuntimeError('Task-owned output required')
OUT.mkdir(parents=True,exist_ok=True);stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
engine=os.environ.get('SAGETV_BROWSER_ENGINE','webkit')
if engine not in ('chromium','webkit'):raise RuntimeError('Unsupported browser')
sources={
 'pal':('/var/media/OpenSageTV_Vibe_Tests/VIBE_AUTHORED_DVD_PAL',21008),
 'sparse':('/var/media/OpenSageTV_Vibe_Tests/VIBE_AUTHORED_DVD_SPARSE',21012),
 'aladdin':('/var/media/videos/Aidens_Movies/ALADDIN',2504),
}
def mcp(action,**v):return C.request(cfg,'/v1/control',dict(action=action,**v),mcp=True,timeout=8)
def api(action,**v):return C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action=action,session=owned,**v),timeout=8)
def guard():
    a=C.activity(cfg);uis=mcp('ui.list').get('contexts',[])
    if a.get('recordingCount')!=0 or a.get('connectedClientCount')!=0 or any(x!=identity for x in uis):raise RuntimeError('Unrelated activity; refuse control')
def wait(test,label,seconds=45):
    deadline=time.monotonic()+seconds
    while time.monotonic()<deadline:
        page.wait_for_timeout(150)
        if test():return
    raise RuntimeError('Timed out: '+label)
def observe(response):
    global owned
    if '/api/miniclient' not in response.url or response.request.method!='POST':return
    try:
        r=response.json()
        if r.get('session') and r.get('clientId','').replace(':','').lower()==identity:owned=r['session']
    except Exception:pass
def state():return mcp('ui.state',context=identity)
def activation():
    # One actual Playwright gesture per observed prompt, not synthetic JS Play.
    if page.locator('#autoplayBtn').is_visible():
        page.locator('#autoplayBtn').click();return True
    return False
try:
    guard()
    with sync_playwright() as pw:
        browser=pw.webkit.launch(headless=True) if engine=='webkit' else pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
        context=browser.new_context(viewport={'width':852,'height':393},http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block')
        page=context.new_page();page.on('response',observe);page.on('pageerror',lambda e:errors.append(str(e)))
        page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify({player:'hls',videoMode:'transcode',videoKbps:1200,resolution:'480',deinterlace:'on',companionDvd:false}));")
        page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
        wait(lambda:owned is not None and identity in mcp('ui.list').get('contexts',[]),'owned UI')
        wait(lambda:api('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'),'native first frame')
        for name,(path,expected) in sources.items():
            guard();r=mcp('media.resolve_exact_path',path=path)
            if r.get('mediaFileId')!=expected:raise RuntimeError('Exact indexed source mismatch: '+name)
            page.evaluate("()=>{const s=window.DVD_FIELD={before:videoPlane.currentSrc,active:null,epoch:0,frames:0,time:0};const f=(n,m)=>{if(window.DVD_FIELD!==s)return;const src=videoPlane.currentSrc;if(src!==s.active){s.active=src;s.epoch++;s.frames=0;s.time=0;}if(src!==s.before){s.frames++;s.time=m.mediaTime;}videoPlane.requestVideoFrameCallback(f);};videoPlane.requestVideoFrameCallback(f);}")
            if not mcp('media.watch',context=identity,media_id=expected,wait_ms=0).get('accepted'):raise RuntimeError('Watch not accepted; no replay')
            wait(lambda:state().get('dvd') and (state().get('media') or {}).get('mediaFileId')==expected,'native disc identity')
            wait(lambda:page.evaluate('videoPlane.videoWidth>0||!dvdStillFrame.hidden'),'decoded picture',60)
            native=state();page.screenshot(path=str(OUT/(stamp+'-'+name+'-initial.png')))
            menu=bool(native.get('dvdMenu'));gesture=activation()
            if menu:
                page.evaluate('()=>{DVD_FIELD.before=videoPlane.currentSrc;DVD_FIELD.frames=0;DVD_FIELD.time=0;}')
                if not mcp('ui.command',context=identity,command='Select').get('accepted'):raise RuntimeError('Authored select not accepted')
            wait(lambda:not state().get('dvdMenu'),'feature after authored default selection',60)
            prompted=[gesture]
            def moving():
                if not prompted[0]:prompted[0]=activation()
                return page.evaluate('DVD_FIELD.frames>=15&&videoPlane.readyState>=2&&!videoPlane.paused&&videoPlane.currentTime>.5&&!videoPlane.error')
            wait(moving,'new presented feature: '+name,60)
            a=page.evaluate('({epoch:DVD_FIELD.epoch,frames:DVD_FIELD.frames,frameTime:DVD_FIELD.time,time:videoPlane.currentTime})')
            page.wait_for_timeout(2000)
            b=page.evaluate('({epoch:DVD_FIELD.epoch,frames:DVD_FIELD.frames,frameTime:DVD_FIELD.time,time:videoPlane.currentTime})')
            native=state();dvd=api('status').get('connection',{}).get('dvd',{})
            row=dict(source=name,mediaId=expected,passed=True,initialMenu=menu,actualBrowserActivation=prompted[0],before=a,after=b,
                title=native.get('dvdTitle'),chapter=native.get('dvdChapter'),nativeTimeMs=native.get('mediaTimeMs'),
                format={k:dvd.get('ps',{}).get(k) for k in ('videoWidth','videoHeight')},audioSelector=dvd.get('audioSelector'))
            if b['epoch']!=a['epoch'] or b['frames']<=a['frames'] or b['frameTime']<=a['frameTime'] or b['time']<=a['time']:
                row['passed']=False
                failure.update(sample=row,native={k:native.get(k) for k in ('dvdMenu','dvdTitle','dvdChapter','mediaTimeMs','durationMs')},
                    dvd=dvd,video=page.evaluate('({time:videoPlane.currentTime,ended:videoPlane.ended,paused:videoPlane.paused,ready:videoPlane.readyState,error:videoPlane.error?.code||null,message:osdMessage.textContent})'))
                raise RuntimeError('Held/repeating clock: '+name)
            rows.append(row);print(json.dumps(row),flush=True)
            page.screenshot(path=str(OUT/(stamp+'-'+name+'-feature.png')))
            guard()
            if not mcp('media.control',context=identity,operation='stop').get('ok'):raise RuntimeError('Stop rejected')
            wait(lambda:not state().get('fullyLoaded') and page.evaluate('videoPlane.paused'),'native/browser Stop')
            rows.append(dict(source=name,gate='stop',passed=True))
        if errors:raise RuntimeError('Browser JS errors')
        passed=True;context.close();browser.close()
except Exception as error:
    failure.update(errorType=type(error).__name__,message=str(error)[:300] if isinstance(error,RuntimeError) else 'Field observation failed')
    raise
finally:
    if owned:
        try:api('stop')
        except Exception:pass
    deadline=time.monotonic()+90
    while time.monotonic()<deadline:
        try:
            if identity not in mcp('ui.list').get('contexts',[]):break
        except Exception:pass
        time.sleep(.25)
    else:cleanup.append('Native UI retirement not independently verified')
    (OUT/(stamp+'-real-dvd-'+engine+'.json')).write_text(json.dumps(dict(passed=passed and not cleanup,engine=engine,
        stockServer='.232',physicalIPhone=False,allDiscCertification=False,optionalExtension=False,rows=rows,errors=errors,cleanup=cleanup,failure=failure),indent=2)+'\n',encoding='utf-8')
    if cleanup:raise RuntimeError('; '.join(cleanup))
