#!/usr/bin/env python3
"""Canonical generated A/V + two DVB languages + PMT removal/restoration.

Uses the existing dev FFmpeg and independently generated ETSI vectors. Never
reads broadcast/user media, contacts a server or changes playback/settings.
The fixture is not evidence of original-broadcast or physical acceptance.
"""
import argparse,hashlib,importlib.util,json,struct,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'artifacts/test-media/VIBE_CAPTION_PMT'
NAME='VibeCaptions-English-Spanish-PMT.ts'
spec=importlib.util.spec_from_file_location('vectors',ROOT/'scripts/parity/generate_fixtures.py')
V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)

def run(args):
 p=subprocess.run(args,capture_output=True,timeout=90)
 if p.returncode:raise RuntimeError('Fixture tool failed: '+p.stderr.decode(errors='replace')[-1200:])
 return p.stdout

def payload_start(packet):
 if len(packet)!=188 or packet[0]!=0x47:raise ValueError('Transport framing')
 if not packet[3]&0x10:return None
 return 4+(packet[4]+1 if packet[3]&0x20 else 0)

def packet_pts(packet):
 start=payload_start(packet)
 if start is None or not packet[1]&0x40:return None
 pes=packet[start:]
 if not pes.startswith(b'\0\0\x01') or len(pes)<14 or not pes[7]&0x80:return None
 b=pes[9:14]
 return ((b[0]&14)<<29)|(b[1]<<22)|((b[2]&254)<<14)|(b[3]<<7)|((b[4]&254)>>1)

def descriptor(language,page):
 return b'\x59\x08'+language.encode('ascii')+b'\x10'+struct.pack('>HH',page,page)

def pmt_packet(original,phase,counter):
 start=payload_start(original)
 if start is None or not original[1]&0x40:raise ValueError('Single PMT packet required')
 start+=1+original[start]
 section=original[start:];size=3+(((section[1]&15)<<8)|section[2]);section=section[:size]
 if section[0]!=2 or V.crc32_mpeg(section)!=b'\0\0\0\0':raise ValueError('Invalid initial PMT')
 body=bytearray(section[3:-4]);body[2]=(body[2]&0xc1)|(phase<<1)
 for pid,lang,page in services(phase):
  desc=descriptor(lang,page);body+=struct.pack('>BHH',6,0xe000|pid,0xf000|len(desc))+desc
 result=V.packetize(4096,V.psi(2,bytes(body)),counter)
 if len(result)!=188:raise ValueError('PMT unexpectedly exceeds one packet')
 return result

def services(phase):
 return [(336,'eng',1),(337,'spa',2)] if phase in (0,3) else [(337,'spa',2)] if phase==1 else []

def bitmap(page,spanish):
 # A visible240x2 region, not a tiny twelve-pixel parser-only vector.
 seg=lambda kind,data:V.dvb_segment(kind,data,page)
 field=b'\x10'+b'\x55'*60+b'\0\xf0'
 display=seg(0x14,b'\0'+struct.pack('>HH',719,575))
 comp=seg(0x10,b'\x1e\x04\x01\0'+struct.pack('>HH',100,400))
 region=seg(0x11,bytes((1,8))+struct.pack('>HH',240,2)+bytes((36,0,0,0))+struct.pack('>HHH',1,0,0))
 y,cr,cb=(128,220,60) if spanish else (255,128,128)
 clut=seg(0x12,bytes((0,0,1,0x81,y,cr,cb,0)))
 obj=seg(0x13,struct.pack('>HBHH',1,0,len(field),0)+field)
 return b'\x20\0'+display+comp+region+clut+obj+seg(0x80,b'')+b'\xff'

def combine(data,phase,counters):
 output=bytearray();next_cue=phase*16+1;pmts=0;injected=0
 for offset in range(0,len(data),188):
  packet=data[offset:offset+188];pid=((packet[1]&31)<<8)|packet[2]
  if pid==4096:
   packet=pmt_packet(packet,phase,counters.get(pid,0));counters[pid]=counters.get(pid,0)+1;pmts+=1
  output+=packet
  timestamp=packet_pts(packet) if pid==256 else None
  if timestamp is None or timestamp/90000<next_cue or next_cue>=16*(phase+1):continue
  for target,_,page in services(phase):
   payload=V.packetize(target,V.pes(next_cue*90000,bitmap(page,target==337)),counters.get(target,0))
   counters[target]=counters.get(target,0)+len(payload)//188;output+=payload;injected+=1
  next_cue+=2
 if not pmts:raise ValueError('A/V PMT missing')
 return bytes(output),dict(phase=phase,services=[dict(pid=p,language=l,page=g) for p,l,g in services(phase)],pmtPackets=pmts,subtitlePes=injected)

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--resume-av',action='store_true',help='Reuse only this unfinished generator\'s four independently validated A/V phases')
 options=parser.parse_args()
 if OUTPUT.exists() and not options.resume_av:raise RuntimeError('Canonical fixture already exists; preserve/no overwrite')
 if any(p.is_symlink() or getattr(p,'is_junction',lambda:False)() for p in OUTPUT.parents):raise RuntimeError('Reparse fixture ancestor')
 if options.resume_av:
  if not OUTPUT.is_dir() or OUTPUT.is_symlink() or {p.name for p in OUTPUT.iterdir()}!={'av-phase-'+str(n)+'.ts' for n in range(4)}:raise RuntimeError('Only exact unfinished generated phases may resume')
 else:OUTPUT.mkdir(parents=True)
 commands=[];phases=[];chunks=[];counters={}
 for phase in range(4):
  target=OUTPUT/('av-phase-'+str(phase)+'.ts')
  args=['ffmpeg','-hide_banner','-loglevel','error','-n','-f','lavfi','-i','testsrc2=size=640x360:rate=25:duration=16',
   '-f','lavfi','-i','sine=frequency=440:sample_rate=48000:duration=16','-map','0:v:0','-map','1:a:0',
   '-c:v','mpeg2video','-q:v','5','-g','25','-bf','0','-c:a','ac3','-b:a','192k',
   '-streamid','0:256','-streamid','1:257','-mpegts_flags','+initial_discontinuity','-tables_version',str(phase),
   '-muxdelay','0','-muxpreload','0','-output_ts_offset',str(phase*16),'-f','mpegts',str(target)]
  if options.resume_av:
   if target.is_symlink() or not target.is_file() or not 0<target.stat().st_size<6*1024*1024:raise RuntimeError('Generated phase identity/size changed')
   check=json.loads(run(['ffprobe','-v','error','-show_streams','-of','json',str(target)]))['streams']
   video=next(s for s in check if s.get('codec_type')=='video');audio=next(s for s in check if s.get('codec_type')=='audio')
   if video['codec_name']!='mpeg2video' or video['width']!=640 or video['height']!=360 or video['id']!='0x100' or audio['codec_name']!='ac3' or audio['id']!='0x101' or abs(float(video['start_time'])-phase*16)>.1:raise RuntimeError('Generated A/V phase metadata changed')
  else:run(args)
  commands.append([v.replace(str(OUTPUT),'<fixture>') for v in args])
  data,meta=combine(target.read_bytes(),phase,counters);chunks.append(data);phases.append(meta)
 data=b''.join(chunks)
 if len(data)>24*1024*1024:raise RuntimeError('Unexpected fixture size')
 with (OUTPUT/NAME).open('xb') as f:f.write(data)
 probe=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(OUTPUT/NAME)]))
 manifest=dict(generated=True,originalBroadcast=False,name=NAME,durationSeconds=64,transitionSeconds=[16,32,48],
  bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),phases=phases,probe=probe,commands=commands)
 with (OUTPUT/'fixture.json').open('x',encoding='utf-8') as f:json.dump(manifest,f,indent=2)
 print(json.dumps(dict(generated=True,name=NAME,bytes=len(data),phases=phases,sha256=manifest['sha256'])))

if __name__=='__main__':main()
