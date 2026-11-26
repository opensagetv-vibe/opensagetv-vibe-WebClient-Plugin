#!/usr/bin/env python3
"""Affected stock232 authored-DVD converter/menu gate; not all-disc certification."""
import importlib.util,json,time
from pathlib import Path
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
identity='da92a86446be';owned=None;complete=False;results=[];errors=[];last_states=[]
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());OUT=ROOT/'artifacts/active/WEB-021';OUT.mkdir(parents=True,exist_ok=True)
def mcp(action,**values):return C.request(cfg,'/v1/control',dict(action=action,**values),mcp=True)
def gate(label,**detail):results.append(dict(gate=label,passed=True,**detail));print('PASS '+label,flush=True)
def observe(response):
    global owned
    try:
        if '/api/miniclient' in response.url and response.request.method=='POST':
            value=response.json()
            if value.get('session') and value.get('clientId','').replace(':','').lower()==identity:owned=value['session']
        elif '/api/hls' in response.url:
            value=response.json()
            if value.get('session'):last_states.append(value)
    except Exception:pass
try:
    before=C.activity(cfg);contexts=mcp('ui.list').get('contexts',[])
    assert before['recordingCount']==0 and before['connectedClientCount']==0 and (not contexts or contexts==[identity])
    media=mcp('media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/OpenSageTV_Vibe_Test_DVD')
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
        context=browser.new_context(viewport={'width':1280,'height':800},http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block',accept_downloads=True)
        page=context.new_page();page.on('response',observe);page.on('pageerror',lambda e:errors.append(str(e)))
        page.add_init_script("""localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');
        localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify({player:'hls',videoMode:'transcode',videoKbps:1200,resolution:'480',deinterlace:'on',deinterlaceFilter:'bwdif'}));""")
        page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html?ui=1280x720',wait_until='domcontentloaded')
        for _ in range(120):
            page.wait_for_timeout(500)
            if owned and identity in mcp('ui.list').get('contexts',[]):
                native=C.request(cfg,'/SageTVWebPlayer/api/miniclient?'+urlencode({'action':'status','session':owned}))
                if native.get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'):break
        else:raise AssertionError('Stock STV first frame unavailable')
        mcp('media.watch',context=identity,media_id=media['mediaFileId'],wait_ms=0)
        page.wait_for_function("(()=>{const v=document.querySelector('#videoPlane');const s=document.querySelector('#dvdStillFrame');return v.videoWidth>0||!s.hidden})()",timeout=120000)
        page.screenshot(path=str(OUT/(stamp+'-root-menu.png')))
        gate('stock authored DVD emits decoded/retained menu background through new converter')
        native=mcp('ui.state',context=identity)
        assert native['dvd'] and native['dvdMenu'],native
        gate('stock authored-menu state is available for directional-key guard')
        page.locator('#stage').focus();page.keyboard.press('ArrowDown');page.wait_for_timeout(700)
        assert mcp('ui.state',context=identity)['dvdMenu']
        gate('authored-menu Down stays menu navigation, not chapter/Time Scroll')
        mcp('ui.command',context=identity,command='DVD Menu');page.wait_for_timeout(1500)
        page.locator('#stage').focus();page.keyboard.press('Enter');page.wait_for_timeout(2000)
        page.screenshot(path=str(OUT/(stamp+'-select.png')))
        # This fixture may default to Languages after returning; do not claim
        # title/chapter/256x parity from only a successful root-menu transition.
        gate('authored DVD Select/return command remains responsive',state=mcp('ui.state',context=identity).get('dvdMenu'))
        assert not errors,errors;complete=True;context.close();browser.close()
finally:
    if owned:
        try:C.request(cfg,'/SageTVWebPlayer/api/miniclient',{'action':'stop','session':owned})
        except Exception:pass
    (OUT/(stamp+'-dvd-affected.json')).write_text(json.dumps({'passed':complete,'realStock232':True,'allDiscCertification':False,'results':results,'errors':errors,'lastHlsStates':last_states[-2:]},indent=2)+'\n')
