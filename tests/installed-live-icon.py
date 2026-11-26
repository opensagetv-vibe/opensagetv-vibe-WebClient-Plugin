"""WEB-122 installed stock232 UI/layout; no media Watch, simulated picker or cast."""
import argparse,json,runpy,time,uuid
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--run-stock232',action='store_true');p.add_argument('--task',choices=['WEB-122','WEB-125','WEB-126'],default='WEB-122');a=p.parse_args()
if not a.run_stock232:raise SystemExit('Explicit stock232 commissioning required')
c=runpy.run_path(str(ROOT/'scripts/commission-mobile.py'));cfg=c['configuration']()
identity='da92a86446be';owned=None
if not c['activity'](cfg)['safeToRestart']:raise SystemExit('Preserve existing recordings/clients')
out=ROOT/'artifacts/active'/a.task;out.mkdir(parents=True,exist_ok=True)
report={'passed':False,'physicalPhone':False,'physicalReceiver':False,'rows':[]}
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-'+uuid.uuid4().hex[:8]
path=out/(stamp+'-installed-icons.json')
def observed(response):
    global owned
    if '/api/miniclient' in response.url and response.request.method=='POST':
        try:
            value=response.json()
            if value.get('session') and value.get('clientId','').replace(':','').lower()==identity:owned=value['session']
        except Exception:pass
try:
    with sync_playwright() as pw:
        for engine in ('chromium','webkit'):
            opts={'headless':True}
            if engine=='chromium':opts.update(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
            browser=getattr(pw,engine).launch(**opts)
            context=browser.new_context(viewport={'width':844,'height':390},
                http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block')
            page=context.new_page();page.on('response',observed);errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
            # Isolated browser preferences match the fullscreen phone/PWA;
            # never change the user's saved browser or SageTV settings.
            page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebMiniClientSettings.v1',JSON.stringify({renderOnly:true}));")
            page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html?_vibeReload=web126.1',wait_until='domcontentloaded')
            page.wait_for_function("document.querySelector('#connectionStatus').textContent.toLowerCase().startsWith('connected')",timeout=45000)
            # Existing local keyboard shortcut, no native STV command.
            page.locator('#stage').focus();page.keyboard.press('ContextMenu')
            page.locator('#remotePanel').wait_for(state='visible')
            page.wait_for_function("document.querySelector('#remoteLive img').complete&&document.querySelector('#remoteLive img').naturalWidth>0")
            live=page.locator('#remoteLive');previous=page.locator('#nav_media_skip_back_2')
            lb,gb=live.bounding_box(),previous.bounding_box()
            assert lb and gb and abs(lb['x']+lb['width']-gb['x'])<1 and abs(lb['y']-gb['y'])<1
            assert lb['x']>=0 and lb['y']>=0 and lb['y']+lb['height']<=390
            assert live.get_attribute('aria-label')=='Watch live' and live.is_disabled()
            home,back,select=[page.locator('#'+i).bounding_box() for i in ('nav_home','nav_back','nav_select')]
            assert abs(home['x']-back['x'])<1 and abs(home['y']+home['height']-back['y'])<1
            assert abs(home['y']-select['y'])<1
            page.screenshot(path=str(out/(stamp+'-'+engine+'-landscape-icons.png')))
            page.locator('#closeRemote').click()
            assert page.evaluate('document.activeElement.id')=='cancelClientExit'
            assert page.locator('#refreshClientPage').is_enabled()
            with page.expect_navigation(wait_until='domcontentloaded'):
                page.locator('#refreshClientPage').click()
            page.wait_for_function("document.querySelector('#connectionStatus').textContent.toLowerCase().startsWith('connected')",timeout=45000)
            assert '_vibeReload=' in page.url
            assert page.evaluate("JSON.parse(localStorage.getItem('sagetvWebMiniClientSettings.v1')).renderOnly===true")
            page.set_viewport_size({'width':1440,'height':900});page.wait_for_timeout(400)
            page.locator('#stage').focus();page.keyboard.press('ContextMenu')
            lb,gb=live.bounding_box(),previous.bounding_box()
            assert lb and gb and abs(lb['x']+lb['width']-gb['x'])<1 and abs(lb['y']-gb['y'])<1
            page.screenshot(path=str(out/(stamp+'-'+engine+'-desktop-icons.png')))
            page.set_viewport_size({'width':393,'height':852});page.wait_for_timeout(400)
            page.locator('#mobileTab-controls').click()
            cast=page.locator('#remoteCast');assert cast.is_visible() and cast.is_disabled()
            assert cast.locator('img').evaluate('e=>e.complete&&e.naturalWidth>0')
            assert page.evaluate("typeof SageVideoCast.Controller==='function'") and not errors,errors
            page.screenshot(path=str(out/(stamp+'-'+engine+'-portrait-icons.png')))
            report['rows'].append({'engine':engine,'landscapeReferenceRowAndBackBelowHome':True,'liveLeftOfSkipInPhoneAndDesktop':True,'xMenuRefreshPreservesSettings':True,'portraitCastNoVideoDisabled':True,
                'exactCastModuleLoaded':True,'errors':errors})
            context.close();browser.close()
            if owned:
                try:c['request'](cfg,'/SageTVWebPlayer/api/miniclient',{'action':'stop','session':owned})
                except RuntimeError as error:
                    if not str(error).startswith('HTTP 404:'):raise
                    # Normal page teardown may already have retired it.
                owned=None
            # Public stop closes only the owned UI; observe retirement before
            # the next engine instead of restarting any server.
            deadline=time.monotonic()+10
            while not c['activity'](cfg)['safeToRestart']:
                if time.monotonic()>=deadline:raise RuntimeError('Owned UI retirement not observed')
                time.sleep(.5)
        report['passed']=True
except Exception as error:
    report['error']=str(error)[:400];raise
finally:
    if owned:
        try:c['request'](cfg,'/SageTVWebPlayer/api/miniclient',{'action':'stop','session':owned})
        except Exception:pass
    path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':report['passed'],'report':str(path.relative_to(ROOT))}))
