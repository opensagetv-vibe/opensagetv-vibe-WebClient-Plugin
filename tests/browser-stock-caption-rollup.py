#!/usr/bin/env python3
"""WEB-034 focused real stock232 CEA playback/seek, not physical iPhone proof."""
import importlib.util,json,os,time,signal
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from urllib.request import urlopen
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
identity='da92a86446be';owned=None;page=None;passed=False;rows=[];errors=[]
OUT=Path(os.environ.get('SAGETV_ARTIFACT_DIR',ROOT/'artifacts/active/WEB-034'));OUT.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
experience=os.environ.get('SAGETV_EXPERIENCE_GATE')=='1'
abort_quality=os.environ.get('SAGETV_QUALITY_ABORT_GATE')=='1'
recover_quality=os.environ.get('SAGETV_QUALITY_RECOVERY_GATE')=='1'
source_preview=os.environ.get('SAGETV_SOURCE_PREVIEW_GATE')=='1'
service_gate=os.environ.get('SAGETV_CEA_SERVICE_GATE')=='1'
seek_target=0 if recover_quality else 30000

def video_state():
    # WebKit can suspend an inspection request as well as page timers. A
    # host deadline must bound that individual RPC, not just the outer loop.
    # This is a test-inspection failure, never proof of encoder slowness.
    def expired(signum,frame):raise TimeoutError('WebKit video inspection RPC stalled for10s')
    previous=signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,10)
    try:return page.evaluate("()=>({width:videoPlane.videoWidth,time:videoPlane.currentTime,paused:videoPlane.paused,prompt:!document.querySelector('#autoplayBtn').hidden,error:videoPlane.error&&videoPlane.error.code})")
    finally:signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,previous)

def advancing_video(allow_gesture=False):
    # play() can initially leave paused=false and reject asynchronously. Do
    # not test the Play button once in that gap, then wait forever for media
    # progress with the now-visible browser permission prompt untouched.
    # Read actual progress and the existing prompt together, with a host-clock
    # budget (headless WebKit can suspend its own page timer during autoplay).
    deadline=time.monotonic()+45;clicked=False;last={}
    while time.monotonic()<deadline:
        last=video_state()
        if last['width']>0 and last['time']>.3 and not last['paused']:return
        if allow_gesture and last['prompt'] and not clicked:
            page.locator('#autoplayBtn').click(timeout=3000);clicked=True
            print('ACTIVATION trusted Play click after visible autoplay rejection',flush=True)
        page.wait_for_timeout(100)
    raise AssertionError('Video did not advance within45s; actual browser state='+json.dumps(last))
def mcp(action,**values):return C.request(cfg,'/v1/control',dict(action=action,**values),mcp=True)
def preview_counts():
    with urlopen('http://'+cfg['address']+':31910/v1/capabilities',timeout=3) as response:
        state=json.load(response)['mimDirect']
    return {key:int(state[key]) for key in ('activeSessions','activePreviewLeases')}
def observed(response):
    global owned
    if '/api/miniclient' in response.url and response.request.method=='POST' and parse_qs(urlparse(response.url).query).get('action')==['start']:
        try:
            data=response.json()
            if data.get('session') and data.get('clientId','').replace(':','').lower()==identity:owned=data['session']
        except Exception:pass
try:
    state=C.activity(cfg);contexts=mcp('ui.list').get('contexts',[])
    assert state.get('recordingCount')==0 and state.get('connectedClientCount')==0
    assert not contexts or contexts==[identity],contexts
    if source_preview:assert preview_counts()=={'activeSessions':0,'activePreviewLeases':0}
    media=mcp('media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/VibeCaptionTest-1080i-CEA608-90s-2s.ts')
    assert media.get('mediaFileId'),media
    with sync_playwright() as pw:
        engine=os.environ.get('SAGETV_BROWSER_ENGINE','chromium')
        if engine not in ('chromium','webkit'):raise ValueError('Unsupported test browser')
        browser=(pw.webkit.launch(headless=True) if engine=='webkit' else
                 pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox']))
        context=browser.new_context(viewport={'width':852,'height':393},http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block')
        page=context.new_page();page.on('response',observed);page.on('pageerror',lambda e:errors.append(str(e)))
        authority={'mode':'stv' if service_gate else 'cc1','cc1Type':'cea608','cc1Language':'eng','cc1Service':1,'cc2Type':'cea608','cc2Service':2}
        page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebCaptionAuthority.v1',JSON.stringify("+json.dumps(authority)+"));localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify({player:'hls',videoMode:'transcode',videoKbps:1000,resolution:'480',deinterlace:'on'}));")
        if source_preview:page.add_init_script("localStorage.setItem('sagetvWebMiniClientSettings.v1',JSON.stringify({scrubPreviews:true}));")
        page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
        page.wait_for_function("document.querySelector('#connectionStatus').textContent.toLowerCase().startsWith('connected')",timeout=60000)
        for _ in range(100):
            if owned:break
            page.wait_for_timeout(100)
        assert owned
        for _ in range(60):
            if identity in mcp('ui.list').get('contexts',[]):break
            page.wait_for_timeout(500)
        else:raise AssertionError('Real stock UI registration did not complete')
        for _ in range(90):
            native=C.request(cfg,'/SageTVWebPlayer/api/miniclient?action=status&session='+owned)
            if native.get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'):break
            page.wait_for_timeout(300)
        else:raise AssertionError('Real stock first native frame did not complete')
        # Reset only this canonical synthetic fixture; a retained resume point
        # can otherwise confound the fresh startup and seek-generation gates.
        mcp('media.clear_watched',media_id=media['mediaFileId'],confirm='true')
        mcp('media.watch',context=identity,media_id=media['mediaFileId'],wait_ms=0)
        mcp('media.seek',context=identity,target_ms=0)
        if service_gate:
            assert mcp('captions.set',context=identity,state='CC1').get('ok'),'Public CC1 selection rejected'
        print('READY canonical Watch/Seek; checking browser user-gesture requirement',flush=True)
        for label,target in [('startup',None),('seek0s' if recover_quality else 'seek30s',seek_target)]:
            if target is not None:
                old_source=page.locator('#videoPlane').evaluate('v=>v.currentSrc')
                if experience:
                    # Real production range handlers; no fake native cursor or
                    # test-only timeline implementation.
                    page.locator('#seekRange').evaluate("(el,target)=>{el.value=String(target/1000);el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));}",target)
                    page.wait_for_function("document.querySelector('#timelinePhase').textContent.startsWith('presented')",timeout=90000)
                else:
                    reply=mcp('media.seek',context=identity,target_ms=target)
                    assert reply.get('ok'),reply
                # Do not accept advancing video/captions from the old source
                # while the normal seek is still creating its HLS generation.
                page.wait_for_function("old=>videoPlane.currentSrc!==old&&videoPlane.readyState>=2",arg=old_source,timeout=90000)
            advancing_video(allow_gesture=target is None)
            page.wait_for_function("(()=>{const e=document.querySelector('.caption-cea-grid');return e&&e.textContent.trim().length>0&&e.getBoundingClientRect().width>0})()",timeout=25000)
            if target is not None:
                cue='00:00:00' if target==0 else '00:00:30'
                page.wait_for_function("cue=>document.querySelector('.caption-cea-grid').textContent.includes(cue)",arg=cue,timeout=15000)
            # Character-rate replaceChildren can retire an ElementHandle
            # between separate protocol calls. Resolve and inspect atomically.
            evidence=page.evaluate("()=>{const e=document.querySelector('.caption-cea-grid'),r=e.getBoundingClientRect(),s=getComputedStyle(e);return{text:e.textContent,x:r.x,y:r.y,width:r.width,height:r.height,align:s.textAlign,whiteSpace:s.whiteSpace}}")
            assert evidence['align']=='left' and evidence['whiteSpace']=='pre',evidence
            assert evidence['x']>=0 and evidence['x']+evidence['width']<=853,evidence
            v=page.locator('#videoPlane').evaluate('v=>({time:v.currentTime,width:v.videoWidth,height:v.videoHeight})')
            page.wait_for_timeout(1000);assert page.locator('#videoPlane').evaluate('v=>v.currentTime')>v['time']
            rows.append({'gate':label,'caption':evidence,'video':v,'passed':True})
            page.screenshot(path=str(OUT/f'{stamp}-stock-{label}.png'))
            print('PASS real stock232',label,'CEA fixed-width captions over advancing transcoded video',flush=True)
        if service_gate:
            before=C.request(cfg,'/SageTVWebPlayer/api/miniclient?action=streamSettings&session='+owned)
            source=page.locator('#videoPlane').evaluate('v=>v.currentSrc')
            for state,visible in [('CC2',False),('CC1',True),('Off',False)]:
                assert mcp('captions.set',context=identity,state=state).get('ok'),'Public caption selection rejected'
                page.wait_for_function("visible=>!!document.querySelector('#localCaptions').textContent.trim()===visible",arg=visible,timeout=10000)
                current=C.request(cfg,'/SageTVWebPlayer/api/miniclient?action=streamSettings&session='+owned)
                assert current.get('session')==before.get('session'),'Caption switch restarted A/V producer'
                assert page.locator('#videoPlane').evaluate('v=>v.currentSrc')==source,'Caption switch replaced video source'
                assert mcp('captions.get',context=identity).get('state')==state,'Public caption state not confirmed'
                rows.append({'gate':'actual-service-'+state,'passed':True,'visible':visible,'sameProducerAndVideo':True})
                print('PASS real stock232 caption service '+state+' visibility without A/V replacement',flush=True)
        active=C.request(cfg,'/SageTVWebPlayer/api/miniclient?action=streamSettings&session='+owned)
        status=C.request(cfg,'/SageTVWebPlayer/api/hls?session='+active['session'])
        assert all(status.get(k) for k in ('hardware','hardwareDecode','hardwareFilters')) and status.get('encoder')=='h264_qsv',status.get('encoder')
        assert status.get('sourceProbeCacheHit') is True,'Completed-source seek should reuse proven metadata'
        rows.append({'gate':'seek-producer','passed':True,'producer':{k:status.get(k) for k in
            ['encoder','hardware','hardwareDecode','hardwareFilters','sourceProbeMs','sourceProbeCacheHit']}})
        if source_preview:
            before=C.request(cfg,'/SageTVWebPlayer/api/miniclient?action=playbackState&session='+owned)
            page.locator('#remoteToggle').click();page.locator('#remoteHelp').click()
            with page.expect_response(lambda r:'/api/miniclient' in r.url and parse_qs(urlparse(r.url).query).get('action')==['sourcePreview'],timeout=15000) as image_response:
                page.locator('#seekRange').evaluate("el=>{el.value='40';el.dispatchEvent(new Event('input',{bubbles:true}));}")
            reply=image_response.value
            assert reply.status==200,'Actual shared preview unavailable: HTTP'+str(reply.status)
            assert reply.headers.get('x-vibe-preview-position-ms')=='40000'
            assert 4<=len(reply.body())<=32768
            page.wait_for_function("!document.querySelector('#timelinePreview').hidden&&document.querySelector('#timelinePreviewImage').naturalWidth===192",timeout=10000)
            assert 'Source preview at' in page.locator('#timelinePreviewLabel').text_content()
            after=C.request(cfg,'/SageTVWebPlayer/api/miniclient?action=playbackState&session='+owned)
            assert before['producer']==after['producer'] and before['source']==after['source'] and before['requestedPositionMs']==after['requestedPositionMs']
            counts=preview_counts();assert counts=={'activeSessions':0,'activePreviewLeases':1},counts
            page.locator('#timelinePreviewLabel').scroll_into_view_if_needed()
            page.screenshot(path=str(OUT/f'{stamp}-stock-source-preview.png'))
            page.locator('#timelineCancel').click();page.locator('#closeRemoteTools').click();page.locator('#hideRemote').click()
            rows.append({'gate':'shared-source-preview-no-playback-seek-or-extra-stream','passed':True,'actualBucketMs':40000,
                'imageWidth':192,'imageHeight':108,'bytes':len(reply.body()),'provider':counts,'fullGpuPlaybackRetained':True})
            print('PASS real shared MIM source image, original GPU playback/captions/source retained, zero extra playback producers',flush=True)
        if experience:
            api=lambda action,**v:C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action=action,session=owned,**v))
            observed=api('playbackState')
            assert observed['requestedPositionMs']==seek_target and observed['acceptedPositionMs']==seek_target,observed
            assert observed['displayedPositionMs'] is not None and observed['displayedPositionMs']>=seek_target,observed
            configured=active['configured'];saved=page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')")
            old_source=page.locator('#videoPlane').evaluate('v=>v.currentSrc')
            old_position=page.locator('#videoPlane').evaluate('v=>v.currentTime')
            if abort_quality:
                # Withhold only the candidate's presented ACK, then explicitly
                # cancel it. Actual media still decodes; this proves rollback,
                # not a spontaneous network/decoder failure or physical phone.
                def withhold_ack(route):
                    request=route.request
                    if parse_qs(urlparse(request.url).query).get('action')==['state']:
                        fields=parse_qs(request.post_data or '',keep_blank_values=True)
                        if fields.get('expectedHlsSession')!=[active['session']]:
                            fields.pop('presentedTimeMs',None)
                            from urllib.parse import urlencode
                            route.continue_(post_data=urlencode(fields,doseq=True));return
                    route.continue_()
                page.route('**/api/miniclient?**',withhold_ack)
            # Explicit synthetic recommendation exercises the PRODUCTION
            # browser consumer (not fabricated WAN throughput). Actual frame
            # callbacks/state reports must commit its server-owned handoff.
            # The real controller is deliberately closure-private. Stimulate
            # its exported policy class, then click its production DOM action;
            # do not expose controller internals just to automate this test.
            page.evaluate("""()=>{const policy=SageMiniExperience.QualityAdvisor.prototype,original=policy.observe;
                policy.observe=function(sample){if(!this.applied){this.recommendation={videoKbps:700,resolution:'480',reason:'Explicit commissioning stimulus, not measured WAN'};return this.recommendation;}return original.call(this,sample);};}""")
            page.wait_for_function("!document.querySelector('#applyQualityRecommendation').disabled",timeout=10000)
            with page.expect_response(lambda r:'/api/miniclient' in r.url and parse_qs(urlparse(r.url).query).get('action')==['qualityPrepare'],timeout=45000) as prepared:
                page.locator('#applyQualityRecommendation').evaluate('el=>el.click()')
            reduction=prepared.value.json()
            assert reduction.get('session')!=active['session'] and reduction['configured']==configured,reduction
            page.wait_for_function("old=>videoPlane.currentSrc!==old&&videoPlane.readyState>=2&&videoPlane.currentTime>.3",arg=old_source,timeout=90000)
            page.wait_for_function("document.querySelector('.caption-cea-grid')&&document.querySelector('.caption-cea-grid').textContent.trim().length>0",timeout=20000)
            reduced=C.request(cfg,'/SageTVWebPlayer/api/hls?session='+reduction['session'])
            assert reduced['streamSettings']['effective']['videoTargetKbps']==700,reduced['streamSettings']
            assert all(reduced.get(k) for k in ('hardware','hardwareDecode','hardwareFilters')),reduced.get('encoder')
            deadline=time.monotonic()+10;handoff={}
            if abort_quality:
                before_abort=api('playbackState')
                assert before_abort['qualityHandoff']=='waiting-for-presentation',before_abort
                with page.expect_request(lambda r:('/hls/'+active['session']+'/stream.m3u8') in r.url,timeout=15000):
                    assert api('qualityAbort',expectedHlsSession=reduction['session'])['ok'] is True
                # MSE creates a NEW blob URL even for the original playlist.
                # Its local time is relative to the30s source anchor, not30s.
                page.wait_for_function('old=>videoPlane.readyState>=2&&!videoPlane.paused&&videoPlane.currentTime>=old-.25',arg=old_position,timeout=30000)
                page.wait_for_function("document.querySelector('.caption-cea-grid')&&document.querySelector('.caption-cea-grid').textContent.trim().length>0",timeout=15000)
                handoff=api('playbackState')
                assert handoff['producer']==active['session'] and handoff['qualityHandoff']=='client-aborted',handoff
                assert api('qualityAbort',expectedHlsSession=reduction['session'])['stale'] is True
                assert page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')")==saved
                rows.append({'gate':'quality-abort-restores-original','passed':True,'state':handoff,'candidateAcknowledgementDeliberatelyWithheld':True,'captionsVisible':True,'browserSavedUnchanged':True})
                print('PASS real stock232 explicit candidate abort restores original video/captions/position',flush=True)
            while time.monotonic()<deadline:
                if abort_quality:break
                handoff=api('playbackState')
                if handoff.get('qualityHandoff')=='presented':break
                page.wait_for_timeout(200)
            if not abort_quality:
                assert handoff.get('qualityHandoff')=='presented' and handoff.get('displayedPositionMs') is not None,handoff
                assert handoff['producer']==reduction['session']
            assert page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')")==saved
            retired=reduction['session'] if abort_quality else active['session']
            assert api('qualityPrepare',expectedHlsSession=retired,timeMs=30000,videoKbps=500,height=480).get('stale') is True
            if not abort_quality:rows.append({'gate':'local-timeline-and-session-quality','passed':True,'state':observed,
                'effectiveVideoKbps':700,'configuredUnchanged':True,'browserSavedUnchanged':True,'retiredProducerRejected':True,
                'recommendation':'synthetic explicit stimulus, not measured WAN','handoff':handoff,'actualFrameAcknowledgement':True})
            if not abort_quality:print('PASS real stock232 browser-consumer quality swap, actual presented ACK, captions/full GPU, settings preserved',flush=True)
            if recover_quality:
                print('WAIT existing60s quality cooldown; same90s fixture stays advancing',flush=True)
                # No bypass of the production server/client cooldown. This
                # optional longer gate starts at zero to retain enough media.
                for _ in range(61):page.wait_for_timeout(1000)
                previous=reduction['session']
                page.evaluate("""()=>{const policy=SageMiniExperience.QualityAdvisor.prototype,original=policy.observe;
                    policy.observe=function(sample){if(this.applied===1){this.recommendation={videoKbps:900,resolution:'480',reason:'Explicit recovery stimulus, not measured WAN'};return this.recommendation;}return original.call(this,sample);};}""")
                page.wait_for_function("!document.querySelector('#applyQualityRecommendation').disabled",timeout=10000)
                with page.expect_response(lambda r:'/api/miniclient' in r.url and parse_qs(urlparse(r.url).query).get('action')==['qualityPrepare'],timeout=45000) as recovered:
                    page.locator('#applyQualityRecommendation').evaluate('el=>el.click()')
                recovery=recovered.value.json()
                assert recovery.get('session') not in (None,previous),recovery
                deadline=time.monotonic()+20
                while time.monotonic()<deadline:
                    restored=api('playbackState')
                    if restored['producer']==recovery['session'] and restored['qualityHandoff']=='presented':break
                    page.wait_for_timeout(200)
                else:raise AssertionError('No actual recovery presentation: '+json.dumps(restored))
                producer=C.request(cfg,'/SageTVWebPlayer/api/hls?session='+recovery['session'])
                assert producer['streamSettings']['effective']['videoTargetKbps']==900
                assert all(producer.get(k) for k in ('hardware','hardwareDecode','hardwareFilters'))
                assert page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')")==saved
                page.wait_for_function("document.querySelector('.caption-cea-grid')&&document.querySelector('.caption-cea-grid').textContent.trim().length>0",timeout=10000)
                rows.append({'gate':'quality-recovery-within-saved-ceiling','passed':True,'effectiveVideoKbps':900,'savedCeilingKbps':1000,'actualFrameAcknowledgement':True,'state':restored,'fullGpu':True,'captionsVisible':True,'configuredUnchanged':recovery['configured']==configured,'browserSavedUnchanged':True,'recommendation':'synthetic explicit stimulus, not measured WAN'})
                print('PASS real stock232700->900 recovery after cooldown, actual frame ACK/CEA/full GPU, saved ceiling intact',flush=True)
        mcp('media.control',context=identity,operation='pause')
        page.wait_for_function('videoPlane.paused',timeout=10000)
        paused=page.locator('#videoPlane').evaluate('v=>v.currentTime')
        page.wait_for_timeout(700)
        assert abs(page.locator('#videoPlane').evaluate('v=>v.currentTime')-paused)<.1
        mcp('media.control',context=identity,operation='play')
        page.wait_for_function('anchor=>!videoPlane.paused&&videoPlane.currentTime>anchor+.3',arg=paused,timeout=15000)
        rows.append({'gate':'pause-resume','passed':True})
        print('PASS real stock232 pause hold/resume after captioned seek',flush=True)
        assert not errors,errors
        passed=True;context.close();browser.close()
finally:
    if page and not passed and page.context.browser.is_connected():
        try:page.screenshot(path=str(OUT/f'{stamp}-stock-failure.png'))
        except Exception:pass
    if owned:
        try:C.request(cfg,'/SageTVWebPlayer/api/miniclient',{'action':'stop','session':owned})
        except Exception:pass
    if source_preview:
        try:
            deadline=time.monotonic()+90
            while True:
                final_activity=C.activity(cfg);final_counts=preview_counts()
                if final_activity.get('safeToRestart') is True and final_counts=={'activeSessions':0,'activePreviewLeases':0}:break
                if time.monotonic()>=deadline:raise RuntimeError('Owned source-preview/session retirement not proven')
                time.sleep(.5)
            rows.append({'gate':'independent-final-activity-preview-retirement','passed':True,'activity':final_activity,'provider':final_counts})
        except Exception as cleanup_error:
            passed=False;rows.append({'gate':'independent-final-activity-preview-retirement','passed':False,'error':type(cleanup_error).__name__})
    (OUT/f'{stamp}-stock-caption-rollup.json').write_text(json.dumps({'passed':passed,'realStock232':True,'engine':os.environ.get('SAGETV_BROWSER_ENGINE','chromium'),'physicalPhone':False,'fixture':'canonical90s/2s CEA608','rows':rows,'pageErrors':errors},indent=2)+'\n')
