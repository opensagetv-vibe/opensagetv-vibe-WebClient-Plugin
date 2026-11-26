#!/usr/bin/env python3
"""One fresh native DVD Audio Change; observe selector/consumer without replay.

This distinguishes stock command delivery, conversion mapping and presentation.
MCP is existing public test setup only. No saved settings/Core/plugin changes.
"""
import asyncio,importlib.util,json,logging,sys,time
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];BRIDGE=ROOT.parent/'ESP32-IOS-Bridge'
sys.path.insert(0,str(BRIDGE/'tools/native_inspector'))
import wireless_inspect as W
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
identity='123c8282e1ee';stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
out=ROOT/'artifacts/active/WEB-014';out.mkdir(parents=True,exist_ok=True)
report=dict(utc=datetime.now(timezone.utc).isoformat(),passed=False,physicalPhone=True,
 navigation='Existing public MCP setup',inputReplayed=False,samples=[])
def mcp(action,**v):return C.request(cfg,'/v1/control',dict(action=action,**v),mcp=True,timeout=8)
def guard():
 a=C.activity(cfg)
 if a.get('recordingCount')!=0 or a.get('connectedClientCount')!=0 or mcp('ui.list').get('contexts')!=[identity]:raise RuntimeError('Require exact phone/no recordings')
def command(name):
 guard()
 if not mcp('ui.command',context=identity,command=name).get('accepted'):raise RuntimeError('Command not accepted; no replay')
original=W.evaluate
class Trigger:
 def read_text(self,**_):return '__INPLACE_DVD_AUDIO_PROBE__'
async def evaluate(session,expression):
 if expression!='__INPLACE_DVD_AUDIO_PROBE__':return await original(session,expression)
 async def ev(s):return await original(session,s)
 async def sample():
  await ev("(()=>{const s=window.__audioProbe;s.pending=true;__iphoneGate.api('status').then(j=>s.dvd=j.connection?.dvd).catch(()=>s.error=true).finally(()=>s.pending=false);return true;})()")
  for _ in range(60):
   if not await ev('window.__audioProbe.pending'):break
   await asyncio.sleep(.05)
  v=await ev("(()=>{const s=window.__audioProbe;return{sourceChanged:videoPlane.currentSrc!==s.before,time:videoPlane.currentTime,paused:videoPlane.paused,ready:videoPlane.readyState,blocked:!autoplayBtn.hidden,error:s.error,dvd:s.dvd};})()")
  return v,await asyncio.to_thread(mcp,'ui.state',context=identity)
 installed=False
 try:
  guard()
  await ev("(()=>{if(!__iphoneGate?.api||window.__audioProbe||document.visibilityState!=='visible')throw Error('Owner unavailable');window.__audioProbe={before:videoPlane.currentSrc};return true;})()");installed=True
  if not (await asyncio.to_thread(mcp,'media.watch',context=identity,media_id=20819,wait_ms=0)).get('accepted'):raise RuntimeError('Fixture Watch rejected')
  deadline=time.monotonic()+60
  while time.monotonic()<deadline:
   v,n=await sample()
   if n.get('dvd') and (n.get('media') or {}).get('mediaFileId')==20819 and v.get('sourceChanged') and v.get('ready',0)>=2:break
   await asyncio.sleep(.15)
  else:raise RuntimeError('Fresh authored picture unavailable')
  if not n.get('dvdMenu'):
   await asyncio.to_thread(command,'DVD Menu')
   for _ in range(100):
    v,n=await sample()
    if n.get('dvdMenu'):break
    await asyncio.sleep(.1)
   else:raise RuntimeError('Root unavailable')
  await ev('(()=>{__audioProbe.before=videoPlane.currentSrc;return true;})()')
  await asyncio.to_thread(command,'Select')
  deadline=time.monotonic()+45
  while time.monotonic()<deadline:
   v,n=await sample()
   if v['blocked']:raise RuntimeError('Real Play gesture required')
   if not n.get('dvdMenu') and v['sourceChanged'] and not v['paused'] and v['ready']>=2 and v['time']>.3:break
   await asyncio.sleep(.1)
  else:raise RuntimeError('Fresh feature unavailable')
  if (v.get('dvd') or {}).get('audioSelector')!='AC3 wire=0xbd80 ffmpegId=0x80':raise RuntimeError('Require known English fixture start')
  report['before']=v
  await ev('(()=>{__audioProbe.before=videoPlane.currentSrc;return true;})()')
  await asyncio.to_thread(command,'DVD Audio Change')
  start=time.monotonic()
  while time.monotonic()-start<20:
   v,n=await sample();report['samples'].append(dict(elapsedMs=round((time.monotonic()-start)*1000),video=v,nativeTimeMs=n.get('mediaTimeMs'),dvdMenu=n.get('dvdMenu')))
   if (v.get('dvd') or {}).get('audioSelector')=='AC3 wire=0xbd81 ffmpegId=0x81' and v['sourceChanged'] and not v['paused'] and v['ready']>=2:
    report.update(passed=True,status='NATIVE_SELECTOR_AND_NEW_CONSUMER_OBSERVED_AUDIO_IDENTITY_STILL_REQUIRES_HDMI');break
   await asyncio.sleep(.25)
  if not report['passed']:
   report['status']='NO_QUALIFIED_INPLACE_SWITCH_OBSERVED'
   raise RuntimeError('No qualified native selector/new-consumer switch; no replay')
  return dict(passed=report['passed'],status=report['status'],samples=len(report['samples']))
 finally:
  if installed:report['observerCleanup']=await ev('(()=>{delete window.__audioProbe;return!window.__audioProbe;})()')
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,page_id=None,verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,screenshot=None)
async def run():
 async def attached(rsd,data):await W.inspect(rsd,data,args)
 await W.probe(args,report,on_rsd=attached)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
try:asyncio.run(asyncio.wait_for(run(),180))
except Exception as e:report.update(passed=False,errorType=type(e).__name__,error=str(e)[:250] if isinstance(e,RuntimeError) else 'Observation unavailable; no replay')
finally:
 W.evaluate=original
 with (out/(stamp+'-inplace-audio-phone.json')).open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps(dict(passed=report['passed'],status=report.get('status'),error=report.get('error')))+'\n'+str(out/(stamp+'-inplace-audio-phone.json')))
raise SystemExit(0 if report['passed'] else 1)
