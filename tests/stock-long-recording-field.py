#!/usr/bin/env python3
"""Real 5.5h source, late HLS epochs and bounded soak using production loader.

No Core Watch/seek/bookmark changes: public HLS API owns disposable producers.
This is host playback/large-offset coverage, NOT a 5.5-hour elapsed soak or
native STV timeline/growing-changeover/physical-phone certification.
"""
import argparse,importlib.util,json,os,shlex,subprocess,time
from pathlib import Path
from urllib.parse import urlencode,urlparse
from playwright.sync_api import sync_playwright
from bounded_browser_rpc import bounded
from playback_activity import observe_activity
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--engine',choices=('chromium','webkit'),required=True)
p.add_argument('--soak-seconds',type=int,default=120)
p.add_argument('--only-soak',action='store_true',help='One late-offset sustained run, without repeating completed landing/tail rows')
p.add_argument('--elapsed-soak-seconds',type=int,choices=(7200,10800),help='Explicit real2h/3h wall-clock run from source0; no late-seek matrix replay')
p.add_argument('--profile-smoke',action='store_true',help='One20s actual1Mbps/480p WEB104 consumer, not multi-hour certification')
p.add_argument('--profile-encoder',choices=('auto','software'),default='auto',help='Focused profile comparison only')
p.add_argument('--profile-start',type=int,choices=(0,18000),default=18000,help='Focused profile timestamp comparison only')
p.add_argument('--decoder-log',action='store_true',help='Bounded focused WebKit decoder warnings, no network trace')
p.add_argument('--require-isolation',action='store_true',help='Opt-in dedicated resource measurement, not normal playback')
p.add_argument('--require-other-client',action='store_true',help='Focused coexistence gate; do not control the existing client')
a=p.parse_args()
if a.elapsed_soak_seconds:p.error('Multi-hour testing removed from required scope by user; use a short focused gate')
if a.require_isolation and a.require_other_client:p.error('Isolation and coexistence are mutually exclusive')
if not 20<=a.soak_seconds<=600:p.error('Bounded soak must be20..600s')
if a.elapsed_soak_seconds and not a.only_soak:p.error('Elapsed soak requires --only-soak')
if a.profile_smoke and (a.elapsed_soak_seconds or a.only_soak):p.error('Profile smoke is a separate focused gate')
if not a.profile_smoke and (a.profile_encoder!='auto' or a.profile_start!=18000):p.error('Profile comparisons require --profile-smoke')
if a.decoder_log and (not a.profile_smoke or a.engine!='webkit'):p.error('Decoder log is only for the focused WebKit gate')
out=ROOT/'artifacts/active'/('WEB-106' if a.require_other_client else 'WEB-104' if a.profile_smoke else 'WP11-008');out.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
report=dict(passed=False,physicalPhone=False,nativeCoreWatch=False,elapsedMultiHourSoak=False,
    engine=a.engine,mediaId=1444,rows=[],cleanup=[])
owned=None;stop_intent=False;page=context=browser=pw=ssh=None
report['resourceSamples']=[]
path=out/(stamp+'-'+a.engine+('-elapsed' if a.elapsed_soak_seconds else '-sustained' if a.only_soak else '')+'-long-recording.json')
report['requestedElapsedSoakSeconds']=a.elapsed_soak_seconds or 0
report['coTenancyObserved']=False
report['activitySamples']=[]
def save():path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')

def activity():
    value=observe_activity(C.activity(cfg),require_isolation=a.require_isolation,
        require_other_client=a.require_other_client)
    report['activitySamples'].append(value)
    report['coTenancyObserved'] |= value['coTenancyObserved']
    report['resourceScope']='shared-server' if report['coTenancyObserved'] else 'server-container'
    return value

def resources():
    global ssh
    if not a.only_soak:return
    if ssh is None:ssh=C.ssh(cfg)
    rows=C.remote(ssh,'docker stats --no-stream --format '+shlex.quote('{{json .}}')+' '+shlex.quote(cfg['unraid_container_name']))
    value=json.loads(rows)
    report['resourceSamples'].append(dict(elapsedSeconds=round(time.monotonic()-resource_start,3),
        activity=activity(),**{key:value.get(key) for key in ('CPUPerc','MemUsage','MemPerc','PIDs')}))
    if a.elapsed_soak_seconds:
        free=int(C.remote(ssh,'docker exec '+shlex.quote(cfg['unraid_container_name'])+' df -PB1 /tmp/sagetv-webplayer-hls').splitlines()[-1].split()[3])
        report['resourceSamples'][-1]['availableSpoolBytes']=free
        if free<2*1024**3:raise RuntimeError('Retire owned soak before storage headroom is exhausted')
        report['stage']='elapsed-running';save()

def api(action,**values):
    path='/SageTVWebPlayer/api/hls'
    return C.request(cfg,path+'?'+urlencode(dict(action=action,**values))) if action=='status' else C.request(cfg,path,dict(action=action,**values),timeout=60)

def sample():
    return page.evaluate("()=>{const s=__longField,v=s.video,p=s.player.snapshot();return{time:v.currentTime,frames:s.frames,frameSourceCurrent:s.frameSource===v.currentSrc,paused:v.paused,width:v.videoWidth,height:v.videoHeight,ready:v.readyState,error:v.error?.code||null,errorMessage:v.error?.message||null,playerError:p.error,startError:s.startError,ended:v.ended,absoluteTimeMs:p.timeMs,recoveries:p.recoveries,clockRegressions:p.clockRegressions,bufferPhase:p.bufferPhase}}")

def wait(test,label,seconds=60):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        v=sample()
        if v['error']:
            report['last']=v
            raise RuntimeError('Actual browser decoder error')
        if test(v):return v
        page.wait_for_timeout(150)
    report['last']=v;raise RuntimeError('Timed out '+label+'; no replay')

try:
    report['stage']='read-only-source-preflight'
    activity()
    resource_start=time.monotonic();resources()
    before=C.request(cfg,'/SageTVWebPlayer/api/media?id=1444')
    if before.get('title')!='Reconstruction: America After the Civil War' or before.get('duration')!=19800000 or before.get('segments')!=1:
        raise RuntimeError('Exact5.5hour source changed')
    files=before.get('files',[])
    if len(files)!=1 or files[0].get('name')!='ReconstructionAmericaAftertheCivilWar-48000171-0.ts' or not files[0].get('streamAccessible'):
        raise RuntimeError('Original source not accessible')
    report['sourceBytes']=files[0].get('streamSize')
    if a.elapsed_soak_seconds:
        free=int(C.remote(ssh,'docker exec '+shlex.quote(cfg['unraid_container_name'])+' df -PB1 /tmp/sagetv-webplayer-hls').splitlines()[-1].split()[3])
        if free<10*1024**3:raise RuntimeError('Explicit elapsed soak needs10GiB initial spool headroom')
    pw=sync_playwright().start()
    if a.engine=='webkit':
        subprocess.run(['bash','/workspace/release-manifest/scripts/prepare-headless-audio.sh'],check=True,timeout=15)
    report['stage']='browser-launch'
    decoder_env=dict(os.environ,GST_DEBUG='2',GST_DEBUG_NO_COLOR='1',
        GST_DEBUG_FILE=str(out/(stamp+'-webkit-decoder.log'))) if a.decoder_log else None
    browser=pw.webkit.launch(headless=True,env=decoder_env) if a.engine=='webkit' else pw.chromium.launch(
        headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
    context=browser.new_context(http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block')
    page=context.new_page();original=page.evaluate
    report['scriptRequests']=[]
    page.on('response',lambda r:report['scriptRequests'].append(dict(path=urlparse(r.url).path,status=r.status)) if urlparse(r.url).path.endswith('.js') and len(report['scriptRequests'])<12 else None)
    page.on('requestfailed',lambda r:report['scriptRequests'].append(dict(path=urlparse(r.url).path,failure=r.failure)) if urlparse(r.url).path.endswith('.js') and len(report['scriptRequests'])<12 else None)
    page.evaluate=lambda *args,**kw:bounded(original,*args,**kw)
    # Actual same-origin legacy shell, no source selected/native UI created.
    # Codec diagnostics preloads5other videos. A fulfilled empty document also
    # failed Chromium subresource loading; never weaken browser network guards.
    page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/index.html',wait_until='domcontentloaded')
    report['stage']='real-runtime-script-load'
    for asset in ('js/miniclient-core.js','js/miniclient-streaming.js','js/miniclient-playback.js','vendor/hlsjs/hls.min.js'):
        page.add_script_tag(url=cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/'+asset)
    page.evaluate("()=>{window.__longErrors=[];const Base=Hls;window.Hls=class extends Base{constructor(...args){super(...args);this.on(Base.Events.ERROR,(_,d)=>{if(__longErrors.length<24)__longErrors.push({type:d.type,details:d.details,fatal:d.fatal,reason:d.reason,errorName:d.error?.name,message:d.error?.message})})}};return true}")
    page.evaluate("()=>{const v=document.createElement('video');v.muted=true;v.playsInline=true;document.body.append(v);const s=window.__longField={video:v,frames:0,done:false,frameSource:''};s.player=new SageMiniPlayback({video:v,settings:()=>({maxBufferSeconds:60}),loadHls:async()=>Hls,resolveUrl:p=>new URL(p,location.href).href,status:async id=>{const r=await fetch('api/hls?session='+encodeURIComponent(id),{cache:'no-store'});if(!r.ok)throw Error('Status refused');return r.json()},recover:async()=>{throw Error('Unexpected recovery; no producer replay')}});function f(){const source=v.currentSrc;v.requestVideoFrameCallback(()=>{if(s.done)return;if(source&&source===v.currentSrc){s.frames++;s.frameSource=source}f()})}f();return true}")
    page.evaluate("()=>{__longField.video.style.cssText='position:fixed;inset:0;width:100vw;height:100vh;z-index:2147483647;background:#000';return true}")
    page.evaluate("()=>{const s=__longField,v=s.video;v.addEventListener('timeupdate',()=>s.player.progress());v.addEventListener('playing',()=>s.player.promoteBuffer());v.addEventListener('canplay',()=>s.player.maybePlay());v.addEventListener('ended',()=>s.player.ended().catch(()=>{s.endError=true}));return true}")
    # Offsets exceed32-bit milliseconds only at much longer durations; these
    # specifically cover a real broadcast timestamp start and5.5-hour index.
    for target,soak in ([(a.profile_start,20)] if a.profile_smoke else [(0,a.elapsed_soak_seconds)] if a.elapsed_soak_seconds else [(18000,a.soak_seconds)] if a.only_soak else [(1980,5),(10800,5),(18000,a.soak_seconds),(17970,5),(19785,0)]):
        report['stage']='start-offset-'+str(target)
        activity()
        profile=dict(stream_profileSchemaVersion=8,stream_player='hls',stream_videoMode='transcode',
            stream_videoKbps=1000,stream_resolution='480',stream_encoder=a.profile_encoder) if a.elapsed_soak_seconds or a.profile_smoke else {}
        produced=api('start',id=1444,segment=0,audio=0,start=target,**profile);owned=produced.get('session');stop_intent=False
        report['ownedSession']=owned;save()
        if not owned or produced.get('mediaId')!=1444 or abs(produced.get('startSeconds',-1)-target)>.001:
            raise RuntimeError('Wrong HLS producer source/origin')
        if a.elapsed_soak_seconds or a.profile_smoke:
            settings=produced.get('streamSettings') or {}
            requested=settings.get('requested') or {};effective=settings.get('effective') or {}
            report['elapsedProfile']=settings;save()
            if str(requested.get('videoKbps'))!='1000' or str(requested.get('resolution'))!='480' or effective.get('videoTargetKbps')!=1000:
                raise RuntimeError('Public HLS did not honor explicit bounded elapsed-soak profile')
        event=dict(hlsSession=owned,playlistUrl=produced['playlistUrl'],startSeconds=target,
            durationMs=produced['durationMs'],transport='hls',streamSettings=produced.get('streamSettings'))
        page.evaluate("event=>{__longField.startError=null;__longField.player.start(event).catch(()=>{__longField.startError=true});return true}",event)
        first=wait(lambda v:v['frameSourceCurrent'] and v['frames']>8 and v['time']>.3 and not v['paused'],'new large-offset pictures',75)
        began=time.monotonic();samples=[];last_progress=began;last_frames=first['frames']
        next_resource=time.monotonic()+30
        if soak:
            while time.monotonic()-began<soak:
                page.wait_for_timeout(min(5000,int(max(.1,soak-(time.monotonic()-began))*1000)))
                current=sample();samples.append(current)
                if current['error'] or current['recoveries'] or current['clockRegressions']:
                    raise RuntimeError('Large-offset decoder/recovery/clock failure')
                if current['frames']>last_frames:
                    last_progress=time.monotonic();last_frames=current['frames']
                elif time.monotonic()-last_progress>45:
                    report['last']=current
                    raise RuntimeError('No presented-frame progress for45s; retire owned soak')
                if a.only_soak and time.monotonic()>=next_resource:
                    resources();next_resource=time.monotonic()+30
                    if a.elapsed_soak_seconds:
                        report['latestPlayback']=current
                        report['elapsedPlaybackSeconds']=round(time.monotonic()-began,3);save()
                        print(json.dumps(dict(observingElapsedSoak=True,elapsedSeconds=report['elapsedPlaybackSeconds'],frames=current['frames'],recoveries=current['recoveries'],clockRegressions=current['clockRegressions'])),flush=True)
            last=sample()
            if last['frames']<=first['frames']+10 or last['time']<first['time']+soak*.7:
                raise RuntimeError('Real-time long-offset output not advancing')
        else:
            last=wait(lambda v:v['ended'],'actual source tail ended',45)
        error=last['absoluteTimeMs']-(target+last['time'])*1000
        if a.profile_smoke and last['height']!=480:raise RuntimeError('Actual decoded profile height differs')
        if abs(error)>5:raise RuntimeError('Production file-relative clock mismatch')
        state=api('status',session=owned)
        report['rows'].append(dict(gate='actual-source-tail-ended' if not soak else 'actual-large-offset-moving-output',
            passed=True,targetSeconds=target,soakSeconds=round(time.monotonic()-began,3),
            first=first,last=last,clockErrorMs=error,encoder=state.get('encoder'),samples=samples))
        page.evaluate('()=>{__longField.player.stop();return true}')
        stop_intent=True;report['ownedStopIntent']=True;save()
        if not api('stop',session=owned).get('stopped'):raise RuntimeError('Owned producer Stop rejected')
        owned=None
        resources()
        if not page.evaluate("()=>{const v=__longField.video;return v.paused&&!v.getAttribute('src')&&!v.srcObject&&v.readyState===0}"):
            raise RuntimeError('Owned decoder not unloaded')
        print('PASS '+a.engine+' source offset '+str(target),flush=True)
    activity()
    after=C.request(cfg,'/SageTVWebPlayer/api/media?id=1444')
    keys=('watched','watchedCompletely','serverResumeSeconds')
    if any(before.get(k)!=after.get(k) for k in keys):raise RuntimeError('Original watched/resume metadata changed')
    report['originalWatchStateUnchanged']=True;report['elapsedMultiHourSoak']=bool(a.elapsed_soak_seconds);report['passed']=True
except Exception as e:
    detail=str(e).splitlines()[0]
    # Only these own-page operations contain no config/auth or remote payload.
    safe=isinstance(e,RuntimeError) or detail.startswith(('Page.evaluate:','Page.goto:','Page.add_script_tag:'))
    report['failure']=dict(type=type(e).__name__,message=detail[:220] if safe else 'Bounded field observation failed')
    if owned:
        try:
            state=api('status',session=owned)
            report['producer']={k:state.get(k) for k in ('encoder','running','exitCode','hlsSeconds','segments','durationMs','startSeconds','inputMode','error','seekStrategy','streamSettings')}
        except Exception:report['producerObservationUnavailable']=True
    if page:
        try:report['hlsErrors']=page.evaluate('()=>window.__longErrors||[]')
        except Exception:report['hlsErrorsUnavailable']=True
finally:
    if page:
        try:page.evaluate('()=>{if(window.__longField){__longField.done=true;__longField.player.stop();__longField.video.remove();delete window.__longField}return true}')
        except Exception:report['cleanup'].append('Browser consumer cleanup unknown')
    if owned and not stop_intent:
        try:
            stop_intent=True;report['ownedStopIntent']=True;save()
            if not api('stop',session=owned).get('stopped'):raise RuntimeError('Owned Stop not accepted')
        except Exception:report['cleanup'].append('Owned HLS Stop unknown; not replayed')
    for resource in (context,browser,pw):
        if resource:
            try:bounded(resource.stop if resource is pw else resource.close)
            except Exception:report['cleanup'].append('Browser retirement unknown')
    if ssh:ssh.close()
    report['passed']=report['passed'] and not report['cleanup']
    save()
    print(json.dumps(dict(passed=report['passed'],rows=len(report['rows']),path=str(path),failure=report.get('failure'),cleanup=report['cleanup'],coTenancyObserved=report['coTenancyObserved'],resourceScope=report.get('resourceScope'))),flush=True)
raise SystemExit(0 if report['passed'] else 1)
