'use strict';
const assert=require('assert'),Core=require('../src/main/webapp/js/miniclient-core.js');
const complete={ReadableStream:function(){},TextDecoder:function(){}};
for(const userAgent of ['iPhone AppleWebKit Safari','iPad AppleWebKit','iPod AppleWebKit','iPhone CriOS/150'])
  assert.equal(Core.eventDelivery({...complete,navigator:{userAgent}}),'long-poll');
assert.equal(Core.eventDelivery({...complete,navigator:{platform:'MacIntel',maxTouchPoints:5}}),'long-poll');
for(const userAgent of ['Macintosh AppleWebKit Safari','Android Chrome/153','Windows Chrome/153'])
  assert.equal(Core.eventDelivery({...complete,navigator:{userAgent}}),'stream');
assert.equal(Core.eventDelivery({TextDecoder:function(){}}),'long-poll');
assert.equal(Core.eventDelivery({ReadableStream:function(){}}),'long-poll');
console.log('PASS 10 event-delivery policy checks: iOS finite polling, desktop/Android streaming, missing API fallback');
