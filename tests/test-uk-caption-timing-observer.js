'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const Controller=require('../src/main/webapp/js/miniclient-captions.js');
const source=fs.readFileSync(__dirname+'/stock-uk-caption-field.py','utf8');
const script=[...source.matchAll(/page\.evaluate\(r"""(.*?)"""\)/gs)].map(m=>m[1]).find(s=>s.includes('SageMiniCaptions.prototype'));
const start=Controller.prototype.start,originalPoll=Controller.prototype.pollTeletext;
const field={},calls=[];let clock=10000,failClock=false;
const options={sourceTimeMs:()=>{if(failClock)throw Error('FAKE_PRIVATE');return clock},timeMs:()=>clock,
 render:function(...args){calls.push({receiver:this,args});return 'original-result'},renderBitmap:()=>17,clearBitmap:()=>{}};
const player=new Controller(options);
try{
 vm.runInNewContext('('+script+')()',{UK_FIELD:field,SageMiniCaptions:Controller});
 Controller.prototype.pollTeletext=()=>{};
 player.start({hlsSession:'test-only',streamSettings:{requested:{captions:'teletext',captionOffsetMs:1000}}});
 player.enqueue([{kind:'text',owner:'local_broadcast',ptsMs:9000,text:'FAKE_PRIVATE_CAPTION'}]);player.present(player.generation);
 assert.equal(field.captionTiming.length,1);assert.equal(field.captionTiming[0].lateMs,0);
 assert.equal(field.captionTiming[0].offsetMs,1000);assert.equal(calls.at(-1).receiver,options);
 assert.equal(options.render('another','teletext',{ptsMs:9000}),'original-result');
 player.options.captionOffsetMs=-1000;
 options.render('another','teletext',{ptsMs:11000});assert.equal(field.captionTiming.at(-1).lateMs,0);
 options.render('','teletext',{ptsMs:0});options.render('other','CC1',{ptsMs:0});
 assert.equal(field.captionTiming.length,3);
 assert.equal(field.captionClears.at(-1).kind,'teletext');
 assert.equal(field.captionClears.at(-1).clockMs,clock);
 options.clearBitmap();assert.equal(field.captionClears.at(-1).kind,'dvb');
 for(let i=0;i<100;i++)options.render('bounded','teletext',{ptsMs:11000});
 assert.equal(field.captionTiming.length,80);assert(!JSON.stringify(field).includes('FAKE_PRIVATE'));
 failClock=true;assert.equal(options.render('sample','teletext',{ptsMs:11000}),'original-result');
 assert.equal(field.captionTimingUnavailable,true);assert(!JSON.stringify(field).includes('FAKE_PRIVATE'));
 console.log('PASS actual caption-controller observer: signed clocks, receiver/return, filter, bound, payload-free and observer-error isolation');
}finally{player.stop();Controller.prototype.start=start;Controller.prototype.pollTeletext=originalPoll;}
