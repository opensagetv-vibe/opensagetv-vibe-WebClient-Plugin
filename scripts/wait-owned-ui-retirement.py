#!/usr/bin/env python3
"""Bounded independent observation only; never repeats Stop or replaces a UI."""
import argparse,importlib.util,json,re,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser(description=__doc__);p.add_argument('identity');a=p.parse_args()
if not re.fullmatch('[0-9a-f]{12}',a.identity):p.error('Exact test identity required')
deadline=time.monotonic()+95;start=time.monotonic()
while True:
 activity=C.activity(cfg);contexts=C.request(cfg,'/v1/control',{'action':'ui.list'},mcp=True).get('contexts',[])
 if activity.get('recordingCount')!=0 or activity.get('connectedClientCount')!=0 or any(x!=a.identity for x in contexts):
  raise SystemExit('Other activity or UNKNOWN; no replay/interruption')
 if not contexts and activity.get('uiContextCount')==0:
  print(json.dumps({'retired':True,'secondsObserved':round(time.monotonic()-start,3),'activity':activity}));break
 if time.monotonic()>deadline:raise SystemExit('Owned native UI retirement unverified; no replay')
 time.sleep(.5)
