#!/usr/bin/env python3
"""Compact local report inspection. Never prints credentials/caption payloads."""
import json,sys,zipfile
with zipfile.ZipFile(sys.argv[1]) as archive:
    entry=archive.getinfo('report.json')
    if entry.file_size>12*1024*1024:raise SystemExit('Report too large')
    text=archive.read(entry).decode('utf-8')
try:
    report=json.loads(text);print('VALID report JSON')
except json.JSONDecodeError as error:
    print('INVALID report JSON: '+str(error));print('Context: '+repr(text[max(0,error.pos-65):error.pos+65]))
    report={}
    for key in ['browser','stream','nativeSession']:
        marker='"'+key+'":';start=text.find(marker)
        if start<0:continue
        try:report[key]=json.JSONDecoder().raw_decode(text[start+len(marker):].lstrip())[0]
        except Exception:pass
browser=report.get('browser',{})
if isinstance(browser,str):
    try:browser=json.loads(browser)
    except Exception:browser={}
native=report.get('nativeSession',{})
if not isinstance(native,dict):native={}
print(json.dumps({'captions':browser.get('diagnostics',{}).get('captions'),
    'playback':{k:v for k,v in browser.get('playback',{}).items() if k in ['id','timeMs','startSeconds','transport','browserEngine']},
    'logs':browser.get('logs',[])[-20:],
    'nativeTrace':[item for item in native.get('connection',{}).get('trace',[]) if 'CC_STATE' in str(item)]},indent=2))
