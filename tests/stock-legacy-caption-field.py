#!/usr/bin/env python3
"""Actual stock event225 probe; counters are NOT visible-caption acceptance.

One ephemeral host UI, existing public APIs only, no Core/config edits. Saved
household/phone profiles are never loaded or changed. Screens need review.
"""
import argparse,importlib.util,json,time
from pathlib import Path
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',choices=('cea','teletext'),default='cea')
p.add_argument('--trace',action='store_true',help='Temporarily enable existing public MCP CC trace, restore exact prior trace state; summarize log counters only')
a=p.parse_args();identity='da92a86446be';owned=None;page=None;context=None;browser=None;pw=None
borrowed=False;restore_attempted=False;stop_attempted=False;rows=[];errors=[];cleanup=[];passed=False;failure={}
trace_before=None;trace_changed=False
OUT=ROOT/'artifacts/active/WP05-003';OUT.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
def mcp(action,**values):return C.request(cfg,'/v1/control',dict(action=action,**values),mcp=True,timeout=60 if action=='media.seek' else 30)
def api(action,**values):
    if action in ('status','streamSettings','playbackState'):
        return C.request(cfg,'/SageTVWebPlayer/api/miniclient?'+urlencode(dict(action=action,session=owned,**values)),timeout=20)
    return C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action=action,session=owned,**values),timeout=30)
def wait(test,label,seconds=40):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        if test():return
        page.wait_for_timeout(150)
    raise RuntimeError('Timed out: '+label)
def observe(response):
    global owned
    if '/api/miniclient' not in response.url or response.request.method!='POST':return
    try:
        value=response.json()
        if value.get('session') and value.get('clientId','').replace(':','').lower()==identity:owned=value['session']
    except Exception:pass
def status():
    con=api('status').get('connection',{})
    return dict(authority=con.get('captionAuthority'),events=con.get('subtitleCallbackEvents'),bytes=con.get('subtitleCallbackBytes'))
def inspect_a53():
    if a.source!='cea':return
    stream=api('streamSettings').get('session')
    data=C.request(cfg,'/SageTVWebPlayer/api/captions?'+urlencode(dict(session=stream,cursor=0,untilMs=15000)),timeout=20)
    counts=dict(cea608Field1=0,cea608Field2=0,cea708Data=0,cea708Start=0,valid608Bytes=0,invalid608Parity=0,paddingPairs=0,controlPairs=0,printablePairs=0)
    names=('cea608Field1','cea608Field2','cea708Data','cea708Start');control_codes={}
    for _,encoded in data.get('packets',[]):
        packet=bytes.fromhex(encoded)
        for i in range(0,len(packet)-2,3):
            if not packet[i]&4:continue
            kind=packet[i]&3;counts[names[kind]]+=1
            if kind<2:
                for value in packet[i+1:i+3]:counts['valid608Bytes' if value.bit_count()%2 else 'invalid608Parity']+=1
                b1,b2=packet[i+1]&127,packet[i+2]&127
                counts['paddingPairs' if b1==b2==0 else 'controlPairs' if 0x10<=b1<0x20 else 'printablePairs']+=1
                if 0x10<=b1<0x20:
                    code=f'{kind}:{b1:02x}:{b2:02x}';control_codes[code]=control_codes.get(code,0)+1
    rows.append(dict(label='original-source-A53-types-and-parity',metadataOnly=counts,controlCodes=control_codes,rawCaptionContentExported=False))
def screen(label):
    metrics=page.evaluate("""()=>{const c=gfxCanvas,d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let alpha=0,bright=0;for(let y=Math.floor(c.height*.6);y<c.height;y++)for(let x=0;x<c.width;x++){const i=(y*c.width+x)*4;if(d[i+3]>0)alpha++;if(d[i+3]>128&&d[i]>180&&d[i+1]>180&&d[i+2]>180)bright++;}return{width:c.width,height:c.height,bottomAlphaPixels:alpha,bottomBrightPixels:bright,localText:localCaptions.textContent.length,localDvbHidden:dvbCaptions.hidden,videoTime:videoPlane.currentTime,videoPaused:videoPlane.paused};}""")
    path=OUT/(stamp+'-'+a.source+'-'+label+'.png');page.screenshot(path=str(path))
    rows.append(dict(label=label,native=status(),publicCaptionState=mcp('captions.get',context=identity).get('state'),metrics=metrics,capture=path.name,visualAcceptance='PENDING_REVIEW'))
    print('Captured '+label,flush=True)
def restore_stv():
    global borrowed,restore_attempted
    if not borrowed:return
    current=mcp('captions.get',context=identity).get('stvFile','')
    if current.endswith('/SageMC_Vibe.xml'):borrowed=False;return
    if not current.endswith('/SageTV7.xml'):raise RuntimeError('Unknown STV; refuse restoration command')
    if restore_attempted:raise RuntimeError('Original STV restoration unconfirmed; no replay')
    restore_attempted=True
    if not api('command',command=28).get('ok'):raise RuntimeError('Home restoration unacknowledged; no replay')
    wait(lambda:mcp('captions.get',context=identity).get('stvFile','').endswith('/SageMC_Vibe.xml'),'original STV restored',20)
    borrowed=False
try:
    activity=C.activity(cfg)
    if activity.get('recordingCount')!=0 or activity.get('connectedClientCount')!=0 or mcp('ui.list').get('contexts'):raise RuntimeError('Require independently idle server')
    source='/var/media/OpenSageTV_Vibe_Tests/VibeCaptionTest-1080i-CEA608-90s-2s.ts' if a.source=='cea' else '/var/media/videos/USER_TEST/Breakfast-26711345-0.ts'
    media=mcp('media.resolve_exact_path',path=source)
    if not media.get('mediaFileId'):raise RuntimeError('Exact existing fixture unavailable')
    pw=sync_playwright().start();browser=pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1280,'height':800},http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block')
    page=context.new_page();page.on('response',observe);page.on('pageerror',lambda e:errors.append(str(e)))
    # Browser Off deliberately leaves the real legacy stock callback renderer
    # as the ONLY caption surface. This is a temporary test profile, not a
    # synthetic property response or an override of production implementation.
    page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebCaptionAuthority.v1',JSON.stringify({mode:'off'}));")
    page.add_init_script((ROOT/'tests/fixtures/native-timeline-cursor.js').read_text(encoding='utf-8'))
    page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html?ui=1280x720',wait_until='domcontentloaded')
    wait(lambda:owned is not None and api('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'),'owned native UI')
    if not mcp('captions.get',context=identity).get('stvFile','').endswith('/SageMC_Vibe.xml'):raise RuntimeError('Unexpected initial STV; no route guessing')
    borrowed=True
    for x,y in ((740,543),(750,542),(158,317)):
        box=page.locator('#gfxCanvas').bounding_box();page.locator('#gfxCanvas').click(position={'x':x*box['width']/1280,'y':y*box['height']/720});page.wait_for_timeout(1000)
    wait(lambda:mcp('captions.get',context=identity).get('stvFile','').endswith('/SageTV7.xml'),'borrowed stock STV',20)
    wait(lambda:page.evaluate("()=>{const c=gfxCanvas,d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;for(let i=3;i<d.length;i+=1024)if(d[i])return true;return false}"),'new stock STV actually drawn',40)
    # Intentional ephemeral configure, unlike the read-only GET observations.
    requested=dict(stream_player='hls',stream_videoMode='transcode',stream_encoder='qsv',stream_videoKbps=1200,stream_resolution='480',stream_captions='608' if a.source=='cea' else 'teletext',stream_captionAuthority='stv',stream_browserCaptionRendering='false',stream_allowFallback='false')
    if C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action='streamSettings',session=owned,**requested)).get('ok') is False:raise RuntimeError('Explicit test profile rejected')
    configured=api('streamSettings').get('configured')
    if not configured or str(configured.get('browserCaptionRendering')).lower()!='false' or configured.get('captionAuthority')!='stv':raise RuntimeError('Legacy-only test profile not effective')
    observed_trace=mcp('captions.get',context=identity)
    if not a.trace and observed_trace.get('ccTraceEnabled'):raise RuntimeError('No-trace gate requires trace already disabled; do not silently change it')
    rows.append(dict(label='trace-mode',requested=a.trace,initialEnabled=observed_trace.get('ccTraceEnabled')))
    if a.trace:
        trace_before=mcp('captions.get',context=identity)
        if not trace_before.get('ccTraceEnabled'):
            trace_changed=True
            if not mcp('captions.trace',state='on').get('ccTraceEnabled'):raise RuntimeError('Temporary trace not confirmed')
    if not mcp('captions.set',context=identity,state='Off').get('ok'):raise RuntimeError('Off rejected')
    if not mcp('media.watch',context=identity,media_id=media['mediaFileId'],wait_ms=0).get('accepted'):raise RuntimeError('Watch rejected')
    wait(lambda:page.evaluate('videoPlane.videoWidth>0'),'actual video')
    if not mcp('media.seek',context=identity,target_ms=5000).get('accepted'):raise RuntimeError('One setup Seek rejected; no replay')
    wait(lambda:page.evaluate('videoPlane.videoWidth>0&&videoPlane.readyState>=2'),'replacement video')
    if page.locator('#autoplayBtn').is_visible():page.locator('#autoplayBtn').click()
    wait(lambda:page.evaluate('!videoPlane.paused&&videoPlane.currentTime>.3'),'moving source')
    inspect_a53()
    if not page.evaluate('TEST_VIDEO_BOUNDS&&TEST_VIDEO_BOUNDS[2]>1150'):api('command',command=15)
    wait(lambda:page.evaluate('TEST_VIDEO_BOUNDS&&TEST_VIDEO_BOUNDS[2]>1150'),'native fullscreen')
    page.wait_for_timeout(7000);screen('off-before')
    for state in ('CC1','CC2','Off'):
        before=status()
        if not mcp('captions.set',context=identity,state=state).get('ok'):raise RuntimeError('Caption selection rejected')
        page.wait_for_timeout(3500)
        for n in range(3):screen(state.lower()+'-'+str(n));page.wait_for_timeout(750)
        if page.evaluate('localCaptions.textContent.trim().length')!=0:raise RuntimeError('Local renderer contaminated the legacy-only test')
        if state!='Off' and status()['events']<=before['events']:raise RuntimeError('No real callback traffic during '+state)
    previous=api('streamSettings').get('session')
    if not mcp('media.seek',context=identity,target_ms=30000).get('accepted'):raise RuntimeError('Post-clear Seek rejected; no replay')
    wait(lambda:api('streamSettings').get('session')!=previous,'new seek producer',40)
    wait(lambda:page.evaluate('!videoPlane.paused&&videoPlane.readyState>=2&&videoPlane.currentTime>.5'),'new seek pictures',40)
    if not mcp('captions.set',context=identity,state='CC1').get('ok'):raise RuntimeError('Post-seek CC1 rejected')
    page.wait_for_timeout(6000);screen('cc1-after-seek')
    if not mcp('captions.set',context=identity,state='Off').get('ok'):raise RuntimeError('Final Off rejected')
    page.wait_for_timeout(1500);screen('off-after-seek')
    if api('streamSettings').get('configured')!=configured:raise RuntimeError('Ephemeral native profile changed unexpectedly')
    if errors:raise RuntimeError('Browser JavaScript errors')
    if a.trace:rows.append(dict(label='trace-log-summary',status='Read separately with host scripts/legacy-caption-log-summary.py; browser runner needs no SSH dependency'))
    restore_stv();passed=True
except Exception as e:
    failure=dict(type=type(e).__name__,message=str(e)[:250] if isinstance(e,RuntimeError) else 'Bounded test failed')
    if page:
        try:screen('failure')
        except Exception:pass
finally:
    if trace_changed:
        try:
            state=mcp('captions.trace',state='off' if trace_before.get('ccTracePropertyPresent') else 'clear')
            if state.get('ccTraceEnabled') or state.get('ccTracePropertyPresent')!=trace_before.get('ccTracePropertyPresent'):cleanup.append('Original trace state unverified')
        except Exception:cleanup.append('Original trace restoration unknown; no replay')
    if owned:
        try:restore_stv()
        except Exception:cleanup.append('Original STV restoration unverified')
        if not stop_attempted:
            stop_attempted=True
            try:
                if not api('stop').get('ok'):cleanup.append('Exact Stop unacknowledged; no replay')
            except Exception:cleanup.append('Exact Stop unknown; no replay')
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
    result=dict(callbackProbePassed=passed and not cleanup,visibleCaptionAcceptance='PENDING_REVIEW',realStock232=True,physicalIPhone=False,source=a.source,rows=rows,errors=errors,cleanup=cleanup,failure=failure)
    target=OUT/(stamp+'-'+a.source+'-legacy-field.json');target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(callbackProbePassed=result['callbackProbePassed'],visualAcceptance=result['visibleCaptionAcceptance'],rows=len(rows),cleanup=cleanup,failure=failure)),flush=True)
raise SystemExit(0 if passed and not cleanup else 1)
