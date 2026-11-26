#!/usr/bin/env python3
"""Pin every current Android preference and primary playback UI input.

This is a source inventory, not an assertion that browser/platform gates pass.
Only reads the reference repository; never modifies Android or private config.
"""
import argparse, hashlib, json, os
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
ANDROID=Path(os.environ.get('SAGETV_ANDROID_REFERENCE',str(ROOT.parent/'opensagetv-vibe-android-client')))
if not os.environ.get('SAGETV_ANDROID_REFERENCE') and not ANDROID.is_dir() and (ROOT.parent/'android-client').is_dir():
    ANDROID=ROOT.parent/'android-client' # Unified environment's stable bind name.
DEST=ROOT/'docs/parity/CURRENT_ANDROID_INVENTORY.json'
NS='{http://schemas.android.com/apk/res/android}'
GROUPS={
 'transcoding_prefs.xml':('Transcoding','FFmpeg Plugin bridge; per-session copy/transcode, GPU/fallback, source cadence and bitrate/audio choices'),
 'playback_track_prefs.xml':('Subtitles / CC','Independent file/DVD subtitles and virtual CEA/Teletext/DVB slots; language/service preferences'),
 'diagnostics_prefs.xml':('Diagnostics','Redacted reports, stats/current-video test, server destination; Android logcat/filesystem permissions are native-only'),
 'media_mappings_prefs.xml':('Input','Keyboard/D-pad/transport/hold contexts; Android hardware scan codes and gamepad details need browser mappings, not Android API emulation'),
 'touch_mappings_prefs.xml':('Input','Touch gestures, long-press and optional multi-finger/edge mappings; avoid stealing browser/native field input'),
 'smb_profile_prefs.xml':('Profiles and server storage','Profile import/export and administrator-mounted diagnostic destination; browsers cannot speak SMB or receive share credentials'),
 'home_background_prefs.xml':('Lifecycle','Visibility/pagehide/bfcache and Media Session; iOS may suspend background execution and cannot provide an Android foreground service'),
 'disc_playback_prefs.xml':('DVD','Native authored navigation plus H.264/AAC delivery; stock-safe optional capabilities only'),
 'remuxing_prefs.xml':('Transcoding','Explicit Copy through compatible HTTP/MSE/HLS containers, no hidden video re-encode'),
 'codec_container_prefs.xml':('Capabilities','Report actual browser codec support and server conversion; no Android-only capability advertisement'),
 'exoplayer_prefs.xml':('Platform','Browser transport/decoder selection replaces Android engine controls; no Exo/AudioTrack API in HTML5'),
 'media3player_prefs.xml':('Platform','Browser transport/decoder selection replaces Android engine controls; no MediaCodec queue or HDMI passthrough API in HTML5'),
 'ijkplayer_prefs.xml':('Platform','Use supported browser decoding/transcoding; IJK JNI/software decoder settings do not exist in HTML5'),
 'gsyplayer_prefs.xml':('Platform','Browser HTMLMediaElement/native HLS/MSE, not Android GSY delegates'),
 'prefs.xml':('App and connection','Connection, identity, render/viewport, settings, diagnostics and wake/idle policies adapted to a PWA'),
}
def inventory():
    sources=[];preferences=[]
    directory=ANDROID/'source/dev/android-shared/src/main/res/xml'
    for path in sorted(directory.glob('*prefs.xml')):
        data=path.read_bytes();sources.append({'path':str(path.relative_to(ANDROID)).replace('\\','/'),'sha256':hashlib.sha256(data).hexdigest()})
        group,adaptation=GROUPS.get(path.name,('REVIEW_REQUIRED','New preference screen; review before parity claim'))
        for element in ET.fromstring(data).iter():
            key=element.get(NS+'key')
            if key:preferences.append({'screen':path.name,'key':key,'title':element.get(NS+'title',''),'default':element.get(NS+'defaultValue'),'group':group,'adaptation':adaptation,'status':'INVENTORIED_NOT_CERTIFIED'})
    for relative in ('VERSION','source/dev/android-shared/src/main/res/layout/navigation.xml','source/dev/android-shared/src/main/java/opensagetv/vibe/miniclient/android/ActivePlayerAdjustmentsDialog.java','source/dev/core/src/main/java/opensagetv/vibe/miniclient/media/CaptionSlotPolicy.java','source/dev/android-shared/src/main/java/opensagetv/vibe/miniclient/android/preferences/TouchPreferences.java','source/dev/android-shared/src/main/java/opensagetv/vibe/miniclient/android/ui/keymaps/DvdTimeScrollPolicy.java','source/dev/android-shared/src/main/java/opensagetv/vibe/miniclient/android/ui/keymaps/DvdRemoteScanPolicy.java'):
        path=ANDROID/relative;data=path.read_bytes();sources.append({'path':relative,'sha256':hashlib.sha256(data).hexdigest()})
    return {'schemaVersion':1,'task':'WEB-020','reference':'current sibling Android source/dev (including local changes)','androidVersion':(ANDROID/'VERSION').read_text().strip(),'physicalParityClaimed':False,'preferenceCount':len(preferences),'sources':sources,'preferences':preferences}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');parser.add_argument('--require-reference',action='store_true');parser.add_argument('--describe-drift',action='store_true',help='Read-only source/preference delta before explicit regeneration');args=parser.parse_args()
    if args.write and args.describe_drift:parser.error('Review drift and regenerate separately')
    if not (ANDROID/'VERSION').is_file():
        if args.write or args.require_reference or args.describe_drift:raise SystemExit('FAIL: current Android checkout required for source comparison/regeneration')
        # Single-repository CI must not depend on an unpublished/dirty sibling
        # checkout or fetch a different Android HEAD behind the audit's back.
        # Validate its recorded inventory, explicitly NOT live-reference drift.
        import re
        saved=json.loads(DEST.read_text(encoding='utf-8'))
        assert saved['schemaVersion']==1 and saved['physicalParityClaimed'] is False
        assert saved['preferenceCount']==len(saved['preferences']) and saved['preferenceCount']>0
        paths=[]
        for source in saved['sources']:
            path=source['path'];assert not path.startswith('/') and '..' not in Path(path).parts
            assert re.fullmatch('[a-f0-9]{64}',source['sha256']);paths.append(path)
        assert len(paths)==len(set(paths)) and 'VERSION' in paths
        assert all(row.get('screen') and row.get('key') and row.get('group') and row.get('adaptation') for row in saved['preferences'])
        print('PASS recorded Android inventory integrity; LIVE_REFERENCE_UNAVAILABLE (not parity/source-drift certification)')
        raise SystemExit()
    current=inventory();value=json.dumps(current,indent=2,ensure_ascii=False)+'\n'
    if args.describe_drift:
        saved=json.loads(DEST.read_text(encoding='utf-8'))
        before={s['path']:s['sha256'] for s in saved['sources']};after={s['path']:s['sha256'] for s in current['sources']}
        old={(p['screen'],p['key']):p for p in saved['preferences']};new={(p['screen'],p['key']):p for p in current['preferences']}
        print(json.dumps(dict(readOnly=True,oldVersion=saved['androidVersion'],newVersion=current['androidVersion'],
            oldCount=saved['preferenceCount'],newCount=current['preferenceCount'],
            changedSources=[p for p in sorted(set(before)|set(after)) if before.get(p)!=after.get(p)],
            added=[dict(screen=k[0],key=k[1],group=new[k]['group'],adaptation=new[k]['adaptation']) for k in sorted(set(new)-set(old))],
            removed=[dict(screen=k[0],key=k[1]) for k in sorted(set(old)-set(new))],
            changedPreferences=[dict(screen=k[0],key=k[1],fields=[f for f in set(old[k])|set(new[k]) if old[k].get(f)!=new[k].get(f)]) for k in sorted(set(new)&set(old)) if old[k]!=new[k]]),indent=2))
        raise SystemExit()
    if args.write:DEST.write_text(value,encoding='utf-8',newline='\n')
    else:
        if not DEST.is_file() or DEST.read_text(encoding='utf-8')!=value:raise SystemExit('FAIL: current Android feature inventory drift; review and regenerate explicitly')
    print('PASS: current Android input/preference inventory ('+str(json.loads(value)['preferenceCount'])+' entries), no automatic parity claim')
