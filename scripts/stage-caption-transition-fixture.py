#!/usr/bin/env python3
"""Stage only the canonical generated caption fixture using public library scan.

No Core/install/config writes. Exact new test directory/readback guards.
--verify-existing never uploads or scans again after an unknown receipt.
"""
import argparse,hashlib,importlib.util,json,shlex,stat,time
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--verify-existing',action='store_true');a=p.parse_args()
 cfg=C.configuration();activity=C.activity(cfg)
 if activity['recordingCount'] or activity['connectedClientCount']:raise RuntimeError('No recording/other-client interruption')
 contexts=C.request(cfg,'/v1/control',dict(action='ui.list'),mcp=True)['contexts']
 if contexts not in ([],['123c8282e1ee']):raise RuntimeError('Unrelated UI present')
 if contexts and C.request(cfg,'/v1/control',dict(action='ui.state',context=contexts[0]),mcp=True).get('fullyLoaded'):raise RuntimeError('Phone playback active')
 source=ROOT/'artifacts/test-media/VIBE_CAPTION_PMT';name='VibeCaptions-English-Spanish-PMT.ts'
 meta=json.loads((source/'fixture.json').read_text())
 if meta.get('name')!=name or not meta.get('generated') or meta.get('originalBroadcast') is not False:raise RuntimeError('Canonical generated identity required')
 files=[source/name,source/'fixture.json']
 for file in files:
  if not file.is_file() or any(p.is_symlink() or getattr(p,'is_junction',lambda:False)() for p in (file,*file.parents)):raise RuntimeError('Ordinary canonical files required')
 if hashlib.sha256(files[0].read_bytes()).hexdigest()!=meta['sha256']:raise RuntimeError('Source checksum mismatch')
 with C.ssh(cfg) as client:
  container=shlex.quote(cfg['unraid_container_name'])
  if any(x.strip() in ('ffmpeg.real','ffmpeg_MIM') for x in C.remote(client,'docker exec '+container+' ps -eo comm').splitlines()):raise RuntimeError('Another producer active')
  info=json.loads(C.remote(client,'docker inspect '+container))[0]
  mounts=[m['Source'] for m in info['Mounts'] if m['Destination']=='/var/media']
  if mounts!=['/mnt/user/sagemedia']:raise RuntimeError('Reviewed media mount changed')
  parent=PurePosixPath(mounts[0])/'OpenSageTV_Vibe_Tests';target=parent/'WP04-Caption-PMT'
  with client.open_sftp() as ftp:
   for directory in (PurePosixPath('/mnt'),PurePosixPath('/mnt/user'),PurePosixPath(mounts[0]),parent):
    if not stat.S_ISDIR(ftp.lstat(str(directory)).st_mode):raise RuntimeError('Ordinary ancestors required')
   if a.verify_existing:
    if not stat.S_ISDIR(ftp.lstat(str(target)).st_mode):raise RuntimeError('Missing exact existing fixture')
   else:
    try:ftp.lstat(str(target))
    except FileNotFoundError:pass
    else:raise RuntimeError('Exact directory exists; no overwrite/replay')
    ftp.mkdir(str(target))
   for file in files:
    destination=str(target/file.name)
    if not a.verify_existing:ftp.put(str(file),destination)
    if not stat.S_ISREG(ftp.lstat(destination).st_mode):raise RuntimeError('Regular fixture destination required')
    with ftp.open(destination,'rb') as stream:digest=hashlib.sha256(stream.read()).hexdigest()
    if digest!=hashlib.sha256(file.read_bytes()).hexdigest():raise RuntimeError('Readback hash mismatch')
 if not a.verify_existing:
  scan=C.request(cfg,'/v1/control',dict(action='library.scan',wait_until_done='true'),mcp=True,timeout=60)
  if not scan.get('requested'):raise RuntimeError('Scan receipt unknown; no replay')
 path='/var/media/OpenSageTV_Vibe_Tests/WP04-Caption-PMT/'+name
 media=C.request(cfg,'/v1/control',dict(action='media.resolve_exact_path',path=path),mcp=True)
 if not media.get('mediaFileId'):raise RuntimeError('Exact source not imported; no alternate scan')
 report=dict(staged=True,generated=True,mediaFileId=media['mediaFileId'],path=path,sha256=meta['sha256'],readOnly=a.verify_existing)
 folder=ROOT/'artifacts/active/WP04-007';folder.mkdir(parents=True,exist_ok=True)
 with (folder/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-caption-fixture-stage.json')).open('x') as f:json.dump(report,f,indent=2)
 print(json.dumps(report))
if __name__=='__main__':main()
