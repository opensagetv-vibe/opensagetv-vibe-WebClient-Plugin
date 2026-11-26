#!/usr/bin/env python3
"""iOS event path: real production renderer, synthetic finite-poll server."""
import importlib.util,os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('display',ROOT/'tests/browser-vibe-display-smoke.py')
F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
POLL=r"""
(()=>{
 Object.defineProperty(navigator,'userAgent',{value:'iPhone AppleWebKit Safari',configurable:true});
 const original=window.fetch;
 TEST.pollPending=0;TEST.pollPeak=0;TEST.pollAborts=0;TEST.pending=[];
 TEST.emit=e=>{TEST.pending.push(e);if(TEST.deliver)TEST.deliver();};
 window.fetch=(url,options={})=>{
   const u=new URL(url,location.href);
   if(u.pathname!='/api/miniclient'||u.searchParams.get('action')!=='events')return original(url,options);
   TEST.requests.push(['events',Object.fromEntries(u.searchParams)]);
   TEST.pollPeak=Math.max(TEST.pollPeak,++TEST.pollPending);
   return new Promise((resolve,reject)=>{
     const clear=()=>{TEST.pollPending--;TEST.deliver=null;options.signal.removeEventListener('abort',abort);};
     const abort=()=>{clear();TEST.pollAborts++;reject(new DOMException('Aborted','AbortError'));};
     TEST.deliver=()=>{if(TEST.pending.length){const events=TEST.pending.splice(0,500);clear();resolve(new Response(JSON.stringify(events)));}};
     options.signal.addEventListener('abort',abort,{once:true});TEST.deliver();
   });
 };
})();
"""
with sync_playwright() as pw:
  for engine in ('chromium','webkit'):
    options={'headless':True}
    if engine=='chromium':options.update(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
    browser=getattr(pw,engine).launch(**options)
    # Fixture readiness expects a stream marker; this marker is NOT an HTTP
    # streaming response. Production must request finite 'events' only.
    context,page,errors=F.load(browser,ROOT/'src/main/webapp',main_transform=lambda s:POLL+'TEST.stream={enqueue:()=>{}};'+s)
    page.wait_for_timeout(300)
    page.evaluate("()=>{TEST.emit(TEST.gfx(31));TEST.emit(TEST.gfx(17,0,0,40,40,0xff00ff00,0xff00ff00,0xff00ff00,0xff00ff00));TEST.emit({...TEST.gfx(30),seq:811,ackRequired:true});}")
    page.wait_for_function("TEST.requests.some(r=>r[0]==='frameAck'&&r[1].sequence==='811')")
    assert page.locator('#gfxCanvas').evaluate('c=>[...c.getContext("2d").getImageData(10,10,1,1).data]')==[0,255,0,255]
    assert page.evaluate("!TEST.requests.some(r=>r[0]==='stream')&&TEST.pollPeak===1")
    print('PASS',engine,'iOS finite responses deliver final frame/ACK with one poll',flush=True)
    page.wait_for_function('TEST.pollPending===1')
    page.evaluate("document.getElementById('reconnectBtn').click()")
    page.wait_for_function('TEST.pollAborts===1&&TEST.pollPending===1')
    assert not errors,errors
    print('PASS',engine,'reconnect aborts outstanding old poll; no duplicate consumer/error',flush=True)
    # Delay a compressed image: media Stop in the next poll must still run.
    page.evaluate("""()=>{
      TEST.startVideo();
      const c=document.createElement('canvas');c.width=c.height=1;
      const png=Uint8Array.from(atob(c.toDataURL().split(',')[1]),x=>x.charCodeAt(0)),b=new Uint8Array(12+png.length),v=new DataView(b.buffer);
      b[0]=34;v.setInt32(4,616);v.setInt32(8,png.length);b.set(png,12);
      const decode=window.createImageBitmap;window.createImageBitmap=async(...a)=>{const image=await decode(...a);return new Promise(resolve=>{TEST.release=()=>{window.createImageBitmap=decode;resolve(image);}})};
      TEST.emit({type:'gfx',cmd:34,assignedHandle:616,payload:btoa(String.fromCharCode(...b))});
    }""")
    page.wait_for_function("typeof TEST.release==='function'")
    page.evaluate("TEST.emit({type:'videoStop'})")
    page.wait_for_function('document.getElementById("videoBounds").hidden',timeout=2000)
    page.evaluate('TEST.release()');assert not errors,errors
    print('PASS',engine,'next-poll media Stop is not blocked by compressed image decode',flush=True)
    context.close();browser.close()
