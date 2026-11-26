#!/usr/bin/env python3
"""WP13-003 actual stock handshake/GFX ledger OFF/ON/OFF, no playback claims."""
import importlib.util,json,time
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
identity='da92a86446be';rows=[];cleanup=[];passed=False;owned=None
out=ROOT/'artifacts/active/WP13-003';out.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
def mcp(action,**kw):return C.request(cfg,'/v1/control',dict(action=action,**kw),mcp=True)
def idle():
    a=C.activity(cfg)
    if a.get('recordingCount')!=0 or a.get('connectedClientCount')!=0 or mcp('ui.list').get('contexts'):raise RuntimeError('Require independently idle test server')
def observed(response):
    global owned
    if '/api/miniclient' not in response.url or response.request.method!='POST':return
    try:
        j=response.json()
        if j.get('session') and j.get('clientId','').replace(':','').lower()==identity:owned=j['session']
    except Exception:pass
def status():return C.request(cfg,'/SageTVWebPlayer/api/miniclient?action=status&session='+owned)
try:
    with sync_playwright() as pw:
        browser=pw.webkit.launch(headless=True)
        try:
            for enabled in (False,True,False):
                idle();owned=None;context=None
                try:
                    context=browser.new_context(viewport={'width':1280,'height':800},http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block')
                    page=context.new_page();page.on('response',observed);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                    page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebMiniClientSettings.v1',JSON.stringify({unifiedGraphics:"+str(enabled).lower()+"}));")
                    page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html?ui=1280x720',wait_until='domcontentloaded')
                    page.wait_for_function("connectionStatus.textContent.toLowerCase().startsWith('connected')",timeout=30000)
                    if not owned:raise RuntimeError('No owned native session')
                    end=time.monotonic()+20
                    while True:
                        s=status();c=s.get('connection',{})
                        if c.get('startupEvents',{}).get('firstFrameCompleted'):break
                        if time.monotonic()>end:raise RuntimeError('Native first frame unavailable')
                        page.wait_for_timeout(100)
                    page.locator('#stage').focus();page.keyboard.press('ArrowDown');page.wait_for_timeout(400);page.keyboard.press('ArrowUp');page.wait_for_timeout(400)
                    s=status();c=s.get('connection',{});ledger=c.get('gfxOpcodeLedger',{})
                    if c.get('unifiedGraphics') is not enabled or not ledger.get('seen') or ledger.get('unknownCount')!=0 or errors:raise RuntimeError('Unexpected negotiated state/opcode/browser error')
                    rows.append(dict(enabled=enabled,ledger=ledger,browserFrames=c.get('browserFrames'),queue=s.get('queuedEvents'),errors=errors))
                    print(json.dumps(dict(passed=True,enabled=enabled,opcodes=len(ledger['seen']),unknown=ledger['unknownCount'])),flush=True)
                finally:
                    if owned:
                        try:C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action='stop',session=owned))
                        except Exception:cleanup.append('Exact Stop outcome unknown')
                    if context:context.close()
                    end=time.monotonic()+90
                    while identity in mcp('ui.list').get('contexts',[]):
                        if time.monotonic()>end:raise RuntimeError('Exact native UI did not retire; no next session')
                        time.sleep(.3)
                    owned=None
            passed=not cleanup
        finally:browser.close()
finally:
    path=out/(stamp+'-unified-diagnostics.json')
    path.write_text(json.dumps(dict(passed=passed,realStock232=True,physicalPhone=False,engine='webkit',rows=rows,cleanup=cleanup),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=passed,rows=len(rows),report=str(path))),flush=True)
raise SystemExit(0 if passed else 1)
