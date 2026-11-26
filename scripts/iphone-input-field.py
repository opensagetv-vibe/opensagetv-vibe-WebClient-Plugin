#!/usr/bin/env python3
"""Actual phone special-key editor, foreground HID and firmware-idle evidence.

One harmless Info mapping, exact restoration, no recording Delete or OS text.
Synthetic focus/editor setup is explicit; delivery uses real encrypted BLE.
"""
import asyncio,importlib.util,json,logging,sys,time
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
sys.path.insert(0,str(BRIDGE/'tools/native_inspector'))
import wireless_inspect as W
from field_hid import InputOwner
from ble_hid import call
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
out=ROOT/'artifacts/active/WEB-023';out.mkdir(parents=True,exist_ok=True)
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');path=out/(stamp+'-iphone-input.json')
report=dict(passed=False,physicalPhone=True,physicalFingerGesture=False,syntheticFocusAndEditorSetup=True,rows=[],cleanup=[])
def save():path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
def guard():
 activity=C.activity(cfg);uis=C.request(cfg,'/v1/control',dict(action='ui.list'),mcp=True)
 if activity.get('recordingCount')!=0 or activity.get('connectedClientCount')!=0 or uis.get('contexts')!=['123c8282e1ee']:raise RuntimeError('Require exact phone and no unrelated activity')
 n=C.request(cfg,'/v1/control',dict(action='ui.state',context='123c8282e1ee'),mcp=True)
 if n.get('fullyLoaded') or n.get('loading'):raise RuntimeError('Preserve active media')
original=W.evaluate
class Trigger:
 def read_text(self,**_):return '__PHONE_INPUT_FIELD__'
async def evaluate(session,expression):
 if expression!='__PHONE_INPUT_FIELD__':return await original(session,expression)
 async def ev(code):return await original(session,code)
 token=(BRIDGE/'build/native-inspector/token.txt').read_text().strip();owner=InputOwner('192.168.10.113',token);installed=False
 async def key(value):
  await asyncio.to_thread(guard);await owner.arm();await owner.send('key',key=value);await owner.close();await asyncio.sleep(.25)
 async def edit(value):
  return await ev("(()=>{const s=__phoneInput;if(s.borrowed!==undefined&&localStorage.getItem('sagetvWebInput.v1')!==s.borrowed)throw Error('Preserve changed mapping');if(remotePanel.hidden)remoteToggle.click();remoteSettings.click();document.querySelector('[data-settings-page=input]').click();mappingContext.value='default';mappingContext.dispatchEvent(new Event('change'));mappingKey.value='Delete';mappingKey.dispatchEvent(new Event('change'));mappingPress.value="+json.dumps(value)+";mappingPress.dispatchEvent(new Event('change'));s.borrowed=localStorage.getItem('sagetvWebInput.v1');for(let i=0;i<4&&!settingsPanel.hidden;i++)closeSettings.click();if(!remotePanel.hidden)hideRemote.click();stage.focus();return document.activeElement===stage})()")
 try:
  await asyncio.to_thread(guard)
  await ev("(()=>{if(document.visibilityState!=='visible'||videoPlane.getAttribute('src')||videoPlane.readyState)throw Error('Preserve active media');if(remotePanel.hidden)remoteToggle.click();nav_home.click();if(!remotePanel.hidden)hideRemote.click();return true})()")
  await asyncio.sleep(1)
  await ev("(()=>{if(document.visibilityState!=='visible'||window.__phoneInput||videoPlane.getAttribute('src')||videoPlane.readyState||keyboardInput.value)throw Error('Visible unloaded phone and empty draft required');const s=window.__phoneInput={raw:localStorage.getItem('sagetvWebInput.v1'),client:localStorage.getItem('sagetvWebMiniClientSettings.v1'),stream:localStorage.getItem('sagetvWebStreaming.v1'),commands:[],events:[],moves:0};s.original=SageMiniInput.normalize(JSON.parse(s.raw||'{}'));s.fetch=window.fetch;s.observed=function(input,o){const u=new URL(typeof input==='string'?input:input instanceof URL?input.href:input.url,location.href);if(u.origin===location.origin&&u.pathname.endsWith('/api/miniclient')&&u.searchParams.get('action')==='command')s.commands.push(Number(new URLSearchParams(o?.body||'').get('command')));return s.fetch.apply(this,arguments)};window.fetch=s.observed;s.listener=e=>{if(!e.isTrusted)return;if(e.type==='pointermove')s.moves++;else if(s.events.length<64)s.events.push({type:e.type,key:e.key==='Delete'?'Delete':e.key==='Backspace'?'Backspace':e.key==='q'?'test-character':'other',target:e.target.id||''})};for(const t of ['keydown','keyup','input','pointermove'])document.addEventListener(t,s.listener,true);return true})()");installed=True
  # Persist originals locally before any production mapping change.
  private=await ev('({input:__phoneInput.raw,client:__phoneInput.client,stream:__phoneInput.stream})')
  with (out/(stamp+'-input-checkpoint.private.json')).open('x',encoding='utf-8') as f:json.dump(private,f)
  await edit('24');await key('delete')
  observed=await ev('({commands:__phoneInput.commands.slice(),events:__phoneInput.events.slice()})')
  if observed['commands']!=[24] or not all(any(e['type']==kind and e['key']=='Delete' for e in observed['events']) for kind in ('keydown','keyup')):raise RuntimeError('Real mapped Delete delivery not verified; no replay')
  report['rows'].append(dict(gate='real-Delete-mapped-once-to-harmless-Info',observed=observed));save()
  await edit('none');await key('delete')
  if await ev('__phoneInput.commands.join()')!='24':raise RuntimeError('Explicit disabled key escaped')
  report['rows'].append(dict(gate='real-Delete-explicit-none-no-command'));save()
  await ev("(()=>{if(remotePanel.hidden)remoteToggle.click();keyboardToggle.click();keyboardInput.focus();return document.activeElement===keyboardInput})()")
  await key('q')
  report['textObservation']=await ev("({oneTestCharacter:/^[qQ]$/.test(keyboardInput.value),capitalized:keyboardInput.value==='Q',commands:__phoneInput.commands.slice(),trustedEvents:__phoneInput.events.slice()})");save()
  if not report['textObservation']['oneTestCharacter'] or report['textObservation']['commands']!=[24]:raise RuntimeError('Foreground text/ownership failed')
  await key('backspace')
  if not await ev("keyboardInput.value===''&&__phoneInput.commands.join()==='24'"):raise RuntimeError('Editable Backspace leaked')
  report['rows'].append(dict(gate='real-printable-and-Backspace-stay-in-local-empty-draft'));save()
  await ev("(()=>{keyboardInput.blur();if(!remotePanel.hidden)hideRemote.click();return true})()")
  # A pointer parked in Safari's edge chrome cannot generate page events.
  # Bounded relative re-positioning is explicit test setup, never a click,
  # guessed absolute location, replay of an uncertain command or touch event.
  await owner.arm()
  for dx,dy in ((100,100),(-200,-200),(200,100),(-100,100)):
   await owner.send('mouse',dx=dx,dy=dy,wheel=0,click=False);await asyncio.sleep(.3)
   if await ev('__phoneInput.moves')>0:break
  await owner.close()
  if await ev('__phoneInput.moves')<1:raise RuntimeError('Trusted pointer delivery absent after bounded repositioning')
  report['rows'].append(dict(gate='trusted-relative-pointer-delivery'));save()
  before=await asyncio.to_thread(call,owner.host,token,'status')
  if not(before.get('firmwareKeepAwakeEnabled') and before.get('connected') and before.get('secure') and before.get('activeInputSessions')==0):raise RuntimeError('Require existing firmware keeper and zero input leases')
  moves=await ev('__phoneInput.moves');began=time.monotonic()
  while time.monotonic()-began<75:
   await asyncio.sleep(5)
   status=await asyncio.to_thread(call,owner.host,token,'status')
   view=await ev('({visible:document.visibilityState,moves:__phoneInput.moves})')
   if not(status.get('connected') and status.get('secure') and status.get('activeInputSessions')==0 and view['visible']=='visible'):raise RuntimeError('Idle coexistence changed; no rearm/unlock')
   if status.get('keepAwakeJiggles',0)>before.get('keepAwakeJiggles',0) and view['moves']>moves:
    report['rows'].append(dict(gate='firmware-idle-trusted-pointer-zero-host-input-leases',secondsObserved=round(time.monotonic()-began,2),jiggles=status['keepAwakeJiggles']-before['keepAwakeJiggles']));break
  else:raise RuntimeError('Firmware idle delivery not observed')
  report['passed']=True
 finally:
  await owner.close()
  if installed:
   try:
    report['draftRestored']=await ev("(()=>{if(keyboardInput.value==='')return true;if(/^[qQ]$/.test(keyboardInput.value)){keyboardInput.value='';return true}throw Error('Preserve unexpected local draft')})()")
   except Exception:report['cleanup'].append('Unexpected local draft preserved')
   try:
    restore=await ev("(()=>{const s=__phoneInput;return s.original.keys.default.Delete||'default'})()")
    await edit(restore)
    report['exactProfilesRestored']=await ev("(()=>{const s=__phoneInput;if(localStorage.getItem('sagetvWebInput.v1')!==s.borrowed)throw Error('Preserve changed mapping');if(s.raw===null)localStorage.removeItem('sagetvWebInput.v1');else localStorage.setItem('sagetvWebInput.v1',s.raw);return localStorage.getItem('sagetvWebInput.v1')===s.raw&&localStorage.getItem('sagetvWebMiniClientSettings.v1')===s.client&&localStorage.getItem('sagetvWebStreaming.v1')===s.stream})()")
    if not report['exactProfilesRestored']:raise RuntimeError('Profile mismatch')
   except Exception:report['cleanup'].append('Mapping restoration unknown; preserve private checkpoint')
   try:report['observerRestored']=await ev("(()=>{const s=__phoneInput;if(window.fetch!==s.observed)throw Error('Observer owner changed');window.fetch=s.fetch;for(const t of ['keydown','keyup','input','pointermove'])document.removeEventListener(t,s.listener,true);delete window.__phoneInput;return true})()")
   except Exception:report['cleanup'].append('Observer restoration unknown')
  report['passed']=report['passed'] and not report['cleanup'];save()
 return dict(passed=report['passed'],rows=len(report['rows']))
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,page_id=None,verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,screenshot=None)
async def run():
 async def attached(rsd,data):await W.inspect(rsd,data,args)
 await W.probe(args,report,on_rsd=attached)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
try:asyncio.run(asyncio.wait_for(run(),210))
except Exception as e:report.update(passed=False,errorType=type(e).__name__,error=str(e)[:220] if isinstance(e,RuntimeError) else 'Bounded observation unavailable; no replay')
finally:W.evaluate=original;save()
print(json.dumps(dict(passed=report['passed'],rows=len(report['rows']),error=report.get('error'),cleanup=report['cleanup'],report=str(path))));raise SystemExit(0 if report['passed'] else 1)
