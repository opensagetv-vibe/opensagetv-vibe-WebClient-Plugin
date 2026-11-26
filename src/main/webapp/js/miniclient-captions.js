/* Browser-local broadcast captions. CEA, Teletext and DVB bitmap subtitles use
 * the video clock, so presentation continues while SageMC hides its OSD. */
(function(root,factory){
  if(typeof module==='object'&&module.exports)module.exports=factory();
  else root.SageMiniCaptions=factory();
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  class Controller {
    constructor(options){this.o=options;this.generation=0;this.timer=null;this.pollTimer=null;this.decoder=null;this.teletext=false;this.dvb=false;this.stv=false;this.stvStateSeen=false;this.stvState=0;this.stvService='';this.queue=[];this.cursor=0;this.lastError='';this.received=0;this.clears=0;this.services=[];this.bitmapExpiry=0;this.queueInfo=null;}
    stop(){++this.generation;clearTimeout(this.timer);clearTimeout(this.pollTimer);this.timer=this.pollTimer=null;this.decoder=null;this.teletext=false;this.dvb=false;this.stv=false;this.stvStateSeen=false;this.stvState=0;this.stvService='';this.queue=[];this.cursor=0;this.services=[];this.bitmapExpiry=0;this.queueInfo=null;this.o.render('');if(this.o.clearBitmap)this.o.clearBitmap();}
    start(event){
      this.stop();this.lastError='';this.received=0;this.clears=0;
      const p=event.streamSettings&&event.streamSettings.requested||{},authority=event.captionAuthority||null;
      this.options=p;this.id=event.hlsSession;this.stv=!!(authority&&authority.mode==='stv');
      if(authority&&authority.mode==='off')return;
      if(!this.id||String(p.captions)==='off')return;
      if(String(p.captions)==='teletext'){this.teletext=true;this.present(this.generation);this.pollTeletext(this.generation);return;}
      if(String(p.captions)==='dvb'){this.dvb=true;this.present(this.generation);this.pollDvb(this.generation);return;}
      if(!['608','708'].includes(String(p.captions)))return;
      const serial=this.generation;
      const initialStvState=authority&&authority.stvStateSeen?Number(authority.stvState)||0:null;
      const service=this.stv?(initialStvState>0?'CC'+Math.max(1,Math.min(4,initialStvState)):'CC'+(Number(p.captionService)||1)):(p.captions==='708'?'708-'+p.captionService:'CC'+p.captionService);
      const enabled=!this.stv||initialStvState===null||initialStvState>0;
      this.decoder=new this.o.Decoder({enabled,service,onCaption:(text,svc,meta)=>{if(this.generation===serial)this.o.render(text,svc,meta);}});
      if(this.stv){this.stvStateSeen=initialStvState!==null;this.stvState=initialStvState===null?0:initialStvState;this.stvService=service;if(!enabled)this.o.render('');}
      const tick=()=>{
        if(serial!==this.generation||!this.decoder)return;
        const now=Math.max(0,this.o.timeMs());let count=0;
        while(this.queue.length&&this.queue[0][0]<=now+3000&&count++<300){const [pts,hex]=this.queue.shift();this.decoder.pushCcData(fromHex(hex),pts);}
        this.decoder.updateTime(Math.max(0,now-(Number(p.captionOffsetMs)||0)));
        this.timer=setTimeout(tick,33);
      };
      tick();this.poll(serial);
    }
    setSageTvState(value,seen=true){
      let state=Number.parseInt(value,10);if(!Number.isFinite(state)||state<0)state=0;
      this.stvStateSeen=!!seen;this.stvState=state;
      if(!this.stv||!this.decoder)return;
      if(this.stvStateSeen&&state===0){this.stvService='';if(typeof this.decoder.setEnabled==='function')this.decoder.setEnabled(false);this.o.render('');return;}
      const service='CC'+Math.max(1,Math.min(4,state||Number(this.options&&this.options.captionService)||1));
      this.stvService=service;if(typeof this.decoder.setService==='function')this.decoder.setService(service);if(typeof this.decoder.setEnabled==='function')this.decoder.setEnabled(true);
    }
    enqueue(cues){
      for(const cue of cues){
        if(!cue||!Number.isFinite(cue.ptsMs)||cue.ptsMs<0)continue;
        if(this.teletext&&(cue.kind!=='text'||cue.owner!=='local_broadcast'))continue;
        if(this.dvb&&(cue.kind!=='bitmap'||cue.owner!=='local_dvb'))continue;
        if(typeof cue.text==='string'&&cue.text.length>32768)throw new Error('Caption text exceeds limit');
        if(typeof cue.data==='string'&&cue.data.length>4*1024*1024)throw new Error('Caption bitmap exceeds limit');
        this.queue.push(cue);this.received++;
      }
      this.queue.sort((a,b)=>a.ptsMs-b.ptsMs);
      if(this.queue.length>512||this.queue.reduce((n,c)=>n+(c.data?c.data.length:0)+(c.text?c.text.length:0),0)>8*1024*1024){this.queue=[];throw new Error('Caption presentation queue exceeds limit');}
    }
    present(serial){
      if(serial!==this.generation||!(this.teletext||this.dvb))return;
      const now=Math.max(0,(this.o.sourceTimeMs?this.o.sourceTimeMs():this.o.timeMs())-(Number(this.options.captionOffsetMs)||0));
      try{
        if(this.bitmapExpiry>0&&now>=this.bitmapExpiry){this.bitmapExpiry=0;this.clears++;if(this.dvb&&this.o.clearBitmap)this.o.clearBitmap();else this.o.render('');}
        let count=0;
        while(this.queue.length&&this.queue[0].ptsMs<=now&&count++<256){
          const cue=this.queue.shift();
          if(cue.clear||this.teletext&&!cue.text){this.clears++;this.bitmapExpiry=0;if(this.dvb&&this.o.clearBitmap)this.o.clearBitmap();else this.o.render('');}
          if(this.teletext&&!cue.clear&&cue.text)this.o.render(String(cue.text),'teletext',{type:'teletext',ptsMs:cue.ptsMs});
          else if(this.dvb&&!cue.clear||this.dvb&&cue.data){
            const rect=Array.isArray(cue.rect)?cue.rect:[],w=Number(rect[2])|0,h=Number(rect[3])|0;
            if(w>0&&h>0&&w*h<=1048576&&cue.format==='rgba-straight'&&typeof cue.data==='string'){
              const rgba=fromBase64(cue.data);if(rgba.length!==w*h*4)throw new Error('Invalid DVB RGBA rectangle length');
              if(this.o.renderBitmap)this.o.renderBitmap(cue,rgba);
            }
          }
          const duration=Math.max(0,Number(cue.durationMs)||0);if(duration>0)this.bitmapExpiry=cue.ptsMs+duration;
        }
      }catch(error){this.lastError=error.message||String(error);if(this.o.error)this.o.error(this.lastError);}
      this.timer=setTimeout(()=>this.present(serial),33);
    }
    async poll(serial){
      if(serial!==this.generation||!this.decoder)return;
      let again=1000;
      try {
        const data=await this.o.fetch({session:this.id,cursor:this.cursor,untilMs:Math.floor(Math.max(0,this.o.timeMs())+10000)});
        if(serial!==this.generation||!this.decoder)return;
        const valid=(data.packets||[]).filter(p=>Array.isArray(p)&&p.length===2&&Number.isFinite(p[0])&&p[0]>=0&&typeof p[1]==='string'&&p[1].length<=186&&p[1].length%6===0&&/^[a-f0-9]*$/i.test(p[1]));
        this.cursor=Number(data.cursor)||0;this.received+=valid.length;
        this.queue.push(...valid);this.queue.sort((a,b)=>a[0]-b[0]);
        if(this.queue.length>12000){this.queue=[];this.stop();throw new Error('Caption queue limit exceeded; local captions stopped');}
        if(valid.length>=1024)again=100;
      }catch(e){
        if(serial===this.generation){this.lastError=e.message||String(e);if(this.o.error)this.o.error(this.lastError);again=3000;}
      }finally{if(serial===this.generation&&this.decoder)this.pollTimer=setTimeout(()=>this.poll(serial),again);}
    }
    async pollTeletext(serial){
      if(serial!==this.generation||!this.teletext)return;
      let again=350;
      try{
        const delay=Number(this.options&&this.options.captionOffsetMs)||0;
        const presentation=Math.max(0,Math.floor((this.o.sourceTimeMs?this.o.sourceTimeMs():this.o.timeMs())-delay));
        const data=await this.o.subtitleFetch({session:this.id,timeMs:presentation+1200,max:256});
        if(serial!==this.generation||!this.teletext)return;
        if(this.retiredBroadcastService(data.teletext,false)){this.queueInfo=data.queue||this.queueInfo;return;}
        const cues=Array.isArray(data.cues)?data.cues:[];
        this.enqueue(cues);this.presentDueNow();
        this.queueInfo=data.queue||this.queueInfo;if(data.teletext&&Array.isArray(data.teletext.services))this.services=data.teletext.services;
        if(cues.length>=128)again=50;
      }catch(e){
        if(serial===this.generation){this.lastError=e.message||String(e);if(this.o.error)this.o.error('Teletext: '+this.lastError);again=2000;}
      }finally{if(serial===this.generation&&this.teletext)this.pollTimer=setTimeout(()=>this.pollTeletext(serial),again);}
    }
    async pollDvb(serial){
      if(serial!==this.generation||!this.dvb)return;
      let again=120;
      try{
        const delay=Number(this.options&&this.options.captionOffsetMs)||0;
        const presentation=Math.max(0,Math.floor((this.o.sourceTimeMs?this.o.sourceTimeMs():this.o.timeMs())-delay));
        const data=await this.o.subtitleFetch({session:this.id,timeMs:presentation+1200,max:256});
        if(serial!==this.generation||!this.dvb)return;
        if(this.retiredBroadcastService(data.dvbBitmap,true)){this.queueInfo=data.queue||this.queueInfo;return;}
        const cues=Array.isArray(data.cues)?data.cues:[];
        this.enqueue(cues);this.presentDueNow();
        this.queueInfo=data.queue||this.queueInfo;if(data.dvbBitmap&&Array.isArray(data.dvbBitmap.services))this.services=data.dvbBitmap.services;
        if(cues.length>=128)again=25;else if(!cues.length)again=250;
      }catch(e){
        if(serial===this.generation){this.lastError=e.message||String(e);if(this.o.error)this.o.error('DVB bitmap: '+this.lastError);again=1500;}
      }finally{if(serial===this.generation&&this.dvb)this.pollTimer=setTimeout(()=>this.pollDvb(serial),again);}
    }
    retiredBroadcastService(state,bitmap){
      // Older peers omit selection metadata. Empty discovery alone is NOT a
      // removal; use only an explicit current-source numeric selection/off.
      if(!state||!Array.isArray(state.services)||!Number.isInteger(state.selectedTrack))return false;
      if(state.active!==false&&state.selectedTrack>=0)return false;
      const at=state.selectionChangedMs;
      const now=Math.max(0,(this.o.sourceTimeMs?this.o.sourceTimeMs():this.o.timeMs())-(Number(this.options&&this.options.captionOffsetMs)||0));
      if(state.active!==false&&Number.isFinite(at)&&at>0&&now<at)return false;
      this.services=state.services;this.queue=[];this.bitmapExpiry=0;this.clears++;
      if(bitmap&&this.o.clearBitmap)this.o.clearBitmap();else this.o.render('');
      return true;
    }
    presentDueNow(){clearTimeout(this.timer);this.timer=null;this.present(this.generation);}
    snapshot(){return {mode:this.dvb?'dvb-bitmap-local':this.teletext?'teletext-local':this.decoder?(this.stv?'stv-controlled-browser-local':'browser-local'):'off',received:this.received,clears:this.clears,cursor:this.cursor,pending:this.queue.length,presentationTickMs:33,lookAheadMs:1200,error:this.lastError,services:this.services,bitmapExpiry:this.bitmapExpiry,queue:this.queueInfo,stvControlled:this.stv,stvStateSeen:this.stvStateSeen,stvState:this.stvState,stvService:this.stvService,decoder:this.decoder?this.decoder.getStats():null};}
  }
  function fromHex(hex){const out=new Uint8Array(hex.length/2);for(let i=0;i<out.length;i++)out[i]=parseInt(hex.slice(i*2,i*2+2),16);return out;}
  function fromBase64(value){if(typeof Buffer!=='undefined'&&typeof Buffer.from==='function')return new Uint8Array(Buffer.from(value,'base64'));const raw=atob(value),out=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)out[i]=raw.charCodeAt(i)&255;return out;}
  return Controller;
});
