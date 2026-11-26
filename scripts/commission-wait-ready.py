#!/usr/bin/env python3
"""Bounded read-only post-restart readiness, not a replay of ordered actions."""
import importlib.util,json,time
from pathlib import Path
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',root/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
deadline=time.monotonic()+90;last=None
while time.monotonic()<deadline:
    try:
        health=C.request(cfg,'/health',mcp=True,timeout=3)
        web=C.request(cfg,'/SageTVWebPlayer/api/health',timeout=3)
        activity=C.activity(cfg)
        if health.get('status')=='ok' and web.get('ok'):
            print(json.dumps({'ready':True,'mcpVersion':health.get('version'),'webVersion':web.get('version'),'activity':activity}));break
        last='Unready health'
    except Exception as error:last=type(error).__name__
    time.sleep(2)
else:raise SystemExit('Readiness timeout; activity UNKNOWN; last '+str(last))
