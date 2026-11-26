#!/usr/bin/env python3
"""Preserve a bounded prefix of this task's active recording, never user media."""
import argparse,hashlib,importlib.util,json,shlex,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser();p.add_argument('--ownership-report',type=Path,required=True)
p.add_argument('--observe-existing',action='store_true',help='After unknown copy receipt, inspect only; never repeat or overwrite')
args=p.parse_args()
report_path=args.ownership_report.resolve(strict=True);active=(ROOT/'artifacts/active/WP11-008').resolve()
if report_path.parent!=active or report_path.is_symlink():raise RuntimeError('Exact owning field report required')
r=json.loads(report_path.read_text(encoding='utf-8'));owned=r.get('ownership',{});mid=owned.get('mediaId');source=owned.get('path')
if r.get('physicalPhone') is not True or not r.get('recordIntent') or not r.get('naturalCompletion') or r.get('cancelIntent') or not mid:raise RuntimeError('Require active owned natural capture')
m=C.request(cfg,'/SageTVWebPlayer/api/media?id='+str(mid));air=r['baseline']['source']
if not m.get('recording') or m.get('id')!=mid or len(m['files'])!=1 or m['files'][0]['path']!=source or m['files'][0]['streamSize']<18800000:raise RuntimeError('Exact active source guard')
if not source.startswith('/var/media/tv/') or air['airingId']!=43057:raise RuntimeError('Only observed WTTW startup failure source allowed')
target='/var/media/OpenSageTV_Vibe_Tests/WEB097_LIVE_WTTW_STARTUP.ts'
with C.ssh(cfg) as ssh:
 container=shlex.quote(cfg['unraid_container_name'])
 # Binary fixture creation only: exclusive output, fixed188-byte packet prefix,
 # read-only source; no Core/configuration/library mutation or filesystem delete.
 if not args.observe_existing:C.remote(ssh,'docker exec '+container+' dd if='+shlex.quote(source)+' of='+shlex.quote(target)+' bs=18800000 count=1 iflag=fullblock conv=excl status=none')
 size=int(C.remote(ssh,'docker exec '+container+' stat -c %s '+shlex.quote(target)).strip())
 if size!=18800000:raise RuntimeError('Owned prefix incomplete; preserve existing output, no copy replay')
 digest=C.remote(ssh,'docker exec '+container+' sha256sum '+shlex.quote(target)).split()[0]
 probe=json.loads(C.remote(ssh,'docker exec '+container+' /opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffprobe -v error -show_entries stream=index,codec_type,codec_name,width,height,field_order,r_frame_rate:format=duration,size -of json '+shlex.quote(target)))
if len(digest)!=64 or probe.get('format',{}).get('size')!='18800000':raise RuntimeError('Bounded fixture hash/size not confirmed')
out=ROOT/'artifacts/results/WEB-097';out.mkdir(parents=True,exist_ok=True)
result=dict(ownedMediaId=mid,originalAiringId=air['airingId'],path=target,bytes=18800000,sha256=digest,source=probe,coreChanged=False,libraryImported=False)
with (out/'STARTUP_FIXTURE.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
print(json.dumps(result))
