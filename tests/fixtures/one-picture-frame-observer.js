/* Read-only test observer. Source change alone is not a presented picture. */
function observeOnePictureFrames(video){
  const s={before:video.currentSrc,active:video.currentSrc,frames:0,frameTime:null,done:false};
  function frame(now,m){
    if(s.done)return;
    const source=video.currentSrc;
    if(source!==s.active){s.active=source;s.frames=0;s.frameTime=null;}
    if(source&&source!==s.before&&video.readyState>=2&&video.videoWidth>0&&
       Number.isFinite(m.mediaTime)&&Math.abs(m.mediaTime-video.currentTime)<=.25){
      s.frames++;s.frameTime=m.mediaTime;
    }
    video.requestVideoFrameCallback(frame);
  }
  video.requestVideoFrameCallback(frame);return s;
}
if(typeof module==='object')module.exports=observeOnePictureFrames;
