#!/usr/bin/env python3
"""Actual production mapping editor/DOM input; synthetic SageTV transport."""
import importlib.util
import json
import os
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get('SAGETV_ARTIFACT_DIR', ROOT / 'artifacts/active/WEB-112')).resolve()
if not OUT.is_relative_to((ROOT / 'artifacts/active').resolve()):
    raise RuntimeError('Owning active task output required')
OUT.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location('fixture', ROOT / 'tests/browser-vibe-display-smoke.py')
F = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F)


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_): pass


server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT / 'src/main/webapp')))
threading.Thread(target=server.serve_forever, daemon=True).start()
rows = []
passed = False
stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
mapping = dict(BrowserSearch='40', Delete='83', Insert='none', ColorF0Red='28', ColorF1Green='24',
               ColorF2Yellow='18', ColorF3Blue='29', ChannelUp='11', ChannelDown='12')
try:
    with sync_playwright() as pw:
        for engine in ('chromium', 'webkit'):
            browser = getattr(pw, engine).launch(headless=True, **(
                dict(executable_path=os.environ.get('CHROMIUM_PATH', '/usr/local/bin/vibe-chromium'), args=['--no-sandbox']) if engine == 'chromium' else {}))
            context = browser.new_context(viewport=dict(width=1280, height=800), service_workers='block')
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.add_init_script(F.INIT)
            page.goto('http://127.0.0.1:' + str(server.server_port) + '/miniclient.html')
            page.wait_for_function("window.TEST&&TEST.stream&&connectionStatus.textContent.startsWith('Connected')")
            def commands(): return page.evaluate("TEST.requests.filter(r=>r[0]==='command').map(r=>Number(r[1].command))")
            def dispatch(key, **extra):
                page.dispatch_event('#stage', 'keydown', dict(key=key, code=key, bubbles=True, cancelable=True, **extra))
                page.dispatch_event('#stage', 'keyup', dict(key=key, code=key, bubbles=True, cancelable=True))
                page.wait_for_timeout(80)
            for key in mapping:
                before = commands()
                dispatch(key)
                assert commands() == before, (engine, key, 'new default must stay inert')
            rows.append(dict(engine=engine, gate='all-nine-new-defaults-inert', passed=True))
            page.locator('#settingsToggle').click()
            page.locator('#settings-tab-input').click()
            for key, action in mapping.items():
                page.locator('#mappingKey').select_option(key)
                page.locator('#mappingPress').select_option(action)
            page.locator('#closeSettings').click()
            page.locator('#stage').focus()
            for key, action in mapping.items():
                before = commands()
                dispatch(key)
                assert commands() == before + ([] if action == 'none' else [int(action)]), (engine, key, commands())
                rows.append(dict(engine=engine, gate='one-explicit-' + key, passed=True))
            # Input fields and modifier combinations retain normal browser/IME
            # ownership; a configured Delete must not escape a text field.
            before = commands()
            dispatch('Delete', ctrlKey=True)
            page.locator('#settingsToggle').click()
            page.locator('#settings-tab-input').click()
            page.dispatch_event('#mappingKey', 'keydown', dict(key='Delete', bubbles=True, cancelable=True))
            assert commands() == before
            page.locator('#closeSettings').click()
            page.locator('#stage').focus()
            dispatch('Backspace')
            assert commands() == before + [75], 'Existing Backspace=Back must not change'
            rows.append(dict(engine=engine, gate='modifier-editor-and-existing-backspace-ownership', passed=True))
            page.reload()
            page.wait_for_function("window.TEST&&TEST.stream&&connectionStatus.textContent.startsWith('Connected')")
            page.locator('#stage').focus()
            before = commands()
            dispatch('BrowserSearch')
            assert commands() == before + [40], 'Explicit mapping must persist'
            assert not errors, errors
            rows.append(dict(engine=engine, gate='mapping-persists-after-real-reload', passed=True))
            context.close()
            browser.close()
            print('PASS ' + engine + ' configurable special keys/defaults/ownership/persistence', flush=True)
    passed = True
finally:
    server.shutdown()
    server.server_close()
    (OUT / (stamp + '-special-keys.json')).write_text(json.dumps(dict(passed=passed, syntheticTransport=True,
        physicalIPhone=False, rows=rows), indent=2) + '\n', encoding='utf-8')
