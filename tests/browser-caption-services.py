#!/usr/bin/env python3
"""Real caption controller/decoder and DOM sink; synthetic state/A53/clock.

Not full STV negotiation, real vendor playback or physical phone acceptance.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
with sync_playwright() as pw:
    for engine in ('chromium', 'webkit'):
        options = {'headless': True}
        if engine == 'chromium':
            options.update(executable_path='/usr/local/bin/vibe-chromium', args=['--no-sandbox'])
        browser = getattr(pw, engine).launch(**options)
        page = browser.new_page()
        page.set_content('<div id="caption"></div>')
        for name in ('atsc-captions.js', 'miniclient-captions.js'):
            page.add_script_tag(content=(ROOT / 'src/main/webapp/js' / name).read_text())
        page.evaluate("""()=>{
          window.G={time:1000,renders:0};
          G.c=new SageMiniCaptions({Decoder:SageAtscCaptions,timeMs:()=>G.time,
            fetch:async()=>({cursor:0,packets:[]}),
            render:text=>{caption.textContent=text;G.renders++;},clearBitmap:()=>{}});
          G.c.start({hlsSession:'synthetic-caption-only',
            captionAuthority:{mode:'stv',stvStateSeen:true,stvState:1},
            streamSettings:{requested:{captions:'608',captionService:1,captionOffsetMs:0}}});
          G.c.decoder.pushCcData(Uint8Array.of(0xfc,0x14,0x20,0xfc,0x48,0x49,0xfc,0x14,0x2f),1000);
        }""")
        page.wait_for_function('caption.textContent === "HI"')
        page.evaluate('G.c.setSageTvState(2,true)')
        assert page.locator('#caption').text_content() == ''
        assert page.evaluate('G.time') == 1000
        page.evaluate('G.c.setSageTvState(1,true)')
        assert page.locator('#caption').text_content() == 'HI'
        before = page.evaluate('G.renders')
        page.evaluate('G.c.setSageTvState(1,true)')
        assert page.evaluate('G.renders') == before
        page.evaluate('G.c.setSageTvState(0,true)')
        assert page.locator('#caption').text_content() == ''
        page.evaluate('G.c.setSageTvState(2,true)')
        assert page.locator('#caption').text_content() == ''
        page.evaluate('G.c.stop()')
        assert page.evaluate('G.c.timer===null && G.c.pollTimer===null && G.c.decoder===null')
        print('PASS', engine, '8 controller/decoder/DOM service, pause-clock, Off and cleanup checks', flush=True)
        page.evaluate("""()=>{
          G.time=11000;caption.textContent='current DVB page';
          G.c.options={captionOffsetMs:1000};
          G.future={active:true,selectedTrack:-1,services:[],selectionChangedMs:16000};
          if(G.c.retiredBroadcastService(G.future,false))throw Error('Early PMT retirement');
        }""")
        assert page.locator('#caption').text_content() == 'current DVB page'
        page.evaluate("G.time=16999;if(G.c.retiredBroadcastService(G.future,false))throw Error('Caption delay ignored')")
        assert page.locator('#caption').text_content() == 'current DVB page'
        page.evaluate("G.time=17000;if(!G.c.retiredBroadcastService(G.future,false))throw Error('Due PMT not retired')")
        assert page.locator('#caption').text_content() == ''
        page.evaluate("caption.textContent='off';G.time=0;G.future.active=false;if(!G.c.retiredBroadcastService(G.future,false))throw Error('Explicit Off must be immediate')")
        assert page.locator('#caption').text_content() == ''
        print('PASS', engine, '4 source-read-ahead/offset/due-retirement/immediate-Off DOM checks', flush=True)
        browser.close()
