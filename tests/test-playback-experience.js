'use strict';
const assert=require('node:assert/strict'),{Timeline,QualityAdvisor,FramePreviews,SourcePreviews}=require('../src/main/webapp/js/miniclient-experience.js');
const state=(seek=0,extra={})=>Object.assign({schemaVersion:1,source:{sessionId:'owner',sourceGeneration:1,seekGeneration:seek},seekable:true,seekStartMs:0,seekEndMs:90000,producer:'first',requestId:'',pending:false,producerReady:true,reportedPositionMs:1000,displayedPositionMs:null},extra);
let n=0;function test(name,fn){return Promise.resolve().then(fn).then(()=>{n++;console.log('PASS '+name);});}
(async()=>{
await test('optional DVD reports uncertain actions honestly without suggesting blind replay',()=>{
 const {dvdActionMessage:message}=require('../src/main/webapp/js/miniclient-experience.js');
 assert.match(message(true,'accepted'),/accepted/);
 for(const outcome of ['unknown','pending']){assert.match(message(false,outcome),/may have taken effect/);assert.match(message(false,outcome),/check playback/);assert.doesNotMatch(message(false,outcome),/action unavailable/);}
 for(const outcome of ['rejected','none',undefined])assert.match(message(false,outcome),/unavailable or load changed/);
});
await test('preview is local, clamped and cancellable; no confirmed position is invented',()=>{
 let calls=0;const t=new Timeline({seek:()=>{calls++;}});t.receive(state());t.preview(999999);assert.equal(t.model().requested,90000);assert.equal(t.model().displayed,null);assert.equal(calls,0);t.cancelPreview();assert.equal(t.model().requested,null);
});
await test('requested, accepted and genuinely presented stages remain distinct',async()=>{
 const t=new Timeline({seek:async p=>({ok:true,state:state(1,{requestId:p.requestId,pending:true,acceptedPositionMs:p.timeMs})})});t.receive(state());
 const pending=t.request(30000);assert.equal(t.model().phase,'sending');assert.equal(t.model().value,30000);await pending;
 assert.equal(t.model().phase,'preparing');assert.equal(t.model().displayed,null);
 assert.equal(typeof t.model().timing.requestToAckMs,'number');assert.equal(t.model().timing.requestToPresentedMs,null);assert.equal(t.model().timing.stockUiProcessedAtMs,null);
 t.receive(state(1,{requestId:'web_1',producer:'new',acceptedPositionMs:30000}));t.presented('first',31000);assert.equal(t.model().displayed,null);
 t.presented('new',30300);assert.equal(t.model().phase,'presented');t.receive(state(1,{requestId:'web_1',producer:'new',acceptedPositionMs:30000}));assert.equal(t.model().phase,'presented');
});
await test('latest request wins over reordered HTTP responses',async()=>{
 const pending=[];const t=new Timeline({seek:p=>new Promise(resolve=>pending.push({p,resolve}))});t.receive(state());const a=t.request(40000),b=t.request(10000);
 pending[1].resolve({ok:true,state:state(2,{requestId:'web_2',acceptedPositionMs:10000,pending:true})});await b;
 pending[0].resolve({ok:true,state:state(1,{requestId:'web_1',acceptedPositionMs:40000,pending:true})});await a;assert.equal(t.model().requested,10000);assert.equal(t.state.source.seekGeneration,2);
});
await test('native seek supersedes local intent and source changes retire callbacks',async()=>{
 let resolve;const t=new Timeline({seek:()=>new Promise(r=>resolve=r)});t.receive(state());const p=t.request(50000);
 t.receive(state(2));assert.equal(t.intent,null);t.receive(state(0,{source:{sessionId:'owner',sourceGeneration:2,seekGeneration:0}}));resolve({ok:true,state:state(1)});await p;assert.equal(t.state.source.sourceGeneration,2);
 assert.equal(t.receive(state(10)),false);assert.equal(t.state.source.sourceGeneration,2);
});
await test('native STV seek exposes accepted target without carrying the old displayed clock',()=>{
 const t=new Timeline({seek:()=>{throw Error('No extra seek');}});t.receive(state());t.presented('first',70000);
 t.receive(state(1,{pending:true,phase:'preparing',requestedPositionMs:30000,acceptedPositionMs:30000}));
 assert.equal(t.model().pending,true);assert.equal(t.model().requested,30000);assert.equal(t.model().accepted,30000);
 assert.equal(t.model().value,30000);assert.equal(t.model().displayed,null);
 t.presented('first',71000);assert.equal(t.model().displayed,null,'Old producer cannot present the accepted seek');
 t.receive(state(1,{producer:'second',phase:'waiting-for-browser',requestedPositionMs:30000,acceptedPositionMs:30000}));
 assert.equal(t.model().pending,true);t.presented('first',72000);assert.equal(t.model().displayed,null);
 t.presented('second',30300);assert.equal(t.model().pending,false);assert.equal(t.model().displayed,30300);assert.equal(t.model().phase,'playing');
});
await test('native paused, failed and superseded seeks never invent a displayed frame',()=>{
 const t=new Timeline({seek:()=>{throw Error('No extra seek');}});t.receive(state());t.presented('first',70000);
 t.receive(state(1,{pending:true,phase:'preparing',requestedPositionMs:30000,acceptedPositionMs:30000}));
 t.receive(state(2,{pending:true,phase:'preparing',requestedPositionMs:10000,acceptedPositionMs:10000}));
 assert.equal(t.model().value,10000);assert.equal(t.receive(state(1)),false);
 t.receive(state(2,{producer:'second',paused:true,phase:'waiting-for-browser',requestedPositionMs:10000,acceptedPositionMs:10000}));
 t.presented('second',10000);assert.equal(t.model().phase,'paused');assert.equal(t.model().pending,false);
 t.receive(state(3,{producer:'second',pending:true,phase:'preparing',requestedPositionMs:45000,acceptedPositionMs:45000}));
 t.receive(state(3,{producer:'',phase:'failed',error:'Preparation failed',requestedPositionMs:45000,acceptedPositionMs:null}));
 assert.equal(t.model().pending,false);assert.equal(t.model().displayed,null);assert.equal(t.model().accepted,null);assert.equal(t.model().phase,'failed');
});
await test('failed or stale request is visible and never claims confirmed success',async()=>{
 const t=new Timeline({seek:async()=>({ok:false,stale:true})});t.receive(state());assert.equal(await t.request(10000),false);assert.equal(t.model().phase,'failed');assert.match(t.model().error,/Recording changed/);assert.equal(t.model().displayed,null);
});
await test('missing, unsupported and DVD state keep native controls and reject local seek',async()=>{
 const t=new Timeline({seek:()=>{throw Error('must not call');}});assert.equal(t.receive({schemaVersion:2}),false);assert.equal(await t.request(10),false);t.receive(state(0,{dvd:true,seekable:false}));assert.equal(await t.request(10),false);
});
await test('diagnostic history is bounded and reports unavailable frames honestly',()=>{
 const t=new Timeline({seek:async()=>({ok:false})});t.receive(state());for(let i=0;i<100;i++)t.note('phase'+i);assert.equal(t.history.length,48);assert.equal(t.model().displayed,null);
});
await test('quality requires sustained measured limitation, not CPU starvation or one stall',()=>{
 const q=new QualityAdvisor(),s={source:'a',active:true,videoKbps:4000,throughputKbps:1200,ahead:1};assert.equal(q.observe({...s,now:3000}),null);assert.equal(q.observe({...s,now:6000}),null);assert(q.observe({...s,now:9000}).videoKbps<1000);
 q.reset();for(let i=1;i<8;i++)assert.equal(q.observe({...s,now:i*3000,throughputKbps:10000}),null);
});
await test('measured starvation can downshift while internal buffer Pause never impersonates user Pause',()=>{
 const sample={source:'starved',active:true,videoKbps:4000,throughputKbps:1000,ahead:0,paused:false,elementPaused:true,rebuffering:true};
 const q=new QualityAdvisor();q.observe({...sample,now:3000});q.observe({...sample,now:6000});assert(q.observe({...sample,now:9000}).videoKbps<1000);
 for(const extra of [{paused:true},{rebuffering:false},{throughputKbps:null}]){const guard=new QualityAdvisor();for(let i=1;i<10;i++)assert.equal(guard.observe({...sample,...extra,now:i*3000}),null);}
 const recovery=new QualityAdvisor();for(let i=1;i<20;i++)assert.equal(recovery.observe({...sample,videoKbps:700,ceilingKbps:4000,throughputKbps:10000,ahead:20,now:i*3000}),null,'Buffering never qualifies for automatic upshift');
});
await test('quality respects DVD, Copy, pause, startup, seek and unknown-throughput boundaries',()=>{
 for(const field of ['dvd','copy','paused','starting','seeking']){const q=new QualityAdvisor();for(let i=1;i<8;i++)assert.equal(q.observe({source:'a',active:true,videoKbps:4000,throughputKbps:1000,ahead:1,now:i*3000,[field]:true}),null);}
 const q=new QualityAdvisor();for(let i=1;i<8;i++)assert.equal(q.observe({source:'a',active:true,videoKbps:4000,ahead:1,now:i*3000}),null);
});
await test('quality cooldown, per-source attempt budget and source reset prevent restart loops',()=>{
 const q=new QualityAdvisor(),s={source:'a',active:true,videoKbps:4000,throughputKbps:1000,ahead:1};for(let i=1;i<=3;i++)q.observe({...s,now:i*3000});q.appliedAt(9000);assert.equal(q.observe({...s,now:12000}),null);
 q.applied=2;assert.equal(q.observe({...s,now:90000}),null);q.observe({...s,source:'b',now:93000});assert.equal(q.applied,0);
});
await test('quality recovery requires ten measured stable samples and never exceeds the saved ceiling',()=>{
 const q=new QualityAdvisor(),s={source:'a',active:true,videoKbps:700,ceilingKbps:800,ceilingHeight:480,throughputKbps:5000,ahead:20};
 for(let i=1;i<10;i++)assert.equal(q.observe({...s,now:i*3000}),null);
 assert.deepEqual(Object.assign({},q.observe({...s,now:30000}),{reason:''}),{videoKbps:800,resolution:'480',direction:'up',reason:''});
 q.appliedAt(30000);for(let i=11;i<29;i++)assert.equal(q.observe({...s,now:i*3000}),null);
 assert(q.observe({...s,now:90000}));q.appliedAt(90000);
 for(let i=31;i<70;i++)assert.equal(q.observe({...s,now:i*3000}),null);
});
await test('unknown headroom, low reserve and already-at-ceiling cannot trigger recovery',()=>{
 for(const extra of [{throughputKbps:null},{ahead:5},{ceilingKbps:700},{ceilingKbps:null},{paused:true},{copy:true},{dvd:true}]){
  const q=new QualityAdvisor();for(let i=1;i<20;i++)assert.equal(q.observe({source:'a',active:true,videoKbps:700,ceilingKbps:1000,throughputKbps:5000,ahead:20,now:i*3000,...extra}),null);
 }
 const q=new QualityAdvisor(),s={source:'a',active:true,videoKbps:700,ceilingKbps:1000,throughputKbps:5000,ahead:20};
 for(let i=1;i<10;i++)q.observe({...s,now:i*3000});q.observe({...s,ahead:1,now:30000});
 assert.equal(q.observe({...s,now:33000}),null,'reserve interruption resets recovery stability');
});
await test('viewed-frame previews bound memory, preserve epochs and never invent unviewed frames',()=>{
 const revoked=[],cache=new FramePreviews(url=>revoked.push(url));cache.begin('a');
 for(let i=0;i<30;i++)assert(cache.offer('a',i*10000,'blob:'+i,20000));
 assert.equal(cache.snapshot().count,16);assert(cache.snapshot().bytes<=524288);assert.equal(revoked.length,14);
 assert.equal(cache.nearest('a',1000),null);assert.equal(cache.nearest('b',290000),null);
 assert.equal(cache.nearest('a',293000).timeMs,290000);assert.equal(cache.nearest('a',299999),null);
 assert.equal(cache.offer('a',290100,'blob:duplicate',20000),false);
 assert.equal(cache.offer('a',300000,'https://foreign/frame.jpg',20000),false);
 assert.equal(cache.offer('a',300000,'blob:oversized',40000),false);
 cache.begin('b');assert.equal(cache.snapshot().count,0);assert.equal(cache.offer('a',300000,'blob:late',20000),false);
});
await test('explicit source previews reuse the same bounded frame cache and never seek',async()=>{
 let now=0,calls=0;const revoked=[],cache=new FramePreviews(url=>revoked.push(url));cache.begin('a');
 const previews=new SourcePreviews({clock:()=>now,fetch:async(key,ms)=>{calls++;return{timeMs:40000,bytes:5000,url:'blob:source'};},
  offer:(...args)=>cache.offer(...args),revoke:url=>revoked.push(url)});
 previews.begin('a');assert(await previews.request('a',42000));assert.equal(cache.nearest('a',42000).kind,'source');assert.equal(cache.snapshot().sourceImages,1);
 assert.equal(await previews.request('a',42000),false);assert.equal(await previews.request('b',30000),false);assert.equal(calls,1);
 now=2100;assert.equal(await previews.request('a',-1),false);assert.equal(previews.snapshot().queued,0);
});
await test('source preview admission has one in-flight job, no queue/retry and source-cancelled blobs',async()=>{
 let resolve,calls=0;const revoked=[],offers=[];
 const p=new SourcePreviews({fetch:(key,ms,signal)=>{calls++;return new Promise(r=>resolve=r);},offer:(...args)=>offers.push(args),revoke:url=>revoked.push(url)});
 p.begin('a');const request=p.request('a',40000);assert.equal(await p.request('a',50000),false);p.begin('b');
 resolve({timeMs:40000,bytes:5000,url:'blob:stale'});assert.equal(await request,false);assert.deepEqual(revoked,['blob:stale']);assert.equal(offers.length,0);assert.equal(calls,1);
});
await test('missing or invalid preview providers preserve normal controls without autonomous retry',async()=>{
 let now=0,calls=0;const revoked=[];
 const p=new SourcePreviews({clock:()=>now,fetch:async()=>{calls++;throw Error('missing');},offer:()=>{throw Error('must not offer');},revoke:url=>revoked.push(url)});
 p.begin('a');assert.equal(await p.request('a',40000),false);now=3000;assert.equal(await p.request('a',40000),false);assert.equal(calls,1);
 assert.equal(p.snapshot().state,'unavailable');
 const bad=new SourcePreviews({fetch:async()=>({timeMs:0,bytes:32769,url:'blob:oversized'}),offer:()=>{throw Error('must not offer');},revoke:url=>revoked.push(url)});
 bad.begin('a');assert.equal(await bad.request('a',0),false);assert.deepEqual(revoked,['blob:oversized']);
});
console.log(n+' playback experience groups PASS');
})().catch(error=>{console.error(error);process.exitCode=1;});
