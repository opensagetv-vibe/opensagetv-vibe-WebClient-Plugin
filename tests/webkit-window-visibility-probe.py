#!/usr/bin/env python3
"""Bounded real X11 minimize/restore preflight; no server/phone or fake visibility.

Run only through xvfb-run with a private display. A hidden page is observed,
never synthesized via JavaScript or browser-protocol visibility overrides.
"""
import json,os,subprocess,time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'artifacts/active/WEB-109';out.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
report=dict(task='WEB-109',serverAccess=False,physicalPhone=False,passed=False,cleanup=[])
wm=None
def command(*args):
    return subprocess.run(args,check=True,capture_output=True,text=True,timeout=5).stdout.strip()
try:
    authority=Path(os.environ.get('XAUTHORITY',''))
    if not os.environ.get('DISPLAY') or authority.name!='Xauthority' or not authority.parent.name.startswith('xvfb-run.') or authority.parent.parent!=Path('/tmp'):
        raise RuntimeError('Require owned xvfb-run private display')
    wm=subprocess.Popen(['openbox','--sm-disable','--config-file','/etc/xdg/openbox/rc.xml'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    with sync_playwright() as pw:
        browser=pw.webkit.launch(headless=False,timeout=15000)
        context=browser.new_context();page=context.new_page()
        page.set_content('<title>VibeWindowVisibilityProbe</title><p>Private display visibility preflight</p>')
        report['before']=page.evaluate('({visibility:document.visibilityState,hidden:document.hidden})')
        windows=command('xdotool','search','--onlyvisible','--name','VibeWindowVisibilityProbe').splitlines()
        if len(windows)!=1 or not windows[0].isdigit():raise RuntimeError('Expected one exact probe window')
        window=windows[0]
        try:
            command('xdotool','windowminimize',window);page.wait_for_timeout(500)
            report['minimized']=page.evaluate('({visibility:document.visibilityState,hidden:document.hidden})')
            visible=subprocess.run(['xdotool','search','--onlyvisible','--name','VibeWindowVisibilityProbe'],capture_output=True,text=True,timeout=5)
            report['x11Minimized']=visible.returncode==1 and not visible.stdout.strip()
        finally:
            command('xdotool','windowmap',window);command('xdotool','windowactivate','--sync',window)
        page.wait_for_timeout(300)
        report['restored']=page.evaluate('({visibility:document.visibilityState,hidden:document.hidden})')
        report['passed']=bool(report.get('x11Minimized') and report['minimized']['hidden'] and report['restored']['visibility']=='visible')
        context.close();browser.close()
except Exception as error:report['failure']=dict(type=type(error).__name__,message=str(error).splitlines()[0][:200])
finally:
    if wm:
        wm.terminate()
        try:wm.wait(timeout=5)
        except subprocess.TimeoutExpired:wm.kill();wm.wait(timeout=5);report['cleanup'].append('WindowManagerForcedExit')
    report['passed']=report['passed'] and not report['cleanup']
    report['status']='PASS' if report['passed'] else 'BACKEND_VISIBILITY_NOT_OBSERVED' if report.get('x11Minimized') and not report.get('failure') else 'FAIL'
    path=out/(stamp+'-webkit-window-visibility.json')
    with path.open('x',encoding='utf-8') as handle:json.dump(report,handle,indent=2)
    print(json.dumps(report),flush=True)
raise SystemExit(0 if report['passed'] else 77 if report['status']=='BACKEND_VISIBILITY_NOT_OBSERVED' else 1)
