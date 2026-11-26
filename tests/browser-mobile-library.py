#!/usr/bin/env python3
"""WEB079/080 production browser deck; mocked catalog/actions, not physical iOS."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import importlib.util,threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('fixture',ROOT/'tests/browser-vibe-display-smoke.py')
F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'src/main/webapp')))
threading.Thread(target=server.serve_forever,daemon=True).start()
INIT=r"""(()=>{const fetch=window.fetch;window.BROWSE={records:[],info:[],plays:[],reads:[],local:true};
window.fetch=async function(url,options={}){
 const u=new URL(url,location.href),a=u.searchParams.get('action'),b=new URLSearchParams(options.body||'');
 if(a==='status'){const r=await fetch.apply(this,arguments),d=await r.json();d.localContent=BROWSE.local;return new Response(JSON.stringify(d));}
 if(u.pathname==='/api/recordings'){
  BROWSE.reads.push(u.search);const videos=u.searchParams.get('kind')==='videos';
  let recordings=videos?[{id:10,title:'Movie',relativePath:'Movies/Action/movie.mkv'},{id:11,title:'Another',relativePath:'Movies/Drama/another.mkv'},{id:12,title:'Root',relativePath:'root.mkv'}]:[{id:1,title:'Series',episode:'First',category:'Comedy',start:1},{id:2,title:'Series',episode:'Second',category:'Comedy',start:2},{id:3,title:'Other',category:'Drama',start:3},{id:4,title:'<img src=x onerror=alert(1)>',category:'Drama'}];
  const q=u.searchParams.get('q');if(q)recordings=recordings.filter(r=>(r.title+' '+r.episode).toLowerCase().includes(q.toLowerCase()));
  return new Response(JSON.stringify({recordings,total:recordings.length}));
 }
 if(u.pathname==='/api/guide'){
  if(options.method==='POST'){BROWSE.records.push(Object.fromEntries(b));return new Response(JSON.stringify({ok:true,accepted:true,pending:true,scheduled:false}));}
  if(a==='recordStatus')return new Response(JSON.stringify({ok:true,scheduled:true}));
  const start=Number(u.searchParams.get('start'))||Math.floor(Date.now()/1800000)*1800000,end=start+4*3600000;
  BROWSE.reads.push(u.search);const airings=[];
  for(let ch=1;ch<=30;ch++)for(let n=0;n<8;n++)airings.push({airingId:ch*100+n,channelNumber:ch+'.1',channelName:'Channel '+ch,channelLogoUrl:ch===2?'https://evil.invalid/logo.svg':ch===1?'api/channelLogo?stationId=1':'/sagex/media/logo/CH'+ch,title:n===0?'Live program':'Future '+n,episode:'Episode '+n,description:'Program description',start:start+n*1800000,end:start+(n+1)*1800000,currentlyAiring:n===0});
  return new Response(JSON.stringify({airings,start,end}));
 }
 if(a==='infoContent'){BROWSE.info.push(Object.fromEntries(b));return new Response(JSON.stringify({ok:true}));}
 if(a==='watchContent'){BROWSE.plays.push(Object.fromEntries(b));return new Response(JSON.stringify({ok:true,accepted:true}));}
 if(a==='contentState')return new Response(JSON.stringify({ok:true,ready:true,layout:'fullscreen'}));
 if(u.pathname.startsWith('/sagex/media/logo/'))return new Response('<svg xmlns="http://www.w3.org/2000/svg" width="40" height="24"><rect width="40" height="24" fill="green"/></svg>',{headers:{'Content-Type':'image/svg+xml'}});
 return fetch.apply(this,arguments);
};})();"""
try:
 with sync_playwright() as pw:
  for engine in ('chromium','webkit'):
   args={'headless':True}
   if engine=='chromium':args.update(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
   browser=getattr(pw,engine).launch(**args)
   for w,h in ((320,568),(393,852),(768,1024)):
    context=browser.new_context(viewport={'width':w,'height':h},has_touch=True,service_workers='block')
    context.add_init_script(F.INIT);context.add_init_script(INIT)
    page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.route('**/sagex/media/logo/**',lambda route:route.fulfill(body='<svg xmlns="http://www.w3.org/2000/svg" width="40" height="24"><rect width="40" height="24" fill="green"/></svg>',content_type='image/svg+xml'))
    page.route('**/api/channelLogo?*',lambda route:route.fulfill(body='<svg xmlns="http://www.w3.org/2000/svg" width="40" height="24"><rect width="40" height="24" fill="green"/></svg>',content_type='image/svg+xml'))
    page.goto(f'http://127.0.0.1:{server.server_port}/miniclient.html')
    page.wait_for_selector('.mc-mobile-folder')
    assert page.locator('#mobileTab-recordings').get_attribute('aria-selected')=='true'
    assert page.locator('.mc-mobile-folder img').count()==0
    page.get_by_role('button',name='▸ Series 2 items').click()
    assert page.locator('.mc-mobile-item').count()==2
    assert page.locator('.mc-mobile-item span').all_text_contents()==['Second','First']
    page.get_by_role('button',name='Info Series',exact=True).first.click()
    page.wait_for_function('BROWSE.info.length===1');assert page.evaluate('BROWSE.info[0].mediaId')=='2'
    assert page.evaluate('BROWSE.plays.length+BROWSE.records.length')==0
    page.locator('.mc-mobile-crumbs button').first.click();assert page.locator('.mc-mobile-folder').count()==3
    page.locator('.mc-mobile-browse select').select_option('category');assert page.locator('.mc-mobile-folder').count()==2
    page.locator('#mobileTab-videos').click();page.wait_for_selector('.mc-mobile-folder')
    page.get_by_role('button',name='▸ Movies 2 items').click();page.get_by_role('button',name='▸ Action 1 items').click()
    assert page.locator('.mc-mobile-item strong').inner_text()=='Movie'
    page.get_by_role('button',name='Info Movie',exact=True).click();page.wait_for_function('BROWSE.info.length===2')
    assert page.evaluate('BROWSE.info[1].mediaId')=='10'
    page.locator('.mc-mobile-crumbs button').first.click();assert page.locator('.mc-mobile-item strong').inner_text()=='Root'
    page.locator('#mobileTab-guide').click();page.wait_for_selector('.mc-mobile-program')
    assert page.locator('.mc-mobile-guide-row').count()==30
    assert page.locator('.mc-mobile-channel img').count()==29
    assert page.locator('img[src*="evil.invalid"]').count()==0
    scroller=page.locator('.mc-mobile-list');assert scroller.evaluate('e=>e.scrollWidth>e.clientWidth&&e.scrollHeight>e.clientHeight')
    # Genuine two-axis scroll preserves both channel labels and time header.
    scroller.evaluate('e=>{e.scrollLeft=300;e.scrollTop=170}')
    page.wait_for_timeout(60)
    rect=scroller.bounding_box();label=page.locator('.mc-mobile-guide-row .mc-mobile-channel').nth(2).bounding_box();header=page.locator('.mc-mobile-guide-header').bounding_box()
    assert abs(label['x']-rect['x'])<2,(label,rect)
    assert abs(header['y']-rect['y'])<2,(header,rect)
    assert page.locator('.mc-mobile-guide-grid').evaluate('e=>e.getBoundingClientRect().width')==1544
    scroller.evaluate('e=>{e.scrollLeft=0;e.scrollTop=0}')
    page.locator('.mc-mobile-program').first.click()
    assert page.locator('.mc-mobile-guide-details').is_visible()
    detail_box=page.locator('.mc-mobile-guide-details').bounding_box()
    assert detail_box['y']+detail_box['height']<=h+1,(w,h,detail_box)
    assert page.locator('.mc-mobile-guide-details [data-content-play]').is_enabled()
    page.get_by_role('button',name='Info Live program',exact=True).click();page.wait_for_function('BROWSE.info.length===3')
    assert page.evaluate('BROWSE.info[2].airingId')=='100'
    assert page.evaluate('BROWSE.plays.length+BROWSE.records.length')==0
    page.get_by_role('button',name='Back to guide',exact=True).click()
    page.locator('.mc-mobile-program').nth(1).click();assert page.locator('.mc-mobile-guide-details [data-content-play]').is_hidden()
    page.get_by_role('button',name='Record Future 1',exact=True).click();page.wait_for_function('BROWSE.records.length===1')
    assert page.evaluate('BROWSE.records[0].airingId')=='101'
    assert page.get_by_role('button',name='Record Future 1',exact=True).is_disabled()
    page.wait_for_function('document.querySelector(".mc-mobile-guide-details").textContent.includes("Scheduled")')
    page.get_by_role('button',name='Back to guide',exact=True).click()
    page.locator('.mc-mobile-program').nth(2).click();page.evaluate('BROWSE.local=false')
    page.get_by_role('button',name='Record Future 2',exact=True).click()
    page.wait_for_function('document.querySelector(".mc-mobile-list-status").textContent.includes("confirmed local")')
    assert page.evaluate('BROWSE.records.length')==1
    page.evaluate('BROWSE.local=true');page.get_by_role('button',name='Back to guide',exact=True).click()
    page.get_by_role('button',name='Later',exact=True).click();page.wait_for_function('BROWSE.reads.some(r=>r.includes("start="))')
    assert page.evaluate('BROWSE.records.length')==1
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),w
    page.set_viewport_size({'width':1024,'height':600});page.wait_for_timeout(100);assert page.locator('#mobileDock').is_hidden()
    assert not errors,errors
    print(f'PASS {engine} {w}x{h}: grouped content/folders/breadcrumbs/Info/Guide logos/sticky two-axis grid/live/future explicit actions/landscape',flush=True)
    context.close()
   browser.close()
finally:server.shutdown()
