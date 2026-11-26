#!/usr/bin/env python3
"""Read-only served/source revision proof using the commissioned232 identity."""
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('commission', ROOT/'scripts/commission-mobile.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
cfg = C.configuration()
results = []
for name in ('miniclient.html', 'css/miniclient.css', 'js/miniclient.js',
             'js/miniclient-core.js', 'js/miniclient-input.js', 'js/miniclient-app.js', 'js/miniclient-support.js',
             'js/miniclient-playback.js',
             'js/miniclient-experience.js',
             'js/miniclient-mobile.js',
             'js/miniclient-streaming.js', 'js/atsc-captions.js', 'js/miniclient-captions.js',
             'icons/vibe/settings.svg', 'icons/vibe/live.svg', 'icons/vibe/cast.svg',
             'js/miniclient-cast.js', 'sw.js'):
    url = cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/'+name+'?verify=web046'
    token = base64.b64encode((cfg['web_username']+':'+cfg['web_password']).encode()).decode()
    request = Request(url, headers={'Authorization': 'Basic '+token, 'Cache-Control': 'no-cache'})
    with urlopen(request, timeout=15) as response:
        served = response.read(4*1024*1024+1)
        if len(served)>4*1024*1024: raise RuntimeError('Served asset exceeds bound')
    expected = (ROOT/'src/main/webapp'/name).read_bytes()
    same = served == expected
    results.append({'asset': name, 'bytes': len(served), 'sha256': hashlib.sha256(served).hexdigest(), 'matchesSource': same})
print(json.dumps({'passed': all(row['matchesSource'] for row in results), 'results': results}, indent=2))
raise SystemExit(0 if all(row['matchesSource'] for row in results) else 1)
