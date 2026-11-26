/* Only after independent MCP proof that the explicitly approved iPhone test
 * playback is closed. An old HLS buffer may still be playing locally. */
(()=>{if((localStorage.getItem('sagetvWebMiniClientId')||'').replace(/[^a-f0-9]/ig,'').toLowerCase()!=='123c8282e1ee')throw Error('Unexpected test identity');for(const v of document.querySelectorAll('video')){v.pause();v.removeAttribute('src');v.load()}setTimeout(()=>location.reload(),200);return{reloadScheduled:true,scope:'approved test source already closed through independent MCP',preferencesPreserved:true}})()
