#!/usr/bin/env python3
"""Actual unchanged Breakfast Copy negative/recovery; serial stock232 only.

No source edits, saved household preferences or control replay. Ephemeral
browser identity. Strict failures are expected only with explicit explanation;
allowed recovery requires an actual replacement producer and decoded frames.
"""
import argparse,hashlib,importlib.util,json,time,re,zipfile
from pathlib import Path
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--engine',choices=('chromium','webkit'),default='chromium')
p.add_argument('--transport',choices=('hls','mpegts'),default='hls')
p.add_argument('--allow-fallback',action='store_true')
p.add_argument('--source',choices=('breakfast','owned-mpeg2'),default='breakfast')
p.add_argument('--task',choices=('WEB-069','WEB-103'),default='WEB-069')
p.add_argument('--export-diagnostics',action='store_true',help='Production browser download, ZIP/report hash validation; no server write')
a=p.parse_args()
if a.source=='owned-mpeg2' and a.task!='WEB-103':p.error('Owned MPEG2 follow-up belongs to WEB-103')
identity='da92a86446be';owned=None;page=None;context=None;browser=None;pw=None
passed=False;failure={};cleanup=[];errors=[];samples=[];requests=[];observed=[];outcome=None;effective_plan={};codec_flags=[]
out=ROOT/'artifacts/active'/a.task;out.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
diagnostic=None
def mcp(action,**v):return C.request(cfg,'/v1/control',dict(action=action,**v),mcp=True,timeout=30)
def api(action):
    if action in ('status','streamSettings'):
        return C.request(cfg,'/SageTVWebPlayer/api/miniclient?'+urlencode(dict(action=action,session=owned)),timeout=15)
    return C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action=action,session=owned),timeout=15)
def observe(response):
    global owned
    if '/api/miniclient' not in response.url:return
    try:
        j=response.json()
        if j.get('session') and j.get('clientId','').replace(':','').lower()==identity:owned=j['session']
    except Exception:pass
def request(req):
    if '/api/miniclient' not in req.url:return
    from urllib.parse import parse_qs,urlparse
    action=parse_qs(urlparse(req.url).query).get('action',[''])[0]
    if req.method=='POST' and action in ('fallback','recover','streamSettings'):requests.append(action)
    if action=='fallback':codec_flags.append(parse_qs(req.post_data or '').get('videoDecodeFailure',['false'])[0]=='true')
def sample():
    return page.evaluate("()=>{document.getElementById('videoInfoBtn').click();const p=JSON.parse(document.getElementById('videoInfoText').textContent).playback;return{time:videoPlane.currentTime,frames:COPY_FIELD.frames,currentFrames:COPY_FIELD.currentFrames,frameSourceCurrent:COPY_FIELD.source===videoPlane.currentSrc,source:videoPlane.currentSrc,width:videoPlane.videoWidth,paused:videoPlane.paused,prompt:!autoplayBtn.hidden,error:videoPlane.error?.code||null,notice:document.getElementById('osdMessage').textContent,producer:p.id,transport:p.transport,intentPaused:p.paused,recovering:p.recovering,settings:p.streamSettings}}")
try:
    act=C.activity(cfg)
    if act.get('recordingCount')!=0 or act.get('connectedClientCount')!=0 or mcp('ui.list').get('contexts'):raise RuntimeError('Require independently idle server')
    if a.source=='owned-mpeg2':
        baseline=json.loads((ROOT/'artifacts/active/WP11-008/20261119T174842Z-iphone-growing-recording.json').read_text(encoding='utf-8'))['ownership']
        expected='/var/media/tv/DonkeyHodie-SwoopaRinoDuckDucksGreatAdventure-43081-0.ts'
        if baseline!={'mediaId':84394,'path':expected}:raise RuntimeError('Require exact prior owned test recording')
        info=C.request(cfg,'/SageTVWebPlayer/api/media?id=84394')
        if info.get('recording') or len(info.get('files',[]))!=1 or info['files'][0]['path']!=expected or info['files'][0]['streamSize']!=567424984 or 'MPEG2-Video' not in info.get('format',''):raise RuntimeError('Owned MPEG2 identity/codec changed')
        source={'mediaFileId':84394}
    else:source=mcp('media.resolve_exact_path',path='/var/media/videos/USER_TEST/Breakfast-26711345-0.ts')
    if not source.get('mediaFileId'):raise RuntimeError('Original source unavailable')
    pw=sync_playwright().start()
    browser=pw.webkit.launch(headless=True) if a.engine=='webkit' else pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':852,'height':393},http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block')
    page=context.new_page();page.on('response',observe);page.on('request',request);page.on('pageerror',lambda e:errors.append(str(e)))
    profile=dict(player=a.transport,videoMode='copy',encoder='software',videoKbps=1200,resolution='source',deinterlace='off',allowFallback=a.allow_fallback,audioLanguage='eng',audioCodec='aac')
    page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebStreaming.v1',"+json.dumps(json.dumps(profile))+");")
    page.add_init_script("localStorage.setItem('sagetvWebMiniClientSettings.v1',JSON.stringify({saveDiagnosticsToServer:false}));")
    page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
    end=time.monotonic()+45
    while not owned or not api('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'):
        if time.monotonic()>end:raise RuntimeError('No owned native first frame')
        page.wait_for_timeout(150)
    before=page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')")
    configured_before=api('streamSettings').get('configured')
    page.evaluate("()=>{const s=window.COPY_FIELD={frames:0,currentFrames:0,source:''};function f(){const src=videoPlane.currentSrc;videoPlane.requestVideoFrameCallback(()=>{if(src&&src===videoPlane.currentSrc){if(s.source!==src){s.source=src;s.currentFrames=0}s.frames++;s.currentFrames++}f()})}f();return true}")
    if not mcp('media.watch',context=identity,media_id=source['mediaFileId'],wait_ms=0).get('accepted'):raise RuntimeError('Watch rejected')
    initial=None;clicked=False;end=time.monotonic()+65;producer_frames={}
    while time.monotonic()<end:
        v=sample();samples.append({k:v[k] for k in ('time','frames','width','paused','error','notice','transport','intentPaused','recovering')})
        if v['producer'] and v['producer'] not in observed:observed.append(v['producer'])
        if v['producer'] and initial is None:initial=v['producer']
        if v['producer'] not in producer_frames:producer_frames[v['producer']]=v['frames']
        fresh_frames=v['frames']-producer_frames[v['producer']]
        if v['prompt'] and not clicked:page.locator('#autoplayBtn').click();clicked=True
        effective=(v.get('settings') or {}).get('effective',{})
        if a.allow_fallback:
            if initial and v['producer']!=initial and effective.get('video')=='libx264' and fresh_frames>=8 and v['frameSourceCurrent'] and v['currentFrames']>=8 and v['width']>0 and not v['paused'] and not v['error']:
                passed=True;outcome='decoded-h264-compatibility-replacement';break
        elif (v['error'] in (3,4) or (v['time']>0 and v['width']==0 and v['frames']==0)) and v['intentPaused'] and 'Copied video was not decoded:' in v['notice'] and 'fallback is disabled' in v['notice']:
            if effective.get('video')!='copy' or requests.count('fallback'):raise RuntimeError('Strict Copy silently changed')
            passed=True;outcome='strict-copy-explicit-unsupported';break
        if effective.get('video')=='copy' and fresh_frames>=8 and v['frameSourceCurrent'] and v['currentFrames']>=8 and v['width']>0 and not v['paused'] and not v['error'] and not requests.count('fallback'):
            passed=True;outcome='copy-directly-decodable';break
        page.wait_for_timeout(250)
    if not passed:failure.update(video=v,producerCount=len(observed));raise RuntimeError('Copy recovery/strict explanation not observed')
    if page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')")!=before:raise RuntimeError('Saved profile changed')
    if api('streamSettings').get('configured')!=configured_before:raise RuntimeError('Native configured defaults changed')
    effective_plan=effective
    if outcome=='decoded-h264-compatibility-replacement' and requests.count('fallback')!=1:raise RuntimeError('Compatibility fallback not one-shot')
    if errors:raise RuntimeError('Unhandled browser errors')
    if a.export_diagnostics:
        target=out/(stamp+'-'+a.engine+'-'+a.transport+'-'+('allowed' if a.allow_fallback else 'strict')+'-diagnostic.zip')
        if target.exists():raise RuntimeError('Preserve prior diagnostic target')
        # Normal production UI. Host-browser gesture, not physical phone proof.
        page.evaluate('()=>{diagnosticsBtn.click();return true}')
        with page.expect_download(timeout=30000) as download:
            page.locator('#downloadReport').click()
        download.value.save_as(target)
        with zipfile.ZipFile(target) as bundle:
            if set(bundle.namelist())!={'report.json','hashes.sha256','README.txt'}:raise RuntimeError('Unexpected diagnostic entries')
            entry=bundle.getinfo('report.json')
            if entry.file_size>12*1024*1024:raise RuntimeError('Report exceeds bound')
            data=bundle.read('report.json');checksum=bundle.read('hashes.sha256').decode('ascii').strip()
        if checksum!=hashlib.sha256(data).hexdigest()+'  report.json':raise RuntimeError('Downloaded report checksum mismatch')
        captured=json.loads(data)
        if not isinstance(captured,dict):raise RuntimeError('Invalid diagnostic report object')
        diagnostic=dict(path=target.name,bytes=target.stat().st_size,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),reportHashVerified=True,productionDownload=True,serverSaveRequested=False)
except Exception as e:
    detail=str(e).splitlines()[0]
    detail=re.sub(r'[a-fA-F0-9]{24,}', '[private-id]', detail)
    passed=False;failure.update(type=type(e).__name__,message=detail[:250])
    print(json.dumps(dict(failureType=type(e).__name__,message=detail[:250])),flush=True)
finally:
    if owned:
        try:api('stop')
        except Exception:cleanup.append('Exact owned Stop unverified')
    if context:context.close()
    if browser:browser.close()
    if pw:pw.stop()
    end=time.monotonic()+90
    while time.monotonic()<end:
        try:
            if identity not in mcp('ui.list').get('contexts',[]):break
        except Exception:pass
        time.sleep(.3)
    else:cleanup.append('Native UI retirement unknown')
    # Session tokens remain out of exported evidence, including failure detail.
    if 'video' in failure:
        failure['video'].pop('producer',None)
    target=out/(stamp+'-'+a.engine+'-'+a.transport+'-'+('allowed' if a.allow_fallback else 'strict')+'.json')
    target.write_text(json.dumps(dict(passed=passed and not cleanup,outcome=outcome,realStock232=True,physicalIPhone=False,source=a.source,ownedTestRecording=a.source=='owned-mpeg2',engine=a.engine,transport=a.transport,allowFallback=a.allow_fallback,producerCount=len(observed),requests=requests,codecFailureFlags=codec_flags,effective=effective_plan,diagnostic=diagnostic,savedBrowserAndNativeDefaultsPreserved=passed,samples=samples,errors=errors,cleanup=cleanup,failure=failure),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=passed and not cleanup,outcome=outcome,requests=requests,producerCount=len(observed),failureType=failure.get('type'),cleanup=cleanup,report=str(target))),flush=True)
raise SystemExit(0 if passed and not cleanup else 1)
