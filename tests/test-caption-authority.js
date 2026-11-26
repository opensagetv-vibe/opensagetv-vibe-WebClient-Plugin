'use strict';
const assert=require('assert');const A=require('../src/main/webapp/js/miniclient-caption-authority.js');
const tracks=[
 {index:1,codec:'eia_608',language:'eng',evidence:'metadata'},
 {index:2,codec:'dvb_teletext',serviceKind:'teletext',language:'eng',teletextPage:888,sourcePid:301,evidence:'observed-pmt',availability:'observed'},
 {index:3,codec:'dvb_teletext',serviceKind:'teletext',language:'spa',teletextPage:889,sourcePid:302,evidence:'observed-pmt',availability:'observed'},
 {index:4,codec:'eia_708',language:'eng',accessibilityChannel:1,evidence:'metadata'}
];
assert.equal(A.resolve(tracks,1,'auto','',1).index,4,'Current Android ordering prefers English CEA708 before Teletext');
assert.equal(A.resolve(tracks,2,'auto','',2).index,3,'CC2 selects distinct described non-English service');
assert.equal(A.resolve(tracks,1,'cea608','spa',1),null,'CEA-608 language is not invented');
assert.equal(A.effective({mode:'stv'},tracks).local,'off');
assert.equal(A.effective({mode:'dvb'},tracks).local,'dvb');
assert.equal(A.effective({mode:'cc1',cc1Type:'teletext'},tracks).local,'teletext');
const mixed=[{index:10,codec:'dvb_teletext',language:'spa',teletextPage:889,sourcePid:10},
 {index:11,codec:'dvb_teletext',language:'eng',teletextPage:888,sourcePid:10},
 {index:12,codec:'dvb_subtitle',language:'eng',sourcePid:11,compositionPageId:1}];
assert.equal(A.resolve(mixed,1,'auto','',1).index,11);
assert.equal(A.resolve(mixed,2,'auto','',2).index,10,'CC2 cannot duplicate reordered CC1');
assert.equal(A.resolve(mixed,1,'dvb','en',1).index,12);
assert.equal(A.effective({mode:'cc1',cc1Type:'dvb'},mixed).local,'dvb');
assert.equal(A.resolve(tracks,1,'cea608','en',1).index,1);
assert.equal(A.resolve(mixed,1,'auto','es',1).index,10);
assert.equal(A.resolve([{index:9,codec:'eia_608',synthetic:true}],1,'auto','',1),null);
const manual=A.effective({mode:'cc1',cc1Type:'cea608'},[]);
assert.equal(manual.local,'608');assert.equal(manual.manual,true);assert.equal(manual.track,undefined);
assert.equal(A.effective({mode:'cc1',cc1Type:'auto'},[]).missing,true,'Auto never invents unobserved CEA captions');
assert.equal(A.effective({mode:'cc2',cc2Type:'cea708',cc2Service:12},[]).service,12);
console.log('caption authority policy: 18 PASS');
