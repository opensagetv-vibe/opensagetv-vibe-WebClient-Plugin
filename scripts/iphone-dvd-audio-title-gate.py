#!/usr/bin/env python3
"""Owned authored DVD: actual iPhone audio/title/Stop/replay, stock APIs only.

Native navigation is explicitly public-MCP test setup, not BLE-key proof or a
production MCP dependency. HDMI USB audio proves selected fixture tones, not
acoustic/lip sync. No saved preferences, bookmarks, Core edits or input replay.
"""
import argparse, asyncio, hashlib, importlib.util, json, logging, subprocess, sys, time, tomllib
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]; BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
sys.path.insert(0,str(BRIDGE/'tools/native_inspector'))
import wireless_inspect as W
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
identity='123c8282e1ee';fixture=20819
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--capture-current-tone',choices=('english','spanish'),help='Read current owned feature audio only; no playback controls')
options=parser.parse_args()
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
out=ROOT/'artifacts/active/WEB-014';out.mkdir(parents=True,exist_ok=True)
report={'utc':datetime.now(timezone.utc).isoformat(),'passed':False,'physicalPhone':True,
        'navigation':'Existing public stock MCP test setup; not hardware key evidence',
        'physicalFingerGesture':False,'inputReplayed':False,'rows':[]}

def mcp(action,**values):
    return C.request(cfg,'/v1/control',dict(action=action,**values),mcp=True,timeout=8)
def guard(loaded=True):
    a=C.activity(cfg)
    if a.get('recordingCount')!=0 or a.get('connectedClientCount')!=0 or mcp('ui.list').get('contexts')!=[identity]:
        raise RuntimeError('Require exact phone/no recordings/other users')
    n=mcp('ui.state',context=identity)
    if loaded and (not n.get('dvd') or (n.get('media') or {}).get('mediaFileId')!=fixture):
        raise RuntimeError('Authored DVD owner changed')
    return n
def command(name):
    guard()
    if not mcp('ui.command',context=identity,command=name).get('accepted'):
        raise RuntimeError('Native setup not accepted; no replay')
def capture_tone(label,expected):
    # Exact opt-in HDMI audio device, never the webcam/room microphone.
    capture=tomllib.loads((BRIDGE/'config/toolbox.local.toml').read_text(encoding='utf-8'))['capture']
    ffmpeg=capture['ffmpeg'];video=capture.get('video_device','USB Video')
    target=out/(stamp+'-'+label+'.mkv');log=target.with_suffix('.ffmpeg.log')
    if target.exists() or log.exists():raise RuntimeError('Capture collision')
    args=[ffmpeg,'-hide_banner','-nostdin','-n','-loglevel','error','-f','dshow','-rtbufsize','256M',
          '-vcodec','mjpeg','-video_size','1920x1080','-framerate','30','-i',
          'video='+video+':audio=Digital Audio Interface (USB Digital Audio)',
          '-t','6','-c:v','libx264','-preset','ultrafast','-pix_fmt','yuv420p','-c:a','pcm_s16le',str(target)]
    r=subprocess.run(args,capture_output=True,timeout=35)
    with log.open('xb') as f:f.write(r.stderr[-65536:])
    if r.returncode or not target.is_file():raise RuntimeError('HDMI capture failed')
    # Existing host analysis environment owns numpy; no phone-venv dependency
    # installation or changes to the pinned inspector environment.
    analyzed=subprocess.run(['py','-3.12',str(ROOT/'scripts/analyze-dvd-hdmi-audio.py'),
        '--input',str(target),'--expected',str(expected)],capture_output=True,text=True,timeout=30,check=True)
    result=json.loads(analyzed.stdout)
    if not result['passed']:
        report['audioFailure']=result;raise RuntimeError('Actual HDMI selected tone does not match')
    return result

if options.capture_current_tone:
    if guard().get('dvdMenu'):raise RuntimeError('Require current owned feature, not a menu')
    tone=capture_tone('current-'+options.capture_current_tone,1000 if options.capture_current_tone=='english' else 440)
    target=out/(stamp+'-current-tone.json')
    with target.open('x',encoding='utf-8') as f:json.dump(dict(passed=True,physicalPhone=True,playbackControlsSent=False,capture=tone),f,indent=2);f.write('\n')
    print(json.dumps(tone)+'\n'+str(target));raise SystemExit()

original=W.evaluate
class Trigger:
    def read_text(self,**_):return '__DVD_AUDIO_TITLE_FIELD__'
async def evaluate(session,expression):
    if expression!='__DVD_AUDIO_TITLE_FIELD__':return await original(session,expression)
    async def ev(s):return await original(session,s)
    async def native(name):await asyncio.to_thread(command,name);await asyncio.sleep(.3)
    async def sample():
        await ev("(()=>{const s=window.__dvdAudioField;s.pending=true;s.nativeError=false;window.__iphoneGate.api('status').then(j=>s.dvd=j.connection?.dvd).catch(()=>s.nativeError=true).finally(()=>s.pending=false);return true;})()")
        for _ in range(40):
            if not await ev('window.__dvdAudioField.pending'):break
            await asyncio.sleep(.05)
        else:raise RuntimeError('Native observation timeout')
        return await ev("(()=>{const s=window.__dvdAudioField,v=videoPlane,c=document.getElementById('dvdSpuCanvas'),p=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let pixels=0;for(let i=3;i<p.length;i+=4)if(p[i])pixels++;return{time:v.currentTime,paused:v.paused,ready:v.readyState,width:v.videoWidth,error:v.error?.code||null,blocked:!document.getElementById('autoplayBtn').hidden,sourceChanged:v.currentSrc!==s.before,hasAssignedSource:!!v.getAttribute('src'),presented:s.presented,lastPresented:s.lastPresented,pixels,nativeError:s.nativeError,dvd:s.dvd,message:document.getElementById('osdMessage').textContent};})()")
    async def checkpoint():
        await ev("(()=>{const s=window.__dvdAudioField;s.before=videoPlane.currentSrc;s.presented=0;s.lastPresented=null;return true;})()")
    async def wait(predicate,label,seconds=35):
        deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:
            r=await sample();n=await asyncio.to_thread(guard)
            if r['nativeError']:raise RuntimeError('Current native observation failed')
            if r['error']:raise RuntimeError('Browser media error')
            if r['blocked']:raise RuntimeError('Real Safari Play required; no synthetic activation')
            if predicate(r,n):return r,n
            await asyncio.sleep(.15)
        report['last']=r;report['lastNative']={k:n.get(k) for k in ('dvdMenu','dvdTitle','dvdChapter','mediaTimeMs')}
        raise RuntimeError('Timed out: '+label)
    async def moving(title,replace=True):
        return await wait(lambda r,n:not n.get('dvdMenu') and n.get('dvdTitle')==title and
            r['ready']>=2 and not r['paused'] and r['time']>.5 and r['presented']>=8 and
            (not replace or r['sourceChanged']), 'new moving title '+str(title))
    async def menu_transition(command,label):
        # Accepted is queued; old menu pixels alone do not acknowledge a new
        # authored menu. Wait for a replacement decoder/picture before sending
        # the next ordered navigation intent. Never replay on timeout.
        await checkpoint();await native(command)
        return await wait(lambda r,n:n.get('dvdMenu') and r['sourceChanged']
            and r['presented']>=1 and r['pixels']>100,'new authored menu '+label)
    async def authored_audio(spanish,reset=False):
        # The authored language menu deliberately applies its VM register and
        # jumps to the feature. This gate qualifies physical stream identity
        # across that genuine FLUSH, not unsupported in-place audio switching.
        await menu_transition('DVD Menu','root for language')
        await native('Down');await menu_transition('Select','languages')
        if reset:
            # Only authored fixture VM registers: reset English/subtitles-Off
            # through its own menu, never user settings or watched history.
            for _ in range(3):await native('Down')
            await menu_transition('Select','reset English returns languages')
        await menu_transition('Select','audio tracks')
        if spanish:await native('Down')
        await menu_transition('Select','languages after audio selection')
        await native('Down');await native('Down')
        await checkpoint();await native('Select')
        return await moving(1)
    installed=False
    try:
        guard()
        await ev("""(()=>{if(!window.__iphoneGate?.api||window.__dvdAudioField||document.visibilityState!=='visible')throw Error('Owner unavailable');const s=window.__dvdAudioField={before:videoPlane.currentSrc,presented:0,lastPresented:null,done:false};const frame=(n,m)=>{if(s.done)return;if(videoPlane.currentSrc!==s.before){s.presented++;s.lastPresented=m.mediaTime;}videoPlane.requestVideoFrameCallback(frame);};videoPlane.requestVideoFrameCallback(frame);return true;})()""");installed=True
        v,n=await authored_audio(False,reset=True)
        report['rows'].append({'gate':'main-title-moving','title':n.get('dvdTitle'),'chapter':n.get('dvdChapter'),'sample':v})
        report['rows'].append({'gate':'English-physical-audio-id','capture':await asyncio.to_thread(capture_tone,'english',1000)})
        v,n=await authored_audio(True)
        report['rows'].append({'gate':'Spanish-physical-audio-id','sample':v,'capture':await asyncio.to_thread(capture_tone,'spanish',440)})
        await native('DVD Subtitle Toggle')
        # The native VM may send type1 then type0 again before a poll. Last
        # command type is NOT an acknowledgement; require actual new SPU pixels.
        v,n=await wait(lambda r,n:r['pixels']>100,'actual subtitle after toggle')
        if (v.get('dvd') or {}).get('audioSelector')!='AC3 wire=0xbd81 ffmpegId=0x81':
            raise RuntimeError('Subtitle update discarded physical Spanish audio selector')
        report['rows'].append({'gate':'independent-audio-retained-after-SPU','sample':v})
        await checkpoint();await native('DVD Next Chapter');v,n=await moving(1)
        if n.get('dvdChapter',0)<2:raise RuntimeError('Chapter did not advance')
        report['rows'].append({'gate':'Spanish-after-SPU-and-chapter-restart','chapter':n.get('dvdChapter'),
            'sample':v,'capture':await asyncio.to_thread(capture_tone,'spanish-after-spu',440)})
        v,n=await authored_audio(False,reset=True)
        report['rows'].append({'gate':'English-audio-restored','sample':v,'capture':await asyncio.to_thread(capture_tone,'english-restored',1000)})
        await menu_transition('DVD Menu','root before special title')
        for _ in range(3):await native('Down')
        await menu_transition('Select','special features')
        await checkpoint();await native('Select');v,n=await moving(2)
        report['rows'].append({'gate':'second-authored-title-moving','title':n.get('dvdTitle'),'sample':v})
        guard();stopped=mcp('media.control',context=identity,operation='stop')
        if not stopped.get('ok'):raise RuntimeError('Stop acceptance unavailable; no replay')
        deadline=time.monotonic()+15
        while time.monotonic()<deadline:
            v=await sample();n=await asyncio.to_thread(guard,False)
            if not n.get('fullyLoaded') and v['paused'] and not (v.get('dvd') or {}).get('active'):break
            await asyncio.sleep(.2)
        else:raise RuntimeError('Stop did not retire native/browser DVD')
        report['rows'].append({'gate':'Stop-retires-DVD','sample':v})
        if not mcp('media.watch',context=identity,media_id=fixture,wait_ms=0).get('accepted'):raise RuntimeError('Replay not accepted')
        for _ in range(100):
            n=await asyncio.to_thread(guard,False)
            if n.get('dvd'):break
            await asyncio.sleep(.2)
        else:raise RuntimeError('Replay load unavailable')
        await native('DVD Menu');await wait(lambda r,n:n.get('dvdMenu') and r['pixels']>100,'replayed root')
        await checkpoint();await native('Select');v,n=await moving(1)
        report['rows'].append({'gate':'Stop-replay-main-title-new-picture','sample':v})
        profiles=await ev("(()=>({client:localStorage.getItem('sagetvWebMiniClientSettings.v1')===window.__iphoneGate.settings,streaming:localStorage.getItem('sagetvWebStreaming.v1')===window.__iphoneGate.streaming}))()")
        if not all(profiles.values()):raise RuntimeError('Saved profiles changed')
        report['profilesUnchanged']=profiles;report['passed']=True;return{'passed':True,'rows':len(report['rows'])}
    finally:
        if installed:report['observerCleanup']=await ev("(()=>{if(window.__dvdAudioField)window.__dvdAudioField.done=true;delete window.__dvdAudioField;return!window.__dvdAudioField;})()")
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,page_id=None,
    verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,screenshot=None)
async def run():
    async def attached(rsd,data):await W.inspect(rsd,data,args)
    await W.probe(args,report,on_rsd=attached)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
try:asyncio.run(asyncio.wait_for(run(),280))
except Exception as e:report.update(passed=False,errorType=type(e).__name__,error=str(e)[:250] if isinstance(e,RuntimeError) else 'Observation unavailable; no replay')
finally:
    W.evaluate=original
    with (out/(stamp+'-iphone-dvd-audio-title.json')).open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({'passed':report['passed'],'rows':len(report['rows']),'error':report.get('error')})+'\n'+str(out/(stamp+'-iphone-dvd-audio-title.json')))
raise SystemExit(0 if report['passed'] else 1)
