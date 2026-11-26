'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(require('node:path').join(__dirname,'iphone-session-probe.js'),'utf8');
for(const open of [false,true]){
  let mutations=0;
  const reject=()=>{mutations++;throw Error('Read-only probe attempted input');};
  const context={innerWidth:852,innerHeight:393,
    localStorage:{getItem:()=> '123C8282E1EE',setItem:reject,removeItem:reject},
    document:{querySelectorAll:()=>[{currentSrc:'',getAttribute:()=>null,paused:true,readyState:0}],
      getElementById:id=>{assert.ok(['remotePanel','exitClientDialog'].includes(id));return{hidden:!open,open,click:reject};}}};
  const result=vm.runInNewContext(source,context,{timeout:1000});
  assert.equal(result.exitDialogOpen,open);assert.equal(result.remoteVisible,open);
  assert.equal(result.media[0].source,false);assert.equal(result.media[0].ready,0);
  assert.equal(mutations,0);
}
console.log('PASS iPhone session observation never clicks controls or requests Exit (2 cases)');
