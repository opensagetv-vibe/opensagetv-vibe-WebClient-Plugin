#!/usr/bin/env python3
"""WEB-121 bounded read-only phone asset/session evidence; no playback commands."""
import json,re,runpy,shlex,time
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
ROOT=Path(__file__).resolve().parents[1]
c=runpy.run_path(str(ROOT/'scripts/commission-mobile.py'));cfg=c['configuration']()
with c['ssh'](cfg) as ssh:
    name='/opt/sagetv/server/jetty/logs/'+time.strftime('%Y_%m_%d',time.gmtime())+'.request.log'
    log=c['remote'](ssh,'docker exec '+shlex.quote(cfg['unraid_container_name'])+' tail -n 18000 '+shlex.quote(name))
assets=[];sessions=[];last_calls=[]
for line in log.splitlines():
    if 'iPhone' not in line:continue
    parts=line.split('"')
    if len(parts)<4:continue
    request=parts[1].split()
    if len(request)!=3:continue
    method,uri,_=request;u=urlsplit(uri);q=parse_qs(u.query)
    at=re.search(r'\[([^]]+)\]',parts[0]);status=parts[2].strip().split()[0]
    row={'at':at.group(1) if at else 'unknown','method':method,'path':u.path,'status':status}
    if method=='GET' and (u.path.endswith(('/miniclient.html','/sw.js')) or '/js/miniclient' in u.path):
        row['revision']=q.get('v',['none'])[0];assets.append(row)
    if '/api/miniclient' in u.path and q.get('session'):
        sessions.extend(q['session'])
    if '/api/' in u.path:row['action']=q.get('action',['none'])[0];last_calls.append(row)
current=[]
for sid in list(dict.fromkeys(sessions))[-20:]:
    try:
        state=c['request'](cfg,'/SageTVWebPlayer/api/miniclient?action=status&session='+sid)
        if state.get('clientId','').replace(':','').lower()!='123c8282e1ee':continue
        connection=state.get('connection',{})
        playback=c['request'](cfg,'/SageTVWebPlayer/api/miniclient?action=playbackState&session='+sid)
        current.append({'session':sid,'alive':state.get('alive'),'error':state.get('error'),
            'phase':connection.get('phase'),'lastTransportError':connection.get('lastTransportError'),
            'playback':playback})
    except RuntimeError:pass
report={'activity':c['activity'](cfg),'phoneAssets':assets[-32:],'lastPhoneCalls':last_calls[-12:],'phoneSessions':current}
out=ROOT/'artifacts/active/WEB-121';out.mkdir(parents=True,exist_ok=True)
path=out/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-phone-recovery.json')
path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2));print(str(path.relative_to(ROOT)))
