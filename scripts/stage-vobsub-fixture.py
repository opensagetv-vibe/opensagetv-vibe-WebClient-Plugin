#!/usr/bin/env python3
"""Stage one owned P06 fixture, never Core/plugin binaries or user media.

Explicit idle guard, exact reviewed sample hashes, new directory only, SFTP
regular-file copies and readback hashes. A partial failure remains in place;
never silently overwrite, remove or create an alternate staging copy.
"""
import hashlib,importlib.util,json,shlex,stat
from pathlib import Path,PurePosixPath

ROOT=Path(__file__).resolve().parents[1];WORKSPACE=ROOT.parent.parent
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
FIXTURE='VibeVobSubExternal-P06'
PUBLIC='X.The.Movie.DVDivX-SChiZO'
HASHES={'idx':'75d31f05ba05b8fd3efca87d8109cde7','sub':'03b4ad4d5386aa2ec520e4dbc9c986be','ifo':'25db19f8b62b5ccd6b3b05146dfd57dc'}

def stage():
    cfg=C.configuration();a=C.activity(cfg)
    if not a.get('safeToRestart'):raise RuntimeError('Independent idle server required for fixture staging')
    source=WORKSPACE/'artifacts/temp/wp06-vobsub-public-sample'
    files={ext:source/(PUBLIC+'.'+ext) for ext in HASHES};files['ts']=source/(FIXTURE+'.ts')
    for ext,path in files.items():
        if not path.is_file() or path.is_symlink() or path.resolve().parent!=source.resolve():raise RuntimeError('Exact reviewed local fixture required')
        if ext in HASHES and hashlib.md5(path.read_bytes()).hexdigest()!=HASHES[ext]:raise RuntimeError('Public sample hash mismatch')
    with C.ssh(cfg) as client:
        container=shlex.quote(cfg['unraid_container_name'])
        info=json.loads(C.remote(client,'docker inspect '+container))[0]
        mounts=[m['Source'] for m in info['Mounts'] if m['Destination']=='/var/media']
        if mounts!=['/mnt/user/sagemedia']:raise RuntimeError('Reviewed test-media mount changed')
        parent=PurePosixPath(mounts[0])/'OpenSageTV_Vibe_Tests'
        target=parent/'WP06-VobSub'
        with client.open_sftp() as ftp:
            for directory in (PurePosixPath('/mnt'),PurePosixPath('/mnt/user'),PurePosixPath(mounts[0]),parent):
                if not stat.S_ISDIR(ftp.lstat(str(directory)).st_mode):raise RuntimeError('Test-fixture ancestor is not an ordinary directory')
            try:ftp.lstat(str(target))
            except FileNotFoundError:pass
            else:raise RuntimeError('Fixture already exists; review exact path, do not overwrite/replay staging')
            ftp.mkdir(str(target));verified=[]
            for ext,path in files.items():
                destination=str(target/(FIXTURE+'.'+ext));ftp.put(str(path),destination)
                if not stat.S_ISREG(ftp.lstat(destination).st_mode):raise RuntimeError('Fixture is not a regular file')
                with ftp.open(destination,'rb') as stream:actual=hashlib.sha256(stream.read()).hexdigest()
                if actual!=hashlib.sha256(path.read_bytes()).hexdigest():raise RuntimeError('Fixture readback hash mismatch')
                verified.append(dict(extension=ext,sha256=actual,bytes=path.stat().st_size))
    # Parent is an established imported test-fixture directory. Do not add an
    # overlapping import root or alter existing library paths just for this test.
    result=C.request(cfg,'/v1/control',dict(action='library.scan',wait_until_done='true'),mcp=True,timeout=60)
    if not result.get('requested'):raise RuntimeError('Public fixture scan outcome unknown; not replayed')
    media=C.request(cfg,'/v1/control',dict(action='media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/WP06-VobSub/'+FIXTURE+'.ts'),mcp=True)
    if not media.get('mediaFileId'):raise RuntimeError('Fixture not imported; no alternate import or scan replay')
    return dict(staged=True,canonicalTestFixture=True,mediaFileId=media['mediaFileId'],files=verified)

if __name__=='__main__':print(json.dumps(stage(),indent=2))
