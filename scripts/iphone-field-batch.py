#!/usr/bin/env python3
"""Serial, exact-page iPhone field probes using the existing paired bridge.

Keeps one verified inspector attachment for a bounded batch. Every expression
retains the bridge's 2048-byte/exact-URL guard and userGesture=False. A timeout
is a failed action, never permission to replay controls. This is synthetic DOM
input on the real phone, not proof of physical gestures or native OS dialogs.
Run with ESP32-IOS-Bridge/.venv-pymobiledevice3/Scripts/python.exe.
"""
import argparse,asyncio,json,logging,sys,subprocess
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'ESP32-IOS-Bridge/tools/native_inspector'))
import wireless_inspect as W

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--task',choices=['WEB-023','WEB-049'],required=True)
p.add_argument('--step',action='append',required=True,help='iphone-*.js[:settle_seconds], sequential/no replay')
p.add_argument('--snapshot',action='store_true')
p.add_argument('--page-id',type=int,help='Explicit discovered exact-URL page; still requires fresh visible nonce/identity proof')
p.add_argument('--thread-dump-after-tap',action='store_true',help='One bounded authenticated MCP JVM snapshot after the exact live test tap')
a=p.parse_args();steps=[]
if a.page_id is not None and not 1<=a.page_id<=65535:p.error('Invalid discovered page ID')
for value in a.step:
    name,sep,delay=value.partition(':');path=ROOT/'tests'/name
    if not name.startswith('iphone-') or Path(name).name!=name or not name.endswith('.js'):
        p.error('Only explicit owning tests/iphone-*.js probes are allowed')
    script=path.read_text(encoding='utf-8');seconds=float(delay) if sep else 0
    if not 0<=seconds<=30 or not 0<len(script.encode('utf-8'))<=2048:p.error('Probe/delay exceeds bound')
    steps.append((name,script,seconds))
if sum(row[2] for row in steps)>120 or len(steps)>30:p.error('Batch exceeds bound')
if a.thread_dump_after_tap and (a.task!='WEB-049' or sum(n=='iphone-timeline-tap-live.js' for n,_,_ in steps)!=1):p.error('Requires exactly one WEB-049 live test tap')
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
out=ROOT/'artifacts/active'/a.task;out.mkdir(parents=True,exist_ok=True)
report={'utc':datetime.now(timezone.utc).isoformat(),'passed':False,'physicalPhone':True,
        'inputEvidence':'synthetic DOM unless explicitly user-confirmed','steps':[]}
original=W.evaluate
class Trigger:
    def read_text(self,**_):return '__OWNED_IPHONE_FIELD_BATCH__'
async def evaluate(session,expression):
    if expression!='__OWNED_IPHONE_FIELD_BATCH__':return await original(session,expression)
    for name,script,delay in steps:
        value=await original(session,script)
        row={'probe':name,'result':value};report['steps'].append(row)
        print(json.dumps(row),flush=True)
        if a.thread_dump_after_tap and name=='iphone-timeline-tap-live.js':
            await asyncio.sleep(.7)
            result=await asyncio.to_thread(subprocess.run,['py','-3.12',str(ROOT/'scripts/iphone-server-threads.py')],capture_output=True,text=True,timeout=30)
            report['threadDiagnostic']={'exitCode':result.returncode,'summary':result.stdout[-1000:]}
            print(json.dumps(report['threadDiagnostic']),flush=True)
        if delay:await asyncio.sleep(delay)
    return {'stepsCompleted':len(report['steps'])}
W.evaluate=evaluate
args=SimpleNamespace(interface_ip='192.168.10.66',phone_ip='192.168.10.107',udid=None,
    page_id=a.page_id,verify_usb_disconnected=False,expression_file=Trigger(),menu_check=False,
    screenshot=out/(stamp+'-iphone-field.png') if a.snapshot else None)
logging.getLogger('pymobiledevice3').setLevel(logging.CRITICAL)
async def run():
    async def attached(rsd,data):await W.inspect(rsd,data,args)
    await W.probe(args,report,on_rsd=attached)
try:asyncio.run(asyncio.wait_for(run(),180))
except Exception as e:
    report.update(passed=False,errorType=type(e).__name__)
    if isinstance(e,(RuntimeError,ValueError)):report['error']=str(e)[:300]
finally:
    with (out/(stamp+'-iphone-field.json')).open('x',encoding='utf-8') as f:
        json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({'passed':report['passed'],'steps':len(report['steps']),'report':str(out/(stamp+'-iphone-field.json'))}),flush=True)
raise SystemExit(0 if report['passed'] else 1)
