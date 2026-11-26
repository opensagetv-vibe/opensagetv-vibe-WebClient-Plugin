'use strict';
// Pure shared-choice/profile checks; not hardware execution certification.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const Streaming=require('../src/main/webapp/js/miniclient-streaming.js');
const names=['auto','qsv','nvenc','vaapi','amf','videotoolbox'];
const html=fs.readFileSync(path.join(__dirname,'../src/main/webapp/miniclient.html'),'utf8');
assert.match(html,/Hardware Encoder<select id="stream_encoder">/);
const options=html.match(/<select id="stream_encoder">([\s\S]*?)<\/select>/)[1];
for(const name of [...names,'software']){
  assert.ok(options.includes('value="'+name+'"'));
  for(const player of ['hls','mpegts']){
    const saved=Streaming.normalize({encoder:name,player});
    assert.equal(saved.encoder,name);
    assert.equal(Streaming.toParams(saved).stream_encoder,name);
    assert.equal(Streaming.normalize(JSON.parse(JSON.stringify(saved))).encoder,name);
    assert.equal(Streaming.normalize({...saved,videoMode:'copy'}).encoder,name);
  }
}
assert.equal(Streaming.normalize({}).encoder,'auto');
assert.throws(()=>Streaming.normalize({encoder:'qsv;evil'}));
let android=path.join(__dirname,'../../opensagetv-vibe-android-client/source/dev/android-shared/src/main/res/values/playback_settings_arrays.xml');
if(!fs.existsSync(android))android=path.join(__dirname,'../../android-client/source/dev/android-shared/src/main/res/values/playback_settings_arrays.xml');
if(fs.existsSync(android)){
  const xml=fs.readFileSync(android,'utf8');
  const values=[...xml.match(/name="values_hardware_encoder">([\s\S]*?)<\/string-array>/)[1].matchAll(/<item>(.*?)<\/item>/g)].map(m=>m[1]);
  assert.deepEqual(values,names);
  assert.ok(xml.includes('Software Only'));
}
console.log('PASS shared Hardware Encoder choices, HLS/TS/Copy/profile/default preservation');
