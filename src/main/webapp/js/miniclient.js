(function(){
'use strict';
const $=id=>document.getElementById(id), Core=window.SageMiniCore;
const stage=$('stage'),visible=$('gfxCanvas'),visibleCtx=visible.getContext('2d',{alpha:true});
const video=$('videoPlane'),videoBounds=$('videoBounds'),dvdStill=$('dvdStillFrame'),dvdStillCtx=dvdStill.getContext('2d'),dvbCanvas=$('dvbCaptions'),dvbCtx=dvbCanvas.getContext('2d',{alpha:true}),fileSubCanvas=$('fileSubtitleCanvas'),fileSubCtx=fileSubCanvas.getContext('2d',{alpha:true}),dvdSpuCanvas=$('dvdSpuCanvas'),dvdSpuCtx=dvdSpuCanvas.getContext('2d',{alpha:true}),statusEl=$('connectionStatus'),msgEl=$('osdMessage'),statsEl=$('stats');
const dvdFrameCache=document.createElement('canvas'),dvdFrameCacheCtx=dvdFrameCache.getContext('2d');
const remotePanel=$('remotePanel'),settingsPanel=$('settingsPanel');
let mobileDock=null;
let settingsPage='all',settingsParent=null,settingsReturnIcon=null;
let settingsTreeReady=false;
let calibrationOwner=null,calibrationSerial=0,calibrationLease=null,calibrationHls=null;
let videoTestGeneration=0,dvdFrameGeneration=0,dvdFrozenGeneration=0,dvdFrameCacheValid=false,dvdFrameSamplerSerial=0,dvdFrameCaptures=0,dvdStillPromotions=0,dvdStillMisses=0;
const SETTINGS_KEY='sagetvWebMiniClientSettings.v1';
const Input=window.SageMiniInput,INPUT_KEY='sagetvWebInput.v1';
let inputSettings;try{inputSettings=Input.normalize(JSON.parse(localStorage.getItem(INPUT_KEY)||'{}'));}catch(_){inputSettings=Input.normalize({});}
function saveInputSettings(){inputSettings=Input.normalize(inputSettings);try{localStorage.setItem(INPUT_KEY,JSON.stringify(inputSettings));}catch(_){} }
const Streaming=window.SageMiniStreaming,Support=window.SageMiniSupport||Object.freeze({redact:v=>v,buildProfile:(a,b,c)=>({kind:'sagetv-webplayer-profile',schemaVersion:1,savedDefaults:{client:a,streaming:b,captions:c}}),previewProfile:v=>v,captionSummary:()=>({}),effectiveTranscode:()=>({})}),CaptionAuthority=window.SageMiniCaptionAuthority||Object.freeze({
  normalize:()=>({mode:'off',cc1Type:'auto',cc1Language:'',cc1Service:1,cc2Type:'auto',cc2Language:'',cc2Service:2}),
  effective:()=>({mode:'off',local:'off',label:'Off (caption authority module unavailable)'})
}),STREAMING_KEY='sagetvWebStreaming.v1',CAPTION_AUTHORITY_KEY='sagetvWebCaptionAuthority.v1';
let streaming=loadStreaming(),captionAuthority=loadCaptionAuthority(),captionInventory=[],captionAutoResolveBusy=false,mpegtsScriptPromise=null;
let sageTvCaptionStateSeen=false,sageTvCaptionState=0;
let captionWireStateSeen=false,lastCaptionEvent=null,captionSelectionSignature='',captionSelectionSerial=0;
let effectiveCaptionSelection=null;
let dvdMenuState=null,dvdMenuStateAt=0;
let lastVideoTest=null,pendingProfileImport=null,diagnosticStatus=null,lastServerConnectionStatus=null;
let activeVideoTest=null,currentVideoMediaId=null;
let diagnosticOperationId=null;const VIDEO_TEST_RECOVERY_KEY='sagetvWebVideoTestRecovery.v1';
function loadCaptionAuthority(){try{return CaptionAuthority.normalize(JSON.parse(localStorage.getItem(CAPTION_AUTHORITY_KEY)||'{}'));}catch(_){return CaptionAuthority.normalize({});}}
function saveCaptionAuthority(){captionAuthority=CaptionAuthority.normalize(captionAuthority);try{localStorage.setItem(CAPTION_AUTHORITY_KEY,JSON.stringify(captionAuthority));}catch(_){}}
function loadStreaming(){try{const v=Object.assign({},JSON.parse(localStorage.getItem(STREAMING_KEY)||'{}'),{audioTrack:-1,subtitleTrack:-1});if(v.subtitleMode==='track')v.subtitleMode='auto';return Streaming.normalize(v);}catch(_){return Streaming.normalize({});}}
let settings=loadSettings(),session='',stopped=false,connectionGeneration=0,rendererGeneration=0;
let failureSnapshot=null,nativeRecoveryCount=0;
let connectingGeneration=0,foregroundPending=false,foregroundProbe=0;
let explicitClientExit=false,explicitExitGeneration=0;
let eventController=null,eventChain=Promise.resolve(),inputChain=Promise.resolve(),inputPending=0,stateBusy=false;
let lastRequestedSize='',resizeInFlight=false,resizeAgain=false;
let renderQueued=0,renderQueuedBytes=0;
// Bounded counters only: no per-command trace allocation or image/identity data.
// A server-rendered menu crosses the network independently of video bitrate.
const renderPerformance={schedulerYields:0,decodedImages:0,imageDecodeMsLast:0,imageDecodeMsMax:0,
  presentedFrames:0,frameQueueMsLast:0,frameQueueMsMax:0,inputAcks:0,inputFailures:0,inputQueueMsLast:0,inputQueueMsMax:0,inputAckMsLast:0,inputAckMsMax:0,inputActionLast:'',eventReadPauses:0,eventReadPauseMsMax:0,eventReadPauseMsTotal:0};
const timedInputActions=new Set(['command','click','key','text','seek']);
let resizeTimer=null,stateTimer=null,hlsScriptPromise=null,currentMenuHint='',menuEpoch=0,guideTimer=null;
let browserLocalRate=1,browserRateError='';
let uiW=1280,uiH=720,currentTarget=0,mainSurface=makeCanvas(uiW,uiH);
let displayRect={left:0,top:0,width:1280,height:720},currentVideoBounds=[0,0,1280,720];
let nativeVideoBounds=[0,0,1280,720],nativeVideoSource=null,videoBoundsOrigin='initial',serverVideoAspect='source';
let videoPresentation=Core.videoPresentation(nativeVideoBounds,1280,720,'browser'),videoLayerRect=null;
let frame=0,gfxCount=0,imageCount=0,lastEventAt=0,lastError='',videoAspect=settings.videoFit;
let videoBoundsTrusted=false,lastTrustedVideoBounds=null,videoPresentationSuspended=false,frameHadClearRect=false;
let seeking=false,lastMove=0,lastBackAt=0,lastClick=null,repeatTimer=null,repeatInterval=null,pageRetired=false;
const Experience=window.SageMiniExperience;
const timeline=new Experience.Timeline({seek:params=>api('timelineSeek',Object.assign({session},params),'POST'),changed:()=>updateExperienceTimeline()});
const qualityAdvisor={key:'',reason:'warming-up',recommendation:null,samples:0,applied:0,
  appliedAt(){this.recommendation=null;this.applied++;}};
let runtimeRateRequestId=Date.now(),runtimeRateUnconfirmedOwner='',bufferReportId=Date.now(),bufferReportAt=-Infinity,bufferReportBusy=false;
let lastPresentedProducer='',lastPresentedTimeMs=null,presentedFrameSerial=0;
let qualityBusy=false,qualityLastResult='';
const framePreviews=new Experience.FramePreviews(url=>URL.revokeObjectURL(url));
const sourcePreviews=Experience.SourcePreviews?new Experience.SourcePreviews({fetch:fetchSourcePreview,
  offer:(...args)=>framePreviews.offer(...args),revoke:url=>URL.revokeObjectURL(url),changed:()=>updateExperienceTimeline()}):
  Object.freeze({begin:()=>{},request:async()=>false,snapshot:()=>({state:'unavailable',queued:0})});
let previewBusy=false,previewSerial=0,previewFailedSource='';
let markerKey='',markerBusy=false,markerRows=[],markerStatus='Markers unavailable';
let dvdCompanionState={state:'off',controls:false};
let dvdCompanionBusy=false,dvdCompanionMessage='';
let unsupportedGfxCount=0,lastUnsupportedGfx=-1;
const repeatConsumed=new WeakMap(),surfaces=new Map([[0,mainSurface]]),images=new Map(),logs=[],uiSizeHistory=new Set();
const COLORKEY=[8,0,16];
function loadSettings(){try{
  const saved=JSON.parse(localStorage.getItem(SETTINGS_KEY)||'{}');
  // One-time migration of the old implicit Source default for the requested
  // edge-to-edge policy. Future explicit Fit choices are never overwritten.
  if(saved.displayPolicyVersion!==2 && (!saved.videoFit||saved.videoFit==='source'))saved.videoFit='cover';
  const normalized=Core.normalizeSettings(saved);
  try{localStorage.setItem(SETTINGS_KEY,JSON.stringify(normalized));}catch(_){}
  return normalized;
}catch(_){return Core.normalizeSettings({});}}
function log(message){logs.push({at:new Date().toISOString(),message:String(message)});if(logs.length>200)logs.shift();}
function setError(e){lastError=e&&e.message?e.message:String(e);log(lastError);}
function saveSettings(){settings=Core.normalizeSettings(settings);try{localStorage.setItem(SETTINGS_KEY,JSON.stringify(settings));}catch(_){}applySettings();}
async function requestJson(path,action,params,method,timeoutMs,parentSignal){
  const inputStarted=path==='api/miniclient'&&timedInputActions.has(action)?performance.now():null;
  let inputSucceeded=false;
  const u=new URL(path,location.href),body=new URLSearchParams();u.searchParams.set('action',action);
  Object.keys(params||{}).forEach(k=>{if(params[k]!==undefined&&params[k]!==null)body.set(k,String(params[k]));});
  const options={method:method||'GET',cache:'no-store'},controller=new AbortController();options.signal=controller.signal;
  const abort=()=>controller.abort();
  if(parentSignal){parentSignal.addEventListener('abort',abort,{once:true});if(parentSignal.aborted)abort();}
  if(options.method==='GET')body.forEach((v,k)=>u.searchParams.set(k,v));else{options.body=body;options.headers={'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'};}
  const timer=setTimeout(()=>controller.abort(),timeoutMs||15000);
  try{const r=await fetch(u.href,options);const t=await r.text();let j={};try{j=t?JSON.parse(t):{};}catch(_){j={error:t.slice(0,500)};}if(!r.ok){const error=new Error(j.error||('HTTP '+r.status));error.httpStatus=r.status;throw error;}inputSucceeded=j.ok!==false;return j;}
  finally{clearTimeout(timer);if(parentSignal)parentSignal.removeEventListener('abort',abort);if(inputStarted!==null){renderPerformance.inputActionLast=action;if(inputSucceeded){const ms=performance.now()-inputStarted;renderPerformance.inputAcks++;renderPerformance.inputAckMsLast=ms;renderPerformance.inputAckMsMax=Math.max(renderPerformance.inputAckMsMax,ms);}else renderPerformance.inputFailures++;}}
}
function api(action,params,method){return requestJson('api/miniclient',action,params,method,['recover','seek','start','fallback','streamSettings','quality','qualityPrepare'].includes(action)?60000:15000);}
function hlsApi(action,params){return requestJson('api/hls',action,params,'GET',5000);}
function loadHlsJs(){
  if(window.Hls)return Promise.resolve(window.Hls);if(hlsScriptPromise)return hlsScriptPromise;
  hlsScriptPromise=new Promise((resolve,reject)=>{
    const script=document.createElement('script');script.src='vendor/hlsjs/hls.min.js';
    const timer=setTimeout(()=>{script.remove();hlsScriptPromise=null;reject(new Error('Timed out loading local hls.js vendor asset'));},15000);
    script.onload=()=>{clearTimeout(timer);if(window.Hls)resolve(window.Hls);else{hlsScriptPromise=null;reject(new Error('hls.js is unavailable'));}};
    script.onerror=()=>{clearTimeout(timer);hlsScriptPromise=null;reject(new Error('Could not load hls.js vendor asset'));};document.head.appendChild(script);
  });return hlsScriptPromise;
}
function loadMpegtsJs(){
  if(window.mpegts)return Promise.resolve(window.mpegts);if(mpegtsScriptPromise)return mpegtsScriptPromise;
  mpegtsScriptPromise=new Promise((resolve,reject)=>{
    const script=document.createElement('script');script.src='vendor/mpegts-1.8.0/mpegts.min.js';
    const timer=setTimeout(()=>{script.remove();mpegtsScriptPromise=null;reject(new Error('Timed out loading cached mpegts.js 1.8.0; prefetch or pre-seed the vendor asset'));},60000);
    script.onload=()=>{clearTimeout(timer);if(window.mpegts)resolve(window.mpegts);else{mpegtsScriptPromise=null;reject(new Error('mpegts.js did not load'));}};
    script.onerror=()=>{clearTimeout(timer);mpegtsScriptPromise=null;reject(new Error('Unable to load the mpegts.js vendor asset'));};document.head.appendChild(script);
  });return mpegtsScriptPromise;
}
const captions=new window.SageMiniCaptions({
  Decoder:window.SageAtscCaptions,timeMs:()=>Math.round((Number(video.currentTime)||0)*1000),
  sourceTimeMs:()=>playback?playback.absoluteTime():0,
  fetch:params=>requestJson('api/captions','read',params,'GET',5000),
  subtitleFetch:params=>requestJson('api/subtitles','read',params,'GET',5000),
  render:renderLocalCaptions,renderBitmap:renderDvbBitmap,clearBitmap:clearDvbBitmap,error:s=>log('Caption side channel: '+s)
});
const OrdinarySubtitleController=window.SageMiniSubtitles||class{constructor(){this.mode='off';}start(){}stop(){}snapshot(){return{mode:'off',error:'ordinary subtitle module unavailable'};}};
const ordinarySubtitles=new OrdinarySubtitleController({
  timeMs:()=>playback?playback.absoluteTime():Math.round((Number(video.currentTime)||0)*1000),
  fetch:params=>requestJson('api/subtitles','read',params,'GET',5000),renderText:renderFileSubtitles,renderBitmap:renderFileSubtitleBitmap,clearBitmap:clearFileSubtitleBitmap,error:s=>log('Ordinary subtitles: '+s)
});
const DvdSpuController=window.SageMiniDvdSpu||class{start(){}stop(){}snapshot(){return{active:false,error:'DVD SPU module unavailable'};}};
const dvdSpu=new DvdSpuController({timeMs:()=>Math.round((Number(video.currentTime)||0)*1000),fetch:params=>requestJson('api/subtitles','read',params,'GET',5000),clear:()=>dvdSpuCtx.clearRect(0,0,dvdSpuCanvas.width,dvdSpuCanvas.height),render:(cue,rgba)=>renderDvdSpu(cue,rgba)});


function hideDvdStill(){dvdStill.hidden=true;dvdStillCtx.clearRect(0,0,dvdStill.width,dvdStill.height);}
function resetDvdFrameCache(clearVisible){dvdFrameSamplerSerial++;dvdFrameGeneration=0;dvdFrozenGeneration=0;dvdFrameCacheValid=false;dvdFrameCache.width=dvdFrameCache.height=1;if(clearVisible)hideDvdStill();}
function cacheDvdVideoFrame(generation,releasePriorStill){
  if(!playback||!playback.dvd||Number(playback.dvdGeneration)!==Number(generation)||!(video.videoWidth>0&&video.videoHeight>0)||video.readyState<2)return false;
  if(releasePriorStill&&dvdFrozenGeneration===Number(generation))return false;
  const w=Math.max(1,video.videoWidth|0),h=Math.max(1,video.videoHeight|0);
  if(dvdFrameCache.width!==w||dvdFrameCache.height!==h){dvdFrameCache.width=w;dvdFrameCache.height=h;}
  try{
    dvdFrameCacheCtx.drawImage(video,0,0,w,h);dvdFrameGeneration=Number(generation)||0;dvdFrameCacheValid=true;dvdFrameCaptures++;
    // Keep the previous menu background over a replacement cell until a real
    // decoded frame from the new generation has actually been copied. Merely
    // receiving loadeddata/playing is too early for one-picture DVD menu cells.
    if(releasePriorStill&&!dvdStill.hidden)hideDvdStill();
    return true;
  }catch(e){log('DVD frame cache: '+e);return false;}
}
function beginDvdFrameCache(generation){
  const gen=Number(generation)||0,serial=++dvdFrameSamplerSerial;dvdFrameGeneration=gen;dvdFrozenGeneration=0;dvdFrameCacheValid=false;dvdFrameCache.width=dvdFrameCache.height=1;
  const sample=()=>{
    if(serial!==dvdFrameSamplerSerial||!playback||!playback.dvd||Number(playback.dvdGeneration)!==gen)return;
    cacheDvdVideoFrame(gen,true);
    if(typeof video.requestVideoFrameCallback==='function')setTimeout(()=>{if(serial===dvdFrameSamplerSerial)video.requestVideoFrameCallback(sample);},180);
    else setTimeout(sample,180);
  };
  if(typeof video.requestVideoFrameCallback==='function')video.requestVideoFrameCallback(sample);else setTimeout(sample,25);
}
function promoteDvdStill(generation){
  const gen=Number(generation)||Number(playback&&playback.dvdGeneration)||0;
  // Stop the old-generation sampler before the player tears down this tiny HLS
  // cell. Otherwise an ended/black frame can overwrite the authored menu frame.
  dvdFrameSamplerSerial++;
  if((!dvdFrameCacheValid||dvdFrameGeneration!==gen)&&playback&&playback.dvd&&Number(playback.dvdGeneration)===gen)cacheDvdVideoFrame(gen,false);
  dvdFrozenGeneration=gen;
  if(!dvdFrameCacheValid||dvdFrameGeneration!==gen){dvdStillMisses++;log('DVD still promotion missed decoded frame for generation '+gen+'; retaining prior menu frame');return !dvdStill.hidden;}
  const W=Math.max(1,videoBounds.clientWidth||dvdFrameCache.width||720),H=Math.max(1,videoBounds.clientHeight||dvdFrameCache.height||480);
  dvdStill.width=W;dvdStill.height=H;dvdStillCtx.fillStyle='#000';dvdStillCtx.fillRect(0,0,W,H);
  const r=Core.mediaContentRect(W,H,dvdFrameCache.width,dvdFrameCache.height,videoAspect);
  try{dvdStillCtx.drawImage(dvdFrameCache,r.left,r.top,r.width,r.height);dvdStill.hidden=false;dvdStillPromotions++;return true;}catch(e){dvdStillMisses++;log('DVD still promotion: '+e);return false;}
}
video.addEventListener('loadeddata',()=>{if(playback&&playback.dvd)cacheDvdVideoFrame(playback.dvdGeneration,true);});
video.addEventListener('playing',()=>{if(playback&&playback.dvd)cacheDvdVideoFrame(playback.dvdGeneration,true);});
video.addEventListener('timeupdate',()=>{if(playback&&playback.dvd)cacheDvdVideoFrame(playback.dvdGeneration,true);});
video.addEventListener('ended',()=>{if(playback&&playback.dvd)cacheDvdVideoFrame(playback.dvdGeneration,false);});

function renderDvdSpu(cue,rgba){const c=cue&&cue.canvas||{},r=cue&&cue.rect||[],cw=Number(c.width)|0,ch=Number(c.height)|0,w=Number(r[2])|0,h=Number(r[3])|0;if(cw<1||ch<1||w<1||h<1||rgba.length!==w*h*4)return;if(dvdSpuCanvas.width!==cw||dvdSpuCanvas.height!==ch){dvdSpuCanvas.width=cw;dvdSpuCanvas.height=ch;}try{dvdSpuCtx.putImageData(new ImageData(new Uint8ClampedArray(rgba),w,h),Number(r[0])|0,Number(r[1])|0);}catch(e){setError(e);}syncDvbCanvasLayout();}
function clearDvbBitmap(){dvbCtx.clearRect(0,0,dvbCanvas.width,dvbCanvas.height);}
function clearFileSubtitleBitmap(){fileSubCtx.clearRect(0,0,fileSubCanvas.width,fileSubCanvas.height);}
function renderFileSubtitleBitmap(cue,rgba){const canvas=cue&&cue.canvas||{},rect=cue&&cue.rect||[],cw=Number(canvas.width)|0,ch=Number(canvas.height)|0,w=Number(rect[2])|0,h=Number(rect[3])|0;if(cw<1||ch<1||w<1||h<1||rgba.length!==w*h*4)return;if(fileSubCanvas.width!==cw||fileSubCanvas.height!==ch){fileSubCanvas.width=cw;fileSubCanvas.height=ch;}try{fileSubCtx.putImageData(new ImageData(new Uint8ClampedArray(rgba),w,h),Number(rect[0])|0,Number(rect[1])|0);}catch(e){setError(e);}syncDvbCanvasLayout();}
function renderFileSubtitles(cues){const root=$('fileSubtitles');root.replaceChildren();for(const cue of cues||[]){const d=document.createElement('div');d.className='file-subtitle-cue';d.textContent=cue.text;const line=Number.isFinite(cue.line)&&cue.line>=0?Math.max(0,Math.min(100,cue.line)):94,pos=Number.isFinite(cue.position)?Math.max(0,Math.min(100,cue.position)):50;d.style.left=pos+'%';d.style.top=line+'%';d.style.textAlign=['start','left'].includes(cue.align)?'left':['end','right'].includes(cue.align)?'right':'center';root.appendChild(d);}}
function renderDvbBitmap(cue,rgba){
  const canvas=cue&&cue.canvas||{},rect=cue&&cue.rect||[];const cw=Number(canvas.width)|0,ch=Number(canvas.height)|0,w=Number(rect[2])|0,h=Number(rect[3])|0;
  if(cw<1||ch<1||w<1||h<1||rgba.length!==w*h*4)return;
  if(dvbCanvas.width!==cw||dvbCanvas.height!==ch){dvbCanvas.width=cw;dvbCanvas.height=ch;}
  try{dvbCtx.putImageData(new ImageData(new Uint8ClampedArray(rgba),w,h),Number(rect[0])|0,Number(rect[1])|0);}catch(e){setError(e);}
  syncDvbCanvasLayout();
}
function syncDvbCanvasLayout(){
  const W=videoBounds.clientWidth||0,H=videoBounds.clientHeight||0;if(!(W>0&&H>0))return;
  const fallbackW=dvbCanvas.width||W,fallbackH=dvbCanvas.height||H,r=Core.mediaContentRect(W,H,video.videoWidth||fallbackW,video.videoHeight||fallbackH,videoAspect);
  for(const c of [dvbCanvas,fileSubCanvas,dvdSpuCanvas]){c.style.left=r.left+'px';c.style.top=r.top+'px';c.style.width=r.width+'px';c.style.height=r.height+'px';}const fs=$('fileSubtitles');fs.style.left=r.left+'px';fs.style.top=r.top+'px';fs.style.width=r.width+'px';fs.style.height=r.height+'px';fs.style.right='auto';fs.style.bottom='auto';
}
function renderLocalCaptions(text,service,meta){
  const root=$('localCaptions');root.replaceChildren();if(!text)return;
  if(meta&&meta.type==='708'&&Array.isArray(meta.windows)&&meta.windows.length){
    for(const w of meta.windows){const d=document.createElement('div');d.className='caption-708-window';d.textContent=w.text;
      const rows=Math.max(1,Math.min(15,Number(w.rows)||1)),columns=Math.max(1,Math.min(42,Number(w.columns)||32));
      d.style.width=columns+'ch';d.style.height=(rows*1.15)+'em';if(Array.isArray(w.lines))d.textContent=w.lines.join('\n');
      d.style.left=Math.max(0,Math.min(100,Number(w.left)||0))+'%';d.style.top=Math.max(0,Math.min(100,Number(w.top)||0))+'%';
      d.style.color=w.fg||'#fff';d.style.background=w.bg||'rgba(0,0,0,.8)';if(w.italic)d.style.fontStyle='italic';if(w.underline)d.style.textDecoration='underline';
      const anchor=Number(w.anchorId)||0;d.style.transform='translate('+[0,-50,-100][anchor%3]+'%,'+[0,-50,-100][Math.floor(anchor/3)%3]+'%)';root.appendChild(d);
    }
  }else{const d=document.createElement('div');d.className='caption-608';d.textContent=text;
    if(meta&&meta.type==='608'){
      d.classList.add('caption-cea-grid');
      if(Array.isArray(meta.lines))d.textContent=meta.lines.join('\n');
      if(meta.mode==='rollup')d.style.height=(Math.max(2,Math.min(4,Number(meta.rows)||2))*1.2)+'em';
    }
    root.appendChild(d);}
}
const playback=new window.SageMiniPlayback({
  presentationEnded:()=>{lastCaptionEvent=null;captionSelectionSerial++;captionSelectionSignature='';effectiveCaptionSelection=null;captions.stop();ordinarySubtitles.stop();},
  dvdMenu:()=>dvdMenuState===true&&Date.now()-dvdMenuStateAt<1500,
  video,settings:()=>settings,status:id=>hlsApi('status',{session:id}),loadHls:loadHlsJs,loadMpegts:loadMpegtsJs,
  fallback:params=>api('fallback',Object.assign({session},params),'POST'),
  nativePreferred:!!video.canPlayType('application/vnd.apple.mpegurl')&&/iP(hone|ad|od)|Macintosh/.test(navigator.userAgent)&&/Safari/.test(navigator.userAgent)&&!/Chrome|Chromium|Edg/.test(navigator.userAgent),
  resolveUrl:path=>{const u=new URL(path,location.href);if(u.origin!==location.origin)throw new Error('Cross-origin HLS URL refused');return u.href;},
  recover:params=>api('recover',Object.assign({session},params),'POST'),message,error:setError,
  mediaUpdate:()=>{if(session)api('mediaUpdate',{session},'POST').catch(setError);}
});
function makeCanvas(w,h){const c=document.createElement('canvas');c.width=Math.max(1,w|0);c.height=Math.max(1,h|0);return c;}
function rememberUiSize(w,h){
  const key=w+'x'+h;uiSizeHistory.delete(key);uiSizeHistory.add(key);
  if(uiSizeHistory.size>16)uiSizeHistory.delete(uiSizeHistory.values().next().value);
}
function message(s){msgEl.textContent=s||'';}
function setStatus(s){statusEl.textContent=s||'';}
function int32(b,o){return ((b[o]&255)<<24)|((b[o+1]&255)<<16)|((b[o+2]&255)<<8)|(b[o+3]&255);}
function u32(b,o){return int32(b,o)>>>0;}
function base64Bytes(s){const raw=atob(s||'');const b=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)b[i]=raw.charCodeAt(i);return b;}
function argb(v){v=v>>>0;return {a:(v>>>24)&255,r:(v>>>16)&255,g:(v>>>8)&255,b:v&255};}
function cssArgb(v){const c=argb(v);return `rgba(${c.r},${c.g},${c.b},${(c.a/255).toFixed(5)})`;}
function isColorKey(v){const c=argb(v);return c.r===COLORKEY[0]&&c.g===COLORKEY[1]&&c.b===COLORKEY[2];}
function targetCanvas(){return surfaces.get(currentTarget)||mainSurface;}
function targetCtx(){return targetCanvas().getContext('2d',{alpha:true});}
function argOffset(n){return 4+n;}
function getI(b,n){return int32(b,argOffset(n));}
function currentScalePoint(ev){return Core.canvasPoint(ev.clientX,ev.clientY,visible.getBoundingClientRect(),uiW,uiH);}

function layoutStage(){
  const sr=stage.getBoundingClientRect();
  displayRect=Core.stageRect(sr.width,sr.height,uiW,uiH,settings.uiResolution==='window'&&!document.body.classList.contains('mc-portrait-dock')&&!new URLSearchParams(location.search).has('ui'));
  const d=displayRect;
  visible.style.left=d.left+'px';visible.style.top=d.top+'px';
  visible.style.width=d.width+'px';visible.style.height=d.height+'px';
  applyVideoBounds();
}
function resetRenderer(w,h){
  rendererGeneration++;
  uiW=Math.max(1,w|0);uiH=Math.max(1,h|0);
  visible.width=uiW;visible.height=uiH;document.documentElement.style.setProperty('--ui-aspect',String(uiW/uiH));
  mainSurface=makeCanvas(uiW,uiH);surfaces.clear();surfaces.set(0,mainSurface);images.clear();currentTarget=0;
  uiSizeHistory.clear();rememberUiSize(uiW,uiH);
  visibleCtx.clearRect(0,0,uiW,uiH);currentVideoBounds=[0,0,uiW,uiH];nativeVideoBounds=currentVideoBounds.slice();nativeVideoSource=null;videoBoundsOrigin='initial';videoBoundsTrusted=false;lastTrustedVideoBounds=null;videoPresentationSuspended=false;frame=0;gfxCount=0;imageCount=0;layoutStage();
}
function startFrame(){currentTarget=0;frameHadClearRect=false;const c=mainSurface.getContext('2d',{alpha:true});c.save();c.setTransform(1,0,0,1,0,0);c.globalCompositeOperation='copy';c.clearRect(0,0,uiW,uiH);c.restore();}
function flip(){if(playback.id&&!frameHadClearRect)videoPresentationSuspended=true;visibleCtx.save();visibleCtx.setTransform(1,0,0,1,0,0);visibleCtx.globalCompositeOperation='copy';visibleCtx.clearRect(0,0,uiW,uiH);visibleCtx.drawImage(mainSurface,0,0);visibleCtx.restore();frame++;if(frame===1&&!playback.id)message('');}
function clip(ctx,x,y,w,h,fn){ctx.save();if(w>0&&h>0){ctx.beginPath();ctx.rect(x,y,w,h);ctx.clip();}try{fn();}finally{ctx.restore();}}
function fillStyle(ctx,x,y,w,h,tl,tr,br,bl){
  if(tl===tr&&tl===br&&tl===bl)return cssArgb(tl);
  let g;
  if(tl===tr&&bl===br){g=ctx.createLinearGradient(x,y,x,y+h);g.addColorStop(0,cssArgb(tl));g.addColorStop(1,cssArgb(bl));return g;}
  if(tl===bl&&tr===br){g=ctx.createLinearGradient(x,y,x+w,y);g.addColorStop(0,cssArgb(tl));g.addColorStop(1,cssArgb(tr));return g;}
  g=ctx.createLinearGradient(x,y,x+w,y+h);g.addColorStop(0,cssArgb(tl));g.addColorStop(.5,cssArgb(tr));g.addColorStop(1,cssArgb(br));return g;
}
function roundedPath(ctx,x,y,w,h,r){r=Math.max(0,Math.min(Math.abs(w)/2,Math.abs(h)/2,r||0));ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);ctx.arcTo(x,y,x+w,y,r);ctx.closePath();}
function clearOrFill(ctx,x,y,w,h,color){if(clearVideoMask(ctx,[x,y,w,h],color,true))return;if(isColorKey(color)||((color>>>24)&255)===0){ctx.clearRect(x,y,w,h);}else{ctx.fillStyle=cssArgb(color);ctx.fillRect(x,y,w,h);}}

async function decodeCompressed(bytes){
  const started=performance.now();
  try{
  const blob=new Blob([bytes]);
  if('createImageBitmap' in window){try{return await createImageBitmap(blob);}catch(_){} }
  return await new Promise((resolve,reject)=>{const url=URL.createObjectURL(blob),im=new Image();im.onload=()=>{URL.revokeObjectURL(url);resolve(im);};im.onerror=()=>{URL.revokeObjectURL(url);reject(new Error('Could not decode SageTV image'));};im.src=url;});
  }finally{const ms=performance.now()-started;renderPerformance.decodedImages++;renderPerformance.imageDecodeMsLast=ms;renderPerformance.imageDecodeMsMax=Math.max(renderPerformance.imageDecodeMsMax,ms);}
}
function imageCanvas(handle){const x=images.get(handle)||surfaces.get(handle);if(!x)return null;return x.canvas||x;}
function allocateImage(handle,w,h,format){
  const c=makeCanvas(w,h),entry={canvas:c,width:w,height:h,format:format||0};
  if(format===256){try{entry.unified=new Core.UnifiedYuvImage(w,h);}catch(e){log('Unified YUV allocation rejected: '+e);return null;}}
  images.set(handle,entry);imageCount++;return c;
}
function optionalI(b,n,fallback){return b.length>=argOffset(n+4)?getI(b,n):fallback;}
function noteUnsupportedGfx(cmd){unsupportedGfxCount++;lastUnsupportedGfx=cmd;log('GFX opcode '+cmd+' was received but is negotiated off / unsupported');}

async function gfx(ev){
  const myRenderer=rendererGeneration;
  const b=base64Bytes(ev.payload);const cmd=ev.cmd|0;gfxCount++;lastEventAt=Date.now();
  switch(cmd){
    case 1: resetRenderer(uiW,uiH); message('SageTV graphics initialized…'); break;
    case 2: message('SageTV graphics deinitialized'); break;
    case 16:{const c=targetCtx(),x=getI(b,0),y=getI(b,4),w=getI(b,8),h=getI(b,12),t=Math.max(1,getI(b,16));c.save();c.lineWidth=t;c.strokeStyle=fillStyle(c,x,y,w,h,getI(b,20),getI(b,24),getI(b,28),getI(b,32));c.strokeRect(x+t/2,y+t/2,Math.max(0,w-t),Math.max(0,h-t));c.restore();break;}
    case 17:{const c=targetCtx(),x=getI(b,0),y=getI(b,4),w=getI(b,8),h=getI(b,12),tl=getI(b,16);if(tl===getI(b,20)&&tl===getI(b,24)&&tl===getI(b,28)&&clearVideoMask(c,[x,y,w,h],tl,false))break;if(isColorKey(tl)&&tl===getI(b,20)&&tl===getI(b,24)&&tl===getI(b,28))c.clearRect(x,y,w,h);else{c.save();c.fillStyle=fillStyle(c,x,y,w,h,tl,getI(b,20),getI(b,24),getI(b,28));c.fillRect(x,y,w,h);c.restore();}break;}
    case 18:{if(currentTarget===0)frameHadClearRect=true;const c=targetCtx(),x=getI(b,0),y=getI(b,4),w=getI(b,8),h=getI(b,12);clearOrFill(c,x,y,w,h,getI(b,16));break;}
    case 19:{const c=targetCtx(),x=getI(b,0),y=getI(b,4),w=getI(b,8),h=getI(b,12),t=Math.max(1,getI(b,16));clip(c,getI(b,36),getI(b,40),getI(b,44),getI(b,48),()=>{c.beginPath();c.ellipse(x+w/2,y+h/2,Math.abs(w/2),Math.abs(h/2),0,0,Math.PI*2);c.lineWidth=t;c.strokeStyle=fillStyle(c,x,y,w,h,getI(b,20),getI(b,24),getI(b,28),getI(b,32));c.stroke();});break;}
    case 20:{const c=targetCtx(),x=getI(b,0),y=getI(b,4),w=getI(b,8),h=getI(b,12);clip(c,getI(b,32),getI(b,36),getI(b,40),getI(b,44),()=>{c.beginPath();c.ellipse(x+w/2,y+h/2,Math.abs(w/2),Math.abs(h/2),0,0,Math.PI*2);c.fillStyle=fillStyle(c,x,y,w,h,getI(b,16),getI(b,20),getI(b,24),getI(b,28));c.fill();});break;}
    case 21:{const c=targetCtx(),x=getI(b,0),y=getI(b,4),w=getI(b,8),h=getI(b,12),t=Math.max(1,getI(b,16)),r=Math.max(0,getI(b,20));clip(c,getI(b,40),getI(b,44),getI(b,48),getI(b,52),()=>{roundedPath(c,x,y,w,h,r);c.lineWidth=t;c.strokeStyle=fillStyle(c,x,y,w,h,getI(b,24),getI(b,28),getI(b,32),getI(b,36));c.stroke();});break;}
    case 22:{const c=targetCtx(),x=getI(b,0),y=getI(b,4),w=getI(b,8),h=getI(b,12),r=Math.max(0,getI(b,16));clip(c,getI(b,36),getI(b,40),getI(b,44),getI(b,48),()=>{roundedPath(c,x,y,w,h,r);c.fillStyle=fillStyle(c,x,y,w,h,getI(b,20),getI(b,24),getI(b,28),getI(b,32));c.fill();});break;}
    case 23: break; // GFX_TEXTMODE is disabled; SageTV rasterizes text into images.
    case 24:{
      const c=targetCtx(),x=getI(b,0),y=getI(b,4),w=getI(b,8),h=getI(b,12),handle=getI(b,16),sx=getI(b,20),sy=getI(b,24),sw=getI(b,28),sh=getI(b,32),blend=getI(b,36)>>>0,src=imageCanvas(handle);if(!src)break;
      // Match the Vibe Android MiniClient renderer exactly here. SageTV can send
      // negative destination dimensions as rendering flags. Android takes abs()
      // for geometry and does NOT mirror the texture; a negative height selects
      // the unblended/copy path. Treating the signs as Canvas scale flips makes
      // rasterized SageMC text appear backwards and framebuffer compositions
      // upside-down. Browser canvases already use SageTV's top-left coordinates,
      // so they also do not need the OpenGL framebuffer Y inversion used by GDX.
      // A retained full-screen target may still be copied with its original
      // allocation bounds after orientation. Its pixels already use the new
      // screen coordinates; map only this exact whole-surface copy to the new
      // screen. Ordinary textures, partial copies and preview surfaces retain
      // their authored coordinates and negative-height compositing behavior.
      const entry=images.get(handle),wholeResizedSurface=currentTarget===0&&entry&&entry.resizedForUi&&
        x===0&&y===0&&sx===0&&sy===0&&Math.abs(w)===entry.nativeWidth&&Math.abs(h)===entry.nativeHeight&&sw===entry.nativeWidth&&sh===entry.nativeHeight;
      const dw=wholeResizedSurface?uiW:Math.abs(w),dh=wholeResizedSurface?uiH:Math.abs(h),bc=argb(blend);if(!(dw>0&&dh>0&&sw!==0&&sh!==0))break;
      c.save();
      try{
        c.globalAlpha=bc.a/255;
        if(h<0){
          // Android uses GL_ONE/GL_ZERO when height is negative. Constrain Canvas
          // 'copy' to the destination rectangle so pixels elsewhere are retained.
          c.beginPath();c.rect(x,y,dw,dh);c.clip();c.globalCompositeOperation='copy';
        }else c.globalCompositeOperation='source-over';
        c.drawImage(src,sx,sy,wholeResizedSurface?src.width:sw,wholeResizedSurface?src.height:sh,x,y,dw,dh);
      }catch(_){}
      c.restore();break;}
    case 25:{const c=targetCtx(),x1=getI(b,0),y1=getI(b,4),x2=getI(b,8),y2=getI(b,12),a=getI(b,16),z=getI(b,20);c.save();if(a===z)c.strokeStyle=cssArgb(a);else{const g=c.createLinearGradient(x1,y1,x2,y2);g.addColorStop(0,cssArgb(a));g.addColorStop(1,cssArgb(z));c.strokeStyle=g;}c.beginPath();c.moveTo(x1,y1);c.lineTo(x2,y2);c.stroke();c.restore();break;}
    case 26:{const h=ev.assignedHandle|0,format=optionalI(b,8,0);if(h)allocateImage(h,getI(b,0),getI(b,4),format);else if(format===256)noteUnsupportedGfx(cmd);break;}
    case 27:{const h=getI(b,0);images.delete(h);if(h!==0)surfaces.delete(h);break;}
    case 28: case 29: case 36: break;
    case 30: flip();break;
    case 31: startFrame();break;
    case 32:{
      const handle=getI(b,0),line=getI(b,4),len=getI(b,8),entry=images.get(handle);if(!entry||!entry.canvas)break;let p=argOffset(12);if(entry.unified){const count=Math.min(len,Math.max(0,b.length-p)),row=entry.unified.loadLine(line,b,p,count);if(row>=0&&entry.unified.ySeen[row]&&entry.unified.uvSeen[row])entry.canvas.getContext('2d').putImageData(new ImageData(entry.unified.rowRgba(row),entry.width,1),0,row);break;}if(line<0||line>=entry.canvas.height)break;const px=Math.min(entry.canvas.width,Math.floor(len/4));const data=new Uint8ClampedArray(px*4);for(let i=0;i<px&&p+3<b.length;i++,p+=4){data[i*4+0]=b[p+1];data[i*4+1]=b[p+2];data[i*4+2]=b[p+3];data[i*4+3]=b[p];}entry.canvas.getContext('2d').putImageData(new ImageData(data,px,1),0,line);break;}
    case 33: break;
    case 34:{
      const original=getI(b,0),len=Math.min(getI(b,4),Math.max(0,b.length-argOffset(8))),handle=(ev.assignedHandle|0)||original;if(len<=0)break;const img=await decodeCompressed(b.slice(argOffset(8),argOffset(8)+len));if(myRenderer!==rendererGeneration){if(img.close)img.close();return;}const c=makeCanvas(img.width||1,img.height||1);c.getContext('2d').drawImage(img,0,0);if(img.close)try{img.close();}catch(_){}images.set(handle,{canvas:c,width:c.width,height:c.height});imageCount++;break;}
    case 35:{
      const srcHandle=getI(b,0),destArg=getI(b,4),dw=getI(b,8),dh=getI(b,12),src=imageCanvas(srcHandle),handle=(ev.assignedHandle|0)||destArg;if(!src||!handle)break;const c=makeCanvas(dw,dh);c.getContext('2d').drawImage(src,0,0,src.width,src.height,0,0,dw,dh);images.set(handle,{canvas:c,width:dw,height:dh});break;}
    case 37:{
      const h=ev.assignedHandle|0,w=getI(b,0),hh=getI(b,4);
      if(h){
        // Cached/queued UI composition surfaces can arrive after several
        // resizes. Their handle still represents the screen, not a portrait-
        // sized clipping box for a landscape popup. Only known screen sizes
        // qualify; ordinary textures and small preview targets stay exact.
        const screenSurface=uiSizeHistory.has(w+'x'+hh),cw=screenSurface?uiW:w,ch=screenSurface?uiH:hh;
        const c=makeCanvas(cw,ch);surfaces.set(h,c);
        images.set(h,{canvas:c,width:cw,height:ch,surface:true,screenSurface,nativeWidth:w,nativeHeight:hh,resizedForUi:screenSurface&&(w!==cw||hh!==ch)});
      }break;}
    case 38:{const h=getI(b,0);currentTarget=surfaces.has(h)?h:0;break;}
    case 40: noteUnsupportedGfx(cmd);break; // diffuse textures are not advertised
    case 41: case 42: case 43: noteUnsupportedGfx(cmd);break; // transforms/batches are not advertised
    case 44: noteUnsupportedGfx(cmd);break; // offline image cache is not advertised
    case 45:{const h=getI(b,0),w=getI(b,4),hh=getI(b,8),format=optionalI(b,12,0);if(format===256&&!settings.unifiedGraphics){noteUnsupportedGfx(cmd);break;}allocateImage(h,w,hh,format);break;}
    case 46:{const h=getI(b,0),w=getI(b,4),hh=getI(b,8),format=optionalI(b,12,0);if(format===256&&!settings.unifiedGraphics){noteUnsupportedGfx(cmd);break;}if(!images.has(h))allocateImage(h,w,hh,format);break;}
    case 130:{if(b.length>=44){const dx=getI(b,20),dy=getI(b,24),dw=getI(b,28),dh=getI(b,32);applyVideoBounds([dx,dy,dw,dh],true,'gfx-video-property');}break;}
    default: break;
  }
}


function clearVideoMask(ctx,rect,color,isClear){
  if(!settings.videoMaskAssist||!playback.id||currentTarget!==0)return false;
  const alpha=(color>>>24)&255;
  if(alpha>=13&&alpha<250&&!isColorKey(color))return false; // translucent OSD is not a video hole
  const screen=[0,0,uiW,uiH],hit=Core.videoMask(color,rect,screen,currentVideoBounds,lastTrustedVideoBounds,isClear,videoPresentationSuspended,videoBoundsTrusted);
  const matte=Core.fullscreenMatte(color,rect,screen,videoPresentation,videoPresentationSuspended);
  if(!hit&&!matte)return false;
  const mask=hit||Core.rectIntersection(rect,screen);
  // A clear is a paint operation, NOT SETVIDEORECT. Only the explicit color
  // key may establish a small legacy preview. Ordinary black clearing and
  // letterbox mattes never shrink or pan the fullscreen HTML video element.
  if(isColorKey(color))applyVideoBounds(mask,true,'color-key');
  else if(isClear&&mask[2]>=uiW*.85&&mask[3]>=uiH*.85&&videoBoundsOrigin==='color-key')
    applyVideoBounds(screen,true,'clear-fullscreen');
  videoPresentationSuspended=false;
  ctx.clearRect(mask[0]-1,mask[1]-1,mask[2]+2,mask[3]+2);return true;
}
function applyVideoBounds(rect,trusted,origin){
  if(Array.isArray(rect)&&rect.length>=4&&trusted!==undefined){
    const raw=rect.slice(0,4).map(Number),valid=raw.every(Number.isFinite)&&raw[2]>0&&raw[3]>0;
    videoBoundsTrusted=!!trusted&&valid;
    if(valid){nativeVideoBounds=raw;lastTrustedVideoBounds=raw.slice();videoBoundsOrigin=origin||'native';}
    else if(!playback.id)nativeVideoBounds=[0,0,uiW,uiH];
  }
  videoPresentation=Core.videoPresentation(nativeVideoBounds,uiW,uiH,settings.videoViewport);
  if(dvdFullscreenFromMenu(videoPresentation))videoPresentation={kind:'fullscreen',rect:[0,0,uiW,uiH],
    nativeRect:nativeVideoBounds.slice(),reason:'qualified-native-dvd-osd'};
  currentVideoBounds=videoPresentation.rect.slice();
  const sr=stage.getBoundingClientRect();
  videoLayerRect=Core.videoLayerRect(videoPresentation,displayRect,sr.width,sr.height,uiW,uiH);
  const d=videoLayerRect;
  videoBounds.hidden=!playback.id;
  videoBounds.style.left=d.left+'px';videoBounds.style.top=d.top+'px';
  videoBounds.style.width=d.width+'px';videoBounds.style.height=d.height+'px';
  videoBounds.dataset.presentation=videoPresentation.kind;
  video.style.objectFit=videoAspect==='fill'?'fill':(videoAspect==='cover'||videoAspect==='zoom')?'cover':'contain';
  video.style.objectPosition='50% 50%';video.style.width='100%';video.style.height='100%';
  if(videoAspect==='4x3'||videoAspect==='16x9'){
    const ratio=videoAspect==='4x3'?4/3:16/9,wantedWidth=Math.min(d.width,d.height*ratio);
    video.style.width=wantedWidth+'px';video.style.height=(wantedWidth/ratio)+'px';video.style.objectFit='fill';
  }
  syncDvbCanvasLayout();
}
function dvdFullscreenFromMenu(presentation){
  return Input.dvdFullscreenPresentation(presentation,{active:!!playback.id&&!stopped,dvd:playback.dvd,
    state:dvdMenuState,at:dvdMenuStateAt,now:Date.now(),menu:currentMenuHint});
}
function refreshDvdPresentation(){
  const wanted=dvdFullscreenFromMenu(Core.videoPresentation(nativeVideoBounds,uiW,uiH,settings.videoViewport));
  if(wanted!==(videoPresentation.reason==='qualified-native-dvd-osd'))applyVideoBounds();
}
function resetBrowserRate(){browserLocalRate=1;browserRateError='';try{video.playbackRate=1;}catch(_){} }
function updateBrowserRate(){
  const choice=$('browserPlaybackRate'),status=$('browserPlaybackRateStatus');
  if(!choice||!status)return; // an older cached shell must retain normal playback
  const actual=Number(video.playbackRate)||1;
  choice.disabled=!playback.id||!playback.attached||playback.dvd;
  choice.value=[.5,1,1.5,2].includes(actual)?String(actual):'1';
  status.textContent=browserRateError||(playback.dvd?'DVD speed is owned by native DVD controls.':!playback.id?'Start a recording to change browser speed.':'Browser '+actual+'× · this recording only; native STV controls are unchanged.');
}
function setBrowserRate(rate){
  if(![.5,1,1.5,2].includes(rate)||!playback.id||!playback.attached||playback.dvd){updateBrowserRate();return false;}
  browserRateError='';
  const previous=Number(video.playbackRate)||1;
  try{playback.control('rate',rate);if(Math.abs(Number(video.playbackRate)-rate)>.001)throw Error('Browser did not accept this playback speed.');browserLocalRate=rate;}
  catch(e){try{if(Number(video.playbackRate)!==previous)video.playbackRate=previous;}catch(_){}browserRateError='Playback speed unavailable: '+String(e.message||e).slice(0,160);}
  updateBrowserRate();return !browserRateError;
}
$('browserPlaybackRate')?.addEventListener('change',()=>setBrowserRate(Number($('browserPlaybackRate').value)));
function destroyVideo(){dvdKeys.cancel(false);resetBrowserRate();timeline.reset();presentedFrameSerial++;lastPresentedProducer='';lastPresentedTimeMs=null;lastCaptionEvent=null;captionSelectionSerial++;captionSelectionSignature='';effectiveCaptionSelection=null;captions.stop();ordinarySubtitles.stop();dvdSpu.stop();playback.stop();resetDvdFrameCache(true);videoBoundsTrusted=false;lastTrustedVideoBounds=null;videoPresentationSuspended=false;videoBounds.hidden=true;updateStats();}
function observePresentedFrames(id){
  const serial=++presentedFrameSerial;lastPresentedProducer='';lastPresentedTimeMs=null;
  if(typeof video.requestVideoFrameCallback!=='function')return;
  const frame=(now,metadata)=>{
    if(serial!==presentedFrameSerial||playback.id!==id||!playback.attached)return;
    const ms=Math.max(0,Math.round((playback.startSeconds+metadata.mediaTime)*1000));
    lastPresentedProducer=id;lastPresentedTimeMs=ms;timeline.presented(id,ms);
    cacheViewedFrame(ms);
    video.requestVideoFrameCallback(frame);
  };
  video.requestVideoFrameCallback(frame);
}
function startVideo(ev){
  dvdKeys.cancel(false);
  const nextMediaId=ev.mediaId==null?null:Number(ev.mediaId),knownIds=currentVideoMediaId!=null&&nextMediaId!=null;
  const sameRecording=knownIds?currentVideoMediaId===nextMediaId:!!playback.id&&!!(ev.seek||ev.recovery||ev.qualityHandoff);
  const keepBrowserRate=!ev.dvd&&sameRecording?browserLocalRate:1;
  if(keepBrowserRate===1)resetBrowserRate();
  currentVideoMediaId=nextMediaId;
  if(ev.qualityHandoff&&ev.previousHlsSession===playback.id){
    // State uploads are periodic. Join at the browser's freshest old-stream
    // position, not an older server report received during encoder warmup.
    const latest=playback.absoluteTime()/1000;
    ev=Object.assign({},ev,{resumeSeconds:Math.max(Number(ev.resumeSeconds)||0,latest-(Number(ev.startSeconds)||0),0)});
  }
  dvdMenuState=null;dvdMenuStateAt=0;if(calibrationOwner)closeCalibration(true);
  lastCaptionEvent=null;captionSelectionSerial++;captionSelectionSignature='';effectiveCaptionSelection=null;
  captionInventory=ev.streamSettings&&ev.streamSettings.source&&ev.streamSettings.source.tracks||[];
  captions.stop();ordinarySubtitles.stop();dvdSpu.stop();
  if(ev&&ev.dvd)beginDvdFrameCache(ev.dvdGeneration);else resetDvdFrameCache(true);
  ev.captionAuthority=CaptionAuthority.effective(captionAuthority,captionInventory);
  if(ev.captionAuthority&&ev.captionAuthority.mode==='stv'){ev.captionAuthority=Object.assign({},ev.captionAuthority,{stvStateSeen:sageTvCaptionStateSeen,stvState:sageTvCaptionState});}
  const started=playback.start(ev);applyVideoBounds();showStreamActual(ev.streamSettings);
  started.then(()=>{if(playback.id===ev.hlsSession){if(!playback.dvd)setBrowserRate(keepBrowserRate);updateBrowserRate();observePresentedFrames(ev.hlsSession);}}).catch(()=>{});
  return started.then(async()=>{if(playback.id===ev.hlsSession){lastCaptionEvent=ev;captions.start(ev);if(captionAuthority.mode==='stv'&&typeof captions.setSageTvState==='function')captions.setSageTvState(sageTvCaptionState,sageTvCaptionStateSeen);refreshStvCaptions().catch(setError);ordinarySubtitles.start(ev);dvdSpu.start(ev);await recoverInterruptedVideoTest(ev);}});
}
async function refreshStvCaptions(){
  const event=lastCaptionEvent,id=playback.id,native=session,generation=connectionGeneration;
  if(!event||event.dvd||event.hlsSession!==id||captionAuthority.mode!=='stv'||!sageTvCaptionStateSeen)return;
  let selected;
  if(sageTvCaptionState===0)selected={mode:'off',local:'off',label:'STV captions off'};
  else {
    selected=CaptionAuthority.effective(Object.assign({},captionAuthority,{mode:sageTvCaptionState===2?'cc2':'cc1'}),captionInventory);
    if(selected.missing&&!captionInventory.some(t=>CaptionAuthority.codec(t)))
      selected={mode:'cc1',local:'608',service:Math.max(1,Math.min(4,sageTvCaptionState)),label:'CEA-608 compatibility fallback (not discovered)'};
  }
  const track=selected.track||{},kind=selected.local||'off',pid=Number.isInteger(track.sourcePid)?track.sourcePid:-1;
  const page=kind==='teletext'?(Number(track.teletextPage)||888):kind==='dvb'?(Number.isInteger(track.compositionPageId)?track.compositionPageId:-1):-1;
  const signature=JSON.stringify([id,sageTvCaptionState,kind,pid,page,selected.service,track.language||'']);
  if(signature===captionSelectionSignature)return;
  captionSelectionSignature=signature;const serial=++captionSelectionSerial;captions.stop();
  let response;
  try{response=await api('captionSelection',{session:native,expectedHlsSession:id,kind,pid,page,language:track.language||''},'POST');}
  catch(error){if(serial===captionSelectionSerial)captionSelectionSignature='';throw error;}
  if(serial!==captionSelectionSerial||native!==session||generation!==connectionGeneration||id!==playback.id)return;
  if(response.ok===false){captionSelectionSignature='';throw new Error('Caption selection is unavailable for the current stream.');}
  effectiveCaptionSelection=selected;
  if(kind!=='off'){
    const requested=Object.assign({},event.streamSettings&&event.streamSettings.requested||{},
      {captions:kind,captionService:selected.service||1,captionPid:pid,captionCompositionPage:page});
    captions.start(Object.assign({},event,{captionAuthority:{mode:selected.mode},streamSettings:{requested}}));
  }
  updateCaptionAuthorityForm();
}
function absoluteMediaTime(){return playback.absoluteTime();}
async function browserState(){
  updateWatchLive();
  videoCast.update();
  if(!session||stopped||!playback.id||stateBusy)return;stateBusy=true;
  const id=session,serial=connectionGeneration;
  const stream=playback.id;
  try{
    const reply=await api('state',Object.assign({session:id,captionState:captionAuthority.mode==='stv'&&!captionWireStateSeen&&!playback.dvd,dvdMenuState:!!playback.dvd,presentedTimeMs:lastPresentedProducer===stream?lastPresentedTimeMs:undefined},playback.state()),'POST');
    if(serial===connectionGeneration&&id===session&&reply.captionDiagnostics){
      const safe=Support.redact(reply.captionDiagnostics),previous=lastServerConnectionStatus||{};
      lastServerConnectionStatus=Object.assign({},previous,{captionDiagnosticsAt:new Date().toISOString(),connection:Object.assign({},previous.connection||{},safe)});
    }
    if(serial===connectionGeneration&&id===session&&reply.playbackState){
      timeline.receive(reply.playbackState);
      if(reply.playbackState.qualityHandoff==='presented')qualityLastResult='Quality switch presented; saved quality unchanged.';
      else if(['timed-out','client-aborted'].includes(reply.playbackState.qualityHandoff))qualityLastResult='Quality switch cancelled; previous stream restored.';
    }
    if(serial===connectionGeneration&&id===session&&reply.dvdCompanion){dvdCompanionState=reply.dvdCompanion;updateDvdCompanion();}
    if(serial===connectionGeneration&&id===session&&stream===playback.id){const observed=Input.dvdMenuObservation(dvdMenuState,dvdMenuStateAt,reply.dvdMenu,Date.now());dvdMenuState=observed.value;dvdMenuStateAt=observed.at;refreshDvdPresentation();if(dvdMenuState!==false)dvdKeys.cancel(false);}
    if(serial===connectionGeneration&&id===session&&stream===playback.id&&!captionWireStateSeen&&Number.isInteger(reply.captionState)&&reply.captionState>=0&&reply.captionState<=4){
      sageTvCaptionStateSeen=true;sageTvCaptionState=reply.captionState;await refreshStvCaptions();
    }
  }
  catch(e){if(serial===connectionGeneration)setError(e);}finally{stateBusy=false;}
}
function nativeConnectionClosed(reason){
  if(stopped)return;
  failureSnapshot={at:new Date().toISOString(),reason:String(reason||'SageTV closed the native connection'),playback:playback.snapshot()};
  stopped=true;clearInterval(stateTimer);clearTimeout(guideTimer);gesture.cancel();touchGesture.cancel();keyRepeat.cancel();clearRepeats();
  if(eventController)eventController.abort();
  destroyVideo();setError(failureSnapshot.reason);setStatus('Disconnected · use Reconnect');
  message(lastError+' — Download diagnostics before using Reconnect.');
  document.body.classList.add('mc-connection-lost');
  $('recoveryReason').textContent=failureSnapshot.reason;
  $('connectionRecovery').hidden=false;$('retryConnectionBtn').disabled=false;
  $('reconnectBtn').disabled=false;$('connectionDiagnosticsBtn').hidden=false;
  if(settings.autoDiagnosticCapture)setTimeout(()=>automaticDiagnosticCapture('automatic-terminal-failure').catch(e=>log('Automatic diagnostic capture: '+(e.message||e))),0);
}
async function processEvent(ev){
  if(!ev)return;lastEventAt=Date.now();
  if(ev.type==='gfx'){await gfx(ev);return;}
  if(ev.type==='playbackState'){timeline.receive(ev.value);updateExperienceTimeline();return;}
  if(ev.type==='dvdCompanion'){dvdCompanionState=ev.value||{state:'unavailable',controls:false};updateDvdCompanion();return;}
  if(ev.type==='videoStart'){startVideo(ev).catch(setError);return;}
  if(ev.type==='videoStop'){destroyVideo();return;}
  if(ev.type==='videoBounds'){nativeVideoSource=ev.src||null;applyVideoBounds(ev.dst,true,'native');return;}
  if(ev.type==='dvd'){if(ev.action==='freeze')promoteDvdStill(ev.generation);return;}
  if(ev.type==='media'){
    playback.control(ev.action,ev.value);if(ev.action==='stop'){resetBrowserRate();videoBounds.hidden=true;updateBrowserRate();}
    browserState();return;
  }
  if(ev.type==='menuHint'){currentMenuHint=String(ev.value||'');menuEpoch++;layoutStage();return;}
  if(ev.type==='aspect'){
    serverVideoAspect=String(ev.value||'').toLowerCase();log('Server video aspect: '+serverVideoAspect+'; browser mode: '+settings.videoFit);applyVideoBounds();return;
  }
  if(ev.type==='gfxUnsupported'){unsupportedGfxCount++;lastUnsupportedGfx=Number(ev.cmd);log('Server reported '+String(ev.name||('GFX '+ev.cmd))+' as '+String(ev.disposition||'unsupported'));return;}
  if(ev.type==='captionState'){
    captionWireStateSeen=true;
    const parsed=Number.parseInt(ev.value,10);sageTvCaptionStateSeen=true;sageTvCaptionState=Number.isFinite(parsed)&&parsed>=0?parsed:0;
    if(captions&&typeof captions.setSageTvState==='function')captions.setSageTvState(sageTvCaptionState,true);
    log('captionState: '+String(ev.value||'')+' → local STV-controlled CC '+(sageTvCaptionState>0?Math.min(4,sageTvCaptionState):'off'));
    if(captionAuthority.mode==='stv'){refreshStvCaptions().catch(setError);updateCaptionAuthorityForm();}return;
  }
  if(ev.type==='channel'||ev.type==='uiAspect'){log(ev.type+': '+String(ev.value||''));return;}
  if(ev.type==='resize'){resizeLocal(ev.width,ev.height);return;}
  if(ev.type==='status'){
    log('Native status: '+ev.state);
    if(ev.state==='closed'){nativeConnectionClosed(ev.error||lastError||'SageTV closed the native connection');return;}
    if(ev.state==='gfx-reconnecting'){setStatus('Recovering native GFX connection…');message('Recovering SageTV graphics connection…');return;}
    if(ev.state==='gfx-reconnected'){nativeRecoveryCount++;setStatus('Connected · GFX recovered');message('');return;}
    setStatus((ev.state||'connected')+(ev.clientId?' · '+ev.clientId:''));
    if(ev.state==='connected')message('Waiting for SageTV / SageMC…');return;
  }
  if(ev.type==='error'){if(ev.fatal){nativeConnectionClosed(ev.message);return;}setError(ev.message||'MiniClient error');message(lastError);return;}
}
function sleep(ms){return new Promise(resolve=>setTimeout(resolve,ms));}
async function eventLoop(serial,id){
  const controller=new AbortController();eventController=controller;
  const active=()=>serial===connectionGeneration&&session===id&&!stopped;
  let workStarted=performance.now(),workCount=0;
  let receiptAt=performance.now(),receiptBusy=false;
  const acknowledgeIdleDelivery=()=>{
    // Renew only after received bytes, not from a background/status timer or
    // server writes, which would retain half-open/orphan sockets indefinitely.
    // The intentionally nonmatching producer makes this existing state route
    // ownership-only, including a race with DVD creation. Never write a clock,
    // Pause, volume or presentation onto an in-flight/new playback producer.
    if(!active()||playback.id||receiptBusy||performance.now()-receiptAt<15000)return;
    receiptAt=performance.now();receiptBusy=true;
    requestJson('api/miniclient','state',{session:id,expectedHlsSession:'__browser_transport_only__',timeMs:-1},'POST',3000,controller.signal)
      .catch(e=>{if(active()&&e.name!=='AbortError'){if(e.httpStatus===404)nativeConnectionClosed('MiniClient session no longer exists; reconnect to SageTV.');else log('Event receipt: '+e.message);}})
      .finally(()=>{receiptBusy=false;});
  };
  const waitForRenderCapacity=async()=>{
    if(active()&&(renderQueued>4096||renderQueuedBytes>8*1024*1024)){
      const pausedAt=performance.now();renderPerformance.eventReadPauses++;
      while(active()&&(renderQueued>4096||renderQueuedBytes>8*1024*1024))await sleep(4);
      const elapsed=performance.now()-pausedAt;
      renderPerformance.eventReadPauseMsTotal+=elapsed;
      renderPerformance.eventReadPauseMsMax=Math.max(renderPerformance.eventReadPauseMsMax,elapsed);
    }
  };
  const consume=ev=>{
    // Playback control must not wait behind PNG decoding or thousands of GFX
    // commands. These methods preserve media-event order through generations.
    if(['videoStart','videoStop','media','captionState','status','error','playbackState'].includes(ev.type)){
      if(active())processEvent(ev).catch(setError);return;
    }
    const bytes=typeof ev.payload==='string'?ev.payload.length:256;
    const frameReceived=ev.type==='gfx'&&(ev.cmd|0)===30?performance.now():null;
    renderQueued++;renderQueuedBytes+=bytes;
    eventChain=eventChain.then(async()=>{
      if(!active())return;
      // Tiny GFX commands previously forced a timer every128 operations even
      // while well below the8ms responsiveness budget. Nested timers can add
      // several milliseconds each on WebKit, replaying old animation frames
      // sluggishly. Keep the wall-time budget and all protocol ordering, but
      // allow up to1024 inexpensive operations before a count-only yield.
      if(++workCount>=1024||performance.now()-workStarted>=8){
        renderPerformance.schedulerYields++;
        await sleep(0);workCount=0;workStarted=performance.now();
      }
      if(active()){
        await processEvent(ev);
        if(active()&&ev.type==='gfx'&&(ev.cmd|0)===30&&ev.ackRequired===true&&Number.isSafeInteger(ev.seq)&&ev.seq>0){
          // Native frame pacing is negotiated at connect. Send this directly:
          // queuing behind a slow user command would recreate the same stall.
          api('frameAck',{session:id,sequence:ev.seq},'POST').catch(e=>{if(active())log('Frame acknowledgement: '+e.message);});
        }
        if(frameReceived!==null&&active()){const ms=performance.now()-frameReceived;renderPerformance.presentedFrames++;renderPerformance.frameQueueMsLast=ms;renderPerformance.frameQueueMsMax=Math.max(renderPerformance.frameQueueMsMax,ms);}
      }
    }).catch(setError).finally(()=>{renderQueued--;renderQueuedBytes-=bytes;});
  };
  while(active()){
    let reader=null;
    try{
      if(Core.eventDelivery(window)==='long-poll'){
        // Use the existing stock-plugin endpoint on iOS: even pre-arming a
        // Fetch read did not eliminate physical-phone redraw stalls. One
        // cancellable finite response at a time avoids that streaming path,
        // with the same ordered graphics, renderer ACKs and no idle busy-poll.
        const events=await requestJson('api/miniclient','events',{session:id,max:500,wait:25000},'GET',30000,controller.signal);
        if(active()&&Array.isArray(events)){
          events.forEach(consume);await waitForRenderCapacity();
          if(active()&&events.length===0){
            const status=await requestJson('api/miniclient','status',{session:id},'GET',3000);
            if(active()&&status.alive===false)nativeConnectionClosed(status.error||'Native SageTV connection ended');
          }
        }continue;
      }
      const url=new URL('api/miniclient',location.href);url.searchParams.set('action','stream');url.searchParams.set('session',id);
      const response=await fetch(url.href,{cache:'no-store',signal:controller.signal});
      if(!active())break;
      if(response.status===404){nativeConnectionClosed('MiniClient session no longer exists; reconnect to SageTV.');break;}
      if(!response.ok)throw new Error('MiniClient stream HTTP '+response.status);
      reader=response.body.getReader();const decoder=new TextDecoder();let pending='';
      let nextPart=reader.read();
      while(active()){
        const part=await nextPart;if(part.done)break;
        // Keep exactly one read pending BEFORE parsing/scheduling this chunk.
        // Affected WebKit Fetch implementations can strand bytes arriving while
        // no pull is pending until the server writes again (WebKit322545).
        // With native FLIP pacing that next write waits for our frame ACK, so
        // the visible SageMC highlight freezes until the1500ms safety timeout.
        // This is read-ahead, not parallel rendering: retain all event order,
        // the existing queue/byte limits and finally's reader cancellation.
        nextPart=reader.read();
        // During queue backpressure/reconnect this promise may reject before
        // the next iteration awaits it. Mark it handled without replacing it:
        // awaiting the original promise still takes the normal error path.
        nextPart.catch(()=>{});
        if(part.value&&part.value.byteLength)acknowledgeIdleDelivery();
        pending+=decoder.decode(part.value,{stream:true});
        if(pending.length>32*1024*1024)throw new Error('Oversized MiniClient event');
        let newline;
        while((newline=pending.indexOf('\n'))>=0){
          const line=pending.slice(0,newline).trim();pending=pending.slice(newline+1);if(!line)continue;
          let event;try{event=JSON.parse(line);}catch(_){continue;}
          if(event.type!=='keepalive')consume(event);
        }
        // Read ahead so media controls arriving in the next network chunk are
        // not blocked by image decode. Bound outstanding GFX work / memory.
        // WEB-048: keep bounded read-ahead; increasing it only delayed queue
        // saturation. Negotiated renderer FLIP acknowledgements pace the native
        // producer instead, without dropping drawing commands or media events.
        await waitForRenderCapacity();
      }
      if(active()){
        // EOF of HTTP is not proof that the native SageTV socket can recover.
        // Inspect the owning session before opening another empty HTTP stream.
        const status=await requestJson('api/miniclient','status',{session:id},'GET',3000);
        if(active()&&status.alive===false){nativeConnectionClosed(status.error||'Native SageTV connection ended');break;}
        if(active()){setStatus('Reconnecting event stream…');await sleep(700);}
      }
    }catch(e){if(active()&&e.name!=='AbortError'){
      if(e.httpStatus===404){nativeConnectionClosed('MiniClient session no longer exists; reconnect to SageTV.');break;}
      setError(e);setStatus('Reconnecting event stream…');await sleep(700);
    }}
    finally{if(reader)try{await reader.cancel();}catch(_){} }
  }
  if(eventController===controller)eventController=null;
}
function stableClientId(){
  const qp=new URLSearchParams(location.search).get('clientId');
  if(/^[0-9A-Fa-f:-]{12,17}$/.test(qp||''))return qp.replace(/[^0-9A-Fa-f]/g,'').slice(0,12).toUpperCase();
  let id='';try{id=localStorage.getItem('sagetvWebMiniClientId')||'';}catch(_){}
  if(/^[0-9A-F]{12}$/i.test(id))return id.toUpperCase();
  const bytes=new Uint8Array(6);crypto.getRandomValues(bytes);bytes[0]=(bytes[0]&0xFC)|0x02;
  id=[...bytes].map(v=>v.toString(16).padStart(2,'0')).join('').toUpperCase();
  try{localStorage.setItem('sagetvWebMiniClientId',id);}catch(_){}return id;
}
function desiredSize(){
  const q=new URLSearchParams(location.search).get('ui'),m=(q||'').match(/^(\d{3,4})x(\d{3,4})$/i);
  document.documentElement.style.setProperty('--mobile-stage-aspect',m?String(Number(m[1])/Number(m[2])):String(16/9));
  if(m)return {w:Math.max(320,Math.min(1920,Number(m[1])))&~1,h:Math.max(240,Math.min(1080,Number(m[2])))&~1};
  const rect=stage.getBoundingClientRect();
  if(document.body.classList.contains('mc-portrait-dock')&&settings.uiResolution==='window'){
    const width=Math.max(640,rect.width*Math.max(1,Math.min(2,window.devicePixelRatio||1)));
    return Core.logicalSize(width,width*9/16,settings.uiResolution,1);
  }
  return Core.logicalSize(rect.width,rect.height,settings.uiResolution,window.devicePixelRatio);
}
async function connect(){
  explicitClientExit=false;explicitExitGeneration++;$('clientExited').hidden=true;
  // One connection attempt per generation. Repeated tap/pageshow/visibility
  // events cannot recreate a new session while it is still starting.
  if(connectingGeneration&&connectingGeneration===connectionGeneration)return;
  const serial=++connectionGeneration,old=session;session='';stopped=false;failureSnapshot=null;lastServerConnectionStatus=null;sageTvCaptionStateSeen=false;sageTvCaptionState=0;captionWireStateSeen=false;captionSelectionSerial++;lastCaptionEvent=null;captionSelectionSignature='';effectiveCaptionSelection=null;
  connectingGeneration=serial;pageRetired=false;foregroundPending=false;foregroundProbe++;
  $('connectionRecovery').hidden=true;$('retryConnectionBtn').disabled=true;
  document.body.classList.remove('mc-connection-lost');$('connectionDiagnosticsBtn').hidden=true;lastError='';
  if(eventController)eventController.abort();gesture.cancel();touchGesture.cancel();keyRepeat.cancel();clearRepeats();clearTimeout(guideTimer);clearInterval(stateTimer);
  destroyVideo();message('Connecting to SageTV MiniClient…');setStatus('Connecting…');$('reconnectBtn').disabled=true;
  const sz=desiredSize();lastRequestedSize=sz.w+'x'+sz.h;resetRenderer(sz.w,sz.h);
  try{
    if(old)try{await api('stop',{session:old},'POST');}catch(_){}
    if(serial!==connectionGeneration)return;
    const server=new URLSearchParams(location.search).get('server')||'';
    const startingOptions=applyCaptionAuthorityToStreaming(Object.assign({},streaming));
    const response=await api('start',Object.assign({server,clientId:stableClientId(),width:sz.w,height:sz.h,unifiedGraphics:!!settings.unifiedGraphics,frameAcks:true},Streaming.toParams(Object.assign({},startingOptions,{adaptiveQuality:settings.adaptiveQuality,adaptiveMinimumKbps:settings.adaptiveMinimumKbps}),Streaming.browserCapabilities(window))),'POST');
    if(serial!==connectionGeneration){api('stop',{session:response.session},'POST').catch(()=>{});return;}
    session=response.session;
    if(response.alive===false){nativeConnectionClosed(response.error||'SageTV closed the connection during initialization');return;}
    setStatus('Connected · '+(response.clientId||stableClientId()));message('Waiting for SageTV / SageMC…');
    eventLoop(serial,session).catch(setError);stateTimer=setInterval(browserState,500);
    if(settings.fullscreenOnConnect)setRenderOnly(true);
    requestResize();
  }catch(e){if(serial===connectionGeneration)nativeConnectionClosed('MiniClient connection failed: '+(e.message||e));}
  finally{if(connectingGeneration===serial)connectingGeneration=0;if(serial===connectionGeneration){$('reconnectBtn').disabled=false;$('retryConnectionBtn').disabled=false;}}
}
async function recoverForeground(){
  if(explicitClientExit)return;
  if(document.hidden||!foregroundPending)return;
  foregroundPending=false;
  if(connectingGeneration&&connectingGeneration===connectionGeneration)return;
  // iOS can return a retired document without the BFCache persisted flag, or
  // freeze a live document until its server session expires. Test the exact
  // generation only: never replay keys, playback starts or seeks, and never
  // loop a failing replacement automatically.
  if(pageRetired||stopped||!session){connect();return;}
  const id=session,generation=connectionGeneration,probe=++foregroundProbe;
  const current=()=>probe===foregroundProbe&&id===session&&generation===connectionGeneration;
  try{
    const result=await requestJson('api/miniclient','status',{session:id},'GET',5000);
    if(!current())return;
    if(document.hidden){foregroundPending=true;return;}
    if(result.alive===false||stopped){connect();return;}
    layoutStage();requestResize();browserState();queueInput('repaint',{x:0,y:0,width:uiW,height:uiH});
  }catch(error){
    if(!current())return;
    if(document.hidden){foregroundPending=true;return;}
    if(error.httpStatus===404){connect();return;}
    // Timeout is not proof of native death: preserve any playing media and
    // offer explicit retry instead of a restart storm.
    log('Foreground session check: '+(error.message||error));
    $('recoveryReason').textContent='Unable to reach SageTV after returning to the app. Check your connection, then reconnect.';
    $('connectionRecovery').hidden=false;$('retryConnectionBtn').disabled=false;
  }
}
function resizeLocal(w,h){
  w=Math.max(320,Math.min(1920,Number(w)||uiW));h=Math.max(240,Math.min(1080,Number(h)||uiH));
  if(w===uiW&&h===uiH){layoutStage();return;}
  // A native resize does not unload SageTV image handles. Clearing the entire
  // image map here loses cached menu text/textures that the server may reuse.
  const old=mainSurface,oldW=uiW,oldH=uiH;
  rememberUiSize(oldW,oldH);rememberUiSize(w,h);
  // SageTV can retain the handles of its full-screen composition surfaces
  // across UI_RESIZE. Resizing only the visible/main canvas leaves those
  // offscreen canvases at portrait width: subsequent landscape drawing is
  // silently clipped before the surface is copied to the visible canvas.
  // Follow only exact old-screen render targets, never ordinary cached
  // images/textures or small preview surfaces, and preserve every handle.
  for(const [handle,surface] of surfaces){
    const entry=images.get(handle);
    if(!handle||!entry||!entry.surface)continue;
    // Match the retained handle's original allocation against the bounded UI
    // history, not just the immediately previous size. Toolbar/standalone and
    // orientation changes may pass through several sizes before this surface
    // is reused for a popup. Keep that classification through later rotations.
    if(!entry.screenSurface&&!uiSizeHistory.has(entry.nativeWidth+'x'+entry.nativeHeight))continue;
    entry.screenSurface=true;
    if(surface.width===w&&surface.height===h)continue;
    const resized=makeCanvas(w,h);
    resized.getContext('2d').drawImage(surface,0,0,surface.width,surface.height,0,0,w,h);
    surfaces.set(handle,resized);
    entry.canvas=resized;entry.width=w;entry.height=h;entry.resizedForUi=true;
  }
  nativeVideoBounds=[nativeVideoBounds[0]*w/oldW,nativeVideoBounds[1]*h/oldH,nativeVideoBounds[2]*w/oldW,nativeVideoBounds[3]*h/oldH];
  if(lastTrustedVideoBounds)lastTrustedVideoBounds=nativeVideoBounds.slice();
  uiW=w;uiH=h;mainSurface=makeCanvas(w,h);
  mainSurface.getContext('2d').drawImage(old,0,0,oldW,oldH,0,0,w,h);surfaces.set(0,mainSurface);
  visible.width=w;visible.height=h;visibleCtx.drawImage(mainSurface,0,0);
  document.documentElement.style.setProperty('--ui-aspect',String(w/h));
  layoutStage();log('Native UI resized to '+w+'x'+h+'; cached image handles retained');
}
async function syncWindowSize(){
  layoutStage();if(!session)return;
  if(resizeInFlight){resizeAgain=true;return;}
  const sz=desiredSize(),key=sz.w+'x'+sz.h;if(key===lastRequestedSize)return;
  const id=session,serial=connectionGeneration;resizeInFlight=true;
  try{
    // Server emits an ordered resize event; do not invalidate the renderer
    // immediately while preceding drawing packets are still being processed.
    const sent=await queueInput('resize',{width:sz.w,height:sz.h});
    if(sent&&id===session&&serial===connectionGeneration)lastRequestedSize=key;
  }finally{resizeInFlight=false;if(resizeAgain){resizeAgain=false;requestResize();}}
}
function requestResize(){clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>syncWindowSize().catch(setError),120);}
let contentPlaySerial=0;
function queueInput(action,params,current){
  if(['command','key','mouse','click'].includes(action))contentPlaySerial++;
  if(!session||stopped)return Promise.resolve(false);
  if(inputPending>64){setError('Input queue is full; check the server connection');return Promise.resolve(false);}
  const id=session,serial=connectionGeneration;inputPending++;
  const queuedAt=timedInputActions.has(action)?performance.now():null;
  const task=inputChain.then(async()=>{
    if(stopped||id!==session||serial!==connectionGeneration)return false;
    if(queuedAt!==null){const ms=performance.now()-queuedAt;renderPerformance.inputQueueMsLast=ms;renderPerformance.inputQueueMsMax=Math.max(renderPerformance.inputQueueMsMax,ms);}
    // A native Time Scroll search is an ordered batch. Keep its Play/arm/move
    // together on this existing input chain; never let a second key interleave
    // or send the remainder after rejection/source retirement. Ordinary input
    // retains its existing one-request path.
    for(const item of Array.isArray(params)?params:[params]){
      if(stopped||id!==session||serial!==connectionGeneration||current&&!current())return false;
      const result=await api(action,Object.assign({session:id},item),'POST');
      if(result.ok===false)return false;
    }
    return true;
  });
  inputChain=task.catch(setError).finally(()=>{inputPending--;});return task.catch(()=>false);
}
function sendCommand(command){
  const dvdFeature=!calibrationOwner&&settingsPanel.hidden&&!exitDialog.open&&
    inputContext()==='dvd'&&dvdMenuState===false&&Date.now()-dvdMenuStateAt<1500;
  if(dvdFeature){
    const commands=dvdKeys.transport(command);
    if(commands)return sendDvdCommands(commands);
  }else if(dvdKeys.scrolling)dvdKeys.cancel(false);
  return sendNativeCommand(command);
}
function sendDvdCommands(commands){
  const id=session,serial=connectionGeneration,stream=playback.id,epoch=playback.dvdGeneration,search=dvdKeys.generation;
  const current=()=>id===session&&serial===connectionGeneration&&stream===playback.id&&epoch===playback.dvdGeneration&&search===dvdKeys.generation&&
    !calibrationOwner&&settingsPanel.hidden&&!exitDialog.open&&inputContext()==='dvd'&&dvdMenuState===false&&Date.now()-dvdMenuStateAt<1500;
  return queueInput('command',commands.map(command=>({command})),current).then(ok=>{if(!ok&&id===session&&stream===playback.id&&search===dvdKeys.generation)dvdKeys.cancel(false);return ok;});
}
function sendNativeCommand(command){
  if(playback.id&&[75,28,18,15,42,88,86,84,85,41,29,40,67,74,89].includes(command)){
    videoPresentationSuspended=true;
    const id=session,serial=connectionGeneration;
    [0,150,500].forEach(delay=>setTimeout(()=>{if(id===session&&serial===connectionGeneration)queueInput('repaint',{x:0,y:0,width:uiW,height:uiH});},delay));
  }
  if(command===6)playback.control('pause');
  else if(command===7)playback.control('play',null,true);
  else if(command===59)playback.control(playback.intentPaused?'play':'pause',null,true);
  else if(command===89){playback.control('pause');videoBounds.hidden=true;}
  return queueInput('command',{command});
}
function sendKey(code,mods,ch){return queueInput('key',{code:code||0,modifiers:mods||0,char:ch||0});}
window.addEventListener('vibe:media-action',e=>{if(!calibrationOwner&&playback.id&&[7,6,89,61,62].includes(e.detail))sendCommand(e.detail);});
function sendMouse(type,point,button,clicks){return queueInput('mouse',{type,x:point.x,y:point.y,button:button||0,modifiers:0,clicks:clicks==null?1:clicks});}
function sendBack(){const now=Date.now();if(now-lastBackAt<250)return;lastBackAt=now;sendCommand(75);}
function inputAction(action){
  if(action==='remote')openRemote();
  else if(action==='keyboard'){openRemote();showDrawer('keyboardPanel','keyboardInput');}
  else if(Object.prototype.hasOwnProperty.call(Input.ACTIONS,action)&&/^\d+$/.test(action))sendCommand(Number(action));
}
const keyRepeat=new Input.Keys({settings:()=>inputSettings,action:inputAction});
const dvdKeys=new Input.DvdKeys({send:sendNativeCommand,batch:sendDvdCommands});
function inputContext(){
  // A decoder existing behind an STV menu does not make that menu DVD keys.
  if(!playback.id||videoPresentation.kind!=='fullscreen')return 'default';
  if(!Input.playbackMenuHint(currentMenuHint))return 'default';
  // Stock STV can paint an OSD-only frame without a video-clear command.
  // That renderer heuristic is not proof of a different native menu. Only
  // the exact, recent DVD-feature observation may override it; named popups,
  // unknown/stale state, preview and ordinary recordings retain the guard.
  if(videoPresentationSuspended&&!(playback.dvd&&dvdMenuState===false&&Date.now()-dvdMenuStateAt<1500))return 'default';
  return playback.dvd?'dvd':playback.intentPaused?'paused':'playing';
}
function sendCanvasClick(point,button){
  const now=Date.now(),mode=settings.clickMode;let includeClick=true;
  if(button===1&&mode==='press_release')includeClick=false;
  if(button===1&&mode==='double_select'){
    includeClick=!!lastClick&&lastClick.button===button&&now-lastClick.at<=700&&Math.hypot(point.x-lastClick.x,point.y-lastClick.y)<=10;
    lastClick=includeClick?null:{x:point.x,y:point.y,button,at:now};
  }
  const hint=currentMenuHint,epoch=menuEpoch,serial=connectionGeneration;
  clearTimeout(guideTimer);
  queueInput('click',{x:point.x,y:point.y,button,includeClick}).then(sent=>{
    if(!sent||!includeClick||button!==1||!settings.guideAssist||!Core.menuIsGuide(hint))return;
    guideTimer=setTimeout(()=>{
      if(serial===connectionGeneration&&epoch===menuEpoch&&currentMenuHint===hint&&settings.guideAssist&&Core.menuIsGuide(currentMenuHint))sendCommand(20);
    },180);
  });
}
const gesture=new Core.PointerGesture({settings:()=>settings,click:sendCanvasClick,open:()=>openRemote(),back:sendBack,
  move:point=>{const now=Date.now();if(now-lastMove<40||inputPending>0)return;lastMove=now;sendMouse(133,point,0,0);},
  dragStart:(point,button)=>sendMouse(130,point,button),
  dragMove:(point,button)=>{const now=Date.now();if(now-lastMove<40||inputPending>2)return;lastMove=now;sendMouse(134,point,button);},
  dragEnd:(point,button)=>sendMouse(131,point,button)
});
const touchGesture=new Input.Touch({settings:()=>inputSettings,action:inputAction,click:point=>sendCanvasClick(point,1)});
visible.addEventListener('pointerdown',e=>{stage.focus();if(e.pointerType==='touch')gesture.suppressUntil=Date.now()+1000;if(touchGesture.down(e,visible.getBoundingClientRect(),currentScalePoint(e))||gesture.down(e,currentScalePoint(e))){e.preventDefault();try{visible.setPointerCapture(e.pointerId);}catch(_){}}});
visible.addEventListener('pointermove',e=>{if(!touchGesture.move(e))gesture.move(e,currentScalePoint(e));});
visible.addEventListener('pointerup',e=>{if(e.pointerType==='touch')gesture.suppressUntil=Date.now()+1000;if(touchGesture.up(e)||gesture.up(e,currentScalePoint(e)))e.preventDefault();try{visible.releasePointerCapture(e.pointerId);}catch(_){}});
visible.addEventListener('pointercancel',()=>{gesture.cancel();touchGesture.cancel();});
visible.addEventListener('lostpointercapture',e=>{if(gesture.active&&gesture.active.id===e.pointerId)gesture.cancel();});
visible.addEventListener('click',e=>gesture.fallbackClick(e,currentScalePoint(e)));
visible.addEventListener('contextmenu',e=>e.preventDefault());
visible.addEventListener('wheel',e=>{e.preventDefault();sendMouse(135,currentScalePoint(e),0,e.deltaY>0?1:-1);},{passive:false});
['mousedown','mouseup','auxclick'].forEach(name=>visible.addEventListener(name,e=>{
  if(e.button!==3||!settings.mouseBack)return;e.preventDefault();e.stopPropagation();if(name==='mousedown')sendBack();
},true));
function clearRepeats(){clearTimeout(repeatTimer);clearInterval(repeatInterval);repeatTimer=null;repeatInterval=null;}
function hideRemoteDrawers(){
  videoTestGeneration++;
  for(const id of ['remoteTools','keyboardPanel','videoInfoPanel'])$(id).hidden=true;
  $('keyboardToggle').setAttribute('aria-expanded','false');$('remoteHelp').setAttribute('aria-expanded','false');
}
function setPhoneToolsExpanded(expanded){
  const tools=$('phoneTools'),toggle=$('phoneToolsToggle');if(!tools||!toggle)return;
  tools.hidden=!expanded;toggle.setAttribute('aria-expanded',String(!!expanded));
  if(expanded)tools.scrollTop=0;
  if(!expanded&&tools.contains(document.activeElement))toggle.focus({preventScroll:true});
}
let watchLivePending=false;
const videoCast=window.SageVideoCast?new window.SageVideoCast.Controller(video,$('remoteCast'),()=>!!session&&!!playback.id&&!stopped,message):
  {update(){$('remoteCast').disabled=true;$('remoteCast').title='Video casting module unavailable. Reload webpage.';}};
function updateWatchLive(){ $('remoteLive').disabled=watchLivePending||!session||!playback.id||playback.dvd; }
function openRemote(expandTools=false){
  updateWatchLive();
  if(mobileDock&&mobileDock.active())mobileDock.controls();
  keyRepeat.cancel();touchGesture.cancel();clearRepeats();
  document.body.classList.add('mc-controls-open');
  hideRemoteDrawers();remotePanel.hidden=false;remotePanel.setAttribute('aria-hidden','false');
  setPhoneToolsExpanded(expandTools);
  $('remoteToggle').setAttribute('aria-expanded','true');
  (playback.id?$('nav_media_pause'):$('nav_options')).focus({preventScroll:true});layoutStage();updateStats();
}
function closeRemote(){
  if(mobileDock&&mobileDock.active()){
    clearRepeats();hideRemoteDrawers();setPhoneToolsExpanded(false);stage.focus({preventScroll:true});return;
  }
  document.body.classList.remove('mc-controls-open');
  clearRepeats();hideRemoteDrawers();remotePanel.hidden=true;remotePanel.setAttribute('aria-hidden','true');
  setPhoneToolsExpanded(false);
  $('remoteToggle').setAttribute('aria-expanded','false');stage.focus({preventScroll:true});layoutStage();
}
function prepareSettingsGroups(){
  const info=document.createElement('button');info.id='remoteStatsInfo';info.className='vibe-icon';info.type='button';
  info.setAttribute('aria-label','Show playback information');info.title='Show playback information';
  info.style.gridColumn='5';info.style.gridRow='1';
  const icon=document.createElement('img');icon.src='icons/vibe/info_outline.svg';icon.alt='';icon.draggable=false;info.appendChild(icon);
  $('remoteStats').after(info);
  const infoLabel=document.createElement('label');infoLabel.className='mc-check';
  const infoCheck=document.createElement('input');infoCheck.type='checkbox';infoCheck.id='showStatsInfo';
  infoLabel.append(infoCheck,document.createTextNode(' Show playback information'));$('showStats').closest('label').after(infoLabel);
  $('showStats').closest('label').lastChild.textContent=' Show playback graphs';
  const adjustment=document.createElement('label');adjustment.appendChild(document.createTextNode('Automatic Bitrate Adjustment'));
  const choice=document.createElement('select');choice.id='automaticBitrateAdjustment';
  for(const [value,label] of [['off','Off (Maximum)'],['switching','Stream Switching'],['inplace','In-place Preferred']])choice.add(new Option(label,value));
  adjustment.appendChild(choice);$('adaptiveQuality').closest('label').before(adjustment);
  $('adaptiveQuality').closest('label').hidden=true;$('stream_runtimeBitrateControl').closest('label').hidden=true;
  choice.addEventListener('change',()=>{
    settings.adaptiveQuality=choice.value!=='off';$('stream_runtimeBitrateControl').checked=choice.value==='inplace';
    saveSettings();commitPrimaryStreamingChoice('automatic bitrate adjustment');
  });
  for(const id of ['cc1Type','cc2Type'])$(id).add(new Option('DVB bitmap','dvb'));
  const inventory=document.createElement('div');inventory.id='captionInventoryList';inventory.className='mc-stream-actual';
  $('captionAuthorityEffective').after(inventory);
  // Move the existing controls, not copies: all stored values, event bindings
  // and stream validation retain one authoritative form element each.
  const browser=$('browserVideoSection');
  for(const id of ['stream_player','videoFit','videoViewport','bufferPreset','startSegments','maxBufferSeconds']){
    const field=$(id);if(field&&browser)browser.insertBefore(field.closest('label'),$('videoTranscoding'));
  }
  for(const el of [...settingsPanel.querySelector('.mc-settings-card').children]){
    if(el.matches('label,button.mc-app-action')||el.id==='resetSettings')el.dataset.settingsGroup='app';
    if(el.matches('p.mc-note'))el.dataset.settingsGroup='app';
  }
  const streamingActions=$('saveStreaming').parentElement;streamingActions.id='streamActions';
  const last=document.createElement('button');last.id='nav_last';last.className='vibe-icon';last.type='button';
  last.dataset.command='60';last.title='Last channel';last.setAttribute('aria-label','Last channel');
  last.style.gridColumn='1';last.style.gridRow='3';
  const image=$('lastChannelIcon').content.firstElementChild.cloneNode(true);last.appendChild(image);
  remotePanel.querySelector('.vibe-pages').appendChild(last);
  ['aspectToggle','remoteSettings','audioSettings','captionSettings'].forEach((id,i)=>{$(id).style.gridColumn=String(i+1);});
}
prepareSettingsGroups();
function syncAdjustmentChoice(){
  const choice=$('automaticBitrateAdjustment');if(choice)choice.value=!settings.adaptiveQuality?'off':$('stream_runtimeBitrateControl').checked?'inplace':'switching';
}
function prepareSettingsTree(){
  const card=settingsPanel.querySelector('.mc-settings-card'),nav=$('settingsCategories');
  const tree=document.createElement('div');tree.id='settingsTree';
  const sections={};
  for(const [key,label] of [['app','General'],['playback','Playback Settings'],['transcoding','Transport Settings'],['input','Input and Remote'],['diagnostics','Diagnostics'],['recovery','Recovery']]){
    const group=document.createElement('details');group.className='mc-settings-section';group.dataset.section=key;
    const summary=document.createElement('summary');summary.textContent=label;summary.hidden=true;
    group.open=true;group.id='settings-page-'+key;group.setAttribute('role','tabpanel');
    group.setAttribute('aria-labelledby','settings-tab-'+key);
    group.appendChild(summary);tree.appendChild(group);sections[key]=group;
  }
  nav.after(tree);nav.hidden=false;nav.setAttribute('role','tablist');
  const pages=['app','playback','transcoding','input','diagnostics','recovery'];
  const labels=['General','Playback','Transport','Input','Diagnostics','Recovery'];
  // Retain shortcut buttons as hidden aliases; visible tabs have one owner each.
  for(const button of nav.querySelectorAll('button'))button.hidden=!pages.includes(button.dataset.settingsPage);
  pages.forEach((key,index)=>{
    let button=nav.querySelector('[data-settings-page="'+key+'"]');
    if(!button){button=document.createElement('button');button.type='button';button.dataset.settingsPage=key;button.addEventListener('click',()=>selectSettingsPage(key));}
    button.hidden=false;button.textContent=labels[index];button.id='settings-tab-'+key;
    button.setAttribute('role','tab');button.setAttribute('aria-controls',sections[key].id);
    nav.appendChild(button);
  });
  nav.addEventListener('keydown',event=>{
    if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key)||event.target.getAttribute('role')!=='tab')return;
    const tabs=[...nav.querySelectorAll('[role="tab"]')],index=tabs.indexOf(event.target);
    const next=event.key==='Home'?0:event.key==='End'?tabs.length-1:(index+(event.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;
    event.preventDefault();event.stopPropagation();selectSettingsPage(tabs[next].dataset.settingsPage);tabs[next].focus({preventScroll:true});
  });
  const move=(id,section,label=true)=>{const field=$(id);if(field)sections[section].appendChild(label?(field.closest('label')||field):field);};
  // Move the existing nodes once, after the App module has added its controls.
  // No cloned fields, new stored processing flags or playback changes.
  for(const id of ['browserVideoSection','companionDvdSection','streamAudioSection','streamCaptionSection','streamSubtitleSection'])move(id,'playback',false);
  move('streamVideoSection','transcoding',false);
  for(const id of ['stream_player','bufferPreset','startSegments','maxBufferSeconds','unifiedGraphics'])move(id,'transcoding');
  for(const id of ['stream_audioCodec','stream_audioKbps','stream_audioChannels']){
    const field=$(id);if(field)$('streamVideoSection').appendChild(field.closest('label'));
  }
  for(const id of ['videoFit','videoViewport','uiResolution','videoMaskAssist','mute'])move(id,'playback');
  move('browserInputSection','input',false);
  for(const id of ['osdTrigger','clickMode','inputMode','mouseBack','guideAssist'])move(id,'input');
  const support=$('supportPreferences');
  for(const child of [...support.children])if(child.tagName!=='SUMMARY')sections.diagnostics.appendChild(child);
  support.removeAttribute('id');support.remove();sections.diagnostics.id='supportPreferences';
  for(const id of ['showStats','showStatsInfo'])move(id,'diagnostics');
  if($('runRuntimeRateTest'))sections.diagnostics.appendChild($('runRuntimeRateTest').parentElement);
  move('audioOutputRestart','recovery',false);move('resetSettings','recovery',false);
  for(const el of [...card.children])if(el.dataset.settingsGroup==='app')sections.app.appendChild(el);
  // App controls were inserted around Reset, so collect them by their group
  // even if a future module inserted one inside a section.
  for(const el of [...settingsPanel.querySelectorAll('[data-settings-group="app"]')])if(!el.closest('.mc-settings-section'))sections.app.appendChild(el);
  const streams=$('streamingPreferences');streams.open=true;
  for(const el of [...streams.children]){
    if(el.tagName==='SUMMARY'){el.hidden=true;continue;}
    sections.transcoding.appendChild(el);
  }
  streams.removeAttribute('id');streams.remove();sections.transcoding.id='streamingPreferences';
  const footer=document.createElement('div');footer.id='settingsStreamFooter';tree.after(footer);
  for(const id of ['streamActions','streamingResult','streamingActual'])footer.appendChild($(id));
  for(const tab of nav.querySelectorAll('[role="tab"]'))tab.setAttribute('aria-controls',sections[tab.dataset.settingsPage].id);
  $('streamVideoSection').querySelector('legend').textContent='Fixed Transcoding Settings';
  // Keep the consolidated controls but display one compact tab at a time.
  for(const el of settingsPanel.querySelectorAll('[data-settings-group]')){
    delete el.dataset.settingsGroup;
    if(el.id!=='companionDvdSection')el.hidden=false;
  }
  $('adaptiveQuality').closest('label').hidden=true;$('stream_runtimeBitrateControl').closest('label').hidden=true;
  // Static essays belong in documentation, not between phone settings.
  // Preserve dynamic status/error text and the concise privacy/apply notices.
  for(const note of tree.querySelectorAll('p.mc-note:not([id]):not([role])'))note.remove();
  const privacy=document.createElement('p');privacy.className='mc-note';privacy.textContent='Reports may contain server addresses and media paths. Review before sharing.';sections.diagnostics.prepend(privacy);
  for(const [id,text] of Object.entries({automaticBitrateAdjustment:'Bitrate adjustment',stream_videoKbps:'Max bitrate (kbps)',adaptiveMinimumKbps:'Min bitrate (kbps)',stream_keyFrameSeconds:'Keyframe interval (s)',stream_resolution:'Maximum height',stream_audioKbps:'Audio bitrate (kbps)',stream_audioFallback:'Missing audio',stream_audioTrack:'Audio track',unifiedGraphics:'Unified graphics (experimental; reconnect)',autoDiagnosticCapture:'Capture terminal failures',saveDiagnosticsToServer:'Save reports to server'})){
    const label=$(id)?.closest('label');if(!label)continue;
    const textNode=[...label.childNodes].find(n=>n.nodeType===Node.TEXT_NODE&&n.textContent.trim());if(textNode)textNode.textContent=text;
  }
  for(const label of tree.querySelectorAll('label:not(.mc-check)')){
    const nodes=[...label.childNodes].filter(n=>n.nodeType===Node.TEXT_NODE&&n.textContent.trim());
    if(!nodes.length)continue;
    const title=document.createElement('span');title.className='mc-setting-label';
    for(const node of nodes)title.appendChild(node);
    title.title=title.textContent;label.prepend(title);
  }
  settingsTreeReady=true;selectSettingsPage(settingsPage);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',prepareSettingsTree,{once:true});
else prepareSettingsTree();
function preparePhoneRemote(){
  const query=window.matchMedia('(max-width: 900px)'),card=remotePanel.querySelector('.mc-remote-card');
  const navigation=document.createElement('div');navigation.className='vibe-phone-navigation';navigation.setAttribute('role','group');navigation.setAttribute('aria-label','SageTV navigation');
  const information=document.createElement('div');information.className='vibe-phone-info';information.setAttribute('role','group');information.setAttribute('aria-label','Playback settings and diagnostics');
  const toggle=document.createElement('button');toggle.id='phoneToolsToggle';toggle.type='button';toggle.className='vibe-icon';
  toggle.title='Settings and diagnostics';toggle.setAttribute('aria-label',toggle.title);toggle.setAttribute('aria-controls','phoneTools');toggle.setAttribute('aria-expanded','false');
  const gear=document.createElement('img');gear.src='icons/vibe/settings.svg';gear.alt='';gear.draggable=false;toggle.appendChild(gear);
  const tools=document.createElement('div');tools.id='phoneTools';tools.className='vibe-phone-tools';tools.hidden=true;
  tools.setAttribute('role','group');tools.setAttribute('aria-label','Playback tools');information.append(toggle,tools);
  toggle.addEventListener('click',()=>setPhoneToolsExpanded(tools.hidden));
  tools.addEventListener('focusin',e=>{
    // Spatial-key focus uses preventScroll to protect the STV viewport. Scroll
    // only this tools column when a keyboard/gamepad reaches an offscreen tool.
    const r=e.target.getBoundingClientRect(),p=tools.getBoundingClientRect();
    if(r.top<p.top)tools.scrollTop-=p.top-r.top;
    else if(r.bottom>p.bottom)tools.scrollTop+=r.bottom-p.bottom;
  });
  // Operator's ICONS_LAYOUT_MOBILE reference: all eight tools on the left,
  // Help precedes Keyboard in the bottom row; Info is between Home and Menu.
  const navIds=['nav_home','nav_info','nav_options','nav_back'],infoIds=['videoInfoBtn','diagnosticsBtn','testVideoBtn','remoteStats','remoteStatsInfo','aspectToggle','remoteSettings','audioSettings','captionSettings'];
  const transport=remotePanel.querySelector('.vibe-transport');
  // Desktop playback order: Watch live, Skip back, Rewind. Capture this as
  // the home position so returning from either phone layout restores it.
  transport.insertBefore($('remoteLive'),$('nav_media_skip_back_2'));
  const original=['remoteLive','remoteHelp','keyboardToggle',...navIds,...infoIds].map(id=>{const node=$(id);return{node,parent:node.parentNode,next:node.nextSibling};})
    .sort((a,b)=>a.node.compareDocumentPosition(b.node)&Node.DOCUMENT_POSITION_FOLLOWING?-1:1);
  transport.appendChild(navigation);card.appendChild(information);
  const update=()=>{
    card.classList.toggle('vibe-phone-layout',query.matches);
    if(query.matches){transport.insertBefore($('keyboardToggle'),transport.firstChild);transport.insertBefore($('remoteHelp'),$('keyboardToggle'));transport.insertBefore(information,$('remoteHelp'));transport.insertBefore($('remoteLive'),$('nav_media_skip_back_2'));navIds.forEach(id=>navigation.appendChild($(id)));infoIds.forEach(id=>tools.appendChild($(id)));}
    else{
      // Restore in reverse order so each original next sibling is already
      // back in its parent. Move existing nodes, never duplicate IDs, commands
      // or settings listeners when the viewport crosses the phone breakpoint.
      [...original].reverse().forEach(o=>o.parent.insertBefore(o.node,o.next&&o.next.parentNode===o.parent?o.next:null));
      card.appendChild(information);
    }
    navigation.hidden=information.hidden=!query.matches;
    setPhoneToolsExpanded(false);
    if(!query.matches&&document.activeElement===toggle)$('remoteSettings').focus({preventScroll:true});
  };
  if(query.addEventListener)query.addEventListener('change',update);else query.addListener(update);
  update();
}
preparePhoneRemote();
if(window.SageMiniMobile)mobileDock=window.SageMiniMobile.mount({
  cancel:()=>{contentPlaySerial++;clearRepeats();keyRepeat.cancel();touchGesture.cancel();hideRemoteDrawers();setPhoneToolsExpanded(false);},
  controls:()=>openRemote(),hide:()=>closeRemote(),layout:()=>{layoutStage();requestResize();},
  read:(kind,q,signal,range={})=>requestJson(kind==='guide'?'api/guide':'api/recordings','read',
    kind==='guide'?{q,hours:4,start:range.start}:{q,limit:500,kind:kind==='videos'?'videos':undefined},'GET',15000,signal),
  info:async params=>{
    if(!session||stopped||explicitClientExit)throw new Error('Reconnect to SageTV first');
    const id=session,generation=connectionGeneration;contentPlaySerial++;
    const reply=await api('infoContent',Object.assign({session:id},params),'POST');
    if(id!==session||generation!==connectionGeneration)throw new Error('The connection changed');
    if(!reply.ok)throw new Error('STV Info was not confirmed');
  },
  record:async airingId=>{
    if(!session||stopped||explicitClientExit)throw new Error('Reconnect to SageTV first');
    const id=session,generation=connectionGeneration;
    const status=await api('status',{session:id},'GET');
    if(id!==session||generation!==connectionGeneration||status.localContent!==true)throw new Error('Recording actions require a confirmed local SageTV connection');
    const reply=await requestJson('api/guide','record',{airingId},'POST',15000);
    if(!reply.ok||reply.scheduled)return reply;
    for(let n=0;n<20;n++){
      await sleep(250);
      const state=await requestJson('api/guide','recordStatus',{airingId},'GET',3000);
      if(state.scheduled)return {ok:true,scheduled:true};
    }
    throw new Error('The request was sent, but the schedule is not confirmed. Refresh the Guide or use STV Info');
  },
  watch:async params=>{
    if(!session||stopped||explicitClientExit)throw new Error('Reconnect to SageTV first');
    const id=session,generation=connectionGeneration,intent=++contentPlaySerial;
    const reply=await api('watchContent',Object.assign({session:id},params),'POST');
    if(id!==session||generation!==connectionGeneration)throw new Error('The connection changed');
    if(!reply.ok)throw new Error('SageTV declined playback');
    await window.SageMiniMobile.showPlayback({
      current:()=>id===session&&generation===connectionGeneration&&intent===contentPlaySerial&&!stopped&&!explicitClientExit,
      read:()=>requestJson('api/miniclient','contentState',Object.assign({session:id},params),'GET',3000),
      show:()=>api('showContent',Object.assign({session:id},params),'POST'),wait:sleep
    });
  }
});
function fillInputMapping(){
  const map=inputSettings.keys[$('mappingContext').value]||{},key=$('mappingKey').value;
  $('mappingPress').value=map[key]||'default';$('mappingHold').value=map[key+':hold']||'default';
  for(const name of ['repeatDelay','repeatInterval','edgeSize','hotspotSize'])$('input_'+name).value=inputSettings[name];
  for(const name of Object.keys(Input.TOUCH))$('touch_'+name).value=inputSettings.touch[name];
  $('input_gamepadEnabled').checked=inputSettings.gamepadEnabled;
}
function prepareInputMappings(){
  Input.KEYS.forEach(key=>$('mappingKey').add(new Option(key,key)));
  const options=select=>Object.entries(Input.ACTIONS).forEach(([value,name])=>select.add(new Option(name,value)));
  options($('mappingPress'));options($('mappingHold'));
  for(const name of Object.keys(Input.TOUCH)){
    const label=document.createElement('label'),select=document.createElement('select');select.id='touch_'+name;options(select);
    label.append(document.createTextNode(name.replace(/_/g,' ')),select);$('touchMappings').appendChild(label);
    select.addEventListener('change',()=>{inputSettings.touch[name]=select.value;saveInputSettings();});
  }
  ['mappingContext','mappingKey'].forEach(id=>$(id).addEventListener('change',fillInputMapping));
  ['mappingPress','mappingHold'].forEach(id=>$(id).addEventListener('change',()=>{
    inputSettings.keys[$('mappingContext').value][$('mappingKey').value+(id==='mappingHold'?':hold':'')]=$(id).value;saveInputSettings();keyRepeat.cancel();
  }));
  for(const name of ['repeatDelay','repeatInterval','edgeSize','hotspotSize'])$('input_'+name).addEventListener('change',()=>{inputSettings[name]=$('input_'+name).value;saveInputSettings();fillInputMapping();});
  $('input_gamepadEnabled').addEventListener('change',()=>{inputSettings.gamepadEnabled=$('input_gamepadEnabled').checked;saveInputSettings();});
  $('resetInputMappings').addEventListener('click',()=>{keyRepeat.cancel();touchGesture.cancel();inputSettings=Input.normalize({});saveInputSettings();fillInputMapping();});
  fillInputMapping();
}
prepareInputMappings();
function selectSettingsPage(page){
  if(settingsTreeReady){
    const aliases={all:'app',app:'app',playback:'playback',video:'playback',audio:'playback',captions:'playback',transcoding:'transcoding',input:'input',diagnostics:'diagnostics',recovery:'recovery'};
    const target=aliases[page]||'app';settingsPage=page;settingsParent=null;$('settingsTitle').textContent='Settings';settingsPanel.dataset.page=target;
    const groups=[...$('settingsTree').children];
    for(const group of groups){group.open=true;group.hidden=group.dataset.section!==target;}
    $('settingsStreamFooter').hidden=!['playback','transcoding'].includes(target);
    const nav=$('settingsCategories');
    for(const tab of nav.querySelectorAll('[role="tab"]')){
      const selected=tab.dataset.settingsPage===target;tab.setAttribute('aria-selected',String(selected));tab.setAttribute('aria-current',String(selected));tab.tabIndex=selected?0:-1;
      if(selected)nav.scrollLeft=Math.max(0,tab.offsetLeft-nav.offsetLeft-(nav.clientWidth-tab.offsetWidth)/2);
    }
    settingsPanel.querySelector('.mc-settings-card').scrollTop=0;
    syncAdjustmentChoice();updateSettingChoices();return;
  }
  const names={all:'Settings',video:'Video settings',audio:'Audio settings',captions:'Subtitles / CC',transcoding:'Transcoding',app:'App settings',input:'Keyboard / touch',diagnostics:'Diagnostics'};
  settingsPage=names[page]?page:'all';$('settingsTitle').textContent=names[settingsPage];
  settingsPanel.dataset.page=settingsPage;
  settingsPanel.querySelectorAll('[data-settings-group]').forEach(el=>{el.hidden=settingsPage!=='all'&&!el.dataset.settingsGroup.split(' ').includes(settingsPage);});
  const streamingPage=['all','video','audio','captions','transcoding'].includes(settingsPage);
  $('streamingPreferences').hidden=!streamingPage;$('streamingPreferences').open=true;
  $('supportPreferences').hidden=!['all','diagnostics'].includes(settingsPage);$('supportPreferences').open=true;
  const actions=$('streamActions');if(actions)actions.hidden=!streamingPage;
  settingsPanel.querySelectorAll('[data-settings-page]').forEach(button=>button.setAttribute('aria-current',String(button.dataset.settingsPage===settingsPage)));
  const card=settingsPanel.querySelector('.mc-settings-card');card.scrollTop=0;
  updateSettingChoices();
  // Scroll only the category strip, not the document or focused native select.
  const nav=$('settingsCategories'),active=nav.querySelector('[aria-current="true"]');
  if(active&&nav.scrollWidth>nav.clientWidth){
    const left=active.offsetLeft-nav.offsetLeft;
    if(left<nav.scrollLeft)nav.scrollLeft=left;
    else if(left+active.offsetWidth>nav.scrollLeft+nav.clientWidth)nav.scrollLeft=left+active.offsetWidth-nav.clientWidth;
  }
}
function updateSettingChoices(){
  // Native select retains its complete accessible value without duplicating
  // it underneath the row. A tooltip is available on pointer-equipped devices.
  settingsPanel.querySelectorAll('label>select').forEach(select=>{
    select.title=select.selectedOptions[0]?.textContent||'';
  });
}
settingsPanel.addEventListener('change',updateSettingChoices);
new MutationObserver(updateSettingChoices).observe(settingsPanel,{childList:true,subtree:true});
function openSettings(section,origin){
  if(settingsPanel.hidden){settingsReturnIcon=!remotePanel.hidden?(origin||document.activeElement):null;settingsParent=null;}
  else if(section==='transcoding'&&settingsPage==='video')settingsParent='video';
  keyRepeat.cancel();clearRepeats();closeRemote();settingsPanel.hidden=false;
  document.body.classList.add('mc-controls-open');
  fillStreamingForm();fillCaptionAuthorityForm();selectSettingsPage(typeof section==='string'?section:'all');
  refreshStreamTracks().catch(setError);refreshDiagnosticDestination().catch(setError);
  // Programmatically focusing an iOS native select/input from the opening
  // gesture can enter its picker/editor immediately. Start on the neutral
  // Back action instead: opening Settings must not edit or Apply anything.
  $('closeSettings').focus({preventScroll:true});
}
function closeSettings(){
  if(!$('calibrationPanel').hidden){closeCalibration();return;}
  if(!$('audioOffsetPanel').hidden){closeAudioOffset();return;}
  if(settingsParent){const parent=settingsParent;settingsParent=null;selectSettingsPage(parent);$('videoTranscoding').focus({preventScroll:true});return;}
  settingsPanel.hidden=true;
  document.body.classList.remove('mc-controls-open');
  if(settingsReturnIcon&&settingsReturnIcon.isConnected){const icon=settingsReturnIcon;settingsReturnIcon=null;openRemote(!!icon.closest('#phoneTools'));icon.focus({preventScroll:true});}
  else stage.focus({preventScroll:true});layoutStage();
}
function showDrawer(id,focusId){hideRemoteDrawers();$(id).hidden=false;$(focusId).focus({preventScroll:true});}
let audioOffsetOriginal=0;
function showAudioOffset(){
  audioOffsetOriginal=Number($('stream_audioOffsetMs').value)||0;$('audioOffsetRange').value=audioOffsetOriginal;
  settingsPanel.querySelector('.mc-settings-card').hidden=true;$('audioOffsetPanel').hidden=false;updateAudioOffset();$('audioOffsetRange').focus();
}
function updateAudioOffset(){const value=Number($('audioOffsetRange').value)||0;$('audioOffsetValue').textContent=(value>=0?'+':'')+(value/1000).toFixed(3)+' s';}
function closeAudioOffset(){
  const value=Number($('audioOffsetRange').value)||0;$('stream_audioOffsetMs').value=value;
  $('audioOffsetPanel').hidden=true;settingsPanel.querySelector('.mc-settings-card').hidden=false;$('audioOffsetOpen').focus({preventScroll:true});
  if(value!==audioOffsetOriginal){if(session&&playback.id)queueStreamingApply('audio sync offset');else commitStreaming(false);}
}
$('audioOffsetOpen').addEventListener('click',showAudioOffset);$('audioOffsetBack').addEventListener('click',closeAudioOffset);
$('audioOffsetRange').addEventListener('input',updateAudioOffset);
$('audioOffsetRange').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();$('audioOffsetRange').value=0;updateAudioOffset();}});
for(const [id,amount] of [['audioOffsetEarlier',-25],['audioOffsetLater',25],['audioOffsetReset',0]])$(id).addEventListener('click',()=>{
  $('audioOffsetRange').value=amount?Math.max(-4000,Math.min(4000,Number($('audioOffsetRange').value)+amount)):0;updateAudioOffset();
});
$('audioOutputRestart').addEventListener('click',()=>{if(session&&playback.id)commitStreaming(true);else $('streamingResult').textContent='No active stream to restart.';});
const calibrationVideo=$('calibrationVideo');
function releaseCalibrationPlayer(){
  calibrationVideo.pause();if(calibrationHls){calibrationHls.destroy();calibrationHls=null;}calibrationVideo.removeAttribute('src');calibrationVideo.load();
}
function releaseCalibrationLease(id){if(id)requestJson('api/av-sync','stop',{id},'POST',5000).catch(error=>log('A/V test cleanup: '+error.message));}
function updateCalibrationOffset(){const value=Number($('calibrationOffset').value)||0;$('calibrationOffsetValue').textContent=(value>=0?'+':'')+(value/1000).toFixed(3)+' s';}
async function generateCalibration(){
  if(!calibrationOwner)return;const serial=++calibrationSerial;
  releaseCalibrationPlayer();releaseCalibrationLease(calibrationLease);calibrationLease=null;
  $('calibrationPlay').disabled=true;$('calibrationApply').disabled=true;$('calibrationStatus').textContent='Generating a bounded server test through the FFmpeg Plugin…';
  try{
    const candidate=readStreamingForm();candidate.audioOffsetMs=Number($('calibrationOffset').value)||0;
    const result=await requestJson('api/av-sync','start',Streaming.toParams(candidate,Streaming.browserCapabilities(window)),'POST',180000);
    if(serial!==calibrationSerial||!calibrationOwner){releaseCalibrationLease(result.id);return;}
    calibrationLease=result.id;const url=new URL(result.playlistUrl,location.href).href;
    if(calibrationVideo.canPlayType('application/vnd.apple.mpegurl')){calibrationVideo.src=url;calibrationVideo.load();}
    else{
      const Hls=await loadHlsJs();if(serial!==calibrationSerial||!calibrationOwner)return;
      if(!Hls||!Hls.isSupported())throw new Error('No supported HLS player in this browser');
      const instance=new Hls({enableWorker:true,maxBufferLength:15,backBufferLength:0});calibrationHls=instance;instance.loadSource(url);instance.attachMedia(calibrationVideo);
      instance.on(Hls.Events.ERROR,(_,error)=>{if(serial===calibrationSerial&&error&&error.fatal)$('calibrationStatus').textContent='A/V test decoder: '+(error.details||error.type);});
    }
    $('calibrationPlay').disabled=false;$('calibrationStatus').textContent='Ready — tap Play test to enable sound. Applied '+(result.audioOffsetMs/1000).toFixed(3)+' s · '+result.encoder+' ('+(result.hardwareEncode?'Hardware':'Software')+' encode).';
  }catch(error){if(serial===calibrationSerial)$('calibrationStatus').textContent='A/V test unavailable: '+error.message;}
  finally{if(serial===calibrationSerial)$('calibrationApply').disabled=false;}
}
function showCalibration(){
  dvdKeys.cancel(true);
  calibrationOwner={native:session,stream:playback.id,generation:connectionGeneration,wasPaused:playback.intentPaused,offset:Number($('stream_audioOffsetMs').value)||0};
  if(playback.id)sendCommand(6);$('calibrationOffset').value=calibrationOwner.offset;updateCalibrationOffset();
  settingsPanel.querySelector('.mc-settings-card').hidden=true;$('calibrationPanel').hidden=false;$('calibrationBack').focus();generateCalibration();
}
function closeCalibration(retiring=false){
  const owner=calibrationOwner;calibrationOwner=null;calibrationSerial++;releaseCalibrationPlayer();releaseCalibrationLease(calibrationLease);calibrationLease=null;
  $('calibrationPanel').hidden=true;settingsPanel.querySelector('.mc-settings-card').hidden=false;
  if(!retiring&&owner){
    const offset=Number($('calibrationOffset').value)||0;$('stream_audioOffsetMs').value=offset;
    const same=owner.native===session&&owner.stream===playback.id&&owner.generation===connectionGeneration;
    if(same&&!owner.wasPaused&&playback.id)sendCommand(7);
    if(same&&offset!==owner.offset){if(session&&playback.id)queueStreamingApply('audio sync offset');else commitStreaming(false);}
    $('audioSyncTest').focus({preventScroll:true});
  }
}
$('audioSyncTest').addEventListener('click',showCalibration);$('calibrationBack').addEventListener('click',()=>closeCalibration());
$('calibrationApply').addEventListener('click',generateCalibration);$('calibrationOffset').addEventListener('input',updateCalibrationOffset);
$('calibrationReset').addEventListener('click',()=>{$('calibrationOffset').value=0;updateCalibrationOffset();});
$('calibrationPlay').addEventListener('click',()=>{calibrationVideo.play().catch(error=>{$('calibrationStatus').textContent='Tap Play again if required by the browser: '+error.message;});});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&calibrationOwner)calibrationVideo.pause();});
window.addEventListener('pagehide',()=>{if(calibrationOwner)closeCalibration(true);});
function layoutSnapshot(){
  const r=stage.getBoundingClientRect();
  return {stage:{width:r.width,height:r.height},nativeBounds:nativeVideoBounds.slice(),source:nativeVideoSource,
    origin:videoBoundsOrigin,presentation:videoPresentation,cssRect:videoLayerRect,
    serverAspect:serverVideoAspect,browserAspect:videoAspect,objectFit:video.style.objectFit};
}
function showVideoInformation(){
  showDrawer('videoInfoPanel','closeVideoInfo');
  $('videoInfoText').textContent=JSON.stringify({scope:'Browser playback and plugin status; not Android device diagnostics',
    layout:layoutSnapshot(),video:{width:video.videoWidth,height:video.videoHeight,readyState:video.readyState,
      networkState:video.networkState,error:video.error?{code:video.error.code,message:video.error.message}:null},
    playback:playback.snapshot(),captions:captions.snapshot(),ordinarySubtitles:ordinarySubtitles.snapshot(),dvdSpu:dvdSpu.snapshot()},null,2);
}
async function waitForTest(predicate,timeoutMs){const end=Date.now()+timeoutMs;while(Date.now()<end){if(predicate())return true;await sleep(100);}return !!predicate();}
function saveVideoTestRecovery(value){try{if(value)sessionStorage.setItem(VIDEO_TEST_RECOVERY_KEY,JSON.stringify(value));else sessionStorage.removeItem(VIDEO_TEST_RECOVERY_KEY);}catch(_){}}
function readVideoTestRecovery(){try{const raw=sessionStorage.getItem(VIDEO_TEST_RECOVERY_KEY);return raw?JSON.parse(raw):null;}catch(_){return null;}}
async function recoverInterruptedVideoTest(ev){if(activeVideoTest)return;const before=readVideoTestRecovery();if(!before)return;const sameMedia=before.mediaId!=null&&ev&&ev.mediaId!=null&&Number(before.mediaId)===Number(ev.mediaId);if(!sameMedia){log('Interrupted video test recovery cleared without mutation because the media changed.');saveVideoTestRecovery(null);return;}if(before.restoreAttempted||before.nativeSession===session)return;before.nativeSession=session;before.hlsSession=playback.id;const restored=await restoreVideoTest(before);log('Interrupted video test recovery: '+(restored?'restored':'unconfirmed; no automatic replay'));}
function sameVideoTestSource(before){return !!before&&!!playback.id&&session===before.nativeSession&&(playback.id===before.hlsSession||(Number.isFinite(before.mediaId)&&before.mediaId>0&&currentVideoMediaId===before.mediaId));}
function videoTestFrameAt(timeMs){return lastPresentedProducer===playback.id&&Number.isFinite(lastPresentedTimeMs)&&Math.abs(lastPresentedTimeMs-timeMs)<1000;}
async function restoreVideoTest(before){
  if(!sameVideoTestSource(before)){saveVideoTestRecovery(null);return false;}
  try{video.muted=!!before.muted;video.volume=Math.max(0,Math.min(1,Number(before.volume)));video.playbackRate=Number(before.playbackRate)||1;}catch(_){}
  let positionRestored=!before.presentationRequired||videoTestFrameAt(before.timeMs);
  if(Math.abs(playback.absoluteTime()-before.timeMs)>1500){const expected=playback.id;before.restoreAttempted=true;before.restoreDelivery='pending';saveVideoTestRecovery(before);try{const delivered=await queueInput('seek',{timeMs:before.timeMs,expectedHlsSession:expected});before.restoreDelivery=delivered?'acknowledged':'unconfirmed';saveVideoTestRecovery(before);positionRestored=!!delivered&&await waitForTest(()=>sameVideoTestSource(before)&&playback.id!==expected&&Math.abs(playback.absoluteTime()-before.timeMs)<1000&&(!before.presentationRequired||videoTestFrameAt(before.timeMs)),3500);}catch(e){before.restoreDelivery='failed';saveVideoTestRecovery(before);positionRestored=false;log('Video test restore seek: '+e);}}
  if(!sameVideoTestSource(before)){saveVideoTestRecovery(null);return false;}
  if(before.intentPaused)playback.control('pause');else playback.control('play',null,true);
  if(positionRestored)saveVideoTestRecovery(null);return positionRestored;
}
async function testCurrentVideo(){
  if(activeVideoTest)return;
  showDrawer('videoInfoPanel','closeVideoInfo');const generation=++videoTestGeneration,id=playback.id,box=$('videoInfoText');
  if(!id){box.textContent='Not tested: no active video. This test never starts a recording by itself.';return;}
  const snap=playback.snapshot(),status=snap.status||{},before={nativeSession:session,hlsSession:id,mediaId:currentVideoMediaId,timeMs:snap.timeMs,paused:video.paused,intentPaused:playback.intentPaused,muted:video.muted,volume:video.volume,playbackRate:video.playbackRate,presentationRequired:typeof video.requestVideoFrameCallback==='function',frames:video.getVideoPlaybackQuality?video.getVideoPlaybackQuality().totalVideoFrames:null};
  activeVideoTest=before;$('testVideoBtn').disabled=true;
  const requireOwner=()=>{if(generation!==videoTestGeneration||!sameVideoTestSource(before))throw new Error('cancelled');};
  saveVideoTestRecovery(before);const steps=[],started=Date.now();box.textContent='Running bounded current-video test… Original position, pause/mute, volume and rate will be restored.';
  try{
    const t0=Number(video.currentTime)||0,f0=before.frames;await sleep(1500);requireOwner();
    const t1=Number(video.currentTime)||0,f1=video.getVideoPlaybackQuality?video.getVideoPlaybackQuality().totalVideoFrames:null;
    steps.push({name:'cadence',ok:before.intentPaused?null:(t1-t0>.2||(f0!=null&&f1>f0)),detail:before.intentPaused?'paused at invocation':{secondsAdvanced:t1-t0,framesAdvanced:f0==null||f1==null?null:f1-f0,bufferAhead:Core.bufferedAhead(video)}});
    const unsafe=!!snap.dvd||!!status.activeRecording||!(snap.durationMs>10000)||!before.presentationRequired;
    if(unsafe)steps.push({name:'mutation-safety',ok:true,skipped:true,reason:snap.dvd?'DVD/title/menu session':status.activeRecording?'live/growing recording':!before.presentationRequired?'presented-frame API unavailable':'unknown or short duration'});
    else{
      const wasPaused=playback.intentPaused;playback.control('pause');await sleep(200);requireOwner();steps.push({name:'pause',ok:video.paused&&playback.intentPaused});if(!wasPaused){playback.control('play',null,true);await sleep(300);requireOwner();steps.push({name:'resume',ok:!playback.intentPaused});}
      const margin=2500,target=Math.min(Math.max(margin,before.timeMs+2000),Math.max(margin,snap.durationMs-margin));
      if(Math.abs(target-before.timeMs)>=1000){const expected=playback.id,delivered=await queueInput('seek',{timeMs:target,expectedHlsSession:expected});const moved=delivered&&await waitForTest(()=>{const observed=playback.absoluteTime();return sameVideoTestSource(before)&&playback.id!==expected&&Math.abs(observed-target)<1000&&Math.abs(observed-before.timeMs)>=750&&videoTestFrameAt(target);},4000);steps.push({name:'reversible-seek',ok:!!moved,targetMs:target,observedMs:playback.absoluteTime(),presentedMs:lastPresentedProducer===playback.id?lastPresentedTimeMs:null,producerChanged:playback.id!==expected});}
      else steps.push({name:'reversible-seek',ok:true,skipped:true,reason:'position too close to media boundary'});
    }
    lastVideoTest={schemaVersion:1,result:steps.every(x=>x.ok!==false)?'PASS':'ATTENTION',boundedMs:Date.now()-started,scope:'Explicit browser/plugin current-video test. Unsafe live/DVD mutation is skipped.',before,after:{timeMs:playback.absoluteTime(),bufferAhead:Core.bufferedAhead(video)},steps,subtitle:Support.captionSummary(captionAuthority,CaptionAuthority.effective(captionAuthority,captionInventory),captionInventory,captions.snapshot(),ordinarySubtitles.snapshot(),dvdSpu.snapshot())};
  }catch(e){lastVideoTest={schemaVersion:1,result:e&&e.message==='cancelled'?'CANCELLED':'ERROR',boundedMs:Date.now()-started,error:e.message||String(e),before,steps};}
  finally{const restored=await restoreVideoTest(before);if(activeVideoTest===before)activeVideoTest=null;$('testVideoBtn').disabled=false;if(lastVideoTest.result==='PASS'&&!restored)lastVideoTest.result='ATTENTION';if(generation===videoTestGeneration&&!$('videoInfoPanel').hidden){lastVideoTest.afterRestore={applied:restored,recoveryPending:!!readVideoTestRecovery(),timeMs:playback.absoluteTime(),paused:playback.intentPaused,muted:video.muted,volume:video.volume,playbackRate:video.playbackRate};box.textContent=JSON.stringify(Support.redact(lastVideoTest),null,2);}log('Current video test: '+(lastVideoTest&&lastVideoTest.result));}
}
$('hideRemote').addEventListener('click',closeRemote);
$('remoteHelp').addEventListener('click',()=>{showDrawer('remoteTools','closeRemoteTools');$('remoteHelp').setAttribute('aria-expanded','true');});
$('remoteLive').addEventListener('click',async()=>{
  const button=$('remoteLive'),expected=playback.id,id=session;
  if(button.disabled||!id||!expected)return;
  watchLivePending=true;button.disabled=true;
  try{
    const result=await api('goLive',{session:id,expectedHlsSession:expected},'POST');
    if(result.accepted){closeRemote();log('Watch live accepted by SageTV');}
    else throw new Error('Watch live is unavailable: the programme changed or is no longer recording.');
  }catch(e){setError(e);}
  finally{watchLivePending=false;updateWatchLive();}
});
$('closeRemoteTools').addEventListener('click',()=>{hideRemoteDrawers();$('remoteHelp').focus({preventScroll:true});});
$('closeKeyboard').addEventListener('click',()=>{hideRemoteDrawers();$('keyboardToggle').focus({preventScroll:true});});
$('closeVideoInfo').addEventListener('click',()=>{videoTestGeneration++;hideRemoteDrawers();$('videoInfoBtn').focus({preventScroll:true});});
$('allSettings').addEventListener('click',()=>openSettings());
$('audioSettings').addEventListener('click',e=>openSettings('audio',e.currentTarget));
$('captionSettings').addEventListener('click',e=>openSettings('captions',e.currentTarget));
$('videoInfoBtn').addEventListener('click',showVideoInformation);
$('testVideoBtn').addEventListener('click',()=>testCurrentVideo().catch(setError));
$('remoteStats').addEventListener('click',()=>{settings.showStats=!settings.showStats;saveSettings();});
$('remoteStatsInfo').addEventListener('click',()=>{settings.showStatsInfo=!settings.showStatsInfo;saveSettings();});
$('aspectToggle').addEventListener('click',()=>{
  const modes=['cover','source','fill'];settings.videoFit=modes[(modes.indexOf(settings.videoFit)+1)%modes.length];
  saveSettings();log('Browser display mode: '+settings.videoFit);
});
remotePanel.addEventListener('pointerdown',e=>{
  const button=e.target.closest('button[data-command][data-repeat="true"]');if(!button||e.button!==0)return;
  clearRepeats();repeatConsumed.set(button,Date.now()+1000);sendCommand(Number(button.dataset.command));
  try{button.setPointerCapture(e.pointerId);}catch(_){}
  repeatTimer=setTimeout(()=>{sendCommand(Number(button.dataset.command));repeatConsumed.set(button,Date.now()+1000);repeatInterval=setInterval(()=>{repeatConsumed.set(button,Date.now()+1000);sendCommand(Number(button.dataset.command));},150);},420);
});
remotePanel.addEventListener('click',e=>{
  if(e.target===remotePanel){closeRemote();return;}
  const button=e.target.closest('[data-command]');if(!button)return;
  if(e.detail!==0&&(repeatConsumed.get(button)||0)>Date.now())return;
  if(button.dataset.dismiss==='true')closeRemote();
  sendCommand(Number(button.dataset.command));
});
['pointerup','pointercancel','lostpointercapture'].forEach(name=>remotePanel.addEventListener(name,clearRepeats));
window.addEventListener('pointerup',clearRepeats);
window.addEventListener('blur',()=>{gesture.cancel();touchGesture.cancel();clearRepeats();keyRepeat.cancel();});
document.addEventListener('visibilitychange',()=>{if(document.hidden){gesture.cancel();touchGesture.cancel();clearRepeats();keyRepeat.cancel();}else layoutStage();});
$('remoteToggle').addEventListener('click',()=>remotePanel.hidden?openRemote():closeRemote());
const exitDialog=$('exitClientDialog');
function cancelClientExit(){exitDialog.close();$('closeRemote').focus({preventScroll:true});}
$('closeRemote').addEventListener('click',()=>{keyRepeat.cancel();touchGesture.cancel();clearRepeats();$('refreshClientPage').disabled=!$('appReloadPage');exitDialog.showModal();$('cancelClientExit').focus({preventScroll:true});});
$('cancelClientExit').addEventListener('click',cancelClientExit);
$('refreshClientPage').addEventListener('click',()=>{
  // Share the App action: cache-busting same-origin navigation, saved settings
  // retained, and confirmation before interrupting this client's playback.
  const reload=$('appReloadPage');if(reload&&!reload.disabled)reload.click();
});
exitDialog.addEventListener('cancel',e=>{e.preventDefault();cancelClientExit();});
$('confirmClientExit').addEventListener('click',()=>{
  explicitClientExit=true;foregroundPending=false;foregroundProbe++;
  if(calibrationOwner)closeCalibration(true);
  retirePageSession('explicit-client-exit');destroyVideo();closeRemote();exitDialog.close();
  $('connectionRecovery').hidden=true;$('clientExited').hidden=false;
  setStatus('Disconnected');message('');$('reconnectAfterExit').focus({preventScroll:true});
});
$('reconnectAfterExit').addEventListener('click',()=>connect());
$('settingsToggle').addEventListener('click',()=>openSettings('all'));$('remoteSettings').addEventListener('click',e=>openSettings('video',e.currentTarget));$('closeSettings').addEventListener('click',closeSettings);
settingsPanel.querySelectorAll('[data-settings-page]').forEach(button=>button.addEventListener('click',()=>{settingsParent=null;selectSettingsPage(button.dataset.settingsPage);}));
if($('videoTranscoding'))$('videoTranscoding').addEventListener('click',()=>openSettings('transcoding'));
settingsPanel.addEventListener('click',e=>{if(e.target===settingsPanel)closeSettings();});
function fillCaptionAuthorityForm(){
  const a=CaptionAuthority.normalize(captionAuthority);for(const k of ['mode','cc1Type','cc1Language','cc1Service','cc2Type','cc2Language','cc2Service']){const id=k==='mode'?'captionAuthorityMode':k,el=$(id);if(el)el.value=String(a[k]);}
  updateCaptionAuthorityForm();
}
function readCaptionAuthorityForm(){return CaptionAuthority.normalize({mode:$('captionAuthorityMode').value,cc1Type:$('cc1Type').value,cc1Language:$('cc1Language').value,cc1Service:$('cc1Service').value,cc2Type:$('cc2Type').value,cc2Language:$('cc2Language').value,cc2Service:$('cc2Service').value});}
function updateCaptionAuthorityForm(){
  let a;try{a=readCaptionAuthorityForm();}catch(_){a=captionAuthority;}const eff=CaptionAuthority.effective(a,captionInventory);
  const stvState=a.mode==='stv'?(sageTvCaptionStateSeen?(sageTvCaptionState>0?' · STV selected CC'+Math.min(4,sageTvCaptionState):' · STV captions off'):' · waiting for STV caption state'):'';
  $('captionAuthorityEffective').textContent='Effective caption source: '+eff.label+stvState+(eff.missing?' (not currently discovered)':'');
  if(a.mode==='stv'&&effectiveCaptionSelection)$('captionAuthorityEffective').textContent+=' · '+effectiveCaptionSelection.label;
  const inventory=$('captionInventoryList');if(inventory){
    inventory.replaceChildren();
    const first=CaptionAuthority.effective(Object.assign({},a,{mode:'cc1'}),captionInventory),second=CaptionAuthority.effective(Object.assign({},a,{mode:'cc2'}),captionInventory);
    for(const track of captionInventory){if(!CaptionAuthority.codec(track))continue;const row=document.createElement('div');
      row.textContent=CaptionAuthority.codec(track).toUpperCase()+' · '+(track.language||'unknown')+
        (first.track===track?' (CC1)':'')+(second.track===track?' (CC2)':'');inventory.appendChild(row);}
    if(!inventory.children.length)inventory.textContent='No broadcast caption services discovered.';
  }
  const slots=$('virtualCaptionSlots');if(slots)slots.hidden=!['cc1','cc2','stv'].includes(a.mode);
  if(typeof updateCaptionControls==='function')updateCaptionControls();
}
function applyCaptionAuthorityToStreaming(candidate){
  captionAuthority=readCaptionAuthorityForm();saveCaptionAuthority();candidate.captionAuthority=captionAuthority.mode;const eff=CaptionAuthority.effective(captionAuthority,captionInventory);
  if(captionAuthority.mode==='stv'){candidate.captions='608';candidate.captionService=1;return candidate;}
  if(captionAuthority.mode==='dvb'){candidate.captions='dvb';return candidate;}
  if(captionAuthority.mode==='off'){candidate.captions='off';return candidate;}
  if(eff.missing){
    const key=captionAuthority.mode==='cc2'?'cc2':'cc1',type=captionAuthority[key+'Type'];
    candidate.captions=type==='cea708'?'708':type==='teletext'?'teletext':type==='dvb'?'dvb':type==='cea608'?'608':'off';
    candidate.captionService=(type==='cea608'||type==='cea708')?Number(captionAuthority[key+'Service']||1):(captionAuthority.mode==='cc2'?2:1);
    candidate.captionLanguage=captionAuthority[key+'Language']||candidate.captionLanguage||'';
    return candidate;
  }
  candidate.captions=eff.local;candidate.captionService=eff.service||1;
  if(eff.track){if(eff.local==='teletext'){candidate.captionPage=Number(eff.track.teletextPage)||888;candidate.captionLanguage=eff.track.language||'';}if(eff.local==='dvb'){candidate.captionPid=Number(eff.track.sourcePid);candidate.captionCompositionPage=Number(eff.track.compositionPageId);candidate.captionLanguage=eff.track.language||'';}}
  return candidate;
}
['captionAuthorityMode','cc1Type','cc1Language','cc1Service','cc2Type','cc2Language','cc2Service'].forEach(id=>{const el=$(id);if(el)el.addEventListener('change',updateCaptionAuthorityForm);});

function fillStreamingForm(value=streaming){
  for(const k of Object.keys(Streaming.DEFAULTS)){const el=$('stream_'+k);if(!el)continue;if(el.type==='checkbox')el.checked=!!value[k];else el.value=String(value[k]);}
  updateAutomaticHeightLabel();
  syncAdjustmentChoice();
  if(typeof updateCaptionControls==='function')updateCaptionControls();
}
function updateAutomaticHeightLabel(){
  const option=$('stream_resolution').querySelector('option[value="auto"]');
  if(option)option.textContent='Automatic ('+Streaming.automaticResolution(window)+'p device limit)';
}
window.addEventListener('resize',updateAutomaticHeightLabel);
function readStreamingForm(){
  const v=Object.assign({},streaming);for(const k of Object.keys(Streaming.DEFAULTS)){const el=$('stream_'+k);if(el)v[k]=el.type==='checkbox'?el.checked:el.value;}
  return Streaming.normalize(v);
}
function showStreamActual(active){
  const el=$('streamingActual');if(!active){el.textContent='No active recording.';return;}
  const e=active.effective||{},source=active.source||{};
  captionInventory=Array.isArray(source.tracks)?source.tracks:[];updateCaptionAuthorityForm();
  const authEff=CaptionAuthority.effective(captionAuthority,captionInventory),requested=active.requested||{};
  if(session&&playback.id&&!captionAutoResolveBusy&&['cc1','cc2'].includes(captionAuthority.mode)&&!authEff.missing&&String(requested.captions||'off')!==String(authEff.local)){captionAutoResolveBusy=true;setTimeout(()=>commitStreaming(true).finally(()=>{captionAutoResolveBusy=false;}),0);}
  el.textContent='Actual video: '+(e.video||'starting')+' · audio: '+(e.audio||'—')+' · stream index: '+(e.audioStreamIndex==null?'auto':e.audioStreamIndex)+
    '\nVideo target: '+(e.videoTargetKbps==null?'not applicable / copy':e.videoTargetKbps+' kbps')+' · audio target: '+(e.audioTargetKbps==null?'copy':e.audioTargetKbps+' kbps')+
    '\nAudio: '+(e.audioLanguage||'unknown')+(e.audioTitle?' · '+e.audioTitle:'')+' · delay '+(e.audioDelayMs||0)+' ms'+
    '\nPipeline: decode '+(e.decode||'—')+(e.decodeAccelerator?' ('+e.decodeAccelerator+')':'')+' · filters '+(e.filters||'—')+' · encode '+(e.effectiveEncoder||e.video||'—')+(e.hardwareEncode?' HW':'')+(e.endToEndGpu?' · end-to-end GPU':' · mixed/software processing')+
    (e.fallbackReason?'\nFallback: '+e.fallbackReason:'')+'\n'+(e.reason||'')+(source.warning?'\n'+source.warning:'');
  const select=$('stream_audioTrack'),value=select.value||'-1';select.replaceChildren(new Option('Automatic / preferred language','-1'));
  for(const t of source.tracks||[])if(t.type==='audio')select.add(new Option('#'+t.index+' · '+(t.language||'unknown language')+' · '+t.codec+' · '+t.channels+' ch'+(t.title?' · '+t.title:''),String(t.index)));
  select.value=[...select.options].some(o=>o.value===value)?value:'-1';
  const sub=$('stream_subtitleTrack'),subValue=sub.value||'-1';sub.replaceChildren(new Option('Automatic / preferred language','-1'));
  for(const t of source.tracks||[]){const c=String(t.codec||'').toLowerCase(),ordinary=t.type==='subtitle'&&!t.serviceKind&&(c.includes('subrip')||c.includes('webvtt')||c==='ass'||c==='ssa'||c.includes('pgs')||c.includes('dvd_subtitle')||c.includes('vobsub'));if(ordinary)sub.add(new Option('#'+t.index+' · '+(t.language||'unknown language')+' · '+t.codec+(t.forced?' · forced':'')+(t.default?' · default':'')+(t.sourceKind==='sidecar'?' · sidecar':'')+(t.title?' · '+t.title:''),String(t.index)));}
  sub.value=[...sub.options].some(o=>o.value===subValue)?subValue:'-1';
  updateSubtitleControls();
  const tele=$('stream_teletextService'),teleValue=tele.value||'';tele.replaceChildren(new Option('Auto / preferred page',''));
  for(const t of source.tracks||[])if(t.serviceKind==='teletext'){const v=[t.sourcePid,t.teletextPage,t.language||''].join(':');tele.add(new Option('Page '+t.teletextPage+' · '+(t.language||'unknown language')+' · PID 0x'+Number(t.sourcePid).toString(16),v));}
  if([...tele.options].some(o=>o.value===teleValue))tele.value=teleValue;
  const dvb=$('stream_dvbService'),wantedDvb=[String(streaming.captionPid),String(streaming.captionCompositionPage),streaming.captionLanguage||''].join(':');dvb.replaceChildren(new Option('Auto / preferred language',''));
  for(const t of source.tracks||[])if(t.serviceKind==='dvb-subtitle'){const v=[t.sourcePid,t.compositionPageId,t.language||''].join(':');dvb.add(new Option((t.language||'unknown language')+' · PID 0x'+Number(t.sourcePid).toString(16)+' · page '+t.compositionPageId+(t.hearingImpaired?' · hearing impaired':''),v));}
  const current=[String($('stream_captionPid').value),String($('stream_captionCompositionPage').value),$('stream_captionLanguage').value||''].join(':');if([...dvb.options].some(o=>o.value===current))dvb.value=current;else if([...dvb.options].some(o=>o.value===wantedDvb))dvb.value=wantedDvb;
}
async function refreshStreamTracks(){
  if(!session){showStreamActual(null);return;}
  const id=session,activeId=playback.id;const response=await api('streamSettings',{session:id},'GET');
  if(id===session&&activeId===playback.id)showStreamActual(response.active);
}
let streamingApplyTimer=null,streamingApplySerial=0,streamingCommitBusy=false,pendingStreamingCommit=null;
function queueStreamingApply(reason){
  if(!session||!playback.id)return;
  if(playback.dvd){commitStreaming(false);return;}
  const owner={session,stream:playback.id,generation:connectionGeneration};
  const serial=++streamingApplySerial;if(streamingApplyTimer)clearTimeout(streamingApplyTimer);
  $('streamingResult').textContent='Pending '+reason+'…';
  streamingApplyTimer=setTimeout(()=>{streamingApplyTimer=null;if(serial!==streamingApplySerial||owner.session!==session||owner.stream!==playback.id||owner.generation!==connectionGeneration)return;commitStreaming(true,serial);},450);
}
async function commitStreaming(now,serial,queued){
  const owner=queued?queued.owner:{session,stream:playback.id,generation:connectionGeneration};
  if(serial==null){streamingApplySerial++;if(streamingApplyTimer){clearTimeout(streamingApplyTimer);streamingApplyTimer=null;}}
  let candidate;
  try{candidate=queued?queued.candidate:applyCaptionAuthorityToStreaming(readStreamingForm());}
  catch(error){$('streamingResult').textContent=error.message||String(error);return;}
  if(settings.adaptiveMinimumKbps>candidate.videoKbps){$('streamingResult').textContent='Minimum bitrate must not exceed Maximum bitrate.';return;}
  // Exactly one server replacement is in flight; only the latest desired
  // successor is retained. Never build an unbounded queue while dragging.
  if(streamingCommitBusy){pendingStreamingCommit={now,serial,owner,candidate};return;}
  if(owner.session!==session||owner.generation!==connectionGeneration||owner.stream!==playback.id)return;
  streamingCommitBusy=true;let successor='';
  const result=$('streamingResult'),buttons=[$('saveStreaming'),$('applyStreaming')];buttons.forEach(b=>b.disabled=true);
  try{
    const params=Streaming.toParams(Object.assign({},candidate,{adaptiveQuality:settings.adaptiveQuality,adaptiveMinimumKbps:settings.adaptiveMinimumKbps}),Streaming.browserCapabilities(window));
    if(now&&(!session||!playback.id))throw new Error('Start a recording first, or save these settings for the next recording.');
    if(session){
      const response=await api('streamSettings',Object.assign({session,applyNow:now,timeMs:playback.absoluteTime(),expectedHlsSession:playback.id},params),'POST');
      if(response.stale)throw new Error('Recording changed before settings were applied. Refresh tracks and try again.');
      // Our own Apply can replace the media ID before its HTTP reply arrives.
      // Accept only that exact returned successor, never an unrelated Watch.
      if(owner.session!==session||owner.generation!==connectionGeneration||
        owner.stream!==playback.id&&response.session!==playback.id)return;
      successor=response.session||owner.stream;
      if(serial!=null&&serial!==streamingApplySerial)return;
      showStreamActual(response.active);
    }
    streaming=Streaming.normalize(Object.assign({},candidate,{audioTrack:-1,subtitleTrack:-1,subtitleMode:candidate.subtitleMode==='track'?'auto':candidate.subtitleMode}));
    try{localStorage.setItem(STREAMING_KEY,JSON.stringify(streaming));}catch(_){}
    if(serial==null||serial===streamingApplySerial)result.textContent=now?(playback.dvd?'DVD settings submitted at the native title position. Paused playback stays paused; replacement video starts on Resume.':'Applied. Restarted at the current reported position; pause intent and native GFX session were retained.'):playback.dvd?'Saved for the next DVD source generation. Active DVD Push playback is unchanged.':'Saved for the next recording. Existing playback is unchanged.';
  }catch(e){result.textContent=e.message||String(e);setError(e);}
  finally{
    streamingCommitBusy=false;buttons.forEach(b=>b.disabled=false);
    drainStreamingCommit(owner,successor);
  }
}
function drainStreamingCommit(owner,successor){
  const next=pendingStreamingCommit;pendingStreamingCommit=null;
  if(next&&next.owner.session===session&&next.owner.generation===connectionGeneration){
    const unchanged=next.owner.stream===playback.id;
    const ours=successor&&playback.id===successor&&next.owner.stream===owner.stream;
    if(unchanged||ours){if(ours)next.owner=Object.assign({},next.owner,{stream:successor});commitStreaming(next.now,next.serial,next);}
  }
}
async function applyQualityRecommendation(){
  const recommendation=qualityAdvisor.recommendation;
  if(!recommendation||qualityBusy||streamingCommitBusy||pendingStreamingCommit||!session||!playback.id||playback.dvd)return;
  const owner={session,stream:playback.id,generation:connectionGeneration},source=timeline.key;
  if(runtimeRateUnconfirmedOwner===owner.stream)return;
  qualityBusy=streamingCommitBusy=true;let successor='';
  qualityAdvisor.appliedAt(performance.now());
  try{
    const runtime=timeline.state&&timeline.state.runtimeBitrateControl;
    if(streaming.runtimeBitrateControl&&runtime&&runtime.available===true){
      // Hold future automatic/manual adaptation if any response is ambiguous.
      // New producer identity clears the hold; the current video is retained.
      runtimeRateUnconfirmedOwner=owner.stream;
      const requestId=++runtimeRateRequestId;
      let result=await api('runtimeRate',{session:owner.session,expectedHlsSession:owner.stream,requestId,videoKbps:recommendation.videoKbps},'POST');
      const deadline=performance.now()+16000;
      while(true){
        if(owner.session!==session||owner.stream!==playback.id||owner.generation!==connectionGeneration||source!==timeline.key)return;
        if(Number(result.requestId)!==requestId)throw new Error('In-place request identity changed; stream retained.');
        if(result.state==='applied'&&Number(result.appliedKbps)===recommendation.videoKbps){
          timeline.state.runtimeBitrateControl=result;
          runtimeRateUnconfirmedOwner='';
          qualityLastResult='Same encoder now at '+result.appliedKbps+' kbps; buffered older segments retain their prior rate.';return;
        }
        if(result.state!=='pending'||performance.now()>deadline)throw new Error('In-place bitrate result unconfirmed; no command replay or decoder restart.');
        await new Promise(resolve=>setTimeout(resolve,500));
        if(owner.session!==session||owner.stream!==playback.id||owner.generation!==connectionGeneration||source!==timeline.key)return;
        result=await api('runtimeRate',{session:owner.session,expectedHlsSession:owner.stream},'GET');
      }
    }
    if(!timeline.state||timeline.state.qualityHandoffRevision!==1||typeof video.requestVideoFrameCallback!=='function')
      throw new Error('This browser/server cannot confirm a quality handoff; current stream retained.');
    const response=await api('qualityPrepare',{session:owner.session,expectedHlsSession:owner.stream,timeMs:playback.absoluteTime(),
      videoKbps:recommendation.videoKbps,height:recommendation.resolution||0},'POST');
    if(owner.session!==session||owner.generation!==connectionGeneration||source!==timeline.key)return;
    if(response.ok===false||response.stale)throw new Error('Recording changed before quality switch.');
    successor=response.session||owner.stream;
    if(owner.stream!==playback.id&&successor!==playback.id)return;
    showStreamActual(response.active);
    qualityLastResult='Replacement prepared at '+recommendation.videoKbps+' kbps; awaiting presented frame. Saved quality unchanged.';
  }catch(error){
    if(owner.session===session&&source===timeline.key){qualityLastResult='Quality switch failed: '+String(error.message||error).slice(0,180);log(qualityLastResult);}
  }finally{qualityBusy=streamingCommitBusy=false;drainStreamingCommit(owner,successor);}
}
$('applyQualityRecommendation').addEventListener('click',()=>applyQualityRecommendation());
for(const [button,operation] of [['runRuntimeRateTest','start'],['readRuntimeRateTest','status']])$(button).addEventListener('click',async()=>{
  try{const result=await api('runtimeRateTest',{session,operation},'POST');$('runtimeRateTestResult').textContent=JSON.stringify(result);}
  catch(error){$('runtimeRateTestResult').textContent='Test unavailable/refused: '+String(error.message||error).slice(0,180);}
});
function updateQualityRecommendation(snap){
  const now=performance.now(),state=timeline.state||{},runtime=state.runtimeBitrateControl;
  const inPlace=streaming.runtimeBitrateControl&&runtime&&runtime.available===true;
  const capable=inPlace||state.qualityHandoffRevision===1&&typeof video.requestVideoFrameCallback==='function';
  const confirmed=runtimeRateUnconfirmedOwner!==snap.id&&(!runtime||runtime.state!=='unconfirmed');
  $('applyQualityRecommendation').disabled=!qualityAdvisor.recommendation||qualityBusy||streamingCommitBusy||!capable||!confirmed;
  $('qualityRecommendation').textContent=qualityBusy?'Adjusting session bitrate…':
    qualityLastResult||('MIM buffer adjustment: '+qualityAdvisor.reason+'. '+settings.adaptiveMinimumKbps+'–'+streaming.videoKbps+' kbps.');
  if(!settings.adaptiveQuality||!snap.id||!session){qualityAdvisor.recommendation=null;qualityAdvisor.reason='fixed-maximum';return;}
  if(state.bufferAdaptationRevision!==1){qualityAdvisor.recommendation=null;qualityAdvisor.reason='provider-unavailable; Fixed bitrate retained';return;}
  if(bufferReportBusy||qualityBusy||streamingCommitBusy||!confirmed||now-bufferReportAt<3000)return;
  const owner={session,stream:snap.id,generation:connectionGeneration,source:timeline.key},report=++bufferReportId;
  const eligible=capable&&!snap.paused&&!snap.blocked&&!snap.recovering&&!snap.starting&&snap.firstFrameMs!=null&&
    !timeline.model().pending&&!video.seeking&&!snap.dvd&&(!video.paused||snap.rebuffering);
  bufferReportBusy=true;bufferReportAt=now;
  api('bufferReport',{session:owner.session,expectedHlsSession:owner.stream,reportId:report,
    positionMs:Math.max(0,Math.round(Number(snap.localTimeSeconds||0)*1000)),bufferMs:Number.isFinite(snap.ahead)?Math.round(snap.ahead*1000):-1,
    buffering:!!snap.rebuffering,eligible},'POST').then(reply=>{
      if(owner.session!==session||owner.stream!==playback.id||owner.generation!==connectionGeneration||owner.source!==timeline.key)return;
      qualityAdvisor.key=owner.source;qualityAdvisor.reason=reply.reason||'unavailable';qualityAdvisor.samples=reply.samples||0;
      qualityAdvisor.recommendation=null;
      if(reply.revision!==1||reply.reportId!==report||!eligible||!settings.adaptiveQuality||playback.intentPaused||video.seeking||timeline.model().pending)return;
      const target=Number(reply.targetKbps);
      if(!target||target<settings.adaptiveMinimumKbps||target>streaming.videoKbps)return;
      qualityAdvisor.recommendation={videoKbps:target,resolution:null,reason:'Shared MIM buffer policy.'};
      if(!qualityBusy&&!streamingCommitBusy)applyQualityRecommendation();
    }).catch(()=>{qualityAdvisor.reason='report unavailable; bitrate held';qualityAdvisor.recommendation=null;})
    .finally(()=>{bufferReportBusy=false;});
}
$('saveStreaming').addEventListener('click',()=>commitStreaming(false));$('applyStreaming').addEventListener('click',()=>commitStreaming(true));
for(const id of ['adaptiveQuality','adaptiveMinimumKbps'])$(id).addEventListener('change',()=>commitPrimaryStreamingChoice('bitrate adjustment'));
for(const id of ['stream_audioOffsetMs','stream_videoKbps']){const el=$(id);if(el)el.addEventListener('input',()=>queueStreamingApply(id==='stream_audioOffsetMs'?'audio delay':'video quality'));}
function commitPrimaryStreamingChoice(reason){
  // Video processing is a primary playback choice. Persist it as soon as the
  // user selects it so closing/reopening Settings cannot silently restore the
  // old value. If media is active, use the existing bounded Apply
  // path so only the media stream restarts and the MiniClient/GFX session stays.
  if(session&&playback.id)queueStreamingApply(reason);
  else{$('streamingResult').textContent='Saving '+reason+'…';commitStreaming(false);}
}
{const el=$('stream_videoMode');if(el)el.addEventListener('change',()=>commitPrimaryStreamingChoice('video processing'));}
for(const id of ['stream_audioTrack','stream_audioCodec','stream_audioChannels','stream_encoder','stream_resolution','stream_fps','stream_deinterlace','stream_deinterlaceFilter','stream_keyFrameSeconds','stream_bFrames']){const el=$(id);if(el)el.addEventListener('change',()=>queueStreamingApply('stream setting'));}
$('refreshTracks').addEventListener('click',()=>refreshStreamTracks().catch(e=>{$('streamingResult').textContent=e.message;}));
$('resetStreaming').addEventListener('click',()=>{fillStreamingForm(Streaming.normalize({}));$('streamingResult').textContent='Defaults loaded into the form. Save or Apply now to use them.';});
$('preparePlayerAssets').addEventListener('click',async()=>{
  const button=$('preparePlayerAssets'),result=$('streamingResult');button.disabled=true;
  result.textContent='Preparing pinned mpegts.js and hls.js assets in the server cache…';
  try {
    const data=await requestJson('api/assets','prefetch',{family:'streaming'},'POST',130000);
    if(data.errors&&data.errors.length)throw new Error(data.errors.join('; '));
    if(!data.streamingReady)throw new Error('Player assets are not ready. Check the server cache and internet access.');
    result.textContent='Player assets cached on the server. Future playback starts use the local cache.';
  }catch(e){result.textContent=e.message||String(e);setError(e);}
  finally{button.disabled=false;}
});
function updateSubtitleControls(){const mode=$('stream_subtitleMode').value;$('stream_subtitleTrack').disabled=mode!=='track';$('stream_subtitleLanguage').disabled=mode==='off'||mode==='track';$('stream_subtitleForcedOnly').disabled=mode==='off';$('stream_subtitleOffsetMs').disabled=mode==='off';}
$('stream_subtitleMode').addEventListener('change',updateSubtitleControls);$('stream_subtitleTrack').addEventListener('change',()=>{if($('stream_subtitleTrack').value!=='-1')$('stream_subtitleMode').value='track';updateSubtitleControls();});
function updateCaptionControls(){
  let mode=$('stream_captions').value;
  try{const a=readCaptionAuthorityForm();if(a.mode==='dvb')mode='dvb';else if(a.mode==='cc1'||a.mode==='cc2'){const k=a.mode==='cc2'?'cc2':'cc1',t=a[k+'Type'];mode=t==='teletext'?'teletext':t==='dvb'?'dvb':t==='cea708'?'708':t==='cea608'?'608':'off';}else mode='off';}catch(_){}
  const cea=$('stream_captionService');cea.disabled=mode==='teletext'||mode==='dvb'||mode==='off';cea.max=mode==='608'?'4':'63';if(Number(cea.value)>Number(cea.max))cea.value='1';$('stream_teletextService').disabled=mode!=='teletext';$('stream_captionPage').disabled=mode!=='teletext';$('stream_dvbService').disabled=mode!=='dvb';$('stream_captionPid').disabled=mode!=='dvb';$('stream_captionCompositionPage').disabled=mode!=='dvb';$('stream_captionLanguage').disabled=mode!=='teletext'&&mode!=='dvb';
}
$('stream_captions').addEventListener('change',updateCaptionControls);
fillCaptionAuthorityForm();
$('stream_teletextService').addEventListener('change',()=>{const v=$('stream_teletextService').value;if(!v)return;const parts=v.split(':');if(parts.length>=2)$('stream_captionPage').value=parts[1];if(parts.length>=3&&parts[2])$('stream_captionLanguage').value=parts[2];});
$('stream_dvbService').addEventListener('change',()=>{const v=$('stream_dvbService').value;if(!v){$('stream_captionPid').value='-1';$('stream_captionCompositionPage').value='-1';return;}const parts=v.split(':');$('stream_captionPid').value=parts[0]||'-1';$('stream_captionCompositionPage').value=parts[1]||'-1';if(parts[2])$('stream_captionLanguage').value=parts[2];});
function downloadBlob(blob,name){const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
async function refreshDiagnosticDestination(){
  try{
    diagnosticStatus=await requestJson('api/support','status',{},'GET',4000);
    const e=$('diagnosticDestinationStatus');if(e)e.textContent=diagnosticStatus.configured?(diagnosticStatus.writesEnabled?'Server diagnostic destination configured ('+(diagnosticStatus.destinationName||'mounted path')+'). Spool '+(diagnosticStatus.spoolFiles||0)+' file(s).':'Destination configured but server writes are disabled.'):'No server diagnostic destination configured. Browser downloads still work.';
    $('sendReportServer').disabled=!(diagnosticStatus.configured&&diagnosticStatus.writesEnabled);
    return diagnosticStatus;
  }catch(error){$('sendReportServer').disabled=true;const el=$('diagnosticDestinationStatus');if(el)el.textContent='Diagnostic destination status unavailable: '+(error.message||error);throw error;}
}
function diagnosticSnapshot(reason){
  const cap=captions.snapshot(),ord=ordinarySubtitles.snapshot(),spu=dvdSpu.snapshot(),ps=playback.snapshot(),st=ps.status||{};
  ps.experience={timeline:timeline.model(),previews:framePreviews.snapshot(),sourcePreviews:sourcePreviews.snapshot(),markers:{count:markerRows.length,state:markerStatus},quality:{enabled:settings.adaptiveQuality,source:qualityAdvisor.key,
    method:'buffer-only',minimumKbps:settings.adaptiveMinimumKbps,maximumKbps:streaming.videoKbps,reason:qualityAdvisor.reason,samples:qualityAdvisor.samples,
    reductions:qualityAdvisor.applied,cooldownUntilMs:qualityAdvisor.cooldown,recommendation:qualityAdvisor.recommendation,lastResult:qualityLastResult}};
  const stvResolved=captionAuthority.mode==='stv'&&effectiveCaptionSelection;
  const eff=stvResolved||CaptionAuthority.effective(captionAuthority,captionInventory);
  const captionReport=Support.captionSummary(captionAuthority,eff,captionInventory,cap,ord,spu);
  if(stvResolved){captionReport.renderOwner=eff.local==='off'?'off':'browser-local-stv-controlled';captionReport.stvStateSeen=sageTvCaptionStateSeen;captionReport.stvState=sageTvCaptionStateSeen?sageTvCaptionState:null;}
  return Support.redact({schemaVersion:1,version:'3.3.0',generatedAt:new Date().toISOString(),reason:reason||'manual',userAgent:navigator.userAgent,nativeSession:session,hlsSession:playback.id||failureSnapshot&&failureSnapshot.playback&&failureSnapshot.playback.id||'',ui:{width:uiW,height:uiH,display:displayRect,viewport:{width:innerWidth,height:innerHeight},requested:lastRequestedSize,frame,gfxCount,images:images.size,lastEventAt,menuHint:currentMenuHint,rendererThread:'main (time-sliced)',renderQueued,renderQueuedBytes,renderPerformance:Object.assign({},renderPerformance),unsupportedGfxCount,lastUnsupportedGfx,unifiedGraphicsRequested:!!settings.unifiedGraphics},videoLayout:layoutSnapshot(),failureSnapshot,serverConnection:lastServerConnectionStatus,nativeRecoveryCount,settings,streaming,browserCapabilities:Streaming.browserCapabilities(window),playback:ps,diagnostics:{captions:captionReport,broadcastQueue:cap.queue||null,fileQueue:ord.queue||null,dvdSpuQueue:spu.queue||null,effectiveTranscode:Support.effectiveTranscode(st),timestampEpoch:st.playbackEpoch||null,dvd:st.dvd||null,dvdMenuState,dvdMenuStateAt,dvdMenuFrame:{generation:dvdFrameGeneration,frozenGeneration:dvdFrozenGeneration,cacheValid:dvdFrameCacheValid,captures:dvdFrameCaptures,promotions:dvdStillPromotions,misses:dvdStillMisses,visible:!dvdStill.hidden}},lastVideoTest,logs:logs.slice(-200)});
}
async function refreshServerConnectionDiagnostic(){if(!session)return;try{const st=Support.redact(await requestJson('api/miniclient','status',{session},'GET',3000));if(st&&typeof st==='object'){delete st.clientId;delete st.session;lastServerConnectionStatus=st;}}catch(e){log('Diagnostic native status: '+(e.message||e));}}
async function fetchDiagnosticZip(reason,saveToServer){await refreshServerConnectionDiagnostic();const report=diagnosticSnapshot(reason),failureHls=failureSnapshot&&failureSnapshot.playback&&failureSnapshot.playback.id||'',body=new URLSearchParams({browserJson:JSON.stringify(report),videoTestJson:JSON.stringify(Support.redact(lastVideoTest)),session:session||'',hlsSession:playback.id||failureHls,saveToServer:String(!!saveToServer)}),u=new URL('api/support',location.href);u.searchParams.set('action','report');const r=await fetch(u.href,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'},body,cache:'no-store'});if(!r.ok)throw new Error((await r.text()).slice(0,500)||('HTTP '+r.status));const state=r.headers.get('X-SageTV-Report-Save')||'not-requested',detail=r.headers.get('X-SageTV-Report-Detail')||'';return{blob:await r.blob(),state,detail};}
async function downloadDiagnosticReport(reason){const out=await fetchDiagnosticZip(reason,settings.saveDiagnosticsToServer);downloadBlob(out.blob,'SageTV-WebPlayer-diagnostics-'+new Date().toISOString().replace(/[:.]/g,'-')+'.zip');log('Diagnostic report downloaded; server save '+out.state+(out.detail?': '+out.detail:''));return out;}
async function saveDiagnosticReportToServer(reason){const out=await fetchDiagnosticZip(reason,true);log('Diagnostic server capture '+out.state+(out.detail?': '+out.detail:''));return out;}
async function automaticDiagnosticCapture(reason){try{if(!diagnosticStatus)await refreshDiagnosticDestination();}catch(_){}if(diagnosticStatus&&diagnosticStatus.configured&&diagnosticStatus.writesEnabled)return saveDiagnosticReportToServer(reason);const out=await downloadDiagnosticReport(reason);log('Automatic diagnostic capture used browser download because no enabled server destination is configured.');return out;}
function exportProfile(){const profile=Support.buildProfile(settings,streaming,captionAuthority,{input:inputSettings,keepAwake:!!($('appKeepAwake')&&$('appKeepAwake').checked),showControls:!!($('appShowControls')&&$('appShowControls').checked),portraitTopPx:Number($('appPortraitTopPx')?.value||0)});downloadBlob(new Blob([JSON.stringify(profile,null,2)+'\n'],{type:'application/json'}),'SageTV-Vibe-Web-profile-v2.json');}
function showProfilePreview(preview){const box=$('profilePreview');if(!box)return;box.textContent=JSON.stringify({schemaVersion:preview.schemaVersion,migrations:preview.migrations,unknownKeys:preview.unknownKeys,willApply:{client:Object.keys(preview.client||{}),streaming:Object.keys(preview.streaming||{}),captions:Object.keys(preview.captions||{}),input:Object.keys(preview.input||{}),browserApp:Object.keys(preview.browserApp||{})},note:'Client identity and per-session audio/subtitle/PID selections are never imported.'},null,2);$('applyProfile').disabled=false;}
async function loadProfileFile(file){const text=await file.text();pendingProfileImport=Support.previewProfile(text);showProfilePreview(pendingProfileImport);}
function applyImportedProfile(){
  if(!pendingProfileImport)return;
  // Validate every scope before mutating any current browser preference.
  let client,streams,cc;try{
    client=Core.normalizeSettings(Object.assign({},settings,pendingProfileImport.client||{}));
    streams=Streaming.normalize(Object.assign({},streaming,pendingProfileImport.streaming||{},{audioTrack:-1,subtitleTrack:-1,captionPid:-1,captionCompositionPage:-1}));
    cc=CaptionAuthority.normalize(Object.assign({},captionAuthority,pendingProfileImport.captions||{}));
  }catch(error){$('profilePreview').textContent='Profile not applied: '+error.message;return;}
  const priorUnified=settings.unifiedGraphics;settings=client;streaming=streams;captionAuthority=cc;
  if(pendingProfileImport.input){inputSettings=Input.normalize(pendingProfileImport.input);saveInputSettings();fillInputMapping();keyRepeat.cancel();touchGesture.cancel();}
  if(pendingProfileImport.browserApp)window.dispatchEvent(new CustomEvent('vibe:app-preferences',{detail:pendingProfileImport.browserApp}));
  try{localStorage.setItem(STREAMING_KEY,JSON.stringify(streaming));}catch(_){}
  saveCaptionAuthority();saveSettings();fillStreamingForm();fillCaptionAuthorityForm();pendingProfileImport=null;
  $('applyProfile').disabled=true;$('profilePreview').textContent='Profile applied. Unrelated existing preferences were preserved.';
  if(priorUnified!==settings.unifiedGraphics&&session)connect();
}
function applySettings(){
  Object.keys(Core.DEFAULTS).forEach(key=>{const el=$(key);if(!el)return;if(el.type==='checkbox')el.checked=settings[key];else el.value=String(settings[key]);});
  statsEl.hidden=!settings.showStatsInfo;$('statsGauges').hidden=!settings.showStats;$('statsPanel').hidden=!(settings.showStats||settings.showStatsInfo);$('statsToggle').setAttribute('aria-pressed',String(settings.showStats||settings.showStatsInfo));
  $('remoteStats').setAttribute('aria-pressed',String(settings.showStats));
  $('remoteStatsInfo').setAttribute('aria-pressed',String(settings.showStatsInfo));
  $('remoteStats').setAttribute('aria-label',settings.showStats?'Hide playback graphs':'Show playback graphs');
  $('remoteStatsInfo').setAttribute('aria-label',settings.showStatsInfo?'Hide playback information':'Show playback information');
  syncAdjustmentChoice();
  const fitLabel={cover:'Fill browser',source:'Fit',fill:'Stretch',zoom:'Zoom','4x3':'4:3','16x9':'16:9'}[settings.videoFit];
  $('aspectToggle').title='Video display: '+fitLabel+' — click to cycle Fill, Fit, Stretch';
  $('aspectToggle').setAttribute('aria-label',$('aspectToggle').title);
  video.muted=settings.mute;videoAspect=settings.videoFit;applyVideoBounds();
  playback.updateBufferSettings();requestResize();
}
Object.keys(Core.DEFAULTS).forEach(key=>{const el=$(key);if(!el)return;el.addEventListener('change',()=>{settings[key]=el.type==='checkbox'?el.checked:el.value;saveSettings();});});
$('unifiedGraphics').addEventListener('change',()=>{if(session){message('Unified graphics setting changed; reconnecting SageTV graphics…');connect();}});
$('resetSettings').addEventListener('click',()=>{settings=Core.normalizeSettings({});saveSettings();setRenderOnly(false);});
function newDiagnosticOperationId(){try{if(crypto&&typeof crypto.randomUUID==='function')return crypto.randomUUID();}catch(_){}return 'support-'+Date.now()+'-'+Math.random().toString(16).slice(2);}
async function runDiagnosticServerAction(action,timeoutMs){if(diagnosticOperationId)throw new Error('A server diagnostic action is already running');const id=newDiagnosticOperationId();diagnosticOperationId=id;$('cancelDiagnosticAction').disabled=false;try{return await requestJson('api/support',action,{confirm:true,operationId:id},'POST',timeoutMs);}finally{if(diagnosticOperationId===id)diagnosticOperationId=null;$('cancelDiagnosticAction').disabled=true;refreshDiagnosticDestination().catch(()=>{});}}
$('exportProfile').addEventListener('click',exportProfile);$('importProfile').addEventListener('click',()=>$('profileFile').click());$('profileFile').addEventListener('change',e=>{const f=e.target.files&&e.target.files[0];if(f)loadProfileFile(f).catch(setError);e.target.value='';});$('applyProfile').addEventListener('click',applyImportedProfile);$('testDiagnosticDestination').addEventListener('click',async()=>{const b=$('testDiagnosticDestination');b.disabled=true;try{const r=await runDiagnosticServerAction('testDestination',10000);$('diagnosticDestinationStatus').textContent=r.ok?'Server destination test passed: '+r.detail:'Server destination test '+(r.stage==='cancelled'?'cancelled':'failed at '+r.stage)+': '+r.detail;}catch(e){setError(e);$('diagnosticDestinationStatus').textContent=e.message||String(e);}finally{b.disabled=false;}});$('retryDiagnosticSpool').addEventListener('click',async()=>{const b=$('retryDiagnosticSpool');b.disabled=true;try{const r=await runDiagnosticServerAction('retrySpool',15000);$('diagnosticDestinationStatus').textContent=r.detail||r.state;}catch(e){setError(e);}finally{b.disabled=false;}});$('cancelDiagnosticAction').addEventListener('click',async()=>{const id=diagnosticOperationId;if(!id)return;$('cancelDiagnosticAction').disabled=true;try{const r=await requestJson('api/support','cancel',{operationId:id},'POST',3000);$('diagnosticDestinationStatus').textContent=r.cancelled?'Cancellation requested; the current bounded file step will finish safely.':'The server action already finished.';}catch(e){setError(e);}});
$('statsToggle').addEventListener('click',()=>{const enabled=!(settings.showStats||settings.showStatsInfo);settings.showStats=settings.showStatsInfo=enabled;saveSettings();});
$('keyboardToggle').addEventListener('click',()=>{showDrawer('keyboardPanel','keyboardInput');$('keyboardToggle').setAttribute('aria-expanded','true');});
function sendText(){const field=$('keyboardInput'),text=field.value;if(!text)return;queueInput('text',{text}).then(sent=>{if(sent&&field.value===text)field.value='';});field.focus();}
$('keyboardSend').addEventListener('click',sendText);$('keyboardInput').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();sendText();}});
$('keyboardBackspace').addEventListener('click',()=>sendKey(8,0,8));$('keyboardEnter').addEventListener('click',()=>sendKey(13,0,13));
function setRenderOnly(enabled){document.body.classList.toggle('mc-render-only',!!enabled);settings.renderOnly=!!enabled;try{localStorage.setItem(SETTINGS_KEY,JSON.stringify(settings));}catch(_){}closeRemote();window.scrollTo(0,0);requestResize();}
$('renderOnlyBtn').addEventListener('click',()=>setRenderOnly(!document.body.classList.contains('mc-render-only')));
$('fullscreenBtn').addEventListener('click',async()=>{try{if(!document.fullscreenElement)await $('app').requestFullscreen();else await document.exitFullscreen();}catch(_){setRenderOnly(true);}stage.focus();});
document.addEventListener('fullscreenchange',()=>{document.body.classList.toggle('mc-fullscreen',!!document.fullscreenElement);requestResize();});
$('reconnectBtn').addEventListener('click',connect);
$('retryConnectionBtn').addEventListener('click',connect);
$('recoveryDiagnosticsBtn').addEventListener('click',()=>downloadDiagnosticReport('connection-failure').catch(setError));
window.addEventListener('keydown',e=>{
  if(e.defaultPrevented||e.isComposing||e.keyCode===229)return;
  if(exitDialog.open){
    keyRepeat.cancel();clearRepeats();
    if(e.key==='Escape'){e.preventDefault();cancelClientExit();}
    else if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){
      e.preventDefault();const actions=[...exitDialog.querySelectorAll('button:not(:disabled)')],index=actions.indexOf(document.activeElement),step=['ArrowLeft','ArrowUp'].includes(e.key)?-1:1;
      actions[(Math.max(0,index)+step+actions.length)%actions.length].focus({preventScroll:true});
    }else if(e.key==='Enter'&&Input.GAMEPAD.some(entry=>entry[0]===e.code)){
      e.preventDefault();if(exitDialog.contains(document.activeElement)&&document.activeElement.matches('button:not(:disabled)'))document.activeElement.click();
    }else if(!['Tab','Enter',' '].includes(e.key))e.preventDefault();
    return;
  }
  if(explicitClientExit){
    if(!['Tab','Enter',' '].includes(e.key))e.preventDefault();return;
  }
  const gamepad=Input.GAMEPAD.some(entry=>entry[0]===e.code);
  const remoteOwnsKeys=!remotePanel.hidden&&(!(mobileDock&&mobileDock.active())||remotePanel.contains(e.target));
  const editable=e.target&&(e.target.isContentEditable||e.target.closest&&e.target.closest('input,textarea,select,[contenteditable="true"],[role="textbox"]'));
  const dvdKey=gamepad?e.code:e.key;
  const dvdDefault=Input.keyAction(inputSettings,'dvd',dvdKey)==='default'&&Input.keyAction(inputSettings,'dvd',dvdKey,true)==='default';
  const dvdFeature=!calibrationOwner&&settingsPanel.hidden&&!exitDialog.open&&inputContext()==='dvd'&&dvdMenuState===false&&Date.now()-dvdMenuStateAt<1500;
  const dvdPlayback=dvdFeature&&!remoteOwnsKeys&&!editable;
  // Remote buttons still own their normal Enter/click and spatial navigation.
  // Focusing/activating one is not retirement of an existing DVD search. An
  // Enter on the next FF/RW button must extend it, not re-arm Time Scroll and
  // accidentally toggle the STV back out. Real context/edit/source loss still
  // cancels; do not deliver raw DVD keys behind the remote overlay.
  if(!dvdFeature||editable)dvdKeys.cancel(false);
  if(dvdPlayback&&dvdDefault&&!e.ctrlKey&&!e.altKey&&!e.metaKey&&dvdKeys.down(e.key)){e.preventDefault();return;}
  if(e.key==='Escape'){
    if(!settingsPanel.hidden){e.preventDefault();closeSettings();return;}
    if(remoteOwnsKeys){e.preventDefault();if(['remoteTools','keyboardPanel','videoInfoPanel'].some(id=>!$(id).hidden)){hideRemoteDrawers();$('nav_options').focus({preventScroll:true});}else if($('phoneToolsToggle').getClientRects().length&&!$('phoneTools').hidden){setPhoneToolsExpanded(false);$('phoneToolsToggle').focus({preventScroll:true});}else closeRemote();return;}
    if(document.body.classList.contains('mc-render-only')){e.preventDefault();setRenderOnly(false);return;}
  }
  const drawer=!remotePanel.hidden?['remoteTools','keyboardPanel','videoInfoPanel'].map($).find(el=>!el.hidden):null;
  const modal=!settingsPanel.hidden?settingsPanel:drawer||(!remotePanel.hidden&&!(mobileDock&&mobileDock.active())?remotePanel:null);
  if(!modal&&mobileDock&&mobileDock.contains(e.target)&&!remotePanel.contains(e.target))return;
  // Synthetic Gamepad keys do not receive native button/select default
  // actions. Supply only the equivalent local action, never a remote command.
  if(gamepad&&modal&&e.target){
    const field=e.target;
    if(e.key==='Enter'&&field.tagName==='BUTTON'){e.preventDefault();field.click();return;}
    if(field.tagName==='SELECT'&&['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.key)){
      field.selectedIndex=Math.max(0,Math.min(field.options.length-1,field.selectedIndex+(['ArrowUp','ArrowLeft'].includes(e.key)?-1:1)));field.dispatchEvent(new Event('change',{bubbles:true}));e.preventDefault();return;
    }
    if(field.tagName==='INPUT'&&field.type==='checkbox'&&e.key==='Enter'){field.checked=!field.checked;field.dispatchEvent(new Event('change',{bubbles:true}));e.preventDefault();return;}
    if(field.tagName==='INPUT'&&['range','number'].includes(field.type)&&['ArrowLeft','ArrowRight'].includes(e.key)){
      if(e.key==='ArrowRight')field.stepUp();else field.stepDown();field.dispatchEvent(new Event('input',{bubbles:true}));e.preventDefault();return;
    }
  }
  if(modal===settingsPanel&&['ArrowUp','ArrowDown'].includes(e.key)&&e.target&&!/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)){const focusable=[...settingsPanel.querySelectorAll('button,input,select,summary,a[href]')].filter(el=>!el.disabled&&el.getClientRects().length);const i=focusable.indexOf(document.activeElement);if(i>=0&&focusable.length){e.preventDefault();focusable[(i+(e.key==='ArrowDown'?1:-1)+focusable.length)%focusable.length].focus({preventScroll:false});return;}}
  if(e.key==='Tab'&&modal){
    const focusable=[...modal.querySelectorAll('button,input,select,summary,a[href]')].filter(el=>!el.disabled&&el.getClientRects().length);
    if(!focusable.length)return;const first=focusable[0],last=focusable[focusable.length-1];
    if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}return;
  }
  if(!settingsPanel.hidden||drawer)return;
  if(remoteOwnsKeys&&/^Arrow/.test(e.key)&&!editable){
    const buttons=[...remotePanel.querySelectorAll('button')].filter(el=>!el.disabled&&el.getClientRects().length);
    const boxes=buttons.map((el,id)=>{const r=el.getBoundingClientRect();return {id,x:r.left,y:r.top,width:r.width,height:r.height};});
    const index=buttons.indexOf(document.activeElement),next=Core.spatialTarget(boxes,index,e.key);
    if(buttons[next])buttons[next].focus({preventScroll:true});e.preventDefault();keyRepeat.cancel();return;
  }
  if(editable||e.target&&/^(?:BUTTON|A)$/.test(e.target.tagName)&&['Enter',' '].includes(e.key))return;
  if(e.ctrlKey||e.metaKey||e.altKey)return;
  if(settings.inputMode==='text'){
    if(e.key==='Tab')return;
    if(e.key.length===1||['Enter','Backspace','Delete','ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){
      e.preventDefault();sendKey(e.keyCode||e.which||0,e.shiftKey?1:0,e.key.length===1?e.key.charCodeAt(0):e.key==='Enter'?13:e.key==='Backspace'?8:0);
    }return;
  }
  if(e.key==='ContextMenu'||e.key==='F10'&&e.shiftKey){e.preventDefault();openRemote();return;}
  const key=gamepad?e.code:e.key,fallback=Core.remoteCommand(e.key),context=inputContext(),mapped=Input.keyAction(inputSettings,context,key),hold=Input.keyAction(inputSettings,context,key,true);
  const action=mapped==='default'?(fallback==null?'default':String(fallback)):mapped;
  if(action!=='default'||hold!=='default'){e.preventDefault();if(!e.repeat)keyRepeat.down(key,action,hold,['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','PageUp','PageDown'].includes(e.key));return;}
  if(e.key&&e.key.length===1){e.preventDefault();sendKey(e.keyCode||e.which||0,e.shiftKey?1:0,e.key.charCodeAt(0));}
});
window.addEventListener('keyup',e=>{dvdKeys.up(e.key);keyRepeat.up(Input.GAMEPAD.some(entry=>entry[0]===e.code)?e.code:e.key);});
window.addEventListener('blur',()=>dvdKeys.cancel(false));
document.addEventListener('visibilitychange',()=>{if(document.hidden)dvdKeys.cancel(false);});
const gamepads=new Input.Gamepads({cancel:()=>keyRepeat.cancel(),event:(type,code,key)=>{
  const target=document.activeElement||stage;target.dispatchEvent(new KeyboardEvent(type,{code,key,bubbles:true,cancelable:true}));
}});
let gamepadFrame=null,lastGamepadPoll=0,gamepadFocused=true;
function pollGamepads(time){
  gamepadFrame=null;if(pageRetired||document.hidden||!gamepadFocused){gamepads.cancel();return;}
  if(time-lastGamepadPoll>=33){lastGamepadPoll=time;
    try{if(inputSettings.gamepadEnabled&&navigator.getGamepads){gamepads.poll(navigator.getGamepads());$('gamepadStatus').textContent=gamepads.padIndex==null?'No standard gamepad active. Press a controller button to connect.':'Standard gamepad connected.';}else{gamepads.cancel();$('gamepadStatus').textContent=navigator.getGamepads?'Gamepad input disabled.':'Gamepad API unavailable in this browser/context.';}}catch(_){gamepads.cancel();$('gamepadStatus').textContent='Gamepad access denied by this browser.';}
  }
  gamepadFrame=requestAnimationFrame(pollGamepads);
}
function resumeGamepads(){if(gamepadFrame==null&&!document.hidden&&!pageRetired&&gamepadFocused&&navigator.getGamepads)gamepadFrame=requestAnimationFrame(pollGamepads);}
document.addEventListener('visibilitychange',()=>{if(document.hidden){gamepads.cancel();if(gamepadFrame!=null)cancelAnimationFrame(gamepadFrame);gamepadFrame=null;}else resumeGamepads();});
window.addEventListener('blur',()=>{gamepadFocused=false;gamepads.cancel();});
window.addEventListener('focus',()=>{gamepadFocused=true;resumeGamepads();});window.addEventListener('gamepaddisconnected',()=>gamepads.cancel());
window.addEventListener('pagehide',()=>{gamepads.cancel();if(gamepadFrame!=null)cancelAnimationFrame(gamepadFrame);gamepadFrame=null;});
window.addEventListener('pageshow',resumeGamepads);resumeGamepads();
$('autoplayBtn').addEventListener('click',()=>{playback.control('play',null,true);sendCommand(7);});
$('seekRange').addEventListener('input',()=>{
  seeking=true;const target=timeline.preview(Number($('seekRange').value)*1000);updateExperienceTimeline();
  if(settings.scrubPreviews&&!playback.dvd&&target!==null&&!framePreviews.nearest(timeline.key,target))sourcePreviews.request(timeline.key,target);
});
$('seekRange').addEventListener('change',()=>{
  const timeMs=Math.max(0,Number($('seekRange').value)*1000);seeking=false;
  if(!session||!playback.id)return;gesture.cancel();
  timeline.request(timeMs).then(ok=>{if(!ok&&timeline.model().error)setError(timeline.model().error);});
});
$('timelineCancel').addEventListener('click',()=>{seeking=false;timeline.cancelPreview();updateExperienceTimeline();});
$('seekRange').addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();event.stopPropagation();seeking=false;timeline.cancelPreview();updateExperienceTimeline();}});
$('timelineLive').addEventListener('click',()=>{const edge=timeline.model().liveEdge;if(Number.isFinite(edge))timeline.request(Math.max(0,edge-1000));});
function updateExperienceTimeline(){
  const model=timeline.model(),range=$('seekRange');
  range.disabled=!model.seekable;
  if(!seeking){range.min=String((model.start||0)/1000);range.max=String(Math.max(1,(model.end||0)/1000));range.value=String(Math.max(0,model.value/1000));}
  $('timelineTime').textContent=model.seekable?Core.timeText(model.value)+' / '+Core.timeText(model.end):model.dvd?'DVD — use native chapter/Time Scroll controls':'No seekable recording';
  const position=value=>Number.isFinite(value)?Core.timeText(value):'not yet observed';
  $('timelinePhase').textContent=(model.error||model.phase)+' · Requested '+position(model.requested)+' · Accepted '+position(model.accepted)+' · Displayed '+position(model.displayed);
  $('timelineCancel').hidden=model.phase!=='preview';$('timelineLive').hidden=!Number.isFinite(model.liveEdge);
  range.setAttribute('aria-valuetext',position(model.value)+'; '+model.phase);
  updateTimelineExtras(model);
  updateDvdCompanion();
}
function updateDvdCompanion(){
  const owner=String(session||'')+':'+String(dvdCompanionState.loadGeneration||0);
  if(updateDvdCompanion.owner!==owner){updateDvdCompanion.owner=owner;dvdCompanionMessage='';}
  $('dvdCompanionStatus').textContent=(dvdCompanionMessage?dvdCompanionMessage+' ':'')+'Client Extension: '+(dvdCompanionState.state||'unavailable')+(dvdCompanionState.controls?' · current-load actions available':' · native controls unchanged');
  document.querySelectorAll('[data-companion-dvd]').forEach(button=>{button.disabled=dvdCompanionBusy||!playback.dvd||!dvdCompanionState.controls;});
}
document.querySelectorAll('[data-companion-dvd]').forEach(button=>button.addEventListener('click',async()=>{
  if(dvdCompanionBusy||!playback.dvd||!dvdCompanionState.controls)return;
  const native=session,generation=connectionGeneration,load=dvdCompanionState.loadGeneration;
  dvdCompanionBusy=true;updateDvdCompanion();
  try{const reply=await api('dvdCompanion',{session,operation:button.dataset.companionDvd},'POST');
    if(native!==session||generation!==connectionGeneration||load!==dvdCompanionState.loadGeneration)return;
    if(reply.state)dvdCompanionState=reply.state;
    dvdCompanionMessage=Experience.dvdActionMessage(reply.ok,reply.state?.actionOutcome);
  }catch(_){if(native===session&&generation===connectionGeneration)dvdCompanionMessage=Experience.dvdActionMessage(false,'unknown');}
  finally{dvdCompanionBusy=false;updateDvdCompanion();}
}));
function cacheViewedFrame(timeMs){
  const key=timeline.key;
  if(!settings.scrubPreviews||playback.dvd||!key||previewBusy||previewFailedSource===key||framePreviews.has(timeMs)||!video.videoWidth||!video.videoHeight)return;
  previewBusy=true;const serial=previewSerial;
  try{
    const canvas=document.createElement('canvas');canvas.width=192;canvas.height=108;
    const ctx=canvas.getContext('2d'),scale=Math.min(192/video.videoWidth,108/video.videoHeight),w=video.videoWidth*scale,h=video.videoHeight*scale;
    ctx.fillStyle='#000';ctx.fillRect(0,0,192,108);ctx.drawImage(video,(192-w)/2,(108-h)/2,w,h);
    canvas.toBlob(blob=>{
      previewBusy=false;
      if(serial!==previewSerial||key!==timeline.key||!settings.scrubPreviews)return;
      if(!blob){previewFailedSource=key;return;}
      framePreviews.offer(key,timeMs,URL.createObjectURL(blob),blob.size);
    },'image/jpeg',.6);
  }catch(_){previewBusy=false;previewFailedSource=key;}
}
async function fetchSourcePreview(key,timeMs,signal){
  const state=timeline.state,native=session;
  if(!state||key!==timeline.key||!state.seekable||state.dvd||!native)throw Error('preview_unavailable');
  const controller=new AbortController(),abort=()=>controller.abort();signal.addEventListener('abort',abort,{once:true});
  if(signal.aborted)abort();
  const deadline=setTimeout(abort,8000);
  try{
    const body=new URLSearchParams({session:native,sourceGeneration:String(state.source.sourceGeneration),timeMs:String(Math.round(timeMs))});
    const response=await fetch(new URL('api/miniclient?action=sourcePreview',location.href),{method:'POST',body,cache:'no-store',signal:controller.signal});
    const position=response.headers.get('X-Vibe-Preview-Position-Ms'),length=Number(response.headers.get('Content-Length'));
    if(!response.ok||response.headers.get('Content-Type')!=='image/jpeg'||!position||!/^\d{1,12}$/.test(position)||length>32768||!response.body||!response.body.getReader)throw Error('preview_unavailable');
    const reader=response.body.getReader(),chunks=[];let bytes=0;
    try{while(true){const read=await reader.read();if(read.done)break;bytes+=read.value.byteLength;if(bytes>32768){controller.abort();throw Error('preview_unavailable');}chunks.push(read.value);}}
    finally{reader.releaseLock();}
    if(signal.aborted||key!==timeline.key||native!==session)throw Error('preview_source_changed');
    const blob=new Blob(chunks,{type:'image/jpeg'});return{timeMs:Number(position),bytes:blob.size,url:URL.createObjectURL(blob)};
  }finally{clearTimeout(deadline);signal.removeEventListener('abort',abort);}
}
window.addEventListener('pagehide',()=>sourcePreviews.begin(''));
function refreshTimelineMarkers(){
  if(markerBusy)return;
  const state=timeline.state,key=timeline.key;
  if(!state||!key||markerKey===key)return;
  markerKey=key;markerRows=[];
  if(!state.seekable||state.dvd||!Number.isInteger(state.mediaId)||state.mediaId<=0){markerStatus='Chapters/Comskip unavailable for this source';return;}
  markerBusy=true;markerStatus='Reading available Comskip markers…';
  requestJson('api/commercials','read',{id:state.mediaId},'GET',3000).then(reply=>{
    if(key!==timeline.key)return;
    markerRows=(Array.isArray(reply.markers)?reply.markers:[]).slice(0,128).filter(m=>Number.isFinite(m.start)&&Number.isFinite(m.end)&&m.start>=0&&m.end>m.start&&[0,3].includes(m.type));
    markerStatus=reply.available?markerRows.length+' Comskip regions; chapter metadata unavailable':'No Comskip/chapter markers available';
  }).catch(()=>{if(key===timeline.key)markerStatus='Markers unavailable; native controls unchanged';})
    .finally(()=>{markerBusy=false;if(key!==timeline.key)refreshTimelineMarkers();});
}
function updateTimelineExtras(model){
  sourcePreviews.begin(settings.scrubPreviews?timeline.key:'');
  if(framePreviews.key!==timeline.key){previewSerial++;framePreviews.begin(timeline.key);sourcePreviews.begin(timeline.key);previewFailedSource='';markerRows=[];if(!timeline.key){markerKey='';markerStatus='Markers unavailable';}}
  if(!settings.scrubPreviews&&framePreviews.entries.length){previewSerial++;framePreviews.begin('');framePreviews.begin(timeline.key);}
  refreshTimelineMarkers();
  const markers=$('timelineMarkers'),duration=Number(model.end)||0;
  const signature=markerKey+':'+duration+':'+markerRows.length;
  if(markers.dataset.rendered!==signature){
    markers.replaceChildren();markers.dataset.rendered=signature;
    if(duration>0)for(const marker of markerRows){
      const start=Math.min(duration,marker.start*1000),end=Math.min(duration,marker.end*1000);
      if(end<=start)continue;const region=document.createElement('span');region.style.left=(start/duration*100)+'%';region.style.width=((end-start)/duration*100)+'%';
      region.title='Comskip '+Core.timeText(start)+'–'+Core.timeText(end);markers.appendChild(region);
    }
  }
  $('timelineMarkerStatus').textContent=markerStatus;
  const preview=model.phase==='preview'&&settings.scrubPreviews?framePreviews.nearest(timeline.key,model.requested):null;
  $('timelinePreview').hidden=!preview;
  if(preview){const img=$('timelinePreviewImage');if(img.getAttribute('src')!==preview.url)img.src=preview.url;
    $('timelinePreviewLabel').textContent=(preview.kind==='source'?'Source preview at ':'Previously viewed at ')+Core.timeText(preview.timeMs)+' (not a new seek)';}
  else $('timelinePreviewImage').removeAttribute('src');
}
function updateDiagnosticGauges(snap){
  const st=snap.status||{},e=st.streamSettings&&st.streamSettings.effective||{};
  const runtime=timeline.state&&timeline.state.runtimeBitrateControl;
  const rate=Number(runtime&&runtime.available?runtime.appliedKbps:e.videoTargetKbps);
  const known=!!snap.id&&snap.firstFrameMs!=null,buffer=known?Number(snap.ahead):NaN;
  const target=Number(snap.bufferTargetSeconds)||Number(snap.configuredBufferSeconds)||0;
  const published=known&&snap.statusAgeMs!==null&&snap.statusAgeMs<=10000?Number(st.hlsSeconds)-Number(snap.localTimeSeconds):NaN;
  const maximum=Number(streaming.videoKbps),minimum=Math.min(settings.adaptiveMinimumKbps,maximum);
  const rows=[
    ['Browser buffer',buffer,0,target,Number.isFinite(buffer)?buffer.toFixed(1)+'s / '+target+'s '+(snap.bufferTargetSeconds?'target':'configured reference'):'Unavailable'],
    ['Server published reserve',published,0,Math.max(30,target),Number.isFinite(published)?Math.max(0,published).toFixed(1)+'s ahead (scale '+Math.max(30,target)+'s)':'Unavailable'],
    ['Video bitrate target',known&&Number.isFinite(rate)&&rate>0?rate:NaN,settings.adaptiveQuality?minimum:0,maximum,
      known&&Number.isFinite(rate)&&rate>0?rate+' kbps · '+(settings.adaptiveQuality?'Adjusted '+minimum+'–'+maximum:'Fixed maximum '+maximum)+' kbps':'Unavailable / video copy']
  ];
  for(const id of ['statsGauges','diagnosticGauges']){
    const root=$(id);if(!root)continue;root.replaceChildren();
    for(const [name,value,min,max,text] of rows){
      const row=document.createElement('div');row.className='mc-gauge';
      const label=document.createElement('span');label.textContent=name;row.append(label);
      if(Number.isFinite(value)&&max>0){const bar=document.createElement('meter');bar.min=min;bar.max=Math.max(min+1,max);bar.value=Math.max(min,Math.min(bar.max,value));bar.setAttribute('aria-label',name);bar.setAttribute('aria-valuetext',text);row.append(bar);}
      else {const missing=document.createElement('span');missing.textContent='Unavailable';row.append(missing);}
      const detail=document.createElement('small');detail.textContent=text;row.append(detail);root.append(row);
    }
    const note=document.createElement('small');note.textContent='Adjustment: '+qualityAdvisor.reason+'. Targets/reserve are not measured network bandwidth. Browser CPU/decoder load is not exposed.';root.append(note);
  }
}
function updateStats(){
  updateWatchLive();
  refreshDvdPresentation();
  updateBrowserRate();
  const snap=playback.snapshot(),st=snap.status||{};
  updateQualityRecommendation(snap);
  statsEl.hidden=!settings.showStatsInfo;$('statsGauges').hidden=!settings.showStats;$('statsPanel').hidden=!(settings.showStats||settings.showStatsInfo);$('autoplayBtn').hidden=!snap.blocked;
  updateDiagnosticGauges(snap);
  const phase=snap.recovering?'recovering':snap.paused?'paused':snap.rebuffering?'buffering':snap.starting?'starting':snap.id?'playing':'idle';
  $('bufferStatus').textContent=snap.id?snap.ahead.toFixed(1)+'s buffer · '+phase:'';
  const produced=Number(st.hlsSeconds)||0,relative=Math.max(0,snap.timeMs/1000-snap.startSeconds),serverAhead=Math.max(0,produced-relative);
  const targetText=snap.hlsVersion||snap.workerEnabled?snap.bufferTargetSeconds+'s target':'browser-managed target';
  const threads=st.threading||{},threadText=key=>threads[key]?'active':'idle';
  const ranges=[];try{for(let i=0;i<Math.min(video.buffered.length,6);i++)ranges.push(video.buffered.start(i).toFixed(1)+'–'+video.buffered.end(i).toFixed(1));}catch(_){}
  statsEl.textContent=`MiniClient 3.3.0 · ${uiW}×${uiH} native → ${Math.round(displayRect.width)}×${Math.round(displayRect.height)} displayed · ${phase}\n`+
    `Time ${Core.timeText(snap.timeMs)} / ${Core.timeText(snap.durationMs)} · browser ahead ${snap.ahead.toFixed(1)}s / ${targetText} · ${snap.bufferPhase} · browser speed ${Number(video.playbackRate)||1}×\n`+
    `Server ahead ${serverAhead.toFixed(1)}s · produced ${produced.toFixed(1)}s · segments ${st.segments||0} · fill ${Number(st.recentFillRate||0).toFixed(2)}× recent / ${Number(st.hlsFillRate||0).toFixed(2)}× average\n`+
    `FFmpeg ${st.encoder||'—'} · ${st.encoder==='copy'?'video copied (no encoding/decoding)':(st.hardware?'hardware':'software')+' encode / '+(st.hardwareDecode?'hardware':'software')+' decode'+(st.decodeAccelerator?' ('+st.decodeAccelerator+')':'')+' / '+(st.hardwareFilters?'hardware':'software')+' filters'} · ${st.inputMode||'—'}\n`+
    `First segment ${st.firstSegmentMs==null?'—':(st.firstSegmentMs/1000).toFixed(2)+'s'} · first progress ${snap.firstFrameMs==null?'—':(snap.firstFrameMs/1000).toFixed(2)+'s'} · recoveries ${snap.recoveries}/6\n`+
    `Startup metadata ${st.sourceProbeMs==null?'—':st.sourceProbeMs+'ms'}${st.sourceProbeCacheHit?' (reused)':''} · ready ${snap.startupTiming&&snap.startupTiming.readyObservedMs!=null?snap.startupTiming.readyObservedMs+'ms':'—'} · library ${snap.startupTiming&&snap.startupTiming.libraryWaitMs!=null?snap.startupTiming.libraryWaitMs+'ms':'—'} · attach ${snap.startupTiming&&snap.startupTiming.attachedMs!=null?snap.startupTiming.attachedMs+'ms':'—'}\n`+
    `Frames ${frame} · GFX ${gfxCount} · images ${images.size} · video ${video.videoWidth||0}×${video.videoHeight||0} · ranges ${ranges.join(', ')||'none'}\n`+
    `STV input ${renderPerformance.inputActionLast||'—'} HTTP ${renderPerformance.inputAcks?renderPerformance.inputAckMsLast.toFixed(0)+'ms':'—'} · send queue ${renderPerformance.inputQueueMsLast.toFixed(0)}ms · frame queue ${renderPerformance.presentedFrames?renderPerformance.frameQueueMsLast.toFixed(0)+'ms':'—'} · image decode max ${renderPerformance.imageDecodeMsMax.toFixed(0)}ms · queued ${renderQueued}\n`+
    `STV events ${Core.eventDelivery(window)} · read pauses ${renderPerformance.eventReadPauses} · longest ${renderPerformance.eventReadPauseMsMax.toFixed(0)}ms\n`+
    `Loader ${snap.loaderWakeups} refill wakeups · ${snap.transport==='mpegts'?'mpegts.js '+snap.tsVersion:'HLS '+(snap.hlsVersion||'native')} · worker request ${snap.workerRequested?'on':'off'} · observed ${snap.workerObserved} · MSE ${snap.transport==='mpegts'?(snap.mseWorkerRequested?'worker requested':'main thread'):'browser-managed'} · GFX main thread (time-sliced)\n`+
    `Producer monitor ${threadText('producerMonitor')} · feeder ${threadText('feeder')} · stderr ${threadText('stderrReader')} · last segment ${st.lastSegmentAgeMs==null?'—':(st.lastSegmentAgeMs/1000).toFixed(1)+'s ago'}\n`+
    `Producer ${st.running?'running':'stopped'} · ENDLIST ${!!st.endList} · ${st.activeRecording?'growing recording':'recorded media'}`+
    `\nAudio ${(st.streamSettings&&st.streamSettings.effective&&st.streamSettings.effective.audio)||'—'} · local CC ${captions.snapshot().mode} · packets ${captions.snapshot().received}`+
    (lastError?'\n'+lastError:'');
  updateExperienceTimeline();
  const tm=timeline.model();statsEl.textContent+='\nTimeline '+tm.phase+' · accepted '+(tm.accepted==null?'unknown':Core.timeText(tm.accepted))+' · presented '+(tm.displayed==null?'unknown':Core.timeText(tm.displayed));
  $('timelineBuffer').textContent=`Browser ${snap.ahead.toFixed(1)}s / ${targetText} · server ${serverAhead.toFixed(1)}s ahead · ${st.encoder||'waiting for FFmpeg'}${st.activeRecording?' · recording is growing':''}`;
}
$('diagnosticsBtn').addEventListener('click',()=>openSettings('diagnostics',$('diagnosticsBtn')));
$('downloadReport').addEventListener('click',async()=>{const b=$('downloadReport');b.disabled=true;try{await downloadDiagnosticReport('manual-download');$('reportActionStatus').textContent='Report downloaded. Review it before sharing.';}catch(e){$('reportActionStatus').textContent=e.message;setError(e);}finally{b.disabled=false;}});
$('sendReportServer').addEventListener('click',async()=>{const b=$('sendReportServer');b.disabled=true;try{const out=await saveDiagnosticReportToServer('manual-server-export');$('reportActionStatus').textContent='Server export: '+out.state+(out.detail?' — '+out.detail:'');}catch(e){$('reportActionStatus').textContent=e.message;setError(e);}finally{refreshDiagnosticDestination().catch(()=>{});}});
let preparedShare=null;
const shareSupported=!!(navigator.share&&navigator.canShare&&window.isSecureContext);
$('shareReport').disabled=!shareSupported;$('shareReport').title=shareSupported?'Prepare, then tap again to open the device share sheet.':'File sharing requires HTTPS and browser support; use Download instead.';
$('shareReport').addEventListener('click',async()=>{
  const b=$('shareReport'),owner=session+':'+connectionGeneration;
  if(preparedShare&&preparedShare.owner===owner){
    const prepared=preparedShare;preparedShare=null;
    try{await navigator.share({files:[prepared.file],title:'SageTV Vibe diagnostic report'});$('reportActionStatus').textContent='Report shared.';}
    catch(error){$('reportActionStatus').textContent=error.name==='AbortError'?'Share cancelled.':'Share failed; use Download: '+error.message;}
    return;
  }
  b.disabled=true;try{
    const out=await fetchDiagnosticZip('manual-share',false);if(owner!==session+':'+connectionGeneration)return;
    const file=new File([out.blob],'SageTV-Vibe-diagnostics.zip',{type:'application/zip'});
    if(!navigator.canShare({files:[file]}))throw new Error('This browser cannot share ZIP files; use Download.');
    preparedShare={owner,file};$('reportActionStatus').textContent='Report ready. Tap Share report again to open your device share sheet.';
  }catch(error){$('reportActionStatus').textContent=error.message;}finally{b.disabled=!shareSupported;}
});
$('connectionDiagnosticsBtn').addEventListener('click',()=>downloadDiagnosticReport('connection-failure').catch(setError));
video.addEventListener('resize',layoutStage);
video.addEventListener('loadedmetadata',()=>{layoutStage();browserState();if(session)api('mediaUpdate',{session},'POST').catch(setError);});
video.addEventListener('timeupdate',()=>playback.progress());video.addEventListener('playing',()=>playback.promoteBuffer());video.addEventListener('canplay',()=>playback.maybePlay());
if('ResizeObserver' in window)new ResizeObserver(()=>{$('localCaptions').style.fontSize=Math.max(8,Math.min(36,videoBounds.clientHeight*.047))+'px';syncDvbCanvasLayout();}).observe(videoBounds);
video.addEventListener('volumechange',browserState);video.addEventListener('ended',()=>playback.ended().catch(setError));
window.addEventListener('resize',requestResize);if(window.visualViewport)window.visualViewport.addEventListener('resize',requestResize);if('ResizeObserver' in window)new ResizeObserver(requestResize).observe(stage);
function retirePageSession(reason){
  if(mobileDock)mobileDock.retire();
  clearInterval(stateTimer);clearTimeout(guideTimer);
  if(pageRetired)return;pageRetired=true;stopped=true;connectionGeneration++;gesture.cancel();touchGesture.cancel();clearRepeats();keyRepeat.cancel();if(eventController)eventController.abort();captions.stop();ordinarySubtitles.stop();dvdSpu.stop();playback.stop();
  const id=session;session='';log('Page session retired: '+reason);
  if(reason==='explicit-client-exit'){
    // The page remains open here. A queued beacon is not evidence that its
    // native sockets/UI were closed (observed on physical Safari). Stop only
    // this captured session once and expose the acknowledged outcome. A late
    // response cannot change a new Exit or Reconnect generation.
    const serial=++explicitExitGeneration,box=$('clientExitStatus');
    box.textContent=id?'Disconnecting from the server…':'No active server session.';
    const current=()=>explicitClientExit&&serial===explicitExitGeneration;
    if(id)requestJson('api/miniclient','stop',{session:id},'POST',5000).then(reply=>{
      if(reply.ok!==true)throw new Error('Server disconnect not confirmed');
      if(current())box.textContent='Server disconnect confirmed. You can close this app.';
    }).catch(error=>{
      if(!current())return;
      box.textContent=error.httpStatus===404?'Server disconnect confirmed: session already closed.':
        'Local playback stopped; server disconnect could not be confirmed. Reconnect will replace the old session.';
      log(error.httpStatus===404?'Explicit exit: session already closed':'Explicit exit: server disconnect unconfirmed');
    });
  }else if(id)try{navigator.sendBeacon(new URL('api/miniclient?action=stop',location.href),new URLSearchParams({session:id}));}catch(_){}
}
window.addEventListener('pagehide',()=>retirePageSession('pagehide'));
window.addEventListener('beforeunload',()=>retirePageSession('beforeunload'));
document.addEventListener('visibilitychange',()=>{if(document.hidden){foregroundPending=true;foregroundProbe++;}else recoverForeground();});
window.addEventListener('pageshow',()=>{if(pageRetired)foregroundPending=true;recoverForeground();});
if('serviceWorker' in navigator)navigator.serviceWorker.register('sw.js').then(reg=>reg.update()).catch(()=>{});
fillStreamingForm();applySettings();if(settings.renderOnly)setRenderOnly(true);setInterval(updateStats,750);refreshDiagnosticDestination().catch(()=>{});connect();
})();
