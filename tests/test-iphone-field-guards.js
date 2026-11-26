/* Offline Safari retains currentSrc after load(): no decoder/source binding. */
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('tests/iphone-codec-field-start.js','utf8');
function fixture(change={}){
 const state={assigned:null,srcObject:null,readyState:0,paused:true,...change};let opened=0;
 const ctx={document:{visibilityState:'visible',activeElement:{id:''},createElement:()=>({style:{}}),body:{appendChild:()=>opened++}},
  localStorage:{getItem:key=>key==='sagetvWebMiniClientId'?'123C8282E1EE':'original'},window:{},
  videoPlane:{currentSrc:'http://example.invalid/old.m3u8',getAttribute:()=>state.assigned,
   srcObject:state.srcObject,readyState:state.readyState,paused:state.paused},calibrationPanel:{hidden:true}};
 return{run:()=>vm.runInNewContext(source,ctx),opened:()=>opened};
}
let f=fixture();assert.equal(f.run().oneFrameOpened,true);assert.equal(f.opened(),1);
for(const change of [{assigned:'new.m3u8'},{srcObject:{}},{readyState:1},{readyState:4},{paused:false}]){
 f=fixture(change);assert.throws(f.run,/Require exact stopped phone/);assert.equal(f.opened(),0);
}
console.log('PASS6 physical field unloaded-video guards; no phone/server input');
