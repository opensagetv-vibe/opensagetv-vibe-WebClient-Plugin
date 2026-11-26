#!/usr/bin/env python3
"""Real Chromium/WebKit UI and central-report integration, synthetic server.
No physical phone, real encoder or measured WAN claim."""
import importlib.util
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('fixture',ROOT/'tests/browser-vibe-display-smoke.py')
F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
with sync_playwright() as pw:
 for engine in ('chromium','webkit'):
  browser=getattr(pw,engine).launch(headless=True,**({'executable_path':'/usr/local/bin/vibe-chromium','args':['--no-sandbox']} if engine=='chromium' else {}))
  for size in ((1440,900),(852,393),(393,852)):
   seam="""window.BUFFER_UI_TEST={
     configure:()=>{timeline.receive({schemaVersion:1,source:{sessionId:'synthetic',sourceGeneration:1,seekGeneration:0},producer:'owned-test',pending:false,qualityHandoffRevision:1,qualityRecoveryRevision:1,bufferAdaptationRevision:1});playback.id='owned-test';},
     bars:s=>updateDiagnosticGauges(s),report:s=>{bufferReportAt=-Infinity;updateQualityRecommendation(s);},
     missing:()=>{timeline.state.bufferAdaptationRevision=0;},state:()=>({reason:qualityAdvisor.reason})};\n"""
   def expose(main):
    before,after=main.rsplit('})();',1);return before+seam+'})();'+after
   context,page,errors=F.load(browser,ROOT/'src/main/webapp',settings={'showStats':True,'adaptiveMinimumKbps':1000,'adaptiveQuality':True},size=size,main_transform=expose)
   page.wait_for_timeout(900)
   assert page.locator('#diagnosticGauges .mc-gauge').count()==3
   assert page.locator('#statsGauges meter').count()==0 # idle is unavailable, not zero
   assert 'Unavailable' in page.locator('#statsGauges').inner_text()
   assert page.locator('#adaptiveMinimumKbps').input_value()=='1000'
   startup=page.evaluate("TEST.requests.find(r=>r[0]==='start')[1]")
   assert startup['stream_adaptiveMinimumKbps']=='1000' and startup['stream_videoKbps']=='8000'
   assert startup['stream_adaptiveQuality']=='true' and startup['stream_player']=='hls'
   # Exercise the production gauge renderer through its existing updateStats
   # callback, with explicitly synthetic browser/provider observations.
   page.evaluate("""()=>{TEST.startVideo();}""")
   page.wait_for_timeout(900)
   assert page.locator('#statsPanel').is_visible()
   page.evaluate('BUFFER_UI_TEST.configure()')
   sample={'id':'owned-test','status':{'hlsSeconds':30,'running':True,'streamSettings':{'effective':{'videoTargetKbps':4000}}},
           'statusAgeMs':0,'localTimeSeconds':10,'firstFrameMs':1,'ahead':2,'rebuffering':True,'bufferTargetSeconds':12,'configuredBufferSeconds':180}
   # Snapshot synchronously: the real periodic stats callback may legitimately
   # replace our synthetic bars with its own unavailable fixture observations.
   gauges=page.evaluate('''(s)=>{BUFFER_UI_TEST.bars(s);BUFFER_UI_TEST.report(s);
     const bars=[...document.querySelectorAll('#statsGauges meter')];
     return{count:bars.length,target:bars[2]&&bars[2].getAttribute('aria-valuetext'),
       geometry:bars.map(b=>({width:b.getBoundingClientRect().width,height:b.getBoundingClientRect().height}))}}''',sample)
   page.wait_for_function("TEST.requests.some(r=>r[0]==='bufferReport')")
   report=page.evaluate("TEST.requests.filter(r=>r[0]==='bufferReport').at(-1)[1]")
   assert report['bufferMs']=='2000' and report['positionMs']=='10000' and report['eligible']=='true'
   assert 'minimumKbps' not in report and 'throughputKbps' not in report # configured at start, buffer-only reports
   assert gauges['count']==3 and gauges['target'].startswith('4000 kbps')
   assert all(0 < b['width'] <= 112.1 and 0 < b['height'] <= 6.5 for b in gauges['geometry']),gauges
   page.wait_for_timeout(40)
   page.evaluate('(s)=>BUFFER_UI_TEST.report({...s,paused:true})',sample)
   page.wait_for_timeout(40)
   assert page.evaluate("TEST.requests.filter(r=>r[0]==='bufferReport').at(-1)[1].eligible")=='false'
   before=page.evaluate("TEST.requests.filter(r=>r[0]==='bufferReport').length")
   page.evaluate('(s)=>{BUFFER_UI_TEST.missing();BUFFER_UI_TEST.report(s)}',sample)
   page.wait_for_timeout(40)
   assert page.evaluate("TEST.requests.filter(r=>r[0]==='bufferReport').length")==before
   assert not errors,errors
   assert not page.locator('a[href="index.html"]').count()
   context.close()
  browser.close()
  print('PASS '+engine+' desktop/landscape/portrait limits, unavailable bars and STV-only navigation')
for entry in ('index.html','client.html'):
 text=(ROOT/'src/main/webapp'/entry).read_text()
 assert "location.replace('miniclient.html'+location.search+location.hash)" in text
 assert 'wasm' not in text.lower() and 'js/app.js' not in text
assert 'wasm-decoder-adapter' not in (ROOT/'src/main/webapp/sw.js').read_text()
print('PASS both legacy entry points and PWA cache use STV only')
