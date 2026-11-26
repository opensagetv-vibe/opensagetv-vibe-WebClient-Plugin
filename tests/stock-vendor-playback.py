#!/usr/bin/env python3
"""WP01-004 real pinned mpegts.js/hls.js MSE, stock232 generated source only."""
import hashlib,importlib.util,json,os,time
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
OUT=ROOT/'artifacts/active/WEB-020';OUT.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());identity='da92a86446be'
rows=[];cleanup=[];owned=None;page=None;context=None;pw=None;browser=None;passed=False;failure=None;assets={}
def mcp(action,**v):return C.request(cfg,'/v1/control',dict(action=action,**v),mcp=True,timeout=8)
def api(action,**v):return C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action=action,session=owned,**v))
def idle():
    a=C.activity(cfg)
    if a.get('recordingCount')!=0 or a.get('connectedClientCount')!=0 or mcp('ui.list').get('contexts'):raise RuntimeError('Require independently idle stock232')
def wait(test,label,seconds=60):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        if test():return
        page.wait_for_timeout(100)
    raise RuntimeError('Timed out: '+label)
def observe(response):
    global owned
    path=urlparse(response.url).path
    if '/vendor/' in path and path.endswith('.js'):
        try:
            data=response.body();assets[path.rsplit('/',2)[-2]+'/'+path.rsplit('/',1)[-1]]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
        except Exception:pass
    if '/api/miniclient' in path and response.request.method=='POST':
        try:
            r=response.json()
            if r.get('session') and r.get('clientId','').replace(':','').lower()==identity:owned=r['session']
        except Exception:pass
def retire():
    global owned,context
    if owned:
        try:api('stop')
        except Exception:pass
        owned=None
    if context:context.close();context=None
    end=time.monotonic()+90
    while time.monotonic()<end:
        if identity not in mcp('ui.list').get('contexts',[]):return
        time.sleep(.3)
    raise RuntimeError('Exact native test UI did not retire')
try:
    idle();resolved=mcp('media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/VibeCaptionTest-1080i-CEA608-90s-2s.ts')
    if resolved.get('mediaFileId')!=20905:raise RuntimeError('Canonical generated source identity changed')
    pw=sync_playwright().start()
    if pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
        for mode,version in [('mpegts','1.8.0'),('hls','1.7.3')]:
            idle();mcp('media.clear_watched',media_id=20905,confirm='true')
            context=browser.new_context(viewport={'width':852,'height':393},http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block')
            page=context.new_page();page.on('response',observe)
            page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify({player:"+json.dumps(mode)+",videoMode:'transcode',videoKbps:1200,resolution:'480',deinterlace:'on'}));")
            page.add_init_script("(()=>{const s=window.VENDOR_FIELD={appends:0,bytes:0,frames:0,done:false},append=SourceBuffer.prototype.appendBuffer;SourceBuffer.prototype.appendBuffer=function(b){s.appends++;s.bytes+=b.byteLength;return append.apply(this,arguments);};document.addEventListener('DOMContentLoaded',()=>{const v=document.getElementById('videoPlane');const f=()=>{if(s.done)return;s.frames++;v.requestVideoFrameCallback(f);};v.requestVideoFrameCallback(f);});})()")
            page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
            wait(lambda:owned is not None and identity in mcp('ui.list').get('contexts',[]),'owned native UI')
            wait(lambda:api('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'),'native first frame')
            if not mcp('media.watch',context=identity,media_id=20905,wait_ms=0).get('accepted'):raise RuntimeError('Watch rejected')
            def moving():
                if page.locator('#autoplayBtn').is_visible():page.locator('#autoplayBtn').click()
                return page.evaluate('VENDOR_FIELD.frames>=15&&videoPlane.currentTime>.5&&videoPlane.videoWidth>0&&!videoPlane.paused')
            wait(moving,'actual '+mode+' video',90)
            actual=page.evaluate('({mpegts:window.mpegts?.version,hls:window.Hls?.version})').get(mode)
            if actual!=version:raise RuntimeError('Expected pinned vendor version '+version+', observed '+str(actual))
            loader=page.locator('#stats').text_content()
            if ('mpegts.js '+version if mode=='mpegts' else 'HLS '+version) not in loader:raise RuntimeError('Actual negotiated loader differs from requested '+mode)
            before=page.evaluate('({time:videoPlane.currentTime,frames:VENDOR_FIELD.frames})');page.wait_for_timeout(1000)
            after=page.evaluate('({time:videoPlane.currentTime,frames:VENDOR_FIELD.frames})')
            if after['time']<=before['time']+.3 or after['frames']<=before['frames']:raise RuntimeError('No actual presented progress')
            if not api('command',command=6).get('ok'):raise RuntimeError('Pause rejected')
            wait(lambda:page.evaluate('videoPlane.paused'),'actual Pause',15)
            pause_time=page.evaluate('videoPlane.currentTime');page.wait_for_timeout(800)
            if abs(page.evaluate('videoPlane.currentTime')-pause_time)>.2:raise RuntimeError('Pause clock advanced')
            if not api('command',command=7).get('ok'):raise RuntimeError('Play rejected')
            wait(lambda:page.evaluate('old=>!videoPlane.paused&&videoPlane.currentTime>old+.5',pause_time),'actual resumed output',20)
            metrics=page.evaluate("()=>({mainThreadAppends:VENDOR_FIELD.appends,mainThreadBytes:VENDOR_FIELD.bytes,frames:VENDOR_FIELD.frames,bufferedRanges:Array.from({length:videoPlane.buffered.length},(_,i)=>[videoPlane.buffered.start(i),videoPlane.buffered.end(i)]),blobSource:videoPlane.currentSrc.startsWith('blob:'),sourceObjectType:videoPlane.srcObject?.constructor?.name||null})")
            # mpegts1.8 can own MSE in a real worker. The main-thread prototype
            # then sees zero appends even though actual MSE output is buffered
            # and decoded. Record that boundary, not a fabricated append count.
            worker_mse=metrics['sourceObjectType']=='MediaSourceHandle'
            if not metrics['bufferedRanges'] or not (metrics['mainThreadAppends']>0 or worker_mse):raise RuntimeError('No verified appended MSE output')
            metrics['workerMseHandleObserved']=worker_mse
            rows.append(dict(mode=mode,vendorVersion=actual,actualLoaderVerified=True,passed=True,before=before,after=after,pauseTime=pause_time,mse=metrics))
            print('PASS real '+mode+' MSE start/advance/Pause/resume',flush=True)
            retire()
        browser.close();passed=True
except Exception as e:
    failure=dict(type=type(e).__name__,message=str(e)[:250])
    if page:
        try:page.screenshot(path=str(OUT/(stamp+'-vendor-failure.png')))
        except Exception:pass
finally:
    if owned or context:
        try:retire()
        except Exception:cleanup.append('Exact native/browser retirement unavailable')
    if browser:
        try:browser.close()
        except Exception:cleanup.append('Browser close failed')
    if pw:
        try:pw.stop()
        except Exception:cleanup.append('Playwright close failed')
    result=dict(passed=passed and not cleanup,stockServer='.232',engine='chromium',physicalPhone=False,realVendorPlayback=True,rows=rows,assets=assets,failure=failure,cleanup=cleanup)
    with (OUT/(stamp+'-real-vendor.json')).open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result));raise SystemExit(0 if result['passed'] else 1)
