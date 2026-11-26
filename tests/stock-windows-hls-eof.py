#!/usr/bin/env python3
"""Actual Windows185 HLS tail/caption EOF, without the native STV terminal Pause.

This separately qualifies the production browser decoder and public HLS API.
It must not be reported as native STV EOF or physical iPhone certification.
"""
import argparse,base64,hashlib,json,os,subprocess,time,tomllib
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from playwright.sync_api import sync_playwright
from bounded_browser_rpc import bounded

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--run-stock185',action='store_true')
p.add_argument('--engine',choices=('chromium','webkit'),required=True)
p.add_argument('--encoder',choices=('auto','software'),default='software',help='Explicit software tail baseline; auto is an independent hardware comparison')
p.add_argument('--decoder-log',action='store_true',help='Bounded WebKit GStreamer diagnostic for this owned decoder')
p.add_argument('--candidate-playback',action='store_true',help='Explicit local production JS candidate; not installed-build acceptance')
a=p.parse_args()
if not a.run_stock185:raise SystemExit('Explicit Windows185 authorization required')
data=tomllib.loads((ROOT.parent/'android-client/config/firetv.toml').read_text())
cfg=data['servers']['windows_fixed']
assert cfg['address']=='192.168.10.185' and cfg['stock'] is True
base='http://192.168.10.185:8080/SageTVWebPlayer/'
user=cfg.get('web_username') or data['servers']['vibe']['web_username']
password=cfg.get('web_password') or data['servers']['vibe']['web_password']
owned=None;page=None;cleanup=[];rows=[];failure=None;stage='idle-preflight';completed=False;vendor_sha=None
out=ROOT/'artifacts/active/MIM-WIN-001';out.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())

def request(path,values=None,mcp=False):
    target=cfg['core_mcp_base_url'].rstrip('/')+'/' if mcp else base
    auth='Bearer '+cfg['core_mcp_token'] if mcp else 'Basic '+base64.b64encode((user+':'+password).encode()).decode()
    r=Request(target+path,data=urlencode(values).encode() if values is not None else None,headers={'Authorization':auth})
    with urlopen(r,timeout=30) as response:return json.load(response)

def activity():return request('v1/control',dict(action='server.activity'),True)
def hls(action,**v):
    values=dict(action=action,**v)
    return request('api/hls?'+urlencode(values)) if action=='status' else request('api/hls',values)
def sample():return page.evaluate('''()=>{const s=WIN_TAIL,v=s.video;return{
 frames:s.frames,time:v.currentTime,duration:v.duration,ended:v.ended,paused:v.paused,
 width:v.videoWidth,error:v.error?.code||null,errorMessage:v.error?.message||'',caption:s.caption.textContent,
 captionSeen:s.captionSeen,presentationEnded:s.ended,captionError:s.captions.lastError,
 received:s.captions.received,hlsErrors:s.hlsErrors,player:s.player.snapshot()}}''')
def wait(test,label,seconds=60):
    deadline=time.monotonic()+seconds
    while time.monotonic()<deadline:
        page.wait_for_timeout(150);v=sample()
        if v['error']:
            rows.append(dict(gate='actual-decoder-error',state=v))
            raise RuntimeError('Actual decoder error: '+str(v['error']))
        if test(v):return v
    rows.append(dict(gate=label,passed=False,last=v));raise RuntimeError('Timed out '+label)

try:
    if activity().get('safeToRestart') is not True:raise RuntimeError('Independently idle Windows185 required')
    with sync_playwright() as pw:
        if a.engine=='webkit':subprocess.run(['bash','/workspace/release-manifest/scripts/prepare-headless-audio.sh'],check=True,timeout=15)
        decoder_env=dict(os.environ,GST_DEBUG='2',GST_DEBUG_NO_COLOR='1',GST_DEBUG_FILE=str(out/(stamp+'-webkit-decoder.log'))) if a.decoder_log and a.engine=='webkit' else None
        browser=pw.webkit.launch(headless=True,env=decoder_env) if a.engine=='webkit' else pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
        context=browser.new_context(http_credentials={'username':user,'password':password},service_workers='block')
        stage='browser-page';print('STAGE '+stage,flush=True)
        page=context.new_page();original=page.evaluate
        page.on('requestfailed',lambda r:print('RESOURCE_FAILURE '+r.url.split('?')[0]+' '+str(r.failure),flush=True))
        page.evaluate=lambda *args,**kw:bounded(original,*args,**kw)
        # Isolate the DOM harness, not media/network/decoder behavior. Load the
        # actual authenticated shell but omit its unrelated legacy library /
        # artwork / Wasm startup. Production MiniPlayback/caption JS is unchanged.
        page.route(base+'js/app.js',lambda route:route.fulfill(status=200,content_type='application/javascript',body='/* isolated EOF harness */'))
        page.goto(base+'index.html',wait_until='domcontentloaded')
        print('PAGE '+page.url,flush=True)
        for asset in ('js/miniclient-core.js','js/miniclient-streaming.js','js/miniclient-playback.js','js/miniclient-captions.js','js/atsc-captions.js','vendor/hlsjs/hls.min.js'):
            print('ASSET '+asset,flush=True)
            if asset=='js/miniclient-playback.js' and a.candidate_playback:
                bounded(page.add_script_tag,content=(ROOT/'src/main/webapp'/asset).read_text(),seconds=20)
            elif asset.startswith('vendor/'):
                # Playwright's external script injection can hang on this
                # Windows Basic-auth challenge. Use the same authenticated
                # server bytes, never a bundled/different Hls implementation.
                auth='Basic '+base64.b64encode((user+':'+password).encode()).decode()
                with urlopen(Request(base+asset,headers={'Authorization':auth}),timeout=15) as response:
                    raw=response.read(2*1024*1024+1)
                if len(raw)>2*1024*1024:raise RuntimeError('Vendor asset exceeds bounded limit')
                vendor_sha=hashlib.sha256(raw).hexdigest()
                bounded(page.add_script_tag,content=raw.decode('utf-8'),seconds=20)
            else:bounded(page.add_script_tag,url=base+asset,seconds=20)
        stage='production-controller-create';print('STAGE '+stage,flush=True)
        page.evaluate('''()=>{
 const s=window.WIN_TAIL={frames:0,captionSeen:false,ended:false,hlsErrors:[]};
 const Base=Hls;window.Hls=class extends Base{constructor(...args){super(...args);this.on(Base.Events.ERROR,(_,d)=>{if(s.hlsErrors.length<24)s.hlsErrors.push({type:d.type,details:d.details,fatal:d.fatal,reason:d.reason,errorName:d.error?.name,message:d.error?.message})})}};
 const v=s.video=document.createElement('video');v.muted=true;v.playsInline=true;
 v.style.cssText='position:fixed;inset:0;width:100vw;height:100vh;z-index:2147483646;background:#000';
 s.caption=document.createElement('div');document.body.append(v,s.caption);
 s.captions=new SageMiniCaptions({Decoder:SageAtscCaptions,timeMs:()=>Math.round(v.currentTime*1000),
   sourceTimeMs:()=>s.player.absoluteTime(),fetch:async p=>{const r=await fetch('api/captions?'+new URLSearchParams({action:'read',...p}));if(!r.ok)throw Error('Caption read refused');return r.json()},
   render:text=>{s.caption.textContent=text;if(text.trim())s.captionSeen=true}});
 s.player=new SageMiniPlayback({video:v,settings:()=>({maxBufferSeconds:60}),loadHls:async()=>Hls,
   resolveUrl:p=>new URL(p,location.href).href,
   status:async id=>{const r=await fetch('api/hls?session='+encodeURIComponent(id),{cache:'no-store'});if(!r.ok)throw Error('HLS status refused');return r.json()},
   recover:async()=>{throw Error('Unexpected recovery; no producer replay')},
   presentationEnded:()=>{s.ended=true;s.captions.stop()}});
 v.addEventListener('timeupdate',()=>s.player.progress());
 v.addEventListener('playing',()=>s.player.promoteBuffer());
 v.addEventListener('canplay',()=>s.player.maybePlay());
 v.addEventListener('ended',()=>s.player.ended().catch(()=>{s.endError=true}));
 function frame(){v.requestVideoFrameCallback(()=>{s.frames++;frame()})}frame();return true;
}''')
        stage='fixture-and-owned-producer';print('STAGE '+stage,flush=True)
        media=request('api/media?id=21314')
        if 'VibeCaptionTest' not in str(media):raise RuntimeError('Canonical caption fixture mismatch')
        produced=hls('start',id=21314,segment=0,audio=0,start=78,
            stream_profileSchemaVersion=8,stream_player='hls',stream_videoMode='transcode',
            stream_videoKbps=1500,stream_resolution='480',stream_encoder=a.encoder,
            stream_deinterlace='on',stream_captions='608',stream_captionService=1,
            stream_captionAuthority='cc1',stream_browserCaptionRendering='true')
        owned=produced.get('session')
        if not owned or produced.get('mediaId')!=21314:raise RuntimeError('Wrong HLS owner')
        event=dict(hlsSession=owned,playlistUrl=produced['playlistUrl'],startSeconds=78,
            durationMs=produced['durationMs'],transport='hls',streamSettings=produced.get('streamSettings'))
        stage='production-controller-start';print('STAGE '+stage,flush=True)
        page.evaluate('''event=>{const s=WIN_TAIL;s.captions.start(event);
 s.player.start(event).catch(()=>{s.startError=true});return true}''',event)
        stage='tail-pictures';print('STAGE '+stage,flush=True)
        first=wait(lambda v:v['frames']>8 and v['width']>0 and not v['paused'] and v['time']>.3,'actual tail pictures',75)
        caption=wait(lambda v:v['captionSeen'],'actual CEA608 tail caption',20)
        ended=wait(lambda v:v['ended'] and v['presentationEnded'] and not v['caption'].strip(),'actual decoder EOF and cleared captions',35)
        if ended['frames']<=first['frames']+15 or ended['captionError']:raise RuntimeError('Tail output/caption progression failed')
        state=hls('status',session=owned)
        rows.append(dict(gate='actual-HLS-decoder-EOF-and-caption-clear',passed=True,first=first,caption=caption,last=ended,
            producer={k:state.get(k) for k in ('running','exitCode','encoder','segments','hlsSeconds','error')}))
        page.evaluate('()=>{WIN_TAIL.captions.stop();WIN_TAIL.player.stop();return true}')
        if not hls('stop',session=owned).get('stopped'):raise RuntimeError('Owned HLS Stop rejected')
        owned=None;completed=True;context.close();browser.close()
except BaseException as exc:
    failure=stage+': '+str(exc).splitlines()[0][:400]
    if owned:
        try:
            state=hls('status',session=owned)
            rows.append(dict(gate='failed-producer-observation',producer={k:state.get(k) for k in ('running','exitCode','encoder','segments','hlsSeconds','error','playlistReady','streamSettings','fallbackStage','hardwareDecodeFallback')}))
            if stage=='tail-pictures' and len(owned)==32 and all(c in '0123456789abcdef' for c in owned):
                auth='Basic '+base64.b64encode((user+':'+password).encode()).decode()
                with urlopen(Request(base+'hls/'+owned+'/seg_00000.ts',headers={'Authorization':auth}),timeout=12) as response:
                    raw=response.read(8*1024*1024+1)
                if len(raw)<=8*1024*1024:
                    (out/(stamp+'-'+a.engine+'-'+a.encoder+'-failed-segment.ts')).write_bytes(raw)
        except Exception:cleanup.append('Failure producer observation unavailable')
    if page:
        try:rows.append(dict(gate='failed-decoder-observation',state=sample()))
        except Exception:pass
finally:
    if owned:
        try:
            if not hls('stop',session=owned).get('stopped'):cleanup.append('Owned HLS Stop refused')
        except Exception:cleanup.append('Owned HLS cleanup unknown')
    report=dict(task='MIM-WIN-001',engine=a.engine,encoderPreference=a.encoder,server='Windows185 stock/Java8',
        nativeSTV=False,physicalIPhone=False,isolatedDomHarness=True,candidatePlayback=a.candidate_playback,rows=rows,failure=failure,cleanup=cleanup,
        vendorAssetSha256=vendor_sha,passed=completed and failure is None and not cleanup,finalActivity=activity())
    (out/(stamp+'-'+a.engine+'-hls-eof.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(engine=a.engine,passed=report['passed'],failure=failure,cleanup=cleanup)),flush=True)
if not report['passed']:raise SystemExit(1)
