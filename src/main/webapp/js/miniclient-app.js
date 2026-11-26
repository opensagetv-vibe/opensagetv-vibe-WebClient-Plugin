/* Home-screen shell only. Playback and SageTV authority remain in MiniClient. */
(function(){
  'use strict';
  const $=id=>document.getElementById(id),toolbar=document.querySelector('.mc-toolbar-actions');
  if(!toolbar||!$('stage'))return;
  const standalone=()=>!!navigator.standalone||window.matchMedia('(display-mode: standalone)').matches;
  const updateViewport=()=>{
    document.body.classList.toggle('mc-standalone',standalone());
    document.documentElement.style.setProperty('--visible-height',(window.visualViewport?window.visualViewport.height:innerHeight)+'px');
  };
  updateViewport();window.addEventListener('resize',updateViewport);
  if(window.visualViewport)window.visualViewport.addEventListener('resize',updateViewport);
  const launcher=document.createElement('button');launcher.id='appMenuBtn';launcher.type='button';
  launcher.className='mc-app-menu';launcher.textContent='Controls';launcher.setAttribute('aria-label','Open Vibe controls');launcher.hidden=true;
  launcher.addEventListener('click',()=>$('remoteToggle').click());$('stage').appendChild(launcher);
  const install=document.createElement('button');install.id='installApp';install.type='button';install.textContent='Install app';toolbar.appendChild(install);
  const help=document.createElement('section');help.id='pwaInstallHelp';help.className='mc-note';
  const title=document.createElement('h3');title.textContent='SageTV Vibe on your Home Screen';
  const steps=document.createElement('p');steps.textContent='On iPhone/iPad: open this MiniClient page in Safari, choose Share, then Add to Home Screen. Keep Open as Web App enabled if offered. Launch the new SageTV Vibe icon for the standalone view. Sign in again if prompted.';
  const limits=document.createElement('p');limits.textContent='SageTV must remain reachable. Offline playback is not available. HTTPS is needed for service-worker caching and secure browser APIs on a remote LAN address; your Home Screen shortcut does not bypass server login or certificate checks.';
  help.append(title,steps,limits);$('remoteTools').appendChild(help);
  let prompt=null;
  window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();prompt=e;});
  install.addEventListener('click',async()=>{
    if(prompt){const pending=prompt;prompt=null;try{await pending.prompt();await pending.userChoice;}catch(_){}return;}
    if($('remotePanel').hidden)$('remoteToggle').click();
    if($('remoteTools').hidden)$('remoteHelp').click();help.scrollIntoView({block:'nearest'});
  });
  window.addEventListener('appinstalled',()=>{install.hidden=true;updateViewport();});
  install.hidden=standalone();

  // Long press is the default entry. A discoverable launcher remains opt-in
  // for users whose browser intercepts the gesture; recovery is independent.
  const appendAppSetting=node=>{const general=document.querySelector('#settingsTree [data-section="app"]');if(general)general.appendChild(node);else $('resetSettings').before(node);};
  const controlsLabel=document.createElement('label');controlsLabel.dataset.settingsGroup='app';controlsLabel.className='mc-check';
  const showControls=document.createElement('input');showControls.id='appShowControls';showControls.type='checkbox';
  try{showControls.checked=localStorage.getItem('vibeWebApp.showControls.v1')==='true';}catch(_){}
  const updateLauncher=()=>{launcher.hidden=!showControls.checked;};
  controlsLabel.append(showControls,document.createTextNode(' Show Controls button'));
  appendAppSetting(controlsLabel);updateLauncher();
  showControls.addEventListener('change',()=>{try{localStorage.setItem('vibeWebApp.showControls.v1',String(showControls.checked));}catch(_){}updateLauncher();});
  window.addEventListener('vibe:app-preferences',event=>{if(event.detail&&typeof event.detail.showControls==='boolean'){showControls.checked=event.detail.showControls;showControls.dispatchEvent(new Event('change'));}});

  // Extra portrait spacing is independent of the OS safe area. Move the
  // common stage, never just the video or graphics/pointer transform.
  const topKey='vibeWebApp.portraitTopPx.v1';
  const topLabel=document.createElement('label');topLabel.dataset.settingsGroup='app';topLabel.className='mc-portrait-spacing';
  const top=document.createElement('input');top.id='appPortraitTopPx';top.type='number';top.min='0';top.max='160';top.step='1';top.inputMode='numeric';
  top.style.minHeight='44px';
  top.title='Extra portrait space below the safe area (0–160 px). Applies immediately.';
  topLabel.append(document.createTextNode('Portrait top spacing (px)'),top);appendAppSetting(topLabel);
  const normalizeTop=value=>value===null||value===''||!Number.isFinite(Number(value))?24:Math.max(0,Math.min(160,Math.round(Number(value))));
  let savedTop=null;try{savedTop=localStorage.getItem(topKey);}catch(_){}
  const applyTop=value=>{
    const pixels=normalizeTop(value);top.value=String(pixels);
    document.documentElement.style.setProperty('--mobile-extra-top',pixels+'px');
    try{localStorage.setItem(topKey,String(pixels));}catch(_){}
  };
  applyTop(savedTop);
  top.addEventListener('input',()=>{if(top.value!==''&&top.validity.valid)applyTop(top.value);});
  top.addEventListener('change',()=>applyTop(top.value));
  window.addEventListener('vibe:app-preferences',event=>{if(event.detail&&typeof event.detail.portraitTopPx==='number')applyTop(event.detail.portraitTopPx);});

  const reload=document.createElement('button');reload.id='appReloadPage';reload.type='button';reload.dataset.settingsGroup='app';reload.textContent='Reload webpage';reload.style.minHeight='44px';
  reload.title='Reload this Web Client without clearing saved settings. Playback will be interrupted.';
  appendAppSetting(reload);
  reload.addEventListener('click',()=>{
    if(reload.disabled)return;
    const video=$('videoPlane');
    // A browser-native confirmation owns input while it is open. This is a
    // user-requested normal reload, not a hidden reconnect/recovery loop.
    if((video.currentSrc||video.getAttribute('src'))&&!window.confirm('Reload the webpage? This interrupts this client’s playback. Saved settings are kept.'))return;
    // A distinct navigation bypasses a retained Safari/PWA document without
    // clearing any settings or relying on browser-specific forceReload flags.
    const target=new URL(window.location.href);target.searchParams.set('_vibeReload',String(Date.now()));
    reload.disabled=true;window.location.replace(target.href);
  });

  // Wake lock is explicit and best-effort, never a hidden silent-audio loop.
  const label=document.createElement('label');label.dataset.settingsGroup='app';label.className='mc-check';
  const awake=document.createElement('input');awake.id='appKeepAwake';awake.type='checkbox';
  try{awake.checked=localStorage.getItem('vibeWebApp.keepAwake.v1')==='true';}catch(_){}
  label.append(awake,document.createTextNode(' Keep screen awake (if supported)'));
  appendAppSetting(label);
  let lease=null,wakeSerial=0;
  async function updateWake(){
    const serial=++wakeSerial,video=$('videoPlane');
    if(lease){const previous=lease;lease=null;try{await previous.release();}catch(_){}}
    if(!awake.checked||document.hidden||video.paused||!navigator.wakeLock||!window.isSecureContext)return;
    try{const next=await navigator.wakeLock.request('screen');if(serial!==wakeSerial||document.hidden||!awake.checked)await next.release();else lease=next;}catch(_){}
  }
  awake.addEventListener('change',()=>{try{localStorage.setItem('vibeWebApp.keepAwake.v1',String(awake.checked));}catch(_){}updateWake();});
  window.addEventListener('vibe:app-preferences',event=>{if(event.detail&&typeof event.detail.keepAwake==='boolean'){awake.checked=event.detail.keepAwake;awake.dispatchEvent(new Event('change'));}});
  ['playing','pause','ended','emptied'].forEach(name=>$('videoPlane').addEventListener(name,updateWake));
  document.addEventListener('visibilitychange',updateWake);
  window.addEventListener('pagehide',()=>{wakeSerial++;if(lease){lease.release().catch(()=>{});lease=null;}});
  if('mediaSession' in navigator){
    const actions={play:7,pause:6,stop:89,seekbackward:62,seekforward:61,previoustrack:62,nexttrack:61};
    for(const [action,command] of Object.entries(actions))try{
      navigator.mediaSession.setActionHandler(action,()=>window.dispatchEvent(new CustomEvent('vibe:media-action',{detail:command})));
    }catch(_){} // Unsupported individual actions must not break Safari startup.
  }
})();
