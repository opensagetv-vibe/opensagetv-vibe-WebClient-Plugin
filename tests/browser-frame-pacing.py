#!/usr/bin/env python3
"""WEB-048 renderer-paced native frames; real browser, synthetic transport."""
import importlib.util
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('display',ROOT/'tests/browser-vibe-display-smoke.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
with sync_playwright() as pw:
    for engine in ('chromium','webkit'):
        options={'headless':True}
        if engine=='chromium':options.update(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
        browser=getattr(pw,engine).launch(**options)
        context,page,errors=fixture.load(browser,ROOT/'src/main/webapp',size=(852,393))
        assert page.evaluate("TEST.requests.find(r=>r[0]==='start')[1].frameAcks")== 'true'
        fixture.video_start(page);page.wait_for_timeout(300)
        page.evaluate("""()=>{
          const c=document.createElement('canvas');c.width=c.height=1;
          const png=Uint8Array.from(atob(c.toDataURL().split(',')[1]),x=>x.charCodeAt(0));
          const b=new Uint8Array(12+png.length),v=new DataView(b.buffer);
          b[0]=34;v.setInt32(4,616);v.setInt32(8,png.length);b.set(png,12);
          const decode=window.createImageBitmap;
          window.createImageBitmap=async(...a)=>{const image=await decode(...a);return new Promise(resolve=>{TEST.releaseImage=()=>{window.createImageBitmap=decode;resolve(image)}})};
          TEST.emit({type:'gfx',cmd:34,assignedHandle:616,payload:btoa(String.fromCharCode(...b))});
          TEST.emit({...TEST.gfx(30),seq:100,ackRequired:true});
          TEST.emit({type:'videoStop'});
        }""")
        page.wait_for_function("typeof TEST.releaseImage==='function'")
        page.wait_for_function('document.getElementById("videoBounds").hidden')
        assert page.evaluate("TEST.requests.filter(r=>r[0]==='frameAck').length")==0
        page.evaluate('TEST.releaseImage()')
        page.wait_for_function("TEST.requests.some(r=>r[0]==='frameAck'&&r[1].sequence==='100')")
        assert page.evaluate("TEST.requests.find(r=>r[0]==='frameAck')[1].session")== 'native-fixture'
        print('PASS',engine,'ack follows image/render completion; media Stop remains immediate',flush=True)
        page.evaluate("()=>{TEST.emit({...TEST.gfx(30),seq:101,ackRequired:false});TEST.emit({...TEST.gfx(30),seq:-1,ackRequired:true});TEST.emit({...TEST.gfx(30),seq:102,ackRequired:true});}")
        page.wait_for_function("TEST.requests.some(r=>r[0]==='frameAck'&&r[1].sequence==='102')")
        assert page.evaluate("TEST.requests.filter(r=>r[0]==='frameAck').map(r=>r[1].sequence)")==['100','102']
        print('PASS',engine,'legacy/no-negotiation and invalid frame sequences never acknowledged',flush=True)
        assert not errors,errors
        context.close();browser.close()
