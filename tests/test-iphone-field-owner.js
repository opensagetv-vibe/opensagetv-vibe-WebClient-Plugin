'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const code=fs.readFileSync(path.join(__dirname,'iphone-field-owner.js'),'utf8');
assert(Buffer.byteLength(code)<=2048,'Inspector expression must remain bounded');
for(const action of ['events','state','status']){
 const calls=[],original=(...args)=>{calls.push(args);return Promise.resolve({ok:true,json:()=>({ok:true})})};
 const c={URL,URLSearchParams,location:{href:'http://test/SageTVWebPlayer/miniclient.html',origin:'http://test'},localStorage:{getItem:k=>k==='sagetvWebMiniClientId'?'123c8282e1ee':null},fetch:original};c.window=c;vm.createContext(c);vm.runInContext(code,c);
 const id='a'.repeat(32),other='b'.repeat(32);
 c.fetch('http://foreign/SageTVWebPlayer/api/miniclient?action='+action+'&session='+other);
 assert.equal(c.__iphoneGate.done,false);assert.notEqual(c.fetch,original);
 c.fetch('http://test/SageTVWebPlayer/api/miniclient?action=command',{body:new URLSearchParams({session:other,command:'8'})});
 assert.equal(c.__iphoneGate.done,false);
 c.fetch(new URL('http://test/SageTVWebPlayer/api/miniclient?action='+action),{body:new URLSearchParams({session:id})});
 assert.equal(c.__iphoneGate.done,true);assert.equal(c.fetch,original,'Observer restores fetch after current owner receipt');
 assert.equal(calls.length,3,'Observation must not add a request');
}
console.log('PASS actual-phone owner events/state/status body/same-origin/no-extra-request/2048-byte guards');
