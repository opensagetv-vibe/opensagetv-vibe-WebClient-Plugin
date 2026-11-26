#!/usr/bin/env python3
"""Real BLE optional-DVD buttons; exact fixture and absent bookmark only.

Never overwrite a pre-existing bookmark or clear a concurrent change. Public
MCP is read-only setup/checkpoint and an explicitly recorded failure cleanup,
not a normal playback dependency. No mutation replay or synthetic click.
"""
import asyncio,importlib.util,json,logging,sys,time
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
sys.path.insert(0,str(BRIDGE/'tools/native_inspector'))
import wireless_inspect as W
from field_hid import InputOwner,move_to
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py');C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration();identity='123c8282e1ee'
def mcp(action,**v):return C.request(cfg,'/v1/control',dict(action=action,**v),mcp=True,timeout=5)
activity=C.activity(cfg)
if activity.get('recordingCount')!=0 or activity.get('connectedClientCount')!=0 or mcp('ui.list').get('contexts')!=[identity]:raise SystemExit('Require exact idle phone ownership')
before=mcp('companion.dvd_bookmark',context=identity)
if before.get('present') is not False:raise SystemExit('Preserve pre-existing bookmark; test refused')
state=mcp('ui.state',context=identity)
if not state.get('dvd') or (state.get('media') or {}).get('mediaFileId')!=20819:raise SystemExit('Require exact authored fixture')
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');out=ROOT/'artifacts/active/WEB-062'/(stamp+'-iphone-companion-controls.json');out.parent.mkdir(parents=True,exist_ok=True)
report={'utc':datetime.now(timezone.utc).isoformat(),'passed':False,'physicalPhone':True,'physicalFingerGesture':False,'syntheticClicks':False,'inputReplayed':False,'rows':[],'bookmarkOriginallyAbsent':True}
original=W.evaluate
class Trigger:
    def read_text(self,**_):return '__DVD_COMPANION_CONTROLS__'
async def evaluate(session,expression):
    if expression!='__DVD_COMPANION_CONTROLS__':return await original(session,expression)
    async def ev(s):return await original(session,s)
    saved=None;installed=False;saveAttempted=False
    async def snapshot():return await ev("(()=>({time:videoPlane.currentTime,paused:videoPlane.paused,ready:videoPlane.readyState,frames:videoPlane.getVideoPlaybackQuality?.().totalVideoFrames,error:videoPlane.error?.code||null,blocked:!document.getElementById('autoplayBtn').hidden,message:document.getElementById('dvdCompanionStatus').textContent,busy:[...document.querySelectorAll('[data-companion-dvd]')].every(e=>e.disabled)}))()")
    async def click(target):
        await ev("(()=>{const e=document.getElementById("+json.dumps(target)+");if(!e||e.disabled)throw Error('Control unavailable');e.scrollIntoView({block:'center'});return{syntheticScrollOnly:true};})()")
        owner=InputOwner('192.168.10.113',(BRIDGE/'build/native-inspector/token.txt').read_text(encoding='ascii').strip())
        try:
            await owner.arm();point=await move_to(owner,ev,target);await owner.send('mouse',dx=0,dy=0,wheel=0,click=True)
        finally:await owner.close()
        deadline=time.monotonic()+5
        while time.monotonic()<deadline:
            r=await snapshot()
            if not r['busy']:
                if not r['message'].startswith('DVD action accepted'):raise RuntimeError('Action not confirmed; do not replay')
                return{'button':target,'pointerHit':point,'feedback':r['message']}
            await asyncio.sleep(.1)
        raise RuntimeError('Action outcome not confirmed; do not replay')
    async def playing(minimum=0,maximum=None):
        deadline=time.monotonic()+25;first=None
        while time.monotonic()<deadline:
            r=await snapshot();n=await asyncio.to_thread(mcp,'ui.state',context=identity)
            if (n.get('media') or {}).get('mediaFileId')!=20819 or not n.get('dvd'):raise RuntimeError('Source changed')
            if r['blocked'] or r['error']:raise RuntimeError('Playback blocked/error; no input replay')
            if not n.get('dvdMenu') and n.get('mediaTimeMs',0)>=minimum and r['ready']>=2 and not r['paused']:
                if first is not None and r['time']>first+.5:
                    if maximum is not None and n['mediaTimeMs']>maximum:raise RuntimeError('Accepted DVD target outside declared tolerance')
                    return{'time':r['time'],'nativeTimeMs':n['mediaTimeMs'],'frames':r['frames']}
                if first is None:first=r['time']
            await asyncio.sleep(.15)
        raise RuntimeError('No advancing feature for accepted control')
    try:
        await ev("""(()=>{if(!window.__iphoneGate?.companionForm||window.__vibeFieldHid||document.visibilityState!=='visible'||document.getElementById('settingsPanel').hidden)throw Error('Require owned visible optional controls');const s=window.__vibeFieldHid={point:null},f=e=>{if(e.isTrusted)s.point={x:e.clientX,y:e.clientY};};document.addEventListener('pointermove',f,true);s.cleanup=()=>{document.removeEventListener('pointermove',f,true);delete window.__vibeFieldHid;};return{readOnlyPointerObserver:true};})()""");installed=True
        row=await click('fieldDvdBeginning');row['picture']=await playing(2000);report['rows'].append(row)
        await asyncio.sleep(4)
        saveAttempted=True;row=await click('fieldDvdSave');saved=await asyncio.to_thread(mcp,'companion.dvd_bookmark',context=identity)
        if not saved.get('present') or not saved.get('valid') or saved.get('positionMs',0)<1000:raise RuntimeError('Saved bookmark unverified')
        report['ownedBookmarkFingerprint']=saved['fingerprint'];row['savedPositionMs']=saved['positionMs'];report['rows'].append(row)
        row=await click('fieldDvdBeginning');row['picture']=await playing(maximum=8000);report['rows'].append(row)
        if (await asyncio.to_thread(mcp,'companion.dvd_bookmark',context=identity)).get('fingerprint')!=saved['fingerprint']:raise RuntimeError('Concurrent bookmark changed; preserve it')
        row=await click('fieldDvdResume');row['picture']=await playing(max(0,saved['positionMs']-2000),saved['positionMs']+15000);report['rows'].append(row)
        if (await asyncio.to_thread(mcp,'companion.dvd_bookmark',context=identity)).get('fingerprint')!=saved['fingerprint']:raise RuntimeError('Concurrent bookmark changed; preserve it')
        row=await click('fieldDvdClear');after=await asyncio.to_thread(mcp,'companion.dvd_bookmark',context=identity)
        report['bookmarkAbsenceRestored']=after.get('present') is False
        if not report['bookmarkAbsenceRestored']:raise RuntimeError('Bookmark clear unverified')
        report['rows'].append(row);saved=None;saveAttempted=False;report['passed']=True;return{'passed':True,'rows':len(report['rows'])}
    finally:
        if saved is not None:
            current=await asyncio.to_thread(mcp,'companion.dvd_bookmark',context=identity)
            if current.get('fingerprint')==saved.get('fingerprint'):
                await asyncio.to_thread(mcp,'companion.dvd_intent',context=identity,operation='clear_resume',confirm='true')
                report['failureCleanupPublicMcp']=True
                report['bookmarkAbsenceRestored']=(await asyncio.to_thread(mcp,'companion.dvd_bookmark',context=identity)).get('present') is False
            else:report['concurrentBookmarkPreserved']=True
        elif saveAttempted:
            current=await asyncio.to_thread(mcp,'companion.dvd_bookmark',context=identity)
            report['bookmarkAbsenceRestored']=current.get('present') is False
            if current.get('present'):report['unknownBookmarkPreserved']=True
        if installed:report['observerCleanup']=await ev("(()=>{window.__vibeFieldHid?.cleanup();return!window.__vibeFieldHid;})()")
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,page_id=None,verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,screenshot=None)
async def run():
    async def attached(rsd,data):await W.inspect(rsd,data,args)
    await W.probe(args,report,on_rsd=attached)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
try:asyncio.run(asyncio.wait_for(run(),160))
except Exception as e:report.update(passed=False,errorType=type(e).__name__,error=str(e)[:250] if isinstance(e,RuntimeError) else 'Observation unavailable; no replay')
finally:
    W.evaluate=original
    with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({'passed':report['passed'],'rows':len(report['rows']),'bookmarkAbsenceRestored':report.get('bookmarkAbsenceRestored'),'error':report.get('error')})+'\n'+str(out))
raise SystemExit(0 if report['passed'] else 1)
