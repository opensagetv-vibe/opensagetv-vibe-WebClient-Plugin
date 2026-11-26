/* P05 SageTV caption authority and virtual CC-slot policy. Kept independent
 * from ordinary subtitle preferences and from DVB bitmap selection. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.SageMiniCaptionAuthority=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const DEFAULTS=Object.freeze({mode:'off',cc1Type:'auto',cc1Language:'',cc1Service:1,cc2Type:'auto',cc2Language:'',cc2Service:2});
function normType(v){v=String(v||'auto').toLowerCase().replace(/[-_]/g,'');return ['auto','teletext','cea608','cea708','dvb'].includes(v)?v:'auto';}
function normalize(v){v=Object.assign({},DEFAULTS,v||{});v.mode=['off','cc1','cc2','stv','dvb'].includes(String(v.mode))?String(v.mode):'off';for(const s of ['cc1','cc2']){v[s+'Type']=normType(v[s+'Type']);v[s+'Language']=String(v[s+'Language']||'').trim().toLowerCase();const n=Number(v[s+'Service']);v[s+'Service']=Number.isInteger(n)&&n>=1&&n<=63?n:(s==='cc1'?1:2);}return v;}
function lang(t){if(!t)return'';const c=codec(t);return c==='cea608'?'':String(t.language||'').toLowerCase();}
function codec(t){const c=String(t&&t.codec||'').toLowerCase(),k=String(t&&t.serviceKind||'').toLowerCase();if(k==='teletext'||c.includes('teletext'))return'teletext';if(k==='dvb'||k==='dvb-bitmap'||c.includes('dvb_subtitle'))return'dvb';if(c.includes('eia_608')||c.includes('cea608'))return'cea608';if(c.includes('eia_708')||c.includes('cea708'))return'cea708';return'';}
function english(l){l=String(l||'').toLowerCase();return l==='en'||l==='eng'||l.startsWith('en-')||l.startsWith('eng-');}
function score(t){const c=codec(t);return c==='cea708'?40:c==='cea608'?35:c==='teletext'?30:20;}
function languageKey(value){const l=String(value||'').toLowerCase().split('-')[0];return ({en:'eng',es:'spa',fr:'fra',fre:'fra',de:'deu',ger:'deu',it:'ita',pt:'por',nl:'nld',dut:'nld'})[l]||l;}
function candidates(tracks,type,language){
  const req=normType(type),want=languageKey(language);
  return (tracks||[]).filter(t=>{
    const c=codec(t);if(!c||t.supported===false||t.synthetic===true||t.availability==='unavailable')return false;
    if(req!=='auto'&&c!==req)return false;
    const actual=languageKey(lang(t));
    // Match current Android CaptionSlotPolicy: 608 language is unknown; only
    // English may use the unlabeled compatibility fallback, never Spanish etc.
    return !want||want===actual||c==='cea608'&&!actual&&want==='eng';
  }).sort((a,b)=>score(b)-score(a));
}
function sameService(a,b){return codec(a)===codec(b)&&a.index===b.index&&Number(a.sourcePid??-1)===Number(b.sourcePid??-1)&&Number(a.teletextPage??-1)===Number(b.teletextPage??-1)&&Number(a.compositionPageId??-1)===Number(b.compositionPageId??-1)&&Number(a.accessibilityChannel||a.service||0)===Number(b.accessibilityChannel||b.service||0);}
function resolve(tracks,slot,type,language,service){
  const c=candidates(tracks,type,language);if(!c.length)return null;
  if(normType(type)==='cea608'||normType(type)==='cea708'){
    const exact=c.find(t=>Number(t.accessibilityChannel||t.service)===Number(service||slot));if(exact)return exact;
  }
  if(language)return c[0];
  const first=c.find(t=>english(lang(t)))||c[0];if(slot!==2)return first;
  // Do not use candidates[1]: English may have moved CC1 to that position.
  if(english(lang(first))){const secondary=c.find(t=>!sameService(t,first)&&lang(t)&&!english(lang(t)));if(secondary)return secondary;}
  return c.find(t=>!sameService(t,first))||first;
}
function effective(authority,tracks){
  const a=normalize(authority);if(a.mode==='off')return{mode:'off',local:'off',label:'Off'};
  if(a.mode==='stv')return{mode:'stv',local:'off',tap:'608',label:'STV / SageTV authority'};
  if(a.mode==='dvb')return{mode:'dvb',local:'dvb',label:'DVB bitmap'};
  const slot=a.mode==='cc2'?2:1,key=slot===1?'cc1':'cc2',t=resolve(tracks,slot,a[key+'Type'],a[key+'Language'],a[key+'Service']);
  if(!t){
    const type=a[key+'Type'];
    // In-band A/53 captions need not have a separate ffprobe subtitle stream.
    // An explicit CEA choice is a manual decoder request, not discovered
    // inventory. Auto must never invent two CEA services for a UK recording.
    if(type==='cea608'||type==='cea708'){
      const service=Math.max(1,Math.min(type==='cea608'?4:63,Number(a[key+'Service'])||slot));
      return{mode:a.mode,local:type==='cea608'?'608':'708',service,manual:true,label:'CC'+slot+' → '+type.toUpperCase()+' service '+service+' (manual, not discovered)'};
    }
    return{mode:a.mode,local:'off',missing:true,label:'CC'+slot+' unavailable'};
  }
  const c=codec(t),service=Number(t.accessibilityChannel||t.service)||Number(a[key+'Service'])||slot;
  return{mode:a.mode,local:c==='teletext'?'teletext':c==='dvb'?'dvb':c==='cea708'?'708':'608',track:t,service:c==='cea708'||c==='cea608'?service:1,label:'CC'+slot+' → '+c.toUpperCase()+(lang(t)?' '+lang(t):'')};
}
return{DEFAULTS,normalize,codec,resolve,effective};
});
