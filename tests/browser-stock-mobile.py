#!/usr/bin/env python3
"""Real stock232/MCP/FFmpeg-plugin integration. Not a physical iPhone test.

Only the known dedicated Web test identity and canonical synthetic fixture;
never a tuner, Core mutation, arbitrary path/import or unrelated user's media.
"""
import importlib.util,json,time,os
from pathlib import Path
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
cfg=C.configuration();identity='da92a86446be'
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
OUT=ROOT/'artifacts/active/WEB-020';OUT.mkdir(parents=True,exist_ok=True)
results=[];owned=None;page=None;complete=False;hls_states=[];leases=[];errors=[];caption_reads=[]
def mcp(action,**values):return C.request(cfg,'/v1/control',dict(action=action,**values),mcp=True)
def gate(label,**evidence):results.append(dict(gate=label,passed=True,**evidence));print('PASS '+label,flush=True)
def capture(label):
    page.screenshot(path=str(OUT/(stamp+'-'+label+'.png')))
def observe(response):
    global owned
    try:
        if '/api/miniclient' in response.url and response.request.method=='POST':
            data=response.json()
            if data.get('session') and data.get('clientId','').replace(':','').lower()==identity:owned=data['session']
        elif '/api/hls' in response.url:
            data=response.json()
            if data.get('session'):hls_states.append(data)
        elif '/api/av-sync' in response.url and response.request.method=='POST':
            data=response.json()
            if data.get('id'):leases.append(data['id'])
        elif '/api/captions' in response.url:
            data=response.json();packets=data.get('packets',[])
            caption_reads.append({'count':len(packets),'cursor':data.get('cursor'),'firstMs':packets[0][0] if packets else None,'lastMs':packets[-1][0] if packets else None,'videoMs':page.locator('#videoPlane').evaluate('(v)=>Math.round(v.currentTime*1000)')})
    except Exception:pass
def decoded():
    page.wait_for_function("(()=>{const v=document.querySelector('#videoPlane');return v.videoWidth>0&&v.currentTime>.2&&!v.paused})()",timeout=120000)
    start=page.locator('#videoPlane').evaluate('(v)=>({time:v.currentTime,frames:v.getVideoPlaybackQuality?v.getVideoPlaybackQuality().totalVideoFrames:0,width:v.videoWidth,height:v.videoHeight})')
    page.wait_for_timeout(1500)
    finish=page.locator('#videoPlane').evaluate('(v)=>({time:v.currentTime,frames:v.getVideoPlaybackQuality?v.getVideoPlaybackQuality().totalVideoFrames:0,width:v.videoWidth,height:v.videoHeight})')
    assert finish['time']>start['time'],(start,finish)
    if start['frames']:assert finish['frames']>start['frames'],(start,finish)
    return finish
def settings(section):
    if page.locator('#settingsPanel').is_hidden():
        page.locator('#settingsToggle').click()
    branch='playback' if section in ('video','audio','captions') else section
    page.locator('#settings-tab-'+branch).click()
def close_settings():
    while page.locator('#settingsPanel').is_visible():page.locator('#closeSettings').click()
def mini(action,**values):
    if not owned:raise RuntimeError('No owned native session')
    if action=='streamSettings' and not values:return C.request(cfg,'/SageTVWebPlayer/api/miniclient?'+urlencode({'action':action,'session':owned}))
    return C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action=action,session=owned,**values))
def visible_caption(label):
    try:page.wait_for_function("document.querySelector('#localCaptions').textContent.trim().length>0",timeout=20000)
    except Exception:
        capture('caption-failure');settings('diagnostics')
        with page.expect_download(timeout=20000) as download:page.locator('#downloadReport').click()
        download.value.save_as(str(OUT/(stamp+'-caption-failure.zip')))
        raise
    capture(label)

try:
    before=C.activity(cfg)
    contexts=mcp('ui.list').get('contexts',[])
    assert before.get('recordingCount')==0 and before.get('connectedClientCount')==0
    assert not contexts or contexts==[identity],contexts
    assert C.request(cfg,'/SageTVWebPlayer/api/health')['version']=='3.3.0'
    fixture=mcp('media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/VibeCaptionTest-1080i-CEA608-90s-2s.ts')
    media_id=fixture.get('mediaFileId')
    assert media_id,fixture
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_PATH','/usr/local/bin/vibe-chromium'),args=['--no-sandbox'])
        context=browser.new_context(viewport={'width':1280,'height':800},http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block',accept_downloads=True)
        page=context.new_page();page.on('response',observe);page.on('pageerror',lambda error:errors.append(str(error)))
        page.add_init_script("""localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');
          localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify({player:'hls',videoMode:'transcode',videoKbps:1500,resolution:'480',deinterlace:'on',deinterlaceFilter:'auto'}));
          localStorage.setItem('sagetvWebCaptionAuthority.v1',JSON.stringify({mode:'cc1',cc1Type:'cea608',cc1Language:'eng',cc1Service:1}));""")
        page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html?ui=1280x720',wait_until='domcontentloaded')
        page.wait_for_function("document.querySelector('#connectionStatus').textContent.toLowerCase().startsWith('connected')",timeout=60000)
        page.wait_for_timeout(2000);assert owned
        for _ in range(60):
            contexts=mcp('ui.list').get('contexts',[])
            native=mini('status')
            if identity in contexts and native.get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'):break
            page.wait_for_timeout(500)
        else:raise AssertionError('Owned stock STV did not complete its first real frame')
        gate('real stock MiniClient connection / current development assets')
        mcp('media.watch',context=identity,media_id=media_id,wait_ms=0)
        picture=decoded();gate('canonical1080i MPEG-2/AC-3 recording decodes via actual HLS',**picture)
        page.wait_for_timeout(3000)
        capture('recording')
        settings('captions');effective=page.locator('#captionAuthorityEffective').inner_text()
        assert '608' in effective,effective
        gate('explicit CEA slot is honestly labeled manual, independent caption authority',effective=effective)
        close_settings()
        visible_caption('visible-cea');gate('canonical CEA text visibly rendered over actual decoded video')
        # Native socket time and browser position both advance; exact source
        # fixture only, no watched-state mutation of user recordings.
        before_time=mcp('ui.state',context=identity)['rawMediaTimeMs']
        mcp('media.seek',context=identity,target_ms=30000)
        page.wait_for_timeout(3000);picture=decoded()
        state=mcp('ui.state',context=identity)
        assert 25000<=state['rawMediaTimeMs']<=55000,state
        gate('stock recording seek replaces source generation near30s',serverRawTimeMs=state['rawMediaTimeMs'],serverAbsoluteTimeMs=state['mediaTimeMs'],beforeMs=before_time,**picture)
        visible_caption('cea-after-seek');gate('CEA captions remain visible after stock seek')
        if os.environ.get('SAGETV_CAPTION_STRESS')=='1':
            for target in [64000,12000,47000]:
                previous=mini('streamSettings')['session'];mcp('media.seek',context=identity,target_ms=target)
                for _ in range(120):
                    page.wait_for_timeout(500)
                    current=mini('streamSettings').get('session')
                    if current and current!=previous and any(row.get('session')==current for row in hls_states):break
                else:raise AssertionError('Seek did not produce a new owned HLS generation')
                picture=decoded();visible_caption('cea-seek-'+str(target))
                gate('repeat CEA seek/current generation at'+str(target)+'ms',targetMs=target,**picture)
        # A paused explicit Apply must not resume while replacing the converter.
        mini('command',command=6)
        page.wait_for_function("document.querySelector('#videoPlane').paused",timeout=10000);page.wait_for_timeout(600)
        settings('transcoding');page.locator('#stream_videoKbps').fill('1200')
        page.locator('#applyStreaming').click()
        page.wait_for_function("/Applied/.test(document.querySelector('#streamingResult').textContent)",timeout=90000)
        assert page.locator('#videoPlane').evaluate('(v)=>v.paused')
        gate('per-client transcoding Apply retains pause intent',result=page.locator('#streamingResult').inner_text())
        close_settings();mini('command',command=7);picture=decoded()
        gate('resumed replacement decodes actual video',**picture)
        # Real phone-sized DOM on stock live transport, not mocked Sage events.
        page.set_viewport_size({'width':390,'height':844});settings('audio');capture('phone-audio')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#audioOffsetOpen').click();page.locator('#audioOffsetRange').focus();page.keyboard.press('ArrowRight');page.keyboard.press('ArrowLeft');page.keyboard.press('Escape')
        assert page.locator('#audioOffsetPanel').is_hidden()
        gate('real phone viewport /25ms audio dialog parent return, no horizontal truncation')
        # Generated calibration uses the deployed required plugin's real path.
        page.locator('#audioSyncTest').click()
        page.wait_for_function("document.querySelector('#calibrationStatus').textContent.startsWith('Ready')",timeout=180000)
        status=page.locator('#calibrationStatus').inner_text();page.locator('#calibrationPlay').click()
        page.wait_for_function("document.querySelector('#calibrationVideo').currentTime>.5",timeout=30000)
        capture('phone-calibration')
        gate('deployed server-generated A/V calibration really plays',status=status)
        page.locator('#calibrationOffset').focus()
        for _ in range(20):page.keyboard.press('ArrowRight')
        assert page.locator('#calibrationOffset').input_value()=='500'
        page.locator('#calibrationApply').click()
        page.wait_for_function("document.querySelector('#calibrationStatus').textContent.includes('0.500 s')",timeout=180000)
        gate('deployed calibration regenerates at+500ms',status=page.locator('#calibrationStatus').inner_text())
        page.locator('#calibrationReset').click();page.locator('#calibrationBack').click()
        assert page.locator('#calibrationVideo').evaluate('(v)=>v.paused&&!v.getAttribute("src")')
        close_settings()
        assert not errors,errors
        gate('no browser exceptions; calibration audio/source retired on Back')
        complete=True;context.close();browser.close()
finally:
    if page and not complete:
        try:capture('failure')
        except Exception:pass
    for lease in leases:
        try:C.request(cfg,'/SageTVWebPlayer/api/av-sync',{'action':'stop','id':lease})
        except Exception:pass
    if owned:
        try:mini('stop')
        except Exception:pass
    report={'passed':complete,'realStockServer':'.232','physicalIPhone':False,'version':'3.3.0','fixture':'canonical90s/2s CEA608','results':results,'pageErrors':errors,'lastHlsStates':hls_states[-3:],'captionReads':caption_reads[-40:]}
    (OUT/(stamp+'-stock-mobile.json')).write_text(json.dumps(report,indent=2)+'\n')
