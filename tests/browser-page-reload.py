#!/usr/bin/env python3
"""WEB-078 production App reload, synthetic transport. Not iPhone evidence."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import importlib.util,threading
from urllib.parse import urlsplit,parse_qs
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('fixture',ROOT/'tests/browser-vibe-display-smoke.py')
F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'src/main/webapp')))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  for engine in ('chromium','webkit'):
   browser=getattr(pw,engine).launch(headless=True,**({'executable_path':'/usr/local/bin/vibe-chromium','args':['--no-sandbox']} if engine=='chromium' else {}))
   context=browser.new_context(viewport={'width':393,'height':852},service_workers='block')
   context.add_init_script(F.INIT)
   page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   url=f'http://127.0.0.1:{server.server_port}/miniclient.html?app=1&ui=1280x720#retained'
   def navigation():
    parsed=urlsplit(page.url);original=urlsplit(url);q=parse_qs(parsed.query)
    assert parsed.netloc==original.netloc and parsed.path==original.path and parsed.fragment==original.fragment
    assert q['app']==['1'] and q['ui']==['1280x720'] and q['_vibeReload'][0].isdigit()
    assert page.evaluate("localStorage.getItem('owned-reload-test')")=='preserve'
    return q['_vibeReload'][0]
   def open_app():
    page.locator('#settingsToggle').click();page.locator('#settings-tab-app').click()
   page.goto(url,wait_until='domcontentloaded');page.wait_for_function('TEST.stream!==null')
   page.evaluate("localStorage.setItem('owned-reload-test','preserve')")
   open_app();page.locator('#appPortraitTopPx').fill('44')
   before=page.evaluate('performance.timeOrigin');page.locator('#appReloadPage').click()
   page.wait_for_function('(before)=>performance.timeOrigin!==before',arg=before)
   first_reload=navigation();current_url=page.url
   assert page.locator('#appPortraitTopPx').input_value()=='44'
   # WEB-126: X-menu force refresh shares the exact App action, no new icon.
   page.locator('#remoteToggle').click();page.locator('#closeRemote').click()
   assert page.evaluate('document.activeElement.id')=='cancelClientExit'
   before=page.evaluate('performance.timeOrigin');page.locator('#refreshClientPage').click()
   page.wait_for_function('(before)=>performance.timeOrigin!==before',arg=before)
   assert navigation()!=first_reload
   first_reload=navigation();current_url=page.url
   # A loaded/paused source still needs confirmation; Cancel must not alter
   # settings, source, native commands or navigate. No actual media fixture.
   page.evaluate("videoPlane.setAttribute('src','data:video/mp4;base64,AAAA')")
   open_app();before=page.evaluate('performance.timeOrigin')
   profile=page.evaluate("localStorage.getItem('sagetvWebMiniClientSettings.v1')")
   command_count=page.evaluate("TEST.requests.filter(r=>r[0]==='command').length")
   def cancel(dialog):
    assert dialog.type=='confirm' and 'Saved settings are kept' in dialog.message
    dialog.dismiss()
   page.once('dialog',cancel);page.locator('#appReloadPage').click()
   assert page.evaluate('performance.timeOrigin')==before
   assert page.url==current_url
   assert page.evaluate("videoPlane.getAttribute('src')")=='data:video/mp4;base64,AAAA'
   assert page.evaluate("localStorage.getItem('sagetvWebMiniClientSettings.v1')")==profile
   assert page.evaluate("TEST.requests.filter(r=>r[0]==='command').length")==command_count
   assert page.locator('#appReloadPage').is_enabled()
   page.once('dialog',lambda d:d.accept());page.locator('#appReloadPage').click()
   page.wait_for_function('(before)=>performance.timeOrigin!==before',arg=before)
   assert navigation()!=first_reload
   assert page.locator('#appPortraitTopPx').input_value()=='44'
   # A cancelled refresh in the X menu leaves playback and the menu intact.
   page.locator('#remoteToggle').click();page.locator('#closeRemote').click()
   page.evaluate("videoPlane.setAttribute('src','data:video/mp4;base64,AAAA')")
   before=page.evaluate('performance.timeOrigin')
   page.once('dialog',cancel);page.locator('#refreshClientPage').click()
   assert page.evaluate('performance.timeOrigin')==before
   assert page.locator('#exitClientDialog').evaluate('e=>e.open')
   page.locator('#cancelClientExit').click()
   assert not errors,errors
   print(f'PASS {engine}: distinct cache-busting reload preserves URL/settings; confirmation/Cancel/accept/no command leakage',flush=True)
   context.close();browser.close()
finally:server.shutdown();server.server_close()
