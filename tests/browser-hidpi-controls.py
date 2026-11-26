#!/usr/bin/env python3
"""WEB-027/028 production browser shell, synthetic SageTV, not HDMI proof."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import importlib.util
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('display',ROOT/'tests/browser-vibe-display-smoke.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'src/main/webapp')))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
  with sync_playwright() as pw:
    for engine in ('chromium','webkit'):
      opts={'headless':True}
      if engine=='chromium':opts.update(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
      browser=getattr(pw,engine).launch(**opts)
      for w,h,expected in ((852,393,[1704,786]),(393,793,[536,1080])):
        context=browser.new_context(viewport={'width':w,'height':h},device_scale_factor=3,has_touch=True,service_workers='block')
        page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.add_init_script(fixture.INIT)
        page.add_init_script("Object.defineProperty(navigator,'standalone',{configurable:true,value:true})")
        page.goto(f'http://127.0.0.1:{server.server_port}/miniclient.html',wait_until='domcontentloaded')
        page.wait_for_function('TEST.stream!==null')
        assert page.locator('#appMenuBtn').is_hidden()
        page.wait_for_function('size=>{const c=document.querySelector("#gfxCanvas");return c.width===size[0]&&c.height===size[1]}',arg=expected,timeout=5000)
        assert page.locator('#gfxCanvas').evaluate('e=>[e.width,e.height]')==expected
        assert page.locator('#gfxCanvas').bounding_box()['width']==w
        b=page.locator('#gfxCanvas').bounding_box();x=b['width']/2;y=b['height']/2
        before=page.evaluate("TEST.requests.filter(r=>r[0]==='click').length")
        event={'pointerId':42,'pointerType':'touch','isPrimary':True,'button':0,'clientX':x,'clientY':y}
        page.dispatch_event('#gfxCanvas','pointerdown',event);page.wait_for_timeout(650)
        page.dispatch_event('#gfxCanvas','pointerup',event)
        assert page.locator('#remotePanel').is_visible()
        assert page.evaluate("TEST.requests.filter(r=>r[0]==='click').length")==before
        page.locator('#phoneToolsToggle').click();page.locator('#remoteSettings').click();page.locator('#settings-tab-app').click()
        page.locator('#appShowControls').check();page.locator('#closeSettings').click();page.locator('#hideRemote').click()
        assert page.locator('#appMenuBtn').is_visible()
        page.reload(wait_until='domcontentloaded');page.wait_for_function('TEST.stream!==null')
        assert page.locator('#appMenuBtn').is_visible()
        page.locator('#appMenuBtn').click();page.locator('#phoneToolsToggle').click();page.locator('#remoteSettings').click();page.locator('#settings-tab-app').click()
        page.locator('#appShowControls').uncheck();page.locator('#closeSettings').click();page.locator('#hideRemote').click()
        assert page.locator('#appMenuBtn').is_hidden()
        assert not errors,errors
        print('PASS',engine,w,h,'DPR3 bounded UI, hidden launcher, long touch, persisted optional fallback',flush=True)
        context.close()
      browser.close()
finally:
  server.shutdown();server.server_close()
