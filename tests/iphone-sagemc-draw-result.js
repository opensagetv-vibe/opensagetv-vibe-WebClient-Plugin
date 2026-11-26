(()=>{const s=window.SAGEMC_DRAW;if(!s||s.active||!s.restored)throw Error('No completed restored probe');return{restored:s.restored,seen:s.seen,calls:s.calls}})()
