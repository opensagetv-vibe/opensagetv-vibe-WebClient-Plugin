#!/usr/bin/env python3
"""WEB-026: retained full-screen native surfaces must follow orientation."""
import importlib.util
import os
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
        context,page,errors=fixture.load(browser,ROOT/'src/main/webapp',size=(393,793))
        page.evaluate("""()=>{let e=TEST.gfx(37,TEST.width,TEST.height);e.assignedHandle=71;TEST.emit(e);
          let small=TEST.gfx(37,20,20);small.assignedHandle=72;TEST.emit(small);
          TEST.originalWidth=TEST.width;TEST.originalHeight=TEST.height;
          const nativeDraw=CanvasRenderingContext2D.prototype.drawImage;
          CanvasRenderingContext2D.prototype.drawImage=function(source,...args){
            if(TEST.recordDraws)TEST.draws.push({source:[source.width,source.height],args});return nativeDraw.call(this,source,...args)};
          TEST.paintSurface=(legacy=false)=>{TEST.draws=[];TEST.recordDraws=true;
            TEST.emit(TEST.gfx(31));TEST.emit(TEST.gfx(38,71));
            TEST.emit(TEST.gfx(18,0,0,TEST.width,TEST.height,0xff00ff00));TEST.emit(TEST.gfx(38,0));
            const cw=legacy?TEST.originalWidth:TEST.width,ch=legacy?TEST.originalHeight:TEST.height;
            TEST.emit(TEST.gfx(24,0,0,cw,ch,71,0,0,cw,ch,0xffffffff));
            TEST.emit(TEST.gfx(24,0,0,20,20,72,0,0,20,20,0xffffffff));TEST.emit(TEST.gfx(30));};} """)
        for w,h in ((852,393),(393,793),(852,393)):
            page.set_viewport_size({'width':w,'height':h})
            # Portrait now negotiates a landscape TV surface above its dock;
            # don't confuse window CSS width with the bounded logical minimum.
            page.wait_for_function('(portrait)=>portrait ? TEST.width>=640&&Math.abs(TEST.width/TEST.height-16/9)<.02 : TEST.width===852',arg=h>w)
            page.wait_for_timeout(180);page.evaluate('TEST.paintSurface()');page.wait_for_timeout(150)
            data=page.locator('#gfxCanvas').evaluate('c=>[...c.getContext("2d").getImageData(Math.floor(c.width*.8),Math.floor(c.height*.5),1,1).data]')
            assert data==[0,255,0,255],(engine,w,h,'retained surface clipped the right side',data)
            page.evaluate('TEST.paintSurface(true)');page.wait_for_timeout(150)
            data=page.locator('#gfxCanvas').evaluate('c=>[...c.getContext("2d").getImageData(Math.floor(c.width*.8),Math.floor(c.height*.5),1,1).data]')
            assert data==[0,255,0,255],(engine,w,h,'old allocation copy bounds clipped screen',data)
            assert page.evaluate('TEST.draws.some(d=>d.source[0]===20&&d.source[1]===20)'), 'small surface changed'
        assert not errors,errors
        print('PASS',engine,'portrait/landscape/portrait retained full-screen surface and small handle',flush=True)
        context.close();browser.close()
