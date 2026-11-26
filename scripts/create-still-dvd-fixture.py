#!/usr/bin/env python3
"""Generate a tiny canonical one-picture DVD menu; never install/import it.

Run in the existing Linux dev container. New exact output/work trees only;
preserve partial failures for inspection rather than deleting user files.
"""
import argparse,hashlib,json,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
output=ROOT/'artifacts/test-media/VIBE_ONE_PICTURE_DVD'
work=None

def run(args,**kwargs):
    result=subprocess.run(args,cwd=work,check=False,timeout=60,stderr=subprocess.PIPE,**kwargs)
    if result.returncode:raise RuntimeError('Fixture tool failed: '+result.stderr.decode('utf-8','replace')[-2000:])
    return result

def main():
    global work
    for path in (output,):
        if path.exists():raise RuntimeError('Preserve existing fixture/staging; no overwrite or alternate copy: '+str(path))
        for parent in path.parents:
            if parent.is_symlink():raise RuntimeError('Fixture ancestor symlink rejected')
    work=Path(tempfile.mkdtemp(prefix='vibe-web085-still-'))
    print(json.dumps(dict(ownedSystemTemporaryDirectory=str(work))),flush=True)
    output.parent.mkdir(parents=True,exist_ok=True)
    font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    background="color=0x183050:s=720x480:r=30000/1001,drawtext=fontfile="+font+":text='ONE PICTURE DVD MENU':fontcolor=white:fontsize=28:x=100:y=45,drawtext=fontfile="+font+":text='Select to play five seconds':fontcolor=white:fontsize=24:x=100:y=105"
    run(['ffmpeg','-hide_banner','-loglevel','error','-n','-f','lavfi','-i',background,
         '-frames:v','1','-c:v','mpeg2video','-pix_fmt','yuv420p','-aspect','16:9','-f','dvd','menu-plain.vob'])
    run(['convert','-size','720x480','xc:none','-stroke','yellow','-strokewidth','3',
         '-fill','none','-draw','rectangle 82,100 638,140','-colors','4','highlight.png'])
    with (work/'menu-plain.vob').open('rb') as source,(work/'menu.vob').open('xb') as target:
        run(['spumux','-m','dvd',str(ROOT/'tests/fixtures/dvd-still-menu.xml')],stdin=source,stdout=target)
    run(['ffmpeg','-hide_banner','-loglevel','error','-n','-f','lavfi','-i','testsrc2=size=720x480:rate=30000/1001:duration=5',
         '-f','lavfi','-i','sine=frequency=660:sample_rate=48000:duration=5','-target','ntsc-dvd',
         '-aspect','16:9','-c:a','ac3','-b:a','192k','-shortest','feature.vob'])
    run(['dvdauthor','-o',str(output),'-x',str(ROOT/'tests/fixtures/dvd-still-author.xml')],stdout=subprocess.DEVNULL)
    verify()

def verify():
    if (output/'fixture.json').exists():raise RuntimeError('Preserve existing fixture manifest')
    required=['VIDEO_TS.IFO','VIDEO_TS.BUP','VTS_01_0.IFO','VTS_01_0.BUP','VTS_01_0.VOB','VTS_01_1.VOB']
    if sorted(p.name for p in (output/'VIDEO_TS').iterdir())!=sorted(required):raise RuntimeError('Unexpected authored fixture files')
    for p in output.rglob('*'):
        if p.is_symlink():raise RuntimeError('Fixture symlink rejected')
    frames=run(['ffprobe','-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=nb_read_frames',
        '-of','json',str(output/'VIDEO_TS/VTS_01_0.VOB')],stdout=subprocess.PIPE)
    values=json.loads(frames.stdout)['streams']
    if len(values)!=1 or values[0].get('nb_read_frames')!='1':raise RuntimeError('Authored menu must contain exactly one real video picture')
    files={str(p.relative_to(output)):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
           for p in output.rglob('*') if p.is_file()}
    manifest=dict(fixture='VIBE_ONE_PICTURE_DVD',generated=True,menuVideoPictures=1,menuAudio=False,
        titleDurationSeconds=5,source='canonical source XML and generated FFmpeg test pattern',files=files)
    with (output/'fixture.json').open('x',encoding='utf-8') as target:json.dump(manifest,target,indent=2)
    print(json.dumps(dict(generated=True,menuVideoPictures=1,files=len(files),output=str(output))))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--verify-existing',action='store_true',help='Verify exact completed generated tree and create its new manifest only')
    if p.parse_args().verify_existing:verify()
    else:main()
