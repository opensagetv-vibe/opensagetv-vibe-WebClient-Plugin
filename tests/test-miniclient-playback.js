'use strict';
const assert=require('node:assert/strict');
const Clock=require('./test-miniclient-core.js');
const Playback=require('../src/main/webapp/js/miniclient-playback.js');
const flush=async()=>{for(let i=0;i<12;i++)await Promise.resolve();};
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};};
function fixture(settings={}){
 const clock=new Clock(),instances=[],errors=[],messages=[],recoveries=[],fallbacks=[];
 const v={currentTime:0,volume:1,muted:false,paused:true,ended:false,videoWidth:1280,videoHeight:720,playCount:0,ranges:[],
  get buffered(){const r=this.ranges;return {length:r.length,start:i=>r[i][0],end:i=>r[i][1]};},
  play(){this.playCount++;this.paused=false;return Promise.resolve();},pause(){this.paused=true;},removeAttribute(){},load(){this.currentTime=0;},canPlayType(){return '';}};
 class Hls{
  static version='fixture';static isSupported=()=>true;static Events={ERROR:'error',MANIFEST_PARSED:'manifest',FRAG_LOADING:'loading',FRAG_LOADED:'loaded',FRAG_BUFFERED:'buffered'};static ErrorTypes={NETWORK_ERROR:'network',MEDIA_ERROR:'media'};
  constructor(config){this.config=config;this.handlers={};this.loads=[];this.destroyed=false;instances.push(this);}
  on(e,f){this.handlers[e]=f;}loadSource(url){this.url=url;}attachMedia(media){this.video=media;this.handlers.manifest?.();}startLoad(p){this.loads.push(p);}destroy(){this.destroyed=true;}recoverMediaError(){this.fixed=true;}
 }
 const f={clock,v,instances,errors,messages,recoveries,fallbacks,Hls,cfg:settings,st:{playlistReady:true,segments:1,hlsSeconds:3,hlsFillRate:2,running:true,endList:false}};
 f.p=new Playback({video:v,clock,settings:()=>f.cfg,status:async id=>({...f.st,session:id}),loadHls:async()=>Hls,resolveUrl:u=>u,
   recover:async x=>{recoveries.push(x);return {ok:true};},fallback:async x=>{fallbacks.push(x);return {ok:true};},message:m=>messages.push(m),error:e=>errors.push(e)});
 f.start=(id='a',extra={})=>f.p.start({hlsSession:id,playlistUrl:'hls/'+id+'/stream.m3u8',durationMs:300000,...extra});return f;
}
(async()=>{
 let count=0;async function test(name,fn){await fn();console.log('PASS '+name);count++;}
 await test('completed HLS idle loader refills near target without changing ceiling or startup',async()=>{
  const f=fixture({maxBufferSeconds:30});await f.start();const h=f.instances[0];h.handlers.buffered();
  f.v.currentTime=10;f.v.ranges=[[0,33]];f.st.activeRecording=false;f.st.hlsSeconds=100;
  f.p.lastLoaderWake=-10000;f.clock.t+=2500;await f.p.hlsHealth();
  assert.equal(f.p.loaderWakeups,1);assert.equal(h.config.maxMaxBufferLength,30);assert.equal(f.p.startSeconds,0);assert.equal(f.recoveries.length,0);f.p.stop();
 });
 await test('early top-up preserves live unknown DVD active-fragment and no-published-reserve guards',async()=>{
  for(const kind of ['live','unknown','dvd','fragment','no-reserve']){
   const f=fixture({maxBufferSeconds:30});await f.start('guard',{dvd:kind==='dvd'});const h=f.instances[0];h.handlers.buffered();
   f.v.currentTime=10;f.v.ranges=[[0,15]];f.st.hlsSeconds=kind==='no-reserve'?15:100;
   if(kind!=='unknown')f.st.activeRecording=kind==='live';
   if(kind==='fragment')h.handlers.loading();
   f.p.lastLoaderWake=-10000;f.clock.t+=2500;await f.p.hlsHealth();assert.equal(f.p.loaderWakeups,0,kind);f.p.stop();
  }
 });
 await test('native Safari depleted loader recovers the same producer at the actual position, including stale HAVE_FUTURE_DATA',async()=>{
  for(const ready of [2,3,4]){
   const f=fixture();f.v.canPlayType=()=> 'probably';f.p.o.nativePreferred=true;
   await f.start('native',{startSeconds:20,streamSettings:{requested:{player:'native',allowFallback:true}}});await flush();
   Object.assign(f.v,{currentTime:30,readyState:ready,networkState:2,paused:false,ended:false});f.v.ranges=[];
   Object.assign(f.p,{firstFrameMs:100,lastTime:30,lastPlayProgress:1000,starvedAt:1000});
   f.st={...f.st,session:'native',dvd:false,playlistUrl:'hls/native/stream.m3u8',hlsSeconds:80};f.clock.t=15001;
   await f.p.hlsHealth();await flush();assert.equal(f.instances.length,1,'native loader must not wait forever with server reserve, ready '+ready);
   assert.equal(f.p.id,'native');assert.equal(f.p.startSeconds,20);assert.equal(f.instances[0].config.startPosition,30);
   assert.equal(f.recoveries.length,0,'healthy encoder not restarted');assert(f.p.absoluteTime()>=50000,'observed clock must not jump backwards');f.p.stop();
  }
 });
 await test('server health feedback reports actual element buffer independently of pause intent',async()=>{
  const f=fixture();f.p.id='owned';f.p.intentPaused=false;Object.assign(f.v,{currentTime:10,readyState:2,networkState:2,seeking:true,paused:true});f.v.ranges=[[0,12.5]];
  const s=f.p.state();assert.equal(s.bufferAheadMs,2500);assert.equal(s.elementPaused,true);assert.equal(s.paused,false);assert.equal(s.seeking,true);assert.equal(s.expectedHlsSession,'owned');assert.equal(s.readyState,2);assert.equal(s.networkState,2);
  assert.equal(s.playbackRevision,'web121.4');assert.equal(f.v.playCount,0);assert.equal(f.recoveries.length,0);
 });
 await test('accepted asynchronous recovery waits for replacement and preserves retry budget',async()=>{
  const f=fixture();await f.start();await flush();f.v.currentTime=23;
  f.p.o.recover=async x=>{f.recoveries.push(x);return {ok:true,pending:true};};
  const now=f.clock.now();await f.p.recover('delayed preparation');
  assert.equal(f.p.recoveryWaitUntil,now+30000);assert.equal(f.p.budget.count,1);
  f.clock.t+=11000;assert.equal(await f.p.recover('duplicate'),false);assert.equal(f.recoveries.length,1);
  f.p.intentPaused=true;f.v.pause(); // latest browser Pause intent, retained across replacement
  await f.start('replacement',{recovery:true,startSeconds:23,paused:true});await flush();
  assert.equal(f.p.budget.count,1);assert(f.p.intentPaused);assert.equal(f.p.id,'replacement');f.p.stop();
 });
 await test('live source gap waits without replacing its decoder, then automatically refills and resumes',async()=>{
  const f=fixture();await f.start();await flush();Object.assign(f.p,{starvedAt:1000,lastProduceProgress:1000,lastInputProgress:1000});f.clock.t=15001;f.v.ranges=[];
  f.st={...f.st,activeRecording:true,hlsSeconds:0,streamHealth:{inputStage:'waiting-source',processAlive:true}};
  await f.p.hlsHealth();assert.equal(f.recoveries.length,0,'no replacement can manufacture absent live bytes');assert(f.p.rebuffering);
  f.clock.t=18000;f.st.hlsSeconds=5;f.st.bytesInput=100000;f.v.ranges=[[0,5]];
  await f.p.hlsHealth();await flush();assert(!f.p.rebuffering);assert(!f.v.paused);assert.equal(f.recoveries.length,0);f.p.stop();
 });
 await test('intermediate hardware exit cannot race the same-owner startup fallback',async()=>{
  const f=fixture();await f.start();await flush();f.v.ranges=[];
  f.st={...f.st,running:false,endList:true,exitCode:69,producerPreparing:true,hlsSeconds:0};
  f.clock.t+=15000;await f.p.hlsHealth();assert.equal(f.recoveries.length,0,'fallback owns this retry, not another browser producer');
  f.st.producerPreparing=false;await f.p.hlsHealth();assert.equal(f.recoveries.length,1,'terminal failure retains bounded browser recovery');f.p.stop();
 });
 await test('native buffer repair refuses pause progress DVD stale ownership seek remote and no server reserve',async()=>{
  for(const why of ['pause','blocked','progress','dvd','stale','seeking','remote','buffered','reserve','startup','ended','error']){
   const f=fixture();f.v.canPlayType=()=> 'probably';f.p.o.nativePreferred=true;
   await f.start('native',{streamSettings:{requested:{player:'native'}}});await flush();
   Object.assign(f.v,{currentTime:30,readyState:2,paused:false});Object.assign(f.p,{firstFrameMs:100,lastTime:30,lastPlayProgress:1000});f.clock.t=15001;
   f.st={...f.st,session:'native',dvd:false,playlistUrl:'hls/native/stream.m3u8',hlsSeconds:80};
   if(why==='pause')f.p.intentPaused=true;if(why==='blocked')f.p.blocked=true;if(why==='progress')f.p.lastPlayProgress=14000;
   if(why==='dvd')f.p.dvd=true;if(why==='stale')f.st.session='other';if(why==='seeking')f.v.seeking=true;
   if(why==='remote')f.v.webkitCurrentPlaybackTargetIsWireless=true;if(why==='buffered')f.v.ranges=[[30,35]];
   if(why==='reserve')f.st.hlsSeconds=31;if(why==='startup')f.p.firstFrameMs=null;if(why==='ended')f.v.ended=true;if(why==='error')f.v.error={code:2};
   assert.equal(await f.p.tryNativeBufferRepair(f.p.generation,f.st),false,why);assert.equal(f.instances.length,0,why);assert.equal(f.recoveries.length,0,why);f.p.stop();
  }
 });
 await test('native buffer repair asynchronous load cannot outlive Stop source Pause or resumed playback',async()=>{
  for(const why of ['stop','source','pause','progress','buffered']){
   const f=fixture();f.v.canPlayType=()=> 'probably';f.p.o.nativePreferred=true;await f.start('native',{streamSettings:{requested:{player:'native'}}});
   Object.assign(f.v,{currentTime:30,readyState:2,paused:false});Object.assign(f.p,{firstFrameMs:100,lastTime:30,lastPlayProgress:1000});f.clock.t=15001;
   f.p.status={...f.st,session:'native',dvd:false,playlistUrl:'hls/native/stream.m3u8',hlsSeconds:80};
   const d=deferred();f.p.o.loadHls=()=>d.promise;const pending=f.p.tryNativeBufferRepair(f.p.generation,f.p.status);await flush();
   if(why==='stop')f.p.stop();if(why==='source')await f.start('new',{streamSettings:{requested:{player:'native'}}});if(why==='pause')f.p.intentPaused=true;
   if(why==='progress')f.p.lastPlayProgress=15000;if(why==='buffered')f.v.ranges=[[30,35]];
   d.resolve(f.Hls);assert.equal(await pending,false,why);assert.equal(f.instances.length,0,why);assert.equal(f.recoveries.length,0,why);f.p.stop();
  }
 });
 await test('passive video diagnostic distinguishes element state from intent without media URLs',async()=>{
  const f=fixture();Object.assign(f.v,{currentTime:.121333,duration:90,readyState:3,networkState:2,seeking:false,playbackRate:1,src:'https://user:secret@host/video?token=private',getVideoPlaybackQuality:()=>({totalVideoFrames:95,droppedVideoFrames:2})});
  f.v.ranges=[[.021333,14.035332]];f.p.intentPaused=false;
  const before={plays:f.v.playCount,paused:f.v.paused,time:f.v.currentTime};const s=f.p.snapshot();
  assert.equal(s.paused,false);assert.equal(s.element.paused,true);assert.equal(s.element.currentTime,.121333);assert.equal(s.element.readyState,3);assert.equal(s.element.networkState,2);
  assert.deepEqual(s.element.buffered.ranges,[[.021333,14.035332]]);assert.equal(s.element.seekable.available,false);assert.deepEqual(s.element.quality,{totalVideoFrames:95,droppedVideoFrames:2});
  assert.deepEqual({plays:f.v.playCount,paused:f.v.paused,time:f.v.currentTime},before);assert.doesNotMatch(JSON.stringify(s.element),/secret|token|https:/);
 });
 await test('video diagnostic caps range enumeration and normalizes unavailable numbers',async()=>{
  const f=fixture();let calls=0;Object.defineProperty(f.v,'seekable',{get:()=>({length:1000,start:i=>{calls++;return i;},end:i=>i+.5})});
  Object.assign(f.v,{duration:Infinity,readyState:NaN,getVideoPlaybackQuality:()=>({totalVideoFrames:-1,droppedVideoFrames:Infinity})});
  const s=f.p.elementSnapshot();assert.equal(s.seekable.ranges.length,16);assert.equal(calls,16);assert.equal(s.seekable.truncated,true);assert.equal(s.duration,null);assert.equal(s.readyState,null);assert.deepEqual(s.quality,{totalVideoFrames:null,droppedVideoFrames:null});
 });
 await test('transient TimeRanges and optional quality failures do not abort diagnostics',async()=>{
  const f=fixture();Object.defineProperty(f.v,'seekable',{get:()=>({length:2,start:()=>{throw Error('range changed');},end:()=>0})});f.v.getVideoPlaybackQuality=()=>{throw Error('unsupported');};
  const s=f.p.elementSnapshot();assert.equal(s.available,true);assert.deepEqual(s.seekable,{available:false,ranges:[]});assert.equal(s.quality,null);
  Object.defineProperty(f.v,'networkState',{get:()=>{throw Error('not available');}});assert.deepEqual(f.p.elementSnapshot(),{available:false});
 });
 await test('invalid video diagnostic ranges are omitted without guessing timestamps',async()=>{
  const f=fixture();f.v.ranges=[[NaN,1],[-1,2],[5,4],[.2,.8]];assert.deepEqual(f.p.elementSnapshot().buffered.ranges,[[.2,.8]]);
 });
 await test('actual confirmed recording EOF retires presentation once without stopping media or touching DVD',async()=>{
  const f=fixture();let retired=0;f.p.o.presentationEnded=()=>retired++;
  await f.start('finite-eof');await flush();
  f.p.firstFrameMs=12;f.v.currentTime=300;f.v.ended=true;f.v.ranges=[[0,300]];
  f.st={...f.st,running:false,endList:true,activeRecording:false,exitCode:0,hlsSeconds:300,durationMs:300000};
  await f.p.ended();await f.p.ended();
  assert.equal(retired,1);assert.equal(f.p.id,'finite-eof');assert.equal(f.recoveries.length,0);
  f.p.stop();
 });
 await test('presentation EOF clear rejects live unknown failed truncated paused and DVD ownership',async()=>{
  for(const change of [{activeRecording:true},{activeRecording:undefined},{running:true},{endList:false},{exitCode:1},{exitCode:null}]){
   const f=fixture();let retired=0;f.p.o.presentationEnded=()=>retired++;
   await f.start();await flush();f.p.firstFrameMs=12;f.v.currentTime=300;f.v.ended=true;
   f.st={...f.st,running:false,endList:true,activeRecording:false,exitCode:0,hlsSeconds:300,durationMs:300000,...change};
   await f.p.ended();assert.equal(retired,0,JSON.stringify(change));f.p.stop();
  }
  for(const scenario of ['dvd','paused','not-ended','no-picture','truncated']){
   const f=fixture();let retired=0;f.p.o.presentationEnded=()=>retired++;
   await f.start();await flush();f.p.firstFrameMs=12;f.v.currentTime=300;f.v.ended=true;
   f.st={...f.st,running:false,endList:true,activeRecording:false,exitCode:0,hlsSeconds:300,durationMs:300000};
   if(scenario==='dvd')f.p.dvd=true;
   if(scenario==='paused')f.p.intentPaused=true;
   if(scenario==='not-ended')f.v.ended=false;
   if(scenario==='no-picture')f.p.firstFrameMs=null;
   if(scenario==='truncated')f.v.currentTime=200;
   await f.p.ended();assert.equal(retired,0,scenario);f.p.stop();
  }
 });
 await test('late EOF status cannot clear a replacement and delayed clean receipt clears once',async()=>{
  const f=fixture();let retired=0;f.p.o.presentationEnded=()=>retired++;
  await f.start();await flush();f.p.firstFrameMs=0;f.v.currentTime=300;f.v.ended=true;
  f.st={...f.st,running:false,endList:true,activeRecording:false,exitCode:null,hlsSeconds:300,durationMs:300000};
  await f.p.ended();assert.equal(retired,0);f.st.exitCode=0;
  await f.p.hlsHealth();await f.p.hlsHealth();assert.equal(retired,1);
  const d=deferred(),real=f.p.o.status;f.p.o.status=()=>d.promise;
  const pending=f.p.ended();await flush();f.p.stop();f.p.o.status=real;
  await f.start('replacement');await flush();d.resolve({...f.st,session:'a'});await pending;
  assert.equal(retired,1);assert.equal(f.p.id,'replacement');f.p.stop();
 });
 await test('failed exact DVD converter stops unsupported recording recovery without consuming retries',async()=>{
  const f=fixture();await f.start('dvd-failed',{dvd:true});await flush();
  f.p.dvd=true;f.p.status={session:'dvd-failed',dvd:true,running:false,endList:false,exitCode:139,error:'Broken pipe'};
  assert.equal(await f.p.recover('Stopped producer'),false);assert(f.p.intentPaused);assert(f.v.paused);
  assert.equal(f.p.budget.count,0);assert.equal(f.recoveries.length,0);assert(f.messages.at(-1).includes('Restart the title'));f.p.stop();
 });
 await test('DVD terminal-failure guard rejects stale unknown healthy and clean cell status',async()=>{
  for(const change of [{session:'other'},{dvd:false},{running:true},{endList:true},{exitCode:0},{exitCode:-2147483648},{exitCode:null}]){
   const f=fixture();await f.start('dvd-current');await flush();f.p.dvd=true;
   f.p.status={session:'dvd-current',dvd:true,running:false,endList:false,exitCode:139,...change};
   assert.equal(await f.p.recover('test'),true);assert.equal(f.recoveries.length,1);f.p.stop();
  }
 });
 async function rejectedNative(paused=false,resumeSeconds=0){
  const f=fixture();f.v.canPlayType=()=> 'probably';f.v.disableRemotePlayback=false;
  f.v.load=function(){this.currentTime=0;this.error=null;};
  f.v.addEventListener=()=>{};
  await f.start('native-rejected',{startSeconds:60,paused,resumeSeconds,streamSettings:{requested:{player:'native',allowFallback:true}}});
  f.st={...f.st,session:'native-rejected',dvd:false,playlistUrl:'hls/native-rejected/stream.m3u8'};
  f.v.error={code:4};return f;
 }
 await test('native HLS rejection before first picture reattaches SAME producer to MSE once, preserving Pause/source/profiles',async()=>{
  for(const paused of [false,true]){
   const f=await rejectedNative(paused),profile=JSON.stringify(f.p.streamSettings);
   await f.p.hlsHealth();await flush();
   assert.equal(f.instances.length,1);assert.equal(f.p.id,'native-rejected');
   assert.equal(f.instances[0].url,'hls/native-rejected/stream.m3u8');
   assert.equal(f.instances[0].config.startPosition,0);assert.equal(f.p.startSeconds,60);
   assert.equal(f.p.intentPaused,paused);assert.equal(f.v.paused,paused);
   assert.equal(JSON.stringify(f.p.streamSettings),profile);
   assert.equal(f.p.snapshot().nativeHlsFallbackResult,'attached');
   assert.equal(f.recoveries.length,0);assert.equal(f.fallbacks.length,0);
   await f.p.hlsHealth();assert.equal(f.instances.length,1);f.p.stop();
   assert.equal(f.v.disableRemotePlayback,false);
  }
 });
 await test('native rejection keeps explicit initial representation offset, never an undecoded native timestamp',async()=>{
  const f=await rejectedNative(false,6.25);f.v.currentTime=.12;f.v.error={code:3};
  await f.p.hlsHealth();assert.equal(f.instances[0].config.startPosition,6.25);
  assert.equal(f.p.startSeconds,60);assert.equal(f.recoveries.length,0);f.p.stop();
 });
 await test('native first-picture fallback refuses strict late network remote DVD stale and other decoders',async()=>{
  for(const reason of ['strict','strict-text','late','network','abort','healthy','blocked','recovering','ended','seeking','remote','remote-unknown','dvd','missing-dvd-state','wrong-session','wrong-path','not-ready','mse','ts','stopped']){
   const f=await rejectedNative();
   if(reason==='strict')f.p.streamSettings.requested.allowFallback=false;
   if(reason==='strict-text')f.p.streamSettings.requested.allowFallback='false';
   if(reason==='late')f.p.firstFrameMs=12;if(reason==='network')f.v.error={code:2};if(reason==='abort')f.v.error={code:1};
   if(reason==='healthy')f.v.error=null;if(reason==='blocked')f.p.blocked=true;if(reason==='recovering')f.p.recovering=true;
   if(reason==='ended')f.v.ended=true;if(reason==='seeking')f.v.seeking=true;
   if(reason==='remote')f.v.remote={state:'connected'};if(reason==='remote-unknown')f.v.remote={state:'unknown'};
   if(reason==='dvd')f.p.dvd=true;if(reason==='missing-dvd-state')delete f.st.dvd;
   if(reason==='wrong-session')f.st.session='other';if(reason==='wrong-path')f.st.playlistUrl='hls/other/stream.m3u8';
   if(reason==='not-ready')f.st.playlistReady=false;
   if(reason==='mse')f.p.hls={destroy(){}};if(reason==='ts')f.p.tsPlayer={destroy(){}};if(reason==='stopped')f.p.stop();
   assert.equal(await f.p.tryNativeHlsMse(f.p.generation,f.st),false,reason);assert.equal(f.instances.length,0,reason);f.p.stop();
  }
 });
 await test('native fallback asynchronous library cannot outlive Stop new source or policy/remote changes',async()=>{
  for(const reason of ['stop','new-source','strict','remote']){
   const f=await rejectedNative(),d=deferred();f.p.status=f.st;f.p.o.loadHls=()=>d.promise;
   const pending=f.p.tryNativeHlsMse(f.p.generation,f.st);await flush();assert(f.p.nativeHlsFallbackPending);
   if(reason==='stop')f.p.stop();if(reason==='new-source'){f.p.o.loadHls=async()=>f.Hls;await f.start('new-source',{streamSettings:{requested:{player:'native'}}});}
   if(reason==='strict')f.p.streamSettings.requested.allowFallback=false;if(reason==='remote')f.v.remote={state:'connected'};
   d.resolve(f.Hls);await pending;assert.equal(f.instances.length,0,reason);f.p.stop();
  }
 });
 await test('native fallback missing support and failed attachment are terminal per producer, never encoder recovery',async()=>{
  for(const reason of ['missing','throw','attach']){
   const f=await rejectedNative();
   class BrokenHls extends f.Hls{attachMedia(){throw Error('Deliberate attach failure')}}
   let loads=0;f.p.o.loadHls=async()=>{loads++;if(reason==='throw')throw Error('Missing library');return reason==='missing'?null:BrokenHls};
   await f.p.hlsHealth();await f.p.hlsHealth();assert.equal(loads,reason==='attach'?2:1);
   assert.equal(f.p.nativeHlsFallbackResult,reason==='attach'?'failed':'unavailable');
   assert.equal(f.recoveries.length,0);assert.equal(f.fallbacks.length,0);
   if(reason==='attach'){assert(f.instances[0].destroyed);assert.equal(f.v.disableRemotePlayback,false);}f.p.stop();
  }
 });
 await test('negotiated forward rates affect only the browser clock, preserving Pause/source/decoder ownership',async()=>{
  const f=fixture();await f.start();await flush();f.p.control('pause');f.v.currentTime=42;
  const decoder=f.instances[0],loads=decoder.loads.slice();
  for(const rate of [.5,1,1.5,2]){f.p.control('rate',rate);assert.equal(f.v.playbackRate,rate);assert(f.v.paused);assert.equal(f.v.currentTime,42);assert.equal(f.p.id,'a');}
  for(const rate of [-2,0,NaN,Infinity]){f.p.control('rate',rate);assert.equal(f.v.playbackRate,2);}
  f.p.control('rate',1);assert.equal(f.v.playbackRate,1);assert.equal(f.instances.length,1);assert.deepEqual(decoder.loads,loads);assert.equal(f.recoveries.length,0);f.p.stop();
 });
 await test('starts on one published segment, no fixed 10-second gate',async()=>{const f=fixture();await f.start();await flush();assert.equal(f.instances.length,1);assert.equal(f.instances[0].config.startPosition,0);assert.deepEqual(f.instances[0].loads,[0]);assert.equal(f.p.snapshot().attached,true);f.p.stop();});
 await test('quality handoff joins or restores an existing HLS representation without replaying zero',async()=>{const f=fixture();await f.start('handoff',{startSeconds:4,resumeSeconds:2.25,seek:true});assert.equal(f.instances[0].config.startPosition,2.25);assert.deepEqual(f.instances[0].loads,[2.25]);await f.start('rollback',{startSeconds:0,resumeSeconds:6.25,seek:true,recovery:true});assert.equal(f.instances[1].config.startPosition,6.25);assert.deepEqual(f.instances[1].loads,[6.25]);f.p.stop();});
 await test('Copy HLS initial buffered gap cannot deadlock reserve refill after seek',async()=>{
  const f=fixture();await f.start('copy-gap',{seek:true,startSeconds:60,streamSettings:{requested:{videoMode:'copy',allowFallback:false},effective:{video:'copy'}}});await flush();
  f.v.currentTime=.256880724;f.v.ranges=[[.746333,183.125333]];f.st.hlsSeconds=183.2;
  await f.p.hlsHealth();await flush();
  assert.equal(f.v.currentTime,.746333,'join actual first buffered sample, not a guessed file position');
  assert(!f.p.rebuffering&&!f.v.paused);assert.equal(f.p.startSeconds,60);
  assert.equal(f.recoveries.length,0);assert.equal(f.fallbacks.length,0);
  assert.equal(f.p.snapshot().initialCopyGapAlignedSeconds,.746333);
  f.v.currentTime=.8;f.v.ranges=[[1.2,183.125333]];await f.p.hlsHealth();
  assert.equal(f.v.currentTime,.8,'only one alignment attempt in this producer');f.p.stop();
 });
 await test('Copy initial gap alignment preserves paused/blocked/resume/DVD/non-Copy/native and large/late/undecoded gaps',async()=>{
  for(const mode of ['pause','blocked','resume','dvd','transcode','native','large','late','undecoded','metadata','short','inside','decode-error','ended','seeking','recovering','changing-range']){
   const f=fixture(),requested={videoMode:mode==='transcode'?'transcode':'copy',allowFallback:false};
   if(mode==='native'){requested.player='native';f.v.canPlayType=()=> 'probably';}
   await f.start('gap-negative-'+mode,{dvd:mode==='dvd',resumeSeconds:mode==='resume'?.4:0,streamSettings:{requested,effective:{video:mode==='transcode'?'libx264':'copy'}}});await flush();
   f.v.currentTime=mode==='late'?1.5:mode==='inside'?.8:.25;
   f.v.ranges=[[mode==='large'?1.25:mode==='late'?2:.746333,mode==='short'?.8:183]];
   if(mode==='pause')f.p.control('pause');if(mode==='blocked')f.p.blocked=true;
   if(mode==='undecoded')f.v.videoWidth=0;if(mode==='metadata')f.v.readyState=1;
   if(mode==='decode-error')f.v.error={code:3};if(mode==='ended')f.v.ended=true;
   if(mode==='seeking')f.v.seeking=true;if(mode==='recovering')f.p.recovering=true;
   if(mode==='changing-range')Object.defineProperty(f.v,'buffered',{get:()=>({length:1,start:()=>{throw Error('Range changed')}})});
   const before=f.v.currentTime;assert.equal(f.p.alignInitialCopyGap(),false,mode);assert.equal(f.v.currentTime,before,mode);
   assert.equal(f.p.snapshot().initialCopyGapAlignedSeconds,null,mode);f.p.stop();
  }
 });
 await test('Copy startup gap setter failure is attempted once and never replays a seek',async()=>{
  const f=fixture();await f.start('gap-failed',{streamSettings:{requested:{videoMode:'copy'},effective:{video:'copy'}}});await flush();
  f.v.ranges=[[.75,5]];let sets=0;Object.defineProperty(f.v,'currentTime',{get:()=>.25,set:()=>{sets++;throw Error('Deliberate setter failure')}});
  assert.equal(f.p.alignInitialCopyGap(),false);assert.equal(f.p.alignInitialCopyGap(),false);assert.equal(sets,1);assert.equal(f.p.snapshot().initialCopyGapAlignedSeconds,null);f.p.stop();
 });
 await test('network estimate excludes producer wait, expires and rejects retired callbacks',async()=>{
  const f=fixture();await f.start();const old=f.instances[0];
  old.handlers.loaded('loaded',{frag:{stats:{loaded:100000,loading:{start:0,first:5000,end:5500}}}});
  assert.equal(f.p.snapshot().network.throughputKbps,1600);assert.equal(f.p.snapshot().network.samples,1);
  old.handlers.loaded('loaded',{frag:{stats:{loaded:100000,loading:{start:0,first:5000,end:5001}}}});
  assert.equal(f.p.snapshot().network.samples,1,'cached/tiny transfer is not measured');
  f.clock.t+=15001;assert.equal(f.p.snapshot().network.throughputKbps,null);
  await f.start('replacement');old.handlers.loaded('loaded',{frag:{stats:{loaded:100000,loading:{first:0,end:500}}}});
  assert.equal(f.p.snapshot().network.throughputKbps,null);assert.equal(f.p.snapshot().network.samples,0);f.p.stop();
 });
 await test('native HLS exposes unavailable transfer timing instead of invented bandwidth',async()=>{
  const f=fixture();f.v.canPlayType=()=> 'probably';await f.start('native',{streamSettings:{requested:{player:'native'}}});
  assert.equal(f.p.snapshot().network.throughputKbps,null);assert.equal(f.p.snapshot().network.method,'unavailable');f.p.stop();
 });
 await test('native HLS restores the handoff offset after metadata, ignoring retired callbacks',async()=>{
  const f=fixture(),listeners=[];f.v.canPlayType=()=> 'probably';
  f.v.addEventListener=(name,callback,options)=>listeners.push({name,callback,options});
  await f.start('native-old',{resumeSeconds:2,streamSettings:{requested:{player:'native'}}});
  await f.start('native-new',{resumeSeconds:6.25,streamSettings:{requested:{player:'native'}}});
  listeners[0].callback();assert.equal(f.v.currentTime,0,'old metadata cannot seek the new stream');
  assert.equal(listeners[1].name,'loadedmetadata');assert.equal(listeners[1].options.once,true);
  listeners[1].callback();assert.equal(f.v.currentTime,6.25);assert.equal(f.p.resumeSeconds,0);f.p.stop();
 });
 await test('ready startup exposes separate discovery/library/attach timings',async()=>{const f=fixture();await f.start();const timing=f.p.snapshot().startupTiming;assert.equal(timing.readyObservedMs,0);assert.equal(timing.libraryWaitMs,0);assert.equal(timing.attachedMs,0);assert.equal(timing.polls,1);f.p.stop();});
 await test('early published segment is found within the bounded 100ms phase',async()=>{const f=fixture();f.st.playlistReady=false;f.st.segments=0;const pending=f.start();await flush();assert.equal(f.instances.length,0);f.st.playlistReady=true;f.st.segments=1;f.clock.advance(100);await pending;assert.equal(f.instances.length,1);assert.equal(f.p.snapshot().startupTiming.readyObservedMs,100);f.p.stop();});
 await test('manual startup threshold respected without blocking',async()=>{const f=fixture({startSegments:3});const pending=f.start();await flush();assert.equal(f.instances.length,0);f.st.segments=3;f.clock.advance(250);await pending;assert.equal(f.instances.length,1);f.p.stop();});
 await test('short completed media does not wait for nonexistent segments',async()=>{const f=fixture({startSegments:10});f.st.endList=true;f.st.running=false;await f.start();assert.equal(f.instances.length,1);f.p.stop();});
 await test('starvation pauses, replenished buffer resumes without undefined variable',async()=>{const f=fixture();await f.start();await flush();f.v.ranges=[];await f.p.hlsHealth();assert(f.p.rebuffering);assert(f.v.paused);f.v.ranges=[[0,4]];await f.p.hlsHealth();await flush();assert(!f.p.rebuffering);assert(!f.v.paused);f.p.stop();});
 await test('user pause is not overridden by buffer refill',async()=>{const f=fixture();await f.start();await flush();f.p.control('pause');f.v.ranges=[[0,20]];const before=f.v.playCount;await f.p.hlsHealth();assert.equal(f.v.playCount,before);assert.equal(f.p.state().paused,true);f.p.stop();});
 await test('rebuffering reports play intent, not temporary video.pause',async()=>{const f=fixture();await f.start();await flush();await f.p.hlsHealth();assert(f.v.paused);assert.equal(f.p.state().paused,false);f.p.stop();});
 await test('browser state reports the native ended signal for DVD cell drain',async()=>{const f=fixture();await f.start('dvd',{dvd:true});f.v.ended=true;assert.equal(f.p.state().ended,true);assert.equal(f.p.state().expectedHlsSession,'dvd');f.p.stop();});
 await test('finished producer with unplayed content is not restarted',async()=>{const f=fixture();f.st={...f.st,running:false,endList:true,hlsSeconds:300};await f.start();f.v.ranges=[[0,120]];await f.p.hlsHealth();assert.equal(f.recoveries.length,0);f.p.stop();});
 await test('premature end recovery includes atomic absolute position and expected session',async()=>{const f=fixture();await f.start('old',{startSeconds:120});f.v.currentTime=5;f.st={...f.st,running:false,endList:true,hlsSeconds:5};await f.p.hlsHealth();assert.deepEqual(f.recoveries,[{timeMs:125000,expectedHlsSession:'old'}]);await f.p.hlsHealth();assert.equal(f.recoveries.length,1,'wait for replacement videoStart');f.p.stop();});
 await test('recovery counter persists across recovery sessions and caps at six',async()=>{const f=fixture();await f.start();for(let i=0;i<6;i++){assert(await f.p.recover('test'));await f.start('r'+i,{recovery:true,seek:true});}assert.equal(f.p.budget.count,6);assert.equal(await f.p.recover('test'),false);assert(f.p.intentPaused);assert.equal(f.recoveries.length,6);await f.start('manual',{seek:true});assert.equal(f.p.budget.count,0);f.p.stop();});
 await test('old asynchronous vendor load cannot attach to new recording',async()=>{const f=fixture(),d=deferred();f.p.o.loadHls=()=>d.promise;const first=f.start('old');await flush();f.p.o.loadHls=async()=>f.Hls;await f.start('new');d.resolve(f.Hls);await first;assert.equal(f.instances.length,1);assert(f.instances[0].url.includes('new'));f.p.stop();});
 await test('old status response cannot replace new session status',async()=>{const f=fixture(),d=deferred();await f.start('old');f.p.o.status=()=>d.promise;const stale=f.p.pollStatus();f.p.o.status=async id=>({...f.st,session:id,marker:'new'});await f.start('new');d.resolve({...f.st,session:'old',marker:'old'});await stale;assert.equal(f.p.status.marker,'new');f.p.stop();});
 await test('concurrent status polls share one request',async()=>{const f=fixture(),d=deferred();await f.start();let calls=0;f.p.o.status=()=>{calls++;return d.promise;};const a=f.p.pollStatus(),b=f.p.pollStatus();assert.equal(calls,1);d.resolve({...f.st,session:'a'});await Promise.all([a,b]);f.p.stop();});
 await test('seek startup reports offset without retaining prior currentTime',async()=>{const f=fixture(),d=deferred();await f.start();f.v.currentTime=40;f.v.load=()=>{};f.p.o.status=()=>d.promise;const start=f.start('b',{seek:true,startSeconds:100});await flush();assert.equal(f.p.absoluteTime(),100000);f.p.stop();d.resolve(f.st);await start;});
 await test('seek preserves pause intent',async()=>{const f=fixture();await f.start();f.p.control('pause');await f.start('b',{seek:true});await flush();assert(f.p.intentPaused);assert(f.v.paused);f.p.stop();});
 await test('autoplay denied displays user action; gesture retries',async()=>{const f=fixture();f.v.play=()=>Promise.reject(Object.assign(new Error('gesture'),{name:'NotAllowedError'}));await f.start();await flush();assert(f.p.blocked);f.v.play=()=>{f.v.paused=false;return Promise.resolve();};f.p.control('play',null,true);await flush();assert(!f.p.blocked);assert(!f.v.paused);f.p.stop();});
 await test('policy-compatible muted playback preserves explicit mute without pretending it has sound',async()=>{
  const f=fixture();f.v.muted=true;f.v.play=()=>{assert(f.v.muted);f.v.paused=false;return Promise.resolve();};
  await f.start();await flush();assert(!f.p.blocked);assert(!f.v.paused);assert(f.v.muted);f.p.stop();
 });
 await test('autoplay rejection never silently mutes or loops producer recovery',async()=>{
  const f=fixture();let calls=0;f.v.play=()=>{calls++;return Promise.reject(Object.assign(new Error('gesture required'),{name:'NotAllowedError'}));};
  await f.start();await flush();assert(f.p.blocked);assert(!f.v.muted);
  for(let n=0;n<3;n++){f.clock.t+=1000;await f.p.hlsHealth();await flush();}
  assert.equal(calls,1);assert.equal(f.recoveries.length,0);assert(!f.v.muted);assert(f.messages.some(x=>String(x).includes('Play video')));f.p.stop();
 });
 await test('source replacement reuses the same media element and preserves explicit mute',async()=>{
  const f=fixture(),element=f.v;f.v.muted=true;await f.start('first');await flush();await f.start('second');await flush();
  assert.equal(f.p.video,element);assert(f.v.muted);assert(f.instances[0].destroyed);assert.equal(f.instances[1].video,element);f.p.stop();
 });
 await test('completed DVD tail is allowed to reach actual ended instead of pausing on rounded EXTINF reserve',async()=>{
  const f=fixture();f.p.o.dvdMenu=()=>false;await f.start('dvd-tail',{dvd:true,durationMs:0});await flush();
  f.st={...f.st,running:false,endList:true,hlsSeconds:24.1};f.v.readyState=4;f.v.currentTime=23.2;f.v.ranges=[[0,23.4]];f.v.paused=false;
  await f.p.hlsHealth();await flush();assert.equal(f.p.rebuffering,false);assert.equal(f.v.paused,false);assert.equal(f.v.currentTime,23.2,'do not invent an ended clock');assert.equal(f.recoveries.length,0);f.p.stop();
 });
 await test('normal end does not loop recovery',async()=>{const f=fixture();f.st={...f.st,endList:true,running:false,hlsSeconds:300};await f.start();f.v.currentTime=300;f.v.ended=true;await f.p.ended();assert.equal(f.recoveries.length,0);f.p.stop();});
 await test('completed recording native HLS drains its real final samples despite rounded producer duration',async()=>{
  const f=fixture();f.v.canPlayType=()=> 'probably';await f.start('recording-tail',{durationMs:89984,streamSettings:{requested:{player:'native'}}});await flush();
  f.st={...f.st,running:false,endList:true,activeRecording:false,hlsSeconds:89.984};f.v.readyState=4;f.v.currentTime=89.3;f.v.ranges=[[0,89.4]];f.v.paused=false;
  await f.p.hlsHealth();assert.equal(f.p.rebuffering,false);assert.equal(f.v.paused,false);assert.equal(f.v.currentTime,89.3);assert.equal(f.v.ended,false);assert.equal(f.recoveries.length,0);f.p.stop();
 });
 await test('native HLS owns decoded-buffer gaps without a client pause or timestamp jump',async()=>{
  for(const inherited of [false,true]){
   const f=fixture();f.v.canPlayType=()=> 'probably';await f.start('native-gap',{durationMs:89984,streamSettings:{requested:{player:'native'}}});await flush();
   f.st={...f.st,running:false,endList:true,activeRecording:false,hlsSeconds:89.965};f.v.readyState=4;f.v.currentTime=4.085;f.v.ranges=[[8.007,89.726]];f.v.paused=inherited;f.p.rebuffering=inherited;f.p.firstFrameMs=100;
   await f.p.hlsHealth();await flush();assert.equal(f.p.rebuffering,false);assert.equal(f.v.paused,false);assert.equal(f.v.currentTime,4.085);assert.equal(f.v.ended,false);assert.equal(f.recoveries.length,0);f.p.stop();
  }
 });
 await test('native HLS actual starvation leaves browser loading and respects user pause/autoplay denial',async()=>{
  for(const mode of ['playing','user','blocked']){
   const f=fixture();f.v.canPlayType=()=> 'probably';await f.start('native-starved-'+mode,{streamSettings:{requested:{player:'native'}}});await flush();
   f.st={...f.st,running:true,endList:false,hlsSeconds:10};f.v.readyState=mode==='playing'?2:4;f.v.currentTime=4;f.v.ranges=[[8,10]];f.v.paused=mode!=='playing';f.p.intentPaused=mode==='user';f.p.blocked=mode==='blocked';const plays=f.v.playCount;
   await f.p.hlsHealth();assert.equal(f.v.paused,mode!=='playing');assert.equal(f.v.playCount,plays);assert.equal(f.v.currentTime,4);assert.equal(f.p.rebuffering,mode==='playing');f.p.stop();
  }
 });
 await test('completed MSE tail wakes its last subsecond fragment without replaying the producer or moving time',async()=>{
  const f=fixture();await f.start('last-fragment',{startSeconds:78,durationMs:89984});await flush();
  f.st={...f.st,running:false,endList:true,activeRecording:false,hlsSeconds:11.945};
  Object.assign(f.v,{currentTime:11.050666666,readyState:2,paused:true});f.v.ranges=[[.021333,11.032332]];
  Object.assign(f.p,{rebuffering:true,lastAppendAt:1000,lastLoadAt:1000,lastLoaderWake:0});f.clock.t=12001;
  await f.p.hlsHealth();await flush();
  assert.equal(f.p.loaderWakeups,1);assert.equal(f.instances[0].loads.at(-1),11.050666666);
  assert.equal(f.v.currentTime,11.050666666);assert.equal(f.v.ended,false);assert.equal(f.recoveries.length,0);f.p.stop();
 });
 await test('subsecond loader margin refuses live unknown running failed truncated DVD and non-HLS source truth',async()=>{
  for(const mode of ['live','unknown','running','open','error','truncated','dvd','mpegts']){
   const f=fixture();await f.start('last-'+mode,{startSeconds:78,durationMs:mode==='truncated'?300000:89984});await flush();
   f.st={...f.st,running:mode==='running',endList:mode!=='open',activeRecording:mode==='unknown'?undefined:mode==='live',hlsSeconds:11.945,error:mode==='error'?'failed':''};
   Object.assign(f.v,{currentTime:11.050666666,readyState:2,paused:true});f.v.ranges=[[.021333,11.032332]];
   Object.assign(f.p,{rebuffering:true,lastAppendAt:1000,lastLoadAt:1000,lastLoaderWake:0});f.clock.t=12001;
   if(mode==='dvd')f.p.dvd=true;if(mode==='mpegts')f.p.transport='mpegts';
   await f.p.hlsHealth();await flush();assert.equal(f.p.loaderWakeups,0,mode);assert.equal(f.v.currentTime,11.050666666);f.p.stop();
  }
 });
 await test('completed recording tail releases only internal refill across native and MSE source epochs',async()=>{
  for(const engine of ['native','hls'])for(const mode of ['internal','user','blocked']){
   const f=fixture();f.v.canPlayType=()=> 'probably';await f.start('recording-tail-'+engine+mode,{startSeconds:30,durationMs:119984,streamSettings:{requested:{player:engine}}});await flush();
   f.st={...f.st,running:false,endList:true,activeRecording:false,hlsSeconds:89.984};f.v.readyState=4;f.v.currentTime=89.3;f.v.ranges=[[0,89.4]];f.v.paused=true;f.p.rebuffering=true;
   f.p.intentPaused=mode==='user';f.p.blocked=mode==='blocked';const plays=f.v.playCount;await f.p.hlsHealth();await flush();
   assert.equal(f.v.playCount,plays+(mode==='internal'?1:0));assert.equal(f.v.paused,mode!=='internal');assert.equal(f.v.currentTime,89.3);assert.equal(f.v.ended,false);assert.equal(f.recoveries.length,0);f.p.stop();
  }
 });
 await test('recording tail exception refuses unknown/live/running/truncated/error/non-HLS output',async()=>{
  for(const mode of ['unknown-source','live','running','no-endlist','unknown-duration','far-duration','error','mpegts']){
   const f=fixture();await f.start('unsafe-tail-'+mode,{durationMs:mode==='unknown-duration'?0:mode==='far-duration'?300000:89984});await flush();
   f.st={...f.st,running:mode==='running',endList:mode!=='no-endlist',activeRecording:mode==='unknown-source'?undefined:mode==='live',hlsSeconds:89.984};f.v.readyState=4;f.v.currentTime=89.3;f.v.ranges=[[0,89.4]];f.v.paused=false;
   if(mode==='error')f.v.error={code:2};if(mode==='mpegts')f.p.transport='mpegts';
   await f.p.hlsHealth();assert.equal(f.p.rebuffering,true,mode);assert.equal(f.v.paused,true,mode);f.p.stop();
  }
 });
 await test('completed DVD tail releases prior internal refill but preserves user pause and autoplay denial',async()=>{
  for(const mode of ['internal','user','blocked']){
   const f=fixture();f.p.o.dvdMenu=()=>false;await f.start('dvd-tail-'+mode,{dvd:true,durationMs:0});await flush();
   f.st={...f.st,running:false,endList:true,hlsSeconds:24.1};f.v.readyState=4;f.v.currentTime=23.2;f.v.ranges=[[0,23.4]];f.v.paused=true;f.p.rebuffering=true;
   f.p.intentPaused=mode==='user';f.p.blocked=mode==='blocked';const plays=f.v.playCount;await f.p.hlsHealth();await flush();
   if(mode==='internal'){assert.equal(f.p.rebuffering,false);assert.equal(f.v.paused,false);assert.equal(f.v.playCount,plays+1);}
   else{assert.equal(f.v.paused,true);assert.equal(f.v.playCount,plays);}
   assert.equal(f.v.ended,false);assert.equal(f.v.currentTime,23.2);f.p.stop();
  }
 });
 await test('DVD tail exception does not bypass running, live, unknown or undecoded producer buffering',async()=>{
  for(const mode of ['running','live','no-endlist','no-frame','ordinary']){
   const f=fixture();f.p.o.dvdMenu=()=>false;await f.start('tail-'+mode,{dvd:mode!=='ordinary',durationMs:0});await flush();
   f.st={...f.st,running:mode==='running',endList:mode!=='no-endlist',activeRecording:mode==='live',hlsSeconds:24.1};
   f.v.readyState=4;f.v.videoWidth=mode==='no-frame'?0:1280;f.v.currentTime=23.2;f.v.ranges=[[0,23.4]];f.v.paused=false;
   await f.p.hlsHealth();assert.equal(f.p.rebuffering,true,mode);assert.equal(f.v.paused,true,mode);f.p.stop();
  }
 });
 await test('native HLS uses same startup and pause policy',async()=>{const f=fixture();f.p.o.nativePreferred=true;f.v.canPlayType=()=> 'probably';await f.start();assert.equal(f.instances.length,0);assert.equal(f.v.src,'hls/a/stream.m3u8');f.p.control('pause');assert(f.p.intentPaused);f.p.stop();});
 await test('explicit Native selects platform HLS without a vendor load',async()=>{const f=fixture();f.v.canPlayType=()=> 'probably';f.p.o.loadHls=()=>{throw Error('native must not load hls.js');};await f.start('native',{streamSettings:{requested:{player:'native'}}});assert.equal(f.instances.length,0);assert.equal(f.p.snapshot().browserEngine,'Native HLS');f.p.stop();});
 await test('explicit HLS/MSE overrides automatic Safari native preference',async()=>{const f=fixture();f.p.o.nativePreferred=true;f.v.canPlayType=()=> 'probably';await f.start('mse',{streamSettings:{requested:{player:'hls'}}});assert.equal(f.instances.length,1);assert.equal(f.p.snapshot().browserEngine,'HLS / MSE');f.p.stop();});
 await test('TS Copy decode failure asks once for codec replacement, not another Copy transport',async()=>{for(const code of [3,4]){const f=fixture();await f.start('ts-copy-error',{startSeconds:30,streamSettings:{requested:{videoMode:'copy',allowFallback:true},effective:{video:'copy'}}});f.p.transport='mpegts';f.v.error={code};f.v.currentTime=.2;await f.p.fallbackTs('actual decode failure');await f.p.hlsHealth();assert.deepEqual(f.fallbacks,[{timeMs:30200,expectedHlsSession:'ts-copy-error',videoDecodeFailure:true}]);assert.equal(f.recoveries.length,0);f.p.stop();}});
 await test('TS Copy replacement preserves pause/autoplay/strict and a failed request never loops recovery',async()=>{for(const mode of ['paused','blocked','strict','failed']){const f=fixture();await f.start('ts-guard',{streamSettings:{requested:{videoMode:'copy',allowFallback:mode!=='strict'},effective:{video:'copy'}}});f.p.transport='mpegts';f.v.error={code:3};if(mode==='paused')f.p.control('pause');if(mode==='blocked')f.p.blocked=true;if(mode==='failed')f.p.o.fallback=async x=>{f.fallbacks.push(x);throw Error('compatibility failed')};await f.p.fallbackTs('decode failure');f.clock.t=60000;await f.p.hlsHealth();assert.equal(f.fallbacks.length,mode==='failed'?1:0,mode);assert.equal(f.recoveries.length,0,mode);if(mode==='failed'||mode==='strict')assert(f.p.intentPaused);f.p.stop();}});
 await test('explicit Copy decode error with dimensions uses its permitted one-shot H.264 fallback',async()=>{for(const code of [3,4]){const f=fixture();await f.start('copy-error',{startSeconds:30,streamSettings:{requested:{videoMode:'copy',allowFallback:true},effective:{video:'copy'}}});f.v.error={code};f.v.currentTime=.2;await f.p.hlsHealth();await f.p.hlsHealth();assert.deepEqual(f.fallbacks,[{timeMs:30200,expectedHlsSession:'copy-error'}]);assert.equal(f.recoveries.length,0);f.p.stop();}});
 await test('Copy decode fallback preserves strict policy and ignores network, abort, pause and retired media',async()=>{for(const which of ['strict','network','abort','paused','blocked','transcode','retired']){const f=fixture();await f.start('copy-guard',{streamSettings:{requested:{videoMode:which==='transcode'?'transcode':'copy',allowFallback:which!=='strict'},effective:{video:which==='transcode'?'libx264':'copy'}}});f.v.error={code:which==='network'?2:which==='abort'?1:3};if(which==='paused')f.p.control('pause');if(which==='blocked')f.p.blocked=true;if(which==='retired')f.p.stop();await f.p.hlsHealth();assert.equal(f.fallbacks.length,0,which);if(which==='strict')assert(f.messages.some(m=>String(m).includes('Automatic fallback is disabled')));f.p.stop();}});
 await test('MPEG-2 Copy falls back to H.264 when timeline advances without decoded video',async()=>{const f=fixture();f.v.videoWidth=0;f.v.videoHeight=0;await f.start('m2',{streamSettings:{requested:{videoMode:'copy',allowFallback:true},effective:{video:'copy',mpeg2Copy:true},source:{tracks:[{type:'video',codec:'mpeg2video'}]}}});f.v.currentTime=1.2;f.v.ranges=[[0,3]];f.st.hlsSeconds=5;f.clock.t=9001;await f.p.hlsHealth();assert.deepEqual(f.fallbacks,[{timeMs:1200,expectedHlsSession:'m2'}]);assert(f.messages.some(m=>String(m).includes('restarting as H.264')));f.p.stop();});
 await test('MPEG-2 Copy stays native when video dimensions decode',async()=>{const f=fixture();await f.start('m2ok',{streamSettings:{requested:{videoMode:'copy',allowFallback:true},effective:{video:'copy',mpeg2Copy:true},source:{tracks:[{type:'video',codec:'mpeg2video'}]}}});f.v.currentTime=1.2;f.v.ranges=[[0,3]];f.st.hlsSeconds=5;f.clock.t=9001;await f.p.hlsHealth();assert.equal(f.fallbacks.length,0);f.p.stop();});
 await test('Copy fallback is codec-agnostic when explicit stream copy advances without video',async()=>{const f=fixture();f.v.videoWidth=0;f.v.videoHeight=0;await f.start('copy-any',{streamSettings:{requested:{videoMode:'copy',allowFallback:true},effective:{video:'copy'},source:{tracks:[{type:'video',codec:'vp9'}]}}});f.v.currentTime=1.1;f.v.ranges=[[0,3]];f.st.hlsSeconds=5;f.clock.t=9001;await f.p.hlsHealth();assert.deepEqual(f.fallbacks,[{timeMs:1100,expectedHlsSession:'copy-any'}]);assert(f.messages.some(m=>String(m).includes('restarting as H.264')));f.p.stop();});
 await test('old interrupted play promise cannot mutate replacement',async()=>{const f=fixture(),d=deferred();f.v.play=()=>d.promise;await f.start('old');f.v.play=()=>Promise.resolve();await f.start('new');await flush();d.reject(Object.assign(new Error('old'),{name:'NotAllowedError'}));await flush();assert(!f.p.blocked);f.p.stop();});
 await test('completed recording duration replaces scheduled duration',async()=>{const f=fixture();await f.start();f.st={...f.st,durationMs:5000,running:false,endList:true,hlsSeconds:5};f.v.currentTime=5;await f.p.hlsHealth();assert.equal(f.p.durationMs,5000);assert.equal(f.recoveries.length,0);f.p.stop();});

 await test('first appended fragment expands 6s startup target to 180s without reloading',async()=>{const f=fixture();await f.start();const h=f.instances[0];assert.equal(h.config.maxBufferLength,6);h.handlers.buffered();await flush();assert.equal(h.config.maxBufferLength,180);assert.equal(h.config.maxMaxBufferLength,180);assert.deepEqual(h.loads,[0]);assert.equal(f.p.snapshot().bufferPhase,'reserve');assert.equal(f.v.currentTime,0);f.p.stop();});
 await test('low-delay startup still fills a large ongoing reserve',async()=>{const f=fixture({bufferPreset:'lowdelay',maxBufferSeconds:300});await f.start();f.instances[0].handlers.buffered();assert.equal(f.p.snapshot().bufferTargetSeconds,300);f.p.stop();});
 await test('forward reserve change applies while playing without resetting playback',async()=>{const f=fixture();await f.start();const h=f.instances[0];h.handlers.buffered();f.v.currentTime=45;f.cfg.maxBufferSeconds=420;f.p.updateBufferSettings();assert.equal(h.config.maxBufferLength,420);assert.deepEqual(h.loads,[0]);assert.equal(f.v.currentTime,45);f.p.stop();});
 await test('settings unrelated to buffering preserve a library memory reduction',async()=>{const f=fixture();await f.start();const h=f.instances[0];h.handlers.buffered();h.config.maxMaxBufferLength=90;f.cfg.showStats=true;f.p.updateBufferSettings();assert.equal(h.config.maxMaxBufferLength,90);assert.equal(f.p.snapshot().bufferTargetSeconds,90);f.p.stop();});
 await test('loader is woken with 20s still buffered instead of waiting to stall',async()=>{const f=fixture();await f.start();const h=f.instances[0];h.handlers.buffered();f.v.currentTime=10;f.v.ranges=[[0,30]];f.st.hlsSeconds=150;f.clock.t+=9000;await f.p.hlsHealth();assert.deepEqual(h.loads,[0,10]);assert.equal(f.p.loaderWakeups,1);assert.equal(f.recoveries.length,0);assert(!f.v.paused);f.p.stop();});
 await test('refill continues while paused without autoplaying',async()=>{const f=fixture();await f.start();await flush();f.p.control('pause');const h=f.instances[0];h.handlers.buffered();f.v.ranges=[[0,10]];f.st.hlsSeconds=250;const before=f.v.playCount;f.clock.t+=9000;await f.p.hlsHealth();assert.equal(f.p.loaderWakeups,1);assert(f.v.paused);assert.equal(f.v.playCount,before);f.p.stop();});
 await test('normal appends fill reserve and continue topping up during long playback',async()=>{const f=fixture();await f.start();const h=f.instances[0];h.handlers.buffered();for(let i=0;i<240;i++){f.clock.t+=1000;f.v.currentTime=i;f.v.ranges=[[Math.max(0,i-30),i+Math.min(180,3+i*3)]];f.st.hlsSeconds=i+Math.min(360,3+i*4);h.handlers.loading();h.handlers.loaded();h.handlers.buffered();await f.p.hlsHealth();}assert.equal(f.p.snapshot().ahead,180);assert.equal(f.p.snapshot().bufferTargetSeconds,180);assert.equal(f.p.loaderWakeups,0);assert.deepEqual(h.loads,[0]);assert.equal(f.recoveries.length,0);f.p.stop();});
 await test('no refill restart at target or when producer has no additional data',async()=>{const f=fixture();await f.start();const h=f.instances[0];h.handlers.buffered();f.v.ranges=[[0,180]];f.st.hlsSeconds=500;f.clock.t+=9000;await f.p.hlsHealth();assert.equal(f.p.loaderWakeups,0);f.v.ranges=[[0,15]];f.st.hlsSeconds=15;f.p.status={...f.st};f.clock.t+=9000;await f.p.hlsHealth();assert.equal(f.p.loaderWakeups,0);f.p.stop();});
 await test('active slow fragment gets its timeout before a loader wakeup',async()=>{const f=fixture();await f.start();const h=f.instances[0];h.handlers.buffered();f.v.ranges=[[0,30]];f.st.hlsSeconds=300;h.handlers.loading();f.clock.t+=15000;await f.p.hlsHealth();assert.equal(f.p.loaderWakeups,0);f.clock.t+=6000;await f.p.hlsHealth();assert.equal(f.p.loaderWakeups,1);f.p.stop();});
 await test('buffer quota pressure reduces reserve and remains reduced',async()=>{const f=fixture();await f.start();const h=f.instances[0];h.handlers.buffered();h.handlers.error('error',{type:'media',details:'bufferFullError',fatal:false});assert(f.p.quotaLimited);assert.equal(f.p.snapshot().bufferTargetSeconds,90);f.cfg.maxBufferSeconds=600;f.p.updateBufferSettings();assert.equal(h.config.maxMaxBufferLength,90);f.p.stop();});
 await test('new recording resets phase and ignores old buffered callbacks',async()=>{const f=fixture();await f.start();const old=f.instances[0];old.handlers.buffered();await f.start('new');old.handlers.buffered();assert.equal(f.p.snapshot().bufferPhase,'startup');assert.equal(f.instances[1].config.maxBufferLength,6);f.p.stop();});
 await test('available server reserve is not discarded when producer stops advancing',async()=>{const f=fixture();await f.start();f.st.hlsSeconds=100;f.p.status={...f.st};f.p.lastProduced=100;f.p.lastProduceProgress=f.clock.now();f.p.starvedAt=1;f.clock.t=15000;await f.p.hlsHealth();assert.equal(f.recoveries.length,0);assert.equal(f.p.loaderWakeups,1);assert.equal(f.instances[0].loads.length,2,'proactive and reactive watchdogs must not duel');f.p.stop();});

 await test('unexplained browser clock regression is clamped within one media generation',async()=>{const f=fixture();await f.start('clock',{startSeconds:100});f.v.currentTime=20;assert.equal(f.p.absoluteTime(),120000);f.v.currentTime=2;assert.equal(f.p.absoluteTime(),120000);assert.equal(f.p.snapshot().clockRegressions,1);await f.start('back',{seek:true,startSeconds:10});assert.equal(f.p.absoluteTime(),10000);f.p.stop();});
 await test('ongoing source reads prevent producer restart while decode output is temporarily cold',async()=>{const f=fixture();await f.start();f.p.starvedAt=1;f.p.lastProduceProgress=1;f.p.lastInputProgress=f.clock.now();f.st={...f.st,hlsSeconds:0,bytesInput:100000,running:true};f.v.ranges=[];f.clock.t=15000;await f.p.hlsHealth();assert.equal(f.recoveries.length,0);f.p.stop();});
 await test('DVD epochs use one-segment startup and bounded 12-second reserve',async()=>{const f=fixture({startSegments:5,maxBufferSeconds:180,bufferPreset:'stable'});await f.start('dvd',{dvd:true,dvdGeneration:7});const h=f.instances[0];assert.equal(f.p.snapshot().dvd,true);assert.equal(f.p.snapshot().dvdGeneration,7);assert.equal(h.config.maxBufferLength,6);h.handlers.buffered();assert.equal(h.config.maxBufferLength,12);assert.equal(h.config.maxMaxBufferLength,12);f.p.stop();});
 await test('short completed DVD cell starts even when normal profile asks for many segments',async()=>{const f=fixture({startSegments:10,maxBufferSeconds:300});f.st={...f.st,segments:1,hlsSeconds:.5,running:false,endList:true};await f.start('dvdshort',{dvd:true,dvdGeneration:8,durationMs:0});assert.equal(f.instances.length,1);assert.equal(f.recoveries.length,0);f.p.stop();});
 await test('completed fresh decoded DVD menu clears misleading buffering without changing the player',async()=>{
  const f=fixture();f.p.o.dvdMenu=()=>true;await f.start('menu',{dvd:true,durationMs:0});
  f.st={...f.st,hlsSeconds:8,running:false,endList:true};f.v.readyState=4;f.v.currentTime=1.88;f.v.paused=true;
  f.p.rebuffering=true;f.p.starvedAt=1;const plays=f.v.playCount;
  await f.p.hlsHealth();assert.equal(f.p.rebuffering,false);assert.equal(f.messages.at(-1),'');
  assert.equal(f.v.currentTime,1.88);assert(f.v.paused);assert.equal(f.v.playCount,plays);assert.equal(f.recoveries.length,0);f.p.stop();
 });
 await test('menu feedback exception never masks feature, stale menu, missing frame or active producers',async()=>{
  for(const which of ['feature','unknown','stale','no-frame','running','not-ended','recording','not-dvd']){
   const f=fixture();f.p.o.dvdMenu=()=>which==='unknown'?null:!['feature','stale'].includes(which);
   await f.start('negative',{dvd:which!=='not-dvd',durationMs:0});
   f.st={...f.st,hlsSeconds:8,running:which==='running',endList:which!=='not-ended',activeRecording:which==='recording'};
   f.v.readyState=which==='no-frame'?1:4;f.v.currentTime=1.88;f.v.ranges=[];
   await f.p.hlsHealth();assert(f.p.rebuffering,which);assert.match(f.messages.at(-1),/Buffering/,which);f.p.stop();
  }
 });
 await test('fresh native DVD joins its first real buffered timestamp once without restarting',async()=>{
  const f=fixture();f.v.canPlayType=()=> 'probably';await f.start('gap',{dvd:true,streamSettings:{requested:{player:'native'}}});
  f.v.readyState=4;f.v.ranges=[[4,87]];f.st.hlsSeconds=87;f.st.running=false;f.st.endList=true;
  await f.p.hlsHealth();assert.equal(f.v.currentTime,4);assert.equal(f.p.snapshot().nativeDvdStartAlignedSeconds,4);assert.equal(f.recoveries.length,0);
  f.v.currentTime=0;f.v.ranges=[[5,87]];await f.p.hlsHealth();assert.equal(f.v.currentTime,0,'no second alignment in this generation');
  await f.start('next-gap',{dvd:true,streamSettings:{requested:{player:'native'}}});f.v.ranges=[[3,87]];await f.p.hlsHealth();assert.equal(f.v.currentTime,3);f.p.stop();
 });
 await test('native DVD start alignment preserves paused intent until explicit Play',async()=>{
  const f=fixture();f.v.canPlayType=()=> 'probably';await f.start('paused-gap',{dvd:true,paused:true,streamSettings:{requested:{player:'native'}}});
  f.v.readyState=4;f.v.ranges=[[4,87]];await f.p.hlsHealth();assert.equal(f.v.currentTime,0);assert.equal(f.p.nativeDvdStartAlignmentAttempted,false);
  f.p.control('play');await f.p.hlsHealth();assert.equal(f.v.currentTime,4);f.p.stop();
 });
 await test('native DVD alignment cannot jump ordinary, ongoing, explicit-resume, huge or undecoded gaps',async()=>{
  for(const which of ['ordinary','ongoing','resume','too-far','not-ready','blocked','mse','at-zero']){
   const f=fixture();f.v.canPlayType=()=> 'probably';await f.start('negative-gap',{dvd:which!=='ordinary',resumeSeconds:which==='resume'?2:0,streamSettings:{requested:{player:which==='mse'?'hls':'native'}}});
   f.v.readyState=which==='not-ready'?1:4;f.v.ranges=[[which==='too-far'?11:which==='at-zero'?0:4,87]];
   if(which==='ongoing')f.p.firstFrameMs=10;if(which==='blocked')f.p.blocked=true;
   await f.p.hlsHealth();assert.equal(f.v.currentTime,0,which);assert.equal(f.p.nativeDvdStartAlignmentAttempted,false,which);f.p.stop();
  }
 });
 async function tinyNativeMenu(){
  const f=fixture();f.menu=true;f.p.o.dvdMenu=()=>f.menu;f.v.canPlayType=()=> 'probably';f.v.disableRemotePlayback=false;
  await f.start('same-still',{dvd:true,dvdGeneration:7,durationMs:0,streamSettings:{requested:{player:'native',allowFallback:true}}});
  f.st={...f.st,session:'same-still',dvd:true,dvdGeneration:7,running:false,endList:true,activeRecording:false,
   dvdConverterEnded:true,exitCode:0,segments:1,hlsSeconds:.042,playlistUrl:'hls/same-still/stream.m3u8'};
  f.v.currentTime=.000001;f.v.duration=.000001;f.v.readyState=1;f.v.ranges=[];f.v.paused=true;f.v.ended=true;f.clock.t=3000;
  return f;
 }
 await test('native one-picture metadata-only menu hands same producer to MSE once without server recovery',async()=>{
  const f=await tinyNativeMenu();f.p.budget.count=2;const settings=JSON.stringify(f.p.streamSettings);
  await f.p.hlsHealth();await flush();
  assert.equal(f.instances.length,1);assert.equal(f.p.id,'same-still');assert.equal(f.instances[0].url,'hls/same-still/stream.m3u8');
  assert.equal(f.p.dvdGeneration,7);assert.equal(JSON.stringify(f.p.streamSettings),settings,'selected Native retained separately from actual MSE');
  assert.equal(f.p.snapshot().browserEngine,'HLS / MSE');assert.equal(f.p.snapshot().nativeDvdStillFallbackResult,'attached');
  assert.equal(f.p.budget.count,2);assert.equal(f.v.disableRemotePlayback,true);
  assert.equal(f.recoveries.length,0);assert.equal(f.fallbacks.length,0);
  await f.p.hlsHealth();assert.equal(f.instances.length,1);f.p.stop();assert.equal(f.v.disableRemotePlayback,false);
 });
 await test('one-picture fallback restores preexisting remote playback choice on Stop and next native source',async()=>{
  for(const before of [false,true]){const f=await tinyNativeMenu();f.v.disableRemotePlayback=before;await f.p.hlsHealth();
   assert.equal(f.v.disableRemotePlayback,true);await f.start('next-native',{streamSettings:{requested:{player:'native'}}});
   assert.equal(f.v.disableRemotePlayback,before);f.p.stop();assert.equal(f.v.disableRemotePlayback,before);}
 });
 await test('one-picture fallback refuses feature stale epoch pause autoplay strict running and real-picture cases',async()=>{
  for(const reason of ['wireless','remote-connecting','remote-connected','remote-unknown','not-dvd','menu','epoch','session','playlist','paused','blocked','recovering','rebuffering','frame','early','strict','running','open','recording','converter','exit','segments','long','zero','ready','width','height','not-ended','seeking','error','duration','nan','buffered','mse']){
   const f=await tinyNativeMenu();
   if(reason==='wireless')f.v.webkitCurrentPlaybackTargetIsWireless=true;
   if(reason.startsWith('remote-'))f.v.remote={state:reason.slice(7)};
   if(reason==='not-dvd')f.p.dvd=false;if(reason==='menu')f.menu=false;if(reason==='epoch')f.st.dvdGeneration=8;
   if(reason==='session')f.st.session='other';if(reason==='playlist')f.st.playlistUrl='hls/other/stream.m3u8';
   if(reason==='paused')f.p.intentPaused=true;if(reason==='blocked')f.p.blocked=true;if(reason==='recovering')f.p.recovering=true;
   if(reason==='rebuffering')f.p.rebuffering=true;if(reason==='frame')f.p.firstFrameMs=10;if(reason==='early')f.clock.t=1000;
   if(reason==='strict')f.p.streamSettings.requested.allowFallback=false;if(reason==='running')f.st.running=true;
   if(reason==='open')f.st.endList=false;if(reason==='recording')f.st.activeRecording=true;if(reason==='converter')f.st.dvdConverterEnded=false;
   if(reason==='exit')f.st.exitCode=1;if(reason==='segments')f.st.segments=2;if(reason==='long')f.st.hlsSeconds=2;if(reason==='zero')f.st.hlsSeconds=0;
   if(reason==='ready')f.v.readyState=2;if(reason==='width')f.v.videoWidth=0;if(reason==='height')f.v.videoHeight=0;
   if(reason==='not-ended')f.v.ended=false;if(reason==='seeking')f.v.seeking=true;if(reason==='error')f.v.error={code:4};
   if(reason==='duration')f.v.duration=.04;if(reason==='nan')f.v.duration=NaN;if(reason==='buffered')f.v.ranges=[[0,.03]];
   if(reason==='mse')f.p.hls={destroy(){}};
   assert.equal(await f.p.tryNativeDvdStillMse(f.p.generation,f.st),false,reason);
   assert.equal(f.instances.length,0,reason);assert.equal(f.v.disableRemotePlayback,false,reason);f.p.stop();
  }
 });
 await test('unsupported or failed MSE library never loops or starts another producer',async()=>{
  for(const mode of ['unsupported','failure']){const f=await tinyNativeMenu();let loads=0;
   f.p.o.loadHls=async()=>{loads++;if(mode==='failure')throw Error('asset unavailable');return {isSupported:()=>false};};
   await f.p.hlsHealth();await f.p.hlsHealth();assert.equal(loads,1);assert.equal(f.instances.length,0);
   assert.equal(f.p.nativeDvdStillFallbackResult,'unavailable');assert.equal(f.v.disableRemotePlayback,false);
   assert.equal(f.recoveries.length,0);assert.equal(f.fallbacks.length,0);f.p.stop();}
 });
 await test('late library resolution respects new source Stop pause menu and fallback-policy changes',async()=>{
  for(const change of ['source','stop','pause','menu','strict']){const f=await tinyNativeMenu(),d=deferred();
   f.p.o.loadHls=()=>d.promise;const pending=f.p.hlsHealth();await flush();
   assert.equal(f.p.nativeDvdStillFallbackResult,'loading');
   if(change==='source')await f.start('new-native',{streamSettings:{requested:{player:'native'}}});
   if(change==='stop')f.p.stop();if(change==='pause')f.p.control('pause');if(change==='menu')f.menu=false;
   if(change==='strict')f.p.streamSettings.requested.allowFallback=false;
   d.resolve(f.Hls);await pending;assert.equal(f.instances.length,0,change);assert.equal(f.v.disableRemotePlayback,false,change);f.p.stop();
  }
 });
 await test('failed MSE attachment retires its browser instance and restores remote playback without replay',async()=>{
  const f=await tinyNativeMenu();class BrokenHls extends f.Hls{attachMedia(){throw Error('MSE attach rejected');}}
  f.p.o.loadHls=async()=>BrokenHls;await f.p.hlsHealth();await flush();
  assert.equal(f.instances.length,1);assert.equal(f.instances[0].destroyed,true);
  assert.equal(f.p.nativeDvdStillFallbackResult,'failed');assert.equal(f.p.attached,false);
  assert.equal(f.v.disableRemotePlayback,false);assert.equal(f.recoveries.length,0);assert.equal(f.fallbacks.length,0);
  await f.p.hlsHealth();assert.equal(f.instances.length,1);f.p.stop();
 });
 async function stalledNativeFeature(){
  const f=fixture();f.menu=false;f.p.o.dvdMenu=()=>f.menu;f.v.canPlayType=()=> 'probably';f.v.disableRemotePlayback=false;
  await f.start('native-feature',{dvd:true,dvdGeneration:9,durationMs:5005,streamSettings:{requested:{player:'native',allowFallback:true}}});
  f.st={...f.st,session:'native-feature',dvd:true,dvdGeneration:9,running:false,endList:true,activeRecording:false,
    dvdConverterEnded:true,exitCode:0,segments:3,hlsSeconds:5,playlistUrl:'hls/native-feature/stream.m3u8'};
  f.v.currentTime=1.36;f.v.duration=1.418;f.v.readyState=2;f.v.ranges=[];f.v.paused=false;f.v.ended=false;
  f.p.lastTime=1.36;f.p.firstFrameMs=100;f.p.lastPlayProgress=1000;f.p.starvedAt=1000;f.clock.t=16000;
  f.p.status=f.st;return f;
 }
 async function stalledNativeDvdStartup(){
  const f=await stalledNativeFeature();f.v.currentTime=.000001;f.v.readyState=4;f.v.duration=Infinity;f.v.ranges=[[.000001,14.164]];
  f.p.firstFrameMs=null;f.p.lastTime=0;f.p.starvedAt=0;
  f.st={...f.st,running:true,endList:false,dvdConverterEnded:false,exitCode:null,segments:29,hlsSeconds:14.515};f.p.status=f.st;
  return f;
 }
 await test('native DVD startup frozen at zero with real buffered media uses SAME producer MSE once, not a seek or encode',async()=>{
  const f=await stalledNativeDvdStartup(),saved=JSON.stringify(f.p.streamSettings);
  await f.p.hlsHealth();assert.equal(f.instances.length,1);assert.equal(f.p.id,'native-feature');
  assert.equal(f.instances[0].url,'hls/native-feature/stream.m3u8');assert.equal(f.instances[0].config.startPosition,.000001);
  assert.equal(JSON.stringify(f.p.streamSettings),saved);assert.equal(f.recoveries.length,0);assert.equal(f.fallbacks.length,0);
  assert.equal(f.p.nativeDvdFeatureFallbackResult,'attached');await f.p.hlsHealth();assert.equal(f.instances.length,1);f.p.stop();
 });
 await test('zero-frame DVD startup decoder handoff preserves unknown remote pause policy source and active progress',async()=>{
  for(const reason of ['not-dvd','menu','unknown-menu','session','playlist','epoch','pause','element-pause','blocked','recovering','ended','seeking','error','decoded','progress','early','strict','strict-text','stopped','endlist','recording','converter','not-ready','width','height','empty','short','gap','wireless','remote-unknown']){
   const f=await stalledNativeDvdStartup();
   if(reason==='not-dvd')f.p.dvd=false;if(reason==='menu')f.menu=true;if(reason==='unknown-menu')f.menu=null;
   if(reason==='session')f.st.session='other';if(reason==='playlist')f.st.playlistUrl='hls/other/stream.m3u8';if(reason==='epoch')f.st.dvdGeneration=10;
   if(reason==='pause')f.p.intentPaused=true;if(reason==='element-pause')f.v.paused=true;if(reason==='blocked')f.p.blocked=true;if(reason==='recovering')f.p.recovering=true;
   if(reason==='ended')f.v.ended=true;if(reason==='seeking')f.v.seeking=true;if(reason==='error')f.v.error={code:2};if(reason==='decoded')f.p.firstFrameMs=50;
   if(reason==='progress')f.v.currentTime=1;if(reason==='early')f.p.lastPlayProgress=f.clock.now()-500;
   if(reason==='strict')f.p.streamSettings.requested.allowFallback=false;if(reason==='strict-text')f.p.streamSettings.requested.allowFallback='false';
   if(reason==='stopped')f.st.running=false;if(reason==='endlist')f.st.endList=true;if(reason==='recording')f.st.activeRecording=true;if(reason==='converter')f.st.dvdConverterEnded=true;
   if(reason==='not-ready')f.v.readyState=2;if(reason==='width')f.v.videoWidth=0;if(reason==='height')f.v.videoHeight=0;
   if(reason==='empty')f.v.ranges=[];if(reason==='short')f.v.ranges=[[0,1]];if(reason==='gap')f.v.ranges=[[2,14]];
   if(reason==='wireless')f.v.webkitCurrentPlaybackTargetIsWireless=true;if(reason==='remote-unknown')f.v.remote={state:'unknown'};
   assert.equal(await f.p.tryNativeDvdFeatureMse(f.p.generation,f.st),false,reason);assert.equal(f.instances.length,0,reason);f.p.stop();
  }
 });
 await test('zero-frame DVD startup cannot attach after an asynchronous source/pause/progress change',async()=>{
  for(const reason of ['source','pause','progress']){
   const f=await stalledNativeDvdStartup(),d=deferred();f.p.o.loadHls=()=>d.promise;
   const pending=f.p.tryNativeDvdFeatureMse(f.p.generation,f.st);await flush();
   if(reason==='source')await f.start('other',{streamSettings:{requested:{player:'native'}}});
   if(reason==='pause')f.p.control('pause');if(reason==='progress')f.p.firstFrameMs=100;
   d.resolve(f.Hls);await pending;assert.equal(f.instances.length,0,reason);f.p.stop();
  }
 });
 await test('completed native DVD feature stall reattaches the SAME produced bytes to MSE at last actual time, without server seek/recovery',async()=>{
  const f=await stalledNativeFeature(),saved=JSON.stringify(f.p.streamSettings);f.p.budget.count=2;
  await f.p.hlsHealth();await flush();
  assert.equal(f.instances.length,1);assert.equal(f.p.id,'native-feature');assert.equal(f.p.dvdGeneration,9);
  assert.equal(f.instances[0].url,'hls/native-feature/stream.m3u8');assert.equal(f.instances[0].config.startPosition,1.36);
  assert.deepEqual(f.instances[0].loads,[1.36]);assert.equal(JSON.stringify(f.p.streamSettings),saved);
  assert.equal(f.p.snapshot().browserEngine,'HLS / MSE');assert.equal(f.p.snapshot().nativeDvdFeatureFallbackResult,'attached');
  assert.equal(f.p.absoluteTime(),1360,'retain last actual same-producer clock while replacement attaches');
  assert.equal(f.p.budget.count,2);assert.equal(f.recoveries.length,0);assert.equal(f.fallbacks.length,0);
  assert.equal(f.v.disableRemotePlayback,true);await f.p.hlsHealth();assert.equal(f.instances.length,1);
  f.p.stop();assert.equal(f.v.disableRemotePlayback,false);
 });
 await test('native DVD feature recovery rejects every unknown/healthy/strict/stale/paused/unfinished source condition',async()=>{
  for(const reason of ['wireless','remote-connecting','remote-connected','remote-unknown','not-dvd','menu','unknown','epoch','session','playlist','pause','element-pause','blocked','recovering','ended','seeking','error','no-frame','early','progress','strict','strict-text','running','open','recording','converter','exit','one-segment','near-tail','full-duration','nan-duration','future-data','width','height','buffered','mse','ts','stop']){
   const f=await stalledNativeFeature();
   if(reason==='wireless')f.v.webkitCurrentPlaybackTargetIsWireless=true;
   if(reason.startsWith('remote-'))f.v.remote={state:reason.slice(7)};
   if(reason==='not-dvd')f.p.dvd=false;if(reason==='menu')f.menu=true;if(reason==='unknown')f.menu=null;
   if(reason==='epoch')f.st.dvdGeneration=10;if(reason==='session')f.st.session='other';if(reason==='playlist')f.st.playlistUrl='hls/other/stream.m3u8';
   if(reason==='pause')f.p.intentPaused=true;if(reason==='element-pause')f.v.paused=true;if(reason==='blocked')f.p.blocked=true;if(reason==='recovering')f.p.recovering=true;
   if(reason==='ended')f.v.ended=true;if(reason==='seeking')f.v.seeking=true;if(reason==='error')f.v.error={code:4};if(reason==='no-frame')f.p.firstFrameMs=null;
   if(reason==='early')f.p.starvedAt=f.clock.now()-1000;if(reason==='progress')f.p.lastPlayProgress=f.clock.now()-1000;
   if(reason==='strict')f.p.streamSettings.requested.allowFallback=false;if(reason==='strict-text')f.p.streamSettings.requested.allowFallback='false';
   if(reason==='running')f.st.running=true;if(reason==='open')f.st.endList=false;if(reason==='recording')f.st.activeRecording=true;
   if(reason==='converter')f.st.dvdConverterEnded=false;if(reason==='exit')f.st.exitCode=1;if(reason==='one-segment')f.st.segments=1;
   if(reason==='near-tail')f.st.hlsSeconds=3;if(reason==='full-duration')f.v.duration=5;if(reason==='nan-duration')f.v.duration=NaN;
   if(reason==='future-data')f.v.readyState=3;if(reason==='width')f.v.videoWidth=0;if(reason==='height')f.v.videoHeight=0;
   if(reason==='buffered')f.v.ranges=[[0,1.4]];if(reason==='mse')f.p.hls={destroy(){}};if(reason==='ts')f.p.tsPlayer={destroy(){}};if(reason==='stop')f.p.stop();
   assert.equal(await f.p.tryNativeDvdFeatureMse(f.p.generation,f.st),false,reason);assert.equal(f.instances.length,0,reason);assert.equal(f.recoveries.length,0,reason);f.p.stop();
  }
 });
 await test('feature handoff cannot outlive source Stop Pause policy menu clock or new buffered media',async()=>{
  for(const change of ['source','stop','pause','strict','menu','progress','buffered','wireless']){
   const f=await stalledNativeFeature(),d=deferred();f.p.o.loadHls=()=>d.promise;
   const pending=f.p.tryNativeDvdFeatureMse(f.p.generation,f.st);await flush();assert.equal(f.p.nativeDvdFeatureFallbackResult,'loading');
   if(change==='source')await f.start('different',{streamSettings:{requested:{player:'native'}}});if(change==='stop')f.p.stop();
   if(change==='pause')f.p.control('pause');if(change==='strict')f.p.streamSettings.requested.allowFallback=false;if(change==='menu')f.menu=true;
   if(change==='progress')f.p.lastPlayProgress=f.clock.now();if(change==='buffered')f.v.ranges=[[1,4]];
   if(change==='wireless')f.v.webkitCurrentPlaybackTargetIsWireless=true;
   d.resolve(f.Hls);await pending;assert.equal(f.instances.length,0,change);assert.equal(f.v.disableRemotePlayback,false,change);f.p.stop();
  }
 });
 await test('missing feature MSE support or failed attachment never repeats or restarts its producer',async()=>{
  for(const mode of ['unsupported','library-error','attach-error']){
   const f=await stalledNativeFeature();let loads=0;
   class Broken extends f.Hls{attachMedia(){throw Error('attachment rejected');}}
   f.p.o.loadHls=async()=>{loads++;if(mode==='library-error')throw Error('unavailable');return mode==='unsupported'?{isSupported:()=>false}:Broken;};
   await f.p.hlsHealth();const initialLoads=loads;await f.p.hlsHealth();assert.equal(loads,initialLoads,mode+' has no retry');assert.equal(loads,mode==='attach-error'?2:1,mode+' validation plus cached attachment load');assert.equal(f.recoveries.length,0);assert.equal(f.fallbacks.length,0);assert.equal(f.v.disableRemotePlayback,false);
   if(mode==='attach-error'){assert.equal(f.instances.length,1);assert(f.instances[0].destroyed);assert.equal(f.p.nativeDvdFeatureFallbackResult,'failed');}
   else{assert.equal(f.instances.length,0);assert.equal(f.v.currentTime,1.36);assert.equal(f.p.nativeDvdFeatureFallbackResult,'unavailable');}f.p.stop();
  }
 });
 await test('feature handoff holds only the old actual clock until new pictures catch up and restores remote playback on next source',async()=>{
  for(const before of [true,false]){
   const f=await stalledNativeFeature();f.v.disableRemotePlayback=before;await f.p.hlsHealth();
   assert.equal(f.p.absoluteTime(),1360);f.v.currentTime=1.4;assert.equal(f.p.absoluteTime(),1400);assert.equal(f.p.nativeDvdFeatureResumeFloorMs,null);
   await f.start('next',{streamSettings:{requested:{player:'native'}}});assert.equal(f.v.disableRemotePlayback,before);assert.equal(f.p.absoluteTime(),0);assert.equal(f.p.nativeDvdFeatureFallbackAttempted,false);f.p.stop();
  }
 });
 console.log('MiniClient playback: '+count+' tests PASS');
})().catch(e=>{console.error(e);process.exitCode=1;});
