'use strict';
const assert=require('assert');
const S=require('../src/main/webapp/js/miniclient-support.js');
let n=0;const ok=(v,name)=>{assert(v,name);console.log('PASS '+name);n++;};
const profile=S.buildProfile(
  {bufferPreset:'auto',showStats:true,autoDiagnosticCapture:false,saveDiagnosticsToServer:true,clientId:'SHOULD-NOT-EXPORT',unrelated:'keep-local'},
  {player:'mpegts',videoKbps:8000,deinterlaceFilter:'bwdif',audioTrack:4,subtitleTrack:7,captionPid:512,captionCompositionPage:42,subtitleLanguage:'eng'},
  {mode:'cc1',cc1Type:'teletext',cc1Language:'eng',cc1Service:1,sessionOnly:'no'}
);
ok(profile.kind===S.PROFILE_KIND&&profile.schemaVersion===2,'profile has explicit kind/schema');
const legacy=S.previewProfile(Object.assign({},profile,{schemaVersion:1}));
ok(legacy.schemaVersion===1&&legacy.migrations.length===1&&!legacy.input,'schema1 imports preserve existing input/app preferences');
const portable=S.previewProfile(S.buildProfile({},{},{},{input:{keys:{dvd:{ArrowLeft:'62',bad:'89'}}},keepAwake:true,password:'not exported'}));
ok(portable.input.keys.dvd.ArrowLeft==='62'&&!portable.input.keys.dvd.bad&&portable.browserApp.keepAwake===true,'portable mappings/wake policy round-trip with normalization');
const launcher=S.previewProfile(S.buildProfile({},{},{},{showControls:false,token:'not exported'}));
ok(launcher.browserApp.showControls===false&&!('token' in launcher.browserApp),'optional hidden Controls preference round-trips without exporting unrelated state');
ok(S.previewProfile(S.buildProfile({},{},{},{portraitTopPx:48})).browserApp.portraitTopPx===48,'portrait top spacing round-trips as browser-only preference');
ok(S.previewProfile(S.buildProfile({},{},{},{portraitTopPx:900})).browserApp.portraitTopPx===160,'imported portrait spacing is bounded');
ok(!('portraitTopPx' in (S.previewProfile(S.buildProfile({},{},{},{portraitTopPx:NaN})).browserApp||{})),'non-finite portrait spacing is not exported');
const autoHeight=S.previewProfile(S.buildProfile({},{resolution:'auto'},{}));
ok(autoHeight.streaming.resolution==='auto','automatic device height stays portable instead of persisting a resolved screen limit');
ok(profile.profileScope==='browser-saved-defaults'&&profile.excludedScopes.includes('administrator-server-settings'),'profile declares scope boundaries');
ok(!('clientId' in profile.savedDefaults.client)&&!('audioTrack' in profile.savedDefaults.streaming)&&!('subtitleTrack' in profile.savedDefaults.streaming),'identity and per-session track choices are excluded');
ok(!('captionPid' in profile.savedDefaults.streaming)&&!('captionCompositionPage' in profile.savedDefaults.streaming),'per-session PID/page choices are excluded');
const imported=JSON.parse(JSON.stringify(profile));imported.extraTop=1;imported.savedDefaults.streaming.futureThing='x';
const preview=S.previewProfile(imported);
ok(preview.unknownKeys.includes('extraTop')&&preview.unknownKeys.includes('streaming.futureThing'),'import preview reports unknown keys');
ok(preview.streaming.player==='mpegts'&&preview.captions.mode==='cc1','import preview retains approved saved defaults');
ok(preview.streaming.deinterlaceFilter==='bwdif','explicit server deinterlace filter survives profile export/import');
const many=JSON.parse(JSON.stringify(profile));for(let i=0;i<80;i++)many.savedDefaults.client['future'+i]=i;
ok(S.previewProfile(many).unknownKeys.length===50,'unknown import keys are bounded');
let rejected=false;try{S.previewProfile({kind:S.PROFILE_KIND,schemaVersion:99,savedDefaults:{}});}catch(_){rejected=true;}ok(rejected,'future profile schema fails closed');
const red=S.redact({Authorization:'Bearer abc',password:'pw',nested:{cookie:'x',captionText:'SECRET CAPTION',payload:'raw'},safe:'ok'});
ok(red.Authorization==='[redacted]'&&red.password==='[redacted]'&&red.nested.cookie==='[redacted]','recognized credentials are redacted');
ok(red.nested.captionText==='[omitted-content]'&&red.nested.payload==='[omitted-content]'&&red.safe==='ok','caption/media content is omitted while counters survive');
const cap=S.captionSummary({mode:'cc1'},{mode:'cc1',local:'teletext',service:1,track:{codec:'teletext',sourcePid:401,teletextPage:888,language:'eng'}},[{},{},{}],{received:12,pending:2,queue:{oldestAgeMs:350}},{mode:'text',received:4,pending:1,queue:{oldestAgeMs:-50},text:'DO NOT EXPORT'},{active:true,received:3,pending:1,queue:{oldestAgeMs:25}});
ok(cap.resolvedSlot==='CC1'&&cap.codec==='teletext'&&cap.pid===401&&cap.page===888&&cap.renderOwner==='browser-local','caption diagnostics resolve slot/codec/PID/page/render owner');
ok(cap.ordinary&&!('text' in cap.ordinary)&&cap.ordinary.queue.oldestAgeMs===-50,'ordinary subtitle diagnostics expose timing counters without subtitle text');
const stvCap=S.captionSummary({mode:'stv'},{mode:'stv',local:'off',label:'STV / SageTV authority'},[],{received:9,pending:1,stvControlled:true,stvStateSeen:true,stvState:1,stvService:'CC1'},null,null);
ok(stvCap.renderOwner==='browser-local-stv-controlled'&&stvCap.effectiveType==='608'&&stvCap.service===1&&stvCap.stvState===1,'STV diagnostics expose local renderer controlled by SageTV state');
const tr=S.effectiveTranscode({transport:'mpegts',encoder:'h264_qsv',accelerator:'qsv',hardware:true,hardwareDecode:false,softwareFallback:false,inputMode:'pipe',streamSettings:{effective:{video:'h264 8Mbps',audio:'aac stereo',detail:'QSV encode'}}});
ok(tr.transport==='mpegts'&&tr.encoder==='h264_qsv'&&tr.hardwareEncode===true&&tr.hardwareDecode===false&&tr.audio==='aac stereo','effective transcode diagnostics distinguish encode/decode mode');
console.log('P14 support/profile helpers: '+n+' tests PASS');
