#!/usr/bin/env python3
"""WEB-042 landscape popup regression; synthetic wire, real production renderer."""
import argparse,importlib.util,json,os,time
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ['SAGETV_ARTIFACT_DIR']);OUT.mkdir(parents=True,exist_ok=True)
parser=argparse.ArgumentParser();parser.add_argument('--expect-stale',action='store_true');args=parser.parse_args()
spec=importlib.util.spec_from_file_location('fixture',ROOT/'tests/browser-vibe-display-smoke.py')
F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
rows=[]
with sync_playwright() as pw:
  for engine in ('chromium','webkit'):
    options={'headless':True}
    if engine=='chromium':options.update(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
    browser=getattr(pw,engine).launch(**options)
    context,page,errors=F.load(browser,ROOT/'src/main/webapp',settings={'uiResolution':'1280x720'},size=(852,393))
    page.wait_for_function('TEST.stream!==null');page.wait_for_timeout(250)
    # A surface can be returned from the server's cache after more than one
    # resize, not just while its original allocation equals the last UI size.
    page.evaluate("""()=>{TEST.resize(622,1080);TEST.resize(536,1080);TEST.resize(1704,786);
      TEST.emit(TEST.gfx(31));let e=TEST.gfx(37,622,1080);e.assignedHandle=771;TEST.emit(e);
      TEST.emit(TEST.gfx(38,771));TEST.emit(TEST.gfx(18,0,0,1704,786,0));
      TEST.emit(TEST.gfx(17,446,130,850,480,0xff336699,0xff336699,0xff336699,0xff336699));
      TEST.emit(TEST.gfx(17,1100,180,100,40,0xff00ff00,0xff00ff00,0xff00ff00,0xff00ff00));
      TEST.emit(TEST.gfx(38,0));TEST.emit(TEST.gfx(24,446,130,850,480,771,446,130,850,480,0xffffffff));TEST.emit(TEST.gfx(30));}""")
    page.wait_for_timeout(400)
    pixel=page.locator('#gfxCanvas').evaluate('c=>[...c.getContext("2d").getImageData(1140,200,1,1).data]')
    passed=pixel==[0,255,0,255]
    rows.append({'engine':engine,'landscapePopupUnclipped':passed,'rightSidePixel':pixel})
    stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
    page.screenshot(path=str(OUT/(stamp+'-'+engine+('-baseline' if args.expect_stale else '-candidate')+'-popup.png')))
    if args.expect_stale:assert not passed,'Baseline unexpectedly passed; regression is not demonstrated'
    else:
      assert passed,(engine,'landscape popup clipped to stale622px surface',pixel)
      # A second rotation must retain the classification of the same handle.
      page.evaluate("""()=>{TEST.resize(536,1080);TEST.resize(1704,786);TEST.emit(TEST.gfx(31));
        TEST.emit(TEST.gfx(38,771));TEST.emit(TEST.gfx(18,0,0,1704,786,0));
        TEST.emit(TEST.gfx(17,1100,180,100,40,0xff00ff00,0xff00ff00,0xff00ff00,0xff00ff00));
        TEST.emit(TEST.gfx(38,0));TEST.emit(TEST.gfx(24,446,130,850,480,771,446,130,850,480,0xffffffff));
        let e=TEST.gfx(37,20,20);e.assignedHandle=772;TEST.emit(e);TEST.emit(TEST.gfx(38,772));
        TEST.emit(TEST.gfx(17,0,0,20,20,0xffff0000,0xffff0000,0xffff0000,0xffff0000));
        TEST.emit(TEST.gfx(38,0));TEST.emit(TEST.gfx(24,0,0,20,20,772,0,0,20,20,0xffffffff));TEST.emit(TEST.gfx(30));}""")
      page.wait_for_timeout(350)
      assert page.locator('#gfxCanvas').evaluate('c=>[...c.getContext("2d").getImageData(1140,200,1,1).data]')==[0,255,0,255]
      assert page.locator('#gfxCanvas').evaluate('c=>[...c.getContext("2d").getImageData(10,10,1,1).data]')==[255,0,0,255]
    assert not errors,errors
    print(('REPRODUCED old failure' if args.expect_stale else 'PASS')+' '+engine+' delayed landscape popup / retained handle / small surface',flush=True)
    context.close();browser.close()
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
(OUT/(stamp+('-baseline' if args.expect_stale else '-candidate')+'-surface-result.json')).write_text(json.dumps(rows,indent=2)+'\n')
