#!/usr/bin/env python3
"""One guarded stock232 restart for the pending normal-manager dependency.

Never retries a restart. Readiness observation is a separate read-only helper.
"""
import argparse,importlib.util,json,shlex
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task',choices=('WP08-006','WEB-097','WEB-098','WEB-099'),default='WP08-006')
    args=parser.parse_args()
    cfg=C.configuration();report=dict(orderedRestartSubmitted=False)
    out=ROOT/'artifacts/active'/args.task/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-dependency-restart.json')
    out.parent.mkdir(parents=True,exist_ok=True)
    try:
        with C.ssh(cfg) as client:
            container=shlex.quote(cfg['unraid_container_name'])
            protected=C.remote(client,'docker exec -w /opt/sagetv/server '+container+' sha256sum -c /usr/local/share/sagetv-stock/protected.sha256')
            report['protectedStockFiles']=protected.count(': OK')
            processes=C.remote(client,'docker exec '+container+' ps -eo comm').splitlines()
            if any(p.strip() in ('ffmpeg','ffmpeg.real','SageTVTranscoder','ffmpeg_MIM') for p in processes):raise RuntimeError('Active encoder; preserve work')
            guard=C.activity(cfg);report['preRestartActivity']=guard
            if report['protectedStockFiles']!=20 or not guard.get('safeToRestart') or any(guard.get(k)!=0 for k in ('recordingCount','uiContextCount','connectedClientCount')):raise RuntimeError('Independent idle proof required')
            report['orderedRestartSubmitted']=True
            C.remote(client,'docker restart '+container)
            report['restartReturned']=True
    finally:
        with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
    print(json.dumps(dict(restartReturned=report.get('restartReturned',False),report=str(out))))
if __name__=='__main__':main()
