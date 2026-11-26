#!/usr/bin/env python3
"""WEB-034 real production presenter with generated CEA, not physical reception."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import importlib.util,json,os,threading,time
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ.get('SAGETV_ARTIFACT_DIR',ROOT/'artifacts/active/WEB-034'));OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('display',ROOT/'tests/browser-vibe-display-smoke.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'src/main/webapp')))
threading.Thread(target=server.serve_forever,daemon=True).start()
results=[];stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
try:
  with sync_playwright() as pw:
    for engine in ('chromium','webkit'):
      opts={'headless':True}
      if engine=='chromium':opts.update(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
      browser=getattr(pw,engine).launch(**opts)
      for width,height in ((852,393),(393,852),(320,568),(1440,900)):
        ctx=browser.new_context(viewport={'width':width,'height':height},service_workers='block')
        ctx.add_init_script(fixture.INIT);page=ctx.new_page();errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        # Capture the production presenter's callback, without exporting private
        # app functions or starting a simulated video as playback evidence.
        prefix="{const Real=SageMiniCaptions;window.SageMiniCaptions=class extends Real{constructor(o){super(o);TEST.captionOptions=o}};}\n"
        page.route('**/js/miniclient.js*',lambda route:route.fulfill(content_type='application/javascript',body=prefix+(ROOT/'src/main/webapp/js/miniclient.js').read_text()))
        page.goto(f'http://127.0.0.1:{server.server_port}/miniclient.html',wait_until='domcontentloaded')
        page.wait_for_function('TEST.stream!==null')
        page.wait_for_timeout(250)
        page.add_style_tag(content='#videoBounds{display:block!important;left:0!important;top:0!important;width:100%!important;height:100%!important}')
        page.evaluate("""()=>{const bounds=document.getElementById('videoBounds');bounds.hidden=false;Object.assign(bounds.style,{left:'0px',top:'0px',width:'100%',height:'100%'});TEST.decoder=new SageAtscCaptions({onCaption:TEST.captionOptions.render})}""")
        page.wait_for_function('!!TEST.decoder')
        page.evaluate("""()=>{TEST.at=0;TEST.pair=(a,b)=>{TEST.at+=50;TEST.decoder.pushCcData(new Uint8Array([252,a,b]),TEST.at);TEST.decoder.updateTime(TEST.at)};TEST.text=s=>{for(let i=0;i<s.length;i+=2)TEST.pair(s.charCodeAt(i),s.charCodeAt(i+1)||0)};TEST.pair(20,37);TEST.text('A')}""")
        def box():return page.locator('.caption-cea-grid').bounding_box()
        first=box();assert first,page.locator('#localCaptions').evaluate('e=>({html:e.outerHTML,parent:e.parentElement.outerHTML.slice(0,200)})')
        page.evaluate("TEST.text(' LONGER CAPTION LINE')");second=box()
        assert abs(first['x']-second['x'])<.5 and abs(first['width']-second['width'])<.5,(first,second)
        assert abs(first['y']-second['y'])<.5,'typing must not shift fixed roll-up window'
        page.evaluate("TEST.pair(20,45)")
        assert page.locator('.caption-cea-grid').text_content()=='A LONGER CAPTION LINE\n'
        assert abs(box()['y']-first['y'])<.5,'CR must move rows, not the box'
        page.evaluate("TEST.text('SECOND');TEST.pair(20,45);TEST.text('THIRD')")
        assert page.locator('.caption-cea-grid').text_content()=='SECOND\nTHIRD'
        assert page.locator('.caption-cea-grid').evaluate("e=>getComputedStyle(e).textAlign")=='left'
        assert first['x']>=0 and first['x']+first['width']<=width+1
        page.screenshot(path=str(OUT/f'{stamp}-{engine}-{width}-rollup.png'))
        page.evaluate("TEST.decoder.updateTime(TEST.at+16000)")
        assert page.locator('#localCaptions').text_content()==''
        page.evaluate("""()=>{TEST.decoder=new SageAtscCaptions({service:'708-1',onCaption:TEST.captionOptions.render});TEST.digital=(bytes,time)=>{const block=[32|bytes.length,...bytes];if(block.length%2===0)block.push(0);TEST.decoder.pushDtvcc(3,(block.length+1)/2,block[0],time);for(let i=1;i<block.length;i+=2)TEST.decoder.pushDtvcc(2,block[i],block[i+1],time);TEST.decoder.updateTime(time)};TEST.digital([152,48,74,104,113,7,0,65],0)}""")
        digital=page.locator('.caption-708-window').bounding_box()
        page.evaluate("TEST.digital([66,67,68,69,70,71,72],100)")
        extended=page.locator('.caption-708-window').bounding_box()
        assert all(abs(digital[k]-extended[k])<.5 for k in ('x','y','width','height')),(digital,extended)
        page.evaluate("TEST.digital([13,83,69,67,79,78,68],1000);TEST.digital([13,84,72,73,82,68],2000)")
        assert page.locator('.caption-708-window').text_content()=='SECOND\nTHIRD'
        page.evaluate("TEST.decoder.updateTime(18000)")
        assert page.locator('#localCaptions').text_content()==''
        page.evaluate("TEST.captionOptions.render('TELETEXT PAGE','teletext',{type:'teletext'})")
        assert page.locator('.caption-cea-grid').count()==0,'Teletext must retain separate page semantics'
        page.evaluate("TEST.captionOptions.render('')")
        assert not errors,errors
        results.append({'engine':engine,'viewport':[width,height],'fixedWindow':first,'passed':True})
        print('PASS',engine,width,'fixed608/708 origin, upward CR, stale clear, Teletext independent',flush=True)
        ctx.close()
      browser.close()
finally:
  server.shutdown()
  (OUT/f'{stamp}-caption-rollup.json').write_text(json.dumps({'generatedCea':True,'physicalPhone':False,'results':results},indent=2)+'\n')
