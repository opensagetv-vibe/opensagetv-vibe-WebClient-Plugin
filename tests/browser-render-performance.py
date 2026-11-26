#!/usr/bin/env python3
"""WEB-037: count production layout work per native frame, synthetic transport.

Operation counts, not host timings, are the regression criterion. High-DPI
canvas and transparent video-hole pixels must remain correct. Real phone
latency is separate evidence, never inferred from these browser fixtures.
"""
import importlib.util
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('display', ROOT/'tests/browser-vibe-display-smoke.py')
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)

with sync_playwright() as pw:
    for engine in ('chromium', 'webkit'):
        options = {'headless': True}
        if engine == 'chromium':
            options.update(executable_path='/usr/local/bin/vibe-chromium', args=['--no-sandbox'])
        browser = getattr(pw, engine).launch(**options)
        context, page, errors = fixture.load(browser, ROOT/'src/main/webapp', size=(852, 393))
        # Keep toolbar wrapping from scheduling unrelated resize/black frames
        # while deliberately stalling image decode or stopping fake playback.
        page.add_style_tag(content='#toolbar{height:75px!important;min-height:75px!important;max-height:75px!important;overflow:hidden;flex:none!important}')
        fixture.video_start(page)
        # Video/buffer toolbar changes legitimately schedule a UI resize. Do
        # not count that asynchronous frame as part of the measured burst.
        page.wait_for_timeout(500)
        page.evaluate("""()=>{
          TEST.layoutReads=0;TEST.flips=0;
          const rect=Element.prototype.getBoundingClientRect;
          Element.prototype.getBoundingClientRect=function(){if(this.id==='stage')TEST.layoutReads++;return rect.call(this)};
          const draw=CanvasRenderingContext2D.prototype.drawImage;
          CanvasRenderingContext2D.prototype.drawImage=function(...a){if(this.canvas.id==='gfxCanvas')TEST.flips++;return draw.apply(this,a)};
          TEST.benchmark=()=>{TEST.layoutReads=0;TEST.flips=0;
            for(let i=0;i<24;i++)TEST.paint(i%2===0);
          };
          TEST.benchmark();
        }""")
        page.wait_for_function('TEST.flips===24', timeout=15000)
        result = page.evaluate("""()=>({engine:'',frames:TEST.flips,stageLayoutReads:TEST.layoutReads,
          canvas:[document.getElementById('gfxCanvas').width,document.getElementById('gfxCanvas').height],
          transparentPixel:document.getElementById('gfxCanvas').getContext('2d').getImageData(10,100,1,1).data[3]})""")
        result['engine'] = engine
        assert result['stageLayoutReads'] == 0, result
        assert result['transparentPixel'] == 0, result
        page.evaluate("""()=>{
          TEST.timerYields=0;TEST.scheduledFrames=0;
          const timer=window.setTimeout;
          window.setTimeout=function(fn,ms,...args){if(ms===0)TEST.timerYields++;return timer(fn,ms,...args)};
          TEST.flips=0;
          TEST.emit(TEST.gfx(31));
          for(let i=0;i<3072;i++)TEST.emit(TEST.gfx(33));
          TEST.emit(TEST.gfx(17,0,0,40,40,0xff00ff00,0xff00ff00,0xff00ff00,0xff00ff00));
          TEST.emit(TEST.gfx(30));
        }""")
        page.wait_for_function('TEST.flips>=1', timeout=15000)
        result['burstTimerYields'] = page.evaluate('TEST.timerYields')
        result['burstPixel'] = page.locator('#gfxCanvas').evaluate('c=>[...c.getContext("2d").getImageData(10,10,1,1).data]')
        assert result['burstPixel'] == [0,255,0,255], result
        assert result['burstTimerYields'] < 20, result
        page.locator('#remoteToggle').evaluate('e=>e.click()')
        # Phone utilities now live behind the gear, unlike desktop controls.
        if page.locator('#phoneToolsToggle').is_visible():
            page.locator('#phoneToolsToggle').click()
        page.locator('#diagnosticsBtn').click()
        page.locator('#downloadReport').click()
        page.wait_for_function("TEST.requests.some(r=>r[0]==='report')")
        report = json.loads(page.evaluate("TEST.requests.filter(r=>r[0]==='report').at(-1)[1].browserJson"))
        timing = report['ui']['renderPerformance']
        assert timing['presentedFrames'] >= 24 and timing['schedulerYields'] >= result['burstTimerYields'], timing
        assert timing['inputActionLast'] in ('','command','click','key','text','seek'),timing
        assert all(isinstance(value, (int,float)) and value >= 0 for key,value in timing.items() if key!='inputActionLast'), timing
        result['diagnostics'] = timing
        page.locator('#closeSettings').click()
        page.evaluate("""()=>{const forward=window.fetch;TEST.failInput=true;
          window.fetch=(url,options)=>{if(new URL(url).searchParams.get('action')==='command'&&TEST.failInput){TEST.failInput=false;return Promise.resolve(new Response('{"error":"intentional input failure"}',{status:503}))}return forward(url,options)};
        }""")
        page.locator('#nav_down').click()
        page.wait_for_timeout(80)
        page.locator('#nav_down').click()
        page.wait_for_timeout(80)
        page.locator('#diagnosticsBtn').click()
        before = page.evaluate("TEST.requests.filter(r=>r[0]==='report').length")
        page.locator('#downloadReport').click()
        page.wait_for_function("n=>TEST.requests.filter(r=>r[0]==='report').length>n", arg=before)
        report = json.loads(page.evaluate("TEST.requests.filter(r=>r[0]==='report').at(-1)[1].browserJson"))
        timing = report['ui']['renderPerformance']
        assert timing['inputFailures'] == 1 and timing['inputAcks'] == 1, timing
        assert timing['inputAckMsLast'] >= 0 and timing['inputAckMsMax'] >= timing['inputAckMsLast'], timing
        result['inputFailuresCountedSeparately'] = True
        page.locator('#closeSettings').click()
        page.evaluate("""()=>{
          const source=document.createElement('canvas');source.width=source.height=1;
          const c=source.getContext('2d');c.fillStyle='#ff0000';c.fillRect(0,0,1,1);
          const png=Uint8Array.from(atob(source.toDataURL().split(',')[1]),c=>c.charCodeAt(0));
          const bytes=new Uint8Array(12+png.length),v=new DataView(bytes.buffer);
          bytes[0]=34;v.setInt32(4,616);v.setInt32(8,png.length);bytes.set(png,12);
          const decode=window.createImageBitmap;
          window.createImageBitmap=async(...a)=>{let img=await decode(...a);return new Promise(resolve=>{TEST.releaseImage=()=>{window.createImageBitmap=decode;resolve(img)}})};
          TEST.flips=0;TEST.emit(TEST.gfx(31));
          TEST.emit({type:'gfx',cmd:34,assignedHandle:616,payload:btoa(String.fromCharCode(...bytes))});
          TEST.emit(TEST.gfx(24,0,0,30,30,616,0,0,1,1,0xffffffff));TEST.emit(TEST.gfx(30));
          TEST.emit({type:'videoStop'});
        }""")
        page.wait_for_function("typeof TEST.releaseImage==='function'")
        page.wait_for_function('document.getElementById("videoBounds").hidden',timeout=5000)
        assert page.locator('#videoBounds').is_hidden(), 'media stop blocked behind GFX read backpressure/image decode'
        assert page.evaluate('TEST.flips') == 0, 'dependent frame passed undecoded image'
        page.evaluate('TEST.releaseImage()')
        page.wait_for_function('TEST.flips>=1')
        pixel = page.locator('#gfxCanvas').evaluate('c=>[...c.getContext("2d").getImageData(10,10,1,1).data]')
        assert pixel == [255,0,0,255], (engine,pixel,page.evaluate('TEST.flips'))
        result['imageOrderingAndImmediateMediaStop'] = True
        assert not errors, errors
        print(json.dumps(result), flush=True)
        context.close()
        browser.close()
