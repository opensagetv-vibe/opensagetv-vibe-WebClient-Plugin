/* Read only the known empty-or-one-test-character local draft; no text export. */
(()=>({focus:document.activeElement?.id||'',length:keyboardInput.value.length,isTestCharacter:/^[qQ]$/.test(keyboardInput.value),remoteVisible:!remotePanel.hidden,keyboardVisible:!keyboardPanel.hidden,settingsVisible:!settingsPanel.hidden,hasOldObserver:!!window.__phoneInput}))()
