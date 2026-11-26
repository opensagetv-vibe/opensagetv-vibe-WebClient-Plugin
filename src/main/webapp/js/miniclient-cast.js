/* WEB-122 video-only browser routing. No mirroring, credentials or URL export. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.SageVideoCast=api;})(typeof window==='object'?window:this,function(){
  'use strict';
  function route(video){
    if(video.disableRemotePlayback)return '';
    if(typeof video.webkitShowPlaybackTargetPicker==='function')return 'airplay';
    if(video.remote&&typeof video.remote.prompt==='function')return 'remote';
    return '';
  }
  class Controller{
    constructor(video,button,active,notify){
      this.video=video;this.button=button;this.active=active;this.notify=notify;
      button.addEventListener('click',()=>this.open());
      for(const event of ['loadedmetadata','emptied','webkitcurrentplaybacktargetiswirelesschanged','webkitplaybacktargetavailabilitychanged'])
        video.addEventListener(event,()=>this.update());
      if(video.remote&&typeof video.remote.addEventListener==='function')
        for(const event of ['connect','connecting','disconnect'])video.remote.addEventListener(event,()=>this.update());
      this.update();
    }
    update(){
      const method=route(this.video),loaded=!!this.active();
      this.button.disabled=!loaded||!method;
      this.button.title=!method?'Video casting unavailable in this browser or playback mode. iPhone supports AirPlay; Chromecast and Fire TV need a compatible sender/receiver app.':
        !loaded?'Start video before casting':method==='airplay'?'Cast video with AirPlay (video only)':'Cast video to a supported receiver (video only)';
      this.button.setAttribute('aria-pressed',String(this.video.webkitCurrentPlaybackTargetIsWireless===true||
        !!(this.video.remote&&this.video.remote.state==='connected')));
    }
    open(){
      this.update();if(this.button.disabled)return false;
      // Invoke synchronously in the real click: awaiting a status/network call
      // first would lose Safari's user activation. Never reload/retune media.
      try{
        const result=route(this.video)==='airplay'?this.video.webkitShowPlaybackTargetPicker():this.video.remote.prompt();
        if(result&&typeof result.catch==='function')result.catch(error=>this.failed(error));
        return true; // picker requested, NOT proof a receiver connected
      }catch(error){this.failed(error);return false;}
    }
    failed(error){
      if(!error||error.name!=='AbortError')this.notify('Unable to open video casting. Use a compatible receiver on the same network; this does not mirror the phone screen.');
      this.update(); // cancellation/failure never pauses, restarts or retries
    }
  }
  return Object.freeze({route,Controller});
});
