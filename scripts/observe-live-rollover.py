#!/usr/bin/env python3
"""WEB-120 read-only current phone/producer observation; never retunes playback."""
import argparse,importlib.util,json,re,shlex
from datetime import datetime,timezone
from pathlib import Path
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',root/'scripts/commission-mobile.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);cfg=c.configuration()
p=argparse.ArgumentParser();p.add_argument('--client-id',default='123c8282e1ee');args=p.parse_args()
with c.ssh(cfg) as ssh:
    logfile='/opt/sagetv/server/jetty/logs/'+datetime.now(timezone.utc).strftime('%Y_%m_%d')+'.request.log'
    log=c.remote(ssh,'docker exec '+shlex.quote(cfg['unraid_container_name'])+' tail -n 2500 '+shlex.quote(logfile))
ids=list(dict.fromkeys(re.findall(r'[?&]session=([a-zA-Z0-9_-]+)',log)))
print(json.dumps({'activity':c.activity(cfg),'client':c.request(cfg,'/v1/control',{'action':'ui.state','context':args.client_id},mcp=True)}))
for sid in ids[-20:]:
    try:
        state=c.request(cfg,'/SageTVWebPlayer/api/miniclient?action=status&session='+sid)
        if state.get('clientId','').replace(':','').lower()!=args.client_id.replace(':','').lower():continue
        playback=c.request(cfg,'/SageTVWebPlayer/api/miniclient?action=playbackState&session='+sid)
        producer=c.request(cfg,'/SageTVWebPlayer/api/hls?session='+playback['producer']) if playback.get('producer') else None
        print(json.dumps({'session':sid,'playback':playback,'producer':producer}))
    except RuntimeError:
        pass
