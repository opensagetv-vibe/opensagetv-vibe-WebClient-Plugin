#!/usr/bin/env python3
"""WEB-133 compact settings tabs, synthetic server, no physical phone claim."""
import importlib.util,json,os,time
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ.get('SAGETV_ARTIFACT_DIR',ROOT/'artifacts/active/WEB-133'));OUT.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
spec=importlib.util.spec_from_file_location('display',ROOT/'tests/browser-vibe-display-smoke.py')
F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
with sync_playwright() as pw:
 for engine in ('chromium','webkit'):
  browser=getattr(pw,engine).launch(headless=True,**({'executable_path':'/usr/local/bin/vibe-chromium','args':['--no-sandbox']} if engine=='chromium' else {}))
  for size in ((1440,1000),(852,393),(393,852),(375,812),(320,568)):
   context,page,errors=F.load(browser,ROOT/'src/main/webapp',settings={'showStats':True},size=size)
   page.locator('#settingsToggle').click()
   assert page.locator('#settingsCategories [role=tab]').all_text_contents()==['General','Playback','Transport','Input','Diagnostics','Recovery']
   assert page.locator('#settingsTree>[role=tabpanel]:visible').count()==1
   assert page.locator('.mc-setting-choice').count()==0
   tabs=page.locator('#settingsCategories [role=tab]').evaluate_all('(tabs)=>tabs.map(e=>({top:e.offsetTop,height:e.offsetHeight,scroll:e.scrollHeight}))')
   assert len({tab['top'] for tab in tabs})==1,tabs
   assert all(tab['height']>=44 and tab['scroll']<=tab['height'] for tab in tabs),tabs
   assert page.locator('#streamingPreferences').count()==1
   assert page.evaluate("document.activeElement.id")=='closeSettings'
   before=page.evaluate('JSON.stringify(TEST.saved)')
   page.locator('#settings-tab-transcoding').click()
   for field in ('stream_player','stream_encoder','maxBufferSeconds','automaticBitrateAdjustment','stream_audioCodec','stream_audioKbps','stream_audioChannels'):
    assert page.locator('#'+field).is_visible(),field
   assert not page.locator('#adaptiveQuality').is_visible()
   assert not page.locator('#stream_runtimeBitrateControl').is_visible()
   assert page.evaluate('JSON.stringify(TEST.saved)')==before,'Opening tabs rewrote preferences'
   assert page.locator('#automaticBitrateAdjustment').input_value()=='off'
   page.locator('#settings-tab-diagnostics').click()
   assert page.locator('#downloadReport').is_visible(), 'Diagnostics must not require another submenu'
   page.locator('#settings-tab-transcoding').click()
   page.locator('#automaticBitrateAdjustment').select_option('inplace')
   page.wait_for_function("JSON.parse(TEST.saved['sagetvWebMiniClientSettings.v1']).adaptiveQuality===true&&JSON.parse(TEST.saved['sagetvWebStreaming.v1']).runtimeBitrateControl===true")
   page.locator('#automaticBitrateAdjustment').select_option('switching')
   page.wait_for_function("JSON.parse(TEST.saved['sagetvWebStreaming.v1']).runtimeBitrateControl===false")
   page.locator('#automaticBitrateAdjustment').select_option('off')
   page.wait_for_function("JSON.parse(TEST.saved['sagetvWebMiniClientSettings.v1']).adaptiveQuality===false")
   assert page.evaluate('document.documentElement.scrollWidth')<=size[0]+1
   for field in ('stream_encoder','maxBufferSeconds','automaticBitrateAdjustment'):
    page.locator('#'+field).scroll_into_view_if_needed();r=page.locator('#'+field).bounding_box()
    assert r['x']>=-1 and r['x']+r['width']<=size[0]+1,(size,field,r)
   page.locator('#settings-tab-input').click();page.keyboard.press('ArrowRight')
   assert page.locator('#settings-tab-diagnostics').get_attribute('aria-selected')=='true'
   page.keyboard.press('End');assert page.locator('#settings-tab-recovery').get_attribute('aria-selected')=='true'
   page.keyboard.press('Home');assert page.locator('#settings-tab-app').get_attribute('aria-selected')=='true'
   for tab in page.locator('#settingsCategories [role=tab]').all():
    tab.click();assert page.locator('#settingsTree>[role=tabpanel]:visible').count()==1
    assert page.locator('#'+tab.get_attribute('aria-controls')).is_visible()
    assert page.locator('#settingsTree>[role=tabpanel]:visible p.mc-note:not([id]):not([role])').count()<=1
   page.locator('#settings-tab-transcoding').click()
   page.locator('#stream_encoder').scroll_into_view_if_needed()
   if size[0]<521:
    assert page.locator('#stream_encoder').evaluate('e=>e.labels[0].getBoundingClientRect().height')<=46
   page.locator('#settings-tab-transcoding').click()
   page.screenshot(path=str(OUT/(stamp+'-'+engine+'-'+str(size[0])+'-tabs.png')))
   page.locator('#closeSettings').click()
   # Upgrade preserves full old statistics; the two controls are independent.
   assert page.locator('#statsPanel').is_visible() and page.locator('#stats').is_visible() and page.locator('#statsGauges').is_visible()
   page.locator('#remoteToggle').click()
   if size[0]<=900:page.locator('#phoneToolsToggle').click()
   graph=page.locator('#remoteStats');info=page.locator('#remoteStatsInfo')
   graph.scroll_into_view_if_needed();g=graph.bounding_box();i=info.bounding_box()
   assert abs(g['y']-i['y'])<1 and abs(g['x']+g['width']-i['x'])<2,(size,g,i)
   info.click();assert page.locator('#remotePanel').is_visible()
   assert page.locator('#statsGauges').is_visible() and not page.locator('#stats').is_visible()
   graph.click();assert not page.locator('#statsPanel').is_visible()
   info.click();assert page.locator('#stats').is_visible() and not page.locator('#statsGauges').is_visible()
   graph.click();assert page.locator('#stats').is_visible() and page.locator('#statsGauges').is_visible()
   assert page.locator('#remotePanel').is_visible()
   assert not errors,errors
   context.close()
   print('PASS',engine,size,'single-row-tabs/compact-fields/preservation/keyboard/adjustment/statistics',flush=True)
  browser.close()
