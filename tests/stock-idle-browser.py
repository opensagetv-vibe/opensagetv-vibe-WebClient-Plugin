#!/usr/bin/env python3
"""Actual idle stock232 event consumption and lost-beacon cleanup; no phone claim.

--source-client is an explicit isolated Playwright route, never a live file edit.
Installed mode is the acceptance gate. No Watch/encoder, Core or settings change.
"""
import argparse,importlib.util,json,time
from pathlib import Path
from urllib.parse import parse_qs,urlparse
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-client',action='store_true');args=p.parse_args()
identity='da92a86446be';owned=None;page=None;context=None;browser=None;pw=None
out=ROOT/'artifacts/active/WEB-092';out.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());report=dict(passed=False,stock232=True,physicalPhone=False,sourceClient=args.source_client,rows=[],receipts=0,errors=[],cleanup=[])
def mcp(action,**v):return C.request(cfg,'/v1/control',dict(action=action,**v),mcp=True,timeout=10)
def api(action):return C.request(cfg,'/SageTVWebPlayer/api/miniclient?action='+action+'&session='+owned,timeout=8)
def observed(response):
    global owned
    if '/api/miniclient' not in response.url or response.request.method!='POST':return
    data=parse_qs(response.request.post_data or '');action=parse_qs(urlparse(response.url).query).get('action',data.get('action',['']))[0]
    if action=='state' and data.get('expectedHlsSession')==['__browser_transport_only__']:report['receipts']+=1
    if action=='start':
        reply=response.json()
        if reply.get('clientId','').replace(':','').lower()==identity:owned=reply.get('session')
try:
    if not C.activity(cfg).get('safeToRestart') or mcp('ui.list').get('contexts'):raise RuntimeError('Independent idle required')
    pw=sync_playwright().start();browser=pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1280,'height':800},service_workers='block',http_credentials={'username':cfg['web_username'],'password':cfg['web_password']})
    page=context.new_page();page.on('response',observed);page.on('pageerror',lambda e:report['errors'].append(type(e).__name__))
    dropped=[];page.on('console',lambda msg:dropped.append(True) if msg.text=='TEST_DROPPED_IDLE_PAGEHIDE_STOP' else None)
    page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE')")
    if args.source_client:page.route('**/js/miniclient.js*',lambda r:r.fulfill(path=str(ROOT/'src/main/webapp/js/miniclient.js'),content_type='application/javascript'))
    page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html?ui=1280x720',wait_until='domcontentloaded')
    page.wait_for_function("connectionStatus.textContent.toLowerCase().startsWith('connected')",timeout=30000)
    if not owned:raise RuntimeError('No exact owned session')
    saved=page.evaluate('JSON.stringify(localStorage)');began=time.monotonic()
    while time.monotonic()-began<105:
        page.wait_for_timeout(5000)
        native=mcp('ui.state',context=identity);status=api('status')
        sample=dict(elapsedSeconds=round(time.monotonic()-began,2),alive=status.get('alive'),fullyLoaded=native.get('fullyLoaded'),receipts=report['receipts'])
        report['rows'].append(sample);print(json.dumps(sample),flush=True)
        if status.get('alive') is not True or native.get('fullyLoaded') is not False:raise RuntimeError('Idle event consumer expired or acquired media')
    if report['receipts']<4:raise RuntimeError('No sustained actual client receipt proof')
    if page.evaluate('JSON.stringify(localStorage)')!=saved:raise RuntimeError('Saved preferences changed')
    page.locator('#stage').focus();page.keyboard.press('ArrowDown');page.keyboard.press('ArrowUp')
    page.wait_for_timeout(500);page.screenshot(path=str(out/(stamp+'-idle.png')))
    if not api('status').get('alive'):raise RuntimeError('Native input failed after idle')
    armed=page.evaluate("""id=>{const send=navigator.sendBeacon;const drop=function(url,body){const u=new URL(url,location.href);if(u.origin===location.origin&&u.pathname.endsWith('/api/miniclient')&&u.searchParams.get('action')==='stop'&&body instanceof URLSearchParams&&body.get('session')===id){console.log('TEST_DROPPED_IDLE_PAGEHIDE_STOP');return false}return send.apply(this,arguments)};navigator.sendBeacon=drop;return navigator.sendBeacon===drop}""",owned)
    if not armed:raise RuntimeError('Exact lost-beacon fault not armed')
    page.close(run_before_unload=True)
    if not page.is_closed():page.wait_for_event('close',timeout=10000)
    closed=time.monotonic();retired=False
    while time.monotonic()-closed<90:
        names=mcp('ui.list').get('contexts',[])
        try:dead=api('status').get('alive') is False
        except RuntimeError as e:
            if not str(e).startswith('HTTP 404:'):raise
            dead=True
        if dead and identity not in names:retired=True;break
        time.sleep(1)
    if not retired:raise RuntimeError('Lost page retained native ownership')
    if not dropped:raise RuntimeError('Lost-beacon fault did not execute')
    report['orphanCleanupSeconds']=round(time.monotonic()-closed,2)
    if report['errors']:raise RuntimeError('Browser errors')
    report['passed']=True
except Exception as error:
    report.update(errorType=type(error).__name__,error=str(error)[:220] if isinstance(error,RuntimeError) else 'Bounded observation failed; no replay')
finally:
    if not report['passed'] and owned:
        try:C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action='stop',session=owned));report['failureCleanupStopSubmitted']=True
        except Exception:report['cleanup'].append('Exact failure cleanup unconfirmed')
    if context:context.close()
    if browser:browser.close()
    if pw:pw.stop()
    path=out/(stamp+'-idle-browser.json');path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=report['passed'],sourceClient=args.source_client,rows=len(report['rows']),receipts=report['receipts'],orphanCleanupSeconds=report.get('orphanCleanupSeconds'),error=report.get('error'),report=str(path))),flush=True)
raise SystemExit(0 if report['passed'] else 1)
