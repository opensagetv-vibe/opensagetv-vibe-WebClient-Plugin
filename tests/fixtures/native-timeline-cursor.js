/* Opt-in stock SageMC/SageTV7 1280x720 fixture, NOT production UI guessing.
 * Observe actual themed position markers separately from new video frames.
 * Does not draw, alter native events, send input, or change player clocks. */
(()=>{
  // Observe native placement, not the browser's Fill policy, when deciding
  // whether this fixture is in VideoOSD or still behind a main-menu preview.
  const read=ReadableStreamDefaultReader.prototype.read,decoder=new TextDecoder();let pending='';
  ReadableStreamDefaultReader.prototype.read=async function(...args){
    const result=await read.apply(this,args);
    if(result.value){
      pending+=decoder.decode(result.value,{stream:true});if(pending.length>16*1024*1024)pending='';
      let end;while((end=pending.indexOf('\n'))>=0){
        const line=pending.slice(0,end);pending=pending.slice(end+1);
        try{const event=JSON.parse(line);if(event.type==='videoBounds')window.TEST_VIDEO_BOUNDS=event.dst;}catch(_){}
      }
    }
    return result;
  };
  const fetchOriginal=window.fetch;
  window.fetch=async function(input,...args){
    const s=window.SEEK,url=new URL(String(input),location.href);
    const click=s&&url.pathname.endsWith('/api/miniclient')&&url.searchParams.get('action')==='click';
    if(click)s.inputSentMs=performance.now()-s.t0;
    const response=await fetchOriginal.call(this,input,...args);
    if(click)s.inputAckMs=performance.now()-s.t0;
    return response;
  };
  window.probeNativeCursor=()=>{
    const s=window.SEEK,c=document.getElementById('gfxCanvas');
    if(!s||!s.cursorFrames||!c||c.width!==1280||c.height!==720)return;
    if(s.stv==='stock'){
      // Canonical unmodified SageTV7 fixture: its themed marker is a red
      // vertical bar. This geometry belongs ONLY to the opt-in pixel test.
      const p=c.getContext('2d').getImageData(179,654,922,35).data;
      let markerX=null,markerScore=0;
      for(let x=0;x<922;x++){
        let score=0;
        for(let y=0;y<35;y++){
          const i=(y*922+x)*4;
          if(p[i]>210&&p[i+1]<65&&p[i+2]<65&&p[i+3]>180)score++;
        }
        if(score>markerScore){markerScore=score;markerX=x+179;}
      }
      const ms=performance.now()-s.t0;
      if(s.cursorFrames.length<256)s.cursorFrames.push({ms,markerX,markerScore});
      if(s.cursorFirstMs===null&&markerScore>=15&&Math.abs(markerX-s.targetX)<=10)s.cursorFirstMs=ms;
      return;
    }
    const ctx=c.getContext('2d'),pixels=ctx.getImageData(330,646,705,33).data,peaks=[];
    let best=0,bestX=0,progressEdge=null,markerX=null,markerScore=0;
    // The white handle consists of opposed triangles OUTSIDE the bar. The
    // fixed white left border inside it is not a movable position marker.
    const strip=ctx.getImageData(320,635,735,55).data;
    for(let x=0;x<735;x++){
      let top=0,bottom=0;
      for(let y=0;y<55;y++){
        const i=(y*735+x)*4,r=strip[i],g=strip[i+1],b=strip[i+2];
        if(r>195&&g>195&&b>185&&Math.max(r,g,b)-Math.min(r,g,b)<40&&strip[i+3]>180){
          if(y>=5&&y<=12)top++;if(y>=39&&y<=49)bottom++;
        }
      }
      const score=Math.min(top,bottom);
      if(score>markerScore){markerScore=score;markerX=x+320;}
    }
    for(let x=0;x<705;x++){
      let white=0;
      for(let y=0;y<33;y++){
        const i=(y*705+x)*4,r=pixels[i],g=pixels[i+1],b=pixels[i+2];
        if(r>195&&g>195&&b>185&&Math.max(r,g,b)-Math.min(r,g,b)<40&&pixels[i+3]>180)white++;
      }
      if(white>best){best=white;bestX=x+330;}
      if(white>=10)peaks.push(x+330);
      // Record the progress edge separately, never pass it off as the handle.
      const j=(19*705+x)*4;
      if(x>24&&progressEdge===null&&pixels[j+1]>100&&pixels[j+1]-pixels[j]>30&&pixels[j+1]-pixels[j+2]>30&&pixels[j+3]>180)progressEdge=x+330;
    }
    const ms=performance.now()-s.t0;
    if(s.cursorFrames.length<256)s.cursorFrames.push({ms,x:bestX,white:best,markerX,markerScore,progressEdge,peaks:peaks.slice(-24)});
    if(s.cursorFirstMs===null&&markerScore>=3&&Math.abs(markerX-s.targetX)<=10)s.cursorFirstMs=ms;
    if(s.progressFirstMs==null&&progressEdge!==null&&Math.abs(progressEdge-s.targetX)<=8)s.progressFirstMs=ms;
  };
  const draw=CanvasRenderingContext2D.prototype.drawImage;
  CanvasRenderingContext2D.prototype.drawImage=function(...args){
    const result=draw.apply(this,args);
    if(this.canvas.id==='gfxCanvas')window.probeNativeCursor();
    return result;
  };
})();
