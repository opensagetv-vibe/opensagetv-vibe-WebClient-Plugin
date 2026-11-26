#!/usr/bin/env python3
"""Bounded read-only owning-plugin log excerpt on the commissioned test server."""
import importlib.util,json,shlex
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
if C.activity(cfg).get('recordingCount')!=0:raise RuntimeError('Do not inspect unrelated active recordings')
with C.ssh(cfg) as client:
    raw=C.remote(client,'docker exec '+shlex.quote(cfg['unraid_container_name'])+' tail -n 800 /opt/sagetv/server/sagetv_0.txt')
    if len(raw)>1024*1024:raise RuntimeError('Log read exceeds bound')
    lines=[line[:600] for line in raw.splitlines() if '[VibeClientExtension]' in line][-60:]
print(json.dumps(dict(readOnly=True,scope='Owning plugin only; last800server lines/max60matches',lines=lines),indent=2))
