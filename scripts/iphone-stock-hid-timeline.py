#!/usr/bin/env python3
"""One exact-phone stock-STV BLE timeline gate, no cross-attach OSD expiry.

Public Watch is separate guarded setup. No saved preferences, clock changes,
synthetic clicks, Core edits or input replay. Keep pixels strictly test-only.
"""
import asyncio,importlib.util,json,logging,sys,time
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
sys.path.insert(0,str(BRIDGE/'tools/native_inspector'))
import wireless_inspect as W
from field_hid import InputOwner,move_to
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
identity='123c8282e1ee'
def mcp(action,**values):return C.request(cfg,'/v1/control',dict(action=action,**values),mcp=True)
activity=C.activity(cfg)
if activity.get('recordingCount')!=0 or activity.get('connectedClientCount')!=0 or mcp('ui.list').get('contexts')!=[identity]:raise SystemExit('Require exact idle test ownership')
if not mcp('captions.get',context=identity).get('stvFile','').endswith('/SageTV7.xml'):raise SystemExit('Require borrowed unmodified stock STV')
if (mcp('ui.state',context=identity).get('media') or {}).get('mediaFileId')!=27166:raise SystemExit('Require exact long Nightline test source')
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
out=ROOT/'artifacts/active/WEB-049'/(stamp+'-stock-hid-timeline.json');out.parent.mkdir(parents=True,exist_ok=True)
report={'utc':datetime.now(timezone.utc).isoformat(),'passed':False,'physicalPhone':True,'physicalFingerGesture':False,'inputReplayed':False,'rows':[]}
original=W.evaluate
class Trigger:
    def read_text(self,**_):return '__STOCK_HID_TIMELINE__'
async def evaluate(session,expression):
    if expression!='__STOCK_HID_TIMELINE__':return await original(session,expression)
    async def ev(script):return await original(session,script)
    async def probe(name):return await ev((ROOT/'tests'/name).read_text(encoding='utf-8'))
    async def wait_video(paused):
        deadline=time.monotonic()+8
        while time.monotonic()<deadline:
            value=await ev("(()=>({paused:videoPlane.paused,ready:videoPlane.readyState,time:videoPlane.currentTime,width:videoPlane.videoWidth,prompt:!document.getElementById('autoplayBtn').hidden}))()")
            if value['prompt']:raise RuntimeError('Trusted Play required; no retry')
            if value['ready']>=2 and value['width']>0 and value['paused']==paused:return value
            await asyncio.sleep(.1)
        raise RuntimeError('Ordered pause/play did not settle; no replay')
    token=(BRIDGE/'build/native-inspector/token.txt').read_text(encoding='ascii').strip()
    owner=InputOwner('192.168.10.113',token);installed=False;traced=False
    try:
        await ev("(()=>{if((localStorage.getItem('sagetvWebMiniClientId')||'').replace(/:/g,'').toLowerCase()!=='123c8282e1ee'||document.visibilityState!=='visible'||window.__vibeFieldHid||!window.__iphoneGate?.api)throw Error('Wrong/hidden/unowned phone');const s=window.__vibeFieldHid={point:null},f=e=>{if(e.isTrusted)s.point={x:e.clientX,y:e.clientY};};document.addEventListener('pointermove',f,true);s.cleanup=()=>{document.removeEventListener('pointermove',f,true);delete window.__vibeFieldHid;};document.getElementById('stage').focus();return{syntheticFocus:true};})()")
        installed=True;await owner.arm()
        # Position BEFORE revealing the short-lived native OSD. Red marker
        # geometry below determines actual Y; no production STV assumptions.
        report['pointerPreparation']=await move_to(owner,ev,'gfxCanvas',{'x':400,'y':325})
        state=await ev("({paused:videoPlane.paused,ready:videoPlane.readyState,width:videoPlane.videoWidth})")
        if state['ready']<2 or state['width']==0:raise RuntimeError('Video not ready; no control sent')
        report['initialPaused']=state['paused']
        if state['paused']:
            await owner.send('key',key='space');await wait_video(False)
        await owner.send('key',key='space');await wait_video(True)
        await owner.send('key',key='space');await wait_video(False)
        geometry=await probe('iphone-stock-marker-geometry.js');report['markerBefore']=geometry
        if not geometry['peaks'] or geometry['peaks'][0]['n']<15:raise RuntimeError('Actual native stock marker absent; no click sent')
        peak=geometry['peaks'][0];y=(peak['lo']+peak['hi'])/4+2
        report['pointerHit']=await move_to(owner,ev,'gfxCanvas',{'x':400,'y':y})
        await probe('iphone-timeline-trace.js');traced=True
        await probe('iphone-stock-timeline-pixels.js');await probe('iphone-touch-observe.js')
        await owner.send('mouse',dx=0,dy=0,wheel=0,click=True)
        deadline=time.monotonic()+15
        while time.monotonic()<deadline:
            result=await probe('iphone-timeline-result.js')
            if result['frames'] and any(row['time']>.1 for row in result['frames']):break
            await asyncio.sleep(.2)
        report['result']=result
        downs=[r for r in result['touch'] if r['type']=='pointerdown' and r['trusted']]
        if not downs:raise RuntimeError('No trusted timeline down; no replay')
        start=downs[0]['at'];old=peak['x']
        changed=[p for p in result['pixelChanges'] if p['at']>=start and p['score']>=15 and p['marker'] is not None and abs(p['marker']-old)>40]
        frames=[f for f in result['frames'] if f['at']>=start and f['time']>.1]
        if not changed or not frames:raise RuntimeError('Marker/new-frame evidence incomplete')
        marker=changed[0]['at']-start;frame=frames[0]['at']-start
        report.update(nativeMarkerMs=marker,newMovingFrameMs=frame)
        if marker>=frame:raise RuntimeError('Native marker still waits for video')
        report['passed']=True
        return {'nativeMarkerMs':marker,'newMovingFrameMs':frame,'realBleClick':True}
    finally:
        report['inputCommands']=owner.sequence-1
        if traced:
            report['traceCleanup']=await ev("(()=>{const t=window.__iphoneGate.trace;t.done=true;return{stopping:true};})()")
        # Restore input ownership even when observation fails. Source playback
        # remains available; no uncertain key is replayed to guess its state.
        await owner.close()
        if installed:await ev("(()=>{window.__vibeFieldHid?.cleanup();return{observerRemoved:!window.__vibeFieldHid};})()")
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,page_id=None,verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,screenshot=None)
async def run():
    async def attached(rsd,data):await W.inspect(rsd,data,args)
    await W.probe(args,report,on_rsd=attached)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
try:asyncio.run(asyncio.wait_for(run(),110))
except Exception as e:report.update(passed=False,errorType=type(e).__name__,error=str(e)[:250] if isinstance(e,RuntimeError) else 'Observation unavailable; no input replay')
finally:
    W.evaluate=original
    with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in report.items() if k in ('passed','error','nativeMarkerMs','newMovingFrameMs')})+'\n'+str(out))
raise SystemExit(0 if report['passed'] else 1)
