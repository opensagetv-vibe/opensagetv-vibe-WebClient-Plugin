/* Explicit idle phone reload test setup. Real activation follows via BLE. */
(()=>{
if(document.visibilityState!=='visible'||(localStorage.getItem('sagetvWebMiniClientId')||'').replace(/:/g,'').toLowerCase()!=='123c8282e1ee')throw Error('Wrong phone');
if(videoPlane.getAttribute('src')||videoPlane.currentSrc||!calibrationPanel.hidden)throw Error('Require idle phone');
const button=document.getElementById('appReloadPage');if(!button)throw Error('078 not loaded');
const before={origin:performance.timeOrigin,client:localStorage.getItem('sagetvWebMiniClientSettings.v1'),streaming:localStorage.getItem('sagetvWebStreaming.v1'),top:localStorage.getItem('vibeWebApp.portraitTopPx.v1')};
sessionStorage.setItem('vibeOwnedReload078',JSON.stringify(before));
remoteSettings.click();document.querySelector('[data-settings-page=app]').click();button.scrollIntoView({block:'center'});button.focus({preventScroll:true});
return{ready:document.activeElement===button,focus:document.activeElement.id,origin:before.origin,viewport:[innerWidth,innerHeight],source:false};
})()
