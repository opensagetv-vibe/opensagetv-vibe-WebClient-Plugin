#!/usr/bin/env python3
"""Read-only, bounded search for the byte-exact original rollback WAR.

Inspect local WARs and ZIP members, including nested installer ZIPs. Never
extract, restore, install, download or modify candidate archives. Explicitly
report skipped bounds/errors; a filename-only search is not absence proof.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import time
import zipfile

EXPECTED='069ec4cd1b080f896311e98a63a6c9168bdc9091039f4326e1506f54f965742d'
MAX_ARCHIVE=512*1024*1024
MAX_MEMBER=32*1024*1024
MAX_EXPANDED=256*1024*1024
MAX_MEMBERS=50000


def inspect_zip(source,label,result,depth=0,budget=None,max_member=None):
    budget=budget if budget is not None else [MAX_EXPANDED]
    limit=MAX_MEMBER if max_member is None else max_member
    if not isinstance(limit,int) or not 1<=limit<=128*1024*1024:raise ValueError('Invalid explicit member bound')
    try:
        with zipfile.ZipFile(source) as archive:
            entries=archive.infolist()
            if len(entries)>MAX_MEMBERS:
                result['skipped'].append(dict(path=label,reason='member-count-bound'));return
            result['archivesInspected']+=1
            for entry in entries:
                name=entry.filename
                if entry.is_dir() or not name.lower().endswith(('.war','.zip')):continue
                member=label+'!'+name
                if entry.flag_bits&1:
                    result['skipped'].append(dict(path=member,reason='encrypted-member'));continue
                if entry.file_size>limit or entry.file_size>budget[0]:
                    result['skipped'].append(dict(path=member,reason='expanded-byte-bound'));continue
                if name.lower().endswith('.zip') and depth>=2:
                    result['skipped'].append(dict(path=member,reason='nested-depth-bound'));continue
                # ZipExtFile enforces CRC; bound actual output too rather than
                # trusting a malformed central-directory size alone.
                with archive.open(entry) as handle:data=handle.read(limit+1)
                budget[0]-=len(data)
                if len(data)!=entry.file_size or len(data)>limit:
                    result['skipped'].append(dict(path=member,reason='member-size-mismatch'));continue
                if name.lower().endswith('.war'):
                    record_war(data,member,result)
                else:
                    inspect_zip(io.BytesIO(data),member,result,depth+1,budget,limit)
    except (OSError,ValueError,RuntimeError,zipfile.BadZipFile,NotImplementedError):
        result['skipped'].append(dict(path=label,reason='archive-unreadable'))


def record_war(data,label,result):
    digest=hashlib.sha256(data).hexdigest()
    row=dict(path=label,bytes=len(data),sha256=digest)
    result['wars'].append(row)
    if digest==EXPECTED:result['matches'].append(row)


def inspect_file(path,root,result,large_zip_metadata=False,max_member=None):
    try:
        # Reject reparse-point traversal, including junctions, before reading.
        relative=path.relative_to(root)
        if not path.resolve().is_relative_to(root.resolve()):raise ValueError('outside-root')
        for ancestor in (path,*path.parents):
            if ancestor==root:break
            attrs=getattr(ancestor.lstat(),'st_file_attributes',0)
            if ancestor.is_symlink() or attrs&0x400:raise ValueError('reparse-point')
        label=relative.as_posix();size=path.stat().st_size
        if size>MAX_ARCHIVE and not (large_zip_metadata and path.suffix.lower()=='.zip'):
            result['skipped'].append(dict(path=label,reason='archive-size-bound'));return
        if path.suffix.lower()=='.war':
            if size>MAX_MEMBER:
                result['skipped'].append(dict(path=label,reason='war-size-bound'));return
            record_war(path.read_bytes(),label,result)
        else:inspect_zip(path,label,result,max_member=max_member)
    except (OSError,ValueError):
        result['skipped'].append(dict(path=str(path.relative_to(root)),reason='path-unavailable-or-reparse'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True)
    parser.add_argument('--large-zip-metadata',action='store_true',help='Inspect large ZIP central directories; member expansion bounds unchanged')
    parser.add_argument('--member-limit-mib',type=int,choices=(32,64,128),default=32,help='Explicit nested-member bound; total256MiB expansion/depth limits still apply')
    parser.add_argument('--candidate',action='append',help='Inspect only this exact workspace-relative archive; repeat for a bounded follow-up')
    args=parser.parse_args()
    repo=Path(__file__).resolve().parents[1];root=repo.parent.parent.resolve()
    output=Path(args.output).resolve()
    allowed=repo/'artifacts/active/WP17-004'
    if not output.is_relative_to(allowed.resolve()):parser.error('Exact task-owned output required')
    if output.exists():parser.error('Refuse report overwrite')
    if args.candidate:
        paths=sorted(set(args.candidate))
        if any(Path(s).is_absolute() or '..' in Path(s).parts or Path(s).suffix.lower() not in ('.war','.zip') for s in paths):
            parser.error('Exact workspace-relative ZIP/WAR candidates required')
    else:
        listed=subprocess.run(['rg','--files','--hidden','--no-ignore','-g','*.war','-g','*.zip'],
                              cwd=root,capture_output=True,text=True,check=True,timeout=20)
        paths=sorted(set(listed.stdout.splitlines()))
    result=dict(task='WP17-004',readOnlyCandidates=True,expectedWarSha256=EXPECTED,
                candidates=len(paths),memberLimitBytes=args.member_limit_mib*1024*1024,
                expansionBudgetBytes=MAX_EXPANDED,archivesInspected=0,wars=[],matches=[],skipped=[])
    started=time.monotonic()
    for index,relative in enumerate(paths):
        if time.monotonic()-started>120:
            result['skipped'].append(dict(reason='total-time-bound',remaining=len(paths)-index));break
        inspect_file(root/relative,root,result,args.large_zip_metadata,args.member_limit_mib*1024*1024)
    result['elapsedSeconds']=round(time.monotonic()-started,3)
    result['coverageComplete']=not result['skipped']
    result['status']='EXACT_BASELINE_FOUND' if result['matches'] else 'NO_MATCH_IN_INSPECTED_BYTES'
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as handle:json.dump(result,handle,indent=2)
    print(json.dumps(dict(status=result['status'],candidates=len(paths),archives=result['archivesInspected'],
                         wars=len(result['wars']),matches=result['matches'],skipped=len(result['skipped']),
                         elapsedSeconds=result['elapsedSeconds'],report=str(output))))


if __name__=='__main__':main()
