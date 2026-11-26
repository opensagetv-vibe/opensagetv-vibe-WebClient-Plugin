"""Actual browser DOM/settings with synthetic provider; no GPU/phone claim."""
import importlib.util,json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('fixture',ROOT/'tests/browser-vibe-display-smoke.py')
F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
with sync_playwright() as pw:
 for engine in ('chromium','webkit'):
  browser=getattr(pw,engine).launch(headless=True,**({'executable_path':'/usr/local/bin/vibe-chromium','args':['--no-sandbox']} if engine=='chromium' else {}))
  for size in ((393,852),(852,393)):
   context,page,errors=F.load(browser,ROOT/'src/main/webapp',size=size)
   page.evaluate("""()=>{const before=window.fetch;TEST.rateCalls=[];TEST.rateRefuse=false;
    window.fetch=async(url,options={})=>{const u=new URL(url,'https://fixture.test/'),q=new URLSearchParams(options.body||u.search);
     if((q.get('action')||u.searchParams.get('action'))==='runtimeRateTest'){
      TEST.rateCalls.push({method:options.method,operation:q.get('operation')});
      return new Response(JSON.stringify(TEST.rateRefuse?{error:'busy_or_unavailable'}:{state:q.get('operation')==='start'?'running':'PASS',synthetic:true}),{status:TEST.rateRefuse?409:200,headers:{'Content-Type':'application/json'}});
     }return before(url,options);
    };}""")
   page.locator('#settingsToggle').click()
   page.locator('#settings-tab-transcoding').click()
   checkbox=page.locator('#stream_runtimeBitrateControl');assert not checkbox.is_checked()
   page.locator('#automaticBitrateAdjustment').select_option('inplace');page.locator('#saveStreaming').click()
   page.wait_for_function("JSON.parse(TEST.storage.getItem('sagetvWebStreaming.v1')||'{}').runtimeBitrateControl===true")
   page.locator('#settings-tab-diagnostics').click()
   page.locator('#runRuntimeRateTest').click();page.wait_for_function("document.querySelector('#runtimeRateTestResult').textContent.includes('running')")
   page.locator('#readRuntimeRateTest').click();page.wait_for_function("document.querySelector('#runtimeRateTestResult').textContent.includes('PASS')")
   assert page.evaluate('TEST.rateCalls')==[{'method':'POST','operation':'start'},{'method':'POST','operation':'status'}]
   page.evaluate('TEST.rateRefuse=true');page.locator('#runRuntimeRateTest').click()
   page.wait_for_function("document.querySelector('#runtimeRateTestResult').textContent.startsWith('Test unavailable/refused:')")
   assert not errors,errors
   print('PASS',engine,size,'default-off/persisted opt-in/start/status/refusal; synthetic provider',flush=True)
   context.close()
  browser.close()
