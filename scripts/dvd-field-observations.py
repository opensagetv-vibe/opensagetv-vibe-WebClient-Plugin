"""Read-only exact-producer observations shared by physical DVD field tools."""
import argparse,importlib.util,json,shlex
from pathlib import Path

def encoder_target(C,cfg,producer):
 if not isinstance(producer,str) or len(producer)!=32 or any(c not in '0123456789abcdef' for c in producer):
  raise RuntimeError('Invalid owned DVD producer')
 with C.ssh(cfg) as client:
  rows=C.remote(client,'docker exec '+shlex.quote(cfg['unraid_container_name'])+' ps -eww -o args').splitlines()
 matches=[shlex.split(row) for row in rows if '/'+producer+'/stream.m3u8' in row and ' -c:v ' in row and row.split()[0].endswith('/ffmpeg.real')]
 if len(matches)!=1:raise RuntimeError('Expected one exact owned DVD encoder')
 command=matches[0];playlist=command[-1]
 if not playlist.endswith('/'+producer+'/stream.m3u8'):raise RuntimeError('Encoder output identity changed')
 values=[command[i+1] for i,x in enumerate(command[:-1]) if x=='-b:v']
 probe=command[0].rsplit('/',1)[0]+'/ffprobe';segment=playlist.rsplit('/',1)[0]+'/seg_00002.ts'
 with C.ssh(cfg) as client:
  encoded=json.loads(C.remote(client,' '.join(shlex.quote(x) for x in ('docker','exec',cfg['unraid_container_name'],probe,'-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','json',segment))))
 sizes={(s.get('width'),s.get('height')) for s in encoded.get('streams',[])}
 if len(sizes)!=1:raise RuntimeError('Ambiguous owned encoded raster')
 width,height=sizes.pop()
 return dict(videoTarget=values[0] if len(values)==1 else None,encoder=command[command.index('-c:v')+1],encodedWidth=width,encodedHeight=height)

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--producer',required=True);a=p.parse_args()
 spec=importlib.util.spec_from_file_location('commission',Path(__file__).with_name('commission-mobile.py'))
 C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
 print(json.dumps(encoder_target(C,C.configuration(),a.producer)))
