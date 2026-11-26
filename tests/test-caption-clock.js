'use strict';
const assert=require('node:assert/strict'),Controller=require('../src/main/webapp/js/miniclient-captions.js');
const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));
(async()=>{
 let fragment=0,recording=20000,rendered=[],queries=[],calls=0;
 const c=new Controller({timeMs:()=>fragment,sourceTimeMs:()=>recording,subtitleFetch:async p=>{queries.push(p);return ++calls===1?{cues:[{kind:'text',owner:'local_broadcast',ptsMs:20500,text:'future cue',durationMs:500}]}:{cues:[]};},render:text=>rendered.push(text)});
 c.start({hlsSession:'seeked',streamSettings:{requested:{captions:'teletext',captionOffsetMs:0}}});await wait(60);
 assert(queries[0].timeMs===21200);assert(!rendered.includes('future cue'),'lookahead must not display early');
 recording=20500;await wait(60);assert.equal(rendered.at(-1),'future cue','use recording clock after seek, not fragment zero');
 recording=21000;await wait(60);assert.equal(rendered.at(-1),'','expiry follows source clock even without a fetch');
 c.stop();let release;const pending=new Promise(resolve=>{release=resolve;});c.o.subtitleFetch=()=>pending;
 c.start({hlsSession:'retired',streamSettings:{requested:{captions:'teletext'}}});c.stop();release({cues:[{kind:'text',owner:'local_broadcast',ptsMs:0,text:'stale'}]});await wait(30);assert(!rendered.includes('stale'));
 console.log('PASS caption33ms presentation, recording clock, no-early lookahead, expiry and stale-fetch rejection (5 assertions)');
})().catch(error=>{console.error(error);process.exitCode=1;});
