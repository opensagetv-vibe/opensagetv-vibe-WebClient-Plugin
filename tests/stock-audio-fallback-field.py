#!/usr/bin/env python3
"""Original UK audio fallback policies on an isolated stock232 browser client.

Actual production policy/encoder/browser output, not acoustic certification.
One Watch per isolated policy, no Seek/retry or saved household settings edits.
"""
import argparse, importlib.util, json, time
from pathlib import Path
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright
from bounded_browser_rpc import bounded

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('commission', ROOT/'scripts/commission-mobile.py')
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
cfg = C.configuration()
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--engine', choices=('chromium', 'webkit'), required=True)
p.add_argument('--policy', choices=('default', 'first', 'strict'), required=True)
a = p.parse_args()
identity = 'da92a86446be'
out = ROOT/'artifacts/active/WP12-001'; out.mkdir(parents=True, exist_ok=True)
stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
report = dict(passed=False, physicalPhone=False, acoustic=False,
              engine=a.engine, policy=a.policy, requestedLanguage='fra', rows=[])
owned = None; page = context = browser = pw = None; cleanup = []

def mcp(action, **values):
    return C.request(cfg, '/v1/control', dict(action=action, **values), mcp=True, timeout=30)

def api(action):
    return C.request(cfg, '/SageTVWebPlayer/api/miniclient?'+urlencode(dict(action=action, session=owned)))

def guard(own=False):
    state = C.activity(cfg)
    if state.get('recordingCount') != 0 or state.get('connectedClientCount') != 0:
        raise RuntimeError('Require no recordings or other clients')
    if mcp('ui.list').get('contexts') != ([identity] if own else []):
        raise RuntimeError('Exact owned UI requirement failed; no takeover')

def wait(check, label, seconds=60):
    end = time.monotonic()+seconds
    while time.monotonic() < end:
        if check(): return
        page.wait_for_timeout(150)
    raise RuntimeError('Timed out '+label+'; no replay')

def observe(response):
    global owned
    if '/api/miniclient' not in response.url or response.request.method != 'POST': return
    try:
        data = response.json()
        if data.get('clientId', '').replace(':', '').lower() == identity and data.get('session'):
            owned = data['session']
    except Exception: pass

def video():
    return page.evaluate("()=>{const v=videoPlane,s=__audioFallback;return{time:v.currentTime,frames:s.frames,sourceCurrent:s.source===v.currentSrc,width:v.videoWidth,paused:v.paused,ready:v.readyState,error:v.error?.code||null,prompt:!autoplayBtn.hidden}}")

try:
    guard()
    source = mcp('media.resolve_exact_path', path='/var/media/videos/USER_TEST/Breakfast-26711345-0.ts')
    if source.get('mediaFileId') != 11224: raise RuntimeError('Original fixture changed')
    pw = sync_playwright().start()
    browser = pw.webkit.launch(headless=True) if a.engine == 'webkit' else pw.chromium.launch(
        headless=True, executable_path='/usr/local/bin/vibe-chromium', args=['--no-sandbox'])
    context = browser.new_context(viewport={'width':852, 'height':393}, service_workers='block',
        http_credentials={'username':cfg['web_username'], 'password':cfg['web_password']})
    profile = dict(player='hls', videoMode='transcode', encoder='qsv', resolution='480',
        videoKbps=1200, audioCodec='aac', audioLanguage='fra', audioFallback=a.policy)
    context.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebStreaming.v1',"+json.dumps(json.dumps(profile))+");")
    page = context.new_page(); original_evaluate = page.evaluate
    page.evaluate = lambda *args, **kwargs: bounded(original_evaluate, *args, **kwargs)
    page.on('response', observe)
    page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html', wait_until='domcontentloaded')
    wait(lambda: owned and api('status').get('connection', {}).get('startupEvents', {}).get('firstFrameCompleted'), 'native first frame')
    guard(True)
    before = api('streamSettings').get('configured')
    if before.get('audioLanguage') != 'fra' or before.get('audioFallback') != a.policy:
        raise RuntimeError('Actual configured policy differs')
    saved = page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')")
    page.evaluate("()=>{const s=window.__audioFallback={frames:0,source:'',done:false};function f(){const source=videoPlane.currentSrc;videoPlane.requestVideoFrameCallback(()=>{if(s.done)return;if(source&&source===videoPlane.currentSrc){s.frames++;s.source=source}f()})}f()}")
    if not mcp('media.watch', context=identity, media_id=11224, wait_ms=0).get('accepted'):
        raise RuntimeError('One Watch rejected')
    if a.policy == 'strict':
        wait(lambda: page.evaluate("document.getElementById('osdMessage').textContent.includes('Preferred audio language fra is not available')"), 'explicit strict missing-language explanation', 35)
        state = api('streamSettings'); v = video()
        if state.get('active') is not None or state.get('session') or v['frames'] or not v['paused']:
            raise RuntimeError('Strict policy silently started a fallback')
        report['rows'].append(dict(gate='strict-missing-language-no-producer-no-picture', passed=True,
            explanationVisible=page.evaluate("document.body.textContent.includes('Preferred audio language fra is not available')")))
        if not report['rows'][-1]['explanationVisible']: raise RuntimeError('Strict explanation is hidden')
    else:
        activated = False; start = time.monotonic(); last = None
        while time.monotonic()-start < 70:
            last = video()
            if last['error']: raise RuntimeError('Actual browser decoder failed')
            if last['prompt'] and not activated:
                page.locator('#autoplayBtn').click(timeout=3000); activated = True
            if last['sourceCurrent'] and last['frames'] >= 12 and not last['paused'] and last['time'] > .3: break
            page.wait_for_timeout(150)
        else: raise RuntimeError('No advancing real output')
        state = api('streamSettings'); effective = state.get('active', {}).get('effective', {})
        expected = 4 if a.policy == 'default' else 1
        report['effective'] = effective
        if effective.get('audioStreamIndex') != expected:
            raise RuntimeError('Actual producer chose wrong fallback track')
        first = last; page.wait_for_timeout(2200); last = video()
        if last['frames'] <= first['frames']+10 or last['time'] <= first['time']+1:
            raise RuntimeError('Actual picture stopped advancing')
        report['rows'].append(dict(gate='missing-language-'+a.policy+'-actual-selected-output', passed=True,
            expectedTrack=expected, before=first, after=last))
    if api('streamSettings').get('configured') != before or page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')") != saved:
        raise RuntimeError('Saved/configured defaults changed')
    report['rows'].append(dict(gate='saved-and-configured-policy-preserved', passed=True))
    report['passed'] = True
except Exception as e:
    report['failure'] = dict(type=type(e).__name__, message=str(e)[:180] if isinstance(e, RuntimeError) else 'Bounded observation failed')
    if page:
        try: report['last'] = video()
        except Exception: pass
finally:
    if owned:
        try:
            guard(True)
            # A rejected producer can leave Core's selected MediaFile open.
            # Submit one public Stop before retiring our UI; never replay it.
            if mcp('ui.state', context=identity).get('fullyLoaded'):
                if not mcp('media.control', context=identity, operation='stop').get('accepted'):
                    raise RuntimeError('Native Stop rejected')
            if not C.request(cfg, '/SageTVWebPlayer/api/miniclient', dict(action='stop', session=owned)).get('ok'):
                cleanup.append('Owned Stop unacknowledged')
        except Exception: cleanup.append('Owned Stop unknown; not replayed')
    for resource in (context, browser, pw):
        if resource:
            try: bounded(resource.stop if resource is pw else resource.close)
            except Exception: cleanup.append('Browser shutdown unknown')
    if owned:
        end=time.monotonic()+90
        while time.monotonic()<end:
            if identity not in mcp('ui.list').get('contexts', []): break
            time.sleep(.3)
        else: cleanup.append('Native retirement unknown')
    report['cleanup'] = cleanup
    report['passed'] = report['passed'] and not cleanup
    path = out/(stamp+'-'+a.engine+'-'+a.policy+'-audio-fallback.json')
    path.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(passed=report['passed'], rows=len(report['rows']), report=str(path), failure=report.get('failure'), cleanup=cleanup)), flush=True)
raise SystemExit(0 if report['passed'] else 1)
