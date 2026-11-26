'use strict';
const assert=require('node:assert/strict');
const Core=require('../src/main/webapp/js/miniclient-core.js');
const Stream=require('../src/main/webapp/js/miniclient-streaming.js');
assert.equal(Core.normalizeSettings({showStats:true}).showStatsInfo,true);
assert.equal(Core.normalizeSettings({}).showStatsInfo,false);
assert.equal(Core.normalizeSettings({showStats:false,showStatsInfo:true}).showStatsInfo,true);
assert.equal(Core.normalizeSettings({showStats:true,showStatsInfo:false}).showStatsInfo,false);
for(const target of [30,60,90,180,300,600]){
 const cfg=Stream.mpegtsConfig(target);
 assert.equal(cfg.lazyLoadMaxDuration,target);
 assert(cfg.lazyLoadRecoverDuration>=target*.8);
 assert(cfg.lazyLoadRecoverDuration>=target-15);
 assert(cfg.lazyLoadRecoverDuration<target);
 assert.equal(cfg.liveSync,false);
}
console.log('PASS legacy stats migration, independent modes and bounded near-full TS refill');
