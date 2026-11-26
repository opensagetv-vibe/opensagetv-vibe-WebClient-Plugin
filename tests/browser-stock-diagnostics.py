#!/usr/bin/env python3
"""Real manager-installed diagnostic ZIP, including nested native crypto JSON."""
import hashlib,importlib.util,io,json,os,time,zipfile
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
owned=None;complete=False;report=None;stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
OUT=Path(os.environ.get('SAGETV_ARTIFACT_DIR',ROOT/'artifacts/active/WEB-054'));OUT.mkdir(parents=True,exist_ok=True)
def observe(response):
    global owned
    if '/api/miniclient' not in response.url or response.request.method!='POST':return
    try:
        value=response.json()
        if value.get('session') and value.get('clientId','').replace(':','').lower()=='da92a86446be':owned=value['session']
    except Exception:pass
try:
    state=C.activity(cfg);uis=C.request(cfg,'/v1/control',{'action':'ui.list'},mcp=True).get('contexts',[])
    assert state['recordingCount']==0 and state['connectedClientCount']==0 and (not uis or uis==['da92a86446be'])
    with sync_playwright() as pw:
        engine=os.environ.get('SAGETV_BROWSER_ENGINE','chromium')
        if engine not in ('chromium','webkit'):raise ValueError('Unsupported test browser')
        browser=(pw.webkit.launch(headless=True) if engine=='webkit' else
                 pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox']))
        context=browser.new_context(http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},accept_downloads=True,service_workers='block')
        page=context.new_page();page.on('response',observe)
        page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');")
        page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
        page.wait_for_timeout(4000);assert owned
        page.locator('#settingsToggle').click();page.locator('#settings-tab-diagnostics').click()
        with page.expect_download(timeout=30000) as download:page.locator('#downloadReport').click()
        path=OUT/(stamp+'-real-diagnostics.zip');download.value.save_as(str(path))
        with zipfile.ZipFile(path) as archive:
            data=archive.read('report.json');report=json.loads(data)
            assert hashlib.sha256(data).hexdigest()+'  report.json' in archive.read('hashes.sha256').decode()
        assert report['version']=='3.3.0'
        assert isinstance(report['browser'],dict) and isinstance(report['miniClient'],dict)
        assert report['miniClient']['connection']['crypto']=='[redacted]'
        assert 'startupEvents' in report['miniClient']['connection']
        experience=report['browser']['playback']['experience']
        assert all(name in experience for name in ('timeline','previews','sourcePreviews','quality','markers'))
        assert experience['sourcePreviews']['queued']==0
        assert experience['sourcePreviews']['method']=='explicit-shared-source-image'
        assert 'previewToken' not in json.dumps(experience)
        complete=True
        assert C.request(cfg,'/SageTVWebPlayer/api/miniclient',{'action':'stop','session':owned}).get('ok') is True
        owned=None
        context.close();browser.close()
        print('PASS real diagnostic ZIP: valid nested JSON, native crypto wholly redacted, safe counters and exact report hash',flush=True)
finally:
    if owned:
        try:C.request(cfg,'/SageTVWebPlayer/api/miniclient',{'action':'stop','session':owned})
        except Exception:pass
    deadline=time.monotonic()+90
    while True:
        final_activity=C.activity(cfg)
        if final_activity.get('safeToRestart') is True:break
        if time.monotonic()>=deadline:
            complete=False;break
        time.sleep(.5)
    (OUT/(stamp+'-diagnostics-result.json')).write_text(json.dumps({'passed':complete,'runtimeVersion':'3.3.0','engine':os.environ.get('SAGETV_BROWSER_ENGINE','chromium'),'realStock232':True,'physicalIPhone':False,'nativeCryptoRedacted':bool(report and report.get('miniClient',{}).get('connection',{}).get('crypto')=='[redacted]')},indent=2)+'\n')
