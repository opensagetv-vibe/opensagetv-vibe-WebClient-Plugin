#!/usr/bin/env python3
"""Borrow/restore only the exact optional DVD test hook through stock MCP.

Compare-and-set plugin configuration; preserve a concurrent change. No Core,
bookmark deletion, direct server config edits, restart or normal-playback MCP
dependency. Restore before retiring the exact phone UI.
"""
import argparse,importlib.util,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py');C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser();p.add_argument('action',choices=['state','enable','restore']);p.add_argument('--checkpoint',type=Path);a=p.parse_args()
identity='123c8282e1ee';keys={'enabled':'true','dvd.owned_navigation':'true','dvd.client_controls':'true','dvd.owned_mode':'copy'}
def mcp(action,**v):return C.request(cfg,'/v1/control',dict(action=action,**v),mcp=True)
activity=C.activity(cfg)
if activity.get('recordingCount')!=0 or activity.get('connectedClientCount')!=0 or mcp('ui.list').get('contexts')!=[identity]:raise SystemExit('Require exact phone ownership/no recordings/other users')
if a.action=='state':
    print(json.dumps({'settings':{k:mcp('companion.config_get',setting=k)['value'] for k in keys},'hook':mcp('companion.dvd_hook',context=identity),'bookmark':mcp('companion.dvd_bookmark',context=identity)},indent=2));raise SystemExit()
if a.checkpoint is None:p.error('Explicit owning checkpoint required')
path=a.checkpoint.resolve()
if not path.is_relative_to((ROOT/'artifacts/active/WEB-023').resolve()):p.error('Owning WEB-023 checkpoint required')
for parent in (path.parent,*path.parents):
    if parent==ROOT.parent:break
    if parent.is_symlink() or (hasattr(parent,'is_junction') and parent.is_junction()):p.error('Reparse destination rejected')
def save(plan):path.write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
if a.action=='enable':
    if path.exists():p.error('Fresh checkpoint required; no input replay')
    hook=mcp('companion.dvd_hook',context=identity)
    if hook.get('playerClass')!='':raise SystemExit('Preserve pre-existing custom player')
    before={k:mcp('companion.config_get',setting=k)['value'] for k in keys}
    plan={'utc':datetime.now(timezone.utc).isoformat(),'identity':identity,'before':before,'changed':[],'hookClass':None,'restored':False}
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f:json.dump(plan,f,indent=2)
    # All mutation intent is checkpointed BEFORE the request. Unknown outcomes
    # are resolved by exact readback on restore, never blindly replayed.
    state=mcp('ui.state',context=identity)
    if state.get('fullyLoaded'):mcp('media.control',context=identity,operation='stop')
    for key,value in keys.items():
        if before[key]==value:continue
        plan['changed'].append(key);save(plan)
        mcp('companion.config_set',setting=key,expected=before[key],value=value,confirm='true')
    plan['hookPending']=True;save(plan)
    selected=mcp('companion.dvd_hook',context=identity,expected='',enabled='true',confirm='true')
    if not selected.get('ownedNavigatorSelected'):raise RuntimeError('Owned navigator selection unverified; restore checkpoint')
    plan['hookClass']=selected['playerClass'];plan['hookPending']=False;save(plan)
    print(json.dumps({'enabled':True,'changedSettings':plan['changed'],'checkpoint':str(path),'normalPlaybackRequiresMcp':False}))
else:
    plan=json.loads(path.read_text(encoding='utf-8'))
    if plan.get('identity')!=identity or set(plan.get('before',{}))!=set(keys) or set(plan.get('changed',[]))-set(keys):raise RuntimeError('Checkpoint ownership mismatch')
    if plan.get('restored'):raise RuntimeError('Already restored; refuse replay')
    current=mcp('companion.dvd_hook',context=identity)
    if current.get('playerClass'):
        expected=plan.get('hookClass')
        if not expected and plan.get('hookPending') and current.get('ownedNavigatorSelected'):expected=current['playerClass']
        if current.get('playerClass')!=expected:raise RuntimeError('Concurrent hook changed; preserved')
        mcp('companion.dvd_hook',context=identity,expected=expected,enabled='false',confirm='true')
    state=mcp('ui.state',context=identity)
    if state.get('fullyLoaded'):mcp('media.control',context=identity,operation='stop')
    for key in reversed(plan['changed']):
        current=mcp('companion.config_get',setting=key)['value']
        if current==plan['before'][key]:continue
        if current!=keys[key]:raise RuntimeError('Concurrent setting changed; preserved '+key)
        mcp('companion.config_set',setting=key,expected=current,value=plan['before'][key],confirm='true')
    restored={k:mcp('companion.config_get',setting=k)['value'] for k in keys}
    if restored!=plan['before'] or mcp('companion.dvd_hook',context=identity).get('playerClass')!='':raise RuntimeError('Restoration mismatch')
    plan['restored']=True;plan['restoredUtc']=datetime.now(timezone.utc).isoformat();save(plan)
    print(json.dumps({'exactSettingsAndHookRestored':True,'checkpoint':str(path)}))
