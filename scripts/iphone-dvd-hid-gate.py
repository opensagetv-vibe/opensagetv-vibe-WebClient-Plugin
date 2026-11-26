#!/usr/bin/env python3
"""Actual-phone native DVD picture/subtitle/menu gate through ESP32 BLE.

Exact authored fixture/UI only. No bookmark clearing, saved settings, Core
changes, synthetic click/keyboard, guessed timestamps or input replay.
"""
import asyncio,importlib.util,json,logging,sys,time
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
sys.path.insert(0,str(BRIDGE/'tools/native_inspector'))
import wireless_inspect as W
from field_hid import InputOwner
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py');C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
identity='123c8282e1ee'
def mcp(action,**v):return C.request(cfg,'/v1/control',dict(action=action,**v),mcp=True,timeout=5)
activity=C.activity(cfg)
if activity.get('recordingCount')!=0 or activity.get('connectedClientCount')!=0 or mcp('ui.list').get('contexts')!=[identity]:raise SystemExit('Require exact idle test ownership')
state=mcp('ui.state',context=identity)
if not state.get('dvdMenu') or (state.get('media') or {}).get('mediaFileId')!=20819:raise SystemExit('Require exact authored root menu')
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');out=ROOT/'artifacts/active/WEB-023'/(stamp+'-dvd-hid-gate.json')
report={'utc':datetime.now(timezone.utc).isoformat(),'passed':False,'physicalPhone':True,'physicalFingerGesture':False,'rows':[],'inputReplayed':False}
original=W.evaluate
class Trigger:
    def read_text(self,**_):return '__DVD_HID_FIELD_GATE__'
def off(n):return n is None or n in (62,8192) or n<0 or bool(n&128)
async def evaluate(session,expression):
    if expression!='__DVD_HID_FIELD_GATE__':return await original(session,expression)
    async def ev(s):return await original(session,s)
    async def sample():return await ev("(()=>{const s=window.__dvdField,v=videoPlane,c=document.getElementById('dvdSpuCanvas'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let n=0;for(let i=3;i<d.length;i+=4)if(d[i])n++;return{time:v.currentTime,paused:v.paused,ready:v.readyState,width:v.videoWidth,frames:v.getVideoPlaybackQuality?.().totalVideoFrames,error:v.error?.code||null,selected:s.selected,pixels:n,sourceChanged:v.currentSrc!==s.previousSource,blocked:!document.getElementById('autoplayBtn').hidden,message:document.getElementById('osdMessage').textContent,presented:s.presented.slice(-8)};})()")
    async def wait(predicate,label,seconds=20):
        deadline=time.monotonic()+seconds;last=None
        while time.monotonic()<deadline:
            last=await sample()
            if predicate(last):return last
            if last['blocked']:raise RuntimeError('Trusted Play required; no replay')
            await asyncio.sleep(.12)
        report['last']=last;raise RuntimeError('Timed out: '+label)
    async def native(command):
        state=await asyncio.to_thread(mcp,'ui.state',context=identity)
        if not state.get('dvd') or (state.get('media') or {}).get('mediaFileId')!=20819:raise RuntimeError('DVD owner changed')
        result=await asyncio.to_thread(mcp,'ui.command',context=identity,command=command)
        if not result.get('accepted'):raise RuntimeError('Native setup rejected; no replay')
    owner=InputOwner('192.168.10.113',(BRIDGE/'build/native-inspector/token.txt').read_text(encoding='ascii').strip())
    installed=False;toggled=False;baseline=None
    try:
        await ev("""(()=>{if(!window.__iphoneGate?.api||window.__dvdField||document.visibilityState!=='visible'||(localStorage.getItem('sagetvWebMiniClientId')||'').replace(/:/g,'').toLowerCase()!=='123c8282e1ee')throw Error('Wrong/unowned phone');const s=window.__dvdField={previousSource:videoPlane.currentSrc,selected:null,presented:[],done:false},f=window.fetch;function observed(input,options){const u=new URL(typeof input==='string'?input:input.url,location.href),p=new URLSearchParams(options?.body||u.search),r=f.apply(this,arguments);if(u.pathname.endsWith('/api/subtitles')&&p.get('scope')==='dvd')r.then(v=>v.clone().json()).then(j=>{if(Number.isInteger(j.dvdSpu?.selected))s.selected=j.dvdSpu.selected;}).catch(()=>{});return r;}window.fetch=observed;s.cleanup=()=>{s.done=true;if(window.fetch===observed)window.fetch=f;delete window.__dvdField;};const frame=(n,m)=>{if(!s.done){if(s.presented.length>=80)s.presented.shift();s.presented.push({time:m.mediaTime,changed:videoPlane.currentSrc!==s.previousSource});videoPlane.requestVideoFrameCallback(frame);}};videoPlane.requestVideoFrameCallback(frame);document.getElementById('stage').focus();return{syntheticFocusOnly:true};})()""");installed=True
        await owner.arm();await owner.send('key',key='enter');await owner.close()
        first=await wait(lambda r:r['sourceChanged'] and not r['paused'] and r['time']>.3 and r['ready']>=2,'moving feature')
        second=await wait(lambda r:r['time']>first['time']+2 and any(p['changed'] and p['time']>.1 for p in r['presented']),'actual presented feature')
        state=await asyncio.to_thread(mcp,'ui.state',context=identity)
        if state.get('dvdMenu'):raise RuntimeError('Still in authored menu')
        report['rows'].append({'gate':'real-BLE-Enter-advancing-feature','before':first,'after':second,'title':state.get('dvdTitle'),'chapter':state.get('dvdChapter')})
        current=await wait(lambda r:r['selected'] is not None,'DVD physical subtitle selection')
        baseline=off(current['selected']);report['initialSubtitleOff']=baseline
        if baseline:await native('DVD Subtitle Toggle');toggled=True
        shown=await wait(lambda r:not off(r['selected']) and r['pixels']>100,'selected title subtitle pixels')
        report['rows'].append({'gate':'actual-title-SPU-pixels','sample':shown})
        await native('DVD Subtitle Toggle');toggled=not toggled
        cleared=await wait(lambda r:off(r['selected']) and r['pixels']==0,'Off clears title SPU')
        report['rows'].append({'gate':'subtitle-Off-no-ghost','sample':cleared})
        if not baseline:await native('DVD Subtitle Toggle');toggled=False
        before=await asyncio.to_thread(mcp,'ui.state',context=identity)
        await ev("(()=>{window.__dvdField.previousSource=videoPlane.currentSrc;window.__dvdField.presented=[];return{chapterWitnessReset:true};})()")
        await native('DVD Next Chapter')
        chapter=await wait(lambda r:r['sourceChanged'] and r['time']>.3 and not r['paused'],'chapter replacement picture')
        after=await asyncio.to_thread(mcp,'ui.state',context=identity)
        if before.get('dvdChapter')==after.get('dvdChapter'):raise RuntimeError('Native chapter did not change')
        report['rows'].append({'gate':'native-next-chapter-and-moving-picture','before':before.get('dvdChapter'),'after':after.get('dvdChapter'),'sample':chapter})
        await native('DVD Menu')
        deadline=time.monotonic()+15
        while time.monotonic()<deadline:
            state=await asyncio.to_thread(mcp,'ui.state',context=identity)
            if state.get('dvdMenu'):break
            await asyncio.sleep(.1)
        else:raise RuntimeError('Authored menu did not return')
        menu=await wait(lambda r:r['width']>0 and r['ready']>=2 and r['pixels']>100 and not r['message'],'decoded selectable menu without misleading buffering')
        report['rows'].append({'gate':'native-root-menu-return-clear-feedback','sample':menu})
        report['passed']=True;return{'physicalRows':len(report['rows']),'passed':True}
    finally:
        if toggled:
            try:
                current=await sample()
                if baseline is not None and off(current['selected'])!=baseline:
                    await native('DVD Subtitle Toggle');report['subtitleRestored']=True
            except Exception:report['subtitleRestoration']='UNVERIFIED'
        report['inputCommands']=owner.sequence-1;await owner.close()
        if installed:report['observerCleanup']=await ev("(()=>{window.__dvdField?.cleanup();return!window.__dvdField;})()")
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,page_id=None,verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,screenshot=None)
async def run():
    async def attached(rsd,data):await W.inspect(rsd,data,args)
    await W.probe(args,report,on_rsd=attached)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
try:asyncio.run(asyncio.wait_for(run(),110))
except Exception as e:report.update(passed=False,errorType=type(e).__name__,error=str(e)[:250] if isinstance(e,RuntimeError) else 'Observation unavailable; no replay')
finally:
    W.evaluate=original
    with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({'passed':report['passed'],'rows':len(report['rows']),'error':report.get('error')})+'\n'+str(out))
raise SystemExit(0 if report['passed'] else 1)
