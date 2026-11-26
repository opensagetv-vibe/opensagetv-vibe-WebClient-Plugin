#!/usr/bin/env python3
"""Production HTTP shell/keyboard/touch tests; synthetic SageTV transport.

Chromium/WebKit emulation is NOT physical Safari/Home Screen/media acceptance.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import importlib.util, json, os, threading, time
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ.get('SAGETV_ARTIFACT_DIR',ROOT/'artifacts/active/WEB-018'))
OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('display_fixture',ROOT/'tests/browser-vibe-display-smoke.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'src/main/webapp')))
threading.Thread(target=server.serve_forever,daemon=True).start()
origin='http://127.0.0.1:'+str(server.server_port)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());results=[];completed=False;page=None
def passed(engine,label):
    results.append({'engine':engine,'gate':label,'passed':True});print('PASS',engine,label,flush=True)
def commands(page):return page.evaluate("TEST.requests.filter(r=>r[0]==='command').map(r=>Number(r[1].command))")
try:
  with sync_playwright() as pw:
    for name in ('chromium','webkit'):
      kind=getattr(pw,name)
      try:browser=kind.launch(headless=True,**({'executable_path':os.environ.get('CHROMIUM_PATH','/usr/local/bin/vibe-chromium'),'args':['--no-sandbox']} if name=='chromium' else {}))
      except Exception as error:
        if name!='webkit':raise
        results.append({'engine':name,'passed':False,'status':'UNAVAILABLE','reason':str(error).splitlines()[0]});print('UNAVAILABLE WebKit',flush=True);continue
      for width,height in ((1440,900),(390,844),(844,390),(320,667)):
        context=browser.new_context(viewport={'width':width,'height':height},has_touch=width<900,service_workers='block')
        page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.add_init_script(fixture.INIT)
        page.goto(origin+'/miniclient.html',wait_until='domcontentloaded')
        page.wait_for_function("window.TEST&&TEST.stream&&document.querySelector('#connectionStatus').textContent.startsWith('Connected')")
        page.locator('#remoteToggle').focus();before=len(commands(page));page.keyboard.press('ArrowRight')
        page.wait_for_function('(n)=>TEST.requests.filter(r=>r[0]===\'command\').length>n',arg=before)
        assert commands(page)[-1]==3
        passed(name,f'{width}x{height} toolbar focus keeps remote keyboard working')
        page.locator('#remoteToggle').click();page.locator('#nav_pgup').focus();before=commands(page)
        page.keyboard.press('ArrowDown');assert page.locator('#nav_last').evaluate('(el)=>document.activeElement===el')
        page.keyboard.press('ArrowDown');assert page.locator('#nav_pgdn').evaluate('(el)=>document.activeElement===el')
        assert commands(page)==before
        page.keyboard.press('ArrowUp');page.keyboard.press('Enter');page.wait_for_timeout(100);assert commands(page)[-1]==60
        passed(name,f'{width}x{height} overlay arrows own focus, Last activates once')
        if page.locator('#phoneToolsToggle').is_visible():page.locator('#phoneToolsToggle').click()
        page.locator('#remoteSettings').click();assert page.locator('#stream_audioCodec').is_hidden()
        assert page.locator('#browserPlaybackRate').is_visible();page.locator('#videoTranscoding').click()
        assert page.locator('#stream_player').is_visible() and page.locator('#stream_encoder').is_visible() and page.locator('#stream_audioCodec').is_visible()
        page.locator('#closeSettings').click();assert page.locator('#remotePanel').is_visible()
        assert page.locator('#remoteSettings').evaluate('(el)=>document.activeElement===el')
        page.locator('#audioSettings').click();assert page.locator('#stream_audioTrack').is_visible() and page.locator('#stream_videoMode').is_hidden()
        page.locator('#audioOffsetOpen').click();page.keyboard.press('ArrowRight');assert page.locator('#audioOffsetRange').input_value()=='25'
        page.keyboard.press('End');assert page.locator('#audioOffsetRange').input_value()=='4000'
        page.keyboard.press('Home');assert page.locator('#audioOffsetRange').input_value()=='-4000'
        page.keyboard.press('Enter');assert page.locator('#audioOffsetRange').input_value()=='0'
        page.keyboard.press('ArrowLeft');page.keyboard.press('Escape')
        assert page.locator('#audioOffsetPanel').is_hidden() and page.locator('#stream_audioOffsetMs').input_value()=='-25'
        passed(name,f'{width}x{height} audio slider25ms bounds/reset/Back returns to Audio')
        page.keyboard.press('Escape');assert page.locator('#remotePanel').is_visible()
        passed(name,f'{width}x{height} compact scoped settings return to parent/icon')
        page.locator('#keyboardToggle').click();before=commands(page);page.locator('#keyboardInput').fill('Vibe café')
        page.keyboard.press('ArrowLeft');assert commands(page)==before
        page.locator('#keyboardSend').click();page.wait_for_timeout(50)
        assert page.evaluate("TEST.requests.filter(r=>r[0]==='text').at(-1)[1].text")=='Vibe café'
        page.keyboard.press('Escape');page.locator('#hideRemote').click()
        passed(name,f'{width}x{height} literal mobile text stays separate from remote shortcuts')
        page.locator('#settingsToggle').click();page.locator('#settings-tab-input').click()
        page.locator('#mappingKey').select_option('ArrowRight');page.locator('#mappingPress').select_option('62');page.locator('#mappingHold').select_option('remote');page.locator('#closeSettings').click()
        page.locator('#remoteToggle').focus();page.keyboard.press('ArrowRight');page.wait_for_timeout(30);assert commands(page)[-1]==62
        before=commands(page);page.keyboard.down('ArrowRight');page.wait_for_timeout(500);page.keyboard.up('ArrowRight')
        assert page.locator('#remotePanel').is_visible() and commands(page)==before
        if page.locator('#phoneToolsToggle').is_visible():page.locator('#phoneToolsToggle').click()
        page.locator('#remoteSettings').click();page.locator('#settings-tab-input').click();page.locator('#resetInputMappings').click();page.locator('#closeSettings').click();page.locator('#hideRemote').click()
        passed(name,f'{width}x{height} configurable press/hold never emits both actions')
        box=page.locator('#gfxCanvas').bounding_box();x=box['x']+box['width']/2;y=box['y']+box['height']/2
        before=len(page.evaluate("TEST.requests.filter(r=>r[0]==='click')"))
        page.dispatch_event('#gfxCanvas','pointerdown',{'pointerId':42,'pointerType':'touch','isPrimary':True,'button':0,'clientX':x,'clientY':y})
        page.wait_for_timeout(650)
        page.dispatch_event('#gfxCanvas','pointerup',{'pointerId':42,'pointerType':'touch','isPrimary':True,'button':0,'clientX':x,'clientY':y})
        assert page.locator('#remotePanel').is_visible()
        assert len(page.evaluate("TEST.requests.filter(r=>r[0]==='click')"))==before
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert page.locator('#nav_last img').evaluate('(el)=>el.complete&&el.naturalWidth>0')
        passed(name,f'{width}x{height} long-touch opens without selecting behind overlay; icons fit')
        page.screenshot(path=str(OUT/(stamp+'-'+name+'-'+str(width)+'-controls.png')))
        assert not errors,errors;context.close()
      browser.close()
    completed=True
except Exception:
  if page and not page.is_closed():page.screenshot(path=str(OUT/(stamp+'-failure.png')))
  raise
finally:
  server.shutdown();server.server_close()
  (OUT/(stamp+'-browser-mobile.json')).write_text(json.dumps({'passed':completed,'syntheticTransport':True,'physicalIPhone':False,'results':results},indent=2)+'\n')
