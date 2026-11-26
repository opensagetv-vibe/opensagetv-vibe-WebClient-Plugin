#!/usr/bin/env python3
"""WEB105 actual native-iPhone preview/quality consumer, explicit test stimulus.

Not measured WAN or automatic adaptation. One exact generated fixture, original
profiles restored, production DOM consumer and real BLE button activation.
"""
import argparse,asyncio,importlib.util,json,logging,signal,sys,time
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlencode
from urllib.request import urlopen
ROOT=Path(__file__).resolve().parents[1];BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
sys.path.insert(0,str(BRIDGE/'tools/native_inspector'))
import wireless_inspect as W
from field_hid import InputOwner
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--abort',action='store_true')
p.add_argument('--skip-preview',action='store_true',help='Do not repeat the already-qualified shared-preview row')
a=p.parse_args()
identity='123c8282e1ee';fixture=20905;owned=None
out=ROOT/'artifacts/active/WEB-105';out.mkdir(parents=True,exist_ok=True)
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');path=out/(stamp+('-abort' if a.abort else '-recovery')+'-iphone-experience.json')
cancel_path=out/(stamp+'-cancel.request')
checkpoint_path=out/(stamp+'-profile-checkpoint.private.json')
cancel_requested=False;cleaning=False
report=dict(passed=False,physicalPhone=True,physicalFingerGesture=False,measuredWan=False,
    stimulus='Explicit synthetic recommendation; production consumer and actual presentation',rows=[],cleanup=[])
report['cancelFile']=cancel_path.name

def request_cancel(_number,_frame):
    global cancel_requested
    cancel_requested=True
def save():path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
def mcp(action,**v):return C.request(cfg,'/v1/control',dict(action=action,**v),mcp=True,timeout=30)
def guard():
    activity=C.activity(cfg)
    if activity['recordingCount'] or activity['connectedClientCount'] or mcp('ui.list')['contexts']!=[identity]:raise RuntimeError('Require exact phone/no unrelated activity')
    return mcp('ui.state',context=identity)
def mini(action,**v):
    values=dict(action=action,session=owned,**v)
    return C.request(cfg,'/SageTVWebPlayer/api/miniclient'+('?' +urlencode(values) if action in ('streamSettings','playbackState','status') else ''),
        None if action in ('streamSettings','playbackState','status') else values,timeout=60)
def counts():
    with urlopen('http://'+cfg['address']+':31910/v1/capabilities',timeout=4) as r:s=json.load(r)['mimDirect']
    return {k:s[k] for k in ('activeSessions','activePreviewLeases')}
original=W.evaluate
class Trigger:
    def read_text(self,**_):return '__PHONE_EXPERIENCE__'
async def evaluate(session,expression):
    global owned
    if expression!='__PHONE_EXPERIENCE__':return await original(session,expression)
    async def ev(code):
        if not cleaning and (cancel_requested or cancel_path.exists()):
            report['cancelledByOperator']=True
            raise RuntimeError('Operator cancelled; retire owned test and restore without input replay')
        # Classify local harness exceptions without exposing arbitrary remote
        # bodies. This is still one exact-page operation, never an input replay.
        wrapper="(()=>{try{return{fieldOk:true,value:eval("+json.dumps(code)+")}}catch(e){return{fieldOk:false,errorName:e.name,detail:['ReferenceError','TypeError','SyntaxError'].includes(e.name)?String(e.message).slice(0,160):'Local test guard refused'}}})()"
        value=await original(session,wrapper)
        if not value.get('fieldOk'):raise RuntimeError('Phone expression '+value.get('errorName','unknown')+': '+value.get('detail','unknown'))
        return value.get('value')
    async def sample():return await ev("(()=>{const s=__phoneExperience,v=videoPlane;return{time:v.currentTime,frames:s.frames,source:s.source,current:s.source===v.currentSrc,width:v.videoWidth,height:v.videoHeight,paused:v.paused,ready:v.readyState,error:v.error?.code||null,prompt:!autoplayBtn.hidden,captionLength:localCaptions.textContent.trim().length,prepared:s.prepared.length,trustedClicks:s.trustedClicks,native:!!v.currentSrc&&!v.currentSrc.startsWith('blob:')}})()")
    async def wait(predicate,label,seconds=45):
        deadline=time.monotonic()+seconds;last=None
        while time.monotonic()<deadline:
            last=await sample()
            if last['error']:raise RuntimeError('Actual native decode error: '+label)
            if predicate(last):return last
            await asyncio.sleep(.2)
        report['last']=last;raise RuntimeError('Timed out '+label+'; no replay')
    async def profile(restore=False):
        await ev("(()=>{const s=__phoneExperience,N=SageMiniStreaming.normalize,A=SageMiniCaptionAuthority.normalize;if("+str(restore).lower()+"&&(JSON.stringify(N(JSON.parse(localStorage.getItem(s.keys[1])||'{}')))!==JSON.stringify(s.borrowed)||JSON.stringify(A(JSON.parse(localStorage.getItem(s.keys[2])||'{}')))!==JSON.stringify(s.authority)))throw Error('Preserve changed profile');const v="+('s.originalStream' if restore else 's.borrowed')+",a="+('s.originalAuthority' if restore else 's.authority')+";for(const k of Object.keys(SageMiniStreaming.DEFAULTS)){const e=document.getElementById('stream_'+k);if(e){if(e.type==='checkbox')e.checked=!!v[k];else e.value=String(v[k])}}for(const k of Object.keys(SageMiniCaptionAuthority.DEFAULTS)){const e=document.getElementById(k==='mode'?'captionAuthorityMode':k);if(e)e.value=String(a[k])}if(saveStreaming.disabled)throw Error('Save busy');saveStreaming.click();return true})()")
        deadline=time.monotonic()+20
        while time.monotonic()<deadline:
            if await ev("(()=>{const s=__phoneExperience;return!saveStreaming.disabled&&JSON.stringify(SageMiniStreaming.normalize(JSON.parse(localStorage.getItem(s.keys[1])||'{}')))===JSON.stringify("+('s.originalStream' if restore else 's.borrowed')+")})()"):return
            await asyncio.sleep(.2)
        raise RuntimeError('Profile Save receipt unknown; no replay')
    async def press_quality(rate):
        report['phase']='quality-button-setup-'+str(rate);save()
        await asyncio.to_thread(guard)
        before=await sample()
        await ev("(()=>{const s=__phoneExperience;s.rate="+str(rate)+";if(!settingsPanel.hidden)closeSettings.click();if(remotePanel.hidden)remoteToggle.click();remoteSettings.click();document.querySelector('#settingsCategories [data-settings-page=transcoding]').click();return true})()")
        deadline=time.monotonic()+10
        report['phase']='quality-recommendation-ready-'+str(rate);save()
        while await ev('applyQualityRecommendation.disabled'):
            if time.monotonic()>deadline:raise RuntimeError('Production quality action unavailable')
            await asyncio.sleep(.2)
        report['phase']='quality-button-focus-'+str(rate);save()
        await ev("(()=>{const e=applyQualityRecommendation;if(!e.getClientRects().length||e.disabled)throw Error('Button hidden');e.scrollIntoView({block:'center'});e.focus();return document.activeElement===e})()")
        report['qualityIntentKbps']=rate;save()
        await owner.arm();await owner.send('key',key='enter');await owner.close()
        await ev('__phoneExperience.rate=null;true')
        current=await wait(lambda v:v['prepared']>before['prepared'] and v['trustedClicks']>before['trustedClicks'],'one production quality prepare and trusted click',65)
        new=await wait(lambda v:v['current'] and v['source']!=before['source'] and v['frames']>current['frames']+12 and not v['paused'] and v['captionLength']>0,'replacement new native pictures/captions',50)
        state=await asyncio.to_thread(mini,'playbackState')
        deadline=time.monotonic()+12
        if not a.abort:
            while state.get('qualityHandoff')!='presented':
                if time.monotonic()>deadline:report['handoff']=state;raise RuntimeError('Actual presentation acknowledgement absent')
                await asyncio.sleep(.2);state=await asyncio.to_thread(mini,'playbackState')
        producer=await ev('__phoneExperience.prepared.at(-1)?.session')
        if not producer or (not a.abort and state.get('producer')!=producer):raise RuntimeError('Candidate/presentation owner mismatch')
        status=await asyncio.to_thread(C.request,cfg,'/SageTVWebPlayer/api/hls?session='+producer)
        effective=(status.get('streamSettings') or {}).get('effective') or {}
        if effective.get('videoTargetKbps')!=rate or not all(status.get(k) for k in ('hardware','hardwareDecode','hardwareFilters')):raise RuntimeError('Actual target/full GPU chain differs')
        report['rows'].append(dict(gate='native-quality-'+str(rate),sample=new,actualPresentedAck=state.get('qualityHandoff')=='presented',handoff=state.get('qualityHandoff'),effective=effective));save()
        return new,state,producer
    owner=InputOwner('192.168.10.113',(BRIDGE/'build/native-inspector/token.txt').read_text().strip())
    installed=borrowed=watch_intent=False;configured=None;before_cc=None
    try:
        report['phase']='guarded-preflight';save()
        if (await asyncio.to_thread(guard)).get('fullyLoaded'):raise RuntimeError('Preserve loaded source')
        info=await asyncio.to_thread(mcp,'media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/VibeCaptionTest-1080i-CEA608-90s-2s.ts')
        if info.get('mediaFileId')!=fixture:raise RuntimeError('Exact generated fixture changed')
        if await asyncio.to_thread(counts)!={'activeSessions':0,'activePreviewLeases':0}:raise RuntimeError('Preserve existing provider owners')
        before_cc=(await asyncio.to_thread(mcp,'captions.get',context=identity))['state']
        await ev("(()=>{if(document.visibilityState!=='visible'||window.__phoneExperience||videoPlane.getAttribute('src')||videoPlane.readyState)throw Error('Require visible unloaded phone');const keys=['sagetvWebMiniClientSettings.v1','sagetvWebStreaming.v1','sagetvWebCaptionAuthority.v1'],s=window.__phoneExperience={keys,saved:keys.map(k=>localStorage.getItem(k)),done:false,frames:0,source:'',prepared:[],trustedClicks:0,rate:null,preview:null,nativeSession:null};s.originalStream=SageMiniStreaming.normalize(JSON.parse(s.saved[1]||'{}'));s.originalAuthority=SageMiniCaptionAuthority.normalize(JSON.parse(s.saved[2]||'{}'));s.borrowed=SageMiniStreaming.normalize({...s.originalStream,player:'native',videoMode:'transcode',encoder:'auto',videoKbps:1000,resolution:'480',deinterlace:'on',captionAuthority:'cc1',captions:'608',captionService:1});s.authority=SageMiniCaptionAuthority.normalize({...s.originalAuthority,mode:'cc1',cc1Type:'cea608',cc1Service:1});s.originalClient=SageMiniCore.normalizeSettings(JSON.parse(s.saved[0]||'{}'));function f(){const src=videoPlane.currentSrc;videoPlane.requestVideoFrameCallback(()=>{if(s.done)return;if(src&&src===videoPlane.currentSrc){s.source=src;s.frames++}f()})}f();return true})()");installed=True
        # Bounded observer only; byte lengths/header/status, never image payload.
        await ev("(()=>{const s=__phoneExperience;s.realFetch=window.fetch;s.fetch=function(input,options){const u=new URL(typeof input==='string'?input:input instanceof URL?input.href:input.url,location.href);if(u.pathname.endsWith('/api/miniclient')&&u.searchParams.get('action')==='events')s.nativeSession=u.searchParams.get('session');if(s.withhold&&u.searchParams.get('action')==='state'&&options?.body){const body=new URLSearchParams(options.body);if(body.get('expectedHlsSession')!==s.baseProducer){body.delete('presentedTimeMs');options={...options,body}}}const r=s.realFetch.call(this,input,options);if(u.searchParams.get('action')==='qualityPrepare')r.then(x=>x.clone().json()).then(j=>{if(!s.done)s.prepared.push(j)}).catch(()=>{});if(u.searchParams.get('action')==='sourcePreview')r.then(async x=>{const b=await x.clone().arrayBuffer();if(!s.done)s.preview={status:x.status,position:x.headers.get('X-Vibe-Preview-Position-Ms'),bytes:b.byteLength}}).catch(()=>{});return r};window.fetch=s.fetch;s.realObserve=SageMiniExperience.QualityAdvisor.prototype.observe;s.observe=function(v){return!s.done&&s.rate?this.recommendation={videoKbps:s.rate,resolution:'480',reason:'Explicit physical-test stimulus; not measured WAN'}:s.realObserve.call(this,v)};SageMiniExperience.QualityAdvisor.prototype.observe=s.observe;s.click=e=>{if(e.isTrusted)s.trustedClicks++};applyQualityRecommendation.addEventListener('click',s.click);return true})()")
        deadline=time.monotonic()+32
        while not (owned:=await ev('__phoneExperience.nativeSession')):
            if time.monotonic()>deadline:raise RuntimeError('Fresh production poll not observed')
            await asyncio.sleep(.2)
        report['phase']='profile-preparation';save()
        configured=(await asyncio.to_thread(mini,'streamSettings'))['configured']
        # Private ignored state, never a public support report. Persist BEFORE
        # borrowing so a page/process interruption cannot lose exact originals.
        checkpoint=await ev("(()=>{const s=__phoneExperience;return{keys:s.keys,saved:s.saved,originalStream:s.originalStream,originalAuthority:s.originalAuthority,originalClient:s.originalClient,borrowed:s.borrowed,authority:s.authority,borrowedClient:SageMiniCore.normalizeSettings({...s.originalClient,scrubPreviews:true,adaptiveQuality:false})}})()")
        checkpoint['configured']=configured
        checkpoint.update(schemaVersion=1,fixtureMediaId=fixture,clientIdentity=identity,beforeCc=before_cc)
        with checkpoint_path.open('x',encoding='utf-8') as f:json.dump(checkpoint,f)
        report['privateProfileCheckpoint']=checkpoint_path.name;save()
        borrowed=True;await profile()
        await ev("(()=>{const s=__phoneExperience;for(const[k,v]of Object.entries({scrubPreviews:true,adaptiveQuality:false})){const e=document.getElementById(k);e.checked=v;e.dispatchEvent(new Event('change',{bubbles:true}))}s.borrowedClient=SageMiniCore.normalizeSettings(JSON.parse(localStorage.getItem(s.keys[0])||'{}'));return true})()")
        report['fixtureResetIntent']=True;save()
        if not (await asyncio.to_thread(mcp,'media.clear_watched',media_id=fixture,confirm='true')).get('ok'):raise RuntimeError('Generated reset unknown')
        watch_intent=True;report['watchIntent']=True;save()
        if not (await asyncio.to_thread(mcp,'media.watch',context=identity,media_id=fixture,wait_ms=0)).get('accepted'):raise RuntimeError('One Watch rejected')
        deadline=time.monotonic()+65;activated=False
        while True:
            v=await sample()
            if v['error']:raise RuntimeError('Native startup decoder error')
            if v['prompt'] and not activated:
                activated=True;await ev('autoplayBtn.focus();true');await owner.arm();await owner.send('key',key='enter');await owner.close()
            if v['current'] and v['frames']>12 and not v['paused'] and v['captionLength']>0:break
            if time.monotonic()>deadline:report['last']=v;raise RuntimeError('No actual captioned native pictures')
            await asyncio.sleep(.2)
        baseline=await asyncio.to_thread(mini,'playbackState');report['rows'].append(dict(gate='native-startup-captioned',sample=v));save()
        if not a.abort and not a.skip_preview:
            deadline=time.monotonic()+15
            while not await ev("!seekRange.disabled&&Number(seekRange.max)>=45"):
                if time.monotonic()>deadline:raise RuntimeError('Browser timeline not ready for an explicit preview')
                await asyncio.sleep(.2)
            report['previewIntent']=await ev("({disabled:seekRange.disabled,max:seekRange.max,enabled:scrubPreviews.checked,savedEnabled:JSON.parse(localStorage.getItem('sagetvWebMiniClientSettings.v1')||'{}').scrubPreviews})");save()
            await ev("(()=>{if(remotePanel.hidden)remoteToggle.click();remoteHelp.click();seekRange.value='40';seekRange.dispatchEvent(new Event('input',{bubbles:true}));return true})()")
            deadline=time.monotonic()+15
            while True:
                result=await ev("(()=>{const s=__phoneExperience,e=timelinePreviewImage;return{preview:s.preview,visible:!timelinePreview.hidden,width:e.naturalWidth,height:e.naturalHeight,label:timelinePreviewLabel.textContent}})()")
                if result['preview'] and result['visible'] and result['width']==192:break
                if time.monotonic()>deadline:report['previewFailure']=result;raise RuntimeError('Actual shared image consumer unavailable')
                await asyncio.sleep(.2)
            now=await asyncio.to_thread(mini,'playbackState');provider=await asyncio.to_thread(counts)
            if result['preview']['status']!=200 or result['preview']['position']!='40000' or not 4<=result['preview']['bytes']<=32768 or result['height']!=108 or 'Source preview at' not in result['label'] or any(baseline[k]!=now[k] for k in ('producer','source','requestedPositionMs')) or provider!={'activeSessions':0,'activePreviewLeases':1}:raise RuntimeError('Shared preview changed playback or invalid output')
            report['rows'].append(dict(gate='shared-preview-native-no-seek',result=result,provider=provider));save()
            report['phase']='preview-dismiss';save()
            await ev('timelineCancel.click();closeRemoteTools.click();hideRemote.click();true')
        report['previewSkippedPreviouslyQualified']=a.skip_preview
        report['phase']='quality-base-owner';save()
        await ev('__phoneExperience.baseProducer='+json.dumps(baseline['producer'])+';__phoneExperience.withhold='+str(a.abort).lower()+';true')
        changed,state,candidate=await press_quality(700)
        if a.abort:
            if state.get('qualityHandoff')!='waiting-for-presentation':raise RuntimeError('Candidate did not retain explicit awaiting-ACK state')
            report['abortIntent']=True;save()
            if not (await asyncio.to_thread(mini,'qualityAbort',expectedHlsSession=candidate)).get('ok'):raise RuntimeError('Abort receipt unknown')
            back=await wait(lambda v:v['current'] and v['source']!=changed['source'] and v['frames']>changed['frames']+12 and not v['paused'] and v['captionLength']>0,'original native producer restoration',45)
            restored=await asyncio.to_thread(mini,'playbackState')
            if restored.get('producer')!=baseline['producer'] or restored.get('qualityHandoff')!='client-aborted':raise RuntimeError('Abort did not restore original owner')
            report['rows'].append(dict(gate='explicit-abort-original-native-pictures',sample=back));save()
        else:
            report['pauseIntent']=True;save()
            if not (await asyncio.to_thread(mcp,'media.control',context=identity,operation='pause')).get('accepted'):raise RuntimeError('Pause receipt unknown')
            paused=await wait(lambda v:v['paused'],'Pause');began=time.monotonic()
            while time.monotonic()-began<61:
                await asyncio.sleep(5);current=await sample()
                if abs(current['time']-paused['time'])>.1:raise RuntimeError('Paused media advanced')
            report['actualCooldownWaitSeconds']=round(time.monotonic()-began,3);save()
            if not (await asyncio.to_thread(mcp,'media.control',context=identity,operation='play')).get('accepted'):raise RuntimeError('Resume receipt unknown')
            await wait(lambda v:not v['paused'] and v['frames']>paused['frames']+12,'Resume')
            await press_quality(900)
        if await ev("(()=>{const s=__phoneExperience;return JSON.stringify(SageMiniStreaming.normalize(JSON.parse(localStorage.getItem(s.keys[1])||'{}')))===JSON.stringify(s.borrowed)})()") is not True:raise RuntimeError('Quality changed saved bitrate ceiling')
        report['passed']=True
    finally:
        global cleaning
        cleaning=True
        if installed and not report['passed']:
            try:report['failureSample']=await sample();report['failurePlayback']=await asyncio.to_thread(mini,'playbackState');save()
            except Exception:report['failureObservationUnknown']=True
        if watch_intent:
            try:
                n=await asyncio.to_thread(guard)
                if n.get('fullyLoaded') and (n.get('media') or {}).get('mediaFileId')!=fixture:raise RuntimeError('Preserve foreign source')
                if n.get('fullyLoaded') and not (await asyncio.to_thread(mcp,'media.control',context=identity,operation='stop')).get('accepted'):raise RuntimeError('Stop receipt unknown')
                if before_cc is not None and not (await asyncio.to_thread(mcp,'captions.set',context=identity,state=before_cc)).get('ok'):raise RuntimeError('Caption restore unknown')
            except Exception:report['cleanup'].append('Exact Stop/caption restore unknown; no replay')
        if borrowed:
            try:
                await profile(True)
                restored=await ev("(()=>{const s=__phoneExperience;if(JSON.stringify(SageMiniCore.normalizeSettings(JSON.parse(localStorage.getItem(s.keys[0])||'{}')))!==JSON.stringify(s.borrowedClient))throw Error('Preserve changed client settings');for(const k of ['scrubPreviews','adaptiveQuality']){const e=document.getElementById(k);e.checked=s.originalClient[k];e.dispatchEvent(new Event('change',{bubbles:true}))}for(let i=0;i<s.keys.length;i++){if(s.saved[i]===null)localStorage.removeItem(s.keys[i]);else localStorage.setItem(s.keys[i],s.saved[i])}return s.keys.every((k,i)=>localStorage.getItem(k)===s.saved[i])})()")
                report['profilesRestored']=restored
                if not restored or (await asyncio.to_thread(mini,'streamSettings'))['configured']!=configured:raise RuntimeError('Configured defaults restoration mismatch')
                if await asyncio.to_thread(counts)!={'activeSessions':0,'activePreviewLeases':0}:raise RuntimeError('Preview lease not retired')
            except Exception:report['cleanup'].append('Profile/provider restoration unknown; preserve checkpoint')
        if installed and not report['cleanup']:
            try:report['observerRestored']=await ev("(()=>{const s=__phoneExperience;s.done=true;s.rate=null;if(window.fetch===s.fetch)window.fetch=s.realFetch;if(SageMiniExperience.QualityAdvisor.prototype.observe===s.observe)SageMiniExperience.QualityAdvisor.prototype.observe=s.realObserve;applyQualityRecommendation.removeEventListener('click',s.click);for(let i=0;i<4&&!settingsPanel.hidden;i++)closeSettings.click();if(!remotePanel.hidden)hideRemote.click();delete window.__phoneExperience;return true})()")
            except Exception:report['cleanup'].append('Observer restoration unknown')
        await owner.close();report['passed']=report['passed'] and not report['cleanup'];save()
    return dict(passed=report['passed'],rows=len(report['rows']))
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,page_id=None,verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,screenshot=None)
async def run():
    async def attached(rsd,data):await W.inspect(rsd,data,args)
    await W.probe(args,report,on_rsd=attached)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
prior_sigint=signal.signal(signal.SIGINT,request_cancel)
try:asyncio.run(asyncio.wait_for(run(),420))
except Exception as e:report.update(passed=False,errorType=type(e).__name__,error=str(e)[:250] if isinstance(e,RuntimeError) else 'Bounded observation unavailable; no replay')
finally:signal.signal(signal.SIGINT,prior_sigint);W.evaluate=original;save()
print(json.dumps(dict(passed=report['passed'],rows=len(report['rows']),report=str(path),error=report.get('error'),cleanup=report['cleanup'])));raise SystemExit(0 if report['passed'] else 1)
