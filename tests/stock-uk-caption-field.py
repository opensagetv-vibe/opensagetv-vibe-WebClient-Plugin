#!/usr/bin/env python3
"""Unchanged UK broadcast: actual browser frames, STV Teletext/DVB lifecycle.

One ephemeral owned UI, one selected transport/encoder, public MCP setup only.
Never resets original recording metadata, edits Core, or logs subtitle text.
"""
import argparse,hashlib,importlib.util,json,os,time
from pathlib import Path
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright
from bounded_browser_rpc import bounded
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--engine',choices=('chromium','webkit'),default='chromium')
p.add_argument('--mode',choices=('qsv','software','copy','fallback'),default='qsv')
p.add_argument('--transport',choices=('hls','mpegts'),default='hls')
p.add_argument('--source',choices=('breakfast','taskmaster'),default='breakfast')
p.add_argument('--caption-offset',type=int,choices=(-1000,1000),help='Additional original-source signed presentation-delay field gate')
p.add_argument('--fullscreen',action='store_true',help='One qualified production fullscreen completion, not a guessed TV toggle')
p.add_argument('--natural-clears',action='store_true',help='Observe actual clear callbacks during uninterrupted moving playback; requires signed observer')
p.add_argument('--off-only',action='store_true',help='Focused real STV CC1/CC2/Off visibility; no seek or pause matrix')
p.add_argument('--off-cycles',type=int,default=1,help='1..8 explicit CC1/CC2/Off cycles, with visible captions before each Off')
p.add_argument('--unified-graphics',choices=('off','on'),help='Isolated WP13-003 stock compatibility A/B; does not change household settings')
a=p.parse_args();identity='da92a86446be';owned=None;page=None;pw=None;context=None;browser=None
if not 1<=a.off_cycles<=8:p.error('Off cycles must be1..8')
if a.natural_clears and a.caption_offset is None:p.error('Natural-clear observation requires the signed observer')
passed=False;rows=[];cleanup=[];errors=[];failure={};subtitle_metadata=[];observed_errors=[];initial_gaps=[];observed_alignments=[]
out=ROOT/'artifacts/active'/('WP13-003' if a.unified_graphics is not None else 'WP03-008' if a.caption_offset is not None else 'WEB-020');out.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
files={'breakfast':'Breakfast-26711345-0.ts','taskmaster':'Taskmaster-ThisIsFoodGlue-26714235-0.ts'}
def mcp(action,**v):
    # Public Seek is synchronous and can outlast a client default while its
    # replacement is already playing. Bound ONE setup response, no replay.
    failure['lastRequest']='mcp:'+action
    return C.request(cfg,'/v1/control',dict(action=action,**v),mcp=True,timeout=60 if action=='media.seek' else 30)
def api(action,**v):
    if action in ('status','streamSettings','playbackState'):
        return C.request(cfg,'/SageTVWebPlayer/api/miniclient?'+urlencode(dict(action=action,session=owned,**v)),timeout=20)
    return C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action=action,session=owned,**v),timeout=20)
def guard():
    act=C.activity(cfg);uis=mcp('ui.list').get('contexts',[])
    if act.get('recordingCount')!=0 or act.get('connectedClientCount')!=0 or uis:raise RuntimeError('Existing activity; require independent exact prior UI retirement')
def wait(test,label,seconds=45):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        if test():return
        page.wait_for_timeout(150)
    raise RuntimeError('Timed out: '+label)
def observe(response):
    global owned
    try:
        if '/api/miniclient' in response.url and response.request.method=='POST':
            j=response.json()
            if j.get('session') and j.get('clientId','').replace(':','').lower()==identity:owned=j['session']
        elif '/api/subtitles' in response.url:
            j=response.json()
            subtitle_metadata.append(dict(scope=j.get('scope'),queue=j.get('queue'),teletext=j.get('teletext'),dvb=j.get('dvbBitmap')))
            del subtitle_metadata[:-12]
    except Exception:pass
def video():
    return page.evaluate(r"""()=>{
      const v=videoPlane,s=UK_FIELD,buffered=[];
      for(let i=0;i<Math.min(4,v.buffered.length);i++)buffered.push([v.buffered.start(i),v.buffered.end(i)]);
      if(v.currentTime<1&&v.videoWidth&&buffered.length&&buffered[0][0]>v.currentTime+.25){
        s.gaps=s.gaps||[];const key=v.currentSrc+':'+buffered[0][0];
        if(s.gapKey!==key&&s.gaps.length<12){s.gapKey=key;s.gaps.push({time:v.currentTime,buffered,paused:v.paused,ready:v.readyState});}
      }
      return{time:v.currentTime,paused:v.paused,ready:v.readyState,width:v.videoWidth,prompt:!autoplayBtn.hidden,error:v.error?.code||null,errorMessage:v.error?.message||null,frames:s.frames,last:s.last,frameSourceCurrent:s.source===v.currentSrc,buffered};
    }""")
def moving(label):
    clicked=False;end=time.monotonic()+60;before=video();last=before
    while time.monotonic()<end:
        last=video()
        if last['error']:
            failure['video']=last
            raise RuntimeError('Actual browser media error')
        if last['prompt'] and not clicked:
            page.locator('#autoplayBtn').click(timeout=3000);clicked=True
        baseline=before['last'] if before['frameSourceCurrent'] else 0
        if last['width']>0 and not last['paused'] and last['ready']>=2 and last['frameSourceCurrent'] and last['frames']>=before['frames']+8 and last['last']>baseline+.15:
            rows.append(dict(gate=label,passed=True,actualBrowserActivation=clicked,video=last));print('PASS '+label,flush=True);return
        page.wait_for_timeout(150)
    failure['video']=last;raise RuntimeError('No advancing presented frames: '+label)
def seek_source(target,label):
    before=api('streamSettings').get('session');src=page.evaluate('videoPlane.currentSrc')
    began=time.monotonic()
    if not mcp('media.seek',context=identity,target_ms=target).get('accepted'):raise RuntimeError('One source seek rejected')
    control_ms=round((time.monotonic()-began)*1000)
    # Accepted queued intent or old presented frames are not settled output.
    wait(lambda:api('streamSettings').get('session')!=before and page.evaluate('(old)=>videoPlane.currentSrc!==old',src),'new producer and browser source for '+label,60)
    moving(label)
    settings=api('streamSettings');native=mcp('ui.state',context=identity)
    hls=C.request(cfg,'/SageTVWebPlayer/api/hls?action=status&session='+settings['session'])
    # The synchronous commissioning API may return after replacement playback
    # has already advanced. Prove producer target plus current decoded output,
    # not a frozen requested-position clock or an absolute TV airing epoch.
    start=hls.get('startSeconds')
    if not isinstance(start,(int,float)) or abs(start*1000-target)>100:
        failure['seekOrigin']=dict(targetMs=target,producerStartSeconds=start,
            nativeRequestedMs=settings.get('nativeSeek',{}).get('targetMs'),
            nativeFileTimeMs=native.get('rawMediaTimeMs'),video=video(),
            producerRunning=hls.get('running'),producerExitCode=hls.get('exitCode'))
        raise RuntimeError('Replacement producer has wrong seek origin')
    samples=[];end=time.monotonic()+8
    while True:
        raw=native.get('rawMediaTimeMs',native.get('mediaTimeMs',-100000));v=video();expected=target+v['time']*1000
        samples.append(dict(nativeMs=raw,decodedRelativeMs=round(v['time']*1000),differenceMs=round(raw-expected)))
        if abs(raw-expected)<=2000:break
        if time.monotonic()>=end:
            failure['seekClock']=dict(targetMs=target,observed=samples,producerStartSeconds=hls.get('startSeconds'))
            raise RuntimeError('Presented native file clock outside target tolerance')
        # Public Core clock polling trails a new decoded browser frame. Observe
        # that independently; never replay Seek or accept the old-source clock.
        page.wait_for_timeout(200);native=mcp('ui.state',context=identity)
    rows.append(dict(gate=label+'-ownership',passed=True,newProducer=True,newBrowserSource=True,targetMs=target,setupControlMs=control_ms,nativeFileTimeMs=raw,nativeFileSamples=samples,producerStartSeconds=start,actualTransport=hls.get('transport')))
def picture():
    return page.evaluate("""()=>{const t=localCaptions.textContent,c=dvbCaptions,p=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let pixels=0;for(let i=3;i<p.length;i+=4)if(p[i])pixels++;return{text:t,pixels,time:videoPlane.currentTime,paused:videoPlane.paused};}""")
def visible(kind):
    window_start=page.evaluate('videoPlane.currentTime*1000')
    wait(lambda:(len(picture()['text'].strip())>0 if kind=='teletext' else picture()['pixels']>100),'visible '+kind,40)
    def sample():
        result=[]
        for _ in range(12):
            v=picture();text=v.pop('text');v['textLength']=len(text);v['textSha256']=hashlib.sha256(text.encode()).hexdigest();result.append(v);page.wait_for_timeout(250)
        return result
    samples=sample();reserve_hold=None
    if samples[-1]['time']<=samples[0]['time']+1:
        # First picture is not an uninterrupted-playback promise. The normal
        # health controller may refill its reserve after the first segment.
        # Observe that once, without issuing Play/Seek or hiding its duration.
        page.evaluate('videoInfoBtn.click()')
        info=json.loads(page.locator('#videoInfoText').text_content())
        reserve_hold=dict(initialSamples=samples,playback=info.get('playback'))
        page.evaluate('closeVideoInfo.click()')
        if not info.get('playback',{}).get('rebuffering'):
            failure['captionSamples']=samples;failure['playback']=info.get('playback')
            raise RuntimeError('Caption sample froze outside normal reserve buffering')
        began=time.monotonic();moving(kind+'-bounded-reserve-recovery')
        reserve_hold['recoveryObservedMs']=round((time.monotonic()-began)*1000)
        samples=sample()
    if samples[-1]['time']<=samples[0]['time']+1:
        failure['captionSamples']=samples
        failure['video']=video()
        status=api('status')
        failure['playback']=status.get('playback')
        settings=api('streamSettings');active=settings.get('session')
        hs=C.request(cfg,'/SageTVWebPlayer/api/hls?action=status&session='+str(active)) if active else {}
        failure['producer']={k:hs.get(k) for k in ('running','playlistReady','hlsSeconds','segments','durationMs','startSeconds','exitCode','error','timings','streamSettings')}
        raise RuntimeError('Caption sample video not advancing')
    if kind=='teletext' and not any(v['textLength'] for v in samples):raise RuntimeError('No visible Teletext')
    if kind=='dvb' and not any(v['pixels']>100 for v in samples):raise RuntimeError('No visible bitmap')
    rows.append(dict(gate=kind+'-visible-advancing-source',passed=True,samples=samples,reserveHold=reserve_hold))
    if a.caption_offset is not None:
        # A seek/resume can deliver a legitimate catch-up cue. Require fresh
        # later presentation at its real source clock, never a synthetic cue.
        wait(lambda:page.evaluate('(kind)=>UK_FIELD.captionTiming.some(r=>r.kind===kind&&r.offsetMs==='+str(a.caption_offset)+'&&r.lateMs>=-50&&r.lateMs<=450)',kind),kind+' signed source-clock delay',45)
        timing=page.evaluate('(kind)=>UK_FIELD.captionTiming.filter(r=>r.kind===kind).slice(-12)',kind)
        rows.append(dict(gate=kind+'-actual-signed-source-clock-delay',passed=True,offsetMs=a.caption_offset,samples=timing))
    if a.natural_clears:
        # Stay on this selected service and advancing source, with no Pause,
        # Off, Seek or synthetic cue to manufacture a clear.
        wait(lambda:page.evaluate('(p)=>UK_FIELD.captionClears.some(r=>r.kind===p.kind&&r.clockMs>p.begin+1500&&!r.paused)',dict(kind=kind,begin=window_start)),kind+' actual natural clear',35)
        clears=page.evaluate('(p)=>UK_FIELD.captionClears.filter(r=>r.kind===p.kind&&r.clockMs>p.begin+1500&&!r.paused).slice(-8)',dict(kind=kind,begin=window_start))
        rows.append(dict(gate=kind+'-natural-clear-during-uninterrupted-playback',passed=True,samples=clears))
    page.screenshot(path=str(out/(stamp+'-'+a.engine+'-'+a.mode+'-'+a.transport+'-'+kind+'.png')))
try:
    guard();source=mcp('media.resolve_exact_path',path='/var/media/videos/USER_TEST/'+files[a.source])
    if not source.get('mediaFileId'):raise RuntimeError('Original source unavailable')
    pw=sync_playwright().start()
    browser=pw.webkit.launch(headless=True) if a.engine=='webkit' else pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':852,'height':393},http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block')
    page=context.new_page();original_evaluate=page.evaluate
    page.evaluate=lambda *args,**kwargs:bounded(original_evaluate,*args,**kwargs)
    page.on('response',observe);page.on('pageerror',lambda e:errors.append(dict(message=str(e),stack=e.stack)))
    profile=dict(player=a.transport,videoMode='copy' if a.mode=='copy' else 'transcode',encoder='nvenc' if a.mode=='fallback' else 'software' if a.mode=='copy' else a.mode,videoKbps=1200,resolution='source' if a.mode=='copy' else '480',deinterlace='off' if a.mode=='copy' else 'on',allowFallback=a.mode=='fallback',audioLanguage='eng',audioCodec='aac')
    if a.caption_offset is not None:profile['captionOffsetMs']=a.caption_offset
    authority=dict(mode='stv',cc1Type='teletext' if a.source=='breakfast' else 'dvb',cc1Language='eng',cc2Type='dvb',cc2Language='eng')
    page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebStreaming.v1',"+json.dumps(json.dumps(profile))+");localStorage.setItem('sagetvWebCaptionAuthority.v1',"+json.dumps(json.dumps(authority))+");")
    if a.unified_graphics is not None:
        page.add_init_script("localStorage.setItem('sagetvWebMiniClientSettings.v1',JSON.stringify({unifiedGraphics:"+str(a.unified_graphics=='on').lower()+"}));")
    page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
    wait(lambda:owned is not None and identity in mcp('ui.list').get('contexts',[]),'owned UI')
    wait(lambda:api('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'),'native first frame')
    if a.unified_graphics is not None:
        actual=api('status').get('connection',{}).get('unifiedGraphics')
        if actual is not (a.unified_graphics=='on'):raise RuntimeError('Requested unified graphics was not negotiated')
        rows.append(dict(gate='exact-unified-graphics-session',passed=True,enabled=actual))
    configured_before=api('streamSettings').get('configured')
    if not configured_before or configured_before.get('player')!=a.transport or configured_before.get('videoMode')!=profile['videoMode'] or configured_before.get('encoder')!=profile['encoder']:raise RuntimeError('Native requested profile does not match the test')
    saved_before=page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')")
    page.evaluate("()=>{const s=window.UK_FIELD={frames:0,last:0,source:'',done:false};function arm(){const source=videoPlane.currentSrc;videoPlane.requestVideoFrameCallback((n,m)=>{if(s.done)return;if(source&&source===videoPlane.currentSrc){s.frames++;s.last=m.mediaTime;s.source=source;}arm();});}arm();}")
    if a.caption_offset is not None:
        page.evaluate(r"""()=>{
          const s=UK_FIELD,p=SageMiniCaptions.prototype,start=p.start;s.captionTiming=[];s.captionClears=[];
          function install(controller){
            const o=controller.o;
            for(const [key,kind] of [['render','teletext'],['renderBitmap','dvb'],['clearBitmap','dvb']]){
              const current=o[key];if(!current||current.ukTimingObserver)continue;
              function observed(...args){
                const result=current.apply(this,args);
                try{
                  const isClear=key==='clearBitmap'||key==='render'&&!args[0]&&controller.teletext;
                  if(isClear){s.captionClears.push({kind,clockMs:controller.o.sourceTimeMs?controller.o.sourceTimeMs():controller.o.timeMs(),paused:!!globalThis.videoPlane?.paused});if(s.captionClears.length>80)s.captionClears.shift();}
                  const cue=kind==='teletext'?args[2]:args[0];
                  if(cue&&Number.isFinite(cue.ptsMs)&&(!cue.clear)&&
                     (kind!=='teletext'||args[1]==='teletext'&&args[0])){
                    const clock=controller.o.sourceTimeMs?controller.o.sourceTimeMs():controller.o.timeMs();
                    const offset=Number(controller.options.captionOffsetMs)||0;
                    s.captionTiming.push({kind,offsetMs:offset,sourceClockMs:clock,cuePtsMs:cue.ptsMs,lateMs:clock-cue.ptsMs-offset});
                    if(s.captionTiming.length>80)s.captionTiming.shift();
                  }
                }catch(_){s.captionTimingUnavailable=true;}
                return result;
              }
              observed.ukTimingObserver=true;o[key]=observed;
            }
          }
          p.start=function(...args){const result=start.apply(this,args);install(this);return result};
        }""")
    page.evaluate(r"""()=>{
      const s=UK_FIELD;s.errors=[];s.alignments=[];
      const p=SageMiniPlayback.prototype,original=p.error;
      const align=p.alignInitialCopyGap;
      if(align)p.alignInitialCopyGap=function(){const result=align.apply(this,arguments);if(result&&s.alignments.length<8)s.alignments.push({startSeconds:this.startSeconds,bufferedSampleSeconds:this.initialCopyGapAlignedSeconds});return result;};
      p.error=function(error){
        try{
        if(s.errors.length<24){
          const text=error&&error.message?error.message:String(error);
          const hls=text.match(/^HLS (networkError|mediaError|muxError|otherError) ([A-Za-z0-9_]{1,64})$/);
          const reasons=['Producer ended before the expected media end','FFmpeg stopped without completing its output','Browser stopped loading available HLS segments','FFmpeg stream stopped advancing with no source-read progress','Browser reached a premature HLS end','Fatal HLS error'];
          const reason=reasons.find(value=>text.includes(value));
          const buffered=[];for(let i=0;i<Math.min(4,videoPlane.buffered.length);i++)buffered.push([videoPlane.buffered.start(i),videoPlane.buffered.end(i)]);
          s.errors.push({kind:hls?hls[0]:reason||'other',relativeSeconds:Number(videoPlane.currentTime)||0,recoveries:this.budget.count,buffered,ready:videoPlane.readyState,paused:videoPlane.paused,fragmentLoading:this.fragmentLoading,phase:this.bufferPhase});
        }
        }catch(_){s.observerUnavailable=true;}
        return original.apply(this,arguments);
      };
    }""")
    if not mcp('media.watch',context=identity,media_id=source['mediaFileId'],wait_ms=0).get('accepted'):raise RuntimeError('Watch rejected')
    wait(lambda:(mcp('ui.state',context=identity).get('media') or {}).get('mediaFileId')==source['mediaFileId'],'exact source')
    moving('original-source-playback')
    if a.fullscreen:
        wait(lambda:api('contentState',mediaId=source['mediaFileId']).get('ready'),'exact loaded fullscreen intent source')
        layout=api('contentState',mediaId=source['mediaFileId']).get('layout')
        if layout=='preview':
            if not api('showContent',mediaId=source['mediaFileId']).get('ok'):raise RuntimeError('One qualified fullscreen request was not confirmed')
        elif layout!='fullscreen':raise RuntimeError('Unknown fullscreen layout; no guessed toggle')
        wait(lambda:api('contentState',mediaId=source['mediaFileId']).get('layout')=='fullscreen','native fullscreen')
        rows.append(dict(gate='qualified-native-fullscreen-no-watch-replay',passed=True))
    if not a.off_only:seek_source(30000,'settled-30s-source-seek')
    settings=api('streamSettings');effective=settings.get('active',{}).get('effective',{})
    # Save only payload-free effective plan, never paths/session IDs.
    if not effective:
        active=settings.get('session')
        hs=C.request(cfg,'/SageTVWebPlayer/api/hls?action=status&session='+str(active)) if active else {}
        effective=(hs.get('streamSettings') or {}).get('effective',{})
    rows.append(dict(gate='actual-effective-plan',passed=True,effective=effective))
    if a.mode=='copy' and effective.get('video')!='copy':raise RuntimeError('Strict copy was not actual copy')
    if a.mode=='qsv' and not effective.get('hardwareEncode'):raise RuntimeError('QSV request was not hardware encoded')
    if a.mode=='software' and (effective.get('hardwareEncode') or effective.get('video')=='copy'):raise RuntimeError('Software profile not actual software encode')
    if a.mode=='fallback' and (effective.get('hardwareEncode') or effective.get('video')!='libx264' or not effective.get('fallbackReason')):raise RuntimeError('Unavailable NVENC did not produce truthful software fallback')
    for state,kind in ([('CC1','teletext'),('CC2','dvb')] if a.source=='breakfast' else [('CC1','dvb')]):
        before=api('streamSettings').get('session')
        if not mcp('captions.set',context=identity,state=state).get('ok'):raise RuntimeError('Public STV caption command rejected')
        visible(kind)
        if api('streamSettings').get('session')!=before:raise RuntimeError('Caption selection restarted A/V')
        if a.off_only:continue
        if not mcp('media.control',context=identity,operation='pause').get('ok'):raise RuntimeError('Pause rejected')
        wait(lambda:video()['paused'],'Pause')
        held=picture();page.wait_for_timeout(2500);after=picture()
        if abs(after['time']-held['time'])>.1 or (kind=='teletext' and after['text']!=held['text']):raise RuntimeError('Paused caption changed or video moved')
        if not mcp('media.control',context=identity,operation='play').get('ok'):raise RuntimeError('Play rejected')
        moving(kind+'-resume')
        seek_source(60000 if kind=='teletext' else 45000,kind+'-post-seek-frames');visible(kind)
    if not mcp('captions.set',context=identity,state='Off').get('ok'):raise RuntimeError('Off rejected')
    failure['offNativeState']=mcp('captions.get',context=identity).get('state')
    wait(lambda:not picture()['text'].strip() and picture()['pixels']==0,'Off clears both renderers',10)
    rows.append(dict(gate='stv-Off-clears-without-AV-restart',passed=True))
    for cycle in range(1,a.off_cycles):
        for state,kind in ([('CC1','teletext'),('CC2','dvb')] if a.source=='breakfast' else [('CC1','dvb')]):
            before=api('streamSettings').get('session')
            if not mcp('captions.set',context=identity,state=state).get('ok'):raise RuntimeError('Cycle caption selection rejected')
            visible(kind)
            if not mcp('captions.set',context=identity,state='Off').get('ok'):raise RuntimeError('Cycle Off rejected')
            failure['offNativeState']=mcp('captions.get',context=identity).get('state')
            wait(lambda:not picture()['text'].strip() and picture()['pixels']==0,'cycle Off clears both renderers',10)
            if api('streamSettings').get('session')!=before:raise RuntimeError('Caption cycle restarted A/V')
            rows.append(dict(gate='repeated-visible-service-Off',cycle=cycle+1,kind=kind,passed=True))
    if api('streamSettings').get('configured')!=configured_before or page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')")!=saved_before:raise RuntimeError('Native configured or browser saved profile changed')
    rows.append(dict(gate='native-configured-and-browser-saved-profiles-preserved',passed=True))
    if errors:raise RuntimeError('Browser JavaScript errors')
    observed_errors=page.evaluate('UK_FIELD.errors||[]');initial_gaps=page.evaluate('UK_FIELD.gaps||[]');observed_alignments=page.evaluate('UK_FIELD.alignments||[]');passed=True
except Exception as e:
    failure['failedRequest']=failure.get('lastRequest')
    failure.update(type=type(e).__name__,message=str(e)[:350] if isinstance(e,RuntimeError) else 'Bounded field check failed',reasonType=type(getattr(e,'reason',None)).__name__)
    if page:
        try:
            # Existing diagnostic drawer only; never issue Play/Seek/recovery.
            page.evaluate('videoInfoBtn.click()')
            snapshot=json.loads(page.locator('#videoInfoText').text_content()).get('playback',{})
            failure['clientPlayback']={k:snapshot.get(k) for k in ('timeMs','startSeconds','paused','attached','starting','rebuffering','blocked','recovering','recoveries','clockRegressions','firstFrameMs','bufferPhase','bufferTargetSeconds','lastFailureClass')}
            failure['clientPlayback']['errorPresent']=bool(snapshot.get('error'))
            diagnostic=json.loads(page.locator('#videoInfoText').text_content())
            cc=diagnostic.get('diagnostics',{}).get('captions',{})
            failure['captionOwner']={k:cc.get(k) for k in ('authority','resolvedSlot','renderOwner','effectiveType','pid','page','service','stvStateSeen','stvState','queuePending','received')}
            failure['offNativeStateAfter']=mcp('captions.get',context=identity).get('state')
            image=picture();failure['remainingCaptionPixels']=image['pixels'];failure['remainingCaptionTextLength']=len(image['text'])
            failure['observedClientErrors']=page.evaluate('UK_FIELD.errors||[]')
            failure['initialGaps']=page.evaluate('UK_FIELD.gaps||[]')
            failure['observedAlignments']=page.evaluate('UK_FIELD.alignments||[]')
        except Exception:failure['diagnosticSnapshotUnavailable']=True
        try:page.screenshot(path=str(out/(stamp+'-uk-caption-failure.png')))
        except Exception:pass
finally:
    if owned:
        try:api('stop')
        except Exception:cleanup.append('Exact owned UI Stop unverified')
    for resource in (context,browser,pw):
        if resource:
            try:bounded(resource.stop if resource is pw else resource.close)
            except Exception:cleanup.append(type(resource).__name__+' bounded shutdown unverified')
    end=time.monotonic()+90
    while time.monotonic()<end:
        try:
            if identity not in mcp('ui.list').get('contexts',[]):break
        except Exception:pass
        time.sleep(.3)
    else:cleanup.append('Owned native UI retirement unverified')
    if passed:failure={}
    # Browser context is retired above; already-captured failure observations
    # remain available without reopening/replaying the source.
    if failure:observed_errors=failure.get('observedClientErrors',[])
    result=dict(passed=passed and not cleanup,realStock232=True,physicalIPhone=False,engine=a.engine,mode=a.mode,transport=a.transport,source=a.source,offCycles=a.off_cycles,unifiedGraphics=a.unified_graphics,captionOffsetMs=a.caption_offset,rows=rows,errors=errors,cleanup=cleanup,failure=failure,observedClientErrors=observed_errors,initialGaps=failure.get('initialGaps',initial_gaps),observedAlignments=failure.get('observedAlignments',observed_alignments))
    target=out/(stamp+'-uk-caption-field.json')
    target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=result['passed'],rows=len(rows),failure=failure,cleanup=cleanup))+'\n'+str(target),flush=True)
raise SystemExit(0 if passed and not cleanup else 1)
