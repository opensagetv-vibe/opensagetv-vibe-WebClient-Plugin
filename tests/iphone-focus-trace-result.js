(()=>{const s=window.__vibeFocusTrace;if(!s?.done||!s.restored)throw Error('Probe absent or pending');delete window.__vibeFocusTrace;return s;})()
