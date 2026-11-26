/* Portable current-Vibe input policy. Browser key names/CSS pixels, not Android
 * scan codes; no code evaluation or arbitrary server API names in mappings. */
(function(root,factory){
  if(typeof module==='object'&&module.exports)module.exports=factory();else root.SageMiniInput=factory();
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const ACTIONS=Object.freeze({none:'Disabled',remote:'Vibe controls',keyboard:'Text keyboard',default:'Default',
    2:'Left',3:'Right',4:'Up',5:'Down',20:'Select',75:'Back',28:'Home',29:'Options',24:'Info',18:'Guide',86:'Recordings',
    7:'Play',6:'Pause',59:'Play / pause',89:'Stop',8:'Fast forward',9:'Rewind',61:'Skip forward',62:'Skip back',
    55:'Page up',56:'Page down',11:'Channel up',12:'Channel down',60:'Last channel',13:'Volume up',14:'Volume down',26:'Mute',25:'Record',10:'Time Scroll',15:'TV',40:'Search',42:'Library',63:'Live TV',65:'Next DVD chapter',66:'Previous DVD chapter',67:'DVD menu',83:'Delete',
    105:'Scroll left',106:'Scroll right',107:'Scroll up',108:'Scroll down',
    30:'0',31:'1',32:'2',33:'3',34:'4',35:'5',36:'6',37:'7',38:'8',39:'9'});
  const CONTEXTS=['default','playing','paused','dvd'];
  const GAMEPAD=[['GamepadA','Enter'],['GamepadB','Escape'],['GamepadX','i'],['GamepadY','o'],['GamepadL1','MediaTrackPrevious'],['GamepadR1','MediaTrackNext'],['GamepadL2','MediaRewind'],['GamepadR2','MediaFastForward'],['GamepadSelect','Escape'],['GamepadStart','ContextMenu'],['GamepadL3','MediaPlayPause'],['GamepadR3','MediaPlayPause'],['GamepadUp','ArrowUp'],['GamepadDown','ArrowDown'],['GamepadLeft','ArrowLeft'],['GamepadRight','ArrowRight']];
  const KEYS=['Enter','ArrowLeft','ArrowRight','ArrowUp','ArrowDown','PageUp','PageDown','MediaPlay','MediaPause','MediaPlayPause','MediaStop','MediaFastForward','MediaRewind','MediaTrackNext','MediaTrackPrevious','AudioVolumeUp','AudioVolumeDown','AudioVolumeMute','Home','Escape','Backspace','ContextMenu','g','i','o','r','m','s','l','t','0','1','2','3','4','5','6','7','8','9',...GAMEPAD.map(x=>x[0])];
  // Standard DOM names, not Android keycodes or guessed numeric browser codes.
  // No new default command: especially preserve Backspace=Back and leave
  // Delete/Insert/colour keys inert until the user explicitly maps them.
  KEYS.push('BrowserSearch','Delete','Insert','ColorF0Red','ColorF1Green','ColorF2Yellow','ColorF3Blue','ChannelUp','ChannelDown');
  const TOUCH={swipe_left:'2',swipe_right:'3',swipe_up:'4',swipe_down:'5',double_tap:'29',long_press:'remote',
    swipe_left_2:'105',swipe_right_2:'106',swipe_up_2:'107',swipe_down_2:'108',double_tap_2:'29',long_press_2:'none',
    swipe_left_3:'75',swipe_right_3:'28',swipe_up_3:'29',swipe_down_3:'24',double_tap_3:'29',long_press_3:'none',
    edge_top:'none',edge_bottom:'keyboard',edge_left:'none',edge_right:'remote',
    hotspot_top_left:'keyboard',hotspot_top_right:'none',hotspot_bottom_left:'remote',hotspot_bottom_right:'29'};
  const action=value=>Object.prototype.hasOwnProperty.call(ACTIONS,String(value))?String(value):'default';
  /** Stock MENU_HINT, including SageMC's actual "MC MediaPlayer OSD" name.
   * Geometry alone cannot distinguish video behind an STV popup. Unknown
   * menus, a named popup or text input retain ordinary navigation keys. */
  function playbackMenuHint(raw){
    if(typeof raw!=='string'||raw.length>2048)return false;
    const fields={};for(const part of raw.split(',')){const n=part.indexOf(':');if(n>=0)fields[part.slice(0,n).trim().toLowerCase()]=part.slice(n+1).trim();}
    const name=fields.menuname||'',popup=fields.popupname||'';
    return /^(?:VideoOSD|DVDOSD|TVOSD|OSD|MediaPlayer|MediaPlayer OSD|MC MediaPlayer OSD)$/i.test(name)
      &&(!popup||/^null$/i.test(popup))&&!/^true$/i.test(fields.hastextinput||'');
  }
  // Unavailable is not a new observation. Retain a recent exact-generation
  // answer only within the existing 1.5s guard, without extending its age.
  // The caller resets both fields on every new source/generation.
  function dvdMenuObservation(previous,at,value,now){
    if(typeof value==='boolean')return {value,at:now};
    return {value:now-at<1500?previous:null,at};
  }
  function dvdFullscreenPresentation(presentation,owner){
    // A stock DVD OSD may omit a new SETVIDEORECT after leaving its library
    // preview. Only current source-owned DVD state plus the known, popup-free
    // OSD can qualify browser fullscreen. Never overwrite the raw rectangle:
    // returning to the main menu must restore that exact preview immediately.
    const s=owner||{},age=s.now-s.at;
    return !!presentation&&presentation.kind==='preview'&&s.active===true&&s.dvd===true&&
      typeof s.state==='boolean'&&Number.isFinite(s.now)&&Number.isFinite(s.at)&&
      age>=0&&age<1500&&playbackMenuHint(s.menu);
  }
  function normalize(input){
    const value=input&&typeof input==='object'?input:{},out={version:1,repeatDelay:420,repeatInterval:150,edgeSize:50,hotspotSize:50,gamepadEnabled:true,keys:{},touch:{}};
    if(typeof value.gamepadEnabled==='boolean')out.gamepadEnabled=value.gamepadEnabled;
    for(const [key,min,max] of [['repeatDelay',150,2000],['repeatInterval',80,1000],['edgeSize',0,100],['hotspotSize',0,100]]){
      const number=Number(value[key]);if(Number.isFinite(number))out[key]=Math.max(min,Math.min(max,Math.round(number)));
    }
    for(const context of CONTEXTS){out.keys[context]={};const source=value.keys&&value.keys[context]||{};
      for(const key of KEYS)for(const suffix of ['',':hold'])if(Object.prototype.hasOwnProperty.call(source,key+suffix))out.keys[context][key+suffix]=action(source[key+suffix]);
    }
    for(const key of Object.keys(TOUCH))out.touch[key]=value.touch&&Object.prototype.hasOwnProperty.call(value.touch,key)?action(value.touch[key]):TOUCH[key];
    return out;
  }
  function keyAction(config,context,key,hold=false){
    const name=key+(hold?':hold':''),maps=config.keys||{};
    const value=maps[context]&&maps[context][name];if(value&&value!=='default')return value;
    return maps.default&&maps.default[name]||'default';
  }
  class Keys {
    constructor(options){this.o=options;this.clock=options.clock||{setTimeout:(f,m)=>setTimeout(f,m),clearTimeout:i=>clearTimeout(i)};this.active=null;this.timer=null;}
    down(key,tap,hold,repeat){
      if(this.active&&this.active.key===key)return;
      this.cancel();const cfg=this.o.settings(),a={key,tap,hold,repeat,held:false};this.active=a;
      if(hold==='default')this.o.action(tap);
      this.timer=this.clock.setTimeout(()=>{if(this.active!==a)return;a.held=true;
        if(hold!=='default')this.o.action(hold);else if(repeat)this.o.action(tap);
        if(repeat&&hold==='default')this.again(a);},cfg.repeatDelay);
    }
    again(a){this.timer=this.clock.setTimeout(()=>{if(this.active!==a)return;this.o.action(a.tap);this.again(a);},this.o.settings().repeatInterval);}
    up(key){const a=this.active;if(!a||a.key!==key)return;if(!a.held&&a.hold!=='default')this.o.action(a.tap);this.cancel();}
    cancel(){if(this.timer!=null)this.clock.clearTimeout(this.timer);this.timer=null;this.active=null;}
  }
  class Touch {
    constructor(options){this.o=options;this.clock=options.clock||{now:()=>Date.now(),setTimeout:(f,m)=>setTimeout(f,m),clearTimeout:i=>clearTimeout(i)};this.points=new Map();this.active=null;this.timer=null;this.tap=null;}
    cancel(){if(this.timer!=null)this.clock.clearTimeout(this.timer);if(this.tap)this.clock.clearTimeout(this.tap.timer);this.timer=null;this.tap=null;this.points.clear();this.active=null;}
    centroid(){let x=0,y=0;for(const p of this.points.values()){x+=p.x;y+=p.y;}return{x:x/Math.max(1,this.points.size),y:y/Math.max(1,this.points.size)};}
    down(e,rect,point){
      if(e.pointerType!=='touch')return false;
      if(this.points.size>=3){this.cancel();return true;}
      this.points.set(e.pointerId,{x:e.clientX,y:e.clientY});
      if(!this.active){this.active={count:1,start:this.centroid(),end:this.centroid(),rect,point,moved:false,fired:false};}
      else{this.active.count=Math.max(this.active.count,this.points.size);this.active.start=this.centroid();this.active.end=this.centroid();}
      if(this.timer!=null)this.clock.clearTimeout(this.timer);
      const a=this.active;this.timer=this.clock.setTimeout(()=>{this.timer=null;if(this.active!==a||a.moved||!this.points.size)return;a.fired=true;this.clearTap(false);this.fire('long_press'+(a.count>1?'_'+a.count:''));},575);
      return true;
    }
    move(e){
      if(!this.points.has(e.pointerId))return false;this.points.set(e.pointerId,{x:e.clientX,y:e.clientY});
      const a=this.active;if(!a||a.fired||a.releasing)return true;a.end=this.centroid();
      if(Math.hypot(a.end.x-a.start.x,a.end.y-a.start.y)>12){a.moved=true;if(this.timer!=null)this.clock.clearTimeout(this.timer);this.timer=null;}
      return true;
    }
    clearTap(deliver){const old=this.tap;this.tap=null;if(old){this.clock.clearTimeout(old.timer);if(deliver&&old.count===1)this.o.click(old.point);}}
    fire(key){const value=this.o.settings().touch[key];if(value&&value!=='none'&&value!=='default')this.o.action(value);}
    up(e){
      if(!this.points.has(e.pointerId))return false;
      this.move(e);if(this.active)this.active.releasing=true;this.points.delete(e.pointerId);
      if(this.timer!=null)this.clock.clearTimeout(this.timer);this.timer=null;if(this.points.size)return true;
      const a=this.active;this.active=null;if(this.timer!=null)this.clock.clearTimeout(this.timer);this.timer=null;
      if(!a||a.fired)return true;
      const cfg=this.o.settings(),dx=a.end.x-a.start.x,dy=a.end.y-a.start.y;
      if(a.moved){
        this.clearTap(false);if(Math.max(Math.abs(dx),Math.abs(dy))<35)return true;
        let direction=Math.abs(dx)>Math.abs(dy)?dx>0?'right':'left':dy>0?'down':'up',edge='';
        if(a.count===1&&cfg.edgeSize){const x=a.start.x-a.rect.left,y=a.start.y-a.rect.top;
          if(direction==='right'&&x<=cfg.edgeSize)edge='left';else if(direction==='left'&&x>=a.rect.width-cfg.edgeSize)edge='right';
          else if(direction==='down'&&y<=cfg.edgeSize)edge='top';else if(direction==='up'&&y>=a.rect.height-cfg.edgeSize)edge='bottom';}
        this.fire(edge?'edge_'+edge:'swipe_'+direction+(a.count>1?'_'+a.count:''));return true;
      }
      if(a.count===1&&cfg.hotspotSize){const x=a.start.x-a.rect.left,y=a.start.y-a.rect.top,s=cfg.hotspotSize;
        const corner=(y<s?'top':y>a.rect.height-s?'bottom':'')+'_'+(x<s?'left':x>a.rect.width-s?'right':'');
        const hotspot=cfg.touch['hotspot_'+corner];if(hotspot&&hotspot!=='none'&&hotspot!=='default'){this.clearTap(false);this.o.action(hotspot);return true;}}
      if(this.tap&&this.tap.count===a.count&&this.clock.now()-this.tap.at<=320&&Math.hypot(this.tap.x-a.start.x,this.tap.y-a.start.y)<35){this.clearTap(false);this.fire('double_tap'+(a.count>1?'_'+a.count:''));return true;}
      this.clearTap(true);const pending={point:a.point,count:a.count,at:this.clock.now(),x:a.start.x,y:a.start.y};
      pending.timer=this.clock.setTimeout(()=>{if(this.tap!==pending)return;this.tap=null;if(a.count===1)this.o.click(a.point);},320);this.tap=pending;
      return true;
    }
  }
  class Gamepads {
    constructor(options){this.o=options;this.pressed=new Set();this.padIndex=null;}
    cancel(){if(this.pressed.size&&this.o.cancel)this.o.cancel();this.pressed.clear();this.padIndex=null;}
    poll(pads){
      const pad=Array.from(pads||[]).find(p=>p&&p.connected&&p.mapping==='standard');
      if(!pad){this.cancel();return;}
      if(this.padIndex!==null&&this.padIndex!==pad.index)this.cancel();this.padIndex=pad.index;
      const next=new Set();for(let i=0;i<GAMEPAD.length;i++)if(pad.buttons[i]&&(pad.buttons[i].pressed||pad.buttons[i].value>.55))next.add(i);
      const x=Number(pad.axes&&pad.axes[0])||0,y=Number(pad.axes&&pad.axes[1])||0;
      if(x<-.55)next.add(14);if(x>.55)next.add(15);if(y<-.55)next.add(12);if(y>.55)next.add(13);
      for(const id of this.pressed)if(!next.has(id))this.o.event('keyup',...GAMEPAD[id]);
      for(const id of next)if(!this.pressed.has(id))this.o.event('keydown',...GAMEPAD[id]);
      this.pressed=next;
    }
  }
  // The same stock STV Time Scroll sequence as Android. This is not a guessed
  // byte seek or a fabricated DVD rate. Only use after a fresh, exact-UI
  // IsShowingDVDMenu=false read; authored menus retain normal directional keys.
  class DvdKeys {
    constructor(options){this.o=options;this.clock=options.clock||{setTimeout:(f,m)=>setTimeout(f,m),clearTimeout:i=>clearTimeout(i)};this.scrolling=false;this.active=null;this.timer=null;this.generation=0;}
    stopRepeat(){if(this.timer!=null)this.clock.clearTimeout(this.timer);this.timer=null;this.active=null;}
    emit(commands){if(this.o.batch)return this.o.batch(commands);for(const command of commands)this.o.send(command);}
    cancel(send=false){this.generation++;this.stopRepeat();if(this.scrolling&&send)this.o.send(7);this.scrolling=false;}
    // Portable transport equivalent: search the STV timeline without asking
    // the HLS converter to decode stock extender I-only/reverse trick packets.
    // Return ordered commands so the caller can guard their source/receipts.
    transport(command){
      if(command===8||command===9){
        this.stopRepeat();
        if(!this.scrolling)this.generation++;
        const commands=this.scrolling?[command]:[7,10,command];
        this.scrolling=true;return commands;
      }
      if(this.scrolling&&[20,6,7,59,75].includes(command)){
        this.stopRepeat();this.scrolling=false;
        if(command!==20)this.generation++;
        return [command===20?10:7];
      }
      return null;
    }
    down(key){
      if(key==='MediaFastForward'||key==='MediaRewind'){
        if(this.active===key)return true;
        this.emit(this.transport(key==='MediaFastForward'?8:9));
        this.active=key;
        const again=()=>{if(this.active!==key)return;this.emit([key==='MediaFastForward'?8:9]);this.timer=this.clock.setTimeout(again,250);};
        this.timer=this.clock.setTimeout(again,420);return true;
      }
      if(['Enter','Escape','MediaPlay','MediaPlayPause','MediaPause'].includes(key)&&this.scrolling){
          this.stopRepeat();if(key!=='Enter')this.generation++;this.emit([key==='Enter'?10:7]);this.scrolling=false;return true;
      }
      if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(key))return false;
      if(this.active===key)return true;this.stopRepeat();this.active=key;
      const horizontal=key==='ArrowLeft'||key==='ArrowRight';
      const command=horizontal?(key==='ArrowRight'?8:9):(key==='ArrowUp'?65:66);
      // Stock UserEvent.TIME_SCROLL is10;15 is TV and merely opens the OSD.
      // Enter/commit must send the SAME Time Scroll toggle, never TV.
      if(horizontal){if(!this.scrolling)this.generation++;const commands=this.scrolling?[command]:[7,10,command];this.scrolling=true;this.emit(commands);}
      const again=()=>{if(this.active!==key)return;this.emit([command]);this.timer=this.clock.setTimeout(again,horizontal?250:1000);};
      this.timer=this.clock.setTimeout(again,horizontal?420:1000);return true;
    }
    up(key){if(this.active!==key)return false;this.stopRepeat();return true;}
  }
  return {ACTIONS,CONTEXTS,KEYS,TOUCH,GAMEPAD,normalize,keyAction,playbackMenuHint,dvdMenuObservation,dvdFullscreenPresentation,Keys,Touch,Gamepads,DvdKeys};
});
