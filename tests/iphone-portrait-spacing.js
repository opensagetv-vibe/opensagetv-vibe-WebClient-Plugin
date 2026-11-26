/* Actual phone layout/preferences test; synthetic DOM input, not finger proof. */
(()=>{
if((localStorage.getItem('sagetvWebMiniClientId')||'').replace(/:/g,'').toLowerCase()!=='123c8282e1ee'||!document.body.classList.contains('mc-portrait-dock'))throw Error('Require exact portrait phone');
const input=document.getElementById('appPortraitTopPx');if(!input)throw Error('077 not loaded');
const rect=()=>{const r=stage.getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height}};
const s=window.__portraitSpacing={value:input.value,client:localStorage.getItem('sagetvWebMiniClientSettings.v1'),streaming:localStorage.getItem('sagetvWebStreaming.v1'),before:rect()};
remoteSettings.click();document.querySelector('[data-settings-page=app]').click();
input.value='48';input.dispatchEvent(new Event('input',{bubbles:true}));s.adjusted=rect();
if(Math.abs(s.adjusted.y-s.before.y-(48-Number(s.value)))>1)throw Error('Stage did not shift correctly');
input.value=s.value;input.dispatchEvent(new Event('change',{bubbles:true}));closeSettings.click();
const restored=rect(),pass=Math.abs(restored.y-s.before.y)<1&&localStorage.getItem('sagetvWebMiniClientSettings.v1')===s.client&&localStorage.getItem('sagetvWebStreaming.v1')===s.streaming;
const out={passed:pass,viewport:[innerWidth,innerHeight],setting:s.value,before:s.before,adjusted:s.adjusted,restored,aspect:restored.w/restored.h,profilesUnchanged:pass};delete window.__portraitSpacing;return out;
})()
