#!/usr/bin/env python3
"""Canonical synthetic PMT/layout transition; no server or user-media writes.

Run with the existing dev-container FFmpeg. English AC-3 PID257 changes from
mono to5.1 at16s; PMT version increments and a distinct1320Hz NAR PID258 appears.
English remains440Hz. Initial discontinuity is signalled, PTS stays continuous.
This is generated transport evidence, not an original broadcast/receiver test.
"""
import hashlib, importlib.util, json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT/'artifacts/test-media/VIBE_AUDIO_PMT'
NAME = 'VibeAudio-PMT-Mono-to-51.ts'


def run(args):
    result = subprocess.run(args, capture_output=True, timeout=90)
    if result.returncode:
        raise RuntimeError('Fixture tool failed: '+result.stderr.decode('utf-8', 'replace')[-1600:])
    return result.stdout


def inspect_tables(data):
    spec = importlib.util.spec_from_file_location('vectors', ROOT/'scripts/parity/generate_fixtures.py')
    vectors = importlib.util.module_from_spec(spec); spec.loader.exec_module(vectors)
    rows = {}
    if len(data) % 188: raise RuntimeError('Invalid transport packet size')
    for offset in range(0, len(data), 188):
        packet = data[offset:offset+188]
        if packet[0] != 0x47: raise RuntimeError('Lost transport sync')
        pid = ((packet[1] & 31) << 8) | packet[2]
        if pid != 4096 or not packet[1] & 0x40: continue
        if not packet[3] & 0x10: continue
        start = 4 + (1+packet[4] if packet[3] & 0x20 else 0)
        start += 1+packet[start]
        section = packet[start:]
        size = 3+(((section[1] & 15) << 8) | section[2]); section = section[:size]
        if len(section) != size or vectors.crc32_mpeg(section) != b'\0\0\0\0':
            raise RuntimeError('PMT must fit one packet and have a valid CRC')
        version = (section[5] >> 1) & 31
        cursor = 12+(((section[10] & 15) << 8) | section[11]); streams = []
        while cursor < len(section)-4:
            kind = section[cursor]; stream_pid = ((section[cursor+1] & 31) << 8) | section[cursor+2]
            length = ((section[cursor+3] & 15) << 8) | section[cursor+4]
            descriptors = section[cursor+5:cursor+5+length]
            streams.append(dict(pid=stream_pid, type=kind, descriptors=descriptors.hex()))
            cursor += 5+length
        old = rows.setdefault(version, dict(firstByte=offset, lastByte=offset, occurrences=0, streams=streams))
        if old['streams'] != streams: raise RuntimeError('Changed PMT without version increment')
        old['lastByte'] = offset; old['occurrences'] += 1
    if sorted(rows) != [0, 1]: raise RuntimeError('Both PMT versions required')
    if [s['pid'] for s in rows[0]['streams']] != [256, 257] or [s['pid'] for s in rows[1]['streams']] != [256, 257, 258]:
        raise RuntimeError('Primary/late stream PID changed')
    if rows[0]['lastByte'] >= rows[1]['firstByte']: raise RuntimeError('PMT order invalid')
    return rows


def main():
    if OUTPUT.exists(): raise RuntimeError('Exact canonical fixture already exists; no overwrite/replay')
    if any(p.is_symlink() for p in OUTPUT.parents): raise RuntimeError('Fixture ancestor symlink rejected')
    OUTPUT.mkdir(parents=True)
    commands = []
    phases = []
    for phase in range(2):
        target = OUTPUT/('phase-'+str(phase)+'.ts')
        audio = 'sine=frequency=440:sample_rate=48000:duration=16' if not phase else (
            'aevalsrc='+ '|'.join(['0.08*sin(2*PI*440*t)']*6)+':s=48000:d=16:c=5.1')
        command = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n',
            '-f', 'lavfi', '-i', 'testsrc2=size=320x180:rate=25:duration=16',
            '-f', 'lavfi', '-i', audio]
        if phase: command += ['-f', 'lavfi', '-i', 'sine=frequency=1320:sample_rate=48000:duration=16']
        command += ['-map', '0:v:0', '-map', '1:a:0']
        if phase: command += ['-map', '2:a:0']
        command += ['-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p', '-g', '25', '-bf', '0',
            '-c:a:0', 'ac3', '-b:a:0', '384k', '-metadata:s:a:0', 'language=eng',
            '-streamid', '0:256', '-streamid', '1:257']
        if phase: command += ['-c:a:1', 'aac', '-b:a:1', '96k', '-metadata:s:a:1', 'language=nar', '-streamid', '2:258']
        command += ['-mpegts_flags', '+initial_discontinuity', '-tables_version', str(phase),
            '-muxdelay', '0', '-muxpreload', '0', '-output_ts_offset', str(16*phase), '-f', 'mpegts', str(target)]
        run(command); commands.append(command)
        probe = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(target)]))
        audios = [s for s in probe['streams'] if s['codec_type'] == 'audio']
        if audios[0]['id'] != '0x101' or audios[0]['channels'] != (6 if phase else 1) or audios[0].get('tags', {}).get('language') != 'eng':
            raise RuntimeError('Source primary audio identity/layout mismatch')
        if phase and (len(audios) != 2 or audios[1]['id'] != '0x102' or audios[1].get('tags', {}).get('language') != 'nar'):
            raise RuntimeError('Late NAR audio missing')
        phases.append(dict(file=target.name, bytes=target.stat().st_size, sha256=hashlib.sha256(target.read_bytes()).hexdigest(), probe=probe))
    combined = b''.join((OUTPUT/p['file']).read_bytes() for p in phases)
    tables = inspect_tables(combined)
    if len(combined) > 12*1024*1024: raise RuntimeError('Unexpected fixture size')
    with (OUTPUT/NAME).open('xb') as file: file.write(combined)
    manifest = dict(generated=True, originalBroadcast=False, name=NAME, transitionSeconds=16,
        durationSeconds=32, primaryPid=257, primaryLanguage='eng', primaryToneHz=440,
        initialChannels=1, finalChannels=6, latePid=258, lateLanguage='nar', lateToneHz=1320,
        sha256=hashlib.sha256(combined).hexdigest(), bytes=len(combined), pmt=tables,
        ffmpegVersion=run(['ffmpeg', '-version']).decode().splitlines()[0], phases=phases,
        commands=[[str(x).replace(str(OUTPUT), '<fixture>') for x in c] for c in commands])
    with (OUTPUT/'fixture.json').open('x', encoding='utf-8') as file: json.dump(manifest, file, indent=2)
    print(json.dumps(dict(generated=True, output=str(OUTPUT), bytes=len(combined), sha256=manifest['sha256'], pmtVersions=list(tables))))


if __name__ == '__main__': main()
