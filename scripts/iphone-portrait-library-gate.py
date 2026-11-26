#!/usr/bin/env python3
"""Actual portrait phone + real ESP32 BLE clicks, exact stock232 UI only.

Synthetic scroll/search setup is labeled; no scheduled recordings, source
imports, saved-setting edits, unknown-action replay or physical-finger claim.
Leaves the canonical video playing for the operator's rotation check.
"""
import asyncio,base64,importlib.util,json,logging,sys,time
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
sys.path.insert(0,str(BRIDGE/'tools/native_inspector'))
import wireless_inspect as W
from field_hid import InputOwner,move_to
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
identity='123c8282e1ee';owned=None
def mcp(action,**values):return C.request(cfg,'/v1/control',dict(action=action,**values),mcp=True,timeout=5)
before=C.activity(cfg)
if before.get('recordingCount')!=0 or before.get('connectedClientCount')!=0 or mcp('ui.list').get('contexts')!=[identity]:raise SystemExit('Require only the exact approved phone and no recording activity')
if mcp('media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/VibeCaptionTest-1080i-CEA608-90s-2s.ts').get('mediaFileId')!=20905:raise SystemExit('Canonical fixture mismatch')
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');out=ROOT/'artifacts/active/WEB-023'/(stamp+'-portrait-library.json');out.parent.mkdir(parents=True,exist_ok=True)
report={'passed':False,'physicalPhone':True,'physicalFingerGesture':False,'inputRoute':'ESP32 BLE','inputReplayed':False,'syntheticSetup':['scrollIntoView','grid scroll offsets','canonical search and All view'],'rows':[]}
original=W.evaluate
class Trigger:
 def read_text(self,**_):return '__PORTRAIT_LIBRARY_FIELD__'
async def evaluate(session,expression):
 global owned
 if expression!='__PORTRAIT_LIBRARY_FIELD__':return await original(session,expression)
 async def ev(script):return await original(session,script)
 async def wait(script,label,seconds=20):
  deadline=time.monotonic()+seconds
  while time.monotonic()<deadline:
   value=await ev(script)
   if value:return value
   await asyncio.sleep(.15)
  raise RuntimeError('Timed out: '+label)
 def row(name,**values):
  report['rows'].append(dict(gate=name,passed=True,**values));print('PASS '+name,flush=True)
 async def snapshot(name):
  size=await ev('({w:innerWidth,h:innerHeight})')
  raw=await asyncio.wait_for(session.send_command('Page.snapshotRect',x=0,y=0,width=size['w'],height=size['h'],coordinateSystem='Viewport'),15)
  if 'params' in raw and 'message' in raw['params']:
   encoded=raw['params']['message']
   if len(encoded.encode())>4194304:raise RuntimeError('Snapshot bound')
   raw=json.loads(encoded)
  data=raw.get('result',{}).get('dataURL','')
  if raw.get('error') or not data.startswith('data:image/png;base64,'):raise RuntimeError('Snapshot unavailable')
  png=base64.b64decode(data.split(',',1)[1],validate=True)
  if not png.startswith(b'\x89PNG\r\n\x1a\n'):raise RuntimeError('Invalid snapshot')
  with out.with_name(out.stem+'-'+name+'.png').open('xb') as stream:stream.write(png)
 async def click(selector):
  target=await ev("(()=>{const e=document.querySelector("+json.dumps(selector)+");if(!e||e.tagName!=='BUTTON'||e.disabled||!e.getClientRects().length)throw Error('Missing explicit test button');e.scrollIntoView({block:'center',inline:'nearest'});__portrait079.target=e;__portrait079.targetId=e.getAttribute('id');e.id='fieldPortrait079';return{tag:e.tagName}})()")
  if target.get('tag')!='BUTTON':raise RuntimeError('Explicit button required')
  owner=InputOwner('192.168.10.113',(BRIDGE/'build/native-inspector/token.txt').read_text(encoding='ascii').strip())
  try:
   await owner.arm();await move_to(owner,ev,'fieldPortrait079');await owner.send('mouse',dx=0,dy=0,wheel=0,click=True,button='primary')
   await wait("window.__portrait079.events.some(e=>e.id==='fieldPortrait079')",'trusted actual button click',3)
  finally:
   report['lastPointerObservation']=getattr(owner,'last_observation',None)
   await owner.close()
   await ev("(()=>{const s=__portrait079;if(s.target){if(s.targetId===null)s.target.removeAttribute('id');else s.target.id=s.targetId;s.target=null}s.events=[];return true})()")
 installed=False
 try:
  initial=await ev("""(()=>{if(document.visibilityState!=='visible'||(localStorage.getItem('sagetvWebMiniClientId')||'').replace(/:/g,'').toLowerCase()!=='123c8282e1ee'||window.__portrait079||window.__vibeFieldHid||!document.body.classList.contains('mc-portrait-dock')||videoPlane.currentSrc)throw Error('Require idle portrait phone');const a=performance.getEntriesByType('resource').map(e=>new URL(e.name)).filter(u=>u.pathname.endsWith('/api/miniclient')&&u.searchParams.has('session'));if(!a.length)throw Error('No session');const s=window.__portrait079={session:a.at(-1).searchParams.get('session'),client:localStorage.getItem('sagetvWebMiniClientSettings.v1'),stream:localStorage.getItem('sagetvWebStreaming.v1'),top:localStorage.getItem('vibeWebApp.portraitTopPx.v1'),events:[],frames:0,done:false,point:null};window.__vibeFieldHid=s;s.listener=e=>{if(!e.isTrusted)return;if(e.type==='pointermove')s.point={x:e.clientX,y:e.clientY};else if(s.events.length<16)s.events.push({id:e.target.closest('button')?.id||'',trusted:true})};document.addEventListener('click',s.listener,true);document.addEventListener('pointermove',s.listener,true);s.cleanup=()=>{s.done=true;for(const n of ['click','pointermove'])document.removeEventListener(n,s.listener,true);if(s.target){if(s.targetId===null)s.target.removeAttribute('id');else s.target.id=s.targetId}delete window.__vibeFieldHid;delete window.__portrait079};function next(){if(s.done)return;s.frames++;videoPlane.requestVideoFrameCallback(next)}videoPlane.requestVideoFrameCallback(next);return{session:s.session,selected:document.querySelector('[role=tab][aria-selected=true]')?.id,view:document.querySelector('.mc-mobile-browse select')?.value,folders:document.querySelectorAll('.mc-mobile-folder').length}})()""");installed=True;owned=initial.pop('session')
  if initial.get('selected')!='mobileTab-recordings' or initial.get('view')!='series' or not initial.get('folders'):raise RuntimeError('Portrait did not default to grouped content')
  configured=C.request(cfg,'/SageTVWebPlayer/api/miniclient?action=streamSettings&session='+owned).get('configured')
  row('actual-content-first-default',**initial)
  await click('.mc-mobile-folder');await wait("document.querySelectorAll('.mc-mobile-item').length>0",'series items')
  row('trusted-BLE-series-folder')
  await click('.mc-mobile-item [data-content-action]');await wait("document.querySelector('.mc-mobile-list-status').textContent.includes('Information opened')",'recording Info')
  if mcp('ui.state',context=identity).get('fullyLoaded'):raise RuntimeError('Info unexpectedly started playback')
  row('trusted-BLE-recording-Info-no-Watch')
  await asyncio.sleep(.7);await snapshot('recording-info')
  await click('#mobileTab-guide');await wait("document.querySelectorAll('.mc-mobile-program').length>0&&[...document.querySelectorAll('.mc-mobile-channel img')].some(e=>e.naturalWidth>0)",'guide and actual logos')
  grid=await ev("""(()=>{const l=document.querySelector('.mc-mobile-list'),b=l.getBoundingClientRect();l.scrollLeft=500;l.scrollTop=150;const h=document.querySelector('.mc-mobile-guide-header').getBoundingClientRect(),c=document.querySelector('.mc-mobile-channel').getBoundingClientRect();return{programs:document.querySelectorAll('.mc-mobile-program').length,logos:[...document.querySelectorAll('.mc-mobile-channel img')].filter(i=>i.naturalWidth>0).length,x:l.scrollLeft,y:l.scrollTop,pinnedX:c.x>=b.x-.5,pinnedY:h.y>=b.y-.5}})()""")
  if not(grid['x']>0 and grid['y']>0 and grid['pinnedX'] and grid['pinnedY']):raise RuntimeError('Guide scroll/header failure')
  row('actual-two-axis-guide-and-decoded-logos-synthetic-scroll',**grid)
  await snapshot('guide-scrolled')
  await ev("(()=>{const l=document.querySelector('.mc-mobile-list');l.scrollLeft=0;l.scrollTop=0;return true})()")
  await click('.mc-mobile-program');detail=await ev("(()=>{const e=document.querySelector('.mc-mobile-guide-details'),b=e.getBoundingClientRect();return{visible:!e.hidden,x:b.x,y:b.y,w:b.width,h:b.height,inside:b.y>=0&&b.bottom<=innerHeight+.5}})()")
  if not(detail['visible'] and detail['inside']):raise RuntimeError('Program details clipped')
  row('trusted-BLE-guide-details-fit-phone',**detail)
  await click('.mc-mobile-guide-details [data-content-action]:last-child');await wait("document.querySelector('.mc-mobile-list-status').textContent.includes('Information opened')",'guide Info')
  if mcp('ui.state',context=identity).get('fullyLoaded'):raise RuntimeError('Guide Info tuned playback')
  row('trusted-BLE-guide-Info-no-tune')
  await asyncio.sleep(.7);await snapshot('guide-info')
  await click('.mc-mobile-detail-close');await wait("document.querySelector('.mc-mobile-guide-details').hidden",'return to guide')
  await click('#mobileTab-videos');await wait("document.querySelectorAll('.mc-mobile-folder').length>0",'import folders')
  await click('.mc-mobile-folder');row('trusted-BLE-import-folder')
  await ev("""(()=>{const g=document.querySelector('.mc-mobile-browse select');g.value='all';g.dispatchEvent(new Event('change',{bubbles:true}));const f=document.querySelector('.mc-mobile-search');f.querySelector('input').value='VibeCaptionTest-1080i-CEA608-90s-2s';f.requestSubmit();return{syntheticCanonicalSearch:true}})()""")
  await wait("document.querySelectorAll('.mc-mobile-item').length===1&&document.querySelector('.mc-mobile-item strong').textContent==='VibeCaptionTest-1080i-CEA608-90s-2s'",'exact canonical result')
  await click('.mc-mobile-item [data-content-action]');await wait("document.querySelector('.mc-mobile-list-status').textContent.includes('Information opened')",'video Info')
  row('trusted-BLE-import-Info')
  await asyncio.sleep(.7);await snapshot('video-info')
  await click('.mc-mobile-item [data-content-play]');await wait("!!videoPlane.currentSrc",'one production Watch',35)
  if await ev("!autoplayBtn.hidden"):await click('#autoplayBtn');row('trusted-BLE-Safari-Play-activation')
  picture=await wait("(()=>{const s=__portrait079,v=videoPlane;return !v.paused&&v.videoWidth>0&&s.frames>10?{frames:s.frames,time:v.currentTime,width:v.videoWidth}:null})()",'new presented canonical pictures',35)
  native=mcp('ui.state',context=identity)
  if (native.get('media') or {}).get('mediaFileId')!=20905:raise RuntimeError('Wrong played source')
  layout=C.request(cfg,'/SageTVWebPlayer/api/miniclient?action=contentState&session='+owned+'&mediaId=20905')
  if not(layout.get('ready') and layout.get('layout')=='fullscreen'):raise RuntimeError('Native playback stayed windowed')
  row('trusted-BLE-canonical-Play-fullscreen-new-frames',**picture)
  preserved=await ev("(()=>{const s=__portrait079;return s.client===localStorage.getItem('sagetvWebMiniClientSettings.v1')&&s.stream===localStorage.getItem('sagetvWebStreaming.v1')&&s.top===localStorage.getItem('vibeWebApp.portraitTopPx.v1')})()")
  if not preserved or C.request(cfg,'/SageTVWebPlayer/api/miniclient?action=streamSettings&session='+owned).get('configured')!=configured:raise RuntimeError('Saved profiles changed')
  row('saved-browser-and-server-profiles-preserved');report['passed']=True
  return {'passed':True,'rows':len(report['rows'])}
 finally:
  if installed:report['observerRemoved']=await ev("(()=>{__portrait079.cleanup();return !window.__portrait079})()")
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,page_id=None,verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,screenshot=out.with_suffix('.png'))
async def run():
 async def attached(rsd,data):await W.inspect(rsd,data,args)
 await W.probe(args,report,on_rsd=attached)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
try:asyncio.run(asyncio.wait_for(run(),180))
except Exception as error:report.update(passed=False,errorType=type(error).__name__,error=str(error)[:200] if isinstance(error,RuntimeError) else 'Observation failure; no replay')
finally:
 W.evaluate=original
 with out.open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2)
print(json.dumps({'passed':report['passed'],'rows':len(report['rows']),'error':report.get('error'),'report':str(out)}));raise SystemExit(0 if report['passed'] else 1)
