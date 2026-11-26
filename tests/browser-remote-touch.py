#!/usr/bin/env python3
"""Production touch remote, mocked transport; not physical Safari acceptance."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import importlib.util, json, os, threading, time
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ['SAGETV_ARTIFACT_DIR']);OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('display_fixture',ROOT/'tests/browser-vibe-display-smoke.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'src/main/webapp')))
threading.Thread(target=server.serve_forever,daemon=True).start()
results=[];complete=False
try:
    with sync_playwright() as pw:
        for engine in ('chromium','webkit'):
            browser=getattr(pw,engine).launch(headless=True,**({'executable_path':'/usr/local/bin/vibe-chromium','args':['--no-sandbox']} if engine=='chromium' else {}))
            context=browser.new_context(viewport={'width':852,'height':393},has_touch=True,is_mobile=True,device_scale_factor=3,service_workers='block')
            page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.add_init_script(fixture.INIT)
            page.goto('http://127.0.0.1:'+str(server.server_port)+'/miniclient.html')
            page.wait_for_function("window.TEST&&TEST.stream&&document.querySelector('#connectionStatus').textContent.startsWith('Connected')")
            page.locator('#remoteToggle').click()
            page.evaluate("""()=>{window.remoteEvents=[];for(const name of ['pointerdown','pointerup','pointercancel','click'])document.getElementById('remotePanel').addEventListener(name,e=>remoteEvents.push({type:e.type,detail:e.detail,pointerType:e.pointerType,target:e.target.closest('button')?.id,at:performance.now()}),true);TEST.requests=[];}""")
            for button in ('nav_down','nav_down','nav_up','nav_up'):
                page.locator('#'+button+' img').tap();page.wait_for_timeout(80)
            page.wait_for_timeout(100)
            commands=page.evaluate("TEST.requests.filter(r=>r[0]==='command').map(r=>+r[1].command)")
            events=page.evaluate('remoteEvents')
            results.append({'engine':engine,'commands':commands,'events':events,'errors':errors})
            assert commands==[5,5,4,4],results[-1]
            assert not errors,errors
            print('PASS '+engine+' four real browser touch taps produce exactly four ordered commands',flush=True)
            context.close();browser.close()
    complete=True
finally:
    server.shutdown();server.server_close()
    (OUT/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-remote-touch.json')).write_text(json.dumps({'passed':complete,'syntheticTransport':True,'physicalIPhone':False,'results':results},indent=2)+'\n')
