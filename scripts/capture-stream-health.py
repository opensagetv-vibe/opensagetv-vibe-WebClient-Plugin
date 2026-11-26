#!/usr/bin/env python3
"""WEB-121 bounded read-only retained/current producer snapshot, including after close."""
import json,runpy,time
from pathlib import Path
root=Path(__file__).resolve().parents[1];c=runpy.run_path(str(root/'scripts/commission-mobile.py'));cfg=c['configuration']()
history=c['request'](cfg,'/SageTVWebPlayer/api/support?action=streamHealth');producers=[]
for owner in history.get('sessions',[]):
    try:producers.append(c['request'](cfg,'/SageTVWebPlayer/api/hls?session='+owner['session']))
    except RuntimeError:pass
report={'activity':c['activity'](cfg),'health':history,'producers':producers}
out=root/'artifacts/active/WEB-121';out.mkdir(parents=True,exist_ok=True)
path=out/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-stream-health.json')
path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'captured':str(path.relative_to(root)),'retainedOwners':len(history.get('sessions',[]))}))
