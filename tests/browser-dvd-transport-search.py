#!/usr/bin/env python3
"""Production DVD transport-search DOM/queue ownership, synthetic native wire."""
import importlib.util,json,threading,time,os
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=Path(os.environ.get('SAGETV_ARTIFACT_DIR',ROOT/'artifacts/active/WEB-113')).resolve()
if not OUT.is_relative_to((ROOT/'artifacts/active').resolve()):raise RuntimeError('Task-owned active output required')
OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('fixture',ROOT/'tests/browser-vibe-display-smoke.py')
F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*_):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'src/main/webapp')))
threading.Thread(target=server.serve_forever,daemon=True).start()
rows=[];complete=False;stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
HOOK=r'''(()=>{const original=fetch;TEST.menu=false;TEST.hold=false;TEST.reject=false;
 window.fetch=async function(url,options={}){const u=new URL(url,location.href),q=new URLSearchParams(u.search);if(options.body)new URLSearchParams(options.body).forEach((v,k)=>q.set(k,v));
 if(q.get('action')==='state'){TEST.requests.push(['state',Object.fromEntries(q)]);return new Response(JSON.stringify({ok:true,dvdMenu:TEST.menu}),{headers:{'Content-Type':'application/json'}});}
 const response=await original.apply(this,arguments);
 if(q.get('action')==='command'&&q.get('command')==='7'){
  if(TEST.hold){TEST.hold=false;await new Promise(r=>TEST.release=r);}
  if(TEST.reject){TEST.reject=false;return new Response(JSON.stringify({ok:false}),{headers:{'Content-Type':'application/json'}});}
 }
 return response;};
 TEST.feature=(dvd=true,id='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')=>{TEST.emit({type:'videoStart',dvd,dvdGeneration:1,hlsSession:id,playlistUrl:'hls/'+id+'/stream.m3u8',transport:'hls',durationMs:60000,paused:false});TEST.emit({type:'videoBounds',dst:[0,0,TEST.width,TEST.height],src:[0,0,720,480]});TEST.emit({type:'menuHint',value:'menuName:MC MediaPlayer OSD,popupName:,hasTextInput:false'});TEST.frame();};})();'''
try:
 with sync_playwright() as pw:
  for engine in ('chromium','webkit'):
   browser=getattr(pw,engine).launch(headless=True,**(dict(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox']) if engine=='chromium' else {}))
   for case in ('normal','remote-enter','remote-enter-menu','menu','recording','popup','stale','atomic','rejected','source-retired','cancel-pending','feature-paint-only','popup-paint-only','recording-paint-only','unknown-paint-only','old-preview-feature','old-preview-menu','old-preview-popup','old-preview-recording','old-preview-stale','old-preview-native'):
    context=browser.new_context(viewport=dict(width=1280,height=800),service_workers='block');page=context.new_page();errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)));page.add_init_script(F.INIT+HOOK)
    page.goto('http://127.0.0.1:'+str(server.server_port)+'/miniclient.html')
    page.wait_for_function("TEST.stream&&connectionStatus.textContent.startsWith('Connected')")
    page.evaluate('TEST.feature(false)' if case in ('recording','recording-paint-only','old-preview-recording') else 'TEST.feature()')
    page.wait_for_function("TEST.requests.some(r=>r[0]==='state'&&r[1].expectedHlsSession==='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')")
    page.wait_for_timeout(100);page.locator('#remoteToggle').click();page.evaluate('TEST.requests=[]')
    def commands():return page.evaluate("TEST.requests.filter(r=>r[0]==='command').map(r=>Number(r[1].command))")
    def click(selector):page.locator(selector).click();page.wait_for_timeout(80)
    ff='#nav_media_skip_forward';rw='#nav_media_skip_back'
    if case=='remote-enter-menu':page.evaluate('TEST.menu=true');page.wait_for_timeout(800)
    if case in ('menu','stale'):
     page.evaluate('TEST.menu=true' if case=='menu' else 'TEST.menu=null');page.wait_for_timeout(1800)
    if case=='popup':page.evaluate("TEST.emit({type:'menuHint',value:'menuName:MC MediaPlayer OSD,popupName:DVD Options,hasTextInput:false'})");page.wait_for_timeout(100)
    if case.endswith('paint-only'):
     if case=='popup-paint-only':page.evaluate("TEST.emit({type:'menuHint',value:'menuName:MediaPlayer OSD,popupName:DVD Options,hasTextInput:false'})")
     if case=='unknown-paint-only':page.evaluate("TEST.emit({type:'menuHint',value:'menuName:Unknown,popupName:,hasTextInput:false'})")
     page.evaluate('TEST.emit(TEST.gfx(31));TEST.emit(TEST.gfx(30))');page.wait_for_timeout(100)
    if case.startswith('old-preview-'):
     if case=='old-preview-menu':page.evaluate("TEST.emit({type:'menuHint',value:'menuName:Dynamic Menu by nielm,popupName:,hasTextInput:false'})")
     if case=='old-preview-popup':page.evaluate("TEST.emit({type:'menuHint',value:'menuName:MediaPlayer OSD,popupName:DVD Options,hasTextInput:false'})")
     if case=='old-preview-stale':page.evaluate('TEST.menu=null')
     if case=='old-preview-native':page.evaluate("videoViewport.value='native';videoViewport.dispatchEvent(new Event('change',{bubbles:true}))")
     page.evaluate("TEST.emit({type:'videoBounds',dst:[67,481,350,161],src:[0,0,720,480]})")
     page.wait_for_timeout(1800 if case=='old-preview-stale' else 100)
     expected='fullscreen' if case=='old-preview-feature' else 'native' if case=='old-preview-native' else 'preview'
     assert page.locator('#videoBounds').get_attribute('data-presentation')==expected,(engine,case,'actual layout owner')
    if case in ('remote-enter','remote-enter-menu'):
     for selector in (ff,ff,rw,'#nav_select'):
      page.locator(selector).focus();page.keyboard.press('Enter');page.wait_for_timeout(100)
     expected=[7,10,8,8,9,10] if case=='remote-enter' else [8,8,9,20]
     assert commands()==expected,(engine,case,commands())
     if case=='remote-enter':
      for selector in (ff,'#nav_media_play'):
       page.locator(selector).focus();page.keyboard.press('Enter');page.wait_for_timeout(100)
      assert commands()[-4:]==[7,10,8,7],(engine,case,'cancel',commands())
    elif case in ('atomic','rejected','source-retired','cancel-pending'):
     page.evaluate('TEST.hold=true');click(ff);page.wait_for_function('!!TEST.release')
     if case=='source-retired':page.evaluate("TEST.feature(true,'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb')");page.wait_for_timeout(80)
     else:click(rw)
     if case=='rejected':page.evaluate('TEST.reject=true')
     if case=='cancel-pending':click('#nav_media_play')
     page.evaluate('TEST.release()');page.wait_for_timeout(300)
     expected=[7,10,8,9] if case=='atomic' else [7,7] if case=='cancel-pending' else [7]
     assert commands()==expected,(engine,case,commands())
     if case=='source-retired':
      page.wait_for_function("TEST.requests.some(r=>r[0]==='state'&&r[1].expectedHlsSession==='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb')")
      page.wait_for_timeout(80);click(ff)
      assert commands()==[7,7,10,8],(engine,'retired search must not leak into successor',commands())
    else:
     click(ff)
     if case=='normal':
      click(rw);click('#nav_select');assert commands()==[7,10,8,9,10],(engine,case,commands())
      click(ff);click('#nav_back');assert commands()[-4:]==[7,10,8,7]
      assert not page.evaluate("TEST.requests.some(r=>['seek','recover','streamSettings'].includes(r[0]))"),'Search must not rebuild the producer'
     elif case in ('feature-paint-only','old-preview-feature'):
      assert commands()==[7,10,8],(engine,case,commands())
      if case=='old-preview-feature':
       page.evaluate("TEST.emit({type:'menuHint',value:'menuName:Dynamic Menu by nielm,popupName:,hasTextInput:false'})")
       page.wait_for_function("videoBounds.dataset.presentation==='preview'")
       assert page.locator('#videoBounds').evaluate("e=>parseFloat(e.style.width)")<400,'Original preview geometry must survive OSD override'
     else:assert commands()==[8],(engine,case,commands())
    assert not errors,errors
    rows.append(dict(engine=engine,case=case,commands=commands(),passed=True));print('PASS '+engine+' '+case,flush=True)
    context.close()
   browser.close()
 complete=True
finally:
 server.shutdown();server.server_close()
 (OUT/(stamp+'-dvd-transport-search.json')).write_text(json.dumps(dict(passed=complete,syntheticTransport=True,physicalPhone=False,rows=rows),indent=2)+'\n',encoding='utf-8')
