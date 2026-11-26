#!/usr/bin/env python3
"""WEB-056: actual production DOM/CSS, synthetic calibration readiness only."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import importlib.util, json, os, threading, time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ['SAGETV_ARTIFACT_DIR']).resolve()
if OUT!=(ROOT/'artifacts/active/WEB-023').resolve():raise SystemExit('Use WEB-023 physical-parent artifacts')
spec=importlib.util.spec_from_file_location('display',ROOT/'tests/browser-vibe-display-smoke.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'src/main/webapp')))
threading.Thread(target=server.serve_forever,daemon=True).start()
rows=[];passed=False
try:
    with sync_playwright() as pw:
        for engine in ('chromium','webkit'):
            options={'headless':True}
            if engine=='chromium':options.update(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
            browser=getattr(pw,engine).launch(**options)
            for w,h in ((852,393),(393,852),(667,375),(320,568),(1440,900)):
                context=browser.new_context(viewport={'width':w,'height':h},has_touch=True,service_workers='block')
                page=context.new_page();page.add_init_script(fixture.INIT)
                page.goto(f'http://127.0.0.1:{server.server_port}/miniclient.html',wait_until='domcontentloaded')
                page.wait_for_function('window.TEST&&TEST.stream')
                for long_error in (False,True):
                    page.evaluate("long=>{settingsPanel.hidden=false;settingsPanel.querySelector('.mc-settings-card').hidden=true;calibrationPanel.hidden=false;calibrationPlay.disabled=false;calibrationStatus.textContent=long?'Tap Play again if required by the browser: The request is not allowed by the user agent or the platform in the current context, possibly because the user denied permission.':'Ready — tap Play test to enable sound.';}",long_error)
                    result=page.evaluate("()=>({viewport:[innerWidth,innerHeight],video:calibrationVideo.getBoundingClientRect().height,controls:['calibrationBack','calibrationPlay','calibrationApply','calibrationReset','calibrationOffset'].map(id=>{const e=document.getElementById(id),r=e.getBoundingClientRect(),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return{id,x:r.x,y:r.y,w:r.width,h:r.height,hit:hit===e||e.contains(hit)}})})")
                    for r in result['controls']:
                        assert r['h']>=44 and r['x']>=0 and r['y']>=0 and r['x']+r['w']<=w+.5 and r['y']+r['h']<=h+.5 and r['hit'],(engine,w,h,long_error,r)
                    assert result['video']>=64,result
                    rows.append({'engine':engine,'viewport':[w,h],'longAutoplayError':long_error,'passed':True,**result})
                print('PASS',engine,w,h,flush=True);context.close()
            browser.close()
    passed=True
finally:
    server.shutdown();server.server_close();OUT.mkdir(parents=True,exist_ok=True)
    stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
    (OUT/(stamp+'-calibration-layout.json')).write_text(json.dumps({'passed':passed,'physicalPhone':False,'rows':rows},indent=2)+'\n',encoding='utf-8')
