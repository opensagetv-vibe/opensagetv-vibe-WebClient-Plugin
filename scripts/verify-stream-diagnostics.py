#!/usr/bin/env python3
"""WEB-121 read-only recorder/report verification; no playback or server writes."""
import base64,hashlib,io,json,runpy,urllib.request,urllib.parse,zipfile
from pathlib import Path
c=runpy.run_path(str(Path(__file__).with_name('commission-mobile.py')));cfg=c['configuration']()
history=c['request'](cfg,'/SageTVWebPlayer/api/support?action=streamHealth')
assert history['enabled'] and history['storageState']=='written'
headers={'Authorization':'Basic '+base64.b64encode((cfg['web_username']+':'+cfg['web_password']).encode()).decode()}
def fetch(path,values=None):
    data=urllib.parse.urlencode(values).encode() if values else None
    req=urllib.request.Request(cfg['web_base_url'].rstrip('/')+path,data=data,headers=headers)
    with urllib.request.urlopen(req,timeout=20) as r:
        result=r.read(4*1024*1024+1)
        assert len(result)<=4*1024*1024
        return result
journal=fetch('/SageTVWebPlayer/api/support?action=streamJournal')
assert 0<len(journal)<=2*1024*1024
rows=[json.loads(line) for line in journal.splitlines() if line.strip()]
assert rows and all(r['observationalOnly'] for r in rows)
bundle=fetch('/SageTVWebPlayer/api/support',{'action':'report','browserJson':'{}'})
with zipfile.ZipFile(io.BytesIO(bundle)) as z:
    for name in ['report.json','stream-health.json','stream-health.jsonl']:
        payload=z.read(name)
        assert hashlib.sha256(payload).hexdigest()+'  '+name in z.read('hashes.sha256').decode()
    assert json.loads(z.read('stream-health.json'))['schemaVersion']==1
    assert z.read('stream-health.jsonl')
print(json.dumps({'passed':True,'retainedOwners':len(history['sessions']),'journalBytes':len(journal),
    'journalRows':len(rows),'bundleHashEntriesVerified':3,'readOnly':True}))
