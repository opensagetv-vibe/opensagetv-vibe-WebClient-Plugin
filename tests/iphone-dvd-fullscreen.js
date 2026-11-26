/* Only after HDMI verified SageMC's owned DVD preview; TV is one toggle. */
(()=>{const s=window.__iphoneGate;if(!s?.api)throw Error('Missing owner');s.dvdFullscreen='pending';s.api('command',{command:15}).then(()=>s.dvdFullscreen='ready').catch(()=>s.dvdFullscreen='failed');return{oneSyntheticTvToggle:true};})()
