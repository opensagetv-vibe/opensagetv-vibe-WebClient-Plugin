const assert=require('assert');
const {RuntimeQualityAdvisor}=require('../src/main/webapp/js/miniclient-experience.js');
const p=new RuntimeQualityAdvisor();
const sample=(i,changes={})=>Object.assign({source:'a',active:true,paused:false,starting:false,seeking:false,dvd:false,copy:false,now:i*3000,
  sampleId:i,sampleMs:1000,throughputKbps:2500,videoKbps:6000,ceilingKbps:6000,ahead:4},changes);
assert.equal(p.observe(sample(1)),null);assert.equal(p.observe(sample(2,{ahead:3})),null);
assert.equal(p.observe(sample(3,{ahead:1,rebuffering:true})).videoKbps,1650);
p.reset();for(let i=1;i<=20;i++)assert.equal(p.observe(sample(i,{throughputKbps:20000,ahead:0,rebuffering:true})),null);
p.reset();for(let i=1;i<10;i++)assert.equal(p.observe(sample(i,{videoKbps:2000,throughputKbps:20000,ahead:2})),null);
assert.equal(p.observe(sample(10,{videoKbps:2000,throughputKbps:20000,ahead:2})).videoKbps,2500);
for(let i=11;i<20;i++)assert.equal(p.observe(sample(i,{videoKbps:2500,throughputKbps:20000,ahead:2})),null);
p.reset();for(let i=1;i<=20;i++)assert.equal(p.observe(sample(i,{sampleId:1})),null);
p.reset();for(let i=1;i<=20;i++)assert.equal(p.observe(sample(i,{throughputKbps:null})),null);
console.log('PASS runtime policy down/up/cooldown/fast-starvation/unique-transfer/unknown timing guards');
