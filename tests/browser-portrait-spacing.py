#!/usr/bin/env python3
"""WEB-077 production shell/settings; synthetic server, not physical iPhone."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import importlib.util, threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('fixture',ROOT/'tests/browser-vibe-display-smoke.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'src/main/webapp')))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  for engine in ('chromium','webkit'):
   browser=getattr(pw,engine).launch(headless=True,**({'executable_path':'/usr/local/bin/vibe-chromium','args':['--no-sandbox']} if engine=='chromium' else {}))
   for standalone in (False,True):
    context=browser.new_context(viewport={'width':393,'height':852},has_touch=True,service_workers='block')
    context.add_init_script(fixture.INIT)
    context.add_init_script('Object.defineProperty(navigator,"standalone",{value:'+str(standalone).lower()+'})')
    page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(f'http://127.0.0.1:{server.server_port}/miniclient.html',wait_until='domcontentloaded')
    page.wait_for_function('TEST.stream!==null')
    page.evaluate("document.documentElement.style.setProperty('--mobile-safe-top','59px')")
    base=59 if standalone else 0
    assert abs(page.locator('#app').evaluate('e=>parseFloat(getComputedStyle(e).paddingTop)')-base-24)<1
    header=page.locator('.mc-toolbar').bounding_box()
    origin=base+(header['height'] if header else 0)
    assert abs(page.locator('#stage').bounding_box()['y']-origin-24)<1
    if standalone:
     page.locator('#mobileTab-controls').click()
     page.locator('#phoneToolsToggle').click();page.locator('#remoteSettings').click()
    else:page.locator('#settingsToggle').click()
    page.locator('#settings-tab-app').click()
    assert page.evaluate('document.activeElement.id')!='appPortraitTopPx'
    field=page.locator('#appPortraitTopPx');assert field.input_value()=='24'
    box=field.bounding_box();label=page.locator('.mc-portrait-spacing').bounding_box();note=page.locator('.mc-portrait-spacing small').bounding_box()
    assert box['x']+box['width']<=label['x']+label['width']+1
    assert note['y']>=box['y']+box['height'] and abs(note['width']-label['width'])<1
    before=page.evaluate('JSON.stringify(TEST.requests)')
    field.fill('48')
    assert abs(page.locator('#stage').bounding_box()['y']-origin-48)<1
    assert page.evaluate('JSON.stringify(TEST.requests)')==before # no Watch/seek/quality/restart
    assert page.evaluate("localStorage.getItem('vibeWebApp.portraitTopPx.v1')")=='48'
    # Shared stage moves but picture aspect and canvas/video alignment do not.
    stage=page.locator('#stage').bounding_box();canvas=page.locator('#gfxCanvas').bounding_box()
    assert abs(stage['width']/stage['height']-16/9)<.02
    assert abs(stage['y']-canvas['y'])<1
    field.fill('0');assert abs(page.locator('#stage').bounding_box()['y']-origin)<1
    field.fill('999');field.dispatch_event('change');assert field.input_value()=='160'
    field.fill('');field.dispatch_event('change');assert field.input_value()=='24'
    page.evaluate("window.dispatchEvent(new CustomEvent('vibe:app-preferences',{detail:{portraitTopPx:36}}))")
    assert field.input_value()=='36'
    page.reload(wait_until='domcontentloaded');page.wait_for_function('TEST.stream!==null')
    assert field.input_value()=='36'
    page.set_viewport_size({'width':852,'height':393});page.wait_for_timeout(200)
    assert page.locator('#app').evaluate('e=>getComputedStyle(e).paddingTop')=='0px'
    page.set_viewport_size({'width':393,'height':852});page.wait_for_timeout(200)
    assert page.locator('#app').evaluate('e=>parseFloat(getComputedStyle(e).paddingTop)')>=36
    # A broken stored value cannot inject CSS or hide the stage.
    page.evaluate("localStorage.setItem('vibeWebApp.portraitTopPx.v1','not-a-number')")
    page.reload(wait_until='domcontentloaded');assert field.input_value()=='24'
    assert not errors,errors
    print(f'PASS {engine} standalone={standalone}: default/live/zero/clamp/profile/reload/rotation/no playback mutation',flush=True)
    context.close()
   browser.close()
finally:server.shutdown();server.server_close()
