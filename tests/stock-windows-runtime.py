#!/usr/bin/env python3
"""Explicit MIM-WIN-001 Windows185 consumer gate, never default CI or phone proof.

Uses existing public APIs and browser-rendered frames, one ordered input per
action, exact commissioned identity/fixture, owned cleanup. No Core writes.
"""
import argparse,base64,json,os,time,tomllib,subprocess,socket
from urllib.error import URLError
from pathlib import Path
from urllib.parse import urlencode,urlparse,parse_qs
from urllib.request import Request,urlopen
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--run-stock185',action='store_true');p.add_argument('--engine',choices=('chromium','webkit'),required=True);p.add_argument('--recording-only',action='store_true');p.add_argument('--skip-eof',action='store_true',help='Separate DVD qualification; does not certify the retained EOF failure');a=p.parse_args()
if not a.run_stock185:raise SystemExit('Explicit Windows185 authorization required')
data=tomllib.loads((ROOT.parent/'android-client/config/firetv.toml').read_text())
cfg=data['servers']['windows_fixed'];assert cfg['address']=='192.168.10.185' and cfg['stock'] is True
base='http://192.168.10.185:8080';identity='da92a86446be';owned=None
user=cfg.get('web_username') or data['servers']['vibe']['web_username']
password=cfg.get('web_password') or data['servers']['vibe']['web_password']
out=ROOT/'artifacts/active/MIM-WIN-001';out.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());rows=[];failure=None;cleanup=[];page=None;stage='preflight'
def request(path,values=None,mcp=False,timeout=30):
    target=cfg['core_mcp_base_url'] if mcp else base
    auth='Bearer '+cfg['core_mcp_token'] if mcp else 'Basic '+base64.b64encode((user+':'+password).encode()).decode()
    r=Request(target.rstrip('/')+path,data=urlencode(values).encode() if values is not None else None,headers={'Authorization':auth})
    with urlopen(r,timeout=timeout) as response:return json.load(response)
def mcp(action,**v):
    # Inspection can time out while the native player owns its media lock.
    # Only these read-only calls are retryable. Never replay Watch/Seek/input.
    readonly=action in ('ui.state','ui.list','server.activity')
    for attempt in range(3 if readonly else 1):
        try:return request('/v1/control',dict(action=action,**v),True,8 if readonly else 30)
        except (TimeoutError,socket.timeout,URLError):
            if not readonly or attempt==2:raise
            if page:page.wait_for_timeout(250)
def api(action,**v):
    values=dict(action=action,session=owned,**v)
    return request('/SageTVWebPlayer/api/miniclient?'+urlencode(values)) if action=='status' else request('/SageTVWebPlayer/api/miniclient',values)
def guard(idle=False):
    activity=mcp('server.activity');contexts=mcp('ui.list').get('contexts',[])
    if activity.get('recordingCount')!=0 or activity.get('connectedClientCount')!=0 or any(x!=identity for x in contexts) or (idle and contexts):raise RuntimeError('Unrelated Windows activity')
def observed(response):
    global owned
    if '/api/miniclient' not in response.url or response.request.method!='POST':return
    if parse_qs(urlparse(response.url).query).get('action')!=['start'] and 'action=start' not in (response.request.post_data or ''):return
    try:
        value=response.json()
        if value.get('session') and value.get('clientId','').replace(':','').lower()==identity:owned=value['session']
    except Exception:pass
def wait(predicate,label,seconds=60):
    print('WAIT '+a.engine+' '+label,flush=True)
    deadline=time.monotonic()+seconds
    while time.monotonic()<deadline:
        page.wait_for_timeout(150)
        if page.locator('#autoplayBtn').is_visible():page.locator('#autoplayBtn').click()
        if predicate():return
    try:
        page.screenshot(path=str(out/(stamp+'-'+a.engine+'-timeout.png')))
        (out/(stamp+'-'+a.engine+'-timeout.json')).write_text(json.dumps(dict(label=label,video=sample(),text=page.locator('body').inner_text()[-5000:]),indent=2)+'\n')
    except Exception:pass
    raise RuntimeError('Timed out: '+label)
def sample():return page.evaluate('''()=>({frames:WIN_GATE.frames,sourceFrames:WIN_GATE.sourceFrames,frameSource:WIN_GATE.frameSource,time:videoPlane.currentTime,src:videoPlane.currentSrc,
 width:videoPlane.videoWidth,paused:videoPlane.paused,ended:videoPlane.ended,ready:videoPlane.readyState,
 error:videoPlane.error?.code||null,captionText:document.getElementById('localCaptions')?.textContent||'',playback:WIN_GATE.player?.snapshot(),controls:WIN_GATE.controls,
 buffered:Array.from({length:videoPlane.buffered.length},(_,i)=>[videoPlane.buffered.start(i),videoPlane.buffered.end(i)])})''')
def video_ended():return page.evaluate('videoPlane.ended')

def advancing(label,seconds=30):
    # A DVD VM transition replaces the producer/decoder epoch. Frames from
    # the preceding menu or recording cannot prove the feature is advancing.
    first=sample();began=time.monotonic()
    def moved():
        nonlocal first,began
        last=sample()
        if last['src']!=first['src']:
            first=last;began=time.monotonic();return False
        return (time.monotonic()-began>=1.5 and last['src']
            and last['frameSource']==last['src'] and last['sourceFrames']>first['sourceFrames']+15
            and last['time']>first['time']+.3 and not last['paused'] and not last['error'])
    wait(moved,label,seconds)
    return first,sample()
try:
    guard(True)
    health=request('/SageTVWebPlayer/api/health')
    if not health.get('transcoderAvailable') or not health.get('ownedProcessStopAvailable'):raise RuntimeError('Owned Windows transcoder unavailable')
    media=mcp('media.resolve_exact_path',path='V:\\OpenSageTV_Vibe_Tests\\VibeCaptionTest-1080i-CEA608-90s-2s.ts')
    if not media.get('mediaFileId'):raise RuntimeError('Canonical Windows fixture missing')
    with sync_playwright() as pw:
        if a.engine=='webkit':subprocess.run(['bash','/workspace/release-manifest/scripts/prepare-headless-audio.sh'],check=True,timeout=15)
        browser=pw.webkit.launch(headless=True) if a.engine=='webkit' else pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
        context=browser.new_context(viewport={'width':852,'height':393},http_credentials={'username':user,'password':password},service_workers='block')
        page=context.new_page();page.on('response',observed)
        page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify({player:'hls',videoMode:'transcode',videoKbps:1500,resolution:'480',deinterlace:'on',companionDvd:false,captions:'608',captionService:1}));localStorage.setItem('sagetvWebCaptionAuthority.v1',JSON.stringify({mode:'cc1',cc1Type:'cea608',cc1Service:1}));localStorage.setItem('sagetvWebMiniClientSettings.v1',JSON.stringify({mute:true}));")
        page.add_init_script("document.addEventListener('DOMContentLoaded',()=>{const g=window.WIN_GATE={frames:0,controls:[]},v=document.getElementById('videoPlane');const proto=SageMiniPlayback.prototype,health=proto.hlsHealth,control=proto.control;proto.hlsHealth=function(...a){g.player=this;return health.apply(this,a)};proto.control=function(...a){g.controls.push({at:performance.now(),action:a[0],value:a[1]});if(g.controls.length>30)g.controls.shift();return control.apply(this,a)};function frame(){g.frames++;v.requestVideoFrameCallback(frame)}v.requestVideoFrameCallback(frame)});")
        page.add_init_script("document.addEventListener('DOMContentLoaded',()=>{const g=WIN_GATE,v=document.getElementById('videoPlane');g.sourceFrames=0;g.frameSource='';function frame(){v.requestVideoFrameCallback(()=>{const src=v.currentSrc;if(g.frameSource!==src){g.frameSource=src;g.sourceFrames=0}g.sourceFrames++;frame()})}frame()});")
        page.goto(base+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
        wait(lambda:owned is not None and identity in mcp('ui.list').get('contexts',[]),'owned native UI')
        wait(lambda:api('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'),'native GFX first frame')
        mcp('media.clear_watched',media_id=media['mediaFileId'],confirm='true');guard()
        if not mcp('media.watch',context=identity,media_id=media['mediaFileId'],wait_ms=0).get('accepted'):raise RuntimeError('Watch refused')
        wait(lambda:page.evaluate('WIN_GATE.frames>15&&videoPlane.videoWidth>0&&videoPlane.currentTime>.5&&!videoPlane.paused&&!videoPlane.error'),'actual recording frames',90)
        start=sample();page.wait_for_timeout(1500);after=sample()
        if after['frames']<=start['frames'] or after['time']<=start['time']+.3:raise RuntimeError('Recording not advancing')
        rows.append(dict(gate='recording-hls-startup-and-advance',passed=True,before=start,after=after))
        print('PASS '+a.engine+' actual Windows HLS recording',flush=True)
        for target in (42000,10000):
            stage='recording-seek-'+str(target)
            old=sample();guard()
            accepted=mcp('media.seek',context=identity,target_ms=target)
            if not accepted.get('ok') or not accepted.get('accepted'):raise RuntimeError('Ordered seek refused')
            absolute_target=int(accepted['absoluteTargetMs'])
            wait(lambda:abs(int(mcp('ui.state',context=identity).get('mediaTimeMs',0))-absolute_target)<10000 and page.evaluate('videoPlane.videoWidth>0&&!videoPlane.paused&&videoPlane.currentTime>.5&&!videoPlane.error') and sample()['src']!=old['src'] and sample()['frames']>old['frames']+15,'public target clock and new seek pictures',60)
            native=mcp('ui.state',context=identity)
            if abs(int(native.get('mediaTimeMs',0))-absolute_target)>10000:raise RuntimeError('Public seek clock outside bounded landing')
            rows.append(dict(gate='ordered-seek-'+str(target),passed=True,absoluteTargetMs=absolute_target,nativeTimeMs=native.get('mediaTimeMs'),video=sample()))
        stage='recording-pause-resume'
        api('command',command=6);wait(lambda:page.evaluate('videoPlane.paused'),'Pause',20)
        held=page.evaluate('videoPlane.currentTime');page.wait_for_timeout(600)
        if abs(page.evaluate('videoPlane.currentTime')-held)>.2:raise RuntimeError('Paused clock advanced')
        api('command',command=7);wait(lambda:page.evaluate('(old)=>!videoPlane.paused&&videoPlane.currentTime>old+.3',held),'Play',30)
        rows.append(dict(gate='pause-resume',passed=True))
        stage='recording-captions'
        wait(lambda:bool(sample()['captionText'].strip()),'real CEA-608 rendered caption',25)
        rows.append(dict(gate='rendered-CEA608-after-seek',passed=True,text=sample()['captionText']))
        stage='recording-eof'
        duration=int(mcp('ui.state',context=identity)['durationMs'])
        if not a.skip_eof:
            accepted=mcp('media.seek',context=identity,target_ms=duration-7000)
            wait(lambda:video_ended(),'actual recording EOF',45)
            rows.append(dict(gate='recording-decoder-EOF',passed=True,video=sample()))
        page.screenshot(path=str(out/(stamp+'-'+a.engine+'-recording.png')))
        guard();mcp('media.control',context=identity,operation='stop')
        wait(lambda:not mcp('ui.state',context=identity).get('fullyLoaded'),'recording Stop',20)
        if a.recording_only:
            context.close();browser.close()
        else:
            stage='DVD-resolve'
        dvd=None
        if a.recording_only:raise StopIteration()
        for path in ('V:\\OpenSageTV_Vibe_Tests\\OpenSageTV_Vibe_Test_DVD\\VIDEO_TS','V:\\OpenSageTV_Vibe_Tests\\OpenSageTV_Vibe_Test_DVD'):
            try:
                found=mcp('media.resolve_exact_path',path=path)
                if found.get('mediaFileId'):dvd=found;break
            except Exception:pass
        if not dvd:raise RuntimeError('Canonical indexed DVD missing')
        stage='DVD-Watch'
        before_dvd=sample();before_frames=before_dvd['frames'];guard();mcp('media.watch',context=identity,media_id=dvd['mediaFileId'],wait_ms=0)
        stage='DVD-native-VM'
        wait(lambda:page.evaluate('WIN_GATE.player?.dvd===true&&(videoPlane.videoWidth>0||!dvdStillFrame.hidden)') and sample()['src']!=before_dvd['src'],'new DVD root picture',90)
        wait(lambda:mcp('ui.state',context=identity).get('dvd') and mcp('ui.state',context=identity).get('fullyLoaded'),'DVD native VM')
        state=mcp('ui.state',context=identity)
        if state.get('dvdMenu'):mcp('ui.command',context=identity,command='Select')
        wait(lambda:not mcp('ui.state',context=identity).get('dvdMenu') and sample()['frames']>before_frames+30 and page.evaluate('!videoPlane.paused&&videoPlane.currentTime>.5&&!videoPlane.error'),'DVD feature',90)
        first,second=advancing('current DVD feature epoch moving output')
        rows.append(dict(gate='native-DVD-root-select-feature',passed=True,before=first,after=second))
        print('PASS '+a.engine+' actual Windows DVD feature',flush=True)
        page.screenshot(path=str(out/(stamp+'-'+a.engine+'-dvd.png')))
        mcp('ui.command',context=identity,command='DVD Next Chapter')
        old=sample();wait(lambda:sample()['frames']>old['frames']+15 and page.evaluate('!videoPlane.paused&&!videoPlane.error'),'DVD chapter output',60)
        rows.append(dict(gate='DVD-chapter-resume',passed=True))
        mcp('media.control',context=identity,operation='stop');wait(lambda:not mcp('ui.state',context=identity).get('fullyLoaded'),'DVD Stop',20)
        rows.append(dict(gate='DVD-bounded-Stop',passed=True));context.close();browser.close()
except StopIteration:pass
except Exception as exc:
    failure=stage+': '+str(exc)
    if page:
        try:page.screenshot(path=str(out/(stamp+'-'+a.engine+'-failure.png')))
        except Exception:pass
finally:
    if owned:
        try:api('stop')
        except Exception:pass
    end=time.monotonic()+60
    while time.monotonic()<end:
        if identity not in mcp('ui.list').get('contexts',[]):break
        time.sleep(.3)
    else:cleanup.append('Owned UI did not retire')
    report=dict(task='MIM-WIN-001',engine=a.engine,server='Windows185 stock/Java8',physicalIPhone=False,
        rows=rows,failure=failure,cleanup=cleanup,passed=failure is None and not cleanup,finalActivity=mcp('server.activity'))
    (out/(stamp+'-'+a.engine+'-windows.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(engine=a.engine,passed=report['passed'],failure=failure,cleanup=cleanup)),flush=True)
if not report['passed']:raise SystemExit(1)
