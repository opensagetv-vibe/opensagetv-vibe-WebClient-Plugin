#!/usr/bin/env python3
"""Production DOM/controller with synthetic transport; NOT physical Safari."""
import importlib.util
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('fixture',ROOT/'tests/browser-vibe-display-smoke.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
HOOK=r"""const fallbackFetch=window.fetch;
TEST.sourceRequests=[];
window.fetch=async (url,options={})=>{
 const u=new URL(url,location.href),q=new URLSearchParams(u.search);
 if(options.body)new URLSearchParams(options.body).forEach((v,k)=>q.set(k,v));
 if(u.pathname.endsWith('/api/commercials')){TEST.markerQuery=Object.fromEntries(q);return new Response(JSON.stringify({available:true,markers:[{start:10,end:20,type:0},{start:-1,end:100,type:0},{start:30,end:40,type:3}]}));}
 if(q.get('action')==='sourcePreview'){
  TEST.sourceRequests.push(Object.fromEntries(q));
  const canvas=document.createElement('canvas');canvas.width=192;canvas.height=108;const ctx=canvas.getContext('2d');
  ctx.fillStyle='green';ctx.fillRect(0,0,192,108);ctx.fillStyle='white';ctx.fillText('Synthetic source30s',5,50);
  const jpeg=await new Promise(resolve=>canvas.toBlob(resolve,'image/jpeg',.6));
  return new Response(jpeg,{headers:{'Content-Type':'image/jpeg','X-Vibe-Preview-Position-Ms':'30000'}});
 }
 if(q.get('action')!=='timelineSeek')return fallbackFetch(url,options);
 const data=Object.fromEntries(q);TEST.requests.push(['timelineSeek',data]);
 TEST.timelineRequest=data;
 return new Promise(resolve=>TEST.finishSeek=()=>resolve(new Response(JSON.stringify({ok:true,state:Object.assign({},TEST.playbackState,
  {requestId:data.requestId,pending:true,acceptedPositionMs:Number(data.timeMs),requestedPositionMs:Number(data.timeMs),source:{sessionId:'owner',sourceGeneration:1,seekGeneration:1}})}))));
};
"""
with sync_playwright() as pw:
 for engine in ('chromium','webkit'):
  opts={'headless':True}
  if engine=='chromium':opts.update(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
  browser=getattr(pw,engine).launch(**opts)
  for size in ((393,852),(852,393)):
   context,page,errors=fixture.load(browser,ROOT/'src/main/webapp',settings={'scrubPreviews':True},size=size,main_transform=lambda main:HOOK+main)
   try:
    fixture.video_start(page)
    page.evaluate("""()=>{TEST.playbackState={schemaVersion:1,mediaId:314,source:{sessionId:'owner',sourceGeneration:1,seekGeneration:0},
     seekable:true,seekStartMs:0,seekEndMs:90000,producer:'video-fixture',requestId:'',pending:false,producerReady:true,reportedPositionMs:1000,displayedPositionMs:null};
     TEST.emit({type:'playbackState',value:TEST.playbackState});}""")
    page.wait_for_function("!document.querySelector('#seekRange').disabled")
    page.wait_for_function("document.querySelectorAll('#timelineMarkers span').length===2")
    assert page.evaluate('TEST.markerQuery.id')=='314'
    fixture.open_remote(page);page.locator('#remoteHelp').click()
    saved=page.evaluate("TEST.storage.getItem('sagetvWebStreaming.v1')")
    page.locator('#seekRange').evaluate("el=>{el.value='30';el.dispatchEvent(new Event('input',{bubbles:true}));}")
    assert 'preview' in page.locator('#timelinePhase').text_content()
    assert page.evaluate("TEST.requests.filter(r=>r[0]==='timelineSeek').length")==0
    page.wait_for_function("!document.querySelector('#timelinePreview').hidden && document.querySelector('#timelinePreviewImage').naturalWidth===192")
    assert page.evaluate('TEST.sourceRequests.length')==1
    assert page.evaluate('TEST.sourceRequests[0].sourceGeneration')=='1'
    assert 'Source preview at' in page.locator('#timelinePreviewLabel').text_content()
    page.locator('#timelineCancel').click()
    assert 'Requested not yet observed' in page.locator('#timelinePhase').text_content()
    page.locator('#seekRange').evaluate("el=>{el.value='45';el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));}")
    page.wait_for_function('!!TEST.finishSeek')
    assert 'sending' in page.locator('#timelinePhase').text_content()
    assert 'Displayed not yet observed' in page.locator('#timelinePhase').text_content()
    page.evaluate('TEST.finishSeek()')
    page.wait_for_function("document.querySelector('#timelinePhase').textContent.startsWith('preparing')")
    assert page.evaluate('TEST.timelineRequest.timeMs')=='45000'
    assert page.evaluate("TEST.storage.getItem('sagetvWebStreaming.v1')")==saved
    assert not page.locator('#adaptiveQuality').is_checked()
    # A stock/old provider with no local-seek contract leaves native controls.
    page.evaluate("TEST.emit({type:'playbackState',value:{schemaVersion:1,source:{sessionId:'owner',sourceGeneration:2,seekGeneration:0},seekable:false,dvd:true}})")
    page.wait_for_function("document.querySelector('#seekRange').disabled")
    assert page.locator('#nav_left').count()==1
    assert not errors,errors
    print('PASS',engine,size,'bounded synthetic source image/no preview seek, cancel, immediate pending, exact request, honest display, default-off quality, native DVD fallback',flush=True)
   finally:context.close()
  browser.close()
