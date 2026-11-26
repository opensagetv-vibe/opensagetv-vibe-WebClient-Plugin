#!/usr/bin/env python3
"""Stage only the generated canonical audio fixture into the established test root.

Public library scan/exact resolution only. No Core, installation or configuration
writes; new exact directory, validated regular files/readback, never overwrite.
"""
import hashlib, importlib.util, json, shlex, stat
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('commission', ROOT/'scripts/commission-mobile.py')
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)


def main():
    cfg = C.configuration()
    if not C.activity(cfg).get('safeToRestart'): raise RuntimeError('Independent idle server required')
    source = ROOT/'artifacts/test-media/VIBE_AUDIO_PMT'
    meta = json.loads((source/'fixture.json').read_text(encoding='utf-8'))
    name = 'VibeAudio-PMT-Mono-to-51.ts'
    if meta.get('name') != name or not meta.get('generated') or meta.get('originalBroadcast') is not False:
        raise RuntimeError('Canonical fixture identity required')
    files = [source/name, source/'fixture.json']
    for file in files:
        if not file.is_file() or file.is_symlink() or any(p.is_symlink() for p in file.parents):
            raise RuntimeError('Canonical regular files required')
    if hashlib.sha256(files[0].read_bytes()).hexdigest() != meta['sha256']: raise RuntimeError('Fixture hash changed')
    with C.ssh(cfg) as client:
        info = json.loads(C.remote(client, 'docker inspect '+shlex.quote(cfg['unraid_container_name'])))[0]
        mounts = [m['Source'] for m in info['Mounts'] if m['Destination'] == '/var/media']
        if mounts != ['/mnt/user/sagemedia']: raise RuntimeError('Reviewed test mount changed')
        parent = PurePosixPath(mounts[0])/'OpenSageTV_Vibe_Tests'; target = parent/'WP12-Audio-PMT'
        with client.open_sftp() as ftp:
            for directory in (PurePosixPath('/mnt'), PurePosixPath('/mnt/user'), PurePosixPath(mounts[0]), parent):
                if not stat.S_ISDIR(ftp.lstat(str(directory)).st_mode): raise RuntimeError('Ordinary ancestors required')
            try: ftp.lstat(str(target))
            except FileNotFoundError: pass
            else: raise RuntimeError('Exact fixture directory exists; no overwrite/replay')
            ftp.mkdir(str(target))
            for file in files:
                destination = str(target/file.name); ftp.put(str(file), destination)
                if not stat.S_ISREG(ftp.lstat(destination).st_mode): raise RuntimeError('Regular destination required')
                with ftp.open(destination, 'rb') as stream: actual = hashlib.sha256(stream.read()).hexdigest()
                if actual != hashlib.sha256(file.read_bytes()).hexdigest(): raise RuntimeError('Readback hash mismatch')
    scan = C.request(cfg, '/v1/control', dict(action='library.scan', wait_until_done='true'), mcp=True, timeout=60)
    if not scan.get('requested'): raise RuntimeError('Public scan outcome unknown; no replay')
    path = '/var/media/OpenSageTV_Vibe_Tests/WP12-Audio-PMT/'+name
    media = C.request(cfg, '/v1/control', dict(action='media.resolve_exact_path', path=path), mcp=True)
    if not media.get('mediaFileId'): raise RuntimeError('Exact fixture not imported; no alternate import')
    print(json.dumps(dict(staged=True, generated=True, mediaFileId=media['mediaFileId'], path=path, sha256=meta['sha256'])))


if __name__ == '__main__': main()
