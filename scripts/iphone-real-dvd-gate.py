#!/usr/bin/env python3
"""Exact owned iPhone PAL/sparse/ALADDIN playback, stock public test setup.

Actual frame callbacks and native clocks, not simulated Safari. Navigation is
existing public MCP commissioning, not physical-key/finger proof. No settings,
bookmarks, optional hooks, Core changes or ordered-input replay.
"""
import argparse,asyncio,importlib.util,json,logging,sys,time
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
sys.path.insert(0,str(BRIDGE/'tools/native_inspector'))
import wireless_inspect as W
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
clock_spec=importlib.util.spec_from_file_location('dvd_field_clock',ROOT/'scripts/dvd-field-clock.py')
clock_check=importlib.util.module_from_spec(clock_spec);clock_spec.loader.exec_module(clock_check)
identity='123c8282e1ee';stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
report=dict(utc=datetime.now(timezone.utc).isoformat(),passed=False,physicalPhone=True,
    physicalFingerGesture=False,navigation='Existing public stock MCP test setup',inputReplayed=False,rows=[])
sources=[('pal','/var/media/OpenSageTV_Vibe_Tests/VIBE_AUTHORED_DVD_PAL',21008,576),
 ('sparse','/var/media/OpenSageTV_Vibe_Tests/VIBE_AUTHORED_DVD_SPARSE',21012,480),
 ('aladdin','/var/media/videos/Aidens_Movies/ALADDIN',2504,480)]
sources.append(('angle','/var/media/OpenSageTV_Vibe_Tests/VIBE_AUTHORED_DVD_MULTIANGLE',21029,480))
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source',choices=('pal','sparse','aladdin','angle'))
parser.add_argument('--root-return',action='store_true',help='Exercise root command after the settled feature')
parser.add_argument('--angles',action='store_true',help='Verify actual red/green/blue picture branches and wrap with explicit stock seeks')
parser.add_argument('--companion',action='store_true',help='Require separately checkpointed optional companion borrow; defer Stop for exact hook restoration')
parser.add_argument('--beginning',action='store_true',help='One synthetic production Start Feature action before observing video; requires companion borrow')
parser.add_argument('--fresh-fixture',action='store_true',help='Clear watched metadata only on the exact generated angle/sparse fixture before its one Watch')
parser.add_argument('--terminal',action='store_true',help='Observe actual terminal EOS acknowledgement and polling retirement on the generated angle fixture')
parser.add_argument('--sparse-subtitles',action='store_true',help='Actual sparse physical Spanish SPU, seek/pause/Off on canonical generated disc')
parser.add_argument('--observe-existing',action='store_true',help='Observe the already-confirmed exact source instead of replaying Watch')
parser.add_argument('--task',choices=('WEB-014','WEB-096','WEB-099'),default='WEB-014',help='Owning affected physical gate')
parser.add_argument('--soak-seconds',type=int,default=0,help='Explicit20..600s ALADDIN physical sustained observation, no extra controls')
parser.add_argument('--player',choices=('hls','native'),help='WEB-099 only: borrow one production Player setting and restore exactly')
parser.add_argument('--seek-ms',type=int,help='WEB-099 only: one exact public DVD seek before observation')
parser.add_argument('--pixels',action='store_true',help='Bounded10s decoded-picture readback alongside presentation counters')
parser.add_argument('--disable-remote',action='store_true',help='WEB-099 comparison of the existing MSE fallback video property; restored afterward')
parser.add_argument('--handoff-mse',action='store_true',help='WEB-099: explicit synthetic same-producer native-to-MSE engine trial, not a reproduced automatic stall')
options=parser.parse_args()
if options.player and (options.task!='WEB-099' or options.source!='aladdin' or options.observe_existing or options.companion):parser.error('Player comparison requires fresh WEB-099 ALADDIN only')
if options.seek_ms is not None and (options.task!='WEB-099' or options.source!='aladdin' or options.observe_existing or options.companion or not 0<=options.seek_ms<=900000):parser.error('Seek requires fresh WEB-099 ALADDIN and0..900000ms')
if options.pixels and (options.task!='WEB-099' or not options.soak_seconds):parser.error('Pixel witness requires WEB-099 soak')
if options.disable_remote and (options.task!='WEB-099' or options.player!='hls'):parser.error('Remote-property comparison requires WEB-099 HLS/MSE borrow')
if options.handoff_mse and (options.task!='WEB-099' or options.source!='aladdin' or options.player or options.observe_existing or options.companion):parser.error('Handoff requires fresh native WEB-099 ALADDIN only')
if options.soak_seconds and (options.source!='aladdin' or not 20<=options.soak_seconds<=600):parser.error('Soak requires explicit ALADDIN and20..600seconds')
out=ROOT/'artifacts/active'/options.task;out.mkdir(parents=True,exist_ok=True)
if options.angles and options.source!='angle':parser.error('Angle test requires explicit angle source')
if options.beginning and not options.companion:parser.error('Beginning action requires explicit companion borrow')
if options.fresh_fixture and options.source not in ('angle','sparse'):parser.error('Fresh-fixture reset requires exact generated angle/sparse source')
if options.terminal and options.source!='angle':parser.error('Terminal gate requires exact generated angle fixture')
if options.sparse_subtitles and (options.source!='sparse' or options.companion):parser.error('Sparse subtitles require exact native sparse source, no companion')
if options.observe_existing and (not options.source or options.fresh_fixture):parser.error('Existing-source observation requires one exact source and no metadata reset')
if options.source:sources=[s for s in sources if s[0]==options.source]
else:sources=[s for s in sources if s[0]!='angle']
def mcp(action,**v):
    # A public DVD command can synchronously await a replacement decoder.
    # Bound its ONE response, but never replay it after an unknown outcome.
    return C.request(cfg,'/v1/control',dict(action=action,**v),mcp=True,
        timeout=8 if action in ('ui.state','ui.list','server.activity','media.resolve_exact_path') else 30)
def guard(expected=None):
    a=C.activity(cfg)
    if a.get('recordingCount')!=0 or a.get('connectedClientCount')!=0 or mcp('ui.list').get('contexts')!=[identity]:raise RuntimeError('Require only exact phone and no recordings')
    n=mcp('ui.state',context=identity)
    if expected and (not n.get('dvd') or (n.get('media') or {}).get('mediaFileId')!=expected):raise RuntimeError('Current disc ownership changed')
    return n
original=W.evaluate
class Trigger:
    def read_text(self,**_):return '__REAL_DVD_PHONE_GATE__'
async def evaluate(session,expression):
    if expression!='__REAL_DVD_PHONE_GATE__':return await original(session,expression)
    async def ev(s):return await original(session,s)
    async def checkpoint():
        await ev("(()=>{const s=window.__realDvdField;s.before=videoPlane.currentSrc;s.active=null;s.frames=0;s.last=0;return true;})()")
    async def sample():
        return await ev("(()=>{const s=window.__realDvdField,v=videoPlane;return{epoch:s.epoch,frames:s.frames,frameTime:s.last,time:v.currentTime,ready:v.readyState,width:v.videoWidth,paused:v.paused,error:v.error?.code||null,changed:v.currentSrc!==s.before,blocked:!autoplayBtn.hidden,still:!dvdStillFrame.hidden,message:osdMessage.textContent};})()")
    async def native():return await asyncio.to_thread(mcp,'ui.state',context=identity)
    async def dvd_state():
        await ev("(()=>{const s=window.__realDvdField;s.pending=true;s.dvd=null;s.failed=false;__iphoneGate.api('status').then(j=>{s.dvd=j.connection?.dvd;s.capabilities=j.connection?.capabilities;}).catch(()=>s.failed=true).finally(()=>s.pending=false);return true;})()")
        for _ in range(100):
            if not await ev('window.__realDvdField.pending'):break
            await asyncio.sleep(.05)
        else:raise RuntimeError('Read-only DVD observation timed out')
        value=await ev('window.__realDvdField.dvd')
        if not value:raise RuntimeError('Read-only DVD observation unavailable')
        return value
    async def wait(test,label,seconds=60):
        deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:
            v=await sample();n=await native()
            if v['error']:raise RuntimeError('Actual Safari media error')
            if v['blocked']:raise RuntimeError('Real Safari Play gesture required; no synthetic activation')
            if test(v,n):return v,n
            await asyncio.sleep(.15)
        report['last']=dict(video=v,native={k:n.get(k) for k in ('dvdMenu','dvdTitle','dvdChapter','mediaTimeMs')})
        raise RuntimeError('Timed out: '+label)
    installed=False;owner_created=False;player_borrowed=False;remote_borrowed=False
    async def save_player(value,restore=False):
        # One normal production Save, not private playback/prototype injection.
        await ev("(()=>{const s=__iphoneGate,b=s.playerBorrow,N=SageMiniStreaming.normalize,raw=localStorage.getItem('sagetvWebStreaming.v1');if(!b)throw Error('Missing player checkpoint');const current=N(JSON.parse(raw||'{}')),expected=N(JSON.parse(b.raw||'{}'));expected.player="+json.dumps(options.player)+";if("+str(restore).lower()+"&&JSON.stringify(current)!==JSON.stringify(expected))throw Error('Preserve unrelated profile edits');const v=N(JSON.parse(b.raw||'{}'));v.player="+json.dumps(value)+";for(const k of Object.keys(SageMiniStreaming.DEFAULTS)){const e=document.getElementById('stream_'+k);if(e){if(e.type==='checkbox')e.checked=!!v[k];else e.value=String(v[k]);}}if(saveStreaming.disabled)throw Error('Save already busy');saveStreaming.click();return true;})()")
        deadline=time.monotonic()+15
        while time.monotonic()<deadline:
            saved=await ev("(()=>{const s=__iphoneGate,N=SageMiniStreaming.normalize,v=N(JSON.parse(localStorage.getItem('sagetvWebStreaming.v1')||'{}')),x=N(JSON.parse(s.playerBorrow.raw||'{}'));x.player="+json.dumps(value)+";return!saveStreaming.disabled&&JSON.stringify(v)===JSON.stringify(x);})()")
            if saved:break
            await asyncio.sleep(.1)
        else:raise RuntimeError('Player Save receipt unknown; no replay')
        if restore:
            await ev("(()=>{const s=__iphoneGate,r=s.playerBorrow.raw;if(r===null)localStorage.removeItem('sagetvWebStreaming.v1');else localStorage.setItem('sagetvWebStreaming.v1',r);delete s.playerBorrow;return true;})()")
    try:
        await asyncio.to_thread(guard)
        if options.task=='WEB-099':
            from field_candidate import playback_revision
            revision=playback_revision(ROOT)
            report['runtimeRevision']=await ev("(()=>({current:[...document.scripts].some(s=>s.src.includes('miniclient-playback.js?"+revision+"')),dvdStartupFallback:typeof SageMiniPlayback.prototype.nativeDvdStartupCandidate==='function'}))()")
            if not all(report['runtimeRevision'].values()):raise RuntimeError('Phone candidate is stale; no test control dispatched')
        # Fresh page reloads retire the older field-batch owner. Reuse the
        # established exact-session observer, never require hidden setup state.
        if not await ev('!!window.__iphoneGate'):
            await ev((ROOT/'tests/iphone-field-owner.js').read_text(encoding='utf-8'))
            owner_created=True
        deadline=time.monotonic()+32
        while not await ev('!!window.__iphoneGate?.done'):
            if time.monotonic()>deadline:raise RuntimeError('No fresh production session poll; no Watch dispatched')
            await asyncio.sleep(.2)
        if options.player:
            current=await asyncio.to_thread(guard)
            if current.get('fullyLoaded') or current.get('loading'):raise RuntimeError('Borrow requires stopped phone')
            original_player=await ev("(()=>{const s=__iphoneGate;if(s.playerBorrow)throw Error('Existing borrow');const raw=localStorage.getItem('sagetvWebStreaming.v1');s.playerBorrow={raw};return SageMiniStreaming.normalize(JSON.parse(raw||'{}')).player;})()")
            player_borrowed=True
            await save_player(options.player)
            report['temporaryPlayer']=options.player
        if options.disable_remote:
            report['remotePlaybackBefore']=await ev("(()=>{const s=__iphoneGate,v=videoPlane;if(!('disableRemotePlayback'in v)||s.remoteBorrow)throw Error('Remote property unavailable/busy');s.remoteBorrow={video:v,before:v.disableRemotePlayback};v.disableRemotePlayback=true;return s.remoteBorrow.before;})()")
            remote_borrowed=True
        await ev("""(()=>{if(!window.__iphoneGate?.api||window.__realDvdField||document.visibilityState!=='visible')throw Error('Require visible owner');const s=window.__realDvdField={before:videoPlane.currentSrc,active:null,epoch:0,frames:0,last:0,done:false};const f=(n,m)=>{if(s.done)return;const src=videoPlane.currentSrc;if(src!==s.active){s.active=src;s.epoch++;s.frames=0;s.last=0;}if(src!==s.before){s.frames++;s.last=m.mediaTime;}videoPlane.requestVideoFrameCallback(f);};videoPlane.requestVideoFrameCallback(f);return true;})()""");installed=True
        if options.handoff_mse:
            await ev("(()=>{const s=__realDvdField,p=SageMiniPlayback.prototype;s.originalStart=p.start;s.startObserver=function(...a){s.player=this;return s.originalStart.apply(this,a);};p.start=s.startObserver;return true;})()")
        for name,path,media_id,height in sources:
            report['stage']='resolve-exact-source'
            await asyncio.to_thread(guard)
            r=await asyncio.to_thread(mcp,'media.resolve_exact_path',path=path)
            if r.get('mediaFileId')!=media_id:raise RuntimeError('Exact disc resolution mismatch')
            if options.fresh_fixture:
                if (name,media_id) not in (('angle',21029),('sparse',21012)):raise RuntimeError('Refuse noncanonical metadata reset')
                current=await asyncio.to_thread(guard)
                if current.get('fullyLoaded'):
                    if (current.get('media') or {}).get('mediaFileId')!=media_id:raise RuntimeError('Preserve another loaded source')
                    report['stage']='one-generated-fixture-stop'
                    if not (await asyncio.to_thread(mcp,'media.control',context=identity,operation='stop')).get('ok'):raise RuntimeError('Fixture Stop rejected')
                    await wait(lambda v,n:not n.get('fullyLoaded') and v['paused'],'fixture Stop before fresh Watch',20)
                if not (await asyncio.to_thread(mcp,'media.clear_watched',media_id=media_id,confirm='true')).get('ok'):raise RuntimeError('Fixture metadata reset rejected')
                report['generatedFixtureWatchedReset']=True
            await checkpoint()
            if options.observe_existing:
                await asyncio.to_thread(guard,media_id)
                await ev("(()=>{__realDvdField.before='';return true;})()")
                report['existingSourceObserved']=True
            else:
                report['stage']='one-watch-intent'
                r=await asyncio.to_thread(mcp,'media.watch',context=identity,media_id=media_id,wait_ms=0)
                if not r.get('accepted'):raise RuntimeError('Watch not accepted; no replay')
            if options.beginning:
                deadline=time.monotonic()+30
                while time.monotonic()<deadline:
                    ready=await ev("(()=>{const b=document.querySelector('[data-companion-dvd=beginning]');return!!b&&!b.disabled&&dvdCompanionStatus.textContent.includes('ready-native-ps');})()")
                    if ready:break
                    await asyncio.sleep(.1)
                else:raise RuntimeError('Current-load Start Feature unavailable')
                await ev("(()=>{const b=document.querySelector('[data-companion-dvd=beginning]');if(!b||b.disabled)throw Error('Start unavailable');b.click();return{oneSyntheticProductionStart:true};})()")
                report['oneSyntheticProductionBeginning']=True
            report['stage']='initial-disc-picture'
            # An already-confirmed menu can be a held decoded picture. It is
            # sufficient for setup, not a new-frame playback acceptance pass.
            v,n=await wait(lambda v,n:n.get('dvd') and (n.get('media') or {}).get('mediaFileId')==media_id and v['changed'] and (v['frames']>=1 or (options.observe_existing and n.get('dvdMenu') and (v['width']>0 or v['still']))),'new disc picture')
            initial_menu=bool(n.get('dvdMenu'))
            if initial_menu:
                await checkpoint();await asyncio.to_thread(guard,media_id)
                report['stage']='one-authored-select'
                if not (await asyncio.to_thread(mcp,'ui.command',context=identity,command='Select')).get('accepted'):raise RuntimeError('Authored default select rejected')
            if options.seek_ms is not None:
                await asyncio.to_thread(guard,media_id);await checkpoint()
                report['oneSeekIntentMs']=options.seek_ms
                if not (await asyncio.to_thread(mcp,'media.seek',context=identity,target_ms=options.seek_ms)).get('accepted'):raise RuntimeError('Seek not accepted; no replay')
            report['stage']='moving-feature'
            # Start Feature is asynchronous. Do not measure its superseded
            # initial-load pictures while the native title clock is still0.
            # This adds readiness, not another Start/seek or a relaxed speed
            # oracle: the following same-epoch wall-clock check is unchanged.
            v,n=await wait(lambda v,n:not n.get('dvdMenu') and v['changed'] and v['frames']>=15 and v['ready']>=2 and not v['paused'] and v['time']>.5
                and (not options.beginning or n.get('mediaTimeMs',0)>500),'moving feature '+name)
            if options.handoff_mse:
                await asyncio.to_thread(guard,media_id)
                report['explicitSyntheticEngineTrial']=True
                report['handoffBefore']=v
                await checkpoint()
                # This is explicitly chosen diagnostic setup, not fake stall
                # state, forced user activation or automatic-fallback proof.
                report['handoffIntent']=await ev("(()=>{const s=__realDvdField,p=s.player,v=videoPlane;if(!p||!p.dvd||p.hls||p.tsPlayer||p.intentPaused||v.paused||SageMiniPlayback.prototype.start!==s.startObserver)throw Error('Native handoff owner changed');SageMiniPlayback.prototype.start=s.originalStart;s.handoff={id:p.id,pending:true};p.start({hlsSession:p.id,playlistUrl:p.status.playlistUrl,dvd:true,dvdGeneration:p.dvdGeneration,startSeconds:p.startSeconds,durationMs:p.durationMs,resumeSeconds:v.currentTime,paused:p.intentPaused,streamSettings:p.streamSettings,recovery:true},false,true).then(()=>{s.handoff.pending=false;s.handoff.engine=p.snapshot().browserEngine;s.handoff.sameProducer=p.id===s.handoff.id;}).catch(e=>{s.handoff.pending=false;s.handoff.error=e.name;});return{oneSameProducerNativeToMse:true,id:s.handoff.id};})()")
                v,n=await wait(lambda v,n:v['changed'] and v['frames']>=15 and not v['paused'] and v['ready']>=2,'explicit native-to-MSE new pictures')
                report['handoffReceipt']=await ev('window.__realDvdField.handoff')
                if report['handoffReceipt'].get('pending') or not report['handoffReceipt'].get('sameProducer') or report['handoffReceipt'].get('engine')!='HLS / MSE':raise RuntimeError('Handoff receipt mismatch; no replay')
            a=v;clocks=[n.get('mediaTimeMs')];speed_started=time.monotonic()
            if options.pixels:
                await ev((ROOT/'tests/iphone-dvd-pixel-cadence.js').read_text(encoding='utf-8'))
            if options.soak_seconds:
                observed=await ev("(()=>{videoInfoBtn.click();const p=JSON.parse(videoInfoText.textContent).playback;closeVideoInfo.click();return{id:p.id,engine:p.browserEngine,hardware:p.status?.hardware,epoch:__realDvdField.epoch};})()")
                report['soakPlaybackStart']=observed
                print(json.dumps(dict(physicalDvdPlaybackStart=observed)),flush=True)
            samples=0;last_note=speed_started;window_start=speed_started;window_before=a;windows=[]
            pixel_windows=[];next_pixels=speed_started+100
            while (time.monotonic()-speed_started<options.soak_seconds if options.soak_seconds else samples<10):
                await asyncio.sleep(.5);b=await sample();n=await native();clocks.append(n.get('mediaTimeMs'))
                samples+=1
                if options.pixels and time.monotonic()>=next_pixels:
                    pixel=await ev("(()=>{const s=__dvdPixels;return{done:s.done,sourceChanged:s.changed,rows:s.rows};})()")
                    pixel_windows.append(dict(elapsedSeconds=time.monotonic()-speed_started,**pixel))
                    report['decodedPixelWindows']=pixel_windows
                    await ev("(()=>{__dvdPixels.done=true;delete window.__dvdPixels;return true;})()")
                    await ev((ROOT/'tests/iphone-dvd-pixel-cadence.js').read_text(encoding='utf-8'))
                    next_pixels=time.monotonic()+100
                if options.soak_seconds and time.monotonic()-last_note>=50:
                    print(json.dumps(dict(physicalDvdSoak=True,seconds=round(time.monotonic()-speed_started),frames=b['frames'],epoch=b['epoch'],error=b['error'])),flush=True);last_note=time.monotonic()
                if b['error'] or b['epoch']!=a['epoch'] or b['paused']:
                    report['failedObservation']=dict(source=name,before=a,after=b,native=n,wallSeconds=time.monotonic()-speed_started)
                    raise RuntimeError('Decoder/source/Pause changed during settled DVD observation')
                if options.soak_seconds and time.monotonic()-window_start>=10:
                    now=time.monotonic();ratio=clock_check.presentation_speed(window_before,b,now-window_start)
                    windows.append(dict(wallSeconds=now-window_start,presentationRatio=ratio,newFrames=b['frames']-window_before['frames']))
                    report['soakWindows']=windows
                    if ratio is None or not .8<=ratio<=1.2:
                        report['failedObservation']=dict(source=name,before=window_before,after=b,native=n)
                        raise RuntimeError('DVD sustained window is not real-time presentation')
                    window_start=now;window_before=b
            wall_seconds=time.monotonic()-speed_started
            if options.pixels:
                report['decodedPixels']=await ev("(()=>{const s=__dvdPixels;return{done:s.done,sourceChanged:s.changed,rows:s.rows};})()")
            speed=clock_check.presentation_speed(a,b,wall_seconds)
            row=dict(source=name,mediaId=media_id,initialMenu=initial_menu,before=a,after=b,nativeClocksMs=clocks,title=n.get('dvdTitle'),chapter=n.get('dvdChapter'),observationWallSeconds=wall_seconds,presentedSpeedRatio=speed)
            report['rows'].append(row)
            if b['epoch']!=a['epoch'] or b['frames']<=a['frames'] or b['frameTime']<=a['frameTime'] or b['time']<=a['time']:raise RuntimeError('Replacement or stalled picture in settled observation: '+name)
            if speed is None or not .8<=speed<=1.2:raise RuntimeError('Actual DVD presented speed differs from wall clock: '+name)
            dvd=await dvd_state()
            if not dvd or (dvd.get('ps') or {}).get('videoHeight')!=height:raise RuntimeError('Native source geometry mismatch')
            row.update(format=(dvd.get('ps') or {}).get('videoHeight'),audioSelector=dvd.get('audioSelector'),nativeClockAdvances=max(clocks)>min(clocks),passed=True)
            row['capabilities']=await ev('window.__realDvdField.capabilities')
            if options.soak_seconds:
                row['productionPlayback']=await ev("(()=>{videoInfoBtn.click();const j=JSON.parse(videoInfoText.textContent);closeVideoInfo.click();return j.playback;})()")
                st=row['productionPlayback'].get('status') or {}
                if row['productionPlayback'].get('recoveries')!=0 or not st.get('running') or not st.get('hardware'):
                    raise RuntimeError('Sustained DVD requires actual live GPU producer and zero recoveries')
            row['optionalCompanion']=options.companion
            print(json.dumps({'source':name,'frames':b['frames']-a['frames'],'nativeClockAdvances':row['nativeClockAdvances']}),flush=True)
            # Picture and native clock proof remain distinct; zero/stuck native
            # clock is recorded as a failure, never renamed decoder-relative.
            if not row['nativeClockAdvances']:raise RuntimeError('Native title clock did not advance: '+name)
            if options.sparse_subtitles:
                # Stock legacy wire may use2, direct PES0x22 or HD flag0x42.
                # All identify the fixture's physical Spanish substream, not
                # logical track1. Do not require one optional navigator flag.
                def spanish(value):return value in (2,0x22,0x42)
                # Observe clones of production responses, never consume the SPU
                # queue with an extra test poll. Restore the exact fetch owner.
                await ev("""(()=>{const s=window.__realDvdField;if(s.realFetch)throw Error('Existing observer');const real=window.fetch;s.realFetch=real;s.spu=null;s.subtitleReads=0;s.subtitleErrors=[];function f(...a){const r=real.apply(this,a),u=new URL(typeof a[0]==='string'?a[0]:a[0].url,location.href);if(u.pathname.endsWith('/api/subtitles')){s.subtitleReads++;r.then(r=>r.clone().json()).then(j=>{if(j.dvdSpu)s.spu=j.dvdSpu;else if(s.subtitleErrors.length<4)s.subtitleErrors.push(j.error||'No DVD state');}).catch(e=>{if(s.subtitleErrors.length<4)s.subtitleErrors.push(e.name);});}return r;}s.fetchObserver=f;window.fetch=f;return true;})()""")
                async def spu_sample():
                    return await ev("(()=>{const s=__realDvdField,c=dvdSpuCanvas,p=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let pixels=0;for(let i=3;i<p.length;i+=4)if(p[i])pixels++;return{state:s.spu,pixels,width:c.width,height:c.height,time:videoPlane.currentTime,paused:videoPlane.paused,reads:s.subtitleReads,errors:s.subtitleErrors};})()")
                async def spu_wait(test,label,seconds=15):
                    end=time.monotonic()+seconds
                    while time.monotonic()<end:
                        item=await spu_sample()
                        if test(item):return item
                        await asyncio.sleep(.15)
                    report['sparseLast']=item
                    raise RuntimeError('Sparse subtitle timeout: '+label)
                async def sparse_command(command):
                    await asyncio.to_thread(guard,media_id)
                    if not (await asyncio.to_thread(mcp,'ui.command',context=identity,command=command)).get('accepted'):raise RuntimeError('Sparse command rejected; no replay')
                initial=await spu_wait(lambda x:x['state'] is not None,'production response')
                selected=initial['state']['selected']
                if selected in (62,8192) or selected<0 or selected&0x80:
                    await sparse_command('DVD Subtitle Toggle')
                    initial=await spu_wait(lambda x:x['state'] and x['state']['selected'] not in (62,8192) and x['state']['selected']>=0 and not x['state']['selected']&0x80,'enabled physical subtitle')
                if not spanish(initial['state']['selected']):
                    previous=initial['state']['selected']
                    await sparse_command('DVD Subtitle Change')
                    await spu_wait(lambda x:x['state'] and x['state']['selected']!=previous,'one language change')
                visible=await spu_wait(lambda x:x['state'] and spanish(x['state']['selected']) and x['pixels']>100,'Spanish physical0x22 pixels')
                row['sparseSpanish']=visible
                await checkpoint()
                if not (await asyncio.to_thread(mcp,'media.seek',context=identity,target_ms=30000)).get('accepted'):raise RuntimeError('Sparse seek rejected')
                await wait(lambda v,n:v['changed'] and v['frames']>=15 and v['ready']>=2 and not v['paused'],'sparse replacement frames')
                row['sparseAfterSeek']=await spu_wait(lambda x:x['state'] and spanish(x['state']['selected']) and x['pixels']>100,'post-seek Spanish')
                if not (await asyncio.to_thread(mcp,'media.control',context=identity,operation='pause')).get('ok'):raise RuntimeError('Pause rejected')
                await wait(lambda v,n:v['paused'],'sparse Pause')
                held=await spu_sample();await asyncio.sleep(20);after=await spu_sample()
                if not after['paused'] or abs(after['time']-held['time'])>.1 or after['pixels']!=held['pixels'] or after['pixels']<=100:raise RuntimeError('Paused sparse subtitle was not retained')
                row['sparsePaused20s']=dict(before=held,after=after)
                # The stock DVD pusher defers VM selector metadata while
                # paused. Qualify paused retention separately, then resume
                # before requesting Off; never invent a browser selector.
                if not (await asyncio.to_thread(mcp,'media.control',context=identity,operation='play')).get('ok'):raise RuntimeError('Resume rejected')
                await wait(lambda v,n:not v['paused'],'sparse resume')
                await sparse_command('DVD Subtitle Toggle')
                row['sparseOff']=await spu_wait(lambda x:x['pixels']==0 and x['state'] and (x['state']['selected'] in (62,8192) or x['state']['selected']<0 or bool(x['state']['selected']&0x80)),'Off clears pixels')
            if options.angles:
                if n.get('dvdAngleCount')!=3:raise RuntimeError('Require independently authored three-angle fixture')
                row['angles']=[]
                for angle,channel in ((1,0),(2,1),(3,2),(1,0)):
                    if row['angles']:
                        await asyncio.to_thread(guard,media_id);await checkpoint()
                        if not (await asyncio.to_thread(mcp,'ui.command',context=identity,command='DVD Angle Change')).get('accepted'):raise RuntimeError('Angle control rejected')
                        # Command acceptance is queued, not completed state.
                        # Wait for the VM angle before one explicit native seek;
                        # otherwise the seek can race the old angle register.
                        if not options.companion:
                            end=time.monotonic()+5
                            while time.monotonic()<end:
                                n=await native()
                                if n.get('dvdAngle')==angle:break
                                await asyncio.sleep(.1)
                            else:raise RuntimeError('Accepted angle did not reach native state')
                        if not options.companion and not (await asyncio.to_thread(mcp,'media.seek',context=identity,target_ms=3000)).get('accepted'):raise RuntimeError('One explicit angle-test seek rejected')
                        v,n=await wait(lambda v,n:v['changed'] and v['frames']>=15 and not v['paused'] and v['ready']>=2 and n.get('dvdAngle')==angle,'actual new angle picture and presentation state')
                    rgb=await ev("(()=>{const v=videoPlane,c=document.createElement('canvas');c.width=c.height=16;const x=c.getContext('2d');x.drawImage(v,0,0,v.videoWidth*.04,v.videoHeight*.04,0,0,16,16);return[...x.getImageData(8,8,1,1).data].slice(0,3);})()")
                    n=await native();row['angles'].append(dict(expected=angle,nativeAngle=n.get('dvdAngle'),rgb=rgb))
                    if n.get('dvdAngle')!=angle or rgb[channel]<80 or max(v for i,v in enumerate(rgb) if i!=channel)>50:raise RuntimeError('Angle metadata/picture branch mismatch')
                    print(json.dumps(dict(actualPhoneAngle=angle,rgb=rgb,passed=True)),flush=True)
            if options.terminal:
                end=time.monotonic()+65
                while time.monotonic()<end:
                    terminal=await dvd_state()
                    if terminal.get('terminalEosAcks',0)>0:break
                    await asyncio.sleep(.25)
                else:raise RuntimeError('Actual terminal acknowledgement unavailable')
                await asyncio.sleep(1.2);after=await dvd_state()
                if after.get('segmentEos',0)-terminal.get('segmentEos',0)>2:raise RuntimeError('Terminal polling did not retire')
                row['terminal']=dict(acks=after.get('terminalEosAcks'),beforePolls=terminal.get('segmentEos'),afterPolls=after.get('segmentEos'),passed=True)
            if options.root_return:
                baseline=await sample();await asyncio.to_thread(guard,media_id)
                if not (await asyncio.to_thread(mcp,'ui.command',context=identity,command='DVD Menu')).get('accepted'):raise RuntimeError('Root command rejected')
                if name=='aladdin':
                    # Independent IFO inspection qualifies this rip's absence
                    # of menu VOBs. Its VMGM command table is routing, not art.
                    v,n=await wait(lambda v,n:not n.get('dvdMenu') and not v['paused'] and v['ready']>=2 and
                        ((v['epoch']==baseline['epoch'] and v['frames']>=baseline['frames']+15 and v['frameTime']>baseline['frameTime']) or
                         (v['epoch']!=baseline['epoch'] and v['frames']>=15 and v['frameTime']>.5)),
                        'command-only root returns moving ALADDIN feature')
                    row['rootReturnsFeature']=dict(video=v,nativeTitle=n.get('dvdTitle'),nativeChapter=n.get('dvdChapter'))
                else:
                    v,n=await wait(lambda v,n:n.get('dvdMenu'),'authored root domain')
                    # Wait on actual new-picture/highlight acknowledgement,
                    # not a fixed2s sleep or native VM domain alone. Read-only
                    # bounded polls never repeat Root or manufacture a frame.
                    deadline=time.monotonic()+20
                    while True:
                        geometry=await ev("(()=>{const s=__realDvdField,c=dvdSpuCanvas,p=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let n=0;for(let i=3;i<p.length;i+=4)if(p[i])n++;return{width:c.width,height:c.height,pixels:n,epoch:s.epoch,frames:s.frames};})()")
                        row['rootHighlightLast']=geometry
                        if (geometry['width']==720 and geometry['height']==height
                                and geometry['pixels']>=100 and geometry['epoch']!=baseline['epoch']
                                and geometry['frames']>=1):break
                        if time.monotonic()>=deadline:raise RuntimeError('Root SPU geometry/picture unavailable')
                        await asyncio.sleep(.15)
                    row['rootHighlight']=geometry
            if options.companion:
                row['stopDeferredForHookRestore']=True
                continue
            await asyncio.to_thread(guard,media_id)
            if not (await asyncio.to_thread(mcp,'media.control',context=identity,operation='stop')).get('ok'):raise RuntimeError('Stop rejected')
            await wait(lambda v,n:not n.get('fullyLoaded') and v['paused'],'Stop retires actual DVD',15)
            row['stopVerified']=True
        if player_borrowed:
            await save_player(original_player,True);player_borrowed=False;report['playerRestored']=True
        profiles=await ev("({client:localStorage.getItem('sagetvWebMiniClientSettings.v1')===__iphoneGate.settings,streaming:localStorage.getItem('sagetvWebStreaming.v1')===__iphoneGate.streaming})")
        if options.companion:
            unchanged=await ev("(()=>{const s=__iphoneGate,t=s.companionForm,N=SageMiniStreaming.normalize;if(!t)return false;const a=N(JSON.parse(t.streaming||'{}')),b=N(JSON.parse(localStorage.getItem('sagetvWebStreaming.v1')||'{}'));a.companionDvd=true;return JSON.stringify(a)===JSON.stringify(b)&&localStorage.getItem('sagetvWebCaptionAuthority.v1')===t.captions;})()")
            if not profiles['client'] or not unchanged:raise RuntimeError('Companion borrow changed unrelated profile state')
            report['temporaryBorrowPreserved']=True
            report['exactRestorationStillRequired']=True
        elif not all(profiles.values()):raise RuntimeError('Saved profile changed')
        report.update(passed=True,profilesUnchanged=profiles);return dict(passed=True,rows=len(report['rows']))
    finally:
        if options.handoff_mse and installed:report['startObserverRestored']=await ev("(()=>{const s=__realDvdField;if(SageMiniPlayback.prototype.start===s.startObserver)SageMiniPlayback.prototype.start=s.originalStart;return SageMiniPlayback.prototype.start===s.originalStart;})()")
        if remote_borrowed:report['remotePlaybackRestored']=await ev("(()=>{const s=__iphoneGate,b=s.remoteBorrow;if(!b||b.video!==videoPlane)throw Error('Remote owner changed');b.video.disableRemotePlayback=b.before;delete s.remoteBorrow;return true;})()")
        if options.pixels:report['pixelObserverCleanup']=await ev("(()=>{if(window.__dvdPixels){__dvdPixels.done=true;delete window.__dvdPixels;}return true;})()")
        if player_borrowed:
            await save_player(original_player,True);report['playerRestoredAfterFailure']=True
        if installed:report['observerCleanup']=await ev("(()=>{const s=window.__realDvdField;if(s){s.done=true;if(s.realFetch&&window.fetch===s.fetchObserver)window.fetch=s.realFetch;}delete window.__realDvdField;return!window.__realDvdField;})()")
        if owner_created:report['fieldOwnerCleanup']=await ev("(()=>{const s=__iphoneGate;if(localStorage.getItem('sagetvWebMiniClientSettings.v1')!==s.settings||localStorage.getItem('sagetvWebStreaming.v1')!==s.streaming)throw Error('Preserve changed owner');if(s.cleanup)s.cleanup();delete window.__iphoneGate;return true})()")
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,page_id=None,verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,screenshot=out/(stamp+'-real-dvd-phone.png'))
async def run():
    async def attached(rsd,data):await W.inspect(rsd,data,args)
    await W.probe(args,report,on_rsd=attached)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
try:asyncio.run(asyncio.wait_for(run(),300+options.soak_seconds))
except Exception as e:report.update(passed=False,errorType=type(e).__name__,error=str(e)[:250] if isinstance(e,RuntimeError) else 'Observation unavailable; no replay')
finally:
    W.evaluate=original
    with (out/(stamp+'-real-dvd-phone.json')).open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps(dict(passed=report['passed'],rows=len(report['rows']),error=report.get('error')))+'\n'+str(out/(stamp+'-real-dvd-phone.json')))
raise SystemExit(0 if report['passed'] else 1)
