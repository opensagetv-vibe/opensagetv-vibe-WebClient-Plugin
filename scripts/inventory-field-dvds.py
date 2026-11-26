#!/usr/bin/env python3
"""Read-only bounded stock232 DVD inventory; no mounts/imports/Core edits."""
import argparse,base64,hashlib,importlib.util,json,shlex,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--inspect-disc',choices=('aladdin','pal','sparse'))
args=parser.parse_args()
if args.inspect_disc:
    roots={'aladdin':'/var/media/videos/Aidens_Movies/ALADDIN',
           'pal':'/var/media/OpenSageTV_Vibe_Tests/VIBE_AUTHORED_DVD_PAL',
           'sparse':'/var/media/OpenSageTV_Vibe_Tests/VIBE_AUTHORED_DVD_SPARSE'}
    root=roots[args.inspect_disc]+'/VIDEO_TS';rows=[]
    with C.ssh(cfg) as client:
        def header(filename,signature):
            command=('docker exec '+shlex.quote(cfg['unraid_container_name'])+
                ' head -c 256 '+shlex.quote(root+'/'+filename)+' | base64')
            data=base64.b64decode(C.remote(client,command),validate=False)
            if len(data)!=256 or data[:12]!=signature:raise RuntimeError('Invalid bounded IFO header')
            return data
        vmg=header('VIDEO_TS.IFO',b'DVDVIDEO-VMG');count=struct.unpack_from('>H',vmg,0x3e)[0]
        if not 1<=count<=16:raise RuntimeError('Title-set count outside this bounded inspection')
        rows.append(dict(file='VIDEO_TS.IFO',menuVobsSector=struct.unpack_from('>I',vmg,0xc0)[0],
            menuTableSector=struct.unpack_from('>I',vmg,0xc8)[0],headerSha256=hashlib.sha256(vmg).hexdigest()))
        for number in range(1,count+1):
            name='VTS_%02d_0.IFO'%number;vts=header(name,b'DVDVIDEO-VTS')
            rows.append(dict(file=name,menuVobsSector=struct.unpack_from('>I',vts,0xc0)[0],
                menuTableSector=struct.unpack_from('>I',vts,0xd0)[0],headerSha256=hashlib.sha256(vts).hexdigest()))
    print(json.dumps(dict(readOnly=True,source=args.inspect_disc,titleSets=count,rows=rows,
        noAuthoredMenuTables=all(r['menuTableSector']==0 and r['menuVobsSector']==0 for r in rows),
        noAuthoredMenuVideo=all(r['menuVobsSector']==0 for r in rows)),indent=2))
    raise SystemExit()
with C.ssh(cfg) as client:
    # Existing authorized media mounts only. No filesystem changes or privileged
    # mount/unmount attempts; finite depth/time/result count bound this read.
    command=('docker exec '+shlex.quote(cfg['unraid_container_name'])+
        " timeout 15 find /var/media/videos /var/media/test /var/media/OpenSageTV_Vibe_Tests -maxdepth 5 -type d -iname VIDEO_TS -print")
    paths=C.remote(client,command).splitlines()
    if len(paths)>200:raise RuntimeError('Inventory exceeds bound')
rows=[]
for path in paths:
    try:
        r=C.request(cfg,'/v1/control',dict(action='media.resolve_exact_path',path=path),mcp=True,timeout=8)
        rows.append(dict(path=path,mediaFileId=r.get('mediaFileId'),indexed=bool(r.get('mediaFileId'))))
    except RuntimeError:rows.append(dict(path=path,indexed=False))
print(json.dumps({'readOnly':True,'stockServer':'.232','dvds':rows},indent=2))
