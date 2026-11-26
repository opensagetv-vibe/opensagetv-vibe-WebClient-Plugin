'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const Playback=require('../src/main/webapp/js/miniclient-playback.js');
const source=fs.readFileSync(__dirname+'/stock-uk-caption-field.py','utf8');
const script=[...source.matchAll(/page\.evaluate\(r"""(.*?)"""\)/gs)].map(m=>m[1]).find(s=>s.includes('SageMiniPlayback.prototype'));
const original=Playback.prototype.error,originalAlign=Playback.prototype.alignInitialCopyGap,field={};
try{
 const video={currentTime:.5,buffered:{length:1,start:()=>.5,end:()=>5},readyState:4,paused:false};
 vm.runInNewContext('('+script+')()',{UK_FIELD:field,SageMiniPlayback:Playback,videoPlane:video});
 const emitted=[],player={budget:{count:1},o:{error:message=>emitted.push(message)}};
 Playback.prototype.error.call(player,'HLS mediaError bufferAppendError');
 assert.equal(field.errors[0].kind,'HLS mediaError bufferAppendError');
 assert.equal(field.errors[0].relativeSeconds,.5);assert.equal(emitted.length,1);
 assert.equal(field.errors[0].buffered[0][1],5);assert.equal(field.errors[0].paused,false);
 Playback.prototype.error.call(player,new Error('private path/token/caption content'));
 assert.equal(field.errors[1].kind,'other');assert(!JSON.stringify(field).includes('private'));
 for(let n=0;n<30;n++)Playback.prototype.error.call(player,'[decoder] Fatal HLS error (1/6)');
 assert.equal(field.errors.length,24);assert.equal(emitted.length,32);
 assert.equal(field.errors[2].kind,'Fatal HLS error');
 field.errors=[];Object.defineProperty(video,'buffered',{get:()=>{throw Error('temporary inspection unavailable')}});
 Playback.prototype.error.call(player,'HLS mediaError bufferAppendError');
 assert.equal(emitted.length,33);assert.equal(field.observerUnavailable,true);
 console.log('PASS UK field error observer: actual production class, receiver/call preservation,24-record cap, payload-free classification');
}finally{Playback.prototype.error=original;Playback.prototype.alignInitialCopyGap=originalAlign;}
