#!/usr/bin/env python3
"""WP12-006 actual stock/phone forward rate, Pause and reset; no control replay."""
import argparse,asyncio,importlib.util,json,logging,sys,time
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
sys.path.insert(0,str(BRIDGE/'tools/native_inspector'))
import wireless_inspect as W
from field_hid import InputOwner
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
identity='123c8282e1ee';fixture=20905
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--browser-local',action='store_true',help='Test production local Video choice; default reproduces public stock native-rate boundary')
parser.add_argument('--smoke-only',action='store_true',help='WEB093 affected ordinary source/seek/20s/Pause/Stop check; no rate matrix')
parser.add_argument('--task',choices=('WEB-093','WEB-094','WEB-095','WEB-096'),default='WEB-093',help='Owning affected task for smoke-only output')
options=parser.parse_args();local=options.browser_local;smoke=options.smoke_only
if smoke and not local:parser.error('Smoke does not issue native rate controls; use --browser-local')
if options.task!='WEB-093' and not smoke:parser.error('Explicit task override is for affected smoke only')
out=ROOT/'artifacts/active'/(options.task if smoke else 'WP12-006');out.mkdir(parents=True,exist_ok=True)
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
report=dict(passed=False,physicalPhone=True,inputReplayed=False,rateControl='production browser-local choice' if local else 'public stock SetPlaybackRate',rows=[])
def mcp(action,**kw):return C.request(cfg,'/v1/control',dict(action=action,**kw),mcp=True,timeout=30)
def guard(loaded=False):
    a=C.activity(cfg)
    if a.get('recordingCount')!=0 or a.get('connectedClientCount')!=0 or mcp('ui.list').get('contexts')!=[identity]:raise RuntimeError('Require exact approved phone and no other activity')
    n=mcp('ui.state',context=identity)
    if loaded and (n.get('media') or {}).get('mediaFileId')!=fixture:raise RuntimeError('Exact fixture owner changed')
    return n
original=W.evaluate
class Trigger:
    def read_text(self,**_):return '__PHONE_RATE_FIELD__'
async def evaluate(session,expression):
    if expression!='__PHONE_RATE_FIELD__':return await original(session,expression)
    async def ev(s):return await original(session,s)
    async def sample():return await ev("(()=>{const v=videoPlane,s=__rateField;return{time:v.currentTime,rate:v.playbackRate,paused:v.paused,ready:v.readyState,width:v.videoWidth,error:v.error?.code||null,blocked:!autoplayBtn.hidden,frames:s.frames,sameSource:v.currentSrc===s.source,seekChanged:v.currentSrc!==s.beforeSeek,assigned:!!v.getAttribute('src')}})()")
    async def change_rate(rate):
        await asyncio.to_thread(guard,True)
        if local:
            await ev("(()=>{const e=document.getElementById('browserPlaybackRate');if(!e||e.disabled)throw Error('Local rate choice unavailable');e.value="+json.dumps(str(rate))+";e.dispatchEvent(new Event('change',{bubbles:true}));return true})()")
        elif not (await asyncio.to_thread(mcp,'media.control',context=identity,operation='rate',rate=rate)).get('accepted'):raise RuntimeError('One rate request rejected')
    async def wait(test,label,seconds=40):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            v=await sample()
            if v['error']:raise RuntimeError('Actual video error: '+label)
            if test(v):return v
            await asyncio.sleep(.15)
        report['last']=v;raise RuntimeError('Timed out '+label+'; no replay')
    owner=InputOwner('192.168.10.113',(BRIDGE/'build/native-inspector/token.txt').read_text().strip())
    installed=False;watched=False;stop_submitted=False
    try:
        if (await asyncio.to_thread(guard)).get('fullyLoaded'):raise RuntimeError('Require stopped source')
        await ev("(()=>{if(document.visibilityState!=='visible'||window.__rateField)throw Error('Phone/observer unavailable');const s=window.__rateField={frames:0,done:false,streaming:localStorage.getItem('sagetvWebStreaming.v1'),client:localStorage.getItem('sagetvWebMiniClientSettings.v1')};const cb=()=>{if(!s.done){s.frames++;videoPlane.requestVideoFrameCallback(cb)}};videoPlane.requestVideoFrameCallback(cb);return true})()");installed=True
        r=await asyncio.to_thread(mcp,'media.watch',context=identity,media_id=fixture,wait_ms=0)
        if not r.get('accepted'):raise RuntimeError('One Watch rejected')
        watched=True;activated=False;end=time.monotonic()+60
        while time.monotonic()<end:
            v=await sample()
            if v['blocked'] and not activated:
                await ev('(()=>{autoplayBtn.focus();return document.activeElement===autoplayBtn})()')
                await owner.arm();await owner.send('key',key='enter');await owner.close();activated=True
            if v['frames']>=12 and not v['paused'] and v['ready']>=2:break
            await asyncio.sleep(.15)
        else:raise RuntimeError('No fresh moving source')
        await asyncio.to_thread(guard,True)
        await ev('(()=>{__rateField.beforeSeek=videoPlane.currentSrc;return true})()')
        if not (await asyncio.to_thread(mcp,'media.seek',context=identity,target_ms=10000)).get('accepted'):raise RuntimeError('One source seek rejected')
        await wait(lambda v:v['seekChanged'] and not v['paused'] and v['ready']>=2 and v['time']>.4,'fresh seek consumer',60)
        await ev('(()=>{__rateField.source=videoPlane.currentSrc;return true})()')
        for rate in ((1,) if smoke else (.5,1.5,2,1)):
            if not smoke:await change_rate(rate)
            before=await wait(lambda v:abs(v['rate']-rate)<.001 and not v['paused'] and v['sameSource'],'actual forward rate',8)
            began=time.monotonic();await asyncio.sleep(20 if smoke else 3);after=await sample();elapsed=time.monotonic()-began
            ratio=(after['time']-before['time'])/elapsed
            n=await asyncio.to_thread(guard,True)
            raw=n.get('rawMediaTimeMs');expected=10000+after['time']*1000
            delta=raw-expected if isinstance(raw,(int,float)) else None
            row=dict(rate=rate,observedRatio=ratio,before=before,after=after,nativeRate=n.get('playbackRate'),nativeFileTimeMs=raw,expectedFileTimeMs=expected,nativeClockErrorMs=delta)
            report['rows'].append(row);print(json.dumps(row),flush=True)
            if not after['sameSource'] or after['frames']<=before['frames'] or abs(ratio-rate)>.4 or abs(n.get('playbackRate',-99)-(1 if local else rate))>.01:raise RuntimeError('Rate return/native/browser presentation mismatch')
            if delta is None or abs(delta)>2000:raise RuntimeError('Native file clock diverged from actual local-rate presentation')
        if not (await asyncio.to_thread(mcp,'media.control',context=identity,operation='pause')).get('accepted'):raise RuntimeError('Pause rejected')
        await wait(lambda v:v['paused'],'Pause')
        if not smoke:
            await change_rate(2)
            await wait(lambda v:v['paused'] and v['rate']==2,'rate preserves Pause',8)
            await change_rate(1)
            await wait(lambda v:v['paused'] and v['rate']==1,'reset preserves Pause',8)
        preserved=await ev("(()=>{const s=__rateField;return{streaming:s.streaming===localStorage.getItem('sagetvWebStreaming.v1'),client:s.client===localStorage.getItem('sagetvWebMiniClientSettings.v1')}})()")
        if not all(preserved.values()):raise RuntimeError('Saved preferences changed')
        report['rows'].append(dict(gate='ordinary-pause-and-profiles' if smoke else 'paused-rate-reset-and-profiles',passed=True,profiles=preserved))
        await asyncio.to_thread(guard,True);stop_submitted=True
        if not (await asyncio.to_thread(mcp,'media.control',context=identity,operation='stop')).get('accepted'):raise RuntimeError('Stop rejected')
        await wait(lambda v:v['paused'] and v['ready']==0 and not v['assigned'],'decoder teardown',15)
        if (await asyncio.to_thread(guard)).get('fullyLoaded'):raise RuntimeError('Native source did not close')
        report['passed']=True;return dict(passed=True,rows=len(report['rows']))
    finally:
        if watched and not stop_submitted:
            try:
                await asyncio.to_thread(guard,True);stop_submitted=True
                report['failureCleanupAccepted']=(await asyncio.to_thread(mcp,'media.control',context=identity,operation='stop')).get('accepted')
            except Exception:report['failureCleanupUnknown']=True
        if installed:
            try:await ev('(()=>{__rateField.done=true;delete window.__rateField;return true})()')
            except Exception:report['observerCleanupUnknown']=True
        await owner.close()
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,page_id=None,verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,screenshot=None)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
async def run():
    async def attached(rsd,data):await W.inspect(rsd,data,args)
    await W.probe(args,report,on_rsd=attached)
try:asyncio.run(asyncio.wait_for(run(),180))
except Exception as e:report.update(passed=False,errorType=type(e).__name__,error=str(e)[:300] if isinstance(e,RuntimeError) else 'Observation unavailable; no replay')
finally:
    path=out/(stamp+('-iphone-ordinary.json' if smoke else '-iphone-rate.json'));path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(passed=report['passed'],rows=len(report['rows']),error=report.get('error'),report=str(path))),flush=True)
raise SystemExit(0 if report['passed'] else 1)
