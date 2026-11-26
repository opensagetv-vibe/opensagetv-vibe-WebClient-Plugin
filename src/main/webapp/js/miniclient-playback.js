/* Browser TS/HLS lifecycle for the real SageTV MiniClient. No DOM globals are
 * required: production dependencies are injected and used by the regression tests.
 */
(function(root, factory) {
  'use strict';
  if (typeof module === 'object' && module.exports) module.exports = factory(require('./miniclient-core.js'),require('./miniclient-streaming.js'));
  else root.SageMiniPlayback = factory(root.SageMiniCore,root.SageMiniStreaming);
})(typeof globalThis !== 'undefined' ? globalThis : this, function(Core, Streaming) {
  'use strict';
  class Playback {
    constructor(options) {
      this.o = options; this.video = options.video;
      this.clock = options.clock || {now: () => Date.now(), setTimeout: (fn, ms) => setTimeout(fn, ms), clearTimeout: id => clearTimeout(id)};
      this.generation = 0; this.hls = null; this.tsPlayer=null;this.transport='hls';this.streamSettings=null;this.tsStats=null;this.tsVersion='';this.tsFallbackPending=false;this.mpeg2FallbackPending=false; this.id = ''; this.status = null;
      this.statusReceivedAt=null;
      this.startSeconds = 0; this.durationMs = 0; this.intentPaused = false;
      this.rebuffering = false; this.blocked = false; this.recovering = false;
      this.attached = false; this.budget = new Core.RecoveryBudget(6);
      this.timer = null; this.inFlightStatus = null; this.lastError = '';
      this.startedAt = 0; this.firstFrameMs = null; this.lastTime = 0;
      this.readyObservedMs = null; this.attachedMs = null; this.libraryWaitMs = null; this.startupPolls = 0;
      this.lastPlayProgress = 0; this.lastProduced = 0; this.lastProduceProgress = 0;
      this.starvedAt = 0; this.localNetworkRetries = 0; this.localMediaRetries = 0;
      this.playPending = false; this.stopped = true; this.recoveryWaitUntil = 0;
      this.bufferPhase = 'startup'; this.bufferTargetSeconds = 6; this.hlsVersion = '';this.appliedBufferKey='';this.dvd=false;this.dvdGeneration=0;
      this.lastAppendAt = 0; this.lastLoadAt = 0; this.lastLoaderWake = 0;
      this.loaderWakeups = 0; this.fragmentLoading = false; this.quotaLimited = false;
      this.lastStableAbsoluteMs = 0; this.clockRegressions = 0; this.clockRegressionActive=false; this.lastFailureClass = '';
      this.lastInputBytes = 0; this.lastInputProgress = 0; this.lastDecodeProgress = 0;
      this.throughputKbps=null;this.throughputAt=0;this.throughputSamples=0;
      this.nativeDvdStartAlignmentAttempted=false;this.nativeDvdStartAlignedSeconds=null;
      this.nativeDvdStillFallbackAttempted=false;this.nativeDvdStillFallbackResult='';this.nativeDvdRemotePlaybackBefore=null;
      this.nativeDvdFeatureFallbackAttempted=false;this.nativeDvdFeatureFallbackResult='';this.nativeDvdFeatureResumeFloorMs=null;
      this.initialCopyGapAttempted=false;this.initialCopyGapAlignedSeconds=null;
      this.nativeHlsFallbackAttempted=false;this.nativeHlsFallbackPending=false;this.nativeHlsFallbackResult='';this.nativeHlsInitialResumeSeconds=0;
    }
    settings() { const s=Core.normalizeSettings(this.o.settings());if(this.dvd){s.startSegments=1;if(s.bufferPreset==='stable')s.bufferPreset='auto';}return s; }
    hlsConfig(steady) { const cfg=Core.hlsConfig(this.settings(),steady);if(this.dvd){const cap=steady?12:6;cfg.maxBufferLength=Math.min(cap,cfg.maxBufferLength);cfg.maxMaxBufferLength=Math.min(cap,cfg.maxMaxBufferLength);cfg.backBufferLength=Math.min(6,cfg.backBufferLength);cfg.liveBackBufferLength=Math.min(6,cfg.liveBackBufferLength);}return cfg; }
    valid(serial) { return serial === this.generation && !!this.id && !this.stopped; }
    notify(message) { if (this.o.message) this.o.message(message || ''); }
    error(error) { this.lastError = error && error.message ? error.message : String(error); if (this.o.error) this.o.error(this.lastError); }
    elementSnapshot() {
      // Passive browser evidence, not decoder/GPU attribution or proof that
      // currentTime was actually presented. Never export the media URL (which
      // may contain credentials), change playback, or let a transient range
      // read make the entire diagnostic download fail.
      const number=value=>typeof value==='number'&&Number.isFinite(value)?value:null;
      const count=value=>Number.isInteger(value)&&value>=0?value:null;
      const flag=value=>typeof value==='boolean'?value:null;
      const ranges=name=>{
        try{
          const source=this.video[name],length=source&&count(source.length);
          if(length==null)return {available:false,ranges:[]};
          const result={available:true,ranges:[],truncated:length>16};
          for(let i=0;i<Math.min(length,16);i++){
            const start=number(source.start(i)),end=number(source.end(i));
            if(start!==null&&end!==null&&start>=0&&end>=start)result.ranges.push([start,end]);
          }
          return result;
        }catch(_){return {available:false,ranges:[]};}
      };
      try{
        const v=this.video;let quality=null;
        try{if(typeof v.getVideoPlaybackQuality==='function'){const q=v.getVideoPlaybackQuality();quality={totalVideoFrames:count(q.totalVideoFrames),droppedVideoFrames:count(q.droppedVideoFrames)};}}catch(_){}
        return {available:true,currentTime:number(v.currentTime),duration:number(v.duration),
          readyState:count(v.readyState),networkState:count(v.networkState),
          paused:flag(v.paused),ended:flag(v.ended),seeking:flag(v.seeking),
          videoWidth:count(v.videoWidth),videoHeight:count(v.videoHeight),
          playbackRate:number(v.playbackRate),mediaErrorCode:v.error?count(v.error.code):null,
          buffered:ranges('buffered'),seekable:ranges('seekable'),played:ranges('played'),quality};
      }catch(_){return {available:false};}
    }
    snapshot() {
      return {id:this.id, status:this.status,statusAgeMs:this.statusReceivedAt===null?null:Math.max(0,this.clock.now()-this.statusReceivedAt),localTimeSeconds:Number(this.video.currentTime),transport:this.transport,streamSettings:this.streamSettings,tsStats:this.tsStats,tsVersion:this.tsVersion, startSeconds:this.startSeconds, durationMs:this.durationMs,
        timeMs:this.absoluteTime(), ahead:Core.bufferedAhead(this.video), paused:this.intentPaused,playbackRate:Number(this.video.playbackRate)||1,
        element:this.elementSnapshot(),
        browserEngine:this.tsPlayer?'MPEG-TS / MSE':this.hls?'HLS / MSE':this.attached?'Native HLS':'Not attached',
        browserDecoder:'Browser-managed (hardware/software not exposed)',
        rebuffering:this.rebuffering, blocked:this.blocked, recovering:this.recovering,
        recoveries:this.budget.count, firstFrameMs:this.firstFrameMs, error:this.lastError,
        network:{throughputKbps:this.throughputAt&&this.clock.now()-this.throughputAt<15000?this.throughputKbps:null,
          samples:this.throughputSamples,sampleId:this.throughputAt,sampleMs:this.throughputSampleMs||0,rawKbps:this.throughputRawKbps||null,method:this.hls?'fragment-body-transfer':'unavailable'},
        startupTiming:{readyObservedMs:this.readyObservedMs,attachedMs:this.attachedMs,libraryWaitMs:this.libraryWaitMs,polls:this.startupPolls},
        attached:this.attached, starting:!!this.id && !this.attached,
        dvd:this.dvd,dvdGeneration:this.dvdGeneration,
        nativeDvdStartAlignedSeconds:this.nativeDvdStartAlignedSeconds,
        nativeDvdStillFallbackAttempted:this.nativeDvdStillFallbackAttempted,
        nativeDvdStillFallbackResult:this.nativeDvdStillFallbackResult,
        nativeDvdFeatureFallbackAttempted:this.nativeDvdFeatureFallbackAttempted,
        nativeDvdFeatureFallbackResult:this.nativeDvdFeatureFallbackResult,
        nativeHlsFallbackResult:this.nativeHlsFallbackResult,
        initialCopyGapAlignedSeconds:this.initialCopyGapAlignedSeconds,
        bufferPhase:this.tsPlayer ? 'continuous reserve' : this.hls ? this.bufferPhase : 'browser-managed',
        bufferTargetSeconds:this.tsPlayer ? this.bufferTargetSeconds : this.hls ? Math.min(this.bufferTargetSeconds, Number(this.hls.config.maxMaxBufferLength)||this.bufferTargetSeconds) : 0,
        configuredBufferSeconds:this.settings().maxBufferSeconds, loaderWakeups:this.loaderWakeups,
        clockRegressions:this.clockRegressions,lastFailureClass:this.lastFailureClass,
        lastAppendAgeMs:this.lastAppendAt ? Math.max(0,this.clock.now()-this.lastAppendAt) : null,
        fragmentLoading:this.fragmentLoading, quotaLimited:this.quotaLimited,
        mseWorkerRequested:!!this.tsPlayer&&this.tsMseWorkerRequested===true,
        hlsVersion:this.hlsVersion, workerEnabled:!!this.tsPlayer||!!(this.hls && this.hls.config.enableWorker),
        workerRequested:!!this.tsPlayer||!!(this.hls && this.hls.config.enableWorker),
        workerObserved:this.tsPlayer?'not observable by mpegts.js API':this.hls?'not observable by hls.js API':'none'};
    }
    absoluteTime() {
      // A video element retains its previous currentTime until load() resets it.
      // During the new startup, report the new seek offset, not the old position.
      let computed=Math.max(0,Math.round((this.startSeconds+(this.attached?Number(this.video.currentTime)||0:0))*1000));
      // A same-producer decoder handoff retains the LAST ACTUALLY OBSERVED
      // clock while its new element attachment is cold, never a fabricated
      // forward position or a transient zero reported back to the DVD VM.
      if(this.nativeDvdFeatureResumeFloorMs!==null){
        if(computed<this.nativeDvdFeatureResumeFloorMs)computed=this.nativeDvdFeatureResumeFloorMs;
        else this.nativeDvdFeatureResumeFloorMs=null;
      }
      // Browser/MSE implementations can transiently report a stale pre-FLUSH or
      // pre-append timestamp. Reverse playback is not supported by this client,
      // so an unexplained >1.5 s regression inside one media generation is not
      // a real user seek. Keep the last proven clock until progress catches up.
      if(this.attached && computed+1500<this.lastStableAbsoluteMs && !this.video.seeking){
        if(!this.clockRegressionActive){this.clockRegressions++;this.clockRegressionActive=true;}return this.lastStableAbsoluteMs;
      }
      if(computed>this.lastStableAbsoluteMs||!this.attached)this.lastStableAbsoluteMs=computed;
      if(computed+1500>=this.lastStableAbsoluteMs)this.clockRegressionActive=false;
      return computed;
    }
    classifyFailure(reason,status){
      const text=String(reason||'').toLowerCase();
      if(/quota|buffer full|append/.test(text))return 'browser-quota';
      if(/network|loading|http|segment/.test(text))return 'transport';
      if(/decode|media error/.test(text))return 'browser-decode';
      if(/ffmpeg|encoder|transcod/.test(text))return 'encoder';
      if(/probe|metadata/.test(text))return 'probe';
      if(/source|input|read|producer/.test(text))return 'source-read';
      if(status&&status.running)return 'producer-stall';
      return 'unknown';
    }
    state() {
      return {expectedHlsSession:this.id, timeMs:this.absoluteTime(),playbackRevision:'web121.4',
        videoWidth:this.video.videoWidth || 0, videoHeight:this.video.videoHeight || 0,
        bufferAheadMs:Math.max(0,Math.round(Core.bufferedAhead(this.video)*1000)),
        readyState:Number(this.video.readyState)||0,networkState:Number(this.video.networkState)||0,
        seeking:!!this.video.seeking,elementPaused:!!this.video.paused,
        recoveryAttempts:this.budget.count,
        nativeBufferRepair:this.nativeBufferRepairAttempted===true,
        volume:this.video.volume, paused:this.intentPaused, ended:!!this.video.ended};
    }
    stop() {
      ++this.generation; this.stopped = true; this.attached = false;
      if (this.timer !== null) this.clock.clearTimeout(this.timer); this.timer = null;
      if (this.hls) { try { this.hls.destroy(); } catch (_) {} this.hls = null; }
      if(this.tsPlayer){try{this.tsPlayer.destroy();}catch(_){}this.tsPlayer=null;}
      this.tsStats=null;this.tsFallbackPending=false;this.mpeg2FallbackPending=false;
      this.id = ''; this.status = null; this.statusReceivedAt=null; this.inFlightStatus = null;this.dvd=false;this.dvdGeneration=0;
      this.nativeDvdStartAlignmentAttempted=false;this.nativeDvdStartAlignedSeconds=null;
      if(this.nativeDvdRemotePlaybackBefore!==null)this.video.disableRemotePlayback=this.nativeDvdRemotePlaybackBefore;
      this.nativeDvdRemotePlaybackBefore=null;this.nativeDvdStillFallbackAttempted=false;this.nativeDvdStillFallbackResult='';
      this.nativeDvdFeatureFallbackAttempted=false;this.nativeDvdFeatureFallbackResult='';this.nativeDvdFeatureResumeFloorMs=null;
      this.nativeHlsFallbackAttempted=false;this.nativeHlsFallbackPending=false;this.nativeHlsFallbackResult='';this.nativeHlsInitialResumeSeconds=0;
      this.throughputKbps=null;this.throughputAt=0;this.throughputSamples=0;
      this.rebuffering = false; this.recovering = false; this.playPending = false; this.recoveryWaitUntil = 0;
      try { this.video.pause(); this.video.removeAttribute('src'); this.video.load(); } catch (_) {}
    }
    async pollStatus(serial) {
      serial = serial == null ? this.generation : serial;
      if (!this.valid(serial)) return null;
      const id = this.id;
      if (this.inFlightStatus && this.inFlightStatus.serial === serial) return this.inFlightStatus.promise;
      const entry = {serial};
      entry.promise = (async () => {
        try {
          const st = await this.o.status(id);
          if (!this.valid(serial) || id !== this.id || (st.session && st.session !== id)) return null;
          this.status = st;
          this.statusReceivedAt=this.clock.now();
          if (Number(st.durationMs) > 0) this.durationMs = Number(st.durationMs);
          const produced = Number(st.hlsSeconds) || 0;
          if (produced > this.lastProduced + 0.1) {
            this.lastProduced = produced; this.lastProduceProgress = this.lastDecodeProgress = this.clock.now();
          }
          const inputBytes=Number(st.bytesInput)||0;
          if(inputBytes>this.lastInputBytes){this.lastInputBytes=inputBytes;this.lastInputProgress=this.clock.now();}
          if (st.error) this.error(st.error);
          return st;
        } catch (e) { if (this.valid(serial)) this.error(e); return null; }
        finally { if (this.inFlightStatus === entry) this.inFlightStatus = null; }
      })();
      this.inFlightStatus = entry;
      return entry.promise;
    }
    async waitServerBuffer(serial) {
      const deadline = this.clock.now() + 45000;
      while (this.valid(serial) && this.clock.now() < deadline) {
        this.startupPolls++;
        const st = await this.pollStatus(serial);
        if (!this.valid(serial)) return false;
        if (st) {
          this.notify('Starting video… ' + (Number(st.hlsSeconds) || 0).toFixed(1) + 's produced · ' +
            (st.segments || 0) + '/' + Core.requiredStartSegments(st, this.settings()) + ' segments');
          if (Core.startupReady(st, this.settings())) {this.readyObservedMs=this.clock.now()-this.startedAt;return true;}
          if (!st.running && st.error && st.producerPreparing!==true) throw new Error(st.error);
        }
        // WEB-046: serialize a short, bounded initial discovery phase. Keep
        // the45s deadline/late250ms cadence and never overlap requests or
        // reduce rebuffer reserve to make the first picture look faster.
        const delay=this.clock.now()-this.startedAt<5000?100:250;
        await new Promise(resolve => this.clock.setTimeout(resolve, delay));
      }
      if (!this.valid(serial)) return false;
      throw new Error('No playable HLS startup buffer after 45 seconds. Check FFmpeg in Diagnostics.');
    }
    async start(event, nativeDvdStillMse, nativeDvdFeatureMse, nativeHlsMse) {
      const keepPaused = (event.seek || event.recovery) ? this.intentPaused : !!event.paused;
      this.stop(); this.stopped = false;
      const forceMse=nativeDvdStillMse===true||nativeDvdFeatureMse===true||nativeHlsMse===true;
      const serial = this.generation;
      this.id = String(event.hlsSession || '');this.dvd=!!event.dvd;this.dvdGeneration=Number(event.dvdGeneration)||0;
      this.nativeBufferRepairAttempted=event.nativeBufferRepair===true;
      this.nativeDvdStillFallbackAttempted=nativeDvdStillMse===true;
      this.nativeDvdStillFallbackResult=nativeDvdStillMse===true?'attaching':'';
      this.nativeDvdFeatureFallbackAttempted=nativeDvdFeatureMse===true;
      this.nativeDvdFeatureFallbackResult=nativeDvdFeatureMse===true?'attaching':'';
      this.nativeHlsFallbackAttempted=nativeHlsMse===true;this.nativeHlsFallbackResult=nativeHlsMse===true?'attaching':'';
      if(forceMse&&'disableRemotePlayback' in this.video){
        this.nativeDvdRemotePlaybackBefore=this.video.disableRemotePlayback;
        this.video.disableRemotePlayback=true; // required for iPhone ManagedMediaSource
      }
      this.startSeconds = Math.max(0, Number(event.startSeconds) || 0);
      // Reusing a still-live previous representation after an aborted handoff
      // must resume within it, not replay its original zero timestamp. This
      // is a browser-local media offset, distinct from the source anchor.
      this.resumeSeconds=Math.max(0,Math.min(14*86400,Number(event.resumeSeconds)||0));
      this.nativeHlsInitialResumeSeconds=this.resumeSeconds;
      if(nativeDvdFeatureMse===true)this.nativeDvdFeatureResumeFloorMs=Math.round((this.startSeconds+this.resumeSeconds)*1000);
      this.durationMs = Math.max(0, Number(event.durationMs) || 0);
      this.intentPaused = keepPaused; this.blocked = false; this.lastError = '';
      if (!event.recovery) { this.budget.reset(); this.localNetworkRetries = 0; this.localMediaRetries = 0; }
      this.lastTime = 0; this.lastProduced = 0; this.starvedAt = 0;
      this.lastStableAbsoluteMs=Math.round(this.startSeconds*1000);this.clockRegressions=0;this.clockRegressionActive=false;this.lastFailureClass='';
      if(event.nativeBufferRepair===true)this.lastStableAbsoluteMs=Math.round((this.startSeconds+this.resumeSeconds)*1000);
      this.lastInputBytes=0;this.lastInputProgress=this.lastDecodeProgress=this.clock.now();
      this.startedAt = this.lastPlayProgress = this.lastProduceProgress = this.clock.now();
      this.initialCopyGapAttempted=false;this.initialCopyGapAlignedSeconds=null;
      this.firstFrameMs = null;this.bufferPhase='startup';this.bufferTargetSeconds=6;
      this.readyObservedMs=null;this.attachedMs=null;this.libraryWaitMs=null;this.startupPolls=0;
      this.lastAppendAt=this.lastLoadAt=this.lastLoaderWake=this.clock.now();
      this.loaderWakeups=0;this.fragmentLoading=false;this.quotaLimited=false;this.hlsVersion='';this.appliedBufferKey='';
      this.transport=event.transport||'hls';this.streamSettings=event.streamSettings||null;this.tsVersion='';
      if(this.transport==='mpegts'){await this.startTs(event,serial);return;}
      if (!this.id || !event.playlistUrl) { this.error('Missing HLS session or playlist URL'); return; }
      this.notify('Starting video…');
      // Fetch the local vendor asset concurrently with FFmpeg's first segment,
      // not after waiting for a fixed ten seconds of produced video.
      const requested=event.streamSettings&&event.streamSettings.requested||{};
      const nativePreferred=!forceMse&&(requested.player==='native'||((!requested.player||requested.player==='auto')&&
        (!!this.o.nativePreferred||requested.nativeHlsSupported===true||requested.nativeHlsSupported==='true')));
      const library = nativePreferred ? Promise.resolve(null) : Promise.resolve().then(() => this.o.loadHls()).catch(e => { return {loadError:e}; });
      try {
        if (!await this.waitServerBuffer(serial)) return;
        const libraryWaitStarted=this.clock.now();
        const Hls = await library;
        if (!this.valid(serial)) return; // also guard the asynchronous script load
        this.libraryWaitMs=this.clock.now()-libraryWaitStarted;
        const url = this.o.resolveUrl(event.playlistUrl);
        if (Hls && !Hls.loadError && Hls.isSupported()) {
          const instance = new Hls(Object.assign(this.hlsConfig(false),{startPosition:this.resumeSeconds})); this.hls = instance;this.hlsVersion=Hls.version||'';
          const active = () => this.valid(serial) && this.hls === instance;
          instance.on(Hls.Events.ERROR, (name, data) => {
            if (!active() || !data) return;
            this.error('HLS ' + (data.type || '') + ' ' + (data.details || ''));
            if (/frag.*(?:error|timeout)/i.test(data.details||'')) this.fragmentLoading=false;
            if (data.details==='bufferFullError') {
              // Do not re-expand a buffer that the browser just rejected. The
              // time target is a reserve goal, not permission to exhaust MSE RAM.
              this.quotaLimited=true;
              const cap=Math.max(6,Math.min(this.bufferTargetSeconds,instance.config.maxMaxBufferLength||this.bufferTargetSeconds)/2);
              instance.config.maxBufferLength=instance.config.maxMaxBufferLength=cap;
              this.bufferTargetSeconds=cap;
            }
            if (!data.fatal) return;
            if (data.type === Hls.ErrorTypes.NETWORK_ERROR && this.localNetworkRetries++ < 2) {
              try { instance.startLoad(Number(this.video.currentTime) || 0); } catch (e) { this.error(e); }
            } else if (data.type === Hls.ErrorTypes.MEDIA_ERROR && this.localMediaRetries++ < 2) {
              try { instance.recoverMediaError(); } catch (e) { this.error(e); }
            } else { this.recover('Fatal HLS error'); }
          });
          const listen=(event,fn)=>{if(event)instance.on(event,(name,data)=>{if(active())fn(data||{});});};
          listen(Hls.Events.FRAG_LOADING,()=>{this.fragmentLoading=true;this.lastLoadAt=this.clock.now();});
          listen(Hls.Events.FRAG_LOADED,data=>{
            this.fragmentLoading=false;this.lastLoadAt=this.clock.now();
            // Exclude time waiting for the producer's first byte. A slow
            // encoder is not proof of a slow WAN. Cached/tiny transfers and
            // missing native-HLS timing remain unavailable, never guessed.
            const stats=data.frag&&data.frag.stats,loading=stats&&stats.loading;
            const elapsed=loading?Number(loading.end)-Number(loading.first):0,bytes=stats&&Number(stats.loaded);
            if(elapsed>=100&&bytes>=16384&&Number.isFinite(bytes)){
              const kbps=bytes*8/elapsed;
              this.throughputRawKbps=kbps;this.throughputSampleMs=elapsed;
              this.throughputKbps=this.throughputKbps==null?kbps:this.throughputKbps*.6+kbps*.4;
              this.throughputAt=this.clock.now();this.throughputSamples++;
            }
          });
          listen(Hls.Events.FRAG_BUFFERED,()=>{
            this.fragmentLoading=false;this.lastAppendAt=this.clock.now();
            // One playable fragment is enough to start. From here the loader
            // keeps running toward the much larger independent reserve target.
            this.promoteBuffer();this.maybePlay();
          });
          instance.on(Hls.Events.MANIFEST_PARSED, () => { if (active()) this.maybePlay(); });
          instance.loadSource(url); this.attached = true; instance.attachMedia(this.video);
          // Explicit zero also applies to the loader, not only liveSync config.
          instance.startLoad(this.resumeSeconds);
        } else if (!forceMse&&this.video.canPlayType('application/vnd.apple.mpegurl')) {
          this.video.src = url; this.attached = true; this.video.load();
          if(this.resumeSeconds>0){
            const resume=()=>{if(this.valid(serial)){try{this.video.currentTime=this.resumeSeconds;this.resumeSeconds=0;}catch(e){this.error(e);}this.maybePlay();}};
            this.video.addEventListener('loadedmetadata',resume,{once:true});
          }
          this.maybePlay();
        } else {
          throw (Hls && Hls.loadError) || new Error('This browser has no supported HLS player');
        }
        if (this.valid(serial)) {if(nativeDvdStillMse===true)this.nativeDvdStillFallbackResult='attached';if(nativeDvdFeatureMse===true)this.nativeDvdFeatureFallbackResult='attached';if(nativeHlsMse===true)this.nativeHlsFallbackResult='attached';this.attachedMs=this.clock.now()-this.startedAt;this.scheduleHealth(serial);}
      } catch (e) {
        if (this.valid(serial)) {
          if(forceMse){
            if(nativeDvdStillMse===true)this.nativeDvdStillFallbackResult='failed';
            if(nativeDvdFeatureMse===true)this.nativeDvdFeatureFallbackResult='failed';
            if(nativeHlsMse===true)this.nativeHlsFallbackResult='failed';
            if(this.hls){try{this.hls.destroy();}catch(_){}this.hls=null;}
            this.attached=false;
            try{this.video.pause();this.video.removeAttribute('src');this.video.load();}catch(_){}
            if(this.nativeDvdRemotePlaybackBefore!==null)this.video.disableRemotePlayback=this.nativeDvdRemotePlaybackBefore;
            this.nativeDvdRemotePlaybackBefore=null;
          }
          this.error(e); this.notify('Playback failed: ' + this.lastError);
        }
      }
    }
    async startTs(event,serial) {
      try {
        if(!this.id||!event.streamUrl)throw new Error('Missing continuous-stream session URL');
        this.notify('Starting continuous MPEG-TS…');
        const library=await this.o.loadMpegts();
        if(!this.valid(serial))return;
        if(!library||!library.getFeatureList().mseLivePlayback)throw new Error('This browser has no compatible MPEG-TS/MSE player');
        const cfg=Streaming.mpegtsConfig(this.settings().maxBufferSeconds);
        this.tsMseWorkerRequested=cfg.enableWorkerForMSE===true;
        const instance=library.createPlayer({type:'mpegts',isLive:false,url:this.o.resolveUrl(event.streamUrl)},cfg);
        this.tsPlayer=instance;this.tsVersion=library.version||'1.8.0';this.bufferTargetSeconds=cfg.lazyLoadMaxDuration;
        const active=()=>this.valid(serial)&&this.tsPlayer===instance;
        instance.on(library.Events.ERROR,(type,detail,info)=>{
          if(!active())return;
          this.error('MPEG-TS '+type+' '+detail+(info&&info.msg?' '+info.msg:''));
          this.fallbackTs(this.lastError);
        });
        instance.on(library.Events.STATISTICS_INFO,data=>{if(active()){this.tsStats=data;this.lastLoadAt=this.clock.now();}});
        instance.on(library.Events.MEDIA_INFO,data=>{if(active()){this.tsMediaInfo=data;this.maybePlay();}});
        instance.attachMediaElement(this.video);this.attached=true;instance.load();this.maybePlay();
        this.scheduleHealth(serial);
      }catch(e){if(this.valid(serial)){this.error(e);await this.fallbackTs(this.lastError);}}
    }
    async fallbackTs(reason) {
      if(!this.id||this.tsFallbackPending||this.transport!=='mpegts'||this.stopped)return false;
      const decodeError=this.video.error;
      if(this.explicitVideoCopyActive()&&decodeError&&(decodeError.code===3||decodeError.code===4))
        return this.fallbackVideoCopy(reason);
      const requested=this.streamSettings&&this.streamSettings.requested||{};
      if(requested.allowFallback===false||requested.allowFallback==='false'||!this.o.fallback){
        this.intentPaused=true;this.video.pause();this.notify('MPEG-TS failed: '+reason+'. Automatic fallback is disabled.');return false;
      }
      const serial=this.generation,id=this.id;
      this.tsFallbackPending=true;this.recovering=true;
      this.notify('MPEG-TS fallback → HLS at '+Core.timeText(this.absoluteTime())+'…');
      try{
        const result=await this.o.fallback({timeMs:this.absoluteTime(),expectedHlsSession:id});
        if(this.valid(serial)) {
          if(result&&result.stale){this.error('Ignored stale MPEG-TS fallback');this.tsFallbackPending=false;}
          this.recovering=false;this.recoveryWaitUntil=this.clock.now()+10000;
        }
        return true;
      }catch(e){
        if(this.valid(serial)){this.recovering=false;this.error(e);this.intentPaused=true;this.video.pause();this.notify('Fallback failed: '+this.lastError);}
        return false;
      }
    }
    explicitVideoCopyActive() {
      const ss=this.streamSettings||{},requested=ss.requested||{},effective=ss.effective||{};
      return requested.videoMode==='copy'&&effective.video==='copy';
    }
    async fallbackVideoCopy(reason) {
      if(!this.id||this.mpeg2FallbackPending||!this.explicitVideoCopyActive()||this.stopped||this.intentPaused||this.blocked)return false;
      const requested=this.streamSettings&&this.streamSettings.requested||{};
      if(requested.allowFallback===false||requested.allowFallback==='false'||!this.o.fallback){
        this.intentPaused=true;this.video.pause();this.notify('Copied video was not decoded: '+reason+'. Automatic fallback is disabled.');return false;
      }
      const serial=this.generation,id=this.id;this.mpeg2FallbackPending=true;this.recovering=true;
      this.notify('Copied video is not decodable by this browser; restarting as H.264 at '+Core.timeText(this.absoluteTime())+'…');
      try{
        const params={timeMs:this.absoluteTime(),expectedHlsSession:id};
        if(this.transport==='mpegts')params.videoDecodeFailure=true;
        const result=await this.o.fallback(params);
        if(this.valid(serial)){
          if(result&&result.stale){this.error('Ignored stale Copy compatibility fallback');this.mpeg2FallbackPending=false;}
          this.recovering=false;this.recoveryWaitUntil=this.clock.now()+10000;
        }
        return true;
      }catch(e){
        if(this.valid(serial)){this.recovering=false;this.error(e);this.intentPaused=true;this.video.pause();this.notify('Copy compatibility fallback failed: '+this.lastError);}
        return false;
      }
    }
    promoteBuffer() {
      if (!this.hls || this.bufferPhase==='reserve') return;
      this.bufferPhase='reserve';this.updateBufferSettings();
    }
    updateBufferSettings() {
      if (!this.hls) return;
      // Only explicit settings changes / first-fragment promotion call this.
      // A periodic health check must NOT undo hls.js memory-pressure reductions.
      const settings=this.settings(),key=this.bufferPhase+':'+settings.maxBufferSeconds;
      if(key===this.appliedBufferKey)return;this.appliedBufferKey=key;
      const cfg=this.hlsConfig(this.bufferPhase==='reserve');
      if(this.quotaLimited) cfg.maxBufferLength=cfg.maxMaxBufferLength=Math.min(cfg.maxBufferLength,this.bufferTargetSeconds);
      Object.assign(this.hls.config,{
        maxBufferLength:cfg.maxBufferLength,maxMaxBufferLength:cfg.maxMaxBufferLength,
        backBufferLength:cfg.backBufferLength,liveBackBufferLength:cfg.liveBackBufferLength,
        maxBufferSize:cfg.maxBufferSize
      });
      this.bufferTargetSeconds=cfg.maxBufferLength;
      // hls.js runs its loader continuously; increasing its target is enough.
      // Do not startLoad() on every update: that aborts healthy fragment requests.
    }
    maintainBuffer(status) {
      if(!this.hls||!this.attached||this.recovering||this.stopped)return;
      const now=this.clock.now(),ahead=Core.bufferedAhead(this.video),relative=Number(this.video.currentTime)||0;
      if(ahead>0.25&&this.bufferPhase==='startup')this.promoteBuffer();
      const goal=Math.min(this.bufferTargetSeconds,Number(this.hls.config.maxMaxBufferLength)||this.bufferTargetSeconds);
      const available=Math.max(0,(Number(status&&status.hlsSeconds)||0)-relative);
      // Wake the loader BEFORE starvation, also while paused or autoplay-blocked.
      // A healthy in-flight fragment gets 20 s (the ordinary request timeout);
      // otherwise 8 s with no append is enough to detect stopped top-up.
      // A clean completed file can leave its final <1s fragment unappended.
      // The ordinary one-second top-up margin then suppresses every wakeup
      // while our reserve pause prevents EOF/caption retirement. A known,
      // source-duration-matching tail may wake the SAME hls.js loader with a
      // smaller margin; never restart the encoder, seek or manufacture ended.
      const completedTail=this.transport==='hls'&&!this.dvd&&status&&status.running===false&&status.endList===true&&
        status.activeRecording===false&&!status.error&&this.durationMs>0&&
        Math.abs((this.startSeconds+Number(status.hlsSeconds))*1000-this.durationMs)<=1000;
      const hasMore=available>ahead+(completedTail ? 0.25 : 1.0);
      // hls.js normally tops up continuously. A proven completed source whose
      // idle loader missed that top-up may be woken earlier near80% reserve.
      // Keep the same ceiling/quota cap and never abort a healthy in-flight
      // request, change native Safari buffering or infer unknown/live as VOD.
      const earlyRefill=!this.dvd&&status&&status.activeRecording===false&&ahead<goal*0.8;
      const idleWait=earlyRefill?2000:8000;
      if(!hasMore||ahead>=goal-1||now-this.lastAppendAt<idleWait||now-this.lastLoaderWake<8000)return;
      if(this.fragmentLoading&&now-this.lastLoadAt<20000)return;
      if(!this.fragmentLoading&&now-this.lastLoadAt<idleWait)return;
      this.lastLoaderWake=now;this.lastLoadAt=now;this.fragmentLoading=false;this.loaderWakeups++;
      this.error('Refill wakeup '+this.loaderWakeups+': browser '+ahead.toFixed(1)+'s / '+goal+'s; server '+available.toFixed(1)+'s');
      try{this.hls.startLoad(relative);}catch(e){this.error(e);}
    }
    maybePlay(userGesture) {
      if (!this.id || !this.attached || this.intentPaused || this.recovering || this.playPending) return;
      if (userGesture) this.blocked = false;
      if (this.blocked || this.rebuffering) return;
      const serial = this.generation;
      this.playPending = true;
      let p;
      try { p = this.video.play(); }
      catch (e) { p = Promise.reject(e); }
      Promise.resolve(p).then(() => {
        if (this.valid(serial)) this.notify('');
      }).catch(e => {
        if (!this.valid(serial)) return;
        // A seek/stop interrupts play() normally. It is not a decoder failure.
        if (e && e.name === 'AbortError') return;
        if (e && e.name === 'NotAllowedError') {
          this.blocked = true;
          this.notify('Browser blocked autoplay. Press the Play video button to start audio/video.');
        } else { this.error(e); }
      }).finally(() => { if (this.valid(serial)) this.playPending = false; });
    }
    control(action, value, userGesture) {
      if (action === 'play') {
        this.intentPaused = false; this.blocked = false;
        this.lastPlayProgress = this.clock.now(); this.starvedAt = 0;
        if (Core.bufferedAhead(this.video) >= Core.resumeTarget(this.settings(), this.status, this.video.currentTime)) this.rebuffering = false;
        this.maybePlay(userGesture);
      } else if (action === 'pause' || action === 'stop') {
        this.intentPaused = true; this.rebuffering = false; this.video.pause();
        if (action === 'stop') { this.stop(); this.notify(''); }
      } else if (action === 'mute') this.video.muted = !!value;
      else if (action === 'volume') this.video.volume = Math.max(0, Math.min(1, Number(value) || 0));
      else if (action === 'rate') {
        const rate = Number(value);
        if (rate >= 0.25 && rate <= 4) { try { this.video.playbackRate = rate; } catch (_) {} }
      } else if (action === 'flush' && this.hls) this.hls.startLoad(Number(this.video.currentTime) || 0);
    }
    progress() {
      if (!this.attached) return;
      const t = Number(this.video.currentTime) || 0;
      if (Math.abs(t - this.lastTime) >= 0.05) {
        this.lastTime = t; this.lastPlayProgress = this.clock.now(); this.starvedAt = 0;this.promoteBuffer();
        if (this.firstFrameMs === null && t > 0) this.firstFrameMs = this.clock.now() - this.startedAt;
      }
    }
    remotePlaybackActive(){
      try{return this.video.webkitCurrentPlaybackTargetIsWireless===true||!!(this.video.remote&&this.video.remote.state!=='disconnected');}
      catch(_){return true;} // Unknown remote ownership must not be disabled.
    }
    nativeDvdStillCandidate(serial,st) {
      const requested=this.streamSettings&&this.streamSettings.requested||{},v=this.video;
      return this.valid(serial)&&this.dvd&&this.attached&&!this.hls&&!this.tsPlayer&&!this.remotePlaybackActive()&&
        !this.intentPaused&&!this.blocked&&!this.recovering&&!this.rebuffering&&
        this.firstFrameMs===null&&this.clock.now()-this.startedAt>=1500&&
        this.o.dvdMenu&&this.o.dvdMenu()===true&&requested.allowFallback!==false&&
        st&&st.session===this.id&&st.playlistUrl==='hls/'+this.id+'/stream.m3u8'&&
        st.dvd===true&&Number(st.dvdGeneration)===this.dvdGeneration&&
        st.running===false&&st.endList===true&&st.activeRecording===false&&
        st.dvdConverterEnded===true&&st.exitCode===0&&st.segments===1&&
        Number(st.hlsSeconds)>0&&Number(st.hlsSeconds)<.1&&
        v.readyState===1&&v.videoWidth>0&&v.videoHeight>0&&v.ended===true&&
        !v.seeking&&!v.error&&Number.isFinite(v.duration)&&v.duration>0&&v.duration<=.001&&
        v.buffered&&v.buffered.length===0;
    }
    async tryNativeDvdStillMse(serial,st) {
      if(this.nativeDvdStillFallbackAttempted||!this.nativeDvdStillCandidate(serial,st))return false;
      // Safari can expose a finite one-picture TS menu as a1us metadata-only
      // stream with no decoded frame. The same bytes decode through HLS/MSE.
      // Change only this browser decoder once; never seek/recover/retranscode
      // the stock DVD source, inflate its duration or override pause/policy.
      this.nativeDvdStillFallbackAttempted=true;this.nativeDvdStillFallbackResult='loading';
      const id=this.id;
      let Hls;
      try{Hls=await this.o.loadHls();}catch(error){if(this.valid(serial))this.nativeDvdStillFallbackResult='unavailable';return false;}
      if(!this.valid(serial)||this.id!==id)return false;
      if(!this.nativeDvdStillCandidate(serial,this.status)) {this.nativeDvdStillFallbackResult='cancelled';return false;}
      if(!Hls||typeof Hls.isSupported!=='function'||!Hls.isSupported()) {this.nativeDvdStillFallbackResult='unavailable';return false;}
      await this.start({hlsSession:id,playlistUrl:st.playlistUrl,dvd:true,dvdGeneration:this.dvdGeneration,
        startSeconds:this.startSeconds,durationMs:this.durationMs,paused:this.intentPaused,
        streamSettings:this.streamSettings,recovery:true},true);
      return true;
    }
    nativeDvdFeatureCandidate(serial,st){
      const v=this.video,r=this.streamSettings&&this.streamSettings.requested||{},time=Number(v.currentTime),now=this.clock.now();
      return this.valid(serial)&&this.dvd&&this.attached&&!this.hls&&!this.tsPlayer&&!this.remotePlaybackActive()&&
        !this.intentPaused&&!this.blocked&&!this.recovering&&!v.paused&&!v.ended&&!v.seeking&&!v.error&&
        this.o.dvdMenu&&this.o.dvdMenu()===false&&this.firstFrameMs!==null&&
        this.starvedAt>0&&now-this.starvedAt>=12000&&now-this.lastPlayProgress>=12000&&
        r.allowFallback!==false&&r.allowFallback!=='false'&&
        st&&st.session===this.id&&st.playlistUrl==='hls/'+this.id+'/stream.m3u8'&&
        st.dvd===true&&Number(st.dvdGeneration)===this.dvdGeneration&&
        st.running===false&&st.endList===true&&st.activeRecording===false&&
        st.dvdConverterEnded===true&&st.exitCode===0&&st.segments>=2&&
        Number.isFinite(time)&&time>.1&&Number(st.hlsSeconds)-time>2&&
        v.readyState===2&&v.videoWidth>0&&v.videoHeight>0&&v.buffered&&v.buffered.length===0&&
        Number.isFinite(v.duration)&&v.duration>0&&Number(st.hlsSeconds)-v.duration>2;
    }
    nativeDvdStartupCandidate(serial,st){
      const v=this.video,r=this.streamSettings&&this.streamSettings.requested||{},time=Number(v.currentTime),now=this.clock.now();
      // WEB-099 physical Safari: play() accepted, readyState4 and14s of real
      // buffered media, but currentTime stays1us and no picture is presented.
      // The paced DVD producer correctly waits for consumption. Switch only
      // the browser decoder, not that healthy source/encoder or stock VM.
      return this.valid(serial)&&this.dvd&&this.attached&&!this.hls&&!this.tsPlayer&&!this.remotePlaybackActive()&&
        !this.intentPaused&&!this.blocked&&!this.recovering&&!v.paused&&!v.ended&&!v.seeking&&!v.error&&
        this.o.dvdMenu&&this.o.dvdMenu()===false&&this.firstFrameMs===null&&
        now-this.startedAt>=12000&&now-this.lastPlayProgress>=12000&&
        r.allowFallback!==false&&r.allowFallback!=='false'&&
        st&&st.session===this.id&&st.playlistUrl==='hls/'+this.id+'/stream.m3u8'&&
        st.dvd===true&&Number(st.dvdGeneration)===this.dvdGeneration&&
        st.running===true&&st.endList===false&&st.activeRecording===false&&st.dvdConverterEnded===false&&!st.error&&
        st.segments>=2&&Number(st.hlsSeconds)>=4&&Number.isFinite(time)&&time>=0&&time<.1&&
        v.readyState>=3&&v.videoWidth>0&&v.videoHeight>0&&Core.bufferedAhead(v)>=3;
    }
    async tryNativeDvdFeatureMse(serial,st){
      const candidate=s=>this.nativeDvdFeatureCandidate(serial,s)||this.nativeDvdStartupCandidate(serial,s);
      if(this.nativeDvdFeatureFallbackAttempted||!candidate(st))return false;
      this.nativeDvdFeatureFallbackAttempted=true;this.nativeDvdFeatureFallbackResult='loading';
      const id=this.id;let Hls;
      try{Hls=await this.o.loadHls();}catch(e){if(this.valid(serial))this.nativeDvdFeatureFallbackResult='unavailable';return false;}
      if(!this.valid(serial)||this.id!==id)return false;
      if(!candidate(this.status)){this.nativeDvdFeatureFallbackResult='cancelled';return false;}
      if(!Hls||typeof Hls.isSupported!=='function'||!Hls.isSupported()){this.nativeDvdFeatureFallbackResult='unavailable';return false;}
      const resume=Number(this.video.currentTime);
      // Same immutable producer/playlist and actual last observed position.
      // No encoder restart, native seek, invented EOS or extra playback stream.
      await this.start({hlsSession:id,playlistUrl:st.playlistUrl,dvd:true,dvdGeneration:this.dvdGeneration,
        startSeconds:this.startSeconds,durationMs:this.durationMs,resumeSeconds:resume,
        paused:this.intentPaused,streamSettings:this.streamSettings,recovery:true},false,true);
      return true;
    }
    scheduleHealth(serial) {
      if (!this.valid(serial)) return;
      this.timer = this.clock.setTimeout(async () => {
        this.timer = null;
        try { await this.hlsHealth(serial); } catch (e) { if (this.valid(serial)) this.error(e); }
        if (this.valid(serial)) this.scheduleHealth(serial);
      }, 750);
    }
    alignInitialCopyGap() {
      // Stream-copy can begin between AAC/video start samples. Pausing for a
      // reserve while currentTime precedes the first buffered range prevents
      // hls.js's playing-only gap controller from ever reaching that media.
      // Join one actually buffered sample within the initial second; never
      // move the file anchor, re-encode, fake a frame, or skip an ongoing gap.
      if(!this.hls||this.tsPlayer||this.dvd||!this.attached||this.stopped||this.recovering||this.initialCopyGapAttempted||
          !this.explicitVideoCopyActive()||this.intentPaused||this.blocked||this.resumeSeconds||
          this.video.readyState<2||!this.video.videoWidth||this.video.error||this.video.ended||this.video.seeking)return false;
      const time=Number(this.video.currentTime)||0,ranges=this.video.buffered;
      if(time<0||time>=1||!ranges||!ranges.length)return false;
      let start,end;try{start=ranges.start(0);end=ranges.end(0);}catch(_){return false;}
      const gap=start-time;
      if(!Number.isFinite(start)||!Number.isFinite(end)||start<=0||start>1||gap<=.25||gap>1||end-start<.25)return false;
      this.initialCopyGapAttempted=true;
      try{this.video.currentTime=start;this.initialCopyGapAlignedSeconds=start;}
      catch(error){this.error(error);return false;}
      this.rebuffering=false;this.starvedAt=0;this.maybePlay();return true;
    }
    nativeHlsMseCandidate(serial,st){
      const v=this.video,r=this.streamSettings&&this.streamSettings.requested||{};
      return this.valid(serial)&&this.transport==='hls'&&!this.dvd&&this.attached&&!this.hls&&!this.tsPlayer&&
        !this.remotePlaybackActive()&&!this.blocked&&!this.recovering&&!v.ended&&!v.seeking&&
        this.firstFrameMs===null&&v.error&&[3,4].includes(Number(v.error.code))&&
        r.allowFallback!==false&&r.allowFallback!=='false'&&
        st&&st.session===this.id&&st.dvd===false&&st.playlistReady===true&&
        st.playlistUrl==='hls/'+this.id+'/stream.m3u8';
    }
    async tryNativeHlsMse(serial,st){
      if(this.nativeHlsFallbackAttempted||!this.nativeHlsMseCandidate(serial,st))return false;
      this.nativeHlsFallbackAttempted=true;this.nativeHlsFallbackPending=true;this.nativeHlsFallbackResult='loading';
      const id=this.id;let Hls;
      try{
        try{Hls=await this.o.loadHls();}catch(e){
          if(this.valid(serial)&&this.id===id){this.nativeHlsFallbackResult='unavailable';this.error('Native HLS failed; browser MSE is unavailable.');this.notify(this.lastError);}
          return true;
        }
        if(!this.valid(serial)||this.id!==id)return false;
        if(!this.nativeHlsMseCandidate(serial,this.status)){this.nativeHlsFallbackResult='cancelled';return false;}
        if(!Hls||typeof Hls.isSupported!=='function'||!Hls.isSupported()){
          this.nativeHlsFallbackResult='unavailable';this.error('Native HLS failed; browser MSE is unsupported.');this.notify(this.lastError);return true;
        }
        // No frame was presented. Reuse the ORIGINAL attachment offset, never
        // an undecoded native timestamp, new encoder, or guessed file clock.
        await this.start({hlsSession:id,playlistUrl:st.playlistUrl,startSeconds:this.startSeconds,
          resumeSeconds:this.nativeHlsInitialResumeSeconds,durationMs:this.durationMs,
          paused:this.intentPaused,recovery:true,streamSettings:this.streamSettings},false,false,true);
        return true;
      }finally{if(this.valid(serial)&&this.id===id)this.nativeHlsFallbackPending=false;}
    }
    nativeBufferStallCandidate(serial,st){
      const v=this.video,now=this.clock.now(),t=Number(v.currentTime);
      return this.valid(serial)&&this.transport==='hls'&&!this.dvd&&this.attached&&!this.hls&&!this.tsPlayer&&
        !this.intentPaused&&!this.blocked&&!this.recovering&&!this.remotePlaybackActive()&&!v.seeking&&!v.error&&
        !v.ended&&this.firstFrameMs!==null&&Number.isFinite(t)&&t>.1&&now-this.lastPlayProgress>=12000&&
        Core.bufferedAhead(v)<.35&&st&&st.session===this.id&&st.dvd===false&&st.playlistReady===true&&
        st.playlistUrl==='hls/'+this.id+'/stream.m3u8'&&!st.error&&Number(st.hlsSeconds)-t>2;
    }
    async tryNativeBufferRepair(serial,st){
      if(!this.nativeBufferStallCandidate(serial,st))return false;
      if(this.nativeBufferRepairAttempted){
        // A second stuck attachment may use the existing bounded exact-position
        // recovery contract, never an unbounded native reload loop.
        if(this.clock.now()-this.startedAt>=20000)await this.recover('Native HLS stayed depleted after browser loader repair');
        return true;
      }
      const id=this.id,r=this.streamSettings&&this.streamSettings.requested||{};let Hls=null;
      if(r.allowFallback!==false&&r.allowFallback!=='false'){
        try{Hls=await this.o.loadHls();}catch(ignored){}
      }
      if(!this.valid(serial)||this.id!==id||!this.nativeBufferStallCandidate(serial,this.status))return false;
      const resume=Number(this.video.currentTime),mse=!!(Hls&&typeof Hls.isSupported==='function'&&Hls.isSupported());
      // Preserve the exact producer and ACTUAL displayed position, not live
      // edge, byte estimates or a new native Watch/Seek. Recheck after async
      // library loading so Stop/Pause/source/remote changes always win.
      await this.start({hlsSession:id,playlistUrl:st.playlistUrl,startSeconds:this.startSeconds,
        resumeSeconds:resume,durationMs:this.durationMs,paused:this.intentPaused,streamSettings:this.streamSettings,
        recovery:true,nativeBufferRepair:true},false,false,mse);
      return true;
    }
    async hlsHealth(serial) {
      serial = serial == null ? this.generation : serial;
      if (!this.valid(serial) || this.recovering || this.nativeHlsFallbackPending || this.clock.now() < this.recoveryWaitUntil) return;
      this.maintainBuffer(this.status);
      const st = await this.pollStatus(serial);
      if (!this.valid(serial) || !st || this.recovering) return;
      this.notifyPresentationEnd(serial,st);
      if(await this.tryNativeHlsMse(serial,st))return;
      if(!this.valid(serial)||this.nativeHlsFallbackResult==='unavailable'||this.nativeHlsFallbackResult==='failed')return;
      if(await this.tryNativeDvdStillMse(serial,st))return;
      if(!this.valid(serial))return;
      this.alignInitialCopyGap();
      // Safari may retain currentTime=0 after a native DVD FLUSH even when
      // its first actual buffered sample begins a few seconds later. Do not
      // wait forever before that range, or restart an already healthy encoder.
      // This is a one-shot new-generation native-DVD startup alignment only,
      // never an ongoing playback gap jump or replacement for an explicit seek.
      if(this.dvd && this.attached && !this.hls && !this.tsPlayer &&
          this.firstFrameMs===null && !this.intentPaused && !this.blocked &&
          !this.resumeSeconds && !this.nativeDvdStartAlignmentAttempted &&
          this.video.readyState>=2 && this.video.videoWidth>0){
        const ranges=this.video.buffered,time=Number(this.video.currentTime)||0;
        if(ranges&&ranges.length){
          const start=ranges.start(0),end=ranges.end(0);
          if(Number.isFinite(start)&&Number.isFinite(end)&&start>time+.1&&
              start>0&&start<=10&&end>start+.25&&time<.1){
            this.nativeDvdStartAlignmentAttempted=true;
            try{this.video.currentTime=start;this.nativeDvdStartAlignedSeconds=start;}
            catch(error){this.error(error);}
          }
        }
      }
      this.progress();this.maintainBuffer(st);
      if(await this.tryNativeBufferRepair(serial,st))return;
      if(!this.valid(serial))return;
      if(await this.tryNativeDvdFeatureMse(serial,st))return;
      if(!this.valid(serial))return;
      // Dimensions can be known from metadata even when the actual copied
      // bitstream is rejected. The no-dimensions watchdog alone misses this
      // case (observed on interlaced H.264). Reuse the same exact-source,
      // permission-aware compatibility fallback, never a restart of the same
      // undecodable Copy stream. Abort/network errors are not codec evidence.
      const copyError=this.video.error;
      if(this.explicitVideoCopyActive()&&!this.mpeg2FallbackPending&&!this.blocked&&!this.intentPaused&&
          copyError&&(copyError.code===3||copyError.code===4)){
        await this.fallbackVideoCopy('browser rejected copied video (MediaError '+copyError.code+')');return;
      }
      // A completed authored menu can intentionally retain its decoded picture
      // until a native DVD selection. It is not a feature rebuffer. Require
      // fresh current-generation menu truth from the owner, finite ENDLIST and
      // a real picture; unknown/stale/feature/running producers keep the normal
      // watchdogs. Do not fabricate progress, resume, freeze or restart media.
      if(this.dvd && this.o.dvdMenu && this.o.dvdMenu()===true &&
          st.running===false && st.endList===true && !st.activeRecording &&
          this.video.readyState>=2 && this.video.videoWidth>0){
        this.rebuffering=false;this.starvedAt=0;this.notify('');return;
      }
      if(this.explicitVideoCopyActive()&&!this.mpeg2FallbackPending&&!this.blocked&&!this.intentPaused&&
          this.clock.now()-this.startedAt>8000&&(Number(this.video.currentTime)||0)>0.5&&
          (!this.video.videoWidth||!this.video.videoHeight)){
        await this.fallbackVideoCopy('audio/timeline advanced but the browser produced no video dimensions');return;
      }
      if(this.transport==='mpegts' && !this.firstFrameMs && this.clock.now()-this.startedAt>45000 && !this.blocked && !this.intentPaused){await this.fallbackTs('No initial video progress after 45 seconds');return;}
      if (this.intentPaused || this.blocked) return;
      const now = this.clock.now(), ahead = Core.bufferedAhead(this.video);
      const relative = Number(this.video.currentTime) || 0;
      const producedAhead = Math.max(0, (Number(st.hlsSeconds) || 0) - relative);
      // A finite DVD cell / completed recording's EXTINF sum can exceed its
      // actual last samples. Ordinary recordings additionally require known
      // completed-source truth and a real tail within1s of the file duration;
      // ENDLIST alone must not hide truncated output or a growing-file stall.
      // Pausing the final <250ms to refill a rounded reserve prevents the
      // real ended event, and therefore native terminal/cell drain, forever.
      // Let the browser consume its own tail. Do not guess an ended state,
      // change its clock or mark native drain before actual consumption.
      const ranges=this.video.buffered;
      const tailEnd=ranges&&ranges.length?ranges.end(ranges.length-1):NaN;
      const completedRecordingTail=this.transport==='hls' && !this.dvd &&
        st.activeRecording===false && this.durationMs>0 &&
        Math.abs((this.startSeconds+tailEnd)*1000-this.durationMs)<=1000 &&
        !Core.incompleteEnd(st,relative,this.durationMs,this.startSeconds);
      const finiteMediaTail=(this.dvd||completedRecordingTail) && st.running===false && st.endList===true &&
        !st.activeRecording && this.video.readyState>=2 && this.video.videoWidth>0 &&
        !this.video.error &&
        Number.isFinite(tailEnd) && tailEnd>=relative && tailEnd-relative<=.25;
      if(finiteMediaTail && this.rebuffering){
        this.rebuffering=false;this.starvedAt=0;this.notify('');
        if(this.video.paused&&!this.video.ended)this.maybePlay();
      }
      if (ahead < 0.25 && !this.video.ended) {
        const nativeHls=this.transport==='hls'&&this.attached&&!this.hls&&!this.tsPlayer;
        // Native HLS owns its loader and buffered-range transitions. A decoded
        // HAVE_FUTURE_DATA gap is not permission for our MSE reserve policy to
        // pause Safari: that can prevent its own gap repair and tail drain.
        // Never change currentTime, manufacture ended, or override user intent.
        if(nativeHls && this.video.readyState>=3 && this.video.videoWidth>0 && !this.video.error){
          const internalRefill=this.rebuffering;
          this.rebuffering=false;this.starvedAt=0;
          if(internalRefill){this.notify('');if(this.video.paused)this.maybePlay();}
        }else{
          if (!this.starvedAt) this.starvedAt = now;
          if (!finiteMediaTail && (st.running || producedAhead > 0.5)) {
            this.rebuffering = true;
            if (!nativeHls && !this.video.paused) this.video.pause();
            this.notify('Buffering… browser ' + ahead.toFixed(1) + 's · server ahead ' + producedAhead.toFixed(1) + 's');
          }
        }
      }
      if (this.rebuffering && ahead >= Core.resumeTarget(this.settings(), st, relative)) {
        this.rebuffering = false; this.starvedAt = 0;
        this.maybePlay(); // intentPaused is checked, never an undefined `paused`
      } else if (!this.rebuffering && this.video.paused && !this.video.ended && ahead >= 0.25) this.maybePlay();
      const depleted = ahead < 0.35 && producedAhead < 1.5;
      if (depleted && Core.incompleteEnd(st, relative, this.durationMs, this.startSeconds)) {
        await this.recover('Producer ended before the expected media end'); return;
      }
      if (depleted && st.producerPreparing!==true && !st.running && !st.endList && now - this.lastProduceProgress > 3000) {
        await this.recover('FFmpeg stopped without completing its output'); return;
      }
      // If playable media already exists on the server, handle the browser
      // loader first. A producer waiting at a growing file's EOF is not proof
      // of producer failure, and restarting it discards a healthy reserve.
      if (this.starvedAt && now - this.starvedAt > 12000 && producedAhead > 2 && this.hls) {
        if(now-this.lastLoaderWake<3000)return; // let a proactive wakeup settle
        this.starvedAt = now;
        if (this.localNetworkRetries++ < 2) { this.lastLoaderWake=now;this.hls.startLoad(relative); }
        else await this.recover('Browser stopped loading available HLS segments');
        return;
      }
      if(this.transport==='mpegts'&&this.starvedAt&&now-this.starvedAt>15000&&producedAhead>2){
        await this.fallbackTs('MPEG-TS stopped buffering available server output');return;
      }
      // Producer recovery is reserved for no playable reserve AND no progress.
      // WEB-121: a live feeder proven to be at the physical writer's EOF has
      // no new bytes to decode. Keep its established PAT/GOP/decoder state;
      // replacing it at that empty tail can turn a temporary capture gap into
      // repeated metadata-only startups. Normal polling/follower growth and
      // stock physical-piece advance remain active, so refill resumes on input.
      const liveInputWait=st.activeRecording===true&&st.running===true&&st.streamHealth&&
        st.streamHealth.processAlive===true&&st.streamHealth.inputStage==='waiting-source';
      if(liveInputWait&&ahead<.35&&producedAhead<1.5){
        this.notify('Waiting for live source data… playback will resume when the recording grows.');return;
      }
      if (this.starvedAt && now - this.starvedAt > 12000 && now - this.lastProduceProgress > 12000 && now-this.lastInputProgress>12000 && st.running && producedAhead < 1.5) {
        await this.recover('FFmpeg stream stopped advancing with no source-read progress'); return;
      }
    }
    notifyPresentationEnd(serial,st) {
      // A real finite-file EOF can leave a last subtitle with a timeout beyond
      // the final video sample. Retire presentation only after independent
      // source/producer/end proof; never a temporary live tail or DVD cell.
      if(!this.valid(serial)||this.dvd||this.intentPaused||this.recovering||
          this.presentationEndGeneration===serial||!st||st.session!==this.id||
          st.activeRecording!==false||st.running!==false||st.endList!==true||st.exitCode!==0||
          this.video.ended!==true||this.video.error||st.error||this.video.readyState<2||
          !this.video.videoWidth||!Number.isFinite(this.firstFrameMs)||!(this.durationMs>0)||
          Math.abs(this.absoluteTime()-this.durationMs)>1000)return false;
      this.presentationEndGeneration=serial;
      if(this.o.presentationEnded)this.o.presentationEnded();
      return true;
    }
    async ended() {
      const serial = this.generation;
      if (!this.valid(serial) || this.intentPaused || this.recovering || this.clock.now() < this.recoveryWaitUntil) return;
      const st = await this.pollStatus(serial);
      if (!this.valid(serial)) return;
      if (st && Core.incompleteEnd(st, Number(this.video.currentTime) || 0, this.durationMs, this.startSeconds)) {
        await this.recover('Browser reached a premature HLS end');
      } else if (st && st.running) {
        // A temporary EVENT tail must continue loading; it is not media EOF.
        if (this.hls) this.hls.startLoad(Number(this.video.currentTime) || 0);
        this.maybePlay();
      } else {
        this.notifyPresentationEnd(serial,st);
        if(this.o.mediaUpdate)this.o.mediaUpdate();
      }
    }
    async recover(reason) {
      if (!this.id || this.recovering || this.stopped || this.clock.now() < this.recoveryWaitUntil) return false;
      // A dead DVD converter cannot be restarted by ordinary recording Seek:
      // stock DVD owns the MPEG-PS generation and its VM position. Repeating
      // that unsupported request only freezes the same picture six times.
      // Leave healthy/clean-drained DVD cells and stale status untouched.
      const st=this.status;
      if(this.dvd && st && st.session===this.id && st.dvd===true && st.running===false &&
          st.endList===false && Number.isInteger(st.exitCode) && st.exitCode!==0 && st.exitCode!==-2147483648){
        this.intentPaused=true;this.video.pause();
        this.error('DVD converter stopped (exit '+st.exitCode+'): '+(st.error||reason));
        this.notify('DVD converter stopped. Restart the title or choose another encoder in Streaming settings.');
        return false;
      }
      if (!this.budget.take()) {
        this.intentPaused = true; this.video.pause();
        this.notify('Playback recovery stopped after 6 attempts. Open Diagnostics or restart the recording.');
        return false;
      }
      const serial = this.generation, id = this.id, timeMs = this.absoluteTime();
      this.recovering = true;
      this.lastFailureClass=this.classifyFailure(reason,this.status);
      this.error('['+this.lastFailureClass+'] '+reason + ' (' + this.budget.count + '/' + this.budget.limit + ')');
      this.notify('Recovering playback at ' + Core.timeText(timeMs) + '…');
      try {
        // Position + expected HLS id travel in ONE request. A prior asynchronous
        // state report cannot race this seek or restart a newly selected video.
        const result = await this.o.recover({timeMs, expectedHlsSession:id});
        if (this.valid(serial)) {
          this.recovering = false;
          // videoStart may already have arrived on the event stream. Otherwise
          // let it arrive before the next starvation check can recover again.
          this.starvedAt = this.clock.now(); this.lastProduceProgress = this.clock.now();
          this.recoveryWaitUntil = this.clock.now() + (result && result.pending ? 30000 : 10000);
          if (result && result.stale) this.error('Ignored stale recovery after the media changed');
        }
        return true;
      } catch (e) {
        if (this.valid(serial)) {
          this.recovering = false; this.starvedAt = this.clock.now(); this.lastProduceProgress = this.clock.now();
          this.recoveryWaitUntil = this.clock.now() + 3000;
          this.error(e); this.notify('Recovery failed: ' + this.lastError);
        }
        return false;
      }
    }
  }
  return Playback;
});
