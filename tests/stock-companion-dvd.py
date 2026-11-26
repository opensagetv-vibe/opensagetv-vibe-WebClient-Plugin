#!/usr/bin/env python3
"""WEB-055 real stock232 optional navigator gate; not physical iPhone proof."""
import importlib.util
import json
import os
import time
from urllib.parse import parse_qs,urlparse
from urllib.error import URLError
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
identity='da92a86446be';owned=None;page=None;passed=False;rows=[];borrowed=[];hook=False;errors=[];cleanup=[]
bookmark_fingerprint=None;bookmark_pending=False;wire_commands=[];subtitle_observations=[];subtitle_borrowed=False;state_observation={}
OUT=Path(os.environ.get('SAGETV_ARTIFACT_DIR',ROOT/'artifacts/active/WEB-055')).resolve()
if not OUT.is_relative_to((ROOT/'artifacts/active').resolve()):raise SystemExit('Output must stay in active task artifacts')
OUT.mkdir(parents=True,exist_ok=True);stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())

def mcp(action,**values):
    # A transient TCP-connect timeout is not DVD playback evidence. Only
    # exact read-only observations may be retried; controls remain one-shot.
    read_only=action in ('ui.state','ui.list','server.activity','companion.config_get','companion.dvd_bookmark') or (action=='companion.dvd_hook' and 'enabled' not in values)
    for attempt in range(3 if read_only else 1):
        try:return C.request(cfg,'/v1/control',dict(action=action,**values),mcp=True,timeout=5 if read_only else 20)
        except (TimeoutError,URLError):
            if not read_only or attempt==2:raise
            print('Transient read-only MCP observation unavailable: '+action,flush=True)
def api(action,**values):return C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action=action,session=owned,**values))
def record(name,**values):rows.append(dict(gate=name,passed=True,**values));print('PASS '+name,flush=True)
def observe(response):
    global owned
    if '/api/subtitles' in response.url:
        try:
            value=response.json();spu=value.get('dvdSpu')
            if value.get('scope')=='dvd' and isinstance(spu,dict):
                row={k:spu.get(k) for k in ('selected','decoded','cues','clears','malformed')}
                row.update(queue=value.get('queue'),requestTimeMs=parse_qs(urlparse(response.url).query).get('timeMs',[''])[0],
                           deliveredBitmaps=sum(bool(c.get('data')) for c in value.get('cues',[])))
                subtitle_observations.append(row)
                del subtitle_observations[:-20]
        except Exception:pass
    if '/api/miniclient' not in response.url or response.request.method!='POST':return
    try:
        params=parse_qs(urlparse(response.url).query)
        params.update(parse_qs(response.request.post_data or ''))
        if params.get('action')==['command'] and params.get('command'):
            wire_commands.append(int(params['command'][0]))
        value=response.json()
        if params.get('action')==['state'] and isinstance(value.get('dvdMenu'),bool):
            state_observation.update(dvdMenu=value['dvdMenu'],at=time.monotonic())
        if value.get('session') and value.get('clientId','').replace(':','').lower()==identity:owned=value['session']
    except Exception:pass

def observe_report(request):
    if '/api/support' not in request.url or request.method!='POST':return
    try:
        report=json.loads(parse_qs(request.post_data or '').get('browserJson',['{}'])[0])
        print(json.dumps({'inputFailureDiagnostic':{'layout':report.get('videoLayout'),'ui':{k:report.get('ui',{}).get(k) for k in ('menuHint','frame','gfxCount','renderQueued')},
              'dvdMenuState':report.get('diagnostics',{}).get('dvdMenuState'),'dvdMenuStateAt':report.get('diagnostics',{}).get('dvdMenuStateAt'),
              'nativeRecoveryCount':report.get('nativeRecoveryCount'),'reason':(report.get('failureSnapshot') or {}).get('reason')}}),flush=True)
    except Exception:pass
def change(key,value):
    before=mcp('companion.config_get',setting=key)['value']
    if before==value:return
    mcp('companion.config_set',setting=key,expected=before,value=value,confirm='true')
    borrowed.append((key,before,value))

def natural_eof_menu(label):
    # Observe natural completion, not a replayed Menu/Seek or an old still.
    page.evaluate("()=>{const s=window.DVD_EOF_FIELD={source:videoPlane.currentSrc,frames:0,done:false};const f=(n,m)=>{if(s.done)return;if(videoPlane.currentSrc!==s.source)s.frames++;videoPlane.requestVideoFrameCallback(f);};videoPlane.requestVideoFrameCallback(f);}")
    try:
        def returned():
            n=mcp('ui.state',context=identity)
            v=page.evaluate("()=>{const c=dvdSpuCanvas,p=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let pixels=0;for(let i=3;i<p.length;i+=4)if(p[i])pixels++;return{changed:videoPlane.currentSrc!==DVD_EOF_FIELD.source,frames:DVD_EOF_FIELD.frames,width:videoPlane.videoWidth,ready:videoPlane.readyState,pixels,message:osdMessage.textContent};}")
            return n.get('dvdMenu') is True and v['changed'] and v['frames']>0 and v['width']>0 and v['ready']>=2 and v['pixels']>100 and not v['message']
        wait_until(returned,label,135)
        dvd=api('status').get('connection',{}).get('dvd',{})
        record(label,generation=dvd.get('generation'),continuations=dvd.get('continuations'),terminalEosAcks=dvd.get('terminalEosAcks'),naturalCompletion=True)
    finally:page.evaluate("()=>{if(window.DVD_EOF_FIELD)DVD_EOF_FIELD.done=true;delete window.DVD_EOF_FIELD;}")
def wait_until(predicate,label,seconds=30):
    deadline=time.monotonic()+seconds
    while time.monotonic()<deadline:
        if predicate():return
        # Sync Playwright dispatches response/page callbacks only while its
        # event loop is pumped. A host sleep plus an owned=None short circuit
        # cannot discover the start response even though the page connected.
        page.wait_for_timeout(200)
    if page:
        page.screenshot(path=str(OUT/(stamp+'-companion-dvd-failure.png')))
        if label=='production key arms native Time Scroll':
            page.locator('#settingsToggle').click();page.locator('#settings-tab-diagnostics').click()
            with page.expect_download(timeout=20000):page.locator('#downloadReport').click()
    raise AssertionError('Timed out: '+label)
try:
    activity=C.activity(cfg);contexts=mcp('ui.list').get('contexts',[])
    assert activity.get('recordingCount')==0 and activity.get('connectedClientCount')==0 and (not contexts or contexts==[identity]),'Independent recording/client guard rejected test'
    media=mcp('media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/OpenSageTV_Vibe_Test_DVD')
    assert media.get('mediaFileId'),'Canonical authored DVD missing'
    with sync_playwright() as pw:
        engine=os.environ.get('SAGETV_BROWSER_ENGINE','chromium')
        if engine not in ('chromium','webkit'):raise ValueError('Unsupported test browser')
        browser=(pw.webkit.launch(headless=True) if engine=='webkit' else
                 pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox']))
        context=browser.new_context(viewport={'width':852,'height':393},http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block')
        page=context.new_page();page.on('response',observe);page.on('request',observe_report);page.on('pageerror',lambda e:errors.append(str(e)))
        # Transparent, bounded observation of native menu hints. Do not expose
        # private JS closure state or inject a fake fullscreen/menu context.
        page.add_init_script(r"""(()=>{window.DVD_NATIVE_HINTS=[];const original=ReadableStreamDefaultReader.prototype.read,states=new WeakMap();
          ReadableStreamDefaultReader.prototype.read=async function(...args){const r=await original.apply(this,args);if(r.value){
            let s=states.get(this);if(!s){s={decoder:new TextDecoder(),pending:''};states.set(this,s);}s.pending+=s.decoder.decode(r.value,{stream:true});
            if(s.pending.length>1048576)s.pending='';let i;while((i=s.pending.indexOf('\n'))>=0){const line=s.pending.slice(0,i);s.pending=s.pending.slice(i+1);
              try{const e=JSON.parse(line);if(e.type==='menuHint'){DVD_NATIVE_HINTS.push(String(e.value).slice(0,256));if(DVD_NATIVE_HINTS.length>16)DVD_NATIVE_HINTS.shift();}}catch(_){}}}return r;};})()""")
        page.add_init_script("""localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');
          localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify({player:'hls',videoMode:'transcode',videoKbps:1200,resolution:'480',deinterlace:'on',companionDvd:true}));""")
        page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
        wait_until(lambda:owned is not None and identity in mcp('ui.list').get('contexts',[]),'owned native registration')
        wait_until(lambda:api('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'),'first native frame')
        contracts=api('status').get('connection',{}).get('capabilities',{}).get('extensionContracts',{})
        assert contracts.get('schemaVersion')==1 and contracts.get('modifiedCoreRequired') is False,'Current stock-contract candidate not loaded'
        assert contracts.get('transformedMainFeature') is False and contracts.get('privateMediaStateUrl') is False,'False private Core capability'
        record('installed-stock-contract-diagnostics',contracts=contracts)
        before_hook=mcp('companion.dvd_hook',context=identity)
        assert before_hook['playerClass']=='','Refuse replacing a previous DVD player'
        for key,value in [('enabled','true'),('dvd.owned_navigation','true'),('dvd.client_controls','true'),('dvd.owned_mode','copy')]:change(key,value)
        selected=mcp('companion.dvd_hook',context=identity,expected='',enabled='true',confirm='true')
        assert selected.get('ownedNavigatorSelected');hook=True
        if os.environ.get('SAGETV_DVD_BOOKMARK_GATE')=='1':
            checkpoint=mcp('companion.dvd_bookmark',context=identity)
            assert checkpoint.get('present') is False,'Preserve pre-existing UI bookmark; refuse save/clear test'
            record('read-only-proof-no-preexisting-owned-bookmark')
        saved=page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')")
        mcp('media.watch',context=identity,media_id=media['mediaFileId'],wait_ms=0)
        wait_until(lambda:'ready-native-ps' in page.locator('#dvdCompanionStatus').text_content(),'explicit browser-native profile',45)
        record('negotiated-revision4-native-program-stream',configuredServerMode='copy',browserProfile='web-mpegps-v1')
        wait_until(lambda:page.evaluate("()=>videoPlane.videoWidth>0||!document.querySelector('#dvdStillFrame').hidden"),'DVD decoded background',60)
        wait_until(lambda:mcp('ui.state',context=identity).get('dvd') is True,'stock DVD load state')
        native=mcp('ui.state',context=identity)
        # SageMC may correctly restore its own last watched position from an
        # earlier gate. Request the authored menu once, rather than wiping
        # watched metadata or assuming that every Watch must open a menu.
        requested_menu=not native.get('dvdMenu')
        if requested_menu:assert api('command',command=67).get('ok') is True
        wait_until(lambda:mcp('ui.state',context=identity).get('dvdMenu') is True,'authored menu selected')
        page.screenshot(path=str(OUT/(stamp+'-companion-dvd-menu.png')))
        record('owned-authored-menu-background-and-native-menu-state',explicitMenuRequested=requested_menu)
        # Use the actual production button handlers, not MCP DVD actions.
        page.locator('#settingsToggle').click()
        page.locator('#settings-tab-playback').click()
        button=page.locator('[data-companion-dvd="beginning"]')
        assert button.is_enabled(),'Current owned controls unavailable'
        menu_source=page.locator('#videoPlane').evaluate('v=>v.currentSrc')
        button.click()
        wait_until(lambda:'accepted' in page.locator('#dvdCompanionStatus').text_content().lower(),'explicit beginning receipt')
        record('production-beginning-button-current-load-receipt')
        if os.environ.get('SAGETV_DVD_FEATURE_GATE')=='1':
            # Receipt alone is not playback. Observe the actual authored title
            # and decoded frames before qualifying the optional action.
            wait_until(lambda:mcp('ui.state',context=identity).get('dvdMenu') is False,'feature leaves authored menu',45)
            page.locator('#closeSettings').click()
            def moving():
                if page.locator('#autoplayBtn').is_visible():page.locator('#autoplayBtn').click()
                return page.locator('#videoPlane').evaluate('v=>v.videoWidth>0&&v.currentTime>.3&&!v.paused')
            witness={'source':None,'time':0}
            def feature_advancing():
                if page.locator('#autoplayBtn').is_visible():page.locator('#autoplayBtn').click()
                shown=page.locator('#videoPlane').evaluate('v=>({source:v.currentSrc,time:v.currentTime,width:v.videoWidth,paused:v.paused,ready:v.readyState})')
                # A menu can still be decoded while title navigation has
                # already completed. Never compare its clock with a fresh
                # feature/cell whose local epoch legitimately restarts at0.
                if not shown['source'] or shown['source']==menu_source:return False
                if shown['source']!=witness['source']:
                    witness.update(source=shown['source'],time=shown['time']);return False
                return shown['width']>0 and shown['ready']>=2 and not shown['paused'] and shown['time']>witness['time']+.3
            wait_until(feature_advancing,'actual advancing feature in its new generation',60)
            feature=mcp('ui.state',context=identity)
            assert feature.get('dvdTitle',0)>0 and feature.get('dvdChapter',0)>0,feature
            record('actual-authored-title-chapter-and-advancing-feature',title=feature['dvdTitle'],chapter=feature['dvdChapter'],newSourceGenerationProven=True)
            if os.environ.get('SAGETV_DVD_EOF_GATE')=='1':natural_eof_menu('owned-natural-feature-eof-new-menu-picture')
            if os.environ.get('SAGETV_DVD_CHAPTER_GATE')=='1':
                previous=page.locator('#videoPlane').evaluate('v=>v.currentSrc')
                assert api('command',command=65).get('ok') is True
                wait_until(lambda:mcp('ui.state',context=identity).get('dvdChapter')!=feature['dvdChapter'],'native next chapter',30)
                following=mcp('ui.state',context=identity)
                assert following.get('dvdChapter',0)>0 and following.get('dvdMenu') is False,following
                wait_until(lambda:page.locator('#videoPlane').evaluate('old=>videoPlane.currentSrc!==old&&videoPlane.videoWidth>0&&videoPlane.readyState>=2',previous),'chapter replacement picture',60)
                wait_until(moving,'advancing next chapter',30)
                record('native-chapter-replacement-and-advancing-video',previousChapter=feature['dvdChapter'],currentChapter=following['dvdChapter'])
            if os.environ.get('SAGETV_DVD_BOOKMARK_GATE')=='1':
                # Use real production buttons, only after the exact connected
                # synthetic UI's bookmark is independently proven absent.
                page.locator('#settingsToggle').click();page.locator('#settings-tab-playback').click()
                bookmark_pending=True
                page.locator('[data-companion-dvd="save_resume"]').click()
                wait_until(lambda:mcp('companion.dvd_bookmark',context=identity).get('present') is True,'saved bookmark readback')
                checkpoint=mcp('companion.dvd_bookmark',context=identity)
                assert checkpoint.get('valid') is True and checkpoint.get('positionMs',0)>1000,checkpoint
                bookmark_fingerprint=checkpoint['fingerprint'];saved_position=checkpoint['positionMs']
                record('production-save-current-title-and-position',title=checkpoint['title'],positionMs=saved_position)
                old_source=page.locator('#videoPlane').evaluate('v=>v.currentSrc')
                page.locator('[data-companion-dvd="beginning"]').click()
                page.locator('#closeSettings').click()
                wait_until(lambda:page.locator('#videoPlane').evaluate('old=>{const v=videoPlane;return v.currentSrc!==old&&v.videoWidth>0&&v.currentTime>.3&&!v.paused}',old_source),'beginning replacement picture',60)
                wait_until(lambda:mcp('ui.state',context=identity).get('mediaTimeMs',saved_position)<saved_position-2000,'beginning moves before saved bookmark',30)
                page.locator('#settingsToggle').click();page.locator('#settings-tab-playback').click()
                old_source=page.locator('#videoPlane').evaluate('v=>v.currentSrc')
                page.locator('[data-companion-dvd="resume"]').click();page.locator('#closeSettings').click()
                wait_until(lambda:page.locator('#videoPlane').evaluate('old=>videoPlane.currentSrc!==old&&videoPlane.videoWidth>0&&videoPlane.readyState>=2',old_source),'resume replacement decoded picture',60)
                wait_until(moving,'resumed advancing video',30)
                # A replacement can decode while the ordered stock DVD clock
                # is still at the just-freed beginning load. Observe the
                # saved-title clock within the existing bounded control gate,
                # not a one-sample assertion or a replayed resume request.
                def resumed_clock():
                    state=mcp('ui.state',context=identity)
                    return state.get('dvdTitle')==checkpoint['title'] and abs(state.get('mediaTimeMs',-999999)-saved_position)<8000
                wait_until(resumed_clock,'native saved-title clock after resume',30)
                restored=mcp('ui.state',context=identity)
                assert restored.get('dvdTitle')==checkpoint['title'] and abs(restored.get('mediaTimeMs',-999999)-saved_position)<8000,{'savedMs':saved_position,'actualMs':restored.get('mediaTimeMs')}
                record('production-resume-advancing-saved-title-position',savedMs=saved_position,actualMs=restored['mediaTimeMs'],approximateDvdLanding=True)
                assert mcp('companion.dvd_bookmark',context=identity)['fingerprint']==bookmark_fingerprint,'Concurrent bookmark change; preserve it'
                page.locator('#settingsToggle').click();page.locator('#settings-tab-playback').click()
                page.locator('[data-companion-dvd="clear_resume"]').click()
                wait_until(lambda:mcp('companion.dvd_bookmark',context=identity).get('present') is False,'original absence restored')
                bookmark_fingerprint=None;bookmark_pending=False;record('production-clear-restores-original-bookmark-absence')
                page.locator('#closeSettings').click()
            if os.environ.get('SAGETV_DVD_SEEK_GATE')=='1':
                # TV opens SageMC's real VideoOSD; Full Screen On is not
                # implemented by every STV. Observe its actual native bounds.
                assert api('command',command=15).get('ok') is True
                wait_until(lambda:page.evaluate("()=>videoBounds.getBoundingClientRect().width>stage.getBoundingClientRect().width*.9"),'native fullscreen video bounds',15)
                wait_until(lambda:mcp('ui.state',context=identity).get('dvdMenu') is False,'native feature still selected')
                # A Core read is not proof the production browser has received
                # the new generation's menu state. Do not send the key during
                # its deliberately fail-safe stale/unknown-state interval.
                wait_until(lambda:state_observation.get('dvdMenu') is False and time.monotonic()-state_observation.get('at',0)<1.2,'fresh production browser DVD state',15)
                prior=mcp('ui.state',context=identity)['mediaTimeMs']
                assert prior>10000,'Require playing chapter beyond the rewind destination'
                prior_source=page.locator('#videoPlane').evaluate('v=>v.currentSrc')
                mark=len(wire_commands)
                if os.environ.get('SAGETV_DVD_INPUT_PROBE')=='1':
                    assert engine=='chromium','Read-only debugger probe is Chrome-only, never acceptance evidence'
                    probe=context.new_cdp_session(page);probe.send('Debugger.enable')
                    def paused(event):
                        frame=event['callFrames'][0]['callFrameId']
                        result=probe.send('Debugger.evaluateOnCallFrame',{'callFrameId':frame,'expression':'JSON.stringify({context:inputContext(),suspended:videoPresentationSuspended,presentation:videoPresentation.kind,dvd:playback.dvd,hasPlayback:!!playback.id,menuHint:currentMenuHint,dvdMenuState,stateAge:Date.now()-dvdMenuStateAt,settingsHidden:settingsPanel.hidden,remoteHidden:remotePanel.hidden,editable:!!editable,dvdDefault})','returnByValue':True})
                        print('READ_ONLY_INPUT_PROBE '+str(result.get('result',{}).get('value')),flush=True)
                        probe.send('Debugger.resume')
                    probe.on('Debugger.paused',paused)
                    probe.send('Debugger.setBreakpointByUrl',{'lineNumber':1443,'urlRegex':r'/js/miniclient\.js(?:\?|$)'})
                page.locator('#stage').focus();page.keyboard.press('ArrowLeft')
                print(json.dumps({'observedNativeHints':page.evaluate('DVD_NATIVE_HINTS'),'commandsAfterArrow':wire_commands[mark:],
                                  'browserDvdMenu':state_observation.get('dvdMenu'),'browserStateAgeMs':round(1000*(time.monotonic()-state_observation.get('at',0))),
                                  'presentation':page.locator('#videoBounds').get_attribute('data-presentation')}),flush=True)
                wait_until(lambda:wire_commands[mark:]==[7,10,9],'production key arms native Time Scroll',10)
                page.keyboard.press('Enter')
                wait_until(lambda:wire_commands[mark:]==[7,10,9,10],'exact production Time Scroll rewind/commit sequence')
                wait_until(lambda:mcp('ui.state',context=identity).get('mediaTimeMs',prior)<prior-2000,'native DVD seek accepted',30)
                wait_until(lambda:page.locator('#videoPlane').evaluate('old=>videoPlane.currentSrc!==old&&videoPlane.videoWidth>0&&videoPlane.readyState>=2',prior_source),'post-seek replacement picture',60)
                wait_until(moving,'post-seek advancing title',30)
                assert mcp('ui.state',context=identity).get('dvdMenu') is False
                record('production-keyboard-time-scroll-seek-and-picture',priorMs=prior,commands=[7,10,9,10],approximateDvdLanding=True)
                assert page.locator('#seekRange').is_disabled()
                assert page.locator('#applyQualityRecommendation').is_disabled()
                record('dvd-refuses-recording-slider-and-automatic-quality')
            if os.environ.get('SAGETV_DVD_SUBTITLE_GATE')=='1':
                # currentSrc/readyState can expose the replacement while the
                # display still holds its previous picture. Wait actual video
                # frame callbacks, not merely a changed URL or cue pixels.
                def presented_frame():
                    return page.locator('#videoPlane').evaluate('v=>new Promise((resolve,reject)=>{const t=setTimeout(()=>reject(new Error("No presented DVD frame")),10000);v.requestVideoFrameCallback((n,m)=>{clearTimeout(t);resolve({mediaTime:m.mediaTime,presentedFrames:m.presentedFrames});});})')
                first_presented=presented_frame();frame_source=page.locator('#videoPlane').evaluate('v=>v.currentSrc')
                frame_deadline=time.monotonic()+30
                while True:
                    page.wait_for_timeout(1200);settled_presented=presented_frame()
                    current_source=page.locator('#videoPlane').evaluate('v=>v.currentSrc')
                    # The browser may retain one old callback during attach,
                    # and stock DVD seek can publish an intermediate FLUSH.
                    # Restart this witness on that real discontinuity, never
                    # count an old picture/URL as the replacement's progress.
                    if current_source!=frame_source or settled_presented['mediaTime']<first_presented['mediaTime']:
                        first_presented=settled_presented;frame_source=current_source
                    if settled_presented['mediaTime']>first_presented['mediaTime']+2:break
                    assert time.monotonic()<frame_deadline,'Actual post-seek frames did not advance within30s'
                wait_until(lambda:bool(subtitle_observations),'production DVD subtitle response')
                def subtitle_off(value):return value in (None,62,8192) or value<0 or bool(value&0x80)
                initially_off=subtitle_off(subtitle_observations[-1].get('selected'))
                if initially_off:
                    mcp('ui.command',context=identity,command='DVD Subtitle Toggle');subtitle_borrowed=True
                def subtitle_pixels():
                    return page.locator('#dvdSpuCanvas').evaluate('c=>{const d=c.getContext("2d").getImageData(0,0,c.width,c.height).data;let n=0;for(let i=3;i<d.length;i+=4)if(d[i])n++;return n}')
                next_spu_notice=[0]
                def visible_title_subtitle():
                    alpha=subtitle_pixels()
                    if time.monotonic()>next_spu_notice[0]:
                        print(json.dumps({'subtitleObservation':subtitle_observations[-1] if subtitle_observations else None,'alphaPixels':alpha,
                                          'videoTime':page.locator('#videoPlane').evaluate('v=>v.currentTime'),'nativeTimeMs':mcp('ui.state',context=identity).get('mediaTimeMs')}),flush=True)
                        next_spu_notice[0]=time.monotonic()+5
                    return subtitle_observations and not subtitle_off(subtitle_observations[-1].get('selected')) and alpha>100
                wait_until(visible_title_subtitle,'actual title SPU physical selection and rendered pixels',25)
                assert mcp('ui.state',context=identity).get('dvdMenu') is False
                record('title-spu-physical-selection-and-real-canvas-pixels',selected=subtitle_observations[-1]['selected'],alphaPixels=subtitle_pixels(),subtitleState=subtitle_observations[-1],firstPresented=first_presented,settledPresented=settled_presented,nativeTimeMs=mcp('ui.state',context=identity).get('mediaTimeMs'))
                page.screenshot(path=str(OUT/(stamp+'-title-subtitles.png')))
                if subtitle_borrowed:
                    mcp('ui.command',context=identity,command='DVD Subtitle Toggle');subtitle_borrowed=False
                    wait_until(lambda:subtitle_off(subtitle_observations[-1].get('selected')) and subtitle_pixels()==0,'subtitle Off clears actual title pixels',10)
                    record('native-subtitle-off-restored-no-ghost-pixels')
            # Public stock controls, routed through the production browser
            # command handler. Return to the authored menu then title again.
            assert api('command',command=67).get('ok') is True
            wait_until(lambda:mcp('ui.state',context=identity).get('dvdMenu') is True,'native authored menu return',30)
            record('native-menu-return-after-owned-feature')
            page.locator('#settingsToggle').click();page.locator('#settings-tab-playback').click()
        assert page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')")==saved,'Action mutated saved profile'
        record('saved-stream-profile-preserved')
        assert not errors,errors
        mcp('companion.dvd_hook',context=identity,expected=selected['playerClass'],enabled='false',confirm='true');hook=False
        mcp('media.control',context=identity,operation='stop')
        for key,before,value in reversed(borrowed):mcp('companion.config_set',setting=key,expected=value,value=before,confirm='true')
        borrowed.clear();record('exact-hook-and-plugin-options-restored')
        page.locator('#closeSettings').click()
        mcp('media.watch',context=identity,media_id=media['mediaFileId'],wait_ms=0)
        wait_until(lambda:'native controls unchanged' in page.locator('#dvdCompanionStatus').text_content(),'unselected provider preserves native controls',45)
        wait_until(lambda:page.evaluate("()=>videoPlane.videoWidth>0||!document.querySelector('#dvdStillFrame').hidden"),'stock fallback menu',60)
        assert mcp('ui.state',context=identity).get('dvdMenu')
        assert not page.locator('[data-companion-dvd="beginning"]').is_enabled()
        record('restored-unselected-extension-native-dvd-fallback')
        if os.environ.get('SAGETV_DVD_EOF_GATE')=='1':
            previous=page.locator('#videoPlane').evaluate('v=>v.currentSrc')
            # Public MCP already maps menu Select to stock DirectPlaybackControl
            # 208. This is explicitly setup, not proof of an STV key binding.
            # Generic command20 can select SageMC's enclosing preview menu.
            assert mcp('ui.command',context=identity,command='Select').get('accepted') is True
            def native_moving():
                if page.locator('#autoplayBtn').is_visible():page.locator('#autoplayBtn').click()
                return page.locator('#videoPlane').evaluate('old=>videoPlane.currentSrc!==old&&videoPlane.videoWidth>0&&videoPlane.currentTime>.5&&!videoPlane.paused',previous) and mcp('ui.state',context=identity).get('dvdMenu') is False
            wait_until(native_moving,'native feature before natural EOF',60)
            natural_eof_menu('stock-native-natural-feature-eof-new-menu-picture')
        mcp('media.control',context=identity,operation='stop')
        assert not errors,errors;passed=True
        # Retire the exact native owner before browser pagehide can retire it
        # itself. A duplicate stop after context.close can correctly return404.
        assert api('stop').get('ok') is True
        owned=None
        context.close();browser.close()
except Exception as failure:
    print('DVD_GATE_FAILURE '+type(failure).__name__+': '+str(failure)[:500],flush=True)
    raise
finally:
    if page and not passed:
        try:page.screenshot(path=str(OUT/(stamp+'-companion-dvd-failure.png')))
        except Exception:pass
    if subtitle_borrowed:
        try:mcp('ui.command',context=identity,command='DVD Subtitle Toggle');subtitle_borrowed=False
        except Exception:cleanup.append('Owned subtitle enable restoration failed')
    if bookmark_pending:
        try:
            current=mcp('companion.dvd_bookmark',context=identity)
            if current.get('present') is False:bookmark_fingerprint=None
            elif bookmark_fingerprint and current.get('fingerprint')==bookmark_fingerprint:
                mcp('companion.dvd_intent',context=identity,operation='clear_resume',confirm='true')
                assert mcp('companion.dvd_bookmark',context=identity).get('present') is False
                bookmark_fingerprint=None
            else:cleanup.append('Concurrent bookmark changed; preserved for manual review')
        except Exception:cleanup.append('Owned test bookmark cleanup failed')
    if hook:
        try:
            current=mcp('companion.dvd_hook',context=identity)
            mcp('companion.dvd_hook',context=identity,expected=current['playerClass'],enabled='false',confirm='true')
            mcp('media.control',context=identity,operation='stop')
        except Exception:cleanup.append('owned DVD hook cleanup failed')
    for key,before,value in reversed(borrowed):
        try:mcp('companion.config_set',setting=key,expected=value,value=before,confirm='true')
        except Exception:cleanup.append('restore failed: '+key)
    if owned:
        try:api('stop')
        except Exception:
            # Already absent is acceptable only with independent read-only
            # identity proof below, not by interpreting any error as idle.
            pass
    # Stock UIContextNames can retain this disconnected owned UI beyond30s.
    # Two observed runs retired independently afterward; allow90s ONLY for
    # read-only retirement proof, not playback readiness or control replay.
    deadline=time.monotonic()+90;retired=False;next_notice=0
    while time.monotonic()<deadline:
        try:
            if identity not in mcp('ui.list').get('contexts',[]):retired=True;break
        except Exception:pass
        if time.monotonic()>=next_notice:
            print('Waiting for exact disconnected native UI retirement (read-only)',flush=True)
            next_notice=time.monotonic()+10
        time.sleep(.25)
    if not retired:cleanup.append('owned native retirement not independently verified')
    (OUT/(stamp+'-companion-dvd.json')).write_text(json.dumps({'passed':passed and not cleanup,'stockServer':'.232','engine':os.environ.get('SAGETV_BROWSER_ENGINE','chromium'),'physicalIPhone':False,'allDiscCertification':False,'rows':rows,'wireCommands':wire_commands,'subtitleStates':subtitle_observations,'pageErrors':errors,'cleanup':cleanup},indent=2)+'\n')
    if cleanup:raise RuntimeError('; '.join(cleanup))
