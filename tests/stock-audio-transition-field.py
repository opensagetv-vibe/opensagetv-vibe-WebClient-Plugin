#!/usr/bin/env python3
"""Generated PMT/layout change through real stock232 policy/QSV/browser playback.

Not acoustic or original-broadcast certification. Exact owned synthetic fixture,
isolated profile, one public Watch, no replay; spectral output verifies no NAR
switch. Actual production modules, encoder, segments and browser decoders.
"""
import argparse, array, base64, cmath, importlib.util, json, math, subprocess, time
from pathlib import Path
from urllib.parse import urlencode, urljoin, urlparse
from playwright.sync_api import sync_playwright
from bounded_browser_rpc import bounded

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('commission', ROOT/'scripts/commission-mobile.py')
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C); cfg = C.configuration()
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--engine', choices=('chromium', 'webkit'), required=True)
p.add_argument('--late-nar', action='store_true', help='Explicitly select the late-discovered NAR PID, never an automatic fallback')
a = p.parse_args()
identity = 'da92a86446be'; media_id = 84231
out = ROOT/'artifacts/active/WP12-001'; out.mkdir(parents=True, exist_ok=True)
stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
report = dict(passed=False, generatedSource=True, originalBroadcast=False, physicalPhone=False,
    acoustic=False, engine=a.engine, mediaId=media_id, lateNar=a.late_nar, rows=[], cleanup=[])
owned = None; page = context = browser = pw = None


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


def wait(test, label, seconds=60):
    end = time.monotonic()+seconds
    while time.monotonic() < end:
        if test(): return
        page.wait_for_timeout(150)
    raise RuntimeError('Timed out '+label+'; no replay')


def observe(response):
    global owned
    if '/api/miniclient' not in response.url or response.request.method != 'POST': return
    try:
        data = response.json()
        if data.get('clientId', '').replace(':', '').lower() == identity and data.get('session'): owned = data['session']
    except Exception: pass


def video():
    return page.evaluate("()=>{const v=videoPlane,s=__audioTransition;return{time:v.currentTime,frames:s.frames,sourceCurrent:s.source===v.currentSrc,width:v.videoWidth,paused:v.paused,ready:v.readyState,error:v.error?.code||null,prompt:!autoplayBtn.hidden,ended:v.ended}}")


def spectrum(path, wanted=440):
    result = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:a:0',
        '-t', '0.5', '-ac', '1', '-ar', '8000', '-f', 'f32le', '-'], capture_output=True, timeout=15)
    if result.returncode: raise RuntimeError('Output audio decode failed')
    samples = array.array('f'); samples.frombytes(result.stdout)
    if len(samples) < 2000: raise RuntimeError('Output audio is too short')
    energy = sum(x*x for x in samples)/len(samples)
    powers = {str(hz): abs(sum(x*cmath.exp(-2j*math.pi*hz*i/8000) for i,x in enumerate(samples)))**2 for hz in (440,1320)}
    ratio = powers[str(wanted)]/max(1e-12, powers[str(1320 if wanted==440 else 440)])
    if energy < 1e-6 or ratio < 20: raise RuntimeError('Output lost selected audio identity')
    return dict(samples=len(samples), meanSquare=energy, selectedToneHz=wanted, selectedToOtherPower=ratio)


try:
    guard()
    source = mcp('media.resolve_exact_path', path='/var/media/OpenSageTV_Vibe_Tests/WP12-Audio-PMT/VibeAudio-PMT-Mono-to-51.ts')
    if source.get('mediaFileId') != media_id: raise RuntimeError('Exact generated fixture changed')
    pw = sync_playwright().start()
    browser = pw.webkit.launch(headless=True) if a.engine == 'webkit' else pw.chromium.launch(
        headless=True, executable_path='/usr/local/bin/vibe-chromium', args=['--no-sandbox'])
    context = browser.new_context(viewport={'width':852,'height':393}, service_workers='block',
        http_credentials={'username':cfg['web_username'],'password':cfg['web_password']})
    profile = dict(player='hls',videoMode='transcode',encoder='qsv',resolution='source',
        videoKbps=1000,audioCodec='aac',audioChannels='2',audioLanguage='nar' if a.late_nar else 'eng',audioFallback='strict',deinterlace='off')
    context.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebStreaming.v1',"+json.dumps(json.dumps(profile))+");")
    page = context.new_page(); original = page.evaluate
    page.evaluate = lambda *args, **kw: bounded(original,*args,**kw); page.on('response',observe)
    page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
    wait(lambda: owned and api('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'),'native first frame')
    guard(True); before = api('streamSettings')['configured']; saved = page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')")
    page.evaluate("()=>{const s=window.__audioTransition={frames:0,source:'',done:false};function f(){const source=videoPlane.currentSrc;videoPlane.requestVideoFrameCallback(()=>{if(s.done)return;if(source&&source===videoPlane.currentSrc){s.frames++;s.source=source}f()})}f()}")
    if not mcp('media.clear_watched',media_id=media_id,confirm='true').get('ok'): raise RuntimeError('Exact generated fixture reset rejected')
    if not mcp('media.watch',context=identity,media_id=media_id,wait_ms=0).get('accepted'): raise RuntimeError('One Watch rejected')
    activated = False; start = time.monotonic(); first = None
    while time.monotonic()-start < 65:
        value = video()
        if value['error']: raise RuntimeError('Actual browser decoder failed')
        if value['prompt'] and not activated: page.locator('#autoplayBtn').click(timeout=3000); activated=True
        if value['sourceCurrent'] and value['frames'] >= 8 and value['time'] > .2 and not value['paused']: first=value; break
        page.wait_for_timeout(150)
    if first is None: raise RuntimeError('No advancing real output')
    state = api('streamSettings'); producer = state.get('session'); effective = state.get('active',{}).get('effective',{})
    report['effective'] = effective
    expected_index=2 if a.late_nar else 1; expected_language='nar' if a.late_nar else 'eng'
    if effective.get('audioStreamIndex') != expected_index or effective.get('audioLanguage') != expected_language: raise RuntimeError('Selected audio identity changed')
    samples=[]
    while video()['time'] < 24:
        page.wait_for_timeout(1000); value=video(); samples.append(value)
        if value['error'] or value['paused'] or value['ended']: raise RuntimeError('Output failed before/after PMT boundary')
        if time.monotonic()-start > 90: raise RuntimeError('Transition output stalled')
    after=video(); current=api('streamSettings')
    if current.get('session') != producer or current.get('active',{}).get('effective',{}).get('audioStreamIndex') != expected_index:
        raise RuntimeError('Unwanted producer or primary stream replacement')
    report['rows'].append(dict(gate='same-producer-real-pictures-cross-PMT-and-layout-change',passed=True,first=first,after=after,samples=samples))
    # Capture two actual output segments, never another encoder or a user source.
    status = C.request(cfg,'/SageTVWebPlayer/api/hls?'+urlencode(dict(session=producer)))
    report['producer']={k:status.get(k) for k in ('encoder','hardware','hardwareDecode','hardwareFilters','running','exitCode','playlistUrl','streamSettings')}
    playlist=urljoin(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/',status['playlistUrl'])
    response=page.evaluate("async url=>{const r=await fetch(url,{cache:'no-store',signal:AbortSignal.timeout(15000)});return{status:r.status,text:r.ok?await r.text():''}}",playlist)
    if response['status']!=200: raise RuntimeError('Owned output playlist unavailable: HTTP '+str(response['status'])+' '+urlparse(playlist).path)
    lines=response['text'].splitlines(); cursor=0; selected={}; duration=None
    for line in lines:
        if line.startswith('#EXTINF:'): duration=float(line.split(':',1)[1].split(',')[0])
        elif line and not line.startswith('#') and duration is not None:
            for target in ((23,) if a.late_nar else (3,23)):
                if cursor <= target < cursor+duration: selected[target]=urljoin(playlist,line)
            cursor+=duration;duration=None
    if len(selected)!=(1 if a.late_nar else 2): raise RuntimeError('Required pre/post output segments missing')
    for target,url in selected.items():
        if urlparse(url).netloc != urlparse(playlist).netloc or not urlparse(url).path.startswith(urlparse(playlist).path.rsplit('/',1)[0]+'/'):
            raise RuntimeError('Output segment escaped owned playlist')
        response=page.evaluate("async url=>{const r=await fetch(url,{cache:'no-store',signal:AbortSignal.timeout(15000)});if(!r.ok)return{status:r.status};const b=new Uint8Array(await r.arrayBuffer());if(b.length>3145728)throw Error('Segment too large');let s='';for(let i=0;i<b.length;i+=8192)s+=String.fromCharCode(...b.subarray(i,i+8192));return{status:r.status,base64:btoa(s)}}",url)
        if response['status']!=200: raise RuntimeError('Owned output segment unavailable')
        data=base64.b64decode(response['base64'],validate=True)
        if len(data)>3*1024*1024: raise RuntimeError('Unexpected output segment size')
        path=out/(stamp+'-'+a.engine+'-audio-'+str(target)+'.ts')
        with path.open('xb') as file:file.write(data)
        report['rows'].append(dict(gate='decoded-output-selected-'+expected_language+'-'+str(target)+'s',passed=True,spectrum=spectrum(path,1320 if a.late_nar else 440)))
    wait(lambda:video()['ended'],'natural generated EOF',30)
    report['rows'].append(dict(gate='natural-EOF-after-layout-transition',passed=True,last=video()))
    if api('streamSettings')['configured'] != before or page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')") != saved:
        raise RuntimeError('Defaults changed')
    report['rows'].append(dict(gate='configured-and-saved-defaults-preserved',passed=True)); report['passed']=True
except Exception as e:
    report['failure']=dict(type=type(e).__name__,message=str(e)[:200] if isinstance(e,RuntimeError) else 'Bounded field observation failed')
    if page:
        try: report['last']=video()
        except Exception: pass
finally:
    if owned:
        try:
            guard(True)
            if mcp('ui.state',context=identity).get('fullyLoaded'):
                if not mcp('media.control',context=identity,operation='stop').get('accepted'): raise RuntimeError('Stop rejected')
            if not C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action='stop',session=owned)).get('ok'): report['cleanup'].append('Owned stop unacknowledged')
        except Exception:report['cleanup'].append('Owned stop unknown; not replayed')
    for resource in (context,browser,pw):
        if resource:
            try:bounded(resource.stop if resource is pw else resource.close)
            except Exception:report['cleanup'].append('Browser shutdown unknown')
    if owned:
        end=time.monotonic()+90
        while time.monotonic()<end:
            try:
                observed=mcp('ui.list'); contexts=observed.get('contexts')
                if observed.get('ok') is not True or not isinstance(contexts,list):
                    raise RuntimeError('Native retirement response is not valid idle evidence')
            except Exception:
                report['cleanup'].append('Read-only native retirement observation unavailable; no control replay')
                break
            if identity not in contexts:break
            time.sleep(.3)
        else:report['cleanup'].append('Native retirement unknown')
    report['passed']=report['passed'] and not report['cleanup']
    path=out/(stamp+'-'+a.engine+('-late-nar' if a.late_nar else '')+'-audio-transition.json');path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=report['passed'],rows=len(report['rows']),report=str(path),failure=report.get('failure'),cleanup=report['cleanup'])),flush=True)
raise SystemExit(0 if report['passed'] else 1)
