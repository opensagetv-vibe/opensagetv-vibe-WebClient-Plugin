#!/usr/bin/env python3
"""One bounded MCP JVM snapshot; stock232 test phone only, no shell/signals."""
import argparse,importlib.util,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(sp);sp.loader.exec_module(C);cfg=C.configuration()
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--client-id',choices=['123c8282e1ee','da92a86446be'],default='123c8282e1ee')
parser.add_argument('--task',choices=['WEB-049','WEB-064','WP11-008'],default='WEB-049')
options=parser.parse_args()
activity=C.activity(cfg)
contexts=C.request(cfg,'/v1/control',{'action':'ui.list'},mcp=True).get('contexts')
if activity.get('recordingCount')!=0 or activity.get('connectedClientCount')!=0 or contexts!=[options.client_id]:
    raise RuntimeError('Require exact phone/no recordings or other clients for diagnostic load')
result=C.request(cfg,'/v1/control',{'action':'diagnostics.threads'},mcp=True)
if not result.get('ok') or result.get('schemaVersion')!=1:raise RuntimeError('Bounded diagnostic unavailable')
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
out=ROOT/'artifacts/active'/options.task/(stamp+'-stock232-threads.json')
out.parent.mkdir(parents=True,exist_ok=True)
with out.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'threadSnapshot':str(out),'threads':len(result['threads']),'total':result['totalThreads'],'truncated':result['truncated']}))
