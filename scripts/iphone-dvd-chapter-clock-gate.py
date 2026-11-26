#!/usr/bin/env python3
"""One settled authored DVD chapter transition on the exact visible iPhone.

Real BLE Select, then one public MCP Next Chapter as test setup only. Never
replays input, changes saved settings or calls a Core-private interface.
"""
import asyncio,importlib.util,json,logging,sys,time
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
sys.path.insert(0,str(BRIDGE/'tools/native_inspector'))
import wireless_inspect as W
from field_hid import InputOwner
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
clock_spec=importlib.util.spec_from_file_location('dvd_field_clock',ROOT/'scripts/dvd-field-clock.py')
clock_check=importlib.util.module_from_spec(clock_spec);clock_spec.loader.exec_module(clock_check)
identity='123c8282e1ee'
def mcp(action,**values):return C.request(cfg,'/v1/control',dict(action=action,**values),mcp=True,timeout=8)
def guard():
    a=C.activity(cfg)
    if a.get('recordingCount')!=0 or a.get('connectedClientCount')!=0 or mcp('ui.list').get('contexts')!=[identity]:raise RuntimeError('Exact idle test ownership required')
    n=mcp('ui.state',context=identity)
    if not n.get('dvd') or (n.get('media') or {}).get('mediaFileId')!=20819:raise RuntimeError('Canonical DVD owner changed')
    return n
if guard().get('dvdMenu') is not True:raise SystemExit('Require reviewed canonical root menu; no automatic Root/Watch')
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
out=ROOT/'artifacts/active/WP08-004'/(stamp+'-iphone-dvd-chapter-clock.json');out.parent.mkdir(parents=True,exist_ok=True)
report={'utc':datetime.now(timezone.utc).isoformat(),'passed':False,'physicalPhone':True,
        'physicalFingerGesture':False,'navigation':'One BLE Select; public MCP Next Chapter test setup',
        'inputReplayed':False,'samples':[],'nextChapterSubmitted':False}
original=W.evaluate
class Trigger:
    def read_text(self,**_):return '__OWNED_DVD_CHAPTER_CLOCK__'
async def evaluate(session,expression):
    if expression!='__OWNED_DVD_CHAPTER_CLOCK__':return await original(session,expression)
    async def ev(script):return await original(session,script)
    owner=InputOwner('192.168.10.113',(BRIDGE/'build/native-inspector/token.txt').read_text(encoding='ascii').strip())
    installed=False
    async def sample(phase):
        v=await ev("""(()=>{const s=__chapterClock,v=videoPlane;return{sourceChanged:v.currentSrc!==s.source,frames:s.frames,lastPresented:s.last,time:v.currentTime,paused:v.paused,ready:v.readyState,width:v.videoWidth,error:v.error?.code||null,blocked:!autoplayBtn.hidden,message:osdMessage.textContent};})()""")
        n=await asyncio.to_thread(guard)
        v.update(phase=phase,nativeMenu=n.get('dvdMenu'),title=n.get('dvdTitle'),chapter=n.get('dvdChapter'),rawMs=n.get('rawMediaTimeMs'))
        report['samples'].append(v)
        if v['blocked'] or v['error']:raise RuntimeError('Playback activation/decoder failure; no input replay')
        return v
    try:
        await ev("""(()=>{if(!window.__iphoneGate?.api||window.__chapterClock||document.visibilityState!=='visible'||(localStorage.getItem('sagetvWebMiniClientId')||'').replace(/:/g,'').toLowerCase()!=='123c8282e1ee')throw Error('Wrong visible phone');const s=window.__chapterClock={source:videoPlane.currentSrc,frames:0,last:null,done:false};function frame(n,m){if(s.done)return;if(videoPlane.currentSrc!==s.source){s.frames++;s.last=m.mediaTime}videoPlane.requestVideoFrameCallback(frame)}videoPlane.requestVideoFrameCallback(frame);stage.focus();return{syntheticFocusOnly:true}})()""");installed=True
        await owner.arm();await owner.send('key',key='enter');await owner.close()
        deadline=time.monotonic()+35;settled=None
        while time.monotonic()<deadline:
            s=await sample('settle-feature')
            # Obtain actual early pictures before a14s converter reserve can
            # move the VM into this fixture's20s next chapter. The subsequent
            # chapter gate still requires five seconds of new decoded frames.
            if s['nativeMenu'] is False and s['sourceChanged'] and s['frames']>=15 and s['time']>=.5 and not s['paused']:
                settled=s;break
            await asyncio.sleep(.3)
        if settled is None:raise RuntimeError('Feature did not settle before chapter test')
        if settled['chapter']!=1:raise RuntimeError('Reader already advanced beyond presented early chapter1; no Next sent')
        if not 0<=settled['rawMs']<15000:raise RuntimeError('Early chapter1 clock window missed; no Next sent')
        await ev("(()=>{const s=__chapterClock;s.source=videoPlane.currentSrc;s.frames=0;s.last=null;return{chapterWitnessReset:true}})()")
        n=await asyncio.to_thread(guard)
        if n.get('dvdMenu') is not False or n.get('dvdChapter')!=1 or not 0<=n.get('rawMediaTimeMs',-1)<15000:raise RuntimeError('Source changed before Next; no dispatch')
        report['nextChapterSubmitted']=True
        if not (await asyncio.to_thread(mcp,'ui.command',context=identity,command='DVD Next Chapter')).get('accepted'):raise RuntimeError('One Next outcome rejected/unknown; not replayed')
        deadline=time.monotonic()+30;first=None;stable=[]
        while time.monotonic()<deadline:
            s=await sample('chapter2')
            if s['sourceChanged'] and s['frames']>=15 and s['time']>.5 and s['ready']>=2 and not s['paused']:
                if not clock_check.chapter_two_picture_clock(s):raise RuntimeError('New chapter pictures disagree with authored20s title clock')
                if first is None:first=s
                stable.append(s)
                if s['lastPresented']>=first['lastPresented']+5:
                    if s['rawMs']<=first['rawMs']+3500:raise RuntimeError('Chapter title clock failed to advance with five seconds of pictures')
                    report.update(passed=True,stableSamples=len(stable),
                        authoredChapterStartMs=20000,readerChapters=sorted({v['chapter'] for v in stable}),
                        readerChapterIsPresentedOracle=False)
                    return{'passed':True,'authoredChapter2PictureClock':True}
            await asyncio.sleep(.35)
        raise RuntimeError('No stable chapter2 replacement pictures')
    finally:
        report['inputCommands']=owner.sequence-1;await owner.close()
        if installed:report['observerCleanup']=await ev("(()=>{if(window.__chapterClock)window.__chapterClock.done=true;delete window.__chapterClock;return!window.__chapterClock})()")
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,page_id=None,verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,screenshot=out.with_suffix('.png'))
async def run():
    async def attached(rsd,data):await W.inspect(rsd,data,args)
    await W.probe(args,report,on_rsd=attached)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
try:asyncio.run(asyncio.wait_for(run(),130))
except Exception as error:report.update(passed=False,errorType=type(error).__name__,error=str(error)[:200] if isinstance(error,RuntimeError) else 'Observation unavailable; no replay')
finally:
    W.evaluate=original
    with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps(dict(passed=report['passed'],samples=len(report['samples']),nextChapterSubmitted=report['nextChapterSubmitted'],error=report.get('error')))+'\n'+str(out))
raise SystemExit(0 if report['passed'] else 1)
