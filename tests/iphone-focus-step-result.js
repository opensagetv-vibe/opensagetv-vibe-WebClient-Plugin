(()=>{const s=window.__vibeFocusStep;if(!s?.done||!s.restored)throw Error('Focus step incomplete or probe ownership changed');delete window.__vibeFocusStep;return s;})()
