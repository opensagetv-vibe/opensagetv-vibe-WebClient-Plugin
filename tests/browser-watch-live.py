"""WEB-120 real browser DOM controls with synthetic native transport, not phone proof."""
import importlib.util,os
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('fixture',root/'tests/browser-vibe-display-smoke.py')
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
checks=0
def desktop_live_position(page):
    live=page.locator('#remoteLive')
    previous=page.locator('#nav_media_skip_back_2')
    rewind=page.locator('#nav_media_skip_back')
    assert live.evaluate("e=>e.parentElement.classList.contains('vibe-transport')")
    assert live.evaluate("e=>e.nextElementSibling.id")== 'nav_media_skip_back_2'
    a,b,c=live.bounding_box(),previous.bounding_box(),rewind.bounding_box()
    assert a and b and c and abs(a['x']+a['width']-b['x'])<1 and abs(b['x']+b['width']-c['x'])<1,(a,b,c)
    assert abs(a['y']-b['y'])<1 and abs(b['y']-c['y'])<1,(a,b,c)
    # Include the other playback tools: the extra cell must not overlap them.
    controls=page.locator('.vibe-bottom button:visible')
    boxes=[controls.nth(i).bounding_box() for i in range(controls.count())]
    for i,a in enumerate(boxes):
        for b in boxes[i+1:]:
            assert min(a['x']+a['width'],b['x']+b['width'])-max(a['x'],b['x'])<1 or min(a['y']+a['height'],b['y']+b['height'])-max(a['y'],b['y'])<1,(a,b)
with sync_playwright() as pw:
    for engine in ('chromium','webkit'):
        options={'headless':True}
        if engine=='chromium':options.update(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
        browser=getattr(pw,engine).launch(**options)
        for size in ((1440,900),(1024,768),(901,600),(844,390),(393,852)):
            ctx,page,errors=f.load(browser,root/'src/main/webapp',size=size)
            page.locator('#remoteToggle').click()
            assert page.locator('#remoteLive').is_visible() and page.locator('#remoteLive').is_disabled();checks+=1
            live=page.locator('#remoteLive')
            assert live.get_attribute('aria-label')=='Watch live' and live.inner_text().strip()==''
            assert live.locator('img').evaluate('e=>e.complete&&e.naturalWidth>0');checks+=1
            gear=page.locator('#phoneToolsToggle')
            if size[0]>900:
                desktop_live_position(page);checks+=1
            if gear.is_visible() and size[0]>size[1]:
                a,b=live.bounding_box(),page.locator('#nav_media_skip_back_2').bounding_box()
                assert abs(a['y']-b['y'])<1 and abs(a['x']+a['width']-b['x'])<1,(size,a,b)
                assert abs(a['width']-b['width'])<1;checks+=1
            if size[0]<size[1]:
                assert live.bounding_box()['width']==44;checks+=1
            page.evaluate("TEST.startVideo()")
            page.wait_for_timeout(250)
            page.locator('#remoteToggle').click()
            if not page.locator('#remotePanel').is_visible():page.locator('#remoteToggle').click()
            page.wait_for_function("!document.getElementById('remoteLive').disabled")
            box=page.locator('#remoteLive').bounding_box()
            assert box and box['x']>=0 and box['x']+box['width']<=size[0];checks+=1
            page.evaluate("(()=>{const old=window.fetch;window.fetch=async(u,o={})=>{const q=new URL(u,location.href).searchParams;new URLSearchParams(o.body).forEach((v,k)=>q.set(k,v));if(q.get('action')==='goLive'){TEST.requests.push(['goLive',Object.fromEntries(q)]);return new Response(JSON.stringify({accepted:true,ok:true}))}return old(u,o)}})()")
            page.locator('#remoteLive').click()
            page.wait_for_function("TEST.requests.some(r=>r[0]==='goLive')")
            request=page.evaluate("TEST.requests.find(r=>r[0]==='goLive')[1]")
            assert request['expectedHlsSession']=='video-fixture' and request['session']=='native-fixture';checks+=1
            page.wait_for_timeout(150)
            assert (page.locator('#remotePanel').is_hidden() or page.locator('body').evaluate("e=>e.classList.contains('mc-portrait-dock')")) and not errors,(size,errors);checks+=1
            # Moving the ONE bound element between layouts must preserve the
            # one source-owned action and not leave a duplicate icon/listener.
            for target in ((844,390),(393,852),(1440,900),(844,390)):
                page.set_viewport_size({'width':target[0],'height':target[1]});page.wait_for_timeout(150)
                assert page.locator('#remoteLive').count()==1
                if not page.locator('#remotePanel').is_visible():page.locator('#remoteToggle').click()
                if target==(844,390):
                    a,b=live.bounding_box(),page.locator('#nav_media_skip_back_2').bounding_box()
                    assert a and b and abs(a['x']+a['width']-b['x'])<1 and abs(a['y']-b['y'])<1
                elif target==(1440,900):
                    desktop_live_position(page);checks+=1
            assert not errors;checks+=1
            ctx.close()
        browser.close()
print('Watch live DOM Chromium/WebKit:',checks,'PASS (synthetic transport)')
