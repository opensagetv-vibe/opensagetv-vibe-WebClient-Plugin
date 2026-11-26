#!/usr/bin/env python3
"""WEB-074 actual production DOM/CSS, simulated lists/stock playback. Not iPhone proof."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import importlib.util, os, threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('fixture',ROOT/'tests/browser-vibe-display-smoke.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'src/main/webapp')))
threading.Thread(target=server.serve_forever,daemon=True).start()
INIT=r"""(()=>{
const fetch=window.fetch;
window.LIB={reads:[],plays:[],fail:false,slow:false,release:null,watchRelease:null,fullscreen:false};
window.fetch=async function(url,options={}){
 const u=new URL(url,location.href),body=new URLSearchParams(options.body||''),a=u.searchParams.get('action');
 if(u.pathname==='/api/recordings'||u.pathname==='/api/guide'){
  LIB.reads.push(u.search);if(LIB.fail)return new Response(JSON.stringify({error:'List unavailable'}),{status:503});
  if(LIB.slow)await new Promise(resolve=>LIB.release=resolve);
  const guide=u.pathname==='/api/guide',videos=u.searchParams.get('kind')==='videos';
  const rows=Array.from({length:70},(_,i)=>({id:100+i,mediaId:guide&&i===0?100:0,airingId:200+i,title:(videos?'Video ':guide?'Program ':'Recording ')+i,episode:i===0?'<img src=x onerror=alert(1)>':'Episode',description:'A long description '.repeat(8),channelNumber:'7.1',currentlyAiring:i===1,start:1700000000000+i*1800000,end:1700000000000+(i+1)*1800000}));
  return new Response(JSON.stringify(guide?{airings:rows}:{recordings:rows}));
 }
 if(a==='watchContent'){
  LIB.fullscreen=false;
  LIB.plays.push(Object.fromEntries(body));
  if(LIB.watchRelease===true)await new Promise(resolve=>LIB.watchRelease=resolve);
  return new Response(JSON.stringify({ok:true,accepted:true}));
 }
 if(a==='contentState')return new Response(JSON.stringify({ok:true,ready:true,layout:LIB.fullscreen?'fullscreen':'preview'}));
 if(a==='showContent'){LIB.fullscreen=true;return new Response(JSON.stringify({ok:true}));}
 return fetch.apply(this,arguments);
};})();"""
try:
 with sync_playwright() as pw:
  for engine in ('chromium','webkit'):
   args={'headless':True}
   if engine=='chromium':args.update(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
   browser=getattr(pw,engine).launch(**args)
   for width,height in ((393,852),(320,568),(768,1024)):
    context=browser.new_context(viewport={'width':width,'height':height},has_touch=True,service_workers='block')
    context.add_init_script(fixture.INIT);context.add_init_script(INIT)
    context.add_init_script("Object.defineProperty(navigator,'standalone',{value:true,configurable:true})")
    page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(f'http://127.0.0.1:{server.server_port}/miniclient.html',wait_until='domcontentloaded')
    page.wait_for_function('TEST.stream!==null');page.wait_for_timeout(350)
    page.locator('#mobileTab-controls').click()
    geometry=page.evaluate("(()=>{const rect=id=>{let r=document.getElementById(id).getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height}};return{stage:rect('stage'),canvas:rect('gfxCanvas'),dock:rect('mobileDock'),remote:rect('remotePanel')}})()")
    assert abs(geometry['stage']['w']-width)<1,geometry
    assert abs(geometry['stage']['w']/geometry['stage']['h']-16/9)<.02,geometry
    assert abs(geometry['canvas']['w']-geometry['stage']['w'])<1,geometry
    assert geometry['dock']['y']>=geometry['stage']['y']+geometry['stage']['h']-1,geometry
    assert geometry['remote']['y']+geometry['remote']['h']<=height+1,geometry
    assert page.locator('#remotePanel').get_attribute('aria-modal') is None
    icons=page.locator('#remotePanel .vibe-icon:visible').evaluate_all('els=>els.map(e=>{const r=e.getBoundingClientRect();return{id:e.id,x:r.x,y:r.y,w:r.width,h:r.height}})')
    # WEB-122 adds video-only Cast and Watch live to the portrait controls.
    assert len(icons)==26,icons
    assert {'remoteCast','remoteLive'}.issubset({r['id'] for r in icons}),icons
    assert all(r['w']>=44 and r['h']>=44 and r['x']>=0 and r['x']+r['w']<=width+1 and r['y']>=geometry['dock']['y'] and r['y']+r['h']<=height+1 for r in icons),icons
    for i,a in enumerate(icons):
     for b in icons[i+1:]:assert not(min(a['x']+a['w'],b['x']+b['w'])>max(a['x'],b['x'])+1 and min(a['y']+a['h'],b['y']+b['h'])>max(a['y'],b['y'])+1),(a,b)
    assert page.locator('#remotePanel').evaluate('e=>e.scrollHeight===e.clientHeight')
    # Model a notched Home Screen viewport: reserve its top inset once, keep
    # the TV aspect/width and shrink only the independent content area.
    page.evaluate("document.documentElement.style.setProperty('--mobile-safe-top','59px')")
    safe=page.locator('#stage').bounding_box()
    assert abs(safe['y']-83)<1,safe
    assert abs(safe['width']-width)<1 and abs(safe['width']/safe['height']-16/9)<.02,safe
    assert page.locator('#remotePanel').evaluate('e=>e.scrollHeight===e.clientHeight')
    assert page.locator('#mobileDock').bounding_box()['y']>=safe['y']+safe['height']-1
    page.evaluate("document.body.classList.remove('mc-standalone')")
    assert page.locator('#app').evaluate('e=>getComputedStyle(e).paddingTop')=='24px'
    page.evaluate("document.body.classList.add('mc-standalone')")
    page.evaluate("document.documentElement.style.removeProperty('--mobile-safe-top')")
    page.locator('#nav_right').click();page.wait_for_timeout(80)
    assert page.evaluate("TEST.requests.filter(r=>r[0]==='command'&&r[1].command==='3').length")==1
    page.locator('#keyboardToggle').click();assert page.locator('#keyboardPanel').is_visible()
    page.locator('#mobileTab-recordings').click();page.wait_for_selector('.mc-mobile-folder');page.locator('.mc-mobile-browse select').select_option('all');page.wait_for_selector('.mc-mobile-item')
    assert page.locator('#keyboardPanel').is_hidden()
    page.locator('.mc-mobile-search input').focus();page.keyboard.press('Tab')
    assert page.evaluate('document.activeElement.textContent')=='Refresh'
    assert page.locator('.mc-mobile-item').count()==70
    assert page.locator('.mc-mobile-item img').count()==0 # textContent, not list HTML
    assert page.locator('.mc-mobile-list').evaluate('e=>e.scrollHeight>e.clientHeight')
    assert page.evaluate('LIB.plays.length')==0
    page.evaluate('LIB.watchRelease=true');page.get_by_role('button',name='Play Recording 0 in SageTV',exact=True).click()
    assert page.locator('.mc-mobile-item button:enabled').count()==0
    page.evaluate('LIB.watchRelease()');page.wait_for_function('!document.querySelector("[data-content-play]").disabled')
    assert page.evaluate('LIB.plays')==[{'session':'native-fixture','mediaId':'100'}]
    count=page.evaluate('TEST.requests.length');page.locator('#mobileTab-videos').focus();page.keyboard.press('ArrowLeft')
    page.wait_for_function('document.querySelector("#mobileTab-guide").getAttribute("aria-selected")==="true"')
    assert page.evaluate('TEST.requests.length')==count # local tabs never send STV arrows
    page.wait_for_selector('.mc-mobile-program');page.locator('.mc-mobile-program').nth(2).click();assert page.locator('[data-content-play]').is_disabled()
    page.get_by_role('button',name='Back to guide',exact=True).click()
    page.locator('.mc-mobile-program').nth(1).click();page.locator('[data-content-play]').click();page.wait_for_function('LIB.plays.length===2')
    assert page.evaluate('LIB.plays[1]')=={'session':'native-fixture','airingId':'201'}
    page.evaluate('LIB.fail=true');page.locator('.mc-mobile-search button').click();page.wait_for_function('document.querySelector(".mc-mobile-list-status").textContent.includes("Unable")')
    assert page.locator('.mc-mobile-item').count()==0
    page.evaluate('LIB.fail=false;LIB.slow=true');page.locator('#mobileTab-recordings').click();page.wait_for_function('!!LIB.release')
    page.locator('#mobileTab-controls').click();page.evaluate('LIB.slow=false;LIB.release()');page.wait_for_timeout(50)
    assert page.locator('#mobilePage-recordings').is_hidden()
    page.locator('#mobileTab-videos').click();page.wait_for_selector('.mc-mobile-item')
    assert page.locator('.mc-mobile-item strong').first.inner_text()=='Video 0'
    page.locator('.mc-mobile-search input').fill('sample');page.locator('.mc-mobile-search').evaluate('e=>e.requestSubmit()');page.wait_for_timeout(50)
    assert any('q=sample' in q and 'kind=videos' in q for q in page.evaluate('LIB.reads'))
    page.set_viewport_size({'width':1024,'height':600});page.wait_for_timeout(250)
    page.evaluate("document.documentElement.style.setProperty('--mobile-safe-top','59px')")
    assert page.locator('#app').evaluate('e=>getComputedStyle(e).paddingTop')=='0px'
    page.evaluate("document.documentElement.style.removeProperty('--mobile-safe-top')")
    assert page.locator('#mobileDock').is_hidden()
    assert page.locator('#stage>#remotePanel').count()==1
    assert page.locator('#remotePanel').is_hidden()
    page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(250)
    page.locator('#mobileTab-controls').click();assert page.locator('#mobilePage-controls>#remotePanel').count()==1
    assert page.locator('[id=nav_right]').count()==1
    assert not errors,errors
    print(f'PASS {engine} portrait {width}x{height}: aspect/dock/26targets/no-scroll/tabs/lists/Play/guards/rotation',flush=True)
    context.close()
   browser.close()
finally:server.shutdown()
