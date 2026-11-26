#!/usr/bin/env python3
"""WEB-030/031 production UI, synthetic transport; not trusted iPhone touch."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
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
      options={'headless':True}
      if engine=='chromium':options.update(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
      browser=getattr(pw,engine).launch(**options)
      for width,height in ((393,852),(852,393)):
        context=browser.new_context(viewport={'width':width,'height':height},screen={'width':393,'height':852},device_scale_factor=3,has_touch=True,service_workers='block')
        context.add_init_script(fixture.INIT)
        context.add_init_script("localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify({resolution:'480',videoKbps:1000,videoMode:'transcode'}))")
        page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(f'http://127.0.0.1:{server.server_port}/miniclient.html',wait_until='domcontentloaded')
        page.wait_for_function('TEST.stream!==null')
        before=page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')")
        for entry in ('toolbar','video'):
          if entry=='toolbar':page.locator('#settingsToggle').click()
          else:
            page.locator('#remoteToggle').click()
            if not page.locator('#remoteSettings').is_visible():page.locator('#phoneToolsToggle').click()
            page.locator('#remoteSettings').click()
          assert page.evaluate('document.activeElement.id')=='closeSettings'
          assert page.locator('#stream_player').input_value()=='auto'
          assert page.locator('#stream_resolution').input_value()=='480'
          page.locator('#closeSettings').click()
          if page.locator('#remotePanel').is_visible():page.locator('#hideRemote').click()
        assert page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')")==before
        assert page.evaluate("TEST.requests.filter(r=>r[0]==='streamSettings'&&r[1].applyNow!==undefined).length")==0
        page.locator('#settingsToggle').click()
        page.locator('#settings-tab-transcoding').click()
        assert '1080p device limit' in page.locator('#stream_resolution option[value=auto]').text_content()
        page.locator('#stream_resolution').select_option('auto')
        page.locator('#saveStreaming').click()
        page.wait_for_function("JSON.parse(localStorage.getItem('sagetvWebStreaming.v1')).resolution==='auto'")
        sent=page.evaluate("TEST.requests.filter(r=>r[0]==='streamSettings'&&r[1].applyNow!==undefined).at(-1)[1]")
        assert sent['stream_resolution']=='1080' and sent['applyNow']=='false',sent
        page.locator('#closeSettings').click();page.locator('#settingsToggle').click()
        page.locator('#settings-tab-transcoding').click()
        assert page.locator('#stream_resolution').input_value()=='auto'
        assert page.evaluate('document.activeElement.id')=='settings-tab-transcoding'
        page.set_viewport_size({'width':height,'height':width});page.wait_for_timeout(150)
        assert '1080p device limit' in page.locator('#stream_resolution option[value=auto]').text_content()
        assert len(page.evaluate("TEST.requests.filter(r=>r[0]==='streamSettings'&&r[1].applyNow!==undefined)"))==1
        assert not errors,errors
        print('PASS',engine,width,height,'neutral focus/unchanged first entry, portable Auto1080, no rotation Apply',flush=True)
        context.close()
      browser.close()
finally:
  server.shutdown();server.server_close()
