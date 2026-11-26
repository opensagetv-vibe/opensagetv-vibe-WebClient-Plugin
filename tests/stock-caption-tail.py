#!/usr/bin/env python3
"""Focused real desktop comparison for WP04's unresolved native tail stall.

No phone access and no claim this MSE comparison fixes native Safari. Watch
only the exact generated fixture, issue each48/5/60s seek once, require actual
new frames and ended, and preserve failure producer/buffer status before Stop.
"""
import argparse
import importlib.util
import json
import time
from pathlib import Path
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright
from playback_activity import observe_idle_phone_field

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('commission', ROOT / 'scripts/commission-mobile.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
cfg = C.configuration()
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--engine', choices=('chromium', 'webkit'), required=True)
p.add_argument('--allow-idle-phone', action='store_true', help='Preserve the exact verified idle commissioned phone; no restart authority')
args = p.parse_args()
identity = 'da92a86446be'
fixture = '/var/media/OpenSageTV_Vibe_Tests/WP04-Caption-PMT/VibeCaptions-English-Spanish-PMT.ts'
out = ROOT / 'artifacts/active/WEB-111'
out.mkdir(parents=True, exist_ok=True)
stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
report = dict(passed=False, engine=args.engine, physicalPhone=False, nativeSafari=False,
              generatedSource=True, orderedInputReplayed=False, rows=[], cleanup=[], errors=[])
owned = page = context = browser = pw = None
native_stop = session_stop = activated = False


def mcp(action, **values):
    return C.request(cfg, '/v1/control', dict(action=action, **values), mcp=True, timeout=30)


def api(action, **values):
    params = dict(action=action, session=owned, **values)
    if action in ('status', 'streamSettings') and not values:
        return C.request(cfg, '/SageTVWebPlayer/api/miniclient?' + urlencode(params))
    return C.request(cfg, '/SageTVWebPlayer/api/miniclient', params)


def observed(response):
    global owned
    if '/api/miniclient' not in response.url or response.request.method != 'POST':
        return
    try:
        value = response.json()
        if value.get('clientId', '').replace(':', '').lower() == identity and value.get('session'):
            owned = value['session']
    except Exception:
        pass


def sample():
    return page.evaluate('''()=>{const v=videoPlane,s=TAIL_FIELD,c=dvbCaptions,
      p=c.getContext('2d').getImageData(0,0,c.width,c.height).data;
      let pixels=0;for(let i=3;i<p.length;i+=4)if(p[i])pixels++;
      return {time:v.currentTime,frames:s.frames,source:s.source,current:s.source===v.currentSrc,
        assigned:!!v.getAttribute('src'),paused:v.paused,ended:v.ended,endedEvents:s.ended,
        ready:v.readyState,error:v.error?.code||null,prompt:!autoplayBtn.hidden,
        visibility:document.visibilityState,pixels,message:osdMessage.textContent,
        buffered:Array.from({length:v.buffered.length},(_,i)=>[v.buffered.start(i),v.buffered.end(i)]),
        playback:s.player?.snapshot()}}''')


def wait(check, label, seconds=45):
    global activated
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        page.wait_for_timeout(150)
        if check():
            return
        if page.locator('#autoplayBtn').is_visible() and not activated:
            activated = True
            page.locator('#autoplayBtn').click()
    raise RuntimeError('Timed out ' + label + '; ordered controls are not replayed')


try:
    activity = C.activity(cfg)
    report['preflight'] = observe_idle_phone_field(activity, mcp('ui.list').get('contexts'),
        lambda name: mcp('ui.state', context=name), args.allow_idle_phone)
    media = mcp('media.resolve_exact_path', path=fixture)
    mid = media.get('mediaFileId')
    if mid != 84502:
        raise RuntimeError('Canonical generated media ID changed')
    info = C.request(cfg, '/SageTVWebPlayer/api/media?id=' + str(mid))
    files = info.get('files', [])
    if info.get('recording') or len(files) != 1 or files[0].get('path') != fixture or files[0].get('streamSize') != 17576496:
        raise RuntimeError('Canonical generated file identity changed')
    pw = sync_playwright().start()
    browser = pw.webkit.launch(headless=True) if args.engine == 'webkit' else pw.chromium.launch(
        headless=True, executable_path='/usr/local/bin/vibe-chromium', args=['--no-sandbox'])
    context = browser.new_context(viewport=dict(width=852, height=393), service_workers='block',
                                  http_credentials=dict(username=cfg['web_username'], password=cfg['web_password']))
    profile = dict(player='hls', videoMode='transcode', encoder='qsv', allowFallback=True,
                   videoKbps=1000, resolution='480', deinterlace='off', captionAuthority='stv', captions='608', captionService=1)
    authority = dict(mode='stv', cc1Type='dvb', cc1Language='eng', cc2Type='dvb', cc2Language='spa')
    context.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');"
        "localStorage.setItem('sagetvWebStreaming.v1'," + json.dumps(json.dumps(profile)) + ");"
        "localStorage.setItem('sagetvWebCaptionAuthority.v1'," + json.dumps(json.dumps(authority)) + ");")
    page = context.new_page()
    page.on('response', observed)
    page.on('pageerror', lambda error: report['errors'].append(str(error)))
    page.goto(cfg['web_base_url'].rstrip('/') + '/SageTVWebPlayer/miniclient.html', wait_until='domcontentloaded')
    wait(lambda: owned is not None and api('status').get('connection', {}).get('startupEvents', {}).get('firstFrameCompleted'), 'owned UI')
    saved = page.evaluate('JSON.stringify(localStorage)')
    configured = api('streamSettings')['configured']
    page.evaluate('''()=>{const s=window.TAIL_FIELD={frames:0,source:'',ended:0,player:null};
      const start=SageMiniPlayback.prototype.start;SageMiniPlayback.prototype.start=function(...a){s.player=this;return start.apply(this,a)};
      videoPlane.addEventListener('ended',()=>s.ended++);
      const f=()=>{const source=videoPlane.currentSrc;videoPlane.requestVideoFrameCallback(()=>{
        if(source&&source===videoPlane.currentSrc){s.source=source;s.frames++}f()})};f()}''')
    if not mcp('media.clear_watched', media_id=mid, confirm='true').get('ok'):
        raise RuntimeError('One exact generated reset rejected')
    if not mcp('media.watch', context=identity, media_id=mid, wait_ms=0).get('accepted'):
        raise RuntimeError('One Watch rejected')
    wait(lambda: sample()['current'] and sample()['frames'] > 12 and not sample()['paused'], 'initial moving pictures', 60)
    # Exact disposable UI only; restore its original Off before closing.
    if mcp('captions.get', context=identity).get('state') != 'Off':
        raise RuntimeError('Unexpected initial caption state; preserve it')
    report['captionBorrowed'] = True
    if not mcp('captions.set', context=identity, state='CC2').get('ok'):
        raise RuntimeError('One caption selection rejected')
    for target in (48000, 5000, 60000):
        before = sample()
        report['stage'] = 'one-seek-' + str(target)
        if not mcp('media.seek', context=identity, target_ms=target).get('accepted'):
            raise RuntimeError('One Seek rejected')
        wait(lambda: sample()['source'] != before['source'] and sample()['current'] and
                     sample()['frames'] > before['frames'] + 8 and not sample()['paused'], 'new source pictures', 60)
        value = sample()
        report['rows'].append(dict(targetMs=target, sample=value))
        print(json.dumps(dict(targetMs=target, time=value['time'], frames=value['frames'])), flush=True)
    wait(lambda: sample()['ended'] and sample()['endedEvents'] > before['endedEvents'], 'actual finite EOF', 25)
    wait(lambda: sample()['pixels'] == 0, 'actual caption clear at EOF', 10)
    report['final'] = sample()
    if page.evaluate('JSON.stringify(localStorage)') != saved or api('streamSettings')['configured'] != configured:
        raise RuntimeError('Disposable saved/configured profile changed')
    if report['errors']:
        raise RuntimeError('Browser JS failure')
    report['passed'] = True
except Exception as error:
    report['failure'] = dict(type=type(error).__name__, message=str(error)[:300])
    if page:
        try: report['failure']['video'] = sample()
        except Exception: report['failure']['videoUnavailable'] = True
    if owned:
        try: report['failure']['producer'] = api('streamSettings').get('active')
        except Exception: report['failure']['producerUnavailable'] = True
finally:
    if owned:
        if report.get('captionBorrowed'):
            try:
                if mcp('captions.get', context=identity).get('state') == 'CC2':
                    mcp('captions.set', context=identity, state='Off')
                else: raise RuntimeError('Caption state changed; preserve it')
            except Exception: report['cleanup'].append('Owned caption restoration unknown')
        try:
            session_stop = True
            api('stop')
        except Exception: report['cleanup'].append('Session Stop receipt unknown; no replay')
    if context: context.close()
    if browser: browser.close()
    if pw: pw.stop()
    end = time.monotonic() + 90
    while time.monotonic() < end:
        try:
            if identity not in mcp('ui.list').get('contexts', []): break
        except Exception: pass
        time.sleep(.3)
    else: report['cleanup'].append('Independent owned native retirement unavailable')
    report['passed'] = report['passed'] and not report['cleanup']
    (out / (stamp + '-caption-tail-' + args.engine + '.json')).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(passed=report['passed'], engine=args.engine, rows=len(report['rows']), cleanup=report['cleanup'], failure=report.get('failure', {}).get('message'))))
raise SystemExit(0 if report['passed'] else 1)
