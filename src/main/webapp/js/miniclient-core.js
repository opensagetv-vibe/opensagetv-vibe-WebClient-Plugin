/* SageTV WebPlayer MiniClient shared policy / input state machines.
 * Behaviour ported from the user's Python HTML5 client v150; no Python runtime.
 * This module deliberately has no DOM dependencies, so the actual production
 * input and buffering rules can be exercised by the Node regression tests.
 */
(function(root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.SageMiniCore = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function() {
  'use strict';
  // Finite JSON responses avoid the affected iOS Fetch streaming path. This
  // selects only STV event delivery; media/HLS quality and decoder are separate.
  function eventDelivery(environment) {
    const n=environment.navigator||{};
    const ios=/iPhone|iPad|iPod/i.test(n.userAgent||'')||
      (n.platform==='MacIntel'&&Number(n.maxTouchPoints)>1);
    return ios||!environment.ReadableStream||!environment.TextDecoder?'long-poll':'stream';
  }
  const DEFAULTS = Object.freeze({
    bufferPreset: 'auto', startSegments: 0, maxBufferSeconds: 180, uiResolution: 'window',
    osdTrigger: 'left_long', clickMode: 'native', guideAssist: true,
    mouseBack: true, showStats: false, showStatsInfo: false, adaptiveQuality: false, adaptiveMinimumKbps: 250, scrubPreviews: false, renderOnly: false, videoMaskAssist: true,
    videoFit: 'cover', videoViewport: 'browser', displayPolicyVersion: 2, mute: false, fullscreenOnConnect: false,
    inputMode: 'remote', unifiedGraphics: false, autoDiagnosticCapture: false, saveDiagnosticsToServer: false
  });
  const ENUMS = {
    bufferPreset: ['auto', 'lowdelay', 'stable'],
    uiResolution: ['window', '1280x720', '1920x1080'],
    osdTrigger: ['left_long', 'right_long', 'left_double', 'right_double', 'center_click'],
    clickMode: ['native', 'press_release', 'double_select'],
    videoFit: ['source', 'cover', 'fill', 'zoom', '4x3', '16x9'],
    videoViewport: ['browser', 'native'],
    inputMode: ['remote', 'text']
  };
  function finite(value, fallback) {
    const n = Number(value); return Number.isFinite(n) ? n : fallback;
  }
  function normalizeSettings(value) {
    const source = value && typeof value === 'object' ? value : {};
    const result = Object.assign({}, DEFAULTS);
    Object.keys(DEFAULTS).forEach(k => {
      if (ENUMS[k]) {
        if (ENUMS[k].includes(source[k])) result[k] = source[k];
      } else if (typeof DEFAULTS[k] === 'boolean') {
        if (typeof source[k] === 'boolean') result[k] = source[k];
      }
    });
    result.startSegments = Math.round(Math.max(0, Math.min(10, finite(source.startSegments, 0))));
    result.maxBufferSeconds = Math.round(Math.max(30, Math.min(600, finite(source.maxBufferSeconds, 180))));
    result.adaptiveMinimumKbps = Math.round(Math.max(250,Math.min(50000,finite(source.adaptiveMinimumKbps,250))));
    // Legacy showStats enabled both text and graphs. Preserve that on upgrade;
    // subsequent independent choices retain explicit false values.
    if(typeof source.showStatsInfo!=='boolean')result.showStatsInfo=result.showStats;
    return result;
  }
  // Startup latency is independent of the forward reserve. A low measured
  // producer rate is not a reason to turn automatic startup into a long wait.
  function requiredStartSegments(status, settings) {
    const cfg = normalizeSettings(settings);
    if (cfg.startSegments > 0) return cfg.startSegments;
    return cfg.bufferPreset === 'stable' ? 3 : 1;
  }
  function startupReady(status, settings) {
    if (!status || !status.playlistReady || finite(status.segments, 0) < 1) return false;
    return !!status.endList || finite(status.segments, 0) >= requiredStartSegments(status, settings);
  }
  function hlsConfig(settings, steady) {
    const cfg = normalizeSettings(settings);
    const max = steady ? cfg.maxBufferSeconds : Math.min(6, cfg.maxBufferSeconds);
    return {
      lowLatencyMode: false, startPosition: 0,
      // EVENT is still live=true inside hls.js. A finite maximum live latency
      // would seek forward when a fast FFmpeg producer builds a large reserve.
      // Recording position belongs to SageTV/the viewer, NOT the producer edge.
      liveSyncDurationCount: 3, liveMaxLatencyDurationCount: Infinity,
      maxLiveSyncPlaybackRate: 1.0, initialLiveManifestSize: 1,
      maxBufferLength: max, maxMaxBufferLength: max,
      maxBufferSize: 128 * 1024 * 1024,
      backBufferLength: 30, liveBackBufferLength: 30,
      maxBufferHole: 0.5,
      fragLoadingMaxRetry: 8, manifestLoadingMaxRetry: 8, levelLoadingMaxRetry: 8,
      enableWorker: true
    };
  }
  function fitRect(width, height, uiWidth, uiHeight) {
    width=Math.max(1,finite(width,1));height=Math.max(1,finite(height,1));
    uiWidth=Math.max(1,finite(uiWidth,1280));uiHeight=Math.max(1,finite(uiHeight,720));
    const scale=Math.min(width/uiWidth,height/uiHeight),w=uiWidth*scale,h=uiHeight*scale;
    return {left:(width-w)/2,top:(height-h)/2,width:w,height:h};
  }
  function logicalSize(width, height, resolution, pixelRatio) {
    const fixed=/^(1280x720|1920x1080)$/.exec(resolution||'');
    if(fixed){const a=fixed[1].split('x').map(Number);return {w:a[0],h:a[1]};}
    width=Math.max(1,finite(width,1280));height=Math.max(1,finite(height,720));
    // CSS pixels are not display pixels on Retina/HDMI. Ask SageTV to rasterize
    // sharper text instead of enlarging one low-density canvas. Bound density
    // and retain existing1920x1080 limits; fixed/manual resolutions stay exact.
    const density=Math.max(1,Math.min(2,finite(pixelRatio,1)));
    width*=density;height*=density;
    // Keep the viewport aspect while limiting rendering load. Very narrow or
    // short windows use a bounded logical minimum and are fitted without crop.
    const scale=Math.min(1,1920/width,1080/height);
    return {w:Math.max(320,Math.round(width*scale/2)*2),h:Math.max(240,Math.round(height*scale/2)*2)};
  }
  /** Canvas coordinates and media presentation are separate. Window mode uses
   * every CSS pixel even when logical dimensions were rounded/capped. Fixed UI
   * resolutions retain their aspect; fullscreen video still owns the stage. */
  function stageRect(width, height, uiWidth, uiHeight, auto) {
    return auto ? {left:0,top:0,width:Math.max(1,finite(width,1)),height:Math.max(1,finite(height,1))}
      : fitRect(width,height,uiWidth,uiHeight);
  }
  function videoPresentation(rect, uiWidth, uiHeight, viewport) {
    const screen=[0,0,Math.max(1,uiWidth),Math.max(1,uiHeight)];
    const valid=Array.isArray(rect)&&rect.length>=4&&rect.slice(0,4).every(Number.isFinite)&&rect[2]>0&&rect[3]>0;
    const raw=valid?rect.slice(0,4):screen.slice();
    const hit=rectIntersection(raw,screen);
    // A small, explicit native rectangle is a menu preview. Near-fullscreen
    // destinations often contain server overscan or an old display aspect;
    // they must not double-letterbox the independent browser video plane.
    const full=!hit || (hit[2]/screen[2]>=.60 && hit[3]/screen[3]>=.60);
    return {kind:viewport==='native'?'native':full?'fullscreen':'preview',
      rect:viewport==='native'?raw:full?screen:raw, nativeRect:raw};
  }
  function videoLayerRect(presentation, display, stageWidth, stageHeight, uiWidth, uiHeight) {
    if(presentation.kind==='fullscreen')return {left:0,top:0,width:stageWidth,height:stageHeight};
    const r=presentation.rect;
    return {left:display.left+r[0]*display.width/uiWidth,top:display.top+r[1]*display.height/uiHeight,
      width:r[2]*display.width/uiWidth,height:r[3]*display.height/uiHeight};
  }

  function canvasPoint(clientX,clientY,rect,uiWidth,uiHeight){
    const width=Math.max(1,finite(rect&&rect.width,1)),height=Math.max(1,finite(rect&&rect.height,1));
    return {x:Math.max(0,Math.min(Math.max(0,uiWidth-1),Math.round((finite(clientX,0)-finite(rect&&rect.left,0))*uiWidth/width))),
      y:Math.max(0,Math.min(Math.max(0,uiHeight-1),Math.round((finite(clientY,0)-finite(rect&&rect.top,0))*uiHeight/height)))};
  }
  function mediaContentRect(width,height,sourceWidth,sourceHeight,mode){
    width=Math.max(1,finite(width,1));height=Math.max(1,finite(height,1));
    let ratio=finite(sourceWidth,0)>0&&finite(sourceHeight,0)>0?sourceWidth/sourceHeight:width/height;
    if(mode==='4x3')ratio=4/3;else if(mode==='16x9')ratio=16/9;
    if(mode==='fill')return {left:0,top:0,width,height};
    const cover=mode==='cover'||mode==='zoom';let w,h;
    if((width/height>ratio)!==cover){h=height;w=height*ratio;}else{w=width;h=width/ratio;}
    return {left:(width-w)/2,top:(height-h)/2,width:w,height:h};
  }

  function fullscreenMatte(color, rect, screen, presentation, suspended) {
    if(!presentation || presentation.kind!=='fullscreen' || suspended)return false;
    const n=color>>>0,a=n>>>24,r=(n>>>16)&255,g=(n>>>8)&255,b=n&255;
    // Do not erase translucent native OSD panels or opaque colored menus.
    if(a<250 || r>8 || g>8 || b>8)return false;
    const hit=rectIntersection(rect,screen);if(!hit)return false;
    const [x,y,w,h]=hit,sw=screen[2],sh=screen[3],eps=2;
    const vertical=(x<=eps||x+w>=sw-eps)&&w<=sw*.25&&h>=sh*.65;
    const horizontal=(y<=eps||y+h>=sh-eps)&&h<=sh*.25&&w>=sw*.65;
    return vertical||horizontal;
  }
  function bufferedAhead(video) {
    if (!video || !video.buffered) return 0;
    const time = finite(video.currentTime, 0);
    try {
      for (let i = 0; i < video.buffered.length; i++) {
        if (time >= video.buffered.start(i) - 0.25 && time <= video.buffered.end(i) + 0.25)
          return Math.max(0, video.buffered.end(i) - time);
      }
    } catch (_) { /* SourceBuffer may have changed during iteration. */ }
    return 0;
  }
  function resumeTarget(settings, status, time) {
    const base = settings.bufferPreset === 'lowdelay' ? 1 : settings.bufferPreset === 'stable' ? 5 : 2;
    // Do not deadlock at the final segment if it is shorter than the normal threshold.
    if (status && status.endList) return Math.max(0.15, Math.min(base, finite(status.hlsSeconds, 0) - finite(time, 0) - 0.10));
    return base;
  }
  function incompleteEnd(status, timeSeconds, durationMs, startSeconds) {
    if (!status || status.producerPreparing===true || status.running || !status.endList) return false;
    const produced = finite(status.hlsSeconds, 0);
    // ENDLIST alone is NOT an error: FFmpeg often finishes before playback does.
    if (produced - finite(timeSeconds, 0) > 1.5) return false;
    if (status.activeRecording) return true;
    if (status.exitCode != null && status.exitCode !== 0) return true;
    // Stock owns physical recording-piece advance. Capture gaps can make its
    // wall-clock duration longer than the actual encoded samples. Once this
    // exact non-growing piece is cleanly exhausted, replaying its tail cannot
    // create the missing seconds; let the real browser ended reach stock EOS.
    // Whole-library truncation and unknown/growing/failed producers keep the
    // old recovery checks. Encoder EOF alone still never manufactures ended.
    if(status.nativeSegment===true&&status.activeRecording===false&&status.exitCode===0&&!status.error)return false;
    return durationMs > 0 && (finite(startSeconds, 0) + produced) * 1000 + 2500 < durationMs;
  }
  function menuIsGuide(hint) {
    return /(?:^|[,;\s])menuName\s*:\s*Guide(?:[,;]|$)/i.test(hint || '');
  }
  function rectIntersection(a, b) {
    if (!a || !b) return null;
    const x=Math.max(a[0],b[0]), y=Math.max(a[1],b[1]);
    const right=Math.min(a[0]+a[2],b[0]+b[2]), bottom=Math.min(a[1]+a[3],b[1]+b[3]);
    return right>x && bottom>y ? [x,y,right-x,bottom-y] : null;
  }
  function videoMask(color, rect, screen, current, previous, clear, suspended, trusted) {
    const n=color>>>0,a=(n>>>24)&255,r=(n>>>16)&255,g=(n>>>8)&255,b=n&255;
    const key=a>127&&Math.abs(r-8)<=2&&g<=2&&Math.abs(b-16)<=2;
    const dark=a<13||(a>127&&r<=12&&g<=12&&b<=18);
    const hit=rectIntersection(rect,screen);if(!hit)return null;
    const area=hit[2]*hit[3],screenArea=Math.max(1,screen[2]*screen[3]);
    const covers=target=>{const h=rectIntersection(hit,target);return !!h&&h[2]*h[3]>=target[2]*target[3]*.70;};
    const candidate=key||(clear&&dark&&(area>=screenArea*.35||(trusted&&covers(current))||covers(previous)))||
      (!suspended&&trusted&&dark&&(covers(current)||area>=screenArea*.75));
    if(!candidate||area<Math.max(64,screenArea*.01))return null;
    return hit;
  }
  function timeText(ms) {
    let s = Math.max(0, Math.floor(finite(ms, 0) / 1000));
    const h = Math.floor(s / 3600); s %= 3600;
    return (h ? h + ':' : '') + (h ? String(Math.floor(s / 60)).padStart(2, '0') : Math.floor(s / 60)) + ':' + String(s % 60).padStart(2, '0');
  }

  class UnifiedYuvImage {
    constructor(width,height) {
      width=Math.trunc(finite(width,0)); height=Math.trunc(finite(height,0));
      if(width<=0||height<=0||width>4096||height>4096||width*height>16777216) throw new Error('invalid unified image size');
      this.width=width;this.height=height;const pixels=width*height;
      this.y=new Uint8Array(pixels);this.uv=new Uint8Array(pixels);this.rgba=new Uint8ClampedArray(pixels*4);
      this.ySeen=new Uint8Array(height);this.uvSeen=new Uint8Array(height);
    }
    loadLine(line,data,offset,length) {
      line=Math.trunc(finite(line,-1));offset=Math.max(0,Math.trunc(finite(offset,0)));
      if(!(data&&line>=0&&line<this.height*2&&offset<data.length))return -1;
      const count=Math.min(this.width,Math.max(0,Math.trunc(finite(length,data.length-offset))),data.length-offset);if(!count)return -1;
      const row=line<this.height?line:line-this.height,target=line<this.height?this.y:this.uv,seen=line<this.height?this.ySeen:this.uvSeen;
      target.set(data.subarray(offset,offset+count),row*this.width);seen[row]=1;
      if(this.ySeen[row]&&this.uvSeen[row])this.convertRow(row);
      return row;
    }
    convertRow(row){
      const base=row*this.width;
      for(let x=0;x<this.width;x++){
        const yy=this.y[base+x],ci=base+(x&~1),u=this.uv[ci],v=this.uv[Math.min(ci+1,base+this.width-1)];
        const c=yy-16,d=u-128,e=v-128;
        const clamp=n=>n<0?0:n>255?255:n;
        const o=(base+x)*4;this.rgba[o]=clamp((298*c+409*e+128)>>8);this.rgba[o+1]=clamp((298*c-100*d-208*e+128)>>8);this.rgba[o+2]=clamp((298*c+516*d+128)>>8);this.rgba[o+3]=255;
      }
    }
    rowRgba(row){
      row=Math.trunc(row);if(row<0||row>=this.height)return new Uint8ClampedArray(0);
      return this.rgba.slice(row*this.width*4,(row+1)*this.width*4);
    }
    complete(){for(let i=0;i<this.height;i++)if(!this.ySeen[i]||!this.uvSeen[i])return false;return true;}
  }
  // DOM-independent keyboard/spatial policy. Local dialogs own navigation;
  // only an unobstructed stage/toolbar sends commands to the remote SageTV UI.
  function remoteCommand(key) {
    const keys={ArrowLeft:2,ArrowRight:3,ArrowUp:4,ArrowDown:5,Enter:20,Escape:75,
      Backspace:75,PageUp:55,PageDown:56,Home:28,' ':59,MediaPlayPause:59,
      MediaPlay:7,MediaPause:6,MediaStop:89,MediaTrackNext:61,MediaTrackPrevious:62,
      MediaFastForward:8,MediaRewind:9,AudioVolumeUp:13,AudioVolumeDown:14,AudioVolumeMute:26};
    if(Object.prototype.hasOwnProperty.call(keys,key))return keys[key];
    if(/^[0-9]$/.test(key))return 30+Number(key);
    return ({g:18,i:24,o:29,r:25,m:26,s:89,l:42,t:15})[String(key||'').toLowerCase()];
  }
  function spatialTarget(items,current,key) {
    const vector={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]}[key];
    if(!vector||!items.length)return current;
    const from=items.find(item=>item.id===current)||items[0],horizontal=!!vector[0];
    const x=from.x+from.width/2,y=from.y+from.height/2;
    const choices=items.filter(item=>item!==from).map(item=>{
      const dx=item.x+item.width/2-x,dy=item.y+item.height/2-y;
      const primary=dx*vector[0]+dy*vector[1],secondary=Math.abs(horizontal?dy:dx);
      const overlap=horizontal?Math.min(from.y+from.height,item.y+item.height)-Math.max(from.y,item.y)
        :Math.min(from.x+from.width,item.x+item.width)-Math.max(from.x,item.x);
      return {id:item.id,primary,secondary,overlap:overlap>1};
    }).filter(item=>item.primary>1);
    choices.sort((a,b)=>Number(b.overlap)-Number(a.overlap)||(a.primary+a.secondary*2)-(b.primary+b.secondary*2));
    return choices.length?choices[0].id:from.id;
  }
  class CommandRepeat {
    constructor(options){this.o=options||{};this.clock=this.o.clock||{setTimeout:(f,m)=>setTimeout(f,m),clearTimeout:i=>clearTimeout(i),setInterval:(f,m)=>setInterval(f,m),clearInterval:i=>clearInterval(i)};this.active=null;this.delay=null;this.interval=null;}
    press(key,command){
      if(this.active&&this.active.key===key)return false;
      this.cancel();this.active={key,command};this.o.send(command);
      this.delay=this.clock.setTimeout(()=>{if(!this.active||this.active.key!==key)return;this.o.send(command);this.interval=this.clock.setInterval(()=>{if(this.active&&this.active.key===key)this.o.send(command);},150);},420);return true;
    }
    release(key){if(this.active&&this.active.key===key)this.cancel();}
    cancel(){if(this.delay!==null)this.clock.clearTimeout(this.delay);if(this.interval!==null)this.clock.clearInterval(this.interval);this.delay=this.interval=null;this.active=null;}
  }

  class RecoveryBudget {
    constructor(limit) { this.limit = limit || 6; this.count = 0; }
    reset() { this.count = 0; }
    take() { if (this.count >= this.limit) return false; this.count++; return true; }
  }
  /** A gesture does not emit a SageTV press until it is known not to be a hold.
   * This prevents the item behind the remote from being activated on release.
   * All distances are CSS pixels; canvas resolution must not affect recognition.
   */
  class PointerGesture {
    constructor(options) {
      this.o = options;
      this.clock = options.clock || {now: () => Date.now(), setTimeout: (fn, ms) => setTimeout(fn, ms), clearTimeout: id => clearTimeout(id)};
      this.active = null; this.timer = null; this.pendingClick = null;
      this.suppressUntil = 0;
    }
    settings() { return normalizeSettings(this.o.settings()); }
    clearTimer() { if (this.timer !== null) this.clock.clearTimeout(this.timer); this.timer = null; }
    clearPending(deliver) {
      const p = this.pendingClick; this.pendingClick = null;
      if (!p) return;
      this.clock.clearTimeout(p.timer);
      if (deliver) this.o.click(p.point, p.button);
    }
    down(e, point) {
      if (this.active || e.isPrimary === false) return false;
      if (e.button === 3 && this.settings().mouseBack) {
        this.o.back(); this.suppressUntil = this.clock.now() + 800; return true;
      }
      if (![0, 1, 2].includes(e.button)) return false;
      const mode = this.settings().osdTrigger;
      const button = e.button === 2 ? 3 : e.button === 1 ? 2 : 1;
      const a = {id: e.pointerId, x: e.clientX, y: e.clientY, point, button,
        browserButton: e.button, fired: false, dragging: false, lastPoint: point};
      this.active = a;
      if ((mode === 'left_long' && button === 1) || (mode === 'right_long' && button === 3)) {
        this.timer = this.clock.setTimeout(() => {
          this.timer = null;
          if (this.active !== a || a.dragging) return;
          a.fired = true; this.clearPending(false);
          this.suppressUntil = this.clock.now() + 1000;
          this.o.open();
        }, 575);
      }
      return true;
    }
    move(e, point) {
      const a = this.active;
      if (!a) { if (this.o.move) this.o.move(point); return; }
      if (e.pointerId !== a.id) return;
      a.lastPoint = point;
      if (a.fired) return;
      if (!a.dragging && Math.hypot(e.clientX - a.x, e.clientY - a.y) > 12) {
        this.clearTimer(); this.clearPending(true); a.dragging = true;
        if (this.o.dragStart) this.o.dragStart(a.point, a.button);
      }
      if (a.dragging && this.o.dragMove) this.o.dragMove(point, a.button);
    }
    up(e, point) {
      const a = this.active;
      if (!a || e.pointerId !== a.id) return false;
      this.clearTimer(); this.active = null;
      this.suppressUntil = this.clock.now() + 800;
      if (a.fired) return true;
      if (a.dragging) { if (this.o.dragEnd) this.o.dragEnd(point, a.button); return true; }
      const mode = this.settings().osdTrigger;
      if (mode === 'center_click' && a.button === 2) { this.clearPending(false); this.o.open(); return true; }
      const doubleMode = (mode === 'left_double' && a.button === 1) || (mode === 'right_double' && a.button === 3);
      if (doubleMode) {
        const p = this.pendingClick;
        if (p && p.button === a.button && this.clock.now() - p.at <= 420 && Math.hypot(e.clientX - p.x, e.clientY - p.y) <= 18) {
          this.clearPending(false); this.o.open();
        } else {
          this.clearPending(true);
          const pending = {point, button: a.button, x: e.clientX, y: e.clientY, at: this.clock.now()};
          pending.timer = this.clock.setTimeout(() => {
            if (this.pendingClick === pending) { this.pendingClick = null; this.o.click(pending.point, pending.button); }
          }, 420);
          this.pendingClick = pending;
        }
      } else { this.clearPending(true); this.o.click(point, a.button); }
      return true;
    }
    cancel() {
      const a = this.active; this.active = null; this.clearTimer(); this.clearPending(false);
      this.suppressUntil = this.clock.now() + 800;
      if (a && a.dragging && this.o.dragEnd) this.o.dragEnd(a.lastPoint, a.button);
    }
    fallbackClick(e, point) {
      // detail=0 is a keyboard/assistive click; pointer-generated clicks were
      // already handled by pointerup and must not also select behind the OSD.
      if (this.clock.now() < this.suppressUntil || this.active || e.button > 0) return;
      this.o.click(point, 1);
    }
  }
  return {DEFAULTS, fitRect, logicalSize, stageRect, videoPresentation, videoLayerRect, canvasPoint, mediaContentRect, fullscreenMatte, normalizeSettings, requiredStartSegments, startupReady, hlsConfig,
    bufferedAhead, resumeTarget, incompleteEnd, menuIsGuide, rectIntersection, videoMask, timeText, RecoveryBudget, PointerGesture, UnifiedYuvImage, CommandRepeat, remoteCommand, spatialTarget, eventDelivery};
});
