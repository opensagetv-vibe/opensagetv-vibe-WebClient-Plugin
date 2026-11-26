#!/usr/bin/env python3
"""WEB-041 production control geometry/input; mock SageTV, not physical touch."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import importlib.util,os,threading,time
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ.get('SAGETV_ARTIFACT_DIR',ROOT/'artifacts/active/WEB-041'));OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('display',ROOT/'tests/browser-vibe-display-smoke.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'src/main/webapp')))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
  with sync_playwright() as pw:
    for engine in ('chromium','webkit'):
      options={'headless':True}
      if engine=='chromium':options.update(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
      browser=getattr(pw,engine).launch(**options)
      # WEB-074 owns the new portrait dock geometry; this is the unchanged
      # landscape overlay acceptance, including simulated iPhone safe areas.
      for w,h,safe in ((852,393,False),(852,393,True),(740,390,True),(667,375,False)):
        context=browser.new_context(viewport={'width':w,'height':h},has_touch=True,service_workers='block')
        context.add_init_script(fixture.INIT)
        context.add_init_script("Object.defineProperty(navigator,'standalone',{configurable:true,value:true})")
        page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(f'http://127.0.0.1:{server.server_port}/miniclient.html',wait_until='domcontentloaded')
        page.wait_for_function('TEST.stream!==null');page.locator('#remoteToggle').evaluate('e=>e.click()')
        if safe:page.add_style_tag(content='.vibe-phone-layout{--phone-left:59px!important;--phone-right:59px!important;--phone-bottom:20px!important}')
        toggle=page.locator('#phoneToolsToggle')
        assert toggle.is_visible() and toggle.get_attribute('aria-expanded')=='false'
        assert page.locator('#phoneTools').is_hidden()
        assert page.locator('.vibe-icon:visible').count()==25,page.locator('.vibe-icon:visible').evaluate_all('els=>els.map(e=>e.id)')
        commands=page.evaluate("TEST.requests.filter(r=>['command','seek'].includes(r[0])).length")
        toggle.click();assert page.locator('#phoneTools').is_visible()
        toggle.click();assert page.locator('#phoneTools').is_hidden()
        assert page.locator('#remotePanel').is_visible()
        toggle.click()
        geometry=page.locator('.vibe-icon').evaluate_all("els=>els.filter(e=>e.getClientRects().length).map(e=>{let r=e.getBoundingClientRect();return{id:e.id,x:r.x,y:r.y,w:r.width,h:r.height}})")
        assert len(geometry)==34 and len({r['id'] for r in geometry})==34
        assert all(r['w']>=44 and r['h']>=44 for r in geometry),geometry
        assert all(r['x']>=0 and r['x']+r['w']<=w+1 and r['y']>=0 and r['y']+r['h']<=h+1 for r in geometry),geometry
        info=['videoInfoBtn','diagnosticsBtn','testVideoBtn','remoteStatsInfo','aspectToggle','remoteSettings','audioSettings','remoteStats','captionSettings']
        chrome=geometry
        for i,a in enumerate(chrome):
          for b in chrome[i+1:]:
            overlap=min(a['x']+a['w'],b['x']+b['w'])-max(a['x'],b['x'])>1 and min(a['y']+a['h'],b['y']+b['h'])-max(a['y'],b['y'])>1
            assert not overlap,(a,b)
        g={r['id']:r for r in geometry}
        assert len({g[item]['x'] for item in info})==2
        assert abs(g['phoneToolsToggle']['x']+44-g['videoInfoBtn']['x'])<1
        for right,left in zip(info[:4],info[4:8]):
          assert abs(g[right]['x']-g[left]['x']-44)<1,g
          assert abs(g[right]['y']-g[left]['y'])<1,g
        assert [g[item]['y'] for item in info[:4]]==sorted(g[item]['y'] for item in info[:4])
        panel=page.locator('#phoneTools').bounding_box()
        assert panel['y']>=0 and panel['y']+panel['height']<=g['phoneToolsToggle']['y']+1,(panel,g)
        assert abs(panel['width']-88)<1 and abs(panel['height']-220)<1,panel
        for item in info:
          page.locator('#'+item).focus()
          r=page.locator('#'+item).bounding_box()
          assert r['y']>=panel['y']-1 and r['y']+r['height']<=panel['y']+panel['height']+1,(item,r,panel)
          assert page.locator('#'+item).evaluate('e=>{let r=e.getBoundingClientRect();return e.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2))}'),item
        assert page.locator('#phoneTools').evaluate('e=>e.scrollHeight===e.clientHeight')
        toggle.focus()
        nav=['nav_info','nav_options','nav_home']
        assert all(abs(g[item]['y']-g['nav_home']['y'])<1 for item in nav)
        assert [g[item]['x'] for item in nav]==sorted(g[item]['x'] for item in nav)
        if w>=800:
          row=['phoneToolsToggle','remoteHelp','keyboardToggle','remoteLive','nav_media_skip_back_2','nav_media_skip_back','nav_media_stop','nav_media_pause','nav_media_play','nav_media_skip_forward','nav_media_skip_forward_2',*nav]
          assert all(abs(g[item]['y']-g['nav_home']['y'])<1 for item in row),g
          assert [g[item]['x'] for item in row]==sorted(g[item]['x'] for item in row)
        assert abs(g['nav_back']['x']-g['nav_home']['x'])<1 and abs(g['nav_back']['y']-g['nav_home']['y']-44)<1,g
        assert abs(g['nav_select']['y']-g['nav_home']['y'])<1,g
        assert abs(g['nav_left']['x']-g['nav_back']['x']-44)<1,g
        # Back is one column left of Left, leaving the bottom Left column empty.
        if w>=800:
          assert abs(g['nav_down']['x']-(g['nav_back']['x']+g['nav_back']['w'])-44)<1,g
        assert g['nav_pgdn']['y']+44<=g['nav_up']['y']+1,g
        assert all(abs(g[item]['x']-g['nav_pgup']['x'])<1 for item in ['nav_up','nav_select','nav_down']),g
        assert g['nav_right']['x']>w/2 and g['nav_down']['y']>h/2
        assert abs(g['remoteHelp']['y']-g['keyboardToggle']['y'])<1
        assert abs(g['remoteHelp']['x']+44-g['keyboardToggle']['x'])<1
        page.locator('#remoteHelp').click();assert page.locator('#remoteTools').is_visible()
        page.locator('#closeRemoteTools').click();assert page.evaluate('document.activeElement.id')=='remoteHelp'
        page.locator('#remoteHelp').focus();page.keyboard.press('ArrowRight');assert page.evaluate('document.activeElement.id')=='keyboardToggle'
        page.locator('#nav_pgup').focus();page.keyboard.press('ArrowDown');assert page.evaluate('document.activeElement.id')=='nav_last'
        page.locator('#nav_info').focus();page.keyboard.press('ArrowRight');assert page.evaluate('document.activeElement.id')=='nav_options'
        page.locator('#remoteSettings').click();page.locator('#closeSettings').click()
        assert page.evaluate('document.activeElement.id')=='remoteSettings'
        assert toggle.get_attribute('aria-expanded')=='true'
        page.keyboard.press('Escape');assert page.locator('#phoneTools').is_hidden()
        assert page.evaluate('document.activeElement.id')=='phoneToolsToggle'
        page.keyboard.press('Enter');assert page.locator('#phoneTools').is_visible()
        assert page.evaluate("TEST.requests.filter(r=>['command','seek'].includes(r[0])).length")==commands
        stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());page.screenshot(path=str(OUT/(stamp+'-'+engine+'-'+str(w)+('-safe' if safe else '')+'.png')))
        # Breakpoint changes restore the original unique nodes and order.
        page.set_viewport_size({'width':1440,'height':900});page.wait_for_timeout(100)
        assert page.locator('.vibe-top>#nav_home').count()==1
        assert page.locator('.vibe-keyboard>#keyboardToggle').count()==1
        assert page.locator('.vibe-top-right>button').evaluate_all('els=>els.map(e=>e.id)')==['remoteHelp','closeRemote']
        assert page.locator('.vibe-utilities>button').count()==9
        assert toggle.is_hidden()
        assert page.locator('.vibe-dpad>button').evaluate_all('els=>els.slice(0,3).map(e=>e.id)')==['nav_options','nav_info','nav_back']
        page.set_viewport_size({'width':w,'height':h});page.wait_for_timeout(100)
        assert page.locator('.vibe-phone-navigation>#nav_home').count()==1
        assert page.locator('#phoneTools').is_hidden()
        assert not errors,errors
        print('PASS',engine,w,h,'safe' if safe else 'plain','reference landscape row/Back below Home/two tool columns,44px,Escape/parent focus/desktop restore,no remote mutations',flush=True)
        context.close()
      browser.close()
finally:
  server.shutdown();server.server_close()
