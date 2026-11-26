#!/usr/bin/env python3
"""WEB-048/049 stock232 native STV timeline; host browser, not iPhone proof."""
import importlib.util,json,os,re,time
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
if os.environ.get('SAGETV_ALLOW_STOCK_TIMELINE')!='1':raise SystemExit('Explicit stock timeline commissioning required')
OUT=Path(os.environ['SAGETV_ARTIFACT_DIR']).resolve()
task=os.environ.get('SAGETV_TIMELINE_TASK','WEB-048')
if task not in ('WEB-048','WEB-049','WEB-050') or OUT!=(ROOT/'artifacts/active'/task).resolve():raise SystemExit('Use the exact owned task artifact directory')
cursor_mode=task in ('WEB-049','WEB-050')
touch_mode=cursor_mode and os.environ.get('SAGETV_TIMELINE_TOUCH')=='1'
stv_mode=os.environ.get('SAGETV_TIMELINE_STV','sagemc')
if stv_mode not in ('sagemc','stock'):raise SystemExit('Unsupported STV')
if stv_mode=='stock' and not cursor_mode:raise SystemExit('Stock STV cursor qualification belongs to WEB-049')
OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
identity='da92a86446be';owned=None;page=None;context=None;browser=None;pw=None;rows=[];errors=[];passed=False;failure=None
engine=os.environ.get('SAGETV_BROWSER_ENGINE','webkit')
if engine not in ('webkit','chromium'):raise SystemExit('Unsupported browser')
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-'+stv_mode+('-touch' if touch_mode else '-mouse');inputs=[];borrowed_stock=False
def mcp(action,**v):return C.request(cfg,'/v1/control',dict(action=action,**v),mcp=True)
def api(action,**v):return C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action=action,session=owned,**v))
def observed(response):
    global owned
    if '/api/miniclient' not in response.url:return
    try:
        action=parse_qs(urlparse(response.url).query).get('action',[''])[0]
        if action=='start':
            data=response.json()
            if data.get('clientId','').replace(':','').lower()==identity:owned=data['session']
        elif action=='click':inputs.append({'observedAt':time.monotonic(),'httpStatus':response.status,'timing':response.request.timing})
    except Exception as error:
        if action=='start':errors.append('Start response inspection: '+type(error).__name__)
def snapshot():
    text=page.locator('#stats').text_content();match=re.search(r'frame queue ([\d.]+)ms.*?queued (\d+)',text)
    native=api('status');pacing=native.get('connection',{}).get('browserFrames',{})
    return {'frameQueueMs':float(match[1]) if match else None,'queuedCommands':int(match[2]) if match else None,'pacing':pacing,'serverQueue':native.get('queuedEvents'),'stats':text}

def restore_stv():
    global borrowed_stock
    if not borrowed_stock:return
    api('command',command=28)
    deadline=time.monotonic()+15
    while time.monotonic()<deadline:
        if mcp('captions.get',context=identity).get('stvFile','').endswith('/SageMC_Vibe.xml'):
            borrowed_stock=False;rows.append({'gate':'original-stv-restored','passed':True});return
        page.wait_for_timeout(300)
    raise AssertionError('Original STV restoration unverified')
def seek(label,target):
    # A normal mouse/touch timeline seek must not be timed in Time Scroll:
    # both STVs deliberately bind their selection marker to TimeScrollTime.
    # Use each STV's normal OSD controls, never its Time Scroll selection.
    # Wait for each state; don't time a tap on a hidden OSD.
    if cursor_mode:
        if stv_mode=='stock':
            api('command',command=59);page.wait_for_function('videoPlane.paused',timeout=5000)
            api('command',command=59);page.wait_for_function('!videoPlane.paused',timeout=5000)
        else:api('command',command=7);api('command',command=24)
    else:api('command',command=10)
    page.wait_for_timeout(400)
    if cursor_mode:
        def marker_present():
            return page.evaluate("stv=>{window.SEEK={stv,t0:performance.now(),targetX:-10000,cursorFrames:[],cursorFirstMs:null};probeNativeCursor();return SEEK.cursorFrames.some(f=>f.markerScore>=(stv==='stock'?15:3));}",stv_mode)
        if not marker_present() and stv_mode=='sagemc':
            api('command',command=24);page.wait_for_timeout(400)
        assert marker_present(),'Native time bar is not visibly ready for an actual tap'
    if cursor_mode:page.screenshot(path=str(OUT/(stamp+'-'+engine+'-'+label+'-before.png')))
    page.evaluate("()=>{const v=videoPlane;window.SEEK={old:v.currentSrc,t0:performance.now(),first:null};const frame=(now,meta)=>{if(v.currentSrc!==SEEK.old&&v.readyState>=2&&meta.mediaTime>.1){SEEK.first={ms:performance.now()-SEEK.t0,time:meta.mediaTime,frames:meta.presentedFrames};return;}v.requestVideoFrameCallback(frame);};v.requestVideoFrameCallback(frame);}")
    if cursor_mode:
        page.evaluate('arg=>{SEEK.stv=arg.stv;SEEK.targetX=arg.left+arg.width*arg.target/89.984;SEEK.cursorFrames=[];SEEK.cursorFirstMs=null;window.probeNativeCursor();}',{'stv':stv_mode,'left':330 if stv_mode=='sagemc' else 179,'width':704 if stv_mode=='sagemc' else 922,'target':target})
        page.evaluate("arg=>{const s=SEEK;s.acceptedMs=null;s.nativeSamples=[];const poll=async()=>{if(SEEK!==s||s.first)return;try{const r=await fetch('api/miniclient?action=streamSettings&session='+encodeURIComponent(arg.session),{cache:'no-store'}),j=await r.json(),ms=performance.now()-s.t0;s.nativeSamples.push({ms,seek:j.nativeSeek,clock:j.lastProvenBrowserTimeMs});if(s.acceptedMs===null&&Math.abs(j.lastProvenBrowserTimeMs-arg.target*1000)<1500)s.acceptedMs=ms;}catch(_){}setTimeout(poll,100);};poll();}",{'session':owned,'target':target})
    box=page.locator('#gfxCanvas').bounding_box();clicks_before=len(inputs)
    left,width,y=(330,704,665) if stv_mode=='sagemc' else (179,922,675)
    x=(left+width*target/89.984)*box['width']/1280;y=y*box['height']/720
    if touch_mode:page.touchscreen.tap(box['x']+x,box['y']+y)
    else:page.locator('#gfxCanvas').click(position={'x':x,'y':y},timeout=5000)
    page.wait_for_function('SEEK.first!==null',timeout=25000)
    frame=page.evaluate('SEEK.first');active=C.request(cfg,'/SageTVWebPlayer/api/miniclient?action=streamSettings&session='+owned)
    status=C.request(cfg,'/SageTVWebPlayer/api/hls?session='+active['session'])
    assert abs(status['startSeconds']-target)<2,(target,status['startSeconds'])
    assert all(status.get(k) for k in ('hardware','hardwareDecode','hardwareFilters')),status.get('encoder')
    assert len(inputs)>clicks_before,'No real browser click request'
    anchor=page.locator('#videoPlane').evaluate('v=>v.currentTime');page.wait_for_timeout(1000)
    assert page.locator('#videoPlane').evaluate('v=>!v.paused&&v.currentTime')>anchor+.3
    state=snapshot();assert state['queuedCommands'] is not None and state['queuedCommands']<4096,state
    assert state['pacing'].get('enabled') is True,state
    cursor=page.evaluate('({firstMs:SEEK.cursorFirstMs,progressFirstMs:SEEK.progressFirstMs,sentMs:SEEK.inputSentMs,ackMs:SEEK.inputAckMs,acceptedMs:SEEK.acceptedMs,frames:SEEK.cursorFrames,nativeSamples:SEEK.nativeSamples})') if cursor_mode else None
    if cursor_mode:
        assert cursor['firstMs'] is not None,'Actual native position marker was not observed'
        assert cursor['firstMs']<frame['ms'],('Native marker still waited for replacement video',cursor['firstMs'],frame['ms'])
    rows.append({'gate':label,'targetSeconds':target,'actualStartSeconds':status['startSeconds'],'firstNewFrame':frame,'input':inputs[-1],'renderer':state,'nativeCursor':cursor})
    page.screenshot(path=str(OUT/(stamp+'-'+engine+'-'+label+'.png')))
    print(json.dumps({'gate':label,'firstNewFrameMs':round(frame['ms'],1),'nativeCursorMs':cursor['firstMs'] if cursor else None,'sentMs':cursor.get('sentMs') if cursor else None,'ackMs':cursor.get('ackMs') if cursor else None,'actualStartSeconds':status['startSeconds'],'queuedCommands':state['queuedCommands'],'frameQueueMs':state['frameQueueMs'],'timeouts':state['pacing'].get('timeouts')}),flush=True)
try:
    activity=C.activity(cfg);contexts=mcp('ui.list').get('contexts',[])
    assert activity.get('recordingCount')==0 and activity.get('connectedClientCount')==0
    assert not contexts,'Requires absent owned identity and no unrelated UIs'
    media=mcp('media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/VibeCaptionTest-1080i-CEA608-90s-2s.ts');assert media.get('mediaFileId')
    pw=sync_playwright().start()
    if pw:
        browser=(pw.webkit.launch(headless=True) if engine=='webkit' else pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox']))
        context=browser.new_context(viewport={'width':1280,'height':800},has_touch=touch_mode,http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block')
        page=context.new_page();page.on('response',observed);page.on('pageerror',lambda e:errors.append(str(e)))
        if cursor_mode:page.add_init_script((ROOT/'tests/fixtures/native-timeline-cursor.js').read_text(encoding='utf-8'))
        page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify({player:'hls',videoMode:'transcode',videoKbps:1000,resolution:'480',deinterlace:'on'}));localStorage.setItem('sagetvWebMiniClientSettings.v1',JSON.stringify({mute:true}));")
        page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html?ui=1280x720',wait_until='domcontentloaded')
        page.wait_for_function("document.getElementById('connectionStatus').textContent.toLowerCase().startsWith('connected')",timeout=60000)
        owner_deadline=time.monotonic()+10
        while not owned and time.monotonic()<owner_deadline:page.wait_for_timeout(100)
        assert owned
        deadline=time.monotonic()+30
        while identity not in mcp('ui.list').get('contexts',[]) and time.monotonic()<deadline:page.wait_for_timeout(250)
        print(json.dumps({'gate':'connected','touch':touch_mode}),flush=True)
        frame_deadline=time.monotonic()+45
        while time.monotonic()<frame_deadline:
            if api('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'):break
            page.wait_for_timeout(300)
        else:raise AssertionError('Owned native UI first frame did not complete')
        if stv_mode=='stock':
            current=mcp('captions.get',context=identity).get('stvFile','')
            assert current.endswith('/SageMC_Vibe.xml'),current
            # SageMC's supported Setup route borrows the DEFAULT stock STV.
            # Home restores the original custom STV; no files/properties are
            # patched and no other client receives a selection change.
            for x,y in [(740,543),(750,542),(158,317)]:
                box=page.locator('#gfxCanvas').bounding_box()
                page.locator('#gfxCanvas').click(position={'x':x*box['width']/1280,'y':y*box['height']/720},timeout=5000)
                page.wait_for_timeout(1000)
            borrowed_stock=True
            deadline=time.monotonic()+15
            while time.monotonic()<deadline:
                if mcp('captions.get',context=identity).get('stvFile','').endswith('/SageTV7.xml'):break
                page.wait_for_timeout(300)
            else:raise AssertionError('Default stock STV route did not load')
        mcp('media.clear_watched',media_id=media['mediaFileId'],confirm='true')
        mcp('media.watch',context=identity,media_id=media['mediaFileId'],wait_ms=0)
        # Match the existing canonical-fixture commissioning workflow: reset
        # only this test source through public Seek before timing any tap.
        mcp('media.seek',context=identity,target_ms=0)
        page.wait_for_function("videoPlane.videoWidth>0&&(!videoPlane.paused||!document.querySelector('#autoplayBtn').hidden)",polling=100,timeout=45000)
        if page.locator('#autoplayBtn').is_visible():page.locator('#autoplayBtn').click()
        page.wait_for_function('videoPlane.videoWidth>0&&videoPlane.currentTime>.3&&!videoPlane.paused',polling=100,timeout=45000)
        # Enter VideoOSD only after the canonical source has settled; early
        # commands can be consumed by SageMC's still-loading main preview.
        if cursor_mode:
            page.wait_for_timeout(1000)
            if not page.evaluate('TEST_VIDEO_BOUNDS&&TEST_VIDEO_BOUNDS[2]>1150'):api('command',command=15)
            page.wait_for_function('TEST_VIDEO_BOUNDS&&TEST_VIDEO_BOUNDS[2]>1150',timeout=10000)
        else:api('command',command=15)
        page.wait_for_function("videoBounds.getBoundingClientRect().width>document.getElementById('stage').getBoundingClientRect().width*.9",timeout=10000)
        stv=mcp('captions.get',context=identity);assert stv.get('stvFile','').endswith('/'+('SageMC_Vibe.xml' if stv_mode=='sagemc' else 'SageTV7.xml')),stv
        page.wait_for_timeout(500)
        assert page.evaluate("videoBounds.getBoundingClientRect().width>document.getElementById('stage').getBoundingClientRect().width*.9"),'Full-screen geometry did not settle'
        print(json.dumps({'gate':'startup','nativeFramePacing':True}),flush=True)
        initial=snapshot();assert initial['pacing'].get('enabled') is True,initial
        for label,target in [('forward30',30),('forward60',60),('backward10',10)]:seek(label,target)
        # Hold the short canonical fixture under sustained native redraws.
        # Otherwise slower automation can reach its90s end-of-file dialog,
        # where the same coordinates are no longer an actual timeline tap.
        mcp('media.control',context=identity,operation='pause')
        page.wait_for_function('videoPlane.paused',timeout=10000)
        page.wait_for_timeout(500)
        held=page.locator('#videoPlane').evaluate('v=>v.currentTime')
        # Time Scroll is a toggle and SageMC may commit its old cursor when
        # repeated. Use supported repaint events, not seek commands, as load.
        for n in range(0 if cursor_mode else 90):
            api('repaint',x=0,y=0,width=1280,height=720);page.wait_for_timeout(500)
            if (n+1)%18==0:
                state=snapshot();assert state['queuedCommands']<4096 and state['frameQueueMs']<1500,state
                assert abs(page.locator('#videoPlane').evaluate('v=>v.currentTime')-held)<.1
                rows.append({'gate':'redraw-'+str((n+1)//2),'renderer':state,'paused':True})
                print(json.dumps({'steadySeconds':(n+1)//2,'queuedCommands':state['queuedCommands'],'frameQueueMs':state['frameQueueMs'],'pacing':state['pacing']}),flush=True)
        mcp('media.control',context=identity,operation='play')
        page.wait_for_function('t=>!videoPlane.paused&&videoPlane.currentTime>t+.3',arg=held,timeout=15000)
        if not cursor_mode:seek('post-animation20',20)
        final=snapshot()
        if not cursor_mode:assert final['pacing'].get('timeouts')==initial['pacing'].get('timeouts'),(initial,final)
        assert final['pacing'].get('acknowledged',0)>initial['pacing'].get('acknowledged',0)
        assert not errors,errors
        rows.append({'gate':'sustained-animation','initial':initial,'final':final,'passed':True})
        # Use public controls, preserving the normal server/client pause path.
        mcp('media.control',context=identity,operation='pause');page.wait_for_function('videoPlane.paused',timeout=10000)
        t=page.locator('#videoPlane').evaluate('v=>v.currentTime');page.wait_for_timeout(700)
        assert abs(page.locator('#videoPlane').evaluate('v=>v.currentTime')-t)<.1
        mcp('media.control',context=identity,operation='play');page.wait_for_function('t=>!videoPlane.paused&&videoPlane.currentTime>t+.3',arg=t,timeout=15000)
        rows.append({'gate':'pause-resume','passed':True})
        restore_stv()
        # Explicit Exit prevents foreground callbacks recreating this owned UI.
        page.locator('#remoteToggle').click();page.locator('#closeRemote').click();page.locator('#confirmClientExit').click()
        page.wait_for_function("!document.getElementById('clientExited').hidden",timeout=10000)
        passed=True
except Exception as error:
    failure=type(error).__name__+': '+str(error)
    if page:
        try:rows.append({'gate':'failure-state','renderer':snapshot(),'nativeConnection':api('status').get('connection'),'video':page.locator('#videoPlane').evaluate('v=>({time:v.currentTime,paused:v.paused,ended:v.ended,ready:v.readyState,width:v.videoWidth,error:v.error&&v.error.message})')})
        except Exception:pass
    raise
finally:
    if page and not passed:
        try:page.screenshot(path=str(OUT/(stamp+'-'+engine+'-timeline-failure.png')))
        except Exception:pass
    if owned:
        if borrowed_stock:
            try:
                restore_stv()
            except Exception as error:
                passed=False;failure=(failure or '')+'; STV restoration: '+type(error).__name__
        try:api('stop')
        except Exception:pass
    if context:
        try:context.close()
        except Exception:pass
    if browser:
        try:browser.close()
        except Exception:pass
    if pw:pw.stop()
    if owned:
        # Exact disconnected stock UI retirement may take over30s; only this
        # read-only observation gets90s, never readiness or replayed controls.
        deadline=time.monotonic()+90;retired=False;last_query_error=None
        while time.monotonic()<deadline:
            try:
                if identity not in mcp('ui.list').get('contexts',[]):retired=True;break
            except Exception as error:last_query_error=type(error).__name__
            # Only repeat this exact read-only observation, never Exit/Stop.
            time.sleep(.25)
        if not retired:
            passed=False;failure=(failure or '')+'; owned UI retirement unverified'+(' ('+last_query_error+')' if last_query_error else '')
    (OUT/(stamp+'-'+engine+'-timeline-result.json')).write_text(json.dumps({'passed':passed,'failure':failure,'stockServer':'.232','stv':stv_mode,'touch':touch_mode,'browser':engine,'physicalIPhone':False,'fixtureMediaId':media.get('mediaFileId') if 'media' in globals() else None,'rows':rows,'pageErrors':errors},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':passed,'browser':engine,'rows':len(rows)}),flush=True)
