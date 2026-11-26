#!/usr/bin/env python3
"""Bounded read-only CC marker summary; never export caption text or raw logs."""
import argparse,importlib.util,json,shlex,re,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
out=a.output.resolve();base=(ROOT/'artifacts/active/WP05-003').resolve()
if out.exists() or not out.is_relative_to(base):raise ValueError('Fresh owning WP05-003 output required')
if C.activity(cfg).get('recordingCount')!=0:raise RuntimeError('Unrelated recording activity')
with C.ssh(cfg) as client:
    raw=C.remote(client,'docker exec '+shlex.quote(cfg['unraid_container_name'])+' tail -c 2097152 /opt/sagetv/server/sagetv_0.txt')
if len(raw)>2*1024*1024:raise RuntimeError('Log exceeds bound')
needles=('Got CC data packet of type:','CC PARITY check failed','CC CHANNEL switched','Skip CC data; wrong channel','VF is updating the CC text now','VF ttu for cc=','Got CC data of 0x','CLEARING the CC display','CC ROLL UP MODE','POP-ON CAPTIONS Resume','DONE loading the captions','CC carriage return')
controls=collections.Counter()
for first,second in re.findall(r'Got CC data of 0x([0-9a-f]{1,2}) 0x([0-9a-f]{1,2})',raw):
    if 0x10<=int(first,16)<0x20:controls[first+':'+second]+=1
value=dict(readOnly=True,scope='Last2MiBserver log; may include earlier trace history, not visual proof',counts={s:raw.count(s) for s in needles},controlCodes=dict(controls),rawLogExported=False)
out.parent.mkdir(parents=True,exist_ok=True)
with out.open('x',encoding='utf-8') as f:json.dump(value,f,indent=2);f.write('\n')
print(json.dumps(value))
