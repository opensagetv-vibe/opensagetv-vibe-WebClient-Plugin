#!/usr/bin/env python3
"""WEB081 actual phone's natural completed-recording tail, no clock/ended edits.

One exact public Watch is synthetic setup. Only an actual Safari activation
prompt may receive one real BLE Enter after explicit button focus. No seek,
settings mutation or replay; --observe-existing never dispatches Watch.
"""
import argparse,asyncio,importlib.util,json,logging,sys,time
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
from field_candidate import playback_revision
ROOT=Path(__file__).resolve().parents[1];BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
EXPECTED_PLAYBACK=playback_revision(ROOT)
sys.path.insert(0,str(BRIDGE/'tools/native_inspector'))
import wireless_inspect as W
from field_hid import InputOwner
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration();identity='123c8282e1ee'
p=argparse.ArgumentParser();p.add_argument('--observe-existing',action='store_true',help='Observe the exact already-started canonical source; never replay Watch');args_cli=p.parse_args()
activity=C.activity(cfg);uis=C.request(cfg,'/v1/control',{'action':'ui.list'},mcp=True)
if activity.get('recordingCount')!=0 or activity.get('connectedClientCount')!=0 or uis.get('contexts')!=[identity]:raise SystemExit('Require exact idle phone ownership')
if args_cli.observe_existing and C.request(cfg,'/v1/control',{'action':'ui.state','context':identity},mcp=True).get('media',{}).get('mediaFileId')!=20905:raise SystemExit('Require already-owned canonical source')
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');out=ROOT/'artifacts/active/WEB-081'/(stamp+'-iphone-eof.json');out.parent.mkdir(parents=True,exist_ok=True)
report={'passed':False,'physicalPhone':True,'physicalFingerGesture':False,'syntheticSetup':'read-only existing canonical source' if args_cli.observe_existing else 'one exact public watchContent media20905','inputReplayed':False,'rows':[]}
original=W.evaluate
class Trigger:
 def read_text(self,**_):return '__PHONE_RECORDING_EOF__'
async def evaluate(session,expression):
 if expression!='__PHONE_RECORDING_EOF__':return await original(session,expression)
 async def ev(script):return await original(session,script)
 installed=False
 try:
  await ev("(()=>{if(window.__eofSessionProbe)throw Error('Existing probe');const p=window.__eofSessionProbe={id:'',real:window.fetch};p.observe=function(...a){const u=new URL(typeof a[0]==='string'?a[0]:a[0].url,location.href),id=u.searchParams.get('session');if(u.origin===location.origin&&u.pathname.endsWith('/api/miniclient')&&u.searchParams.get('action')==='events'&&/^[a-f0-9]{32}$/.test(id||'')){p.id=id;if(window.fetch===p.observe)window.fetch=p.real;}return p.real.apply(this,a)};window.fetch=p.observe;return true})()")
  deadline=time.monotonic()+35
  while not await ev('!!window.__eofSessionProbe?.id'):
   if time.monotonic()>deadline:raise RuntimeError('Fresh native session not observed; no Watch dispatched')
   await asyncio.sleep(.2)
  setup=await ev("""(()=>{if(document.visibilityState!=='visible'||(localStorage.getItem('sagetvWebMiniClientId')||'').replace(/:/g,'').toLowerCase()!=='123c8282e1ee'||window.__phoneEof||window.__vibeFieldHid||(!!(videoPlane.getAttribute('src')||videoPlane.srcObject)||videoPlane.readyState>0)!==OBSERVE)throw Error('Require exact owned phone/source');const id=window.__eofSessionProbe?.id;if(!id)throw Error('No fresh native session');const s=window.__phoneEof={session:id,settings:localStorage.getItem('sagetvWebMiniClientSettings.v1'),stream:localStorage.getItem('sagetvWebStreaming.v1'),ended:0,frames:0,done:false,point:null};window.__vibeFieldHid=s;s.end=()=>s.ended++;s.move=e=>{if(e.isTrusted)s.point={x:e.clientX,y:e.clientY}};videoPlane.addEventListener('ended',s.end);document.addEventListener('pointermove',s.move,true);function frame(){if(s.done)return;s.frames++;videoPlane.requestVideoFrameCallback(frame)}videoPlane.requestVideoFrameCallback(frame);s.cleanup=()=>{s.done=true;videoPlane.removeEventListener('ended',s.end);document.removeEventListener('pointermove',s.move,true);delete window.__vibeFieldHid;delete window.__phoneEof};return{session:s.session,playbackRevision:[...document.scripts].find(e=>e.src.includes('miniclient-playback.js'))?.src.split('?')[1]}})()""".replace('OBSERVE',json.dumps(args_cli.observe_existing)));installed=True
  if setup.get('playbackRevision')!=EXPECTED_PLAYBACK:raise RuntimeError('Wrong installed playback revision')
  report['verifiedPlaybackRevision']=EXPECTED_PLAYBACK
  configured=(await asyncio.to_thread(C.request,cfg,'/SageTVWebPlayer/api/miniclient?action=streamSettings&session='+setup['session'])).get('configured')
  if not args_cli.observe_existing:
   result=await asyncio.to_thread(C.request,cfg,'/SageTVWebPlayer/api/miniclient',{'action':'watchContent','session':setup['session'],'mediaId':20905})
   if not result.get('accepted'):raise RuntimeError('Exact Watch refused; no replay')
  report['rows'].append({'gate':'existing-source-observation-no-replay' if args_cli.observe_existing else 'one-public-Watch-accepted','passed':True});clicked=False;first=None;deadline=time.monotonic()+140
  while time.monotonic()<deadline:
   current=await ev("(()=>{const s=__phoneEof,v=videoPlane,r=v.buffered;return{time:v.currentTime,duration:Number.isFinite(v.duration)?v.duration:null,frames:s.frames,ended:s.ended,nativeEnded:v.ended,paused:v.paused,ready:v.readyState,error:v.error?.code||null,prompt:!autoplayBtn.hidden,nativeHls:!!v.currentSrc&&!v.currentSrc.startsWith('blob:'),tailEnd:r.length?r.end(r.length-1):null,message:osdMessage.textContent}})()")
   if current['error']:raise RuntimeError('Actual media error')
   if current['prompt'] and not clicked:
    owner=InputOwner('192.168.10.113',(BRIDGE/'build/native-inspector/token.txt').read_text(encoding='ascii').strip())
    try:
     await ev("(()=>{if(autoplayBtn.hidden||autoplayBtn.disabled)throw Error('Activation target changed');autoplayBtn.focus({preventScroll:true});if(document.activeElement!==autoplayBtn)throw Error('Focus failed');return true})()")
     await owner.arm();await owner.send('key',key='enter');clicked=True;report['activation']='one BLE Enter after synthetic explicit Play-button focus'
    finally:await owner.close()
   if first is None and current['frames']>10 and not current['paused']:
    first=current;report['rows'].append({'gate':'new-presented-recording-frames','passed':True,'sample':first});print('PASS new presented recording frames',flush=True)
   if current['time']>87 and len(report.setdefault('tailSamples',[]))<12:report['tailSamples'].append(current)
   if first and current['ended']>0:
    await asyncio.sleep(.7)
    terminal=await ev("({ended:__phoneEof.ended,message:osdMessage.textContent,source:!!videoPlane.currentSrc,paused:videoPlane.paused})")
    if 'Buffering' in terminal['message']:raise RuntimeError('Buffering persists after actual ended')
    report['rows'].append({'gate':'actual-native-ended-no-internal-refill-deadlock','passed':True,'sample':current,'terminal':terminal});print('PASS actual native ended without refill deadlock',flush=True);break
   await asyncio.sleep(.2)
  else:
   report['last']=current;raise RuntimeError('Actual ended did not arrive within natural fixture duration')
  if not first.get('nativeHls'):raise RuntimeError('Expected actual native Safari HLS')
  preserved=await ev("(()=>{const s=__phoneEof;return s.settings===localStorage.getItem('sagetvWebMiniClientSettings.v1')&&s.stream===localStorage.getItem('sagetvWebStreaming.v1')})()")
  current_configured=(await asyncio.to_thread(C.request,cfg,'/SageTVWebPlayer/api/miniclient?action=streamSettings&session='+setup['session'])).get('configured')
  if not preserved or current_configured!=configured:raise RuntimeError('Saved profiles changed')
  report['passed']=True;report['profilesPreserved']=True;return {'passed':True,'rows':len(report['rows'])}
 finally:
  if installed:report['observerRemoved']=await ev("(()=>{__phoneEof.cleanup();return !window.__phoneEof})()")
  await ev("(()=>{const p=window.__eofSessionProbe;if(p&&window.fetch===p.observe)window.fetch=p.real;delete window.__eofSessionProbe;return true})()")
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,page_id=None,verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,screenshot=out.with_suffix('.png'))
async def run():
 async def attached(rsd,data):await W.inspect(rsd,data,args)
 await W.probe(args,report,on_rsd=attached)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
try:asyncio.run(asyncio.wait_for(run(),170))
except Exception as error:report.update(passed=False,errorType=type(error).__name__,error=str(error)[:200] if isinstance(error,RuntimeError) else 'Observation unavailable; no replay')
finally:
 W.evaluate=original
 with out.open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2)
print(json.dumps({'passed':report['passed'],'rows':len(report['rows']),'error':report.get('error'),'report':str(out)}));raise SystemExit(0 if report['passed'] else 1)
