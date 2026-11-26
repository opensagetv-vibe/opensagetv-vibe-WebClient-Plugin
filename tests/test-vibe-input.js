'use strict';
const assert=require('node:assert/strict'),I=require('../src/main/webapp/js/miniclient-input.js'),Clock=require('./test-miniclient-core.js');
let n=0;function test(name,fn){fn();console.log('PASS '+name);n++;}
test('mapping normalization strips injected keys/actions and clamps repeat bounds',()=>{
 const x=I.normalize({keys:{default:{ArrowLeft:'9999',Enter:'remote',bad:'2'}},touch:{swipe_left:'eval'},repeatInterval:0,repeatDelay:Infinity});
 assert.equal(x.keys.default.ArrowLeft,'default');assert.equal(x.keys.default.Enter,'remote');assert.equal(x.keys.default.bad,undefined);assert.equal(x.touch.swipe_left,'default');assert.equal(x.repeatInterval,80);assert.equal(x.repeatDelay,420);
});
test('context inheritance preserves explicit disable and hold actions',()=>{
 const x=I.normalize({keys:{default:{ArrowLeft:'62','Enter:hold':'remote'},dvd:{ArrowLeft:'none'}}});
 assert.equal(I.keyAction(x,'playing','ArrowLeft'),'62');assert.equal(I.keyAction(x,'dvd','ArrowLeft'),'none');assert.equal(I.keyAction(x,'dvd','Enter',true),'remote');
});

test('portable special keys preserve explicit mappings without destructive defaults',()=>{
 const keys=['BrowserSearch','Delete','Insert','ColorF0Red','ColorF1Green','ColorF2Yellow','ColorF3Blue','ChannelUp','ChannelDown'];
 const defaults=I.normalize({});assert.equal(new Set(I.KEYS).size,I.KEYS.length);
 for(const key of keys){assert(I.KEYS.includes(key));assert.equal(I.keyAction(defaults,'playing',key),'default');}
 const config=I.normalize({keys:{default:{BrowserSearch:'40',Delete:'83',Insert:'none',ColorF0Red:'28',ColorF1Green:'24',ColorF2Yellow:'18',ColorF3Blue:'29',ChannelUp:'11',ChannelDown:'12'},paused:{Delete:'none'}}});
 for(const [key,action] of Object.entries(config.keys.default))assert.equal(I.keyAction(config,'playing',key),action);
 assert.equal(I.keyAction(config,'paused','Delete'),'none');
 assert.equal(I.keyAction(defaults,'playing','Backspace'),'default');
 assert.equal(I.normalize({keys:{default:{Delete:'9999'}}}).keys.default.Delete,'default');
});
test('tap and hold are mutually exclusive; release is not a second tap',()=>{
 const clock=new Clock(),calls=[],keys=new I.Keys({clock,settings:()=>I.normalize({}),action:x=>calls.push(x)});
 keys.down('Enter','20','remote',false);clock.advance(100);assert.deepEqual(calls,[]);keys.up('Enter');assert.deepEqual(calls,['20']);
 keys.down('Enter','20','remote',false);clock.advance(420);keys.up('Enter');assert.deepEqual(calls,['20','remote']);
});
test('repeat is bounded by configured cadence and cancels across focus/lifecycle',()=>{
 const clock=new Clock(),calls=[],keys=new I.Keys({clock,settings:()=>I.normalize({repeatDelay:200,repeatInterval:100}),action:x=>calls.push(x)});
 keys.down('ArrowRight','3','default',true);keys.down('ArrowRight','3','default',true);clock.advance(199);assert.equal(calls.length,1);
 clock.advance(201);assert.equal(calls.length,4);keys.cancel();clock.advance(5000);assert.equal(calls.length,4);
});
function touch(){const clock=new Clock(),calls=[],cfg=I.normalize({}),rect={left:0,top:0,width:500,height:400};
 const t=new I.Touch({clock,settings:()=>cfg,action:x=>calls.push(x),click:()=>calls.push('click')});
 const e=(id,x=200,y=200)=>({pointerId:id,pointerType:'touch',clientX:x,clientY:y});return{clock,calls,cfg,rect,t,e};}
test('touch hold opens controls once and never clicks underneath',()=>{const f=touch();f.t.down(f.e(1),f.rect,{});f.clock.advance(575);f.t.up(f.e(1));f.clock.advance(1000);assert.deepEqual(f.calls,['remote']);});
test('single swipe sends Android directional default, not mouse drag/click',()=>{const f=touch();f.t.down(f.e(1),f.rect,{});f.t.up(f.e(1,140));f.clock.advance(1000);assert.deepEqual(f.calls,['2']);});
test('double tap sends Options without selecting the underlying item',()=>{const f=touch();for(let i=0;i<2;i++){f.t.down(f.e(1),f.rect,{});f.t.up(f.e(1));f.clock.advance(100);}assert.deepEqual(f.calls,['29']);});
test('multi-finger lifting does not misinterpret spread fingers as a swipe',()=>{const f=touch();f.t.down(f.e(1,170),f.rect,{});f.t.down(f.e(2,230),f.rect,{});f.t.up(f.e(1,170));f.t.up(f.e(2,230));f.clock.advance(1000);assert.deepEqual(f.calls,[]);});
test('two-finger swipe uses Scroll, three-finger swipe uses Home',()=>{
 for(const count of [2,3]){const f=touch();for(let i=1;i<=count;i++)f.t.down(f.e(i,180+i*10),f.rect,{});
 for(let i=1;i<=count;i++)f.t.move(f.e(i,280+i*10));for(let i=1;i<=count;i++)f.t.up(f.e(i,280+i*10));f.clock.advance(1000);assert.deepEqual(f.calls,[count===2?'106':'28']);}
});
test('edge and hotspot defaults follow Android TouchPreferences',()=>{
 const f=touch();f.t.down(f.e(1,490,200),f.rect,{});f.t.up(f.e(1,400,200));assert.deepEqual(f.calls,['remote']);
 const g=touch();g.t.down(g.e(1,20,20),g.rect,{});g.t.up(g.e(1,20,20));assert.deepEqual(g.calls,['keyboard']);
});
test('cancel discards pending tap/hold and cannot leak input after retirement',()=>{const f=touch();f.t.down(f.e(1),f.rect,{});f.t.up(f.e(1));f.t.cancel();f.clock.advance(5000);assert.deepEqual(f.calls,[]);});
test('standard gamepad buttons/stick transitions are edge-owned and disconnect cancels',()=>{
 const events=[],g=new I.Gamepads({event:(...e)=>events.push(e),cancel:()=>events.push(['cancel'])});
 const pad={index:0,connected:true,mapping:'standard',axes:[0,0],buttons:Array.from({length:16},()=>({pressed:false,value:0}))};
 pad.buttons[0].pressed=true;g.poll([pad]);g.poll([pad]);assert.deepEqual(events,[['keydown','GamepadA','Enter']]);
 pad.buttons[0].pressed=false;pad.axes[0]=.8;g.poll([pad]);assert.deepEqual(events.slice(1),[['keyup','GamepadA','Enter'],['keydown','GamepadRight','ArrowRight']]);
 g.poll([]);assert.deepEqual(events.at(-1),['cancel']);assert.equal(g.pressed.size,0);
});
test('stock and SageMC playback hints preserve popup/text/menu navigation',()=>{
 for(const menu of ['VideoOSD','DVDOSD','TVOSD','OSD','MediaPlayer','MediaPlayer OSD','MC MediaPlayer OSD']){
  assert(I.playbackMenuHint('menuName:'+menu+',popupName:null,hasTextInput:false'));
  assert.equal(I.playbackMenuHint('menuName:'+menu+',popupName:DVD Options'),false);
  assert.equal(I.playbackMenuHint('menuName:'+menu+',popupName:null,hasTextInput:true'),false);
 }
 for(const hint of ['',null,'menuName:Main Menu','menuName:MC MediaPlayer OSD Settings','popupName:null'])assert.equal(I.playbackMenuHint(hint),false);
});
test('unavailable DVD state cannot erase fresh truth or extend its deadline',()=>{
 let s=I.dvdMenuObservation(null,0,false,10000);assert.deepEqual(s,{value:false,at:10000});
 s=I.dvdMenuObservation(s.value,s.at,null,11100);assert.deepEqual(s,{value:false,at:10000});
 s=I.dvdMenuObservation(s.value,s.at,undefined,11500);assert.deepEqual(s,{value:null,at:10000});
 s=I.dvdMenuObservation(false,10000,true,11100);assert.deepEqual(s,{value:true,at:11100});
 assert.deepEqual(I.dvdMenuObservation(null,0,null,12000),{value:null,at:0});
});
test('DVD arrows use stock Time Scroll, not a rate or guessed seek; Select accepts',()=>{
 const clock=new Clock(),calls=[],dvd=new I.DvdKeys({clock,send:x=>calls.push(x)});
 dvd.down('ArrowRight');dvd.up('ArrowRight');dvd.down('ArrowLeft');dvd.up('ArrowLeft');dvd.down('Enter');
 assert.deepEqual(calls,[7,10,8,9,10]);assert.equal(dvd.scrolling,false);
 assert.equal(I.ACTIONS[10],'Time Scroll');assert.equal(I.ACTIONS[15],'TV');
 assert.equal(I.ACTIONS[63],'Live TV');assert.equal(I.ACTIONS[42],'Library');
});
test('DVD chapters require hold and repeat only while held; Play cancels scrolling',()=>{
 const clock=new Clock(),calls=[],dvd=new I.DvdKeys({clock,send:x=>calls.push(x)});
 dvd.down('ArrowUp');clock.advance(999);dvd.up('ArrowUp');assert.deepEqual(calls,[]);
 dvd.down('ArrowDown');clock.advance(2000);dvd.up('ArrowDown');assert.deepEqual(calls,[66,66]);
 dvd.down('ArrowRight');dvd.down('MediaPlayPause');assert.deepEqual(calls.slice(-4),[7,10,8,7]);
});
test('DVD lifecycle cancellation retires repeat without sending commands into another UI',()=>{
 const clock=new Clock(),calls=[],dvd=new I.DvdKeys({clock,send:x=>calls.push(x)});
 dvd.down('ArrowRight');clock.advance(420);dvd.cancel(false);clock.advance(10000);assert.deepEqual(calls,[7,10,8,8]);assert.equal(dvd.scrolling,false);
});
test('DVD transport search batches native Time Scroll without claiming video rate',()=>{
 const dvd=new I.DvdKeys({send:()=>{}});
 assert.deepEqual(dvd.transport(8),[7,10,8]);assert.deepEqual(dvd.transport(8),[8]);
 assert.deepEqual(dvd.transport(9),[9]);assert.deepEqual(dvd.transport(20),[10]);
 assert.equal(dvd.scrolling,false);assert.equal(dvd.transport(20),null);
 for(const cancel of [6,7,59,75]){dvd.transport(9);assert.deepEqual(dvd.transport(cancel),[7]);assert.equal(dvd.scrolling,false);}
 assert.equal(dvd.transport(89),null);
});
test('DVD held transport searches repeat while pressed and stop on release',()=>{
 const clock=new Clock(),calls=[],dvd=new I.DvdKeys({clock,send:c=>calls.push(c)});
 dvd.down('MediaFastForward');dvd.down('MediaFastForward');clock.advance(670);dvd.up('MediaFastForward');
 assert.deepEqual(calls,[7,10,8,8,8]);clock.advance(5000);assert.equal(calls.length,5);
 dvd.down('MediaRewind');dvd.up('MediaRewind');assert.deepEqual(calls.slice(-1),[9]);
 dvd.down('Enter');assert.deepEqual(calls.slice(-1),[10]);assert.equal(dvd.scrolling,false);
});
test('DVD optional batch seam preserves Play-arm-move atomic intent',()=>{
 const clock=new Clock(),batches=[],dvd=new I.DvdKeys({clock,send:()=>{throw Error('Must use ordered batch');},batch:c=>batches.push(c)});
 dvd.down('ArrowRight');dvd.up('ArrowRight');dvd.down('Enter');
 dvd.down('MediaRewind');dvd.up('MediaRewind');dvd.down('MediaPlay');
 assert.deepEqual(batches,[[7,10,8],[10],[7,10,9],[7]]);
});
test('qualified native DVD OSD can display fullscreen without mutating stale preview bounds',()=>{
 const p={kind:'preview',rect:[67,481,350,161],nativeRect:[67,481,350,161]},before=JSON.stringify(p);
 const s={active:true,dvd:true,state:false,at:1000,now:2000,menu:'menuName:MediaPlayer OSD,popupName:,hasTextInput:false'};
 assert.equal(I.dvdFullscreenPresentation(p,s),true);assert.equal(I.dvdFullscreenPresentation(p,{...s,state:true}),true);
 assert.equal(JSON.stringify(p),before);
});
test('DVD fullscreen ownership rejects other content native viewport popup unknown and stale state',()=>{
 const p={kind:'preview'},s={active:true,dvd:true,state:false,at:1000,now:2000,menu:'menuName:MC MediaPlayer OSD,popupName:,hasTextInput:false'};
 for(const change of [{active:false},{dvd:false},{state:null},{state:'false'},{now:2500},{now:999},{now:NaN},{at:Infinity},
  {menu:'menuName:Dynamic Menu by nielm,popupName:,hasTextInput:false'},
  {menu:'menuName:MediaPlayer OSD,popupName:Stopped,hasTextInput:false'},
  {menu:'menuName:MediaPlayer OSD,popupName:,hasTextInput:true'},{menu:''}])assert.equal(I.dvdFullscreenPresentation(p,{...s,...change}),false,JSON.stringify(change));
 for(const kind of ['native','fullscreen',undefined])assert.equal(I.dvdFullscreenPresentation({kind},s),false);
 assert.equal(I.dvdFullscreenPresentation(null,s),false);
});
console.log(n+' portable Vibe input groups PASS');
