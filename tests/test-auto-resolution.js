'use strict';
const assert=require('node:assert/strict');
const S=require('../src/main/webapp/js/miniclient-streaming.js');
let count=0;
function test(name,fn){fn();count++;console.log('PASS '+name);}
test('Retina phone physical short edge gives1080 independent of orientation',()=>{
  assert.equal(S.automaticResolution({screen:{width:393,height:852},devicePixelRatio:3}),'1080');
  assert.equal(S.automaticResolution({screen:{width:852,height:393},devicePixelRatio:3}),'1080');
});
test('standard HD/4K screens resolve existing numeric wire caps',()=>{
  for(const [w,h,dpr,expected] of [[1920,1080,1,'1080'],[1280,720,1,'720'],[1920,1080,2,'2160'],[640,360,1,'480']])
    assert.equal(S.automaticResolution({screen:{width:w,height:h},devicePixelRatio:dpr}),expected);
});
test('missing and invalid dimensions/density have bounded fallback',()=>{
  assert.equal(S.automaticResolution(),'720');
  assert.equal(S.automaticResolution({screen:{width:NaN,height:Infinity},devicePixelRatio:NaN,innerWidth:1280,innerHeight:720}),'720');
  assert.equal(S.automaticResolution({screen:{width:100000,height:100000},devicePixelRatio:1000}),'2160');
});
test('Auto survives profile normalization but server receives supported number',()=>{
  const profile=S.normalize({resolution:'auto',videoKbps:1000});
  assert.equal(profile.resolution,'auto');
  assert.equal(S.toParams(profile,{autoResolution:'1080'}).stream_resolution,'1080');
  assert.equal(profile.resolution,'auto');
  assert.equal(S.toParams(profile).stream_resolution,'720');
});
test('explicit Copy plus Auto does not add an unsupported scaling request',()=>{
  assert.equal(S.toParams({videoMode:'copy',resolution:'auto'},{autoResolution:'1080'}).stream_resolution,'source');
});
test('manual heights and existing Source default are unchanged',()=>{
  assert.equal(S.DEFAULTS.resolution,'source');
  for(const resolution of ['source','480','720','1080','2160'])assert.equal(S.toParams({resolution},{autoResolution:'1080'}).stream_resolution,resolution);
});
test('capability-only limit does not leak into persistent profile or wire keys',()=>{
  assert.equal(S.normalize({resolution:'auto',autoResolution:'1080'}).autoResolution,undefined);
  assert.equal(S.toParams({resolution:'auto'},{autoResolution:'1080'}).stream_autoResolution,undefined);
});
console.log('Automatic device video height: '+count+' PASS');
