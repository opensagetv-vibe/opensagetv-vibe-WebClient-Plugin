#!/usr/bin/env python3
"""Stage only the new generated one-picture DVD in the existing test import.

No server installation/configuration/Core change, no overwrite or alternative
staging on failure. The exact idle phone may remain connected; no playback is
interrupted. One public scan, then read-only exact-path resolution.
"""
import argparse,hashlib,importlib.util,json,stat
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
source=ROOT/'artifacts/test-media/VIBE_ONE_PICTURE_DVD'

def stage(nonfirst=False,observe=False):
    source=ROOT/'artifacts/test-media'/('VIBE_NONFIRST_DVD' if nonfirst else 'VIBE_ONE_PICTURE_DVD')
    cfg=C.configuration()
    def mcp(action,**v):return C.request(cfg,'/v1/control',dict(action=action,**v),mcp=True,timeout=120 if action=='library.scan' else 20)
    a=C.activity(cfg);contexts=mcp('ui.list').get('contexts')
    if a.get('recordingCount')!=0 or a.get('connectedClientCount')!=0 or contexts not in ([],['123c8282e1ee']):raise RuntimeError('Preserve recordings/other users')
    if contexts and mcp('ui.state',context=contexts[0]).get('fullyLoaded') is not False:raise RuntimeError('Preserve loaded phone playback')
    manifest=json.loads((source/'fixture.json').read_text(encoding='utf-8'))
    if manifest.get('generated') is not True or manifest.get('menuVideoPictures')!=1 or len(manifest.get('files',{}))!=6:raise RuntimeError('Exact generated fixture required')
    if nonfirst and (manifest.get('fixture')!='VIBE_NONFIRST_DVD' or manifest.get('mainTitle')!=2 or len(manifest.get('titles',[]))!=2):raise RuntimeError('Exact explicit two-title fixture required')
    if sum(v['bytes'] for v in manifest['files'].values())>10*1024*1024:raise RuntimeError('Bounded fixture exceeded')
    for name,value in manifest['files'].items():
        path=source/name
        if Path(name).parent!=Path('VIDEO_TS') or path.is_symlink() or not path.resolve().is_relative_to(source.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest()!=value['sha256']:raise RuntimeError('Fixture hash/path mismatch')
    leaf='WP10-NonFirst' if nonfirst else 'WP08-OnePicture'
    target=PurePosixPath('/mnt/user/sagemedia/OpenSageTV_Vibe_Tests')/leaf
    with C.ssh(cfg) as client,client.open_sftp() as ftp:
        for parent in (PurePosixPath('/mnt'),PurePosixPath('/mnt/user'),PurePosixPath('/mnt/user/sagemedia'),target.parent):
            if not stat.S_ISDIR(ftp.lstat(str(parent)).st_mode):raise RuntimeError('Ordinary test-root ancestor required')
        try:present=ftp.lstat(str(target))
        except FileNotFoundError:
            if observe:raise RuntimeError('No existing exact fixture to observe')
        else:
            if not observe:raise RuntimeError('Preserve existing fixture; no overwrite/staging replay')
            if not stat.S_ISDIR(present.st_mode):raise RuntimeError('Ordinary fixture directory required')
        if not observe:ftp.mkdir(str(target));ftp.mkdir(str(target/'VIDEO_TS'))
        if not stat.S_ISDIR(ftp.lstat(str(target/'VIDEO_TS')).st_mode):raise RuntimeError('Ordinary VIDEO_TS required')
        for name,value in manifest['files'].items():
            path=str(target/name)
            if not observe:ftp.put(str(source/name),path)
            if not stat.S_ISREG(ftp.lstat(path).st_mode):raise RuntimeError('Remote fixture not regular')
            with ftp.open(path,'rb') as stream:digest=hashlib.sha256(stream.read()).hexdigest()
            if digest!=value['sha256']:raise RuntimeError('Remote fixture hash mismatch')
    if not observe:
        scan=mcp('library.scan',wait_until_done='true')
        if not scan.get('requested'):raise RuntimeError('One public scan not accepted; no replay')
    found=mcp('media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/'+leaf+'/VIDEO_TS')
    print(json.dumps(dict(staged=not observe,observationOnly=observe,files=6,hashesVerified=True,publicScanAccepted=None if observe else True,
        mediaFileId=found.get('mediaFileId'),path='/var/media/OpenSageTV_Vibe_Tests/'+leaf)))
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--nonfirst',action='store_true')
    parser.add_argument('--observe-only',action='store_true',help='Hash-check the existing exact fixture and read its import ID; never upload/scan/replay')
    args=parser.parse_args();stage(args.nonfirst,args.observe_only)
