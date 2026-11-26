#!/usr/bin/env python3
"""Bounded stock232 physical-iPhone test setup via existing public MCP APIs.

No Core/config changes, unrelated media controls or playback dependency on MCP.
The phone's normal browser controls remain the subjects of the physical gates.
"""
import argparse,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
parser=argparse.ArgumentParser();parser.add_argument('action',choices=['watch-caption-fixture','watch-user-nightline','watch-dvd-fixture','dvd-root','dvd-next','dvd-select','dvd-subtitle-toggle','seek-fixture-start','seek-fixture-30','seek-fixture-60','seek-current-nightline','captions-on','captions-off','pause','play','back','info','restore-custom-stv','state'])
parser.add_argument('--require-feature',action='store_true',help='For dvd-next only: refuse menu/late feature and independently observe the changed chapter')
args=parser.parse_args();cfg=C.configuration();identity='123c8282e1ee'
if args.require_feature and args.action!='dvd-next':parser.error('Feature guard is only for the one dvd-next test action')
def mcp(action,**v):return C.request(cfg,'/v1/control',dict(action=action,**v),mcp=True)
activity=C.activity(cfg);contexts=mcp('ui.list').get('contexts')
if activity.get('recordingCount')!=0 or activity.get('connectedClientCount')!=0 or contexts!=[identity]:
    raise RuntimeError('Require only the approved exact iPhone UI and no recordings/other clients')
if args.action=='back':
    result=mcp('ui.command',context=identity,command='Back')
    print(json.dumps({'action':'Back','ok':result.get('ok'),'accepted':result.get('accepted')}));raise SystemExit()
if args.action=='state':
    state=mcp('ui.state',context=identity)
    print(json.dumps({'activity':activity,'state':state,'stv':mcp('captions.get',context=identity)},indent=2));raise SystemExit()
if args.action in ('dvd-root','dvd-next','dvd-select','dvd-subtitle-toggle'):
    state=mcp('ui.state',context=identity)
    if state.get('dvd') is not True or (state.get('media') or {}).get('mediaFileId')!=20819:raise RuntimeError('Require exact authored DVD')
    if args.require_feature and (state.get('dvdMenu') is not False or state.get('dvdChapter')!=1 or not 0<=state.get('rawMediaTimeMs',-1)<60000):raise RuntimeError('Require fresh chapter1 feature, not a menu or late EOF')
    if args.action=='dvd-select' and state.get('dvdMenu') is not True:raise RuntimeError('Public decoder-test Select requires exact authored menu')
    command={'dvd-root':'DVD Menu','dvd-next':'DVD Next Chapter','dvd-select':'Select','dvd-subtitle-toggle':'DVD Subtitle Toggle'}[args.action]
    result=mcp('ui.command',context=identity,command=command)
    observation={}
    if args.require_feature:
        import time
        time.sleep(1)
        after=mcp('ui.state',context=identity)
        observation=dict(beforeChapter=state.get('dvdChapter'),afterChapter=after.get('dvdChapter'),afterMenu=after.get('dvdMenu'),chapterConfirmed=after.get('dvdChapter')==2 and after.get('dvdMenu') is False)
    print(json.dumps({'action':args.action,'accepted':result.get('accepted'),'ok':result.get('ok'),**observation}));raise SystemExit(0 if not args.require_feature or observation['chapterConfirmed'] else 1)
if args.action in ('info','restore-custom-stv'):
    stv=mcp('captions.get',context=identity).get('stvFile','')
    if args.action=='restore-custom-stv' and not stv.endswith('/SageTV7.xml'):
        raise RuntimeError('Require the borrowed stock STV before restoration')
    result=mcp('ui.command',context=identity,command='Home' if args.action=='restore-custom-stv' else 'Info')
    print(json.dumps({'action':args.action,'accepted':result.get('accepted'),'ok':result.get('ok')}));raise SystemExit()
if args.action=='watch-dvd-fixture':
    fixture=mcp('media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/OpenSageTV_Vibe_Test_DVD')
    if fixture.get('mediaFileId')!=20819:raise RuntimeError('Exact authored DVD fixture unavailable')
    result=mcp('media.watch',context=identity,media_id=20819,wait_ms=0)
    print(json.dumps({'action':args.action,'accepted':result.get('accepted'),'ok':result.get('ok')}));raise SystemExit()
if args.action in ('captions-on','captions-off','pause','play'):
    state=mcp('ui.state',context=identity)
    if (state.get('media') or {}).get('mediaFileId') not in (20905,27166):raise RuntimeError('Unknown source; refusing test control')
    result=mcp('captions.set',context=identity,state='CC1' if args.action=='captions-on' else 'Off') if args.action.startswith('captions-') else mcp('media.control',context=identity,operation=args.action)
    print(json.dumps({'action':args.action,'ok':result.get('ok'),'captionState':result.get('state')}));raise SystemExit()
if args.action=='watch-user-nightline':
    fixture=mcp('media.resolve_exact_path',path='/var/media/tv/Nightline-66287549-0.ts')
    if fixture.get('mediaFileId')!=27166:raise RuntimeError('Exact user-reproduced recording unavailable')
    result=mcp('media.watch',context=identity,media_id=27166,wait_ms=0)
    print(json.dumps({'action':args.action,'accepted':result.get('accepted'),'ok':result.get('ok')}));raise SystemExit()
if args.action=='seek-current-nightline':
    state=mcp('ui.state',context=identity)
    if (state.get('media') or {}).get('mediaFileId')!=27166:raise RuntimeError('Exact user-reproduced Nightline is not current')
    result=mcp('media.seek',context=identity,target_ms=300000)
    print(json.dumps({'accepted':result.get('accepted'),'ok':result.get('ok'),'targetMs':300000}));raise SystemExit()
fixture=mcp('media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/VibeCaptionTest-1080i-CEA608-90s-2s.ts')
media_id=fixture.get('mediaFileId')
if not media_id:raise RuntimeError('Canonical fixture unavailable')
if args.action=='watch-caption-fixture':
    result=mcp('media.watch',context=identity,media_id=media_id,wait_ms=0)
else:
    state=mcp('ui.state',context=identity)
    if (state.get('media') or {}).get('mediaFileId')!=media_id:raise RuntimeError('Exact fixture is not current; refuse seek')
    result=mcp('media.seek',context=identity,target_ms={'seek-fixture-start':0,'seek-fixture-30':30000,'seek-fixture-60':60000}[args.action])
print(json.dumps({'action':args.action,'fixtureId':media_id,'accepted':result.get('accepted'),'ok':result.get('ok')},indent=2))
