#!/usr/bin/env python3
"""Generate an explicit non-first-main DVD; never install/import or overwrite.

Use the existing dev image/toolchain with root artifacts/temp bind-mounted at
/vibe-task-temp. Work is retained there until reviewed and moved to deleteme;
canonical test-media and source XML retain their established project paths.
"""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--work-dir',required=True);a=p.parse_args()
    work=Path(a.work_dir);output=ROOT/'artifacts/test-media/VIBE_NONFIRST_DVD'
    if not work.resolve().is_relative_to(Path('/vibe-task-temp')):raise RuntimeError('Explicit workspace temp bind required')
    for path in (work,output):
        if path.exists():raise RuntimeError('Preserve existing fixture/work; no overwrite or alternate staging: '+str(path))
        if any(x.is_symlink() for x in path.parents):raise RuntimeError('Ordinary ancestors required')
    work.mkdir(parents=True);output.parent.mkdir(parents=True,exist_ok=True)
    def run(args,**kw):
        r=subprocess.run(args,cwd=work,check=False,timeout=90,stderr=subprocess.PIPE,**kw)
        if r.returncode:raise RuntimeError('Tool failed: '+r.stderr.decode('utf-8','replace')[-2000:])
        return r
    font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    text="color=0x183050:s=720x480:r=30000/1001,drawtext=fontfile="+font+":text='NON-FIRST MAIN TITLE':fontcolor=white:fontsize=28:x=100:y=60,drawtext=fontfile="+font+":text='MAIN - TITLE TWO':fontcolor=white:fontsize=26:x=110:y=148,drawtext=fontfile="+font+":text='EXTRA - TITLE ONE':fontcolor=white:fontsize=26:x=110:y=228"
    run(['ffmpeg','-hide_banner','-loglevel','error','-n','-f','lavfi','-i',text,'-frames:v','1','-c:v','mpeg2video','-pix_fmt','yuv420p','-aspect','16:9','-f','dvd','menu-plain.vob'])
    run(['convert','-size','720x480','xc:none','-stroke','yellow','-strokewidth','3','-fill','none','-draw','rectangle 82,140 638,184 rectangle 82,220 638,264','-colors','4','highlight.png'])
    with (work/'menu-plain.vob').open('rb') as source,(work/'menu.vob').open('xb') as target:
        run(['spumux','-m','dvd',str(ROOT/'tests/fixtures/dvd-nonfirst-menu.xml')],stdin=source,stdout=target)
    for name,seconds,color,frequency,label in [('extra',4,'0x8b2020',440,'EXTRA TITLE ONE'),('main',12,'0x20508b',1000,'MAIN TITLE TWO')]:
        v=f"color={color}:s=720x480:r=30000/1001:d={seconds},drawtext=fontfile={font}:text='{label}':fontcolor=white:fontsize=40:x=100:y=190,drawbox=x=mod(t*140\\,600):y=310:w=90:h=50:color=yellow:t=fill"
        run(['ffmpeg','-hide_banner','-loglevel','error','-n','-f','lavfi','-i',v,'-f','lavfi','-i',f'sine=frequency={frequency}:sample_rate=48000:duration={seconds}','-target','ntsc-dvd','-aspect','16:9','-c:a','ac3','-b:a','192k','-shortest',name+'.vob'])
    run(['dvdauthor','-o',str(output),'-x',str(ROOT/'tests/fixtures/dvd-nonfirst-author.xml')],stdout=subprocess.DEVNULL)
    expected={'VIDEO_TS.IFO','VIDEO_TS.BUP','VTS_01_0.IFO','VTS_01_0.BUP','VTS_01_0.VOB','VTS_01_1.VOB'}
    if {x.name for x in (output/'VIDEO_TS').iterdir()}!=expected:raise RuntimeError('Unexpected authored tree; preserve for review')
    files={str(x.relative_to(output)):dict(bytes=x.stat().st_size,sha256=hashlib.sha256(x.read_bytes()).hexdigest()) for x in output.rglob('*') if x.is_file()}
    manifest=dict(fixture='VIBE_NONFIRST_DVD',generated=True,menuVideoPictures=1,menuAudio=False,mainTitle=2,
        titles=[dict(title=1,label='extra',seconds=4,chapterStarts=[0]),dict(title=2,label='main',seconds=12,chapterStarts=[0,4,8])],files=files)
    with (output/'fixture.json').open('x',encoding='utf-8') as f:json.dump(manifest,f,indent=2)
    print(json.dumps(dict(generated=True,mainTitle=2,files=len(files),bytes=sum(v['bytes'] for v in files.values()),output=str(output),work=str(work))))
if __name__=='__main__':main()
