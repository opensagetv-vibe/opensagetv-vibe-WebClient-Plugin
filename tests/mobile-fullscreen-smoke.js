'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const context={window:{}};vm.runInNewContext(fs.readFileSync('src/main/webapp/js/miniclient-mobile.js','utf8'),context);
const show=context.window.SageMiniMobile.showPlayback;
(async()=>{
 let reads=0,shows=0,waits=0,active=true;
 const options={current:()=>active,read:async()=>({ready:++reads>1,layout:shows?'fullscreen':'preview'}),show:async()=>{shows++;return{ok:true}},wait:async()=>{waits++}};
 await show(options);assert.deepEqual([reads,shows,waits],[3,1,2]);
 await show({...options,read:async()=>({ready:true,layout:'fullscreen'})});assert.equal(shows,1);
 await assert.rejects(show({...options,read:async()=>({ready:false,layout:'preview'})}),/dialog/);assert.equal(shows,1);
 await assert.rejects(show({...options,read:async()=>({ready:true,layout:'unknown'})}),/dialog/);assert.equal(shows,1);
 active=false;await assert.rejects(show(options),/cancelled/);active=true;
 await assert.rejects(show({...options,read:async()=>{active=false;return{ready:true,layout:'preview'}}}),/cancelled/);assert.equal(shows,1);active=true;
 let unknown=0;await assert.rejects(show({...options,read:async()=>({ready:true,layout:'preview'}),show:async()=>{unknown++;throw Error('delivery unknown')}}),/unknown/);assert.equal(unknown,1);
 let refused=0;await assert.rejects(show({...options,read:async()=>({ready:true,layout:'preview'}),show:async()=>{refused++;return{ok:false}}}),/changed/);assert.equal(refused,1);
 let delayed=0;await assert.rejects(show({...options,read:async()=>({ready:true,layout:'preview'}),show:async()=>{delayed++;return{ok:true}}}),/dialog/);assert.equal(delayed,1);
 console.log('PASS 9 fullscreen intent cases: delayed source/fullscreen/modal/unknown/cancel/retired/no replay/refused/unconfirmed-view');
})().catch(error=>{console.error(error);process.exitCode=1});
