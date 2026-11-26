#!/usr/bin/env python3
"""One authored iPhone title EOF -> new menu decoder, no synthetic navigation.

Canonical fixture/UI only. Enter is real ESP32 BLE. No seek, FLUSH, loop,
server change, bookmark or playback input replay. One exact inspector owner.
"""
import argparse,asyncio,importlib.util,json,logging,sys,time
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
sys.path.insert(0,str(BRIDGE/'tools/native_inspector'))
import wireless_inspect as W
from field_hid import InputOwner
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py');C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
identity='123c8282e1ee'
p=argparse.ArgumentParser();p.add_argument('--observe-existing',action='store_true',help='Read-only continuation of the already-started canonical feature; never repeat Enter');p.add_argument('--public-select',action='store_true',help='One existing public MCP DVD Select as decoder-test setup, not a physical-key claim');p.add_argument('--task',choices=['WEB-060','WEB-064','WEB-081','WEB-084'],default='WEB-060');args_cli=p.parse_args()
if args_cli.observe_existing and args_cli.public_select:p.error('Choose one start intent')
def mcp(action,**v):return C.request(cfg,'/v1/control',dict(action=action,**v),mcp=True,timeout=5)
a=C.activity(cfg)
if a.get('recordingCount')!=0 or a.get('connectedClientCount')!=0 or mcp('ui.list').get('contexts')!=[identity]:raise SystemExit('Require exact idle test ownership')
s=mcp('ui.state',context=identity)
if not s.get('dvd') or bool(s.get('dvdMenu'))==args_cli.observe_existing or (s.get('media') or {}).get('mediaFileId')!=20819:raise SystemExit('Require exact authored root menu or explicitly existing feature')
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');out=ROOT/'artifacts/active'/args_cli.task/(stamp+'-iphone-natural-dvd-eof.json');out.parent.mkdir(parents=True,exist_ok=True)
report={'utc':datetime.now(timezone.utc).isoformat(),'passed':False,'physicalPhone':True,'physicalFingerGesture':False,'inputReplayed':False,'samples':[]}
original=W.evaluate
class Trigger:
    def read_text(self,**_):return '__DVD_EOF_FIELD_GATE__'
async def evaluate(session,expression):
    if expression!='__DVD_EOF_FIELD_GATE__':return await original(session,expression)
    async def ev(text):return await original(session,text)
    owner=InputOwner('192.168.10.113',(BRIDGE/'build/native-inspector/token.txt').read_text(encoding='ascii').strip())
    installed=False
    try:
        await ev("""(()=>{if(!window.__iphoneGate?.api||window.__dvdEofField||document.visibilityState!=='visible'||(localStorage.getItem('sagetvWebMiniClientId')||'').replace(/:/g,'').toLowerCase()!=='123c8282e1ee')throw Error('Wrong/unowned phone');const s=window.__dvdEofField={initial:videoPlane.currentSrc,feature:null,done:false,presented:0,lastPresented:null};const frame=(n,m)=>{if(!s.done){s.presented++;s.lastPresented=m.mediaTime;videoPlane.requestVideoFrameCallback(frame);}};videoPlane.requestVideoFrameCallback(frame);document.getElementById('stage').focus();return{syntheticFocusOnly:true};})()""");installed=True
        if args_cli.observe_existing:
            await ev("(()=>{window.__dvdEofField.feature=videoPlane.currentSrc;return{existingFeatureObserved:true,noNavigationInput:true};})()")
        elif args_cli.public_select:
            selected=await asyncio.to_thread(mcp,'ui.command',context=identity,command='Select')
            if not selected.get('accepted'):raise RuntimeError('One public DVD Select rejected; no replay')
            report['navigation']='Existing public MCP decoder-test setup, not BLE/finger input proof'
        else:
            await owner.arm();await owner.send('key',key='enter');await owner.close()
        deadline=time.monotonic()+135;feature=False;feature_generation=None
        while time.monotonic()<deadline:
            await ev("(()=>{const s=window.__dvdEofField;s.nativePending=true;window.__iphoneGate.api('status').then(j=>s.native=j.connection?.dvd).finally(()=>s.nativePending=false);return{readOnlyStatusRequested:true};})()")
            for _ in range(30):
                if not await ev("window.__dvdEofField.nativePending"):break
                await asyncio.sleep(.1)
            else:raise RuntimeError('Read-only native state unavailable')
            v=await ev("""(()=>{const s=window.__dvdEofField,v=videoPlane,c=document.getElementById('dvdSpuCanvas'),p=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let pixels=0;for(let i=3;i<p.length;i+=4)if(p[i])pixels++;if(!s.feature&&v.currentSrc!==s.initial&&v.currentTime>.3)s.feature=v.currentSrc;return{time:v.currentTime,paused:v.paused,ready:v.readyState,width:v.videoWidth,frames:v.getVideoPlaybackQuality?.().totalVideoFrames,error:v.error?.code||null,featureStarted:!!s.feature,newSourceAfterFeature:!!s.feature&&v.currentSrc!==s.feature,presented:s.presented,lastPresented:s.lastPresented,pixels,blocked:!document.getElementById('autoplayBtn').hidden,message:document.getElementById('osdMessage').textContent,dvd:s.native};})()""")
            native=await asyncio.to_thread(mcp,'ui.state',context=identity)
            if not native.get('dvd') or (native.get('media') or {}).get('mediaFileId')!=20819:raise RuntimeError('DVD owner changed')
            v['nativeMenu']=native.get('dvdMenu');v['title']=native.get('dvdTitle');v['chapter']=native.get('dvdChapter');report['samples'].append(v)
            if v['blocked']:raise RuntimeError('Trusted Play required; no input replay')
            if v['error']:raise RuntimeError('Browser media error')
            if v['featureStarted'] and not v['nativeMenu'] and v['time']>1:
                feature=True
                if feature_generation is None:feature_generation=(v.get('dvd') or {}).get('generation')
            if feature and v['nativeMenu'] and v['newSourceAfterFeature'] and v['ready']>=2 and v['width']>0 and v['pixels']>100 and (v['frames'] or 0)>0 and not v['message']:
                if feature_generation is None or (v.get('dvd') or {}).get('generation',0)<=feature_generation:raise RuntimeError('Menu reused ended feature decoder')
                report['passed']=True;report['featureGeneration']=feature_generation;return{'passed':True,'naturalMenuPicture':True}
            await asyncio.sleep(1)
        raise RuntimeError('Natural title EOF did not produce a new decoded menu')
    finally:
        report['inputCommands']=owner.sequence-1;await owner.close()
        if installed:report['observerCleanup']=await ev("(()=>{if(window.__dvdEofField)window.__dvdEofField.done=true;delete window.__dvdEofField;return!window.__dvdEofField;})()")
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,page_id=None,verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,screenshot=None)
async def run():
    async def attached(rsd,data):await W.inspect(rsd,data,args)
    await W.probe(args,report,on_rsd=attached)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
try:asyncio.run(asyncio.wait_for(run(),165))
except Exception as e:report.update(passed=False,errorType=type(e).__name__,error=str(e)[:250] if isinstance(e,RuntimeError) else 'Observation unavailable; no input replay')
finally:
    W.evaluate=original
    with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({'passed':report['passed'],'samples':len(report['samples']),'error':report.get('error')})+'\n'+str(out))
raise SystemExit(0 if report['passed'] else 1)
