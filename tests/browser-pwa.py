#!/usr/bin/env python3
"""Real service-worker/cache/manifest tests. Synthetic SageTV; not iPhone proof."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import importlib.util,json,os,threading,time,socket,re
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=Path(os.getenv('SAGETV_ARTIFACT_DIR',str(ROOT/'artifacts/active/WEB-019')));OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('display',ROOT/'tests/browser-vibe-display-smoke.py');fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
class Handler(SimpleHTTPRequestHandler):
    network_down=False
    extensions_map={**SimpleHTTPRequestHandler.extensions_map,'.webmanifest':'application/manifest+json'}
    def log_message(self,*args):pass
    def do_GET(self):
        if self.network_down:
            self.connection.shutdown(socket.SHUT_RDWR);self.connection.close();return
        super().do_GET()
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'src/main/webapp')));threading.Thread(target=server.serve_forever,daemon=True).start()
origin='http://127.0.0.1:'+str(server.server_port);results=[];completed=False
expected_cache=re.search(r"const CACHE='([^']+)'",(ROOT/'src/main/webapp/sw.js').read_text()).group(1)
def passed(engine,gate):results.append({'engine':engine,'gate':gate,'passed':True});print('PASS',engine,gate,flush=True)
try:
  with sync_playwright() as pw:
    for engine in ('chromium','webkit'):
      browser=getattr(pw,engine).launch(headless=True,**({'executable_path':'/usr/local/bin/vibe-chromium','args':['--no-sandbox']} if engine=='chromium' else {}))
      context=browser.new_context(viewport={'width':390,'height':844},has_touch=True,service_workers='allow');page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
      page.add_init_script('window.networkFetch=window.fetch.bind(window);'+fixture.INIT)
      page.add_init_script("""window.LEASE={requested:0,released:0};Object.defineProperty(navigator,'wakeLock',{configurable:true,value:{request:async()=>{LEASE.requested++;return {release:async()=>{LEASE.released++;}};}}});""")
      page.goto(origin+'/miniclient.html?app=1',wait_until='domcontentloaded')
      assert page.locator('#appMenuBtn').is_hidden()
      manifest=page.evaluate("async()=>{const link=document.querySelector('link[rel=manifest]');return await(await networkFetch(link.href)).json()}")
      assert manifest['display']=='standalone' and manifest['start_url'].endswith('miniclient.html?app=1')
      assert page.locator('meta[name=apple-mobile-web-app-capable]').get_attribute('content')=='yes'
      passed(engine,'actual MiniClient manifest, standalone start and Apple metadata')
      page.wait_for_function("navigator.serviceWorker.controller!==null",timeout=20000)
      entries=page.evaluate("async key=>{if(!(await caches.keys()).includes(key))throw Error('Current shell cache absent');return (await(await caches.open(key)).keys()).map(r=>r.url)}",expected_cache)
      assert any('miniclient-input.js' in x for x in entries) and any('last_channel.svg' in x for x in entries)
      assert any('miniclient-experience.js' in x for x in entries)
      assert not any('/api/' in x or '/hls/' in x or '/vendor/' in x for x in entries)
      passed(engine,'service worker installs complete current shell, no API/media/vendor cache')
      page.locator('#installApp').click();assert 'Add to Home Screen' in page.locator('#pwaInstallHelp').text_content()
      page.keyboard.press('Escape');page.locator('#hideRemote').click();page.locator('#settingsToggle').click()
      page.locator('#settings-tab-app').click()
      page.locator('#appKeepAwake').check()
      page.evaluate("()=>{const v=document.querySelector('#videoPlane');Object.defineProperty(v,'paused',{configurable:true,get:()=>false});v.dispatchEvent(new Event('playing'));}")
      page.wait_for_function('LEASE.requested===1');page.evaluate("()=>{Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'));}")
      page.wait_for_function('LEASE.released===1');passed(engine,'explicit wake lock releases on background, no silent-audio workaround')
      # A real failed HTTP connection exercises SW fetch fallback in both engines.
      # Playwright's WebKit setOffline/reload can abort before its SW runs.
      page.locator('#appShowControls').check()
      Handler.network_down=True;page.reload(wait_until='domcontentloaded')
      # Portrait defaults to the content deck; native Controls remain optional.
      # The persisted launcher preference still survives an offline shell load.
      assert page.locator('#appShowControls').is_checked()
      assert page.locator('#mobileDock').is_visible() if page.locator('body.mc-portrait-dock').count() else page.locator('#appMenuBtn').is_visible()
      try:page.evaluate("networkFetch('/api/not-cached').then(()=>true,()=>false)")
      except Exception:pass
      assert not page.evaluate("async()=>(await caches.match('/api/not-cached'))!==undefined")
      passed(engine,'versioned MiniClient shell reloads offline; live API remains uncached')
      Handler.network_down=False;assert not errors,errors;context.close();browser.close()
    completed=True
finally:
  server.shutdown();server.server_close();(OUT/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-pwa.json')).write_text(json.dumps({'passed':completed,'syntheticSageTV':True,'physicalIPhone':False,'results':results},indent=2)+'\n')
