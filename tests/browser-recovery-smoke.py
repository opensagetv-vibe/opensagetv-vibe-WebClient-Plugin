#!/usr/bin/env python3
"""Production browser UI + mocked HTTP for connection-loss and recovery; not live SageTV."""
from pathlib import Path
import json, os, re, time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT/'src/main/webapp'
count=0
OUT=Path(os.environ.get('SAGETV_ARTIFACT_DIR',ROOT/'artifacts/active/WEB-025'));OUT.mkdir(parents=True,exist_ok=True)
STAMP=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())

def passed(name):
    global count
    count+=1
    print('PASS '+name, flush=True)

def fixture(browser, fallback=False, initial_dead=False):
    page=browser.new_page(viewport={'width':1000,'height':650},service_workers='block',accept_downloads=True)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    html=re.sub(r'<script[^>]*>.*?</script>','',(WEB/'miniclient.html').read_text(),flags=re.S)
    html=re.sub(r'<link[^>]*>','',html)
    page.set_content(html);page.add_style_tag(content=(WEB/'css/miniclient.css').read_text())
    page.evaluate(r'''(()=>{
      const T=window.TEST={requests:[],reports:[],stream:null,alive:true,id:0,blob:null,beacons:[],storage:{}};
      Object.defineProperty(navigator,'sendBeacon',{configurable:true,value:(u,b)=>{T.beacons.push(String(b));return true;}});
      const nativeURL=URL.createObjectURL.bind(URL);URL.createObjectURL=blob=>{T.blob=blob;return nativeURL(blob);};
      T.emit=item=>T.stream.enqueue(new TextEncoder().encode(JSON.stringify(item)+'\n'));
      T.end=()=>{T.stream.close();T.stream=null;};
      window.fetch=async(url,options={})=>{
        const q=new URLSearchParams(new URL(url).search);
        if(options.body)new URLSearchParams(options.body).forEach((v,k)=>q.set(k,v));
        const d=Object.fromEntries(q),a=d.action,path=new URL(url).pathname;T.requests.push([a,d,path]);
        if(path.endsWith('/api/support')){if(a==='status')return new Response('{"configured":false,"writesEnabled":false}');if(a==='report'){T.reports.push(d);return new Response(new Blob(['PKfixture'],{type:'application/zip'}),{headers:{'Content-Type':'application/zip'}});}}
        if(a==='start'){if(T.delayStart)await new Promise(r=>setTimeout(r,T.delayStart));return new Response(JSON.stringify({session:'recovery-'+(++T.id),clientId:d.clientId,alive:!T.initialDead,error:T.initialDead?'SocketException: Connection reset':''}));}
        if(a==='status'){if(T.status404)return new Response('{"error":"Session expired"}',{status:404});if(T.statusError)throw Error('Network unavailable');return new Response(JSON.stringify({alive:T.alive,error:T.alive?'':'SocketException: Connection reset',connection:{lastGfxCommand:'get property GFX_RESOLUTION',reconnectAttempts:3}}));}
        if(a==='events')return new Response('[]');
        if(a==='stream'){if(T.delayStream404){T.delayStream404=false;T.stream404Waiting=true;await new Promise(r=>{T.release404=r;});return new Response('{}',{status:404});}return new Response(new ReadableStream({start(c){T.stream=c;}}));}
        return new Response('{"ok":true}');
      };
    })();''')
    page.evaluate('(x)=>{TEST.initialDead=x.initialDead;if(x.fallback){TEST.alive=false;window.ReadableStream=undefined;}}',{'fallback':fallback,'initialDead':initial_dead})
    for name in ['miniclient-core.js','miniclient-input.js','miniclient-streaming.js','miniclient-caption-authority.js','atsc-captions.js','miniclient-captions.js','miniclient-subtitles.js','miniclient-dvd-spu.js','miniclient-playback.js','miniclient-experience.js','miniclient-support.js']:
        page.evaluate((WEB/'js'/name).read_text())
    main=(WEB/'js/miniclient.js').read_text()
    page.evaluate("(function(location,localStorage){\n"+main+"\n})({href:'https://fixture.test/miniclient.html',origin:'https://fixture.test',search:'?ui=640x360'},{getItem:k=>TEST.storage[k]||(k==='sagetvWebMiniClientSettings.v1'?'{\"renderOnly\":true}':null),setItem:(k,v)=>{TEST.storage[k]=v;}})")
    return page,errors

def emit(page,item):page.evaluate('x=>TEST.emit(x)',item)
def requests(page,action):return page.evaluate("a=>TEST.requests.filter(x=>x[0]===a && x[2].endsWith('/api/miniclient')).length",action)

def visibility(page,hidden):
    page.evaluate("hidden=>{Object.defineProperty(document,'hidden',{configurable:true,value:hidden});document.dispatchEvent(new Event('visibilitychange'));}",hidden)

def mobile_return_gates(browser,engine):
    page,errors=fixture(browser);page.wait_for_function('TEST.stream!==null')
    page.set_viewport_size({'width':393,'height':793})
    first=page.evaluate("TEST.requests.find(r=>r[0]==='start')[1].clientId")
    visibility(page,True);page.evaluate('TEST.status404=true;TEST.delayStart=100')
    visibility(page,False)
    page.evaluate("window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:false}));window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))")
    page.wait_for_function('TEST.id===2');page.wait_for_timeout(200)
    assert requests(page,'start')==2 and requests(page,'stop')==1
    assert page.evaluate("TEST.requests.filter(r=>r[0]==='start').every(r=>r[1].clientId===TEST.storage.sagetvWebMiniClientId)")
    assert page.evaluate("TEST.storage.sagetvWebMiniClientId")==first
    assert not page.locator('#connectionRecovery').is_visible()
    passed(engine+' foreground404 recreates once with stable identity; duplicate lifecycle events do not storm')
    page.evaluate('TEST.status404=false;TEST.delayStart=0')
    visibility(page,True);visibility(page,False);page.wait_for_timeout(200)
    assert requests(page,'start')==2
    passed(engine+' healthy foreground return keeps native session and never replays media start/seek')
    for persisted in (False,True,False):
        before=requests(page,'start');page.evaluate("window.dispatchEvent(new PageTransitionEvent('pagehide',{persisted:true}))")
        page.evaluate('p=>window.dispatchEvent(new PageTransitionEvent("pageshow",{persisted:p}))',persisted)
        page.wait_for_function('(n)=>TEST.id===n',arg=before+1)
    assert len(page.evaluate('TEST.beacons'))==3
    passed(engine+' repeated pagehide returns work with and without BFCache flag')
    visibility(page,True);page.evaluate('TEST.statusError=true');visibility(page,False)
    page.wait_for_function('!document.querySelector("#connectionRecovery").hidden')
    before=requests(page,'start');page.wait_for_timeout(200);assert requests(page,'start')==before
    retry=page.locator('#retryConnectionBtn');assert retry.is_visible() and retry.is_enabled()
    box=retry.bounding_box();assert box['height']>=44 and box['x']>=0 and box['x']+box['width']<=393
    assert page.locator('#retryConnectionBtn').evaluate('e=>document.elementFromPoint(e.getBoundingClientRect().x+10,e.getBoundingClientRect().y+10)===e')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    passed(engine+' offline foreground preserves native session and shows reachable stage retry')
    page.evaluate('TEST.statusError=false');retry.click();page.wait_for_function('(n)=>TEST.id===n',arg=before+1)
    assert not page.locator('#connectionRecovery').is_visible()
    assert not page.evaluate("TEST.requests.some(r=>['seek','command','play','recover'].includes(r[0]))")
    assert not errors,errors
    passed(engine+' explicit mobile retry recovers without replaying remote commands or playback requests')
    page.close()
    page,errors=fixture(browser);page.wait_for_function('TEST.stream!==null')
    visibility(page,True)
    emit(page,{'type':'error','fatal':True,'message':'Browser GFX queue overflow; reconnect required'})
    page.wait_for_function("document.body.classList.contains('mc-connection-lost')")
    page.evaluate('TEST.initialDead=true');visibility(page,False)
    page.wait_for_function('TEST.id===2 && !document.querySelector("#connectionRecovery").hidden')
    page.evaluate("window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:false}));window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))")
    page.wait_for_timeout(250);assert requests(page,'start')==2
    assert page.locator('#retryConnectionBtn').is_enabled() and not errors,errors
    passed(engine+' background GFX overflow gets one return attempt; failed replacement remains manual, no lifecycle loop')
    for w,h in ((320,568),(852,393)):
        page.set_viewport_size({'width':w,'height':h});page.evaluate("document.body.classList.add('mc-fullscreen','mc-standalone')")
        retry=page.locator('#retryConnectionBtn');box=retry.bounding_box()
        assert retry.is_visible() and box['height']>=44 and box['y']>=0 and box['y']+box['height']<=h
        assert box['x']>=0 and box['x']+box['width']<=w
        assert retry.evaluate('e=>{const r=e.getBoundingClientRect();return document.elementFromPoint(r.x+r.width/2,r.y+r.height/2)===e}')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    passed(engine+' narrow and short standalone/fullscreen recovery actions stay inside viewport and hit-testable')
    page.close()
    page,errors=fixture(browser);page.wait_for_function('TEST.stream!==null')
    page.evaluate('TEST.delayStream404=true;TEST.end()');page.wait_for_function('TEST.stream404Waiting===true')
    page.locator('#reconnectBtn').evaluate('e=>e.click()')
    page.wait_for_function('TEST.id===2');page.evaluate('TEST.release404()');page.wait_for_timeout(150)
    assert not page.evaluate("document.body.classList.contains('mc-connection-lost')") and not errors,errors
    passed(engine+' late old-generation HTTP404 cannot close the replacement session')
    page.close()

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.getenv('CHROMIUM_PATH','/usr/local/bin/vibe-chromium'),headless=True,args=['--no-sandbox'])
    page,errors=fixture(browser)
    page.wait_for_function('TEST.stream!==null')
    assert not page.locator('#toolbar').is_visible()
    emit(page,{'type':'error','fatal':True,'message':'GFX connection ended: SocketException: Connection reset'})
    page.wait_for_function("document.body.classList.contains('mc-connection-lost')")
    assert page.locator('#toolbar').is_visible() and page.locator('#reconnectBtn').is_enabled()
    assert page.locator('#connectionDiagnosticsBtn').is_visible()
    assert 'Connection reset' in page.locator('#osdMessage').inner_text()
    passed('fatal native reset reveals recovery/diagnostic buttons in render-only view')
    before=requests(page,'stream');page.wait_for_timeout(1000)
    assert requests(page,'stream')==before
    passed('terminal native failure stops the empty HTTP reconnect loop')
    page.locator('#connectionDiagnosticsBtn').click()
    page.wait_for_function('TEST.reports.length>0')
    report=json.loads(page.evaluate('TEST.reports.slice(-1)[0].browserJson'))
    assert 'Connection reset' in report['failureSnapshot']['reason']
    assert report['serverConnection']['connection']['lastGfxCommand']=='get property GFX_RESOLUTION'
    passed('one-click diagnostics contains failure snapshot and native connection trace')
    page.screenshot(path=str(OUT/(STAMP+'-recovery-desktop.png')))
    page.locator('#reconnectBtn').click()
    page.wait_for_function('TEST.id===2 && !document.body.classList.contains("mc-connection-lost")')
    assert requests(page,'stop')==1 and requests(page,'start')==2
    assert not errors,errors
    passed('explicit Reconnect stops old session and creates one replacement')
    page.close()

    page,errors=fixture(browser);page.wait_for_function('TEST.stream!==null')
    emit(page,{'type':'status','state':'gfx-reconnecting'})
    page.wait_for_function("document.querySelector('#connectionStatus').textContent.includes('Recovering')")
    emit(page,{'type':'status','state':'gfx-reconnected'})
    page.wait_for_function("document.querySelector('#connectionStatus').textContent.includes('GFX recovered')")
    assert requests(page,'start')==1 and requests(page,'stop')==0
    assert not page.evaluate("document.body.classList.contains('mc-connection-lost')")
    passed('successful native GFX recovery keeps the browser session instead of restarting playback')
    page.close()

    page,errors=fixture(browser);page.wait_for_function('TEST.stream!==null')
    page.evaluate('TEST.alive=false;TEST.end()')
    page.wait_for_function("document.body.classList.contains('mc-connection-lost')")
    assert requests(page,'status')==1 and requests(page,'stream')==1
    passed('HTTP EOF detects dead native session even when terminal event was missed')
    page.close()

    page,errors=fixture(browser);page.wait_for_function('TEST.stream!==null');page.evaluate('TEST.end()')
    page.wait_for_function("TEST.requests.filter(x=>x[0]==='stream').length===2")
    assert requests(page,'start')==1
    passed('transient HTTP EOF reconnects only HTTP while native session remains alive')
    page.close()

    page,errors=fixture(browser,fallback=True)
    page.wait_for_function("document.body.classList.contains('mc-connection-lost')")
    before=requests(page,'events');page.wait_for_timeout(300);assert requests(page,'events')==before
    passed('long-poll fallback also stops when native session is dead')
    page.close()

    page,errors=fixture(browser,initial_dead=True)
    page.wait_for_function("document.body.classList.contains('mc-connection-lost')")
    assert requests(page,'stream')==0 and page.locator('#connectionDiagnosticsBtn').is_visible()
    passed('startup failure returned by start is not shown as a connected session')
    page.set_viewport_size({'width':390,'height':700})
    page.wait_for_timeout(200)
    assert page.locator('#retryConnectionBtn').is_visible() and page.locator('#recoveryDiagnosticsBtn').is_visible()
    assert page.locator('#retryConnectionBtn').bounding_box()['height']>=44
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.screenshot(path=str(OUT/(STAMP+'-recovery-mobile.png')))
    passed('mobile error recovery controls remain visible without horizontal clipping')
    page.close();mobile_return_gates(browser,'Chromium');browser.close()
    browser=p.webkit.launch(headless=True);mobile_return_gates(browser,'WebKit');browser.close()
print(f'Browser recovery: {count} tests PASS (production DOM/JavaScript, mocked HTTP)')
