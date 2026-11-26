/* Restore only the two fields changed by the failed pre-Watch harness.
 * Prior061723 real profile read=STV/auto; all intervening field runs prove
 * exact saved-profile restoration. No media/input/other settings change.
 */
(()=>{if(videoPlane.getAttribute('src')||saveStreaming.disabled||window.__ceaRestore)throw Error('Require idle one-shot restore');const a=SageMiniCaptionAuthority.normalize(JSON.parse(localStorage.getItem('sagetvWebCaptionAuthority.v1')||'{}')),p=SageMiniStreaming.normalize(JSON.parse(localStorage.getItem('sagetvWebStreaming.v1')||'{}'));if(a.mode!=='cc1'||a.cc1Type!=='cea708'||a.cc1Service!==1||p.captionAuthority!=='cc1'||p.captions!=='708'||p.captionService!==1)throw Error('Preserve unexpected profile');window.__ceaRestore={before:a,stream:p,intent:true};captionAuthorityMode.value='stv';cc1Type.value='auto';saveStreaming.click();return{restoreIntent:true,priorEvidence:'20261119T061723Z + subsequent exact profile preservation',mediaUnchanged:true}})()
