"""WEB-122 real DOM/user-gesture tests; picker APIs mocked, no receiver proof."""
import importlib.util
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('fixture',root/'tests/browser-vibe-display-smoke.py')
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
checks=0
with sync_playwright() as pw:
    for engine in ('chromium','webkit'):
        options={'headless':True}
        if engine=='chromium':options.update(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
        browser=getattr(pw,engine).launch(**options)
        ctx,page,errors=f.load(browser,root/'src/main/webapp',size=(393,852))
        page.locator('#remoteToggle').click()
        button=page.locator('#remoteCast')
        assert button.is_visible() and button.is_disabled();checks+=1
        page.evaluate("""()=>{TEST.pickers=[];Object.defineProperty(videoPlane,'remote',{configurable:true,value:undefined});
          Object.defineProperty(videoPlane,'webkitShowPlaybackTargetPicker',{configurable:true,value:()=>TEST.pickers.push({kind:'airplay',active:navigator.userActivation?.isActive})});} """)
        assert button.is_disabled();checks+=1
        page.evaluate('TEST.startVideo()');page.wait_for_function('!remoteCast.disabled')
        if not page.locator('#remotePanel').is_visible():page.locator('#remoteToggle').click()
        before=page.evaluate('TEST.requests.length');page.locator('#remoteCast').click()
        assert page.evaluate("TEST.pickers.length===1&&TEST.pickers[0].kind==='airplay'&&TEST.pickers[0].active===true")
        assert page.evaluate("TEST.requests.slice(%d).every(r=>!['goLive','recover','command','seek','stop','start'].includes(r[0]))"%before);checks+=1
        page.evaluate("()=>{Object.defineProperty(videoPlane,'webkitCurrentPlaybackTargetIsWireless',{configurable:true,value:true});videoPlane.dispatchEvent(new Event('webkitcurrentplaybacktargetiswirelesschanged'));}")
        assert button.get_attribute('aria-pressed')=='true';checks+=1
        page.evaluate("()=>{videoPlane.disableRemotePlayback=true;videoPlane.dispatchEvent(new Event('loadedmetadata'));}")
        assert button.is_disabled();checks+=1
        page.evaluate("""()=>{videoPlane.disableRemotePlayback=false;
          Object.defineProperty(videoPlane,'webkitShowPlaybackTargetPicker',{configurable:true,value:undefined});
          Object.defineProperty(videoPlane,'remote',{configurable:true,value:{state:'disconnected',prompt:()=>{TEST.pickers.push({kind:'remote',active:navigator.userActivation?.isActive});return Promise.resolve();}}});
          videoPlane.dispatchEvent(new Event('loadedmetadata'));} """)
        button.click();assert page.evaluate("TEST.pickers.at(-1).kind==='remote'&&TEST.pickers.at(-1).active===true");checks+=1
        page.evaluate("()=>{videoPlane.remote.prompt=()=>Promise.reject(new DOMException('cancelled','AbortError'));}")
        button.click();page.wait_for_timeout(60);assert button.is_enabled();checks+=1
        page.evaluate("()=>{videoPlane.remote.prompt=()=>{throw new Error('receiver unavailable')};}")
        button.click();assert 'Unable to open video casting' in page.locator('#osdMessage').inner_text()
        assert button.is_enabled();checks+=1
        page.evaluate("()=>{Object.defineProperty(videoPlane,'remote',{configurable:true,value:undefined});videoPlane.dispatchEvent(new Event('emptied'));}")
        assert button.is_disabled() and 'Chromecast and Fire TV' in button.get_attribute('title');checks+=1
        page.set_viewport_size({'width':844,'height':390});page.wait_for_timeout(180)
        assert button.is_hidden();checks+=1
        assert not errors,errors;ctx.close()
        ctx,page,errors=f.load(browser,root/'src/main/webapp',size=(393,852),main_transform=lambda main:'window.SageVideoCast=undefined;\n'+main)
        assert page.locator('#remoteCast').is_disabled() and not errors;checks+=1
        ctx.close();browser.close()
print('Video-only cast DOM Chromium/WebKit:',checks,'PASS (mocked pickers, no physical receiver)')
