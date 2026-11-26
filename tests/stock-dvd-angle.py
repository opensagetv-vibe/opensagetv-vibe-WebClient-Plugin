#!/usr/bin/env python3
"""Bounded real angle-picture comparison on stock232, never a phone PASS.

Canonical generated fixture only. Public MCP setup, real browser frames and
RGB branch identity; one command per intent, no ordered-control replay.
"""
import importlib.util,json,os,time
from pathlib import Path
from urllib.error import URLError
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
identity='da92a86446be';owned=None;page=None;pw=None;context=None;browser=None;borrowed=[];hook=None;rows=[];cleanup=[];passed=False;failure={}
optional=os.environ.get('SAGETV_ANGLE_COMPANION')=='1'
engine=os.environ.get('SAGETV_BROWSER_ENGINE','webkit')
if engine not in ('webkit','chromium'):raise RuntimeError('Unsupported browser')
OUT=Path(os.environ.get('SAGETV_ARTIFACT_DIR',ROOT/'artifacts/active/WEB-014')).resolve()
if not OUT.is_relative_to((ROOT/'artifacts/active').resolve()):raise RuntimeError('Owning active output required')
OUT.mkdir(parents=True,exist_ok=True);stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
def mcp(action,**v):return C.request(cfg,'/v1/control',dict(action=action,**v),mcp=True,timeout=8)
def api(action,**v):
    # Natural END can coincide with native teardown. Retry ONLY a read-only
    # status observation; never replay a queued playback/control mutation.
    for attempt in range(3 if action=='status' else 1):
        try:return C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action=action,session=owned,**v),timeout=5 if action=='status' else 20)
        except (URLError,TimeoutError):
            if action!='status' or attempt==2:raise
            print('Transient read-only terminal status unavailable',flush=True)
def guard():
    a=C.activity(cfg);contexts=mcp('ui.list').get('contexts',[])
    if a.get('recordingCount')!=0 or a.get('connectedClientCount')!=0 or (contexts and contexts!=[identity]):raise RuntimeError('Independent activity guard rejected angle test')
def state():return mcp('ui.state',context=identity)
def observed(response):
    global owned
    if '/api/miniclient' not in response.url or response.request.method!='POST':return
    try:
        r=response.json()
        if r.get('session') and r.get('clientId','').replace(':','').lower()==identity:owned=r['session']
    except Exception:pass
def wait(test,label,seconds=35):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        if test():return
        page.wait_for_timeout(150)
    raise RuntimeError('Timed out: '+label)
def checkpoint():
    page.evaluate("()=>{const s=window.ANGLE_FIELD;s.before=videoPlane.currentSrc;s.active=null;s.frames=0;s.last=0;}")
def picture():
    if page.locator('#autoplayBtn').is_visible():page.locator('#autoplayBtn').click()
    return page.evaluate("()=>({changed:videoPlane.currentSrc!==ANGLE_FIELD.before,frames:ANGLE_FIELD.frames,time:videoPlane.currentTime,ready:videoPlane.readyState,paused:videoPlane.paused,error:videoPlane.error?.code||null})")
try:
    guard();resolved=mcp('media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/VIBE_AUTHORED_DVD_MULTIANGLE')
    if resolved.get('mediaFileId')!=21029:raise RuntimeError('Require exact generated three-angle fixture')
    pw=sync_playwright().start()
    if pw:
        browser=pw.webkit.launch(headless=True) if engine=='webkit' else pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
        context=browser.new_context(viewport={'width':852,'height':393},http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block')
        page=context.new_page();page.on('response',observed)
        page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify({player:'hls',videoMode:'transcode',videoKbps:1200,resolution:'480',deinterlace:'on',companionDvd:"+str(optional).lower()+"}));")
        page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
        wait(lambda:owned is not None and identity in mcp('ui.list').get('contexts',[]),'owned native UI')
        wait(lambda:api('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'),'native first frame')
        if optional:
            if mcp('companion.dvd_hook',context=identity).get('playerClass')!='':raise RuntimeError('Preserve preexisting player hook')
            for k,v in [('enabled','true'),('dvd.owned_navigation','true'),('dvd.client_controls','true'),('dvd.owned_mode','copy')]:
                before=mcp('companion.config_get',setting=k)['value']
                if before!=v:
                    borrowed.append((k,before,v));mcp('companion.config_set',setting=k,expected=before,value=v,confirm='true')
            hook=mcp('companion.dvd_hook',context=identity,expected='',enabled='true',confirm='true')['playerClass']
        # Only disposable generated fixture metadata; no user recording or
        # separate companion bookmark is cleared or overwritten.
        if not mcp('media.clear_watched',media_id=21029,confirm='true').get('ok'):raise RuntimeError('Canonical watched reset rejected')
        page.evaluate("()=>{const s=window.ANGLE_FIELD={before:videoPlane.currentSrc,active:null,frames:0,last:0,done:false};const f=(n,m)=>{if(s.done)return;const src=videoPlane.currentSrc;if(src!==s.active){s.active=src;s.frames=0;}if(src!==s.before){s.frames++;s.last=m.mediaTime;}videoPlane.requestVideoFrameCallback(f);};videoPlane.requestVideoFrameCallback(f);}")
        if not mcp('media.watch',context=identity,media_id=21029,wait_ms=0).get('accepted'):raise RuntimeError('Watch rejected; no replay')
        branches=((1,0),) if os.environ.get('SAGETV_ANGLE_END_ONLY')=='1' else ((1,0),(2,1),(3,2),(1,0))
        for angle,channel in branches:
            if rows:
                guard();checkpoint()
                if not mcp('ui.command',context=identity,command='DVD Angle Change').get('accepted'):raise RuntimeError('Angle command rejected')
                wait(lambda:state().get('dvdAngle')==angle,'native changed angle',5)
                # Stock native read-ahead can already contain the old branch.
                # Wait for register completion before one explicit seek.
                if not optional and not mcp('media.seek',context=identity,target_ms=3000).get('accepted'):raise RuntimeError('Seek rejected')
            def moving():
                v=picture()
                return v['changed'] and v['frames']>=12 and v['time']>.3 and v['ready']>=2 and not v['paused'] and not v['error']
            wait(moving,'actual branch '+str(angle))
            rgb=page.evaluate("()=>{const v=videoPlane,c=document.createElement('canvas');c.width=c.height=16;const x=c.getContext('2d');x.drawImage(v,0,0,v.videoWidth*.04,v.videoHeight*.04,0,0,16,16);return[...x.getImageData(8,8,1,1).data].slice(0,3);}")
            n=state();row=dict(expected=angle,nativeAngle=n.get('dvdAngle'),angleCount=n.get('dvdAngleCount'),rgb=rgb,picture=picture());rows.append(row)
            if n.get('dvdAngle')!=angle or n.get('dvdAngleCount')!=3 or rgb[channel]<80 or max(v for i,v in enumerate(rgb) if i!=channel)>50:raise RuntimeError('VM/actual picture branch mismatch')
            print(json.dumps(dict(angle=angle,rgb=rgb,passed=True)),flush=True)
        if os.environ.get('SAGETV_ANGLE_END_GATE')=='1':
            wait(lambda:api('status').get('connection',{}).get('dvd',{}).get('terminalEosAcks',0)>0,'actual terminal drain acknowledgement',60)
            before=api('status').get('connection',{}).get('dvd',{})
            page.wait_for_timeout(1200)
            after=api('status').get('connection',{}).get('dvd',{})
            if after.get('segmentEos',0)-before.get('segmentEos',0)>2:raise RuntimeError('Terminal END polling did not retire')
            rows.append(dict(gate='actual-terminal-end-acknowledged-and-polling-retired',beforePolls=before.get('segmentEos'),afterPolls=after.get('segmentEos'),terminalEosAcks=after.get('terminalEosAcks'),passed=True))
            print('PASS actual terminal END acknowledged and retired',flush=True)
        passed=True
except Exception as e:
    failure.update(type=type(e).__name__,message=str(e)[:250])
    if owned:
        try:failure['dvd']=api('status').get('connection',{}).get('dvd',{});failure['native']={k:state().get(k) for k in ('fullyLoaded','dvdMenu','dvdAngle','dvdAngleCount','mediaTimeMs')}
        except Exception:failure['diagnosticsUnavailable']=True
    if page:
        try:failure['video']=page.evaluate("()=>({time:videoPlane.currentTime,duration:videoPlane.duration,ended:videoPlane.ended,paused:videoPlane.paused,ready:videoPlane.readyState,message:osdMessage.textContent,ranges:Array.from({length:videoPlane.buffered.length},(_,i)=>[videoPlane.buffered.start(i),videoPlane.buffered.end(i)])})")
        except Exception:pass
        try:page.screenshot(path=str(OUT/(stamp+'-angle-failure.png')))
        except Exception:pass
finally:
    if hook:
        try:mcp('companion.dvd_hook',context=identity,expected=hook,enabled='false',confirm='true')
        except Exception:cleanup.append('Exact hook restore failed')
    if owned:
        try:mcp('media.control',context=identity,operation='stop')
        except Exception:pass
    for k,before,v in reversed(borrowed):
        try:mcp('companion.config_set',setting=k,expected=v,value=before,confirm='true')
        except Exception:cleanup.append('Configuration restore failed '+k)
    if owned:
        try:api('stop')
        except Exception:pass
    # Keep the exact native context alive until hook/options are restored.
    if context:
        try:context.close()
        except Exception:cleanup.append('Browser context close failed')
    if browser:
        try:browser.close()
        except Exception:cleanup.append('Browser close failed')
    if pw:
        try:pw.stop()
        except Exception:cleanup.append('Playwright close failed')
    end=time.monotonic()+90
    while time.monotonic()<end:
        try:
            if identity not in mcp('ui.list').get('contexts',[]):break
        except Exception:pass
        time.sleep(.3)
    else:cleanup.append('Native UI retirement unavailable')
    result=dict(passed=passed and not cleanup,engine=engine,stockServer='.232',optionalCompanion=optional,physicalPhone=False,rows=rows,failure=failure,cleanup=cleanup)
    with (OUT/(stamp+'-angle-'+engine+'.json')).open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result));raise SystemExit(0 if result['passed'] else 1)
