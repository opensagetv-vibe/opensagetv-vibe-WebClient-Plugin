'use strict';
const assert=require('node:assert/strict');
const Controller=require('../src/main/webapp/js/miniclient-captions.js');
async function check(kind,state,clearExpected){
 let text='old source page',pixels=8;
 const c=new Controller({timeMs:()=>0,render:t=>text=t,clearBitmap:()=>pixels=0,
  subtitleFetch:async()=>({cues:[{kind:'text',owner:'local_broadcast',ptsMs:1000,text:'obsolete queued page'}],[kind==='teletext'?'teletext':'dvbBitmap']:state})});
 c.id='same-producer';c.options={};c[kind]=true;
 c.queue=[{kind:'text',owner:'local_broadcast',ptsMs:2000,text:'old future page'}];
 try{
  await c[kind==='teletext'?'pollTeletext':'pollDvb'](c.generation);
  if(clearExpected){
   assert.equal(kind==='teletext'?text:pixels,kind==='teletext'?'':0,'explicit removed/disabled service clears visible output');
   assert.equal(c.queue.length,0,'retired-service cues cannot reappear later');
  }else assert.equal(kind==='teletext'?text:pixels,kind==='teletext'?'old source page':8,'unknown/legacy or valid service does not fabricate loss');
 }finally{c.stop();}
}
(async()=>{
 let count=0;
 for(const kind of ['teletext','dvb']){
  {
   let now=11000,text='current page',pixels=480;
   const c=new Controller({timeMs:()=>now,sourceTimeMs:()=>now,render:t=>text=t,clearBitmap:()=>pixels=0,
    subtitleFetch:async()=>({cues:[],[kind==='teletext'?'teletext':'dvbBitmap']:{active:true,selectedTrack:-1,services:[],selectionChangedMs:16000}})});
   c.id='same';c.options={};c[kind]=true;
   try{
    await c[kind==='teletext'?'pollTeletext':'pollDvb'](c.generation);
    assert.equal(kind==='teletext'?text:pixels,kind==='teletext'?'current page':480,'source read-ahead cannot clear a still-current service');
    now=16000;await c[kind==='teletext'?'pollTeletext':'pollDvb'](c.generation);
    assert.equal(kind==='teletext'?text:pixels,kind==='teletext'?'':0,'service retires at its source presentation time');
    count++;
   }finally{c.stop();}
  }
  for(const state of [{active:true,selectedTrack:-1,services:[]},{active:false,selectedTrack:42,services:[{trackId:42}]}]){await check(kind,state,true);count++;}
  for(const state of [null,{}, {services:[]}, {active:true,selectedTrack:'-1',services:[]}, {active:true,selectedTrack:42,services:[{trackId:42}]}]){await check(kind,state,false);count++;}
  let resolve,text='old',pixels=8;
  const c=new Controller({timeMs:()=>0,render:t=>text=t,clearBitmap:()=>pixels=0,subtitleFetch:()=>new Promise(r=>resolve=r)});
  c.id='old';c.options={};c[kind]=true;
  const pending=c[kind==='teletext'?'pollTeletext':'pollDvb'](c.generation);
  c.stop();c[kind]=true;text='replacement';pixels=16;
  resolve({cues:[],[kind==='teletext'?'teletext':'dvbBitmap']:{active:true,selectedTrack:-1,services:[]}});
  await pending;
  assert.equal(text,'replacement','late old-source reply cannot clear replacement text');
  assert.equal(pixels,16,'late old-source reply cannot clear replacement bitmap');
  assert.equal(c.pollTimer,null,'retired request does not restart polling');c.stop();count++;
 }
 console.log('PASS'+count+' broadcast service-loss production-controller cases');
})().catch(e=>{console.error(e);process.exitCode=1;});
