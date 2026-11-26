#!/usr/bin/env python3
"""Actual manager-installed codec-test page and native browser decoder.

MPEG2 negative results are explicit capability observations, not H264 failures.
No MiniClient created, recording read, profile edited or runtime stub used.
"""
import importlib.util,json,time
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
state=C.activity(cfg)
if state.get('recordingCount')!=0 or state.get('connectedClientCount')!=0:
    raise RuntimeError('Require no recordings or other clients')
out=ROOT/'artifacts/active/WP16-002';out.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
report={'engine':'chromium','physicalPhone':False,'realNativePlayback':True,'passed':False,'rows':[]}
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
        context=browser.new_context(http_credentials={'username':cfg['web_username'],'password':cfg['web_password']})
        page=context.new_page()
        page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/codec-test.html',wait_until='domcontentloaded')
        support=page.evaluate("document.createElement('video').canPlayType('application/vnd.apple.mpegurl')")
        report['nativeHlsCanPlayType']=support
        if not support:report['status']='UNSUPPORTED_NATIVE_HLS'
        else:
            page.wait_for_function("!document.getElementById('run').disabled",timeout=15000)
            page.locator('#run').click()
            page.wait_for_function("[...document.querySelectorAll('.card .result')].every(r=>/result (pass|fail)$/.test(r.className))",timeout=75000)
            report['rows']=page.evaluate("""()=>[...document.querySelectorAll('.card')].map(c=>{
              const v=c.querySelector('video'),t=c.querySelector('.facts').textContent;
              const i=t.indexOf('result=');return {id:c.dataset.id,detail:i>=0?JSON.parse(t.slice(i+7)):null,
              directSource:!!v.currentSrc&&!v.currentSrc.startsWith('blob:')}})""")
            controls=[r for r in report['rows'] if r['id'].startswith('h264')]
            if len(controls)!=3 or not all(r['directSource'] and r['detail'] and r['detail']['ok'] for r in controls):
                raise RuntimeError('A native H264 compatibility control failed')
            report['passed']=True;report['status']='COMPARISON_COMPLETE_CAPABILITIES_RECORDED'
        page.evaluate("()=>{for(const v of document.querySelectorAll('video')){v.pause();v.removeAttribute('src');v.load()}}")
        context.close();browser.close()
except Exception as error:
    report['errorType']=type(error).__name__
    if isinstance(error,RuntimeError):report['error']=str(error)
finally:
    path=out/(stamp+'-chromium-native-codec.json');path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report.get('status','FAIL'),'passed':report['passed'],'report':str(path)}))
raise SystemExit(0 if report['passed'] else 77 if report.get('status')=='UNSUPPORTED_NATIVE_HLS' else 1)
