/* Fresh independent observation after one real BLE Enter; no replay. */
(()=>{
if((localStorage.getItem('sagetvWebMiniClientId')||'').replace(/:/g,'').toLowerCase()!=='123c8282e1ee')throw Error('Wrong phone');
const before=JSON.parse(sessionStorage.getItem('vibeOwnedReload078')||'null');if(!before)throw Error('No reload test owner');
const same=before.client===localStorage.getItem('sagetvWebMiniClientSettings.v1')&&before.streaming===localStorage.getItem('sagetvWebStreaming.v1')&&before.top===localStorage.getItem('vibeWebApp.portraitTopPx.v1');
const changed=performance.timeOrigin!==before.origin;
const out={reloaded:changed,preferencesPreserved:same,visible:document.visibilityState,sourceAssigned:!!videoPlane.getAttribute('src'),appRevision:[...document.scripts].find(e=>e.src.includes('miniclient-app.js'))?.src.split('?')[1],portraitTopPx:document.getElementById('appPortraitTopPx')?.value,focus:document.activeElement.id};
if(changed&&same)sessionStorage.removeItem('vibeOwnedReload078');return out;
})()
