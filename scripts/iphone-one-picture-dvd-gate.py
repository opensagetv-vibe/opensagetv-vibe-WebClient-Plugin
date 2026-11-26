#!/usr/bin/env python3
"""Actual one-picture authored menu/held frame/Select/feature/root, stock only.

One exact generated Watch as test setup; real ESP32 BLE Select. No guessed
clock/frame writes, input replay, source edits, settings changes or Core code.
"""
import argparse,asyncio,base64,hashlib,importlib.util,json,logging,re,sys,time
from urllib.request import Request,urlopen
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
sys.path.insert(0,str(BRIDGE/'tools/native_inspector'))
import wireless_inspect as W
from field_hid import InputOwner
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
identity='123c8282e1ee';media_id=78957
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--hold-seconds',type=int,default=10)
parser.add_argument('--task',choices=('WP08-006','WEB-092','WEB-093','WEB-023'),default='WP08-006',help='Owning active task for this affected physical rerun')
options=parser.parse_args()
if not 10<=options.hold_seconds<=120:parser.error('Hold must remain10..120seconds')
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
out=ROOT/'artifacts/active'/options.task/(stamp+'-iphone-one-picture.json');out.parent.mkdir(parents=True,exist_ok=True)
report=dict(passed=False,physicalPhone=True,physicalFingerGesture=False,inputReplayed=False,
            menuVideoPictures=1,fixtureGenerated=True,menuHoldSeconds=options.hold_seconds,samples=[],rows=[])
def mcp(action,**values):return C.request(cfg,'/v1/control',dict(action=action,**values),mcp=True,timeout=15)
def guard(loaded=False):
    a=C.activity(cfg)
    if a.get('recordingCount')!=0 or a.get('connectedClientCount')!=0 or mcp('ui.list').get('contexts')!=[identity]:raise RuntimeError('Exact idle test owner required')
    n=mcp('ui.state',context=identity)
    if loaded and (not n.get('dvd') or n.get('media',{}).get('mediaFileId')!=media_id):raise RuntimeError('Exact one-picture source changed')
    return n
original=W.evaluate
class Trigger:
    def read_text(self,**_):return '__ONE_PICTURE_DVD__'
async def evaluate(session,expression):
    if expression!='__ONE_PICTURE_DVD__':return await original(session,expression)
    async def ev(script):return await original(session,script)
    owner=InputOwner('192.168.10.113',(BRIDGE/'build/native-inspector/token.txt').read_text(encoding='ascii').strip())
    installed=False
    async def sample():
        v=await ev("""(()=>{const s=__onePictureField,v=videoPlane,c=dvdSpuCanvas,d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let pixels=0;for(let i=3;i<d.length;i+=4)if(d[i])pixels++;return{time:v.currentTime,ready:v.readyState,paused:v.paused,width:v.videoWidth,frames:s.frames,frameSourceCurrent:s.active===v.currentSrc,frameTime:s.frameTime,sourceChanged:v.currentSrc!==s.before,ended:v.ended,still:!dvdStillFrame.hidden,pixels,blocked:!autoplayBtn.hidden,error:v.error?.code||null,message:osdMessage.textContent}})()""")
        detail=await ev("(()=>{const v=videoPlane,p=window.__observedPlayback?.instance;return{duration:Number.isFinite(v.duration)?v.duration:null,network:v.networkState,buffered:Array.from({length:v.buffered.length},(_,i)=>[v.buffered.start(i),v.buffered.end(i)]),attached:p?.attached,pending:p?.playPending,rebuffering:p?.rebuffering,intentPaused:p?.intentPaused,firstFrameMs:p?.firstFrameMs,selectedPlayer:p?.streamSettings?.requested?.player,engine:p?.snapshot().browserEngine,stillFallback:p?.nativeDvdStillFallbackResult,remotePlaybackDisabled:v.disableRemotePlayback}})()")
        v.update(detail)
        v.update(await ev("(()=>{const p=window.__observedPlayback?.instance;return{featureFallback:p?.nativeDvdFeatureFallbackResult,featureSameProducer:__onePictureField.featureProducer?p?.id===__onePictureField.featureProducer:null,producerRecoveries:p?.snapshot().recoveries,remoteState:videoPlane.remote?.state||'unavailable',wireless:videoPlane.webkitCurrentPlaybackTargetIsWireless===true}})()"))
        v['server']=await ev("(()=>{const s=window.__observedPlayback?.instance?.status;return s?Object.fromEntries(['running','endList','activeRecording','hlsSeconds','segments','dvdConverterEnded','exitCode','dvdGeneration'].map(k=>[k,s[k]])):null})()")
        n=await asyncio.to_thread(guard,True);v.update(nativeMenu=n.get('dvdMenu'),nativeMs=n.get('rawMediaTimeMs'))
        report['samples'].append(v)
        if v['error'] or v['blocked']:raise RuntimeError('One-picture playback/activation failed; no replay')
        return v
    async def wait(predicate,label,seconds=45):
        until=time.monotonic()+seconds
        while time.monotonic()<until:
            v=await sample()
            if v['frameSourceCurrent'] and predicate(v):return v
            await asyncio.sleep(.2)
        raise RuntimeError('Timed out: '+label)
    try:
        if (await asyncio.to_thread(guard)).get('fullyLoaded'):raise RuntimeError('Preserve existing playback')
        if not (await asyncio.to_thread(mcp,'ui.command',context=identity,command='Home')).get('accepted'):raise RuntimeError('Owned public Home setup rejected')
        await asyncio.sleep(.7)
        found=await asyncio.to_thread(mcp,'media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/WP08-OnePicture/VIDEO_TS')
        if found.get('mediaFileId')!=media_id:raise RuntimeError('Generated fixture identity mismatch')
        report['pagePreflight']=await ev("({owner:!!window.__iphoneGate?.api,observer:!!window.__onePictureField,currentSource:!!videoPlane.currentSrc,assignedSource:!!videoPlane.getAttribute('src'),paused:videoPlane.paused,ready:videoPlane.readyState,visible:document.visibilityState==='visible',remotePlaybackDisabled:videoPlane.disableRemotePlayback})")
        await ev("(()=>{if(!window.__iphoneGate?.api||window.__onePictureField||!videoPlane.paused||videoPlane.readyState!==0||document.visibilityState!=='visible')throw Error('Require idle exact page');return true})()")
        await ev((ROOT/'tests/fixtures/one-picture-frame-observer.js').read_text(encoding='utf-8')+"\nwindow.__onePictureField=observeOnePictureFrames(videoPlane);true;");installed=True
        await ev((ROOT/'tests/iphone-playback-observe-prepare.js').read_text(encoding='utf-8'))
        report['watchSubmitted']=True
        if not (await asyncio.to_thread(mcp,'media.watch',context=identity,media_id=media_id,wait_ms=0)).get('accepted'):raise RuntimeError('One Watch not accepted')
        first=await wait(lambda v:v['nativeMenu'] and v['width']>0 and v['frames']>=1 and v['pixels']>100,'one actual menu picture/highlight')
        report['rows'].append(dict(gate='actual-one-picture-menu',sample=first))
        # Public content completion is separate from decoded-media readiness.
        # Do not send a generic TV toggle or Select against a stale preview.
        until=time.monotonic()+15
        while True:
            await ev("(()=>{const s=__onePictureField;s.viewPending=true;__iphoneGate.api('contentState',{mediaId:78957}).then(r=>s.view={ready:r.ready,layout:r.layout}).catch(()=>s.view={error:true}).finally(()=>s.viewPending=false);return true})()")
            while await ev('__onePictureField.viewPending'):await asyncio.sleep(.05)
            view=await ev('__onePictureField.view')
            if (view.get('ready') and view.get('layout') in ('preview','fullscreen')) or time.monotonic()>=until:break
            await asyncio.sleep(.15)
        report['viewBefore']=view
        if not view.get('ready') or view.get('layout') not in ('preview','fullscreen'):raise RuntimeError('Unknown DVD layout; no guessed toggle')
        if view['layout']=='preview':
            await ev("(()=>{const s=__onePictureField;s.viewPending=true;__iphoneGate.api('showContent',{mediaId:78957}).then(r=>s.shown=r.ok).catch(()=>s.shown=false).finally(()=>s.viewPending=false);return true})()")
            while await ev('__onePictureField.viewPending'):await asyncio.sleep(.05)
            if not await ev('__onePictureField.shown'):raise RuntimeError('One qualified fullscreen request refused')
        await asyncio.sleep(options.hold_seconds)
        held=await sample()
        if not held['nativeMenu'] or held['pixels']<100 or held['message'] or not (held['still'] or held['width']>0):raise RuntimeError('One-picture menu not retained after bounded hold')
        report['rows'].append(dict(gate='held10s-without-audio' if options.hold_seconds==10 else 'held'+str(options.hold_seconds)+'s-without-audio',sample=held))
        await ev("(()=>{__onePictureField.before=videoPlane.currentSrc;__onePictureField.frames=0;stage.focus();return true})()")
        await owner.arm();await owner.send('key',key='enter');await owner.close()
        feature=await wait(lambda v:not v['nativeMenu'] and v['sourceChanged'] and v['frames']>=15 and v['time']>.5 and not v['paused'],'new moving five-second feature')
        report['rows'].append(dict(gate='real-BLE-select-new-feature',sample=feature))
        await ev("(()=>{__onePictureField.featureProducer=window.__observedPlayback?.instance?.id;__onePictureField.before=videoPlane.currentSrc;__onePictureField.frames=0;return true})()")
        root=await wait(lambda v:v['nativeMenu'] and v['sourceChanged'] and v['frames']>=1 and v['width']>0 and v['ready']>=2 and v['pixels']>100 and not v['message'],'natural return to one-picture root')
        report['rows'].append(dict(gate='natural-root-new-picture',sample=root))
        if not (await asyncio.to_thread(mcp,'media.control',context=identity,operation='stop')).get('ok'):raise RuntimeError('Stop not accepted')
        until=time.monotonic()+15
        while time.monotonic()<until:
            n=await asyncio.to_thread(guard)
            if n.get('fullyLoaded') is False:break
            await asyncio.sleep(.2)
        else:raise RuntimeError('Stop did not retire one-picture source')
        until=time.monotonic()+15
        while True:
            stopped=await ev("(()=>{const v=videoPlane,p=window.__observedPlayback?.instance;return{stopped:p?.stopped,producerRetired:!p?.id,paused:v.paused,ready:v.readyState,assignedSource:!!v.getAttribute('src'),remotePlaybackDisabled:v.disableRemotePlayback}})()")
            if stopped.get('stopped') and stopped['producerRetired'] and stopped['paused'] and stopped['ready']==0 and not stopped['assignedSource']:break
            if time.monotonic()>=until:raise RuntimeError('Browser decoder teardown did not complete')
            await asyncio.sleep(.1)
        report['stopState']=stopped
        if stopped['remotePlaybackDisabled']!=report['pagePreflight']['remotePlaybackDisabled']:raise RuntimeError('Remote-playback preference was not restored')
        profiles=await ev("({client:localStorage.getItem('sagetvWebMiniClientSettings.v1')===__iphoneGate.settings,streaming:localStorage.getItem('sagetvWebStreaming.v1')===__iphoneGate.streaming})")
        if not all(profiles.values()):raise RuntimeError('Saved profiles changed')
        report.update(passed=True,profilesUnchanged=profiles);return dict(passed=True,rows=len(report['rows']))
    finally:
        report['inputCommands']=owner.sequence-1;await owner.close()
        # Preserve only this generated one-picture source's encoded output
        # when native Safari fails. No source replacement, input or retry.
        if not report.get('passed') and installed:
            try:
                await asyncio.to_thread(guard,True)
                playlist=await ev("(()=>{const p=window.__observedPlayback?.instance;return p?.id?'hls/'+p.id+'/stream.m3u8':''})()")
                if not re.fullmatch(r'hls/[0-9a-f]{32}/stream\.m3u8',playlist):raise RuntimeError('No exact owned HLS')
                def fetch(path,limit):
                    auth=base64.b64encode((cfg['web_username']+':'+cfg['web_password']).encode()).decode()
                    with urlopen(Request(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/'+path,headers={'Authorization':'Basic '+auth}),timeout=10) as response:
                        data=response.read(limit+1)
                        if len(data)>limit:raise RuntimeError('Diagnostic body exceeds bound')
                        return data
                manifest=await asyncio.to_thread(fetch,playlist,65536)
                report['failureManifest']=manifest.decode('utf-8')
                entries=[x for x in manifest.decode('utf-8').splitlines() if x and not x.startswith('#')]
                if len(entries)!=1 or not re.fullmatch(r'seg_\d{5}\.ts',entries[0]):raise RuntimeError('Only exact one-segment fixture export is allowed')
                data=await asyncio.to_thread(fetch,playlist.rsplit('/',1)[0]+'/'+entries[0],1024*1024)
                segment=out.with_name(out.stem+'-segment.ts')
                with segment.open('xb') as file:file.write(data)
                report['onePictureOutput']={'manifest':manifest.decode('utf-8'),'segment':segment.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
            except Exception as error:report['onePictureExportError']=type(error).__name__
        if installed:report['observerRemoved']=await ev("(()=>{if(window.__onePictureField)__onePictureField.done=true;delete window.__onePictureField;return!window.__onePictureField})()")
        if installed:await ev("(()=>{window.__observedPlayback?.cleanup();return!window.__observedPlayback})()")
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,page_id=None,verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,screenshot=out.with_suffix('.png'))
async def run():
    async def attached(rsd,data):await W.inspect(rsd,data,args)
    await W.probe(args,report,on_rsd=attached)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
try:asyncio.run(asyncio.wait_for(run(),max(150,options.hold_seconds+90)))
except Exception as error:report.update(passed=False,errorType=type(error).__name__,error=str(error)[:200] if isinstance(error,RuntimeError) else 'Observation unavailable; no replay')
finally:
    W.evaluate=original
    with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(passed=report['passed'],rows=len(report['rows']),error=report.get('error'),report=str(out))))
raise SystemExit(0 if report['passed'] else 1)
