'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
(async()=>{
 const calls=[],read=async(url,options={})=>{calls.push({url,options});return{ok:true,json:async()=>({})}};
 const context={window:{fetch:read},fetch:read,URL,URLSearchParams,location:{href:'https://fixture.test/miniclient.html',origin:'https://fixture.test'},setTimeout:(...a)=>{const t=setTimeout(...a);t.unref();return t},clearTimeout,
  localStorage:{getItem:k=>k==='sagetvWebMiniClientId'?'123c8282e1ee':null},
  document:{visibilityState:'visible'},performance:{getEntriesByType:()=>[{name:'https://fixture.test/api/miniclient?action=events&session=synthetic-owned'}]}};
 vm.createContext(context);
 for(const file of ['iphone-field-owner.js','iphone-refresh-field-session.js']){
  const source=fs.readFileSync(path.join(__dirname,file),'utf8');assert(Buffer.byteLength(source)<=2048);
  vm.runInContext(source,context);
  // Observe a NEW actual poll, not a stale Performance entry or a non-token
  // sentinel that the exact-owner safety guard must reject.
  const id=file.includes('refresh')?'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
  await context.window.fetch('https://fixture.test/api/miniclient?action=events&session='+id);
  for(const action of ['status','streamSettings','playbackState']){
   await context.window.__iphoneGate.api(action);const c=calls.at(-1),url=new URL(c.url,'https://fixture.test/');
   assert.equal(url.searchParams.get('action'),action);assert.equal(c.options.method||'GET','GET');assert(!('body' in c.options));
   assert.equal(url.searchParams.get('session'),id);
  }
  await context.window.__iphoneGate.api('stop');assert.equal(calls.at(-1).options.method,'POST');
 }
 console.log('PASS actual fresh/rebound iPhone field helpers keep three reads GET, Stop POST and exact scoped session; no live input');
})().catch(e=>{console.error(e);process.exitCode=1});
