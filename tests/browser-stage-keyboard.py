#!/usr/bin/env python3
"""WEB-057 production keyboard ownership; synthetic server, real browser keys."""
import importlib.util,json,os,time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ['SAGETV_ARTIFACT_DIR']);OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('display',ROOT/'tests/browser-vibe-display-smoke.py')
F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
old='e.target&&/BUTTON|A/.test(e.target.tagName)'
new='e.target&&/^(?:BUTTON|A)$/.test(e.target.tagName)'
rows=[];complete=False

def commands(page):return page.evaluate("TEST.requests.filter(r=>r[0]==='command').map(r=>+r[1].command)")
def clear(page):page.evaluate('TEST.requests=[]')

try:
    with sync_playwright() as pw:
        for engine in ('chromium','webkit'):
            browser=getattr(pw,engine).launch(headless=True,**({'executable_path':'/usr/local/bin/vibe-chromium','args':['--no-sandbox']} if engine=='chromium' else {}))
            for baseline in (True,False):
                context,page,errors=F.load(browser,ROOT/'src/main/webapp',size=(852,393),main_transform=(lambda source:source.replace(new,old)) if baseline else None)
                assert page.locator('#stage').evaluate('e=>e.tagName')=='MAIN'
                clear(page);page.locator('#stage').focus();page.keyboard.press('Enter');page.wait_for_timeout(100)
                assert commands(page)==([] if baseline else [20]),commands(page)
                rows.append({'engine':engine,'case':'baseline-MAIN-Enter' if baseline else 'MAIN-Enter','commands':commands(page)})
                if baseline:context.close();continue
                clear(page);page.locator('#stage').focus();page.keyboard.press('Space');page.wait_for_timeout(100)
                assert commands(page)==[59],commands(page)
                rows.append({'engine':engine,'case':'MAIN-Space','commands':commands(page)})
                page.evaluate("()=>{for(const tag of ['button','a','input','select']){const e=document.createElement(tag);e.id='ownership-'+tag;e.textContent=tag;if(tag==='a')e.href='#local-test';if(tag==='select')e.add(new Option('Local','local'));e.addEventListener('click',event=>{window.localKeyClicks=(window.localKeyClicks||0)+1;event.preventDefault();});document.getElementById('stage').append(e);}}")
                for tag in ('button','a','input','select'):
                    clear(page);page.locator('#ownership-'+tag).focus();page.keyboard.press('Enter');page.wait_for_timeout(100)
                    assert commands(page)==[],(tag,commands(page))
                    rows.append({'engine':engine,'case':tag+'-local-Enter','commands':commands(page)})
                assert not errors,errors
                context.close()
            browser.close()
    complete=True
finally:
    out=OUT/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-stage-keyboard.json')
    out.write_text(json.dumps({'passed':complete,'physicalPhone':False,'syntheticTransport':True,'rows':rows},indent=2)+'\n',encoding='utf-8')
print('PASS: '+str(len(rows))+' baseline/production keyboard ownership rows in Chromium and WebKit')
