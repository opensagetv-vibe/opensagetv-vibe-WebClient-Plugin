#!/usr/bin/env python3
"""WP14: actual stock232 current-video restoration and post-failure ZIP.

Ephemeral browser preferences, canonical generated fixture only. One owned UI;
no Core/config writes or command replay. Host browsers, not physical iPhone.
"""
import argparse,hashlib,importlib.util,json,os,time,zipfile
from pathlib import Path
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
engine=os.environ.get('SAGETV_BROWSER_ENGINE','chromium')
if engine not in ('chromium','webkit'):raise ValueError('Unsupported engine')
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--task',choices=('WEB-067','WEB-070'),default='WEB-067');args=p.parse_args()
OUT=ROOT/'artifacts/active'/args.task;OUT.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());identity='da92a86446be'
owned=None;page=None;context=None;browser=None;pw=None;rows=[];errors=[];cleanup=[];failure={};passed=False;stop_attempted=False
def mcp(action,**v):return C.request(cfg,'/v1/control',dict(action=action,**v),mcp=True,timeout=30)
def api(action,**v):
    if action in ('status','streamSettings','playbackState'):
        return C.request(cfg,'/SageTVWebPlayer/api/miniclient?'+urlencode(dict(action=action,session=owned,**v)),timeout=20)
    return C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action=action,session=owned,**v),timeout=20)
def wait(predicate,label,seconds=45):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        if predicate():return
        page.wait_for_timeout(150)
    raise RuntimeError('Timed out: '+label)
def observe(response):
    global owned
    if '/api/miniclient' not in response.url or response.request.method!='POST':return
    try:
        value=response.json()
        if value.get('session') and value.get('clientId','').replace(':','').lower()==identity:owned=value['session']
    except Exception:pass
def vstate():return page.evaluate('()=>({time:videoPlane.currentTime,paused:videoPlane.paused,muted:videoPlane.muted,volume:videoPlane.volume,rate:videoPlane.playbackRate,frames:CURRENT_VIDEO_FIELD.frames,ready:videoPlane.readyState,width:videoPlane.videoWidth,prompt:!autoplayBtn.hidden,error:videoPlane.error?.code||null})')
def moving(label):
    before=vstate();clicked=False;end=time.monotonic()+60
    while time.monotonic()<end:
        v=vstate()
        if v['error']:raise RuntimeError('Browser media error')
        if v['prompt'] and not clicked:page.locator('#autoplayBtn').click();clicked=True
        if not v['paused'] and v['width'] and v['frames']>=before['frames']+8:return
        page.wait_for_timeout(150)
    failure['video']=v;raise RuntimeError('No decoded progress: '+label)
def result():
    text=page.locator('#videoInfoText').text_content()
    try:return json.loads(text)
    except ValueError:return {}
try:
    activity=C.activity(cfg)
    if activity.get('recordingCount')!=0 or activity.get('connectedClientCount')!=0 or mcp('ui.list').get('contexts'):raise RuntimeError('Require independently idle server')
    source=mcp('media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/VibeCaptionTest-1080i-CEA608-90s-2s.ts')
    if source.get('mediaFileId')!=20905:raise RuntimeError('Canonical fixture identity changed')
    pw=sync_playwright().start()
    browser=pw.webkit.launch(headless=True) if engine=='webkit' else pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':852,'height':393},http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},accept_downloads=True,service_workers='block')
    page=context.new_page();page.on('response',observe);page.on('pageerror',lambda e:errors.append(str(e)))
    page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify({player:'hls',videoMode:'transcode',encoder:'qsv',videoKbps:1200,resolution:'480',deinterlace:'on',allowFallback:false}));")
    page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
    wait(lambda:owned is not None and api('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'),'owned first frame')
    original=page.evaluate("()=>({client:localStorage.getItem('sagetvWebMiniClientSettings.v1'),streaming:localStorage.getItem('sagetvWebStreaming.v1'),captions:localStorage.getItem('sagetvWebCaptionAuthority.v1')})")
    connection=api('status').get('connection',{})
    if not isinstance(connection.get('captionAuthority'),dict) or not all(isinstance(connection.get(k),int) for k in ('subtitleCallbackEvents','subtitleCallbackBytes')):raise RuntimeError('Installed payload-free callback metadata missing')
    rows.append(dict(gate='payload-free-callback-status',passed=True,authority=connection['captionAuthority'],events=connection['subtitleCallbackEvents'],bytes=connection['subtitleCallbackBytes']))
    page.evaluate("()=>{const s=window.CURRENT_VIDEO_FIELD={frames:0};const f=()=>{s.frames++;videoPlane.requestVideoFrameCallback(f)};videoPlane.requestVideoFrameCallback(f)}")
    if not mcp('media.watch',context=identity,media_id=20905,wait_ms=0).get('accepted'):raise RuntimeError('Watch rejected')
    moving('initial')
    if not mcp('media.seek',context=identity,target_ms=30000).get('accepted'):raise RuntimeError('One setup Seek rejected')
    moving('seek')
    # Let normal startup reserve settle; this is not part of test execution.
    page.wait_for_timeout(3500);moving('settled setup')
    for paused in (False,True):
        if paused:
            if not mcp('media.control',context=identity,operation='pause').get('ok'):raise RuntimeError('Pause rejected')
            wait(lambda:vstate()['paused'],'actual Pause')
        before=vstate()
        if page.locator('#remotePanel').is_hidden():page.locator('#remoteToggle').click()
        if not page.locator('#testVideoBtn').is_visible():page.locator('#phoneToolsToggle').click()
        page.locator('#testVideoBtn').click()
        wait(lambda:'afterRestore' in result(),'current-video test completion',30)
        tested=result();failure['currentVideoTest']=tested
        if tested.get('result')!='PASS' or not tested.get('afterRestore',{}).get('applied'):raise RuntimeError('Real current-video test did not restore successfully')
        if args.task=='WEB-070':
            step=next((s for s in tested.get('steps',[]) if s.get('name')=='reversible-seek'),{})
            if step.get('producerChanged') is not True or not isinstance(step.get('presentedMs'),(int,float)) or abs(step['presentedMs']-step.get('targetMs',-999999))>=1000:raise RuntimeError('Test accepted an old producer or logical anchor without a replacement presented picture')
        after=tested['afterRestore']
        if after['paused']!=paused or after['muted']!=before['muted'] or abs(after['volume']-before['volume'])>.001 or after['playbackRate']!=before['rate']:raise RuntimeError('Playback/audio state changed')
        if abs(after['timeMs']-tested['before']['timeMs'])>1500:raise RuntimeError('Original position not restored')
        current=page.evaluate("()=>({client:localStorage.getItem('sagetvWebMiniClientSettings.v1'),streaming:localStorage.getItem('sagetvWebStreaming.v1'),captions:localStorage.getItem('sagetvWebCaptionAuthority.v1')})")
        if current!=original:raise RuntimeError('Saved preferences changed')
        rows.append(dict(gate='paused-current-video' if paused else 'playing-current-video',passed=True,test=tested))
        print('PASS '+rows[-1]['gate'],flush=True);page.locator('#closeVideoInfo').click()
    # End only our exact native UI. This causes a real disconnected-source
    # failure, rather than injecting a pretend error event into production JS.
    stop_attempted=True
    if not api('stop').get('ok'):raise RuntimeError('Owned Stop not acknowledged; do not replay')
    wait(lambda:not page.locator('#connectionRecovery').is_hidden(),'terminal disconnect UI',65)
    with page.expect_download(timeout=30000) as download:page.locator('#connectionDiagnosticsBtn').click()
    target=OUT/(stamp+'-'+engine+'-failure-diagnostics.zip');download.value.save_as(str(target))
    with zipfile.ZipFile(target) as archive:
        data=archive.read('report.json');report=json.loads(data)
        if hashlib.sha256(data).hexdigest()+'  report.json' not in archive.read('hashes.sha256').decode():raise RuntimeError('Report hash mismatch')
    snap=report.get('browser',{})
    if not snap.get('failureSnapshot') or snap.get('version')!='3.3.0':raise RuntimeError('Failure context lost before export')
    if not isinstance((snap.get('serverConnection') or {}).get('connection',{}).get('captionAuthority'),dict):raise RuntimeError('Last native caption diagnostics lost from ZIP')
    # The raw report is local active evidence only; inspect structure, never
    # print bearer/basic headers, session IDs, media or caption content.
    def check(value):
        if isinstance(value,dict):
            for k,v in value.items():
                if any(x in k.lower() for x in ('authorization','password','cookie','crypto','token','sessionkey')) and v not in (None,'[redacted]'):raise RuntimeError('Sensitive field not redacted')
                if k.lower() in ('captiontext','subtitletext','payload','mediabytes') and v not in (None,'[omitted-content]','[redacted]'):raise RuntimeError('Content field not omitted')
                check(v)
        elif isinstance(value,list):
            for v in value:check(v)
    check(report)
    rows.append(dict(gate='real-terminal-failure-export-before-reconnect',passed=True,reportBytes=len(data),hashVerified=True,failureSnapshotPresent=True))
    if errors:raise RuntimeError('Browser JavaScript errors')
    passed=True;failure={}
except Exception as e:failure.update(type=type(e).__name__,message=str(e)[:250] if isinstance(e,RuntimeError) else 'Bounded field check failed')
finally:
    # Stop above can already have retired its exact native peer. No Stop replay.
    if owned and not stop_attempted:
        try:
            if identity in mcp('ui.list').get('contexts',[]):api('stop')
        except Exception:cleanup.append('Owned Stop unknown')
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
    (OUT/(stamp+'-'+engine+'-current-video.json')).write_text(json.dumps(dict(passed=passed and not cleanup,engine=engine,realStock232=True,physicalIPhone=False,rows=rows,errors=errors,cleanup=cleanup,failure=failure),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=passed and not cleanup,rows=len(rows),cleanup=cleanup,failureType=failure.get('type'))),flush=True)
raise SystemExit(0 if passed and not cleanup else 1)
