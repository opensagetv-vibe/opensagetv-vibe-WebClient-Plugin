#!/usr/bin/env python3
"""WP14-006 exact default-off gate after restoring original JVM environment."""
import hashlib,importlib.util,io,json,time,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration()
status=C.request(cfg,'/SageTVWebPlayer/api/support')
assert status['configured'] is False and status['writesEnabled'] is False
assert status['spoolFiles']==0 and status['spoolBytes']==0
test=C.request(cfg,'/SageTVWebPlayer/api/support?action=testDestination',{'confirm':'true','operationId':'wp14006-default-off'})
assert test['ok'] is False and test['stage']=='policy'
retry=C.request(cfg,'/SageTVWebPlayer/api/support?action=retrySpool',{'confirm':'true','operationId':'wp14006-default-off'})
assert retry['state']=='disabled'
out=ROOT/'artifacts/active/WP14-006';out.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
report={'passed':True,'realStock232':True,'configured':False,'writesEnabled':False,'spoolFiles':0,
        'boundedWriteTestRefused':True,'spoolRetryRefused':True,'activity':C.activity(cfg)}
path=out/(stamp+'-default-off.json');path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'report':str(path)}))
