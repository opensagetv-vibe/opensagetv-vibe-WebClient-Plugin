'use strict';
const assert = require('node:assert/strict');
global.window = global;
require('../src/main/webapp/js/atsc-captions.js');
let checks = 0;
function check(value, message) { assert.ok(value, message); checks++; console.log('PASS ' + message); }
function decoder(service = 'CC1') {
  const seen = [];
  const d = new SageAtscCaptions({service, onCaption: (text, selected, meta) => seen.push({text, selected, meta})});
  return {d, seen, text: () => seen.at(-1)?.text || ''};
}
function pair(d, field, first, second, time = 1000) {
  d.pushCcData(Uint8Array.of(0xfc | field, first, second), time);
}
function pop(d, channel, text, time = 1000) {
  const field = channel >= 3 ? 1 : 0, control = channel % 2 ? 0x14 : 0x1c;
  pair(d, field, control, 0x20, time);
  for (let i = 0; i < text.length; i += 2) pair(d, field, text.charCodeAt(i), text.charCodeAt(i + 1) || 0, time);
  pair(d, field, control, 0x2f, time);
  d.updateTime(time);
}
const empty = decoder();
pop(empty.d, 1, 'FIRST');
check(empty.text() === 'FIRST', 'selected service begins with real decoded text');
empty.d.setService('CC2');
check(empty.text() === '', 'switch to a service with no due cues immediately clears prior service');
check(empty.d.lastTimeMs === 1000, 'service switch never fabricates or advances presentation time');
empty.d.setService('CC1');
check(empty.text() === 'FIRST', 'return to populated service preserves its in-time decoded memory');
const renders = empty.seen.length;
empty.d.setService('CC1');
check(empty.seen.length === renders, 'repeated same-service authority state never clears or flickers current text');
empty.d.addCue(4, 5000, 'FUTURE');
empty.d.setService('CC4');
check(empty.text() === '' && empty.d.lastTimeMs === 1000, 'future selected-service cues cannot display early during a switch');
empty.d.updateTime(5000);
check(empty.text() === 'FUTURE', 'future service appears only when its actual presentation clock arrives');

const all = decoder();
for (let channel = 1; channel <= 4; channel++) pop(all.d, channel, 'CH' + channel);
for (let channel = 1; channel <= 4; channel++) {
  all.d.setService('CC' + channel);
  check(all.text() === 'CH' + channel, 'both CEA608 fields retain independent channel ' + channel);
}
all.d.setEnabled(false);
all.d.setService('CC3');
check(all.text() === '', 'service change cannot enable disabled captions');
all.d.setEnabled(true);
check(all.text() === 'CH3', 'explicit enable restores only selected service');
all.d.resetForSeek();
check(all.text() === '', 'seek clears all prior-service presentation');
all.d.setService('CC4');
check(all.text() === '', 'service switch after seek cannot revive retired cues');

function block(d, service, bytes, time) {
  const data = service < 7 ? [(service << 5) | bytes.length, ...bytes] : [0xe0 | bytes.length, service, ...bytes];
  if (data.length % 2 === 0) data.push(0);
  d.pushDtvcc(3, (data.length + 1) / 2, data[0], time);
  for (let i = 1; i < data.length; i += 2) d.pushDtvcc(2, data[i], data[i + 1], time);
  d.updateTime(time);
}
const digital = decoder('708-1');
for (const service of [1, 2, 6, 7, 12, 63]) block(digital.d, service, Array.from(Buffer.from('S' + service)), 1000);
for (const service of [1, 2, 6, 7, 12, 63]) {
  digital.d.setService('708-' + service);
  check(digital.text() === 'S' + service, 'CEA708 standard/extended service remains independently addressable: ' + service);
}
digital.d.setService('708-3');
check(digital.text() === '', 'empty CEA708 service clears prior digital window');
digital.d.setService('CC1');
check(digital.text() === '', 'digital-to-empty-analog switch never leaves digital captions');
console.log('Caption service vectors: ' + checks + ' PASS (generated decoder input, not physical service discovery)');
