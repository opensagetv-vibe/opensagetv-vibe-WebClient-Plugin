/* Stock-compatible playback experience policy. No DOM, Core patches, guessed
 * STV pixels, or required Client Extension. Injectable I/O keeps the real
 * production state machines independently testable. */
(function(root,factory){
  if(typeof module==='object'&&module.exports)module.exports=factory();
  else root.SageMiniExperience=factory();
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const finite=value=>typeof value==='number'&&Number.isFinite(value);
  const sourceKey=state=>state&&state.source?String(state.source.sessionId)+':'+state.source.sourceGeneration:'';
  function dvdActionMessage(accepted,outcome){
    if(accepted===true)return 'DVD action accepted for the current owned load.';
    if(outcome==='unknown'||outcome==='pending')return 'DVD action acknowledgement was not confirmed. It may have taken effect; check playback before trying again. Native controls remain available.';
    return 'DVD action unavailable or load changed; native controls remain available.';
  }
  class Timeline {
    constructor(options){this.o=options;this.clock=options.clock||(()=>performance.now());this.serial=0;this.reset();}
    reset(){this.state=null;this.key='';this.intent=null;this.draft=null;this.displayed=null;this.history=[];this.producer='';}
    note(phase,detail){
      const previous=this.history[this.history.length-1];
      const id=this.intent&&this.intent.id||'';
      if(previous&&previous.phase===phase&&previous.requestId===id)return;
      this.history.push({phase,requestId:id,atMs:this.clock(),detail:detail||null});
      if(this.history.length>48)this.history.shift();
    }
    receive(state){
      if(!state||state.schemaVersion!==1||!sourceKey(state))return false;
      const key=sourceKey(state);
      if(this.state&&state.source.sessionId===this.state.source.sessionId&&
          Number(state.source.sourceGeneration)<Number(this.state.source.sourceGeneration))return false;
      if(key===this.key&&this.state&&Number(state.source.seekGeneration)<Number(this.state.source.seekGeneration))return false;
      // STV touches use the normal native SEEK, not this slider's request().
      // Retire the previous renderer observation as soon as that accepted
      // epoch/producer changes. Otherwise the local slider and diagnostics
      // keep showing the old picture's clock throughout replacement startup.
      // This does not draw or guess SageTV's own position marker.
      if(this.state&&(key!==this.key||state.producer!==this.producer||
          Number(state.source.seekGeneration)>Number(this.state.source.seekGeneration)))this.displayed=null;
      if(this.intent&&this.state&&key===this.key&&Number(state.source.seekGeneration)>Number(this.state.source.seekGeneration)&&state.requestId!==this.intent.id){this.note('superseded-by-native-control');this.intent=null;this.draft=null;}
      if(this.key&&this.key!==key){this.intent=null;this.draft=null;this.displayed=null;this.history=[];}
      this.key=key;this.state=state;this.producer=state.producer||'';
      if(this.intent&&state.requestId===this.intent.id){
        this.intent.accepted=state.acceptedPositionMs;
        // Periodic producer snapshots must not undo an observed video frame.
        // A new request/source or an actual failure still supersedes it.
        if(this.intent.phase!=='presented'||state.error||state.pending)
          this.intent.phase=state.error?'failed':state.pending?'preparing':state.producerReady?'waiting-for-browser':'waiting-for-segments';
        this.intent.error=state.error||null;this.note(this.intent.phase);
      }
      return true;
    }
    clamp(value){
      if(!this.state||!this.state.seekable||!finite(Number(value)))return null;
      return Math.max(this.state.seekStartMs,Math.min(this.state.seekEndMs,Number(value)));
    }
    preview(value){const target=this.clamp(value);if(target!==null)this.draft=target;return target;}
    cancelPreview(){this.draft=null;}
    async request(value){
      const target=this.clamp(value);if(target===null)return false;
      const key=this.key,state=this.state;
      // A source epoch guards intent; a changing HLS producer is not a source
      // change. A late HTTP acknowledgement cannot overwrite a newer request.
      const intent={id:'web_'+(++this.serial),target,accepted:null,phase:'sending',startedAt:this.clock(),error:null};
      this.intent=intent;this.draft=null;this.note('sending');if(this.o.changed)this.o.changed();
      try{
        const reply=await this.o.seek({requestId:intent.id,sourceGeneration:state.source.sourceGeneration,timeMs:target});
        if(this.intent!==intent||this.key!==key)return false;
        intent.ackMs=Math.max(0,this.clock()-intent.startedAt);
        if(!reply||reply.ok===false)throw new Error(reply&&reply.stale?'Recording changed; choose the position again.':'Seek was not accepted.');
        if(reply.state)this.receive(reply.state);
        return true;
      }catch(error){
        if(this.intent===intent&&this.key===key){intent.phase='failed';intent.error=String(error.message||error).slice(0,180);this.note('failed');}
        return false;
      }finally{if(this.o.changed)this.o.changed();}
    }
    presented(producer,timeMs){
      if(!this.state||this.state.pending||producer!==this.producer||!finite(timeMs)||timeMs<0)return;
      this.displayed=timeMs;
      const intent=this.intent;
      if(intent&&intent.phase!=='failed'&&this.state.requestId===intent.id&&!this.state.pending&&Math.abs(timeMs-Number(intent.accepted))<2000){
        if(intent.phase!=='presented'){intent.phase='presented';intent.presentedMs=this.clock()-intent.startedAt;this.note('presented');}
      }
    }
    model(){
      const s=this.state||{},i=this.intent;
      const actual=this.displayed!==null?this.displayed:s.displayedPositionMs;
      const accepted=i?i.accepted:finite(s.acceptedPositionMs)?s.acceptedPositionMs:null;
      const requested=i?i.target:finite(s.requestedPositionMs)?s.requestedPositionMs:null;
      const nativePending=!i&&!s.error&&(s.pending===true||
        (['waiting-for-browser','waiting-for-segments'].includes(s.phase)&&accepted!==null&&!finite(actual)));
      const pending=i?!['presented','failed'].includes(i.phase):nativePending;
      const phase=!i&&finite(actual)&&['waiting-for-browser','waiting-for-segments'].includes(s.phase)?
        (s.paused?'paused':'playing'):s.phase||'idle';
      return{seekable:!!s.seekable,dvd:!!s.dvd,start:s.seekStartMs,end:s.seekEndMs,liveEdge:s.liveEdgeMs,
        requested:this.draft!==null?this.draft:requested,accepted,displayed:actual,
        value:this.draft!==null?this.draft:pending?(i?i.target:accepted):finite(actual)?actual:s.reportedPositionMs||0,
        pending,phase:this.draft!==null?'preview':i?i.phase:phase,error:i&&i.error||s.error||null,
        producer:s.producer||'',source:this.key,requestId:i?i.id:null,
        timing:{requestToAckMs:i&&finite(i.ackMs)?i.ackMs:null,requestToPresentedMs:i&&finite(i.presentedMs)?i.presentedMs:null,
          producerPrepareMs:s.timing&&finite(s.timing.prepareMs)?s.timing.prepareMs:null,stockUiProcessedAtMs:null},history:this.history.slice()};
    }
  }
  // Original policy, kept equivalent to Android RuntimeQualityAdvisor. No
  // extra downloads/encoders; stale, cache-only or missing measurements abstain.
  class RuntimeQualityAdvisor {
    constructor(){this.reset();}
    reset(){this.key='';this.fast=this.slow=0;this.last=0;this.reserve=-1;this.highWater=0;this.cooldown=0;this.low=this.high=0;this.recommendation=null;this.sampleId=0;}
    appliedAt(now){this.cooldown=Math.max(this.cooldown,now+20000);this.low=this.high=0;this.recommendation=null;}
    observe(s){
      if(s.source!==this.key){this.reset();this.key=s.source;}
      if(!s.active||s.paused||(s.elementPaused&&!s.rebuffering)||s.starting||s.seeking||s.dvd||s.copy||!s.source){this.low=this.high=0;return this.recommendation=null;}
      if(!Number.isFinite(s.throughputKbps)||s.throughputKbps<=0||!Number.isFinite(s.ahead)||s.ahead<0||!Number.isFinite(s.videoKbps)||s.videoKbps<250||!Number.isFinite(s.ceilingKbps)||s.ceilingKbps<s.videoKbps)return this.recommendation=null;
      // Polling the same transfer repeatedly is not sustained bandwidth proof.
      if(!s.sampleId||s.sampleId===this.sampleId||this.last&&s.now-this.last<3000)return this.recommendation;
      this.sampleId=s.sampleId;
      if(this.last&&s.now-this.last>30000){this.fast=this.slow=0;this.low=this.high=0;this.reserve=-1;this.highWater=0;}
      const ms=s.ahead*1000,w=Math.max(.1,Math.min(10,(s.sampleMs||1000)/1000));
      this.fast=this.fast?this.fast*Math.pow(.5,w/3)+s.throughputKbps*(1-Math.pow(.5,w/3)):s.throughputKbps;
      this.slow=this.slow?this.slow*Math.pow(.5,w/10)+s.throughputKbps*(1-Math.pow(.5,w/10)):s.throughputKbps;
      const estimate=Math.min(this.fast,this.slow),falling=this.reserve>=0&&ms<this.reserve-250,stable=this.reserve<0||ms>=this.reserve-250;
      this.highWater=Math.max(this.highWater,ms);this.reserve=ms;this.last=s.now;
      this.low=(s.rebuffering||ms<5000||falling&&ms<10000)&&estimate<(s.videoKbps+192)*1.2?this.low+1:0;
      const next=Math.min(s.ceilingKbps,Math.floor(s.videoKbps*1.25/50)*50);
      this.high=!s.rebuffering&&stable&&ms>=Math.min(12000,Math.max(1000,this.highWater*.75))&&next>s.videoKbps&&estimate>(next+192)/.70?this.high+1:0;
      if(s.now<this.cooldown)return this.recommendation=null;
      let target=0,direction='down';
      if(this.low>=3){target=Math.max(250,Math.min(Math.floor(s.videoKbps*.75),Math.trunc((estimate*.75-192)/50)*50));if(target>=s.videoKbps*.85)target=0;}
      else if(this.high>=10){target=next;direction='up';}
      if(!target)return this.recommendation=null;
      this.cooldown=s.now+(direction==='up'?60000:20000);this.low=this.high=0;
      return this.recommendation={videoKbps:target,resolution:null,direction,reason:'Measured bandwidth and buffer trend; same encoder, fixed resolution.'};
    }
  }
  class QualityAdvisor {
    constructor(){this.reset();}
    reset(){this.key='';this.low=0;this.high=0;this.lastSample=0;this.cooldown=0;this.applied=0;this.recommendation=null;}
    observe(sample){
      if(sample.source!==this.key){this.reset();this.key=sample.source;}
      // The reserve gate pauses the video element while user intent remains
      // PLAY. That is precisely when a measured network downshift can help;
      // treating the internal pause as a user Pause disables recovery from
      // starvation. Explicit Pause/autoplay blockage stay ineligible. Never
      // use rebuffering as permission to invent a throughput measurement.
      const paused=sample.paused||(sample.elementPaused&&!sample.rebuffering);
      if(!sample.source||!sample.active||paused||sample.starting||sample.seeking||sample.dvd||sample.copy){this.low=0;this.high=0;this.recommendation=null;return null;}
      if(sample.now-this.lastSample<3000)return this.recommendation;
      this.lastSample=sample.now;
      // Use actual observed throughput only. Buffer starvation with adequate
      // delivery can be a decoder/producer problem, not insufficient bandwidth.
      const kbps=Number(sample.throughputKbps),target=Number(sample.videoKbps);
      if(!Number.isFinite(kbps)||kbps<=0||!Number.isFinite(target)||target<250){this.low=0;this.high=0;this.recommendation=null;return null;}
      const limited=kbps<(target+192)*1.25&&sample.ahead<5;
      this.low=limited?this.low+1:Math.max(0,this.low-1);
      // Increase much more slowly than a decrease: ten spaced body-transfer
      // samples,15s playable reserve and80% measured headroom. Missing native
      // HLS timing is never invented. Never exceed the saved user ceiling.
      const ceiling=Number(sample.ceilingKbps);
      const headroom=!sample.rebuffering&&Number.isFinite(ceiling)&&ceiling>target&&sample.ahead>=15&&kbps>(target+192)*1.8;
      this.high=headroom?this.high+1:0;
      if(this.high>=10&&sample.now>=this.cooldown&&this.applied<2){
        const raised=Math.min(ceiling,Math.floor(target*1.25/50)*50);
        if(raised>target){const height=raised<1000?480:raised<2500?720:1080;
          return this.recommendation={videoKbps:raised,resolution:String(Math.min(Number(sample.ceilingHeight)||height,height)),direction:'up',reason:'Sustained measured headroom and stable reserve; bounded recovery within the saved ceiling.'};}
      }
      if(this.low<3||sample.now<this.cooldown||this.applied>=2){this.recommendation=null;return null;}
      const bitrate=Math.max(250,Math.min(Math.floor(target*.7),Math.floor((kbps*.7-192)/50)*50));
      if(bitrate>=target*.85){this.recommendation=null;return null;}
      const resolution=bitrate<1000?'480':bitrate<2500?'720':null;
      return this.recommendation={videoKbps:bitrate,resolution,direction:'down',reason:'Observed delivery is below the active video target and the buffer remains low.'};
    }
    appliedAt(now){this.cooldown=now+60000;this.applied++;this.low=this.high=0;this.recommendation=null;}
    failedAt(now){this.cooldown=now+60000;this.low=this.high=0;this.recommendation=null;}
  }
  /** Reuses frames already decoded by this browser: no second encoder, media
   * seek, filesystem access or network request. Missing/unviewed times stay
   * unavailable. URLs are always retired on eviction/source replacement. */
  class FramePreviews {
    constructor(revoke){this.revoke=revoke;this.key='';this.entries=[];this.bytes=0;}
    begin(key){if(key===this.key)return;for(const e of this.entries)this.revoke(e.url);this.key=key;this.entries=[];this.bytes=0;}
    offer(key,timeMs,url,bytes,kind){
      if(!key||key!==this.key||!finite(timeMs)||timeMs<0||!Number.isFinite(bytes)||bytes<=0||bytes>32768||!String(url).startsWith('blob:')){this.revoke(url);return false;}
      const bucket=Math.floor(timeMs/10000),old=this.entries.find(e=>e.bucket===bucket);
      if(old){this.revoke(url);return false;}
      while(this.entries.length>=16||this.bytes+bytes>524288){const e=this.entries.shift();this.bytes-=e.bytes;this.revoke(e.url);}
      this.entries.push({bucket,timeMs,url,bytes,kind:kind==='source'?'source':'viewed'});this.bytes+=bytes;return true;
    }
    has(timeMs){return this.entries.some(e=>e.bucket===Math.floor(timeMs/10000));}
    nearest(key,timeMs){
      if(key!==this.key||!finite(timeMs))return null;
      let nearest=null;for(const e of this.entries)if(Math.abs(e.timeMs-timeMs)<=5000&&(!nearest||Math.abs(e.timeMs-timeMs)<Math.abs(nearest.timeMs-timeMs)))nearest=e;
      return nearest;
    }
    snapshot(){const sourceImages=this.entries.filter(e=>e.kind==='source').length;return{count:this.entries.length,bytes:this.bytes,source:this.key,
      method:sourceImages?'bounded-source-and-viewed-frames':'previously-decoded-browser-frame',sourceImages,futurePreviews:sourceImages>0};}
  }
  /** Explicit slider-input requests only. No timer, retry, work queue, seek or
   * playback producer. The existing frame cache owns all admitted blob URLs. */
  class SourcePreviews {
    constructor(options){this.o=options;this.key='';this.serial=0;this.busy=false;this.lastAt=-Infinity;this.bucket=null;this.controller=null;this.state='idle';}
    begin(key){if(key===this.key)return;this.serial++;this.key=key;this.bucket=null;this.lastAt=-Infinity;this.state='idle';if(this.controller)this.controller.abort();}
    async request(key,timeMs){
      const now=(this.o.clock||(()=>performance.now()))(),bucket=Math.floor(timeMs/10000);
      if(!key||key!==this.key||!finite(timeMs)||timeMs<0||timeMs>14*86400000||this.busy||bucket===this.bucket||now-this.lastAt<2000)return false;
      this.busy=true;this.bucket=bucket;this.lastAt=now;this.state='loading';
      const serial=this.serial,controller=new AbortController();this.controller=controller;let image=null;
      try{
        image=await this.o.fetch(key,timeMs,controller.signal);
        if(serial!==this.serial||key!==this.key||controller.signal.aborted){if(image&&image.url)this.o.revoke(image.url);image=null;return false;}
        if(!image||!finite(image.timeMs)||image.timeMs<0||image.timeMs>14*86400000||!Number.isFinite(image.bytes)||image.bytes<4||image.bytes>32768||!String(image.url).startsWith('blob:'))throw Error('preview_unavailable');
        const accepted=this.o.offer(key,image.timeMs,image.url,image.bytes,'source');image=null;this.state=accepted?'ready':'viewed-frame-retained';return accepted;
      }catch(_){if(image&&image.url)this.o.revoke(image.url);if(serial===this.serial)this.state='unavailable';return false;}
      finally{this.busy=false;if(this.controller===controller)this.controller=null;if(this.o.changed)this.o.changed();}
    }
    snapshot(){return{state:this.state,busy:this.busy,method:'explicit-shared-source-image',queued:0};}
  }
  return{Timeline,QualityAdvisor,RuntimeQualityAdvisor,FramePreviews,SourcePreviews,sourceKey,dvdActionMessage};
});
