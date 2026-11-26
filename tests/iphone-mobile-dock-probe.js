/* Actual phone, read-only geometry. Counters are not audible/touch evidence. */
(()=>{
if((localStorage.getItem('sagetvWebMiniClientId')||'').replace(/:/g,'').toLowerCase()!=='123c8282e1ee')throw Error('Wrong phone');
const r=id=>{const e=document.getElementById(id),b=e.getBoundingClientRect();return{x:b.x,y:b.y,w:b.width,h:b.height,visible:!!e.getClientRects().length}};
const s=r('stage'),d=r('mobileDock'),c=r('remotePanel'),list=document.querySelector('.mc-mobile-list');
return{viewport:[innerWidth,innerHeight],portrait:document.body.classList.contains('mc-portrait-dock'),stage:s,dock:d,controls:c,stageAspect:s.w/s.h,
tabs:[...document.querySelectorAll('[role=tab]')].map(e=>({id:e.id,selected:e.getAttribute('aria-selected')})),
buttons:[...remotePanel.querySelectorAll('button')].filter(e=>e.getClientRects().length).map(e=>{const b=e.getBoundingClientRect();return{id:e.id,w:b.width,h:b.height}}),
controlScroll:[remotePanel.scrollHeight,remotePanel.clientHeight],list:{count:document.querySelectorAll('.mc-mobile-item').length,status:document.querySelector('.mc-mobile-list-status')?.textContent||'',scroll:list?[list.scrollHeight,list.clientHeight]:null},
video:{time:videoPlane.currentTime,paused:videoPlane.paused,width:videoPlane.videoWidth},profilesPreserved:window.__iphoneGate?localStorage.getItem('sagetvWebMiniClientSettings.v1')===__iphoneGate.settings&&localStorage.getItem('sagetvWebStreaming.v1')===__iphoneGate.streaming:null};
})()
