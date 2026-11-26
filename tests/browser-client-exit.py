#!/usr/bin/env python3
"""WEB-035 production X/Hide/modal/explicit-exit behavior, mocked SageTV."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import importlib.util,json,os,threading,time
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ.get('SAGETV_ARTIFACT_DIR',ROOT/'artifacts/active/WEB-035'));OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('display',ROOT/'tests/browser-vibe-display-smoke.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'src/main/webapp')))
threading.Thread(target=server.serve_forever,daemon=True).start()
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());results=[]
try:
  with sync_playwright() as pw:
    for engine in ('chromium','webkit'):
      options={'headless':True}
      if engine=='chromium':options.update(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
      browser=getattr(pw,engine).launch(**options)
      for width,height in ((852,393),(393,852),(320,568),(1440,900)):
        context=browser.new_context(viewport={'width':width,'height':height},service_workers='block')
        context.add_init_script(fixture.INIT)
        context.add_init_script("navigator.sendBeacon=(url,data)=>{TEST.beacons=(TEST.beacons||[]).concat([{url:String(url),session:String(data.get('session'))}]);return true}")
        context.add_init_script("const exitFetch=window.fetch;TEST.exitStops=[];window.fetch=function(u,o){const q=new URL(u,location.href).searchParams;if(q.get('action')==='stop'){TEST.exitStops.push(new URLSearchParams(o?.body||'').get('session'));if(TEST.rejectExitStop)return Promise.resolve(new Response('{}',{status:503}));if(TEST.deferExitStop)return new Promise(r=>TEST.releaseExitStop=()=>r(new Response(JSON.stringify({ok:true}))));}return exitFetch.apply(this,arguments);};")
        page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(f'http://127.0.0.1:{server.server_port}/miniclient.html',wait_until='domcontentloaded')
        page.wait_for_function('TEST.stream!==null');page.wait_for_timeout(250)
        page.locator('#remoteToggle').click();page.locator('#closeRemote').click()
        assert page.locator('#exitClientDialog').evaluate('e=>e.open')
        assert page.locator('#remotePanel').is_visible(),'X must not silently hide'
        assert page.evaluate('document.activeElement.id')=='cancelClientExit'
        count=page.evaluate('TEST.requests.filter(r=>r[0]==="command").length')
        page.keyboard.press('ArrowRight');assert page.evaluate('document.activeElement.id')=='confirmClientExit'
        page.keyboard.press('ArrowRight');assert page.evaluate('document.activeElement.id')=='refreshClientPage'
        page.keyboard.press('ArrowLeft');assert page.evaluate('document.activeElement.id')=='confirmClientExit'
        page.keyboard.press('ArrowLeft');page.keyboard.press('Enter')
        assert not page.locator('#exitClientDialog').evaluate('e=>e.open')
        assert page.evaluate('document.activeElement.id')=='closeRemote'
        assert not page.evaluate('!!TEST.beacons?.length'),'Cancel must not stop session'
        page.locator('#closeRemote').click();page.keyboard.press('Escape')
        assert page.locator('#remotePanel').is_visible()
        page.locator('#hideRemote').click()
        if page.evaluate('document.body.classList.contains("mc-portrait-dock")'):
            assert page.locator('#remotePanel').is_visible(),'portrait Controls tab stays available below STV'
            assert page.evaluate('document.activeElement.id==="stage"&&phoneTools.hidden&&remoteTools.hidden&&keyboardPanel.hidden&&videoInfoPanel.hidden'),'portrait Hide must dismiss drawers/tools and return stage focus'
        else:assert page.locator('#remotePanel').is_hidden()
        assert not page.locator('#exitClientDialog').evaluate('e=>e.open'),'green arrow only hides'
        page.locator('#remoteToggle').click();page.locator('#closeRemote').click()
        assert page.locator('#confirmClientExit').evaluate('e=>e.getBoundingClientRect().height')>=44
        page.screenshot(path=str(OUT/f'{stamp}-{engine}-{width}-confirm.png'))
        page.locator('#confirmClientExit').click()
        assert page.locator('#clientExited').is_visible()
        page.wait_for_function('TEST.exitStops.length===1',timeout=5000)
        assert page.evaluate('TEST.exitStops[0]===TEST.requests.find(r=>r[0]==="stop")[1].session')
        page.wait_for_function('document.getElementById("clientExitStatus").textContent.includes("confirmed")')
        assert not page.evaluate('!!TEST.beacons?.length'),'explicit Exit needs an acknowledged request, not only a queued beacon'
        assert page.locator('#videoPlane').evaluate('v=>v.paused&&!v.getAttribute("src")')
        starts=page.evaluate('TEST.requests.filter(r=>r[0]==="start").length')
        page.evaluate("document.dispatchEvent(new Event('visibilitychange'));window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))")
        page.wait_for_timeout(350)
        assert page.evaluate('TEST.requests.filter(r=>r[0]==="start").length')==starts,'intentional exit must not auto-reconnect'
        assert page.evaluate('TEST.requests.filter(r=>r[0]==="command").length')==count,'modal keys leaked into SageTV'
        page.locator('#reconnectAfterExit').click()
        page.wait_for_function('document.getElementById("clientExited").hidden')
        page.wait_for_function('(n)=>TEST.requests.filter(r=>r[0]==="start").length>n',arg=starts)
        assert not errors,errors
        if width==852:
            page.evaluate('TEST.rejectExitStop=true')
            page.locator('#remoteToggle').click();page.locator('#closeRemote').click();page.locator('#confirmClientExit').click()
            page.wait_for_function('document.getElementById("clientExitStatus").textContent.includes("could not be confirmed")')
            calls=page.evaluate('TEST.exitStops.length');page.wait_for_timeout(350)
            assert page.evaluate('TEST.exitStops.length')==calls,'unknown Stop must not be replayed'
            assert page.locator('#clientExited').is_visible()
            page.evaluate('TEST.rejectExitStop=false')
            page.locator('#reconnectAfterExit').click();page.wait_for_function('clientExited.hidden&&TEST.stream!==null')
            page.evaluate('TEST.deferExitStop=true')
            page.locator('#remoteToggle').click();page.locator('#closeRemote').click();page.locator('#confirmClientExit').click()
            page.wait_for_function('typeof TEST.releaseExitStop==="function"')
            old=page.evaluate('TEST.exitStops.at(-1)')
            page.locator('#reconnectAfterExit').click();page.wait_for_function('clientExited.hidden&&TEST.stream!==null')
            new=page.evaluate('TEST.requests.filter(r=>r[0]==="start").length')
            page.evaluate('TEST.releaseExitStop()');page.wait_for_timeout(350)
            assert page.locator('#clientExited').is_hidden(),'late old Stop cannot reopen Exit'
            assert page.evaluate('TEST.requests.filter(r=>r[0]==="start").length')==new
            assert page.evaluate('TEST.exitStops.at(-1)')==old,'old Stop must retain exact session ownership'
            assert not errors,errors
        results.append({'engine':engine,'viewport':[width,height],'passed':True})
        print('PASS',engine,width,'X confirm/default Cancel/Escape/Hide/explicit exit/reconnect/modal ownership',flush=True)
        context.close()
      browser.close()
finally:
  server.shutdown();(OUT/f'{stamp}-exit.json').write_text(json.dumps({'mockSageTV':True,'physicalPhone':False,'results':results},indent=2)+'\n')
