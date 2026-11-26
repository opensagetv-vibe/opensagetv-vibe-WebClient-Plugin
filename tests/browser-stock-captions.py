#!/usr/bin/env python3
"""Real UK Teletext/DVB + stock STV virtual-slot selection, stock232 only."""
import importlib.util,json,time
from pathlib import Path
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
cfg=C.configuration();identity='da92a86446be';owned=None;page=None;results=[];complete=False;errors=[];caption_requests=[];state_reads=[]
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());OUT=ROOT/'artifacts/active/WEB-020';OUT.mkdir(parents=True,exist_ok=True)
def mcp(action,**values):return C.request(cfg,'/v1/control',dict(action=action,**values),mcp=True)
def mini(action,**values):
    if action in ['status','streamSettings'] and not values:return C.request(cfg,'/SageTVWebPlayer/api/miniclient?'+urlencode({'action':action,'session':owned}))
    return C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action=action,session=owned,**values))
def gate(name,**detail):results.append(dict(gate=name,passed=True,**detail));print('PASS '+name,flush=True)
def capture(label):page.screenshot(path=str(OUT/(stamp+'-'+label+'.png')))
def observe(response):
    global owned
    try:
        if '/api/miniclient' not in response.url or response.request.method!='POST':return
        data=response.json()
        if 'captionState' in data:state_reads.append(data)
        if data.get('session') and data.get('clientId','').replace(':','').lower()==identity:owned=data['session']
        if 'captionSelection' in response.url:
            from urllib.parse import parse_qs
            values=parse_qs(response.request.post_data or '')
            caption_requests.append({'kind':values.get('kind'),'ok':data.get('ok')})
    except Exception:pass
try:
    before=C.activity(cfg);contexts=mcp('ui.list').get('contexts',[])
    assert before.get('recordingCount')==0 and before.get('connectedClientCount')==0
    assert not contexts or contexts==[identity]
    fixture=mcp('media.resolve_exact_path',path='/var/media/videos/USER_TEST/Breakfast-26711345-0.ts')
    assert fixture.get('mediaFileId'),fixture
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
        context=browser.new_context(viewport={'width':1280,'height':800},http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block',accept_downloads=True)
        page=context.new_page();page.on('response',observe);page.on('pageerror',lambda e:errors.append(str(e)))
        page.add_init_script("""localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');
        localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify({player:'hls',videoMode:'transcode',videoKbps:1500,resolution:'480'}));
        localStorage.setItem('sagetvWebCaptionAuthority.v1',JSON.stringify({mode:'stv',cc1Type:'teletext',cc1Language:'eng',cc1Service:1,cc2Type:'dvb',cc2Language:'eng',cc2Service:2}));""")
        page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html?ui=1280x720',wait_until='domcontentloaded')
        for _ in range(120):
            page.wait_for_timeout(500)
            if owned and identity in mcp('ui.list').get('contexts',[]) and mini('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'):break
        else:raise AssertionError('Stock STV first frame unavailable')
        mcp('media.watch',context=identity,media_id=fixture['mediaFileId'],wait_ms=0)
        page.wait_for_function("document.querySelector('#videoPlane').videoWidth>0&&document.querySelector('#videoPlane').currentTime>.5",timeout=120000)
        mcp('captions.set',context=identity,state='CC1')
        try:page.wait_for_function("document.querySelector('#localCaptions').textContent.trim().length>0",timeout=30000)
        except Exception:
            capture('stv-failure');page.locator('#settingsToggle').click();page.locator('#settings-tab-diagnostics').click()
            with page.expect_download(timeout=20000) as download:page.locator('#downloadReport').click()
            download.value.save_as(str(OUT/(stamp+'-stv-failure.zip')))
            raise
        first=mini('streamSettings');capture('stock-stv-teletext')
        gate('stock STV CC1 selects visible Teletext on real UK video',selection=mcp('captions.get',context=identity).get('state'))
        mcp('captions.set',context=identity,state='CC2')
        page.wait_for_function("(()=>{const c=document.querySelector('#dvbCaptions');if(!c.width||!c.height)return false;const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;for(let i=3;i<d.length;i+=4)if(d[i])return true;return false})()",timeout=30000,polling=500)
        second=mini('streamSettings');capture('stock-stv-dvb')
        assert first.get('session') and first.get('session')==second.get('session'),(first.get('session'),second.get('session'))
        assert any(x.get('kind')==['dvb'] and x.get('ok') for x in caption_requests),caption_requests
        gate('stock STV CC2 selects visible DVB bitmap without restarting A/V',selection=mcp('captions.get',context=identity).get('state'))
        mcp('captions.set',context=identity,state='Off')
        page.wait_for_function("document.querySelector('#localCaptions').textContent.trim().length===0&&(()=>{const c=document.querySelector('#dvbCaptions');const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;for(let i=3;i<d.length;i+=4)if(d[i])return false;return true})()",timeout=10000,polling=500)
        gate('stock STV Off clears both local caption surfaces')
        assert not errors,errors;complete=True;context.close();browser.close()
finally:
    if owned:
        try:mini('stop')
        except Exception:pass
    (OUT/(stamp+'-stock-caption.json')).write_text(json.dumps({'passed':complete,'realStock232':True,'physicalIPhone':False,'results':results,'captionSelections':caption_requests,'errors':errors,'stateReads':state_reads[-60:]},indent=2)+'\n')
