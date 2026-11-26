#!/usr/bin/env python3
"""Model a withheld idle Fetch chunk. Synthetic transport, NOT Safari evidence.

The model retains bytes arriving without a pending read until another write,
matching the failure mechanism described in WebKit bug322545. Native frame
pacing then cannot produce that next write before its timeout. A pending read
must be armed before synchronous parsing/scheduling of the preceding chunk.
"""
import argparse, importlib.util, json, os, time
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ['SAGETV_ARTIFACT_DIR']);OUT.mkdir(parents=True,exist_ok=True)
parser=argparse.ArgumentParser();parser.add_argument('--expect-stall',action='store_true');args=parser.parse_args()
spec=importlib.util.spec_from_file_location('display',ROOT/'tests/browser-vibe-display-smoke.py')
F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
MODEL=r"""
(()=>{
 const fetch0=window.fetch,read0=ReadableStreamDefaultReader.prototype.read,parse0=JSON.parse;
 TEST.waiting=false;TEST.outstanding=0;TEST.maxOutstanding=0;TEST.injected=false;
 ReadableStreamDefaultReader.prototype.read=function(...a){
   if(this!==TEST.reader)return read0.apply(this,a);
   TEST.waiting=true;TEST.maxOutstanding=Math.max(TEST.maxOutstanding,++TEST.outstanding);
   return read0.apply(this,a).finally(()=>{TEST.waiting=false;TEST.outstanding--;});
 };
 window.fetch=async(...a)=>{
   const r=await fetch0(...a),u=new URL(a[0],location.href);
   if(u.pathname==='/api/miniclient'&&u.searchParams.get('action')==='stream'){
     const get=r.body.getReader.bind(r.body);r.body.getReader=(...a)=>(TEST.reader=get(...a));
   }
   return r;
 };
 JSON.parse=function(text,...a){
   const value=parse0.call(this,text,...a);
   if(value?.web037Trigger&&!TEST.injected){
     TEST.injected=true;
     const events=[TEST.gfx(31),TEST.gfx(17,0,0,40,40,0xff00ff00,0xff00ff00,0xff00ff00,0xff00ff00),{...TEST.gfx(30),seq:703,ackRequired:true}];
     const bytes=new TextEncoder().encode(events.map(e=>JSON.stringify(e)+'\n').join(''));
     if(TEST.waiting)TEST.stream.enqueue(bytes);else TEST.strandedBytes=bytes.length;
   }
   return value;
 };
})();
"""
rows=[]
with sync_playwright() as pw:
  for engine in ('chromium','webkit'):
    options={'headless':True}
    if engine=='chromium':options.update(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
    browser=getattr(pw,engine).launch(**options)
    context,page,errors=F.load(browser,ROOT/'src/main/webapp',size=(852,393),main_transform=lambda main:MODEL+main)
    page.wait_for_timeout(500)
    page.evaluate("TEST.emit({type:'keepalive',web037Trigger:true})")
    page.wait_for_timeout(700)
    result=page.evaluate("()=>({injected:TEST.injected,strandedBytes:TEST.strandedBytes||0,maxOutstanding:TEST.maxOutstanding,ack:TEST.requests.some(r=>r[0]==='frameAck'&&r[1].sequence==='703'),pixel:[...gfxCanvas.getContext('2d').getImageData(10,10,1,1).data]})")
    result['engine']=engine;rows.append(result)
    assert result['injected'] and result['maxOutstanding']==1,result
    if args.expect_stall:assert not result['ack'] and result['strandedBytes']>0,result
    else:assert result['ack'] and result['strandedBytes']==0 and result['pixel']==[0,255,0,255],result
    assert not errors,errors
    print(('REPRODUCED' if args.expect_stall else 'PASS')+' '+engine+' withheld final chunk / one pending read / native frame ACK',flush=True)
    context.close();browser.close()
(OUT/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+('-baseline' if args.expect_stall else '-candidate')+'-stream-read-ahead.json')).write_text(json.dumps({'modeledTransport':True,'physicalIPhone':False,'rows':rows},indent=2)+'\n')
