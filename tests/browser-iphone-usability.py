#!/usr/bin/env python3
"""WEB-024 production UI regressions; emulated browsers, not physical touch."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import os
from pathlib import Path
import threading
import time
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get('SAGETV_ARTIFACT_DIR', ROOT / 'artifacts/active/WEB-024'))
spec = importlib.util.spec_from_file_location('display', ROOT / 'tests/browser-vibe-display-smoke.py')
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT / 'src/main/webapp')))
threading.Thread(target=server.serve_forever, daemon=True).start()
results = []
complete = False
try:
    with sync_playwright() as pw:
        for engine in ('chromium', 'webkit'):
            options = {'headless': True}
            if engine == 'chromium':
                options.update(executable_path='/usr/local/bin/vibe-chromium', args=['--no-sandbox'])
            browser = getattr(pw, engine).launch(**options)
            for w, h in ((393, 852), (852, 393), (320, 568), (1440, 900)):
                context = browser.new_context(viewport={'width': w, 'height': h}, has_touch=w<900, service_workers='block')
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.add_init_script(fixture.INIT)
                page.goto(f'http://127.0.0.1:{server.server_port}/miniclient.html', wait_until='domcontentloaded')
                page.wait_for_function('window.TEST&&TEST.stream')
                assert page.locator('#appMenuBtn').is_hidden()
                page.locator('#remoteToggle').click()
                # Current phone layout intentionally collapses settings under
                # Gear. Exercise that visible control, not a hidden old icon.
                if page.locator('#remoteSettings').is_hidden():
                    page.locator('#phoneToolsToggle').click()
                page.locator('#remoteSettings').click()
                page.locator('#settings-tab-transcoding').click()
                page.wait_for_timeout(100)
                if w < 900:
                    sizes = page.locator('#closeSettings,#settings-tab-transcoding,#stream_player,#saveStreaming,#applyStreaming').evaluate_all('(els)=>els.map(e=>({id:e.id,h:e.getBoundingClientRect().height}))')
                    assert all(item['h'] >= 44 for item in sizes), sizes
                    # Physical iOS native selects override the CSS minimum.
                    # Ignoring that minimum must not shrink our explicit height.
                    forced = page.locator('#stream_player').evaluate('e=>{const previous=e.style.minHeight;try{e.style.minHeight="0px";return e.getBoundingClientRect().height}finally{e.style.minHeight=previous}}')
                    assert forced >= 44, forced
                    assert page.locator('#settingsCategories [role=tab]').count()==6
                    assert page.locator('.mc-setting-choice').count()==0
                    assert 'native HLS' in page.locator('#stream_player').get_attribute('title')
                    assert page.locator('#stream_player').evaluate('(e)=>e.labels[0].getBoundingClientRect().height') <=46 if w<521 else True
                # Category navigation must bring the requested end tab into view,
                # retain Back, and not apply/restart a stream merely by opening UI.
                before = page.evaluate('TEST.requests.filter(r=>r[0]==="streamSettings").length')
                page.locator('#settings-tab-diagnostics').click()
                assert page.locator('#supportPreferences').is_visible()
                page.locator('#settings-tab-playback').click()
                assert page.locator('#stream_audioTrack').is_visible()
                page.locator('#closeSettings').click()
                assert page.locator('#remotePanel').is_visible()
                assert page.locator('#remoteSettings').evaluate('(e)=>document.activeElement===e')
                assert page.evaluate('TEST.requests.filter(r=>r[0]==="streamSettings").length') == before
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                assert not errors, errors
                results.append({'engine': engine, 'viewport': [w, h], 'passed': True})
                print('PASS', engine, w, h, flush=True)
                context.close()
            browser.close()
    complete = True
finally:
    server.shutdown()
    server.server_close()
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    (OUT / (stamp + '-iphone-ui.json')).write_text(json.dumps({'passed': complete, 'syntheticTransport': True, 'physicalTouch': False, 'results': results}, indent=2)+'\n', encoding='utf-8')
