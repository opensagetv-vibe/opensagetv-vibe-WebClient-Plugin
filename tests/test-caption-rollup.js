'use strict';
const assert=require('node:assert/strict');global.window=global;
require('../src/main/webapp/js/atsc-captions.js');
let out='',meta=null,pts=0,checks=0;
const p=new SageAtscCaptions({onCaption:(text,service,m)=>{out=text;meta=m;}});
function check(value,message){assert.ok(value,message);checks++;}
function pair(a,b){pts+=50;p.pushCcData(Uint8Array.of(0xfc,a,b),pts);p.updateTime(pts);}
function text(s){for(let i=0;i<s.length;i+=2)pair(s.charCodeAt(i),s.charCodeAt(i+1)||0);}
pair(0x14,0x25);text('FIRST');
check(meta.mode==='rollup'&&meta.rows===2&&meta.columns===32,'RU2 fixed row/column metadata');
check(meta.lines.join('|')==='|FIRST','new text stays in bottom writing row');
pair(0x14,0x2d);
check(meta.lines.join('|')==='FIRST|','CR moves old row up before new characters');
pair(0x14,0x2d);
check(meta.lines.join('|')==='FIRST|','duplicated CR must not scroll twice');
pair(0x14,0x60);text('SECOND');pair(0x14,0x60);
check(meta.lines.join('|')==='FIRST|SECOND','repeated PAC is not a roll-up newline');
pair(0x14,0x2d);text('THIRD');
check(meta.lines.join('|')==='SECOND|THIRD','drop oldest row at RU2 capacity');
pair(0x14,0x2d);text('X'.repeat(40));
check(meta.lines.at(-1).length===32,'row bounded to32 cells, no marquee');
pair(0x14,0x26);pair(0x14,0x27);
check(meta.rows===4&&meta.lines.length===4,'RU3/RU4 bounded row count');
pair(0x14,0x2c);check(out==='','explicit source erase immediate');
p.resetForSeek();out='';pair(0x14,0x20);text('POP');
check(out==='','pop-on memory remains hidden before EOC');
pair(0x14,0x2f);check(out==='POP'&&meta.mode==='popon','pop-on EOC unaffected');
const last=pts;p.updateTime(last+15999);check(out==='POP','caption retained before16s');
for(let i=0;i<5;i++)p.updateTime(last+15999);
check(out==='POP','paused playback clock does not expire captions');
p.updateTime(last+16000);check(out==='','quiet commercial clears stale caption');
p.resetForSeek();pts=20000;pair(0x14,0x25);text('NEW');
check(out==='NEW','seek reset and next real captions resume');
p.setEnabled(false);check(out==='','Off clears immediately');
p.setEnabled(true);check(out==='NEW','On restores in-time caption');
pts+=16000;text('BACK');check(out==='BACK','608 expired rows do not reappear when captions resume');

let dOut='',dMeta;const d=new SageAtscCaptions({service:'708-1',onCaption:(t,s,m)=>{dOut=t;dMeta=m;}});
function send708(bytes,time){const block=[0x20|bytes.length,...bytes];if(block.length%2===0)block.push(0);d.pushDtvcc(3,(block.length+1)/2,block[0],time);for(let i=1;i<block.length;i+=2)d.pushDtvcc(2,block[i],block[i+1],time);d.updateTime(time);}
// Visible bottom-center window:2rows x8columns. Encoded sizes are minus one.
send708([0x98,0x30,74,104,0x71,7,0,...Buffer.from('FIRST')],0);
send708([13,...Buffer.from('SECOND')],1000);
send708([13,...Buffer.from('THIRD')],2000);
check(dOut==='SECOND\nTHIRD','708 CR scrolls at configured window bottom');
check(dMeta.windows[0].lines.join('|')==='SECOND|THIRD','708 fixed presentation lines');
send708([13,...Buffer.from('123456789012')],3000);
check(dOut==='THIRD\n12345678','708 column bound does not overwrite or expand');
d.updateTime(19000);check(dOut==='','708 stale caption clears on playback clock');
send708([...Buffer.from('BACK')],20000);check(dOut==='BACK','708 expired rows do not reappear when captions resume');
console.log(`PASS WEB-034 ${checks} roll-up/column/CR/PAC/pop-on/erase/pause/seek/stale tests`);
