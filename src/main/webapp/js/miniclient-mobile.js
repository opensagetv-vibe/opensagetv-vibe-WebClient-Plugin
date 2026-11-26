(function(root){
'use strict';
// Pure browser models: display paths never become filesystem/API inputs.
function folderParts(item){
  const path=String(item.relativePath||'').replace(/\\/g,'/');
  if(path.length>4096||path.startsWith('/')||path.includes(':'))return [];
  const parts=path.split('/').filter(Boolean);
  if(parts.some(p=>p==='.'||p==='..'||p.includes('\0')))return [];
  return parts.slice(0,-1);
}
function groupRows(rows,mode,path){
  const groups=new Map(),items=[];
  for(const item of rows){
    const parts=mode==='folders'?folderParts(item):mode==='series'?[String(item.title||'Untitled')]:mode==='category'?[String(item.category||'Uncategorized')]:[];
    if(!path.every((p,i)=>parts[i]===p))continue;
    if(parts.length>path.length){
      const label=parts[path.length];
      if(!groups.has(label))groups.set(label,{label,count:0});
      groups.get(label).count++;
    }else items.push(item);
  }
  return {groups:[...groups.values()].sort((a,b)=>a.label.localeCompare(b.label,undefined,{numeric:true})),items};
}
function guideModel(rows,reply){
  const half=1800000,now=Date.now(),valid=rows.filter(r=>Number.isFinite(Number(r.start))&&Number(r.end)>Number(r.start));
  let start=Number(reply.start),end=Number(reply.end);
  if(!Number.isFinite(start)||!start)start=valid.length?Math.floor(Math.min(...valid.map(r=>Number(r.start)))/half)*half:Math.floor(now/half)*half;
  if(!Number.isFinite(end)||end<=start)end=start+4*3600000;
  end=Math.min(end,start+12*3600000);
  const channels=new Map();
  for(const item of valid){
    const a=Math.max(start,Number(item.start)),b=Math.min(end,Number(item.end));if(b<=a)continue;
    const key=String(item.channelNumber||'')+'\0'+String(item.channelName||'');
    if(!channels.has(key))channels.set(key,{number:String(item.channelNumber||''),name:String(item.channelName||''),logo:item.channelLogoUrl||'',programs:[]});
    channels.get(key).programs.push({item,left:(a-start)/60000*6,width:(b-a)/60000*6});
  }
  const sorted=[...channels.values()].sort((a,b)=>a.number.localeCompare(b.number,undefined,{numeric:true})||a.name.localeCompare(b.name));
  for(const channel of sorted)channel.programs.sort((a,b)=>a.left-b.left);
  return {start,end,width:(end-start)/60000*6,channels:sorted};
}
async function showPlayback(options){
  // Reads may wait for public Watch's async completion. Never replay Watch or
  // the TV transition, and never force a modal/unknown/different source.
  let sent=false;
  for(let n=0;n<40;n++){
    if(!options.current())throw new Error('Playback view request cancelled');
    const state=await options.read();
    if(!options.current())throw new Error('Playback view request cancelled');
    if(state.ready&&state.layout==='fullscreen')return;
    if(state.ready&&state.layout==='preview'&&!sent){
      sent=true;
      const reply=await options.show();
      if(!reply.ok)throw new Error('Playback view changed; use Controls');
    }
    await options.wait(250);
  }
  throw new Error('Playback is loading or needs an STV dialog; use Controls');
}
// The STV remains the only playback/UI session. These lists are browser UI,
// not another player, recurring poll, tuner allocation or recording command.
function mount(options){
  const doc=root.document,stage=doc.getElementById('stage'),remote=doc.getElementById('remotePanel');
  const dock=doc.createElement('section');dock.id='mobileDock';dock.className='mc-mobile-dock';dock.hidden=true;
  dock.setAttribute('aria-label','Mobile SageTV browser');
  const tabs=doc.createElement('div');tabs.className='mc-mobile-tabs';tabs.setAttribute('role','tablist');tabs.setAttribute('aria-label','Browse and control');
  const names={controls:'Controls',recordings:'Recordings',guide:'Guide',videos:'Videos'},panels={},buttons={};
  let selected='recordings',active=false,serial=0,controller=null,busy=false,searchTimer=null;
  dock.appendChild(tabs);
  for(const key of Object.keys(names)){
    const button=doc.createElement('button');button.id='mobileTab-'+key;button.type='button';button.textContent=names[key];
    button.setAttribute('role','tab');button.setAttribute('aria-controls','mobilePage-'+key);
    const panel=doc.createElement('section');panel.id='mobilePage-'+key;panel.className='mc-mobile-page';panel.setAttribute('role','tabpanel');panel.setAttribute('aria-labelledby',button.id);
    buttons[key]=button;panels[key]=panel;tabs.appendChild(button);dock.appendChild(panel);
    button.addEventListener('click',()=>select(key));
    button.addEventListener('keydown',event=>{
      const keys=Object.keys(names),index=keys.indexOf(key);
      const next=event.key==='ArrowRight'?(index+1)%keys.length:event.key==='ArrowLeft'?(index+keys.length-1)%keys.length:event.key==='Home'?0:event.key==='End'?keys.length-1:-1;
      if(next>=0){event.preventDefault();event.stopPropagation();select(keys[next]);buttons[keys[next]].focus();}
    });
  }
  const toolbar=doc.createElement('form');toolbar.className='mc-mobile-search';toolbar.setAttribute('role','search');
  const search=doc.createElement('input');search.type='search';search.maxLength=120;search.placeholder='Search';search.setAttribute('aria-label','Search selected content');
  const refresh=doc.createElement('button');refresh.type='submit';refresh.textContent='Refresh';toolbar.append(search,refresh);
  const status=doc.createElement('p');status.className='mc-mobile-list-status';status.setAttribute('role','status');
  const list=doc.createElement('div');list.className='mc-mobile-list';list.tabIndex=0;list.setAttribute('aria-label','Content results');
  const queries={recordings:'',guide:'',videos:''};
  const views={recordings:'series',videos:'folders'},paths={recordings:[],videos:[]};
  let loaded=[],loadedReply={},guideStart=0;
  const browse=doc.createElement('div');browse.className='mc-mobile-browse';
  const group=doc.createElement('select');group.setAttribute('aria-label','Group content');
  for(const [value,label] of [['series','Series'],['folders','Folders'],['category','Category'],['all','All items']]){
    const option=doc.createElement('option');option.value=value;option.textContent=label;group.appendChild(option);
  }
  const crumbs=doc.createElement('nav');crumbs.className='mc-mobile-crumbs';crumbs.setAttribute('aria-label','Content folder');browse.append(group,crumbs);
  const ranges=doc.createElement('div');ranges.className='mc-mobile-guide-range';
  for(const [delta,label] of [[-1,'Earlier'],[0,'Now'],[1,'Later']]){
    const button=doc.createElement('button');button.type='button';button.textContent=label;
    button.addEventListener('click',()=>{guideStart=delta?(guideStart||Math.floor(Date.now()/1800000)*1800000)+delta*4*3600000:0;load();});ranges.appendChild(button);
  }
  const detail=doc.createElement('div');detail.className='mc-mobile-guide-details';detail.hidden=true;detail.setAttribute('aria-label','Selected program');
  detail.addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();event.stopPropagation();detail.hidden=true;const selected=list.querySelector('[aria-pressed="true"]');if(selected)selected.focus();}});
  stage.after(dock);
  function invalidate(){serial++;if(controller)controller.abort();controller=null;clearTimeout(searchTimer);}
  function note(text){status.textContent=text;}
  function refreshButtons(){for(const b of dock.querySelectorAll('[data-content-play],[data-content-action]'))b.disabled=busy||b.dataset.available!=='true';}
  function addText(parent,tag,text){const element=doc.createElement(tag);element.textContent=text||'';parent.appendChild(element);return element;}
  function makeItem(item,key){
      const row=doc.createElement('article');row.className='mc-mobile-item';
      const text=doc.createElement('div');row.appendChild(text);addText(text,'strong',item.title||'Untitled');
      if(item.episode)addText(text,'span',item.episode);
      const when=Number(item.start)>0?new Date(Number(item.start)).toLocaleString():'';
      addText(text,'small',[item.channelNumber,item.channelName,when,item.recording?'Recording now':''].filter(Boolean).join(' · '));
      if(item.description)addText(text,'p',item.description);
      const mediaId=Number(key==='guide'?item.mediaId:item.id),airingId=key==='guide'?Number(item.airingId):0;
      const available=Number.isSafeInteger(mediaId)&&mediaId>0||key==='guide'&&item.currentlyAiring===true&&Number.isSafeInteger(airingId)&&airingId>0;
      const play=doc.createElement('button');play.type='button';play.textContent='▶ Play';play.dataset.contentPlay='true';play.dataset.available=String(available);play.disabled=!available||busy;
      play.setAttribute('aria-label','Play '+(item.title||'Untitled')+' in SageTV');
      if(!available)play.title='Only current broadcasts or available recordings can play';
      play.addEventListener('click',async()=>{
        if(busy||!active||selected!==key||!available)return;
        busy=true;refreshButtons();note('Requesting playback in SageTV…');
        try{
          await options.watch(mediaId>0?{mediaId}:{airingId});
          if(active&&selected===key)note('Play requested in SageTV. Video will appear above; use Controls for STV dialogs.');
        }catch(error){if(active&&selected===key)note('Play was not confirmed: '+error.message+'. It was not automatically retried.');}
        finally{busy=false;refreshButtons();}
      });
      const actions=doc.createElement('div');actions.className='mc-mobile-item-actions';actions.appendChild(play);
      function action(label,allowed,run){
        const button=doc.createElement('button');button.type='button';button.textContent=label;button.dataset.contentAction='true';button.dataset.available=String(allowed);button.disabled=busy||!allowed;
        button.setAttribute('aria-label',label+' '+(item.title||'Untitled'));
        button.addEventListener('click',async()=>{
          if(busy||!active||selected!==key||!allowed)return;
          busy=true;refreshButtons();note(label+' requested…');
          try{await run();if(active&&selected===key)note(label==='Info'?'Information opened in the STV above.': 'Recording request accepted by SageTV.');}
          catch(error){if(active&&selected===key)note(label+' was not confirmed: '+error.message+'. It was not automatically retried.');}
          finally{busy=false;refreshButtons();}
        });actions.appendChild(button);
      }
      if(key==='guide'&&Number(item.start)>Date.now()&&Number.isSafeInteger(airingId)&&airingId>0){
        play.hidden=true;
        if(item.manualRecord)addText(actions,'small','Scheduled');
        else action('Record',true,async()=>{const reply=await options.record(airingId);if(!reply.ok)throw new Error('SageTV declined recording');item.manualRecord=true;for(const b of actions.querySelectorAll('[data-content-action]'))if(b.textContent==='Record'){b.dataset.available='false';b.textContent='Scheduled';}});
      }
      action('Info',Number.isSafeInteger(key==='guide'?airingId:mediaId)&&(key==='guide'?airingId:mediaId)>0,()=>options.info(key==='guide'?{airingId}:{mediaId}));
      row.appendChild(actions);return row;
  }
  function renderGuide(rows){
    const model=guideModel(rows,loadedReply),grid=doc.createElement('div');grid.className='mc-mobile-guide-grid';grid.style.width=(104+model.width)+'px';grid.setAttribute('role','table');grid.setAttribute('aria-label','Channel and time guide');
    list.classList.add('mc-mobile-guide');list.setAttribute('aria-label','Guide; scroll vertically for channels and horizontally for time');
    const header=doc.createElement('div');header.className='mc-mobile-guide-header';header.setAttribute('role','row');
    addText(header,'strong','Channel').className='mc-mobile-channel';
    const clock=doc.createElement('div');clock.className='mc-mobile-guide-times';clock.style.width=model.width+'px';
    for(let t=model.start;t<model.end;t+=1800000){const tick=addText(clock,'span',new Date(t).toLocaleTimeString([],{hour:'numeric',minute:'2-digit'}));tick.style.left=((t-model.start)/60000*6)+'px';}
    header.appendChild(clock);grid.appendChild(header);
    for(const channel of model.channels){
      const row=doc.createElement('div');row.className='mc-mobile-guide-row';row.setAttribute('role','row');
      const label=doc.createElement('div');label.className='mc-mobile-channel';label.setAttribute('role','rowheader');
      // Only the connected plugin's authenticated logo endpoint, not URLs
      // supplied by schedule metadata, can load an image into this deck.
      if((/^api\/channelLogo\?stationId=[1-9]\d*$/.test(channel.logo)||/^\/sagex\/media\/logo\//.test(channel.logo))&&!/[\r\n\\]/.test(channel.logo)){
        const image=doc.createElement('img');image.src=channel.logo;image.alt='';image.loading='lazy';image.addEventListener('error',()=>image.remove(),{once:true});label.appendChild(image);
      }
      addText(label,'strong',channel.number);addText(label,'small',channel.name);
      const track=doc.createElement('div');track.className='mc-mobile-guide-track';track.style.width=model.width+'px';track.setAttribute('role','cell');
      for(const program of channel.programs){
        const item=program.item,button=doc.createElement('button');button.type='button';button.className='mc-mobile-program';button.style.left=program.left+'px';button.style.width=program.width+'px';
        const when=new Date(Number(item.start)).toLocaleTimeString([],{hour:'numeric',minute:'2-digit'})+' – '+new Date(Number(item.end)).toLocaleTimeString([],{hour:'numeric',minute:'2-digit'});
        addText(button,'strong',item.title||'Untitled');addText(button,'small',when);button.title=[item.title,item.episode,when,item.description].filter(Boolean).join('\n');
        button.setAttribute('aria-label',[channel.number,item.title,when].join(' '));button.addEventListener('click',()=>{
          for(const b of grid.querySelectorAll('[aria-pressed]'))b.setAttribute('aria-pressed','false');button.setAttribute('aria-pressed','true');
          const close=doc.createElement('button');close.type='button';close.className='mc-mobile-detail-close';close.textContent='Back to guide';
          close.addEventListener('click',()=>{detail.hidden=true;button.focus();});
          detail.replaceChildren(close,makeItem(item,'guide'));detail.hidden=false;
        });track.appendChild(button);
      }
      row.append(label,track);grid.appendChild(row);
    }
    list.appendChild(grid);
    note(model.channels.length+' channels · '+new Date(model.start).toLocaleString()+' – '+new Date(model.end).toLocaleTimeString([],{hour:'numeric',minute:'2-digit'})+(rows.length>=6000?' (limit reached; narrow search)':''));
    if(!model.channels.length)note('No matching guide data. Check this server’s guide setup or choose Now/Refresh.');
  }
  function render(){
    const key=selected,rows=loaded;list.replaceChildren();detail.replaceChildren();detail.hidden=true;
    list.classList.remove('mc-mobile-guide');list.setAttribute('aria-label','Content results');
    if(key==='guide'){renderGuide(rows);return;}
    const path=paths[key],mode=views[key],result=groupRows(rows,mode,path);crumbs.replaceChildren();group.value=mode;
    for(let i=0;i<=path.length;i++){
      const b=doc.createElement('button');b.type='button';b.textContent=i?path[i-1]:names[key];b.disabled=i===path.length;
      b.addEventListener('click',()=>{paths[key]=path.slice(0,i);list.scrollTop=0;render();});crumbs.appendChild(b);
    }
    for(const folder of result.groups){
      const button=doc.createElement('button');button.className='mc-mobile-folder';button.type='button';
      addText(button,'strong','▸ '+folder.label);addText(button,'small',folder.count+' items');
      button.addEventListener('click',()=>{paths[key]=path.concat(folder.label);list.scrollTop=0;render();});list.appendChild(button);
    }
    const items=result.items.slice().sort(key==='recordings'?(a,b)=>Number(b.start||0)-Number(a.start||0):(a,b)=>String(a.title||'').localeCompare(String(b.title||''),undefined,{numeric:true}));
    for(const item of items)list.appendChild(makeItem(item,key));
    const limited=Number(loadedReply.total)>rows.length||rows.length>=500;
    note((result.groups.length?result.groups.length+' folders · ':'')+items.length+' items'+(limited?' (first500 matching items; narrow search)':'')+(!rows.length?' · No matching content.':''));
  }
  group.addEventListener('change',()=>{if(selected==='guide'||selected==='controls')return;views[selected]=group.value;paths[selected]=[];list.scrollTop=0;render();});
  async function load(){
    if(!active||selected==='controls')return;
    invalidate();const generation=serial,key=selected;controller=new AbortController();
    list.replaceChildren();detail.replaceChildren();detail.hidden=true;note('Loading '+names[key]+'…');
    try{
      const reply=await options.read(key,queries[key],controller.signal,{start:guideStart||undefined,hours:4});
      if(!active||selected!==key||generation!==serial)return;
      loadedReply=reply;loaded=((key==='guide'?reply.airings:reply.recordings)||[]).filter(item=>item&&typeof item==='object').slice(0,key==='guide'?6000:500);render();
    }catch(error){if(active&&selected===key&&generation===serial&&error.name!=='AbortError')note('Unable to load content: '+error.message+'. Use Refresh to try again.');}
  }
  function select(key){
    if(options.cancel)options.cancel();
    invalidate();selected=key;
    for(const name of Object.keys(names)){
      const on=name===key;panels[name].hidden=!on;buttons[name].setAttribute('aria-selected',String(on));buttons[name].tabIndex=on?0:-1;
    }
    if(key==='controls'){if(active)options.controls();}
    else{
      browse.hidden=key==='guide';ranges.hidden=key!=='guide';detail.hidden=true;
      panels[key].append(toolbar,browse,ranges,status,list,detail);search.value=queries[key];search.setAttribute('aria-label','Search '+names[key]);list.scrollTop=0;list.scrollLeft=0;load();
    }
  }
  toolbar.addEventListener('submit',event=>{event.preventDefault();queries[selected]=search.value.trim();load();});
  search.addEventListener('input',()=>{clearTimeout(searchTimer);queries[selected]=search.value.trim();if(paths[selected])paths[selected]=[];searchTimer=setTimeout(load,300);});
  const query=root.matchMedia('(orientation: portrait) and (max-width: 900px), (orientation: portrait) and (pointer: coarse)');
  function update(){
    const before=active;active=query.matches;doc.body.classList.toggle('mc-portrait-dock',active);dock.hidden=!active;
    if(active){panels.controls.appendChild(remote);remote.setAttribute('role','group');remote.removeAttribute('aria-modal');select(selected);}
    else if(before){invalidate();stage.appendChild(remote);remote.setAttribute('role','dialog');remote.setAttribute('aria-modal','true');options.hide();}
    if(options.layout)options.layout();
  }
  if(query.addEventListener)query.addEventListener('change',update);else query.addListener(update);
  select(selected);update();
  return {active:()=>active,controls:()=>{if(active&&selected!=='controls')select('controls');},retire:()=>{invalidate();},contains:element=>active&&dock.contains(element)};
}
root.SageMiniMobile=Object.freeze({mount,showPlayback,folderParts,groupRows,guideModel});
})(window);
