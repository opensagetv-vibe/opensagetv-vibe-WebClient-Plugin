'use strict';
const assert=require('assert'),Core=require('../src/main/webapp/js/miniclient-core.js');
assert.strictEqual(Core.remoteCommand('ArrowRight'),3);
assert.strictEqual(Core.remoteCommand('MediaPlayPause'),59);
assert.strictEqual(Core.remoteCommand('7'),37);
assert.strictEqual(Core.remoteCommand('G'),18);
assert.strictEqual(Core.remoteCommand('F12'),undefined);
const boxes=[{id:'a',x:0,y:0,width:44,height:44},{id:'b',x:44,y:0,width:44,height:44},
  {id:'c',x:44,y:44,width:44,height:44},{id:'d',x:0,y:88,width:44,height:44}];
assert.strictEqual(Core.spatialTarget(boxes,'a','ArrowRight'),'b');
assert.strictEqual(Core.spatialTarget(boxes,'a','ArrowDown'),'d');
assert.strictEqual(Core.spatialTarget(boxes,'b','ArrowDown'),'c');
assert.strictEqual(Core.spatialTarget(boxes,'c','ArrowLeft'),'a'); // stable equal-distance tie
assert.strictEqual(Core.spatialTarget(boxes.map(b=>b.id==='d'?Object.assign({},b,{y:75}):b),'c','ArrowLeft'),'d');
assert.strictEqual(Core.spatialTarget(boxes,'a','ArrowLeft'),'a');
assert.strictEqual(Core.spatialTarget([],'a','ArrowDown'),'a');
console.log('PASS mobile keyboard mapping and sparse-row/column geometric focus (12 assertions)');
