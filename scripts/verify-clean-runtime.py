#!/usr/bin/env python3
"""Build only explicit runtime/test inputs in a Git-less DEV temp directory.

Never captures configuration, credentials, appdata or host Git metadata. Retire
the exact owned source archive recoverably and remove only the matched mktemp
DEV directory; no server connection, installation or publication.
"""
import argparse,hashlib,json,re,subprocess,time,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];WORKSPACE=ROOT.parents[1]
# Run from the real workspace host; the DEV alias /workspace/web-client-plugin
# has no projects/ parent and would incorrectly stage into container /. The
# helper itself invokes DEV for compilation, including Git-less verification.
if ROOT.parent.name!='projects' or not (WORKSPACE/'AGENTS.md').is_file():
 raise SystemExit('Run this staging orchestrator from the native workspace host, not its DEV alias')
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--task',choices=('WEB-095','WEB-096','WEB-097','WEB-099','WEB-100','WEB-101','WEB-104','WEB-108','WEB-112','WEB-113','WEB-116','WEB-117','WP15-001'),required=True);args=p.parse_args()
tag=args.task.lower().replace('-','');temp_pattern='/tmp/vibe-'+tag+'-clean[.][A-Za-z0-9]{6}'
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
relative=Path('artifacts/temp')/(stamp+'-'+args.task+'-clean-runtime.zip')
archive=WORKSPACE/relative;retired=WORKSPACE/'deleteme'/relative
output=ROOT/'artifacts/active'/args.task/(stamp+'-clean-runtime.json')
required=['VERSION','release.properties','BUILD_INFO.json','scripts/build-local.sh',
 'scripts/package-local-plugin.py','scripts/verify-mobile-package.py','tests/test-build-info.py',
 'tests/test-caption-service-loss.js','tests/test-teletext-controller.js','tests/test-dvb-controller.js',
 'tests/test-miniclient-playback.js','tests/test-miniclient-core.js',
 'tests/PmtServiceRetirementSmoke.java','tests/parity/fixtures/teletext-188.ts','tests/parity/fixtures/dvb-2bpp.ts']
if args.task=='WEB-099':required+=['tests/HardwarePipelineSmoke.java']
if args.task=='WEB-104':required+=['tests/HlsControlProfileSmoke.java','tests/HardwarePipelineSmoke.java']
if args.task=='WP15-001':required+=['tests/P15StockContractsSmoke.java','tests/MiniClientProtocolSmoke.java','tests/CompanionDvdSmoke.java','tests/P12AudioPolicySmoke.java','tests/DvdNativeProtocolSmoke.java']
if args.task=='WEB-108':required+=['tests/StockDvdReconfigureSmoke.java','tests/StockClientPlaybackSmoke.java','tests/StockClientInfoSmoke.java']
if args.task in ('WEB-112','WEB-113','WEB-117'):required+=['tests/test-vibe-input.js']
if args.task in ('WEB-100','WEB-101'):required+=[
 'tests/DvbTransitionFixtureSmoke.java','tests/DvbPmtTimingSmoke.java',
 'artifacts/test-media/VIBE_CAPTION_PMT/VibeCaptions-English-Spanish-PMT.ts',
 'artifacts/test-media/VIBE_CAPTION_PMT/fixture.json']
if args.task=='WEB-097':required+=['tests/OwnedProcessControlSmoke.java','tests/HlsProcessStopSmoke.java','tests/OwnedProcessCapabilityAbsentSmoke.java','scripts/prepare-process-control-tests.sh']
paths=sorted(set([p.relative_to(ROOT).as_posix() for p in (ROOT/'src').rglob('*') if p.is_file()]+required))
def guard(path):
 if not path.resolve().is_relative_to(WORKSPACE.resolve()):raise RuntimeError('Outside workspace')
 for parent in [path,*path.parents]:
  if parent==WORKSPACE:break
  if parent.is_symlink() or getattr(parent,'is_junction',lambda:False)():raise RuntimeError('Reparse staging rejected')
def docker(*args,timeout=180):
 value=subprocess.run(['docker',*args],capture_output=True,text=True,timeout=timeout)
 if value.returncode:raise RuntimeError('DEV command failed; '+value.stdout[-1800:]+'\n'+value.stderr[-1800:])
 return value.stdout
report={'passed':False,'serverMutation':False,'gitMetadataPresent':False,'inputs':len(paths)};temporary=None
try:
 for path in [archive,retired,output]:
  guard(path)
  if path.exists():raise RuntimeError('Preserve preexisting staging/result')
 archive.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as bundle:
  for name in paths:
   source=ROOT/name;guard(source)
   if not source.is_file():raise RuntimeError('Required clean input missing')
   bundle.write(source,name)
  if args.task=='WEB-097':
   provider=ROOT.parent/'opensagetv-vibe-FFmpeg-Plugin/output/packages/SageTVFFmpegPlugin.jar';guard(provider)
   if not provider.is_file():raise RuntimeError('Required built provider JAR absent')
   # This test dependency is never copied into the application WAR.
   bundle.write(provider,'test-dependencies/SageTVFFmpegPlugin.jar')
   report['providerJarSha256']=hashlib.sha256(provider.read_bytes()).hexdigest()
 report['archiveSha256']=hashlib.sha256(archive.read_bytes()).hexdigest()
 temporary=docker('exec','opensagetv-vibe-dev','mktemp','-d','/tmp/vibe-'+tag+'-clean.XXXXXX').strip()
 if not re.fullmatch(temp_pattern,temporary):raise RuntimeError('Unexpected DEV temp target')
 docker('cp',str(archive),'opensagetv-vibe-dev:'+temporary+'/input.zip')
 program='''import hashlib,json,sys,zipfile,subprocess
from pathlib import Path
base=Path(sys.argv[1]);source=base/'source';source.mkdir()
with zipfile.ZipFile(base/'input.zip') as z:
 for n in z.namelist():
  if not (source/n).resolve().is_relative_to(source.resolve()):raise RuntimeError('Archive path rejected')
 z.extractall(source)
assert not (source/'.git').exists()
commands=[['bash','scripts/build-local.sh'],['python3','scripts/package-local-plugin.py'],
 ['python3','scripts/verify-mobile-package.py'],['python3','tests/test-build-info.py','--exact-artifacts'],
 ['node','tests/test-caption-service-loss.js'],['node','tests/test-teletext-controller.js'],['node','tests/test-dvb-controller.js'],
 ['node','tests/test-miniclient-playback.js'],
 ['javac','--release','8','-cp','build/manual/classes','-d','build/manual/test-classes','tests/PmtServiceRetirementSmoke.java'],
 ['java','-cp','build/manual/classes:build/manual/test-classes','org.opensagetv.webplayer.PmtServiceRetirementSmoke']]
for command in commands:subprocess.run(command,cwd=source,check=True)
print(json.dumps({'warSha256':hashlib.sha256((source/'dist/SageTVWebPlayer.war').read_bytes()).hexdigest(),'commands':len(commands)}))
'''
 if args.task in ('WEB-112','WEB-113','WEB-117'):
  program=program.replace("for command in commands:subprocess.run(command,cwd=source,check=True)","""commands=commands[:4]+[['node','tests/test-vibe-input.js'],['node','--check','src/main/webapp/sw.js'],['node','--check','src/main/webapp/js/miniclient.js']]
for command in commands:subprocess.run(command,cwd=source,check=True)""")
 if args.task=='WEB-116':
  program=program.replace("for command in commands:subprocess.run(command,cwd=source,check=True)","""commands=commands[:4]+[['node','tests/test-miniclient-playback.js'],['node','--check','src/main/webapp/sw.js']]
for command in commands:subprocess.run(command,cwd=source,check=True)""")
 if args.task=='WP15-001':
  program=program.replace("for command in commands:subprocess.run(command,cwd=source,check=True)","""commands=commands[:4]
for test in ['P15StockContractsSmoke','MiniClientProtocolSmoke','CompanionDvdSmoke','P12AudioPolicySmoke','DvdNativeProtocolSmoke']:
 commands += [['javac','--release','8','-cp','build/manual/classes:/usr/share/java/servlet-api.jar','-d','build/manual/test-classes','tests/'+test+'.java'],
 ['java','-cp','build/manual/classes:build/manual/test-classes:/usr/share/java/servlet-api.jar','org.opensagetv.webplayer.'+test]]
for command in commands:subprocess.run(command,cwd=source,check=True)""")
 if args.task=='WEB-099':
  program=program.replace("for command in commands:subprocess.run(command,cwd=source,check=True)","""commands=commands[:4]+[['node','tests/test-miniclient-playback.js'],
 ['javac','--release','8','-cp','build/manual/classes','-d','build/manual/test-classes','tests/HardwarePipelineSmoke.java'],
 ['java','-cp','build/manual/classes:build/manual/test-classes','org.opensagetv.webplayer.HardwarePipelineSmoke']]
for command in commands:subprocess.run(command,cwd=source,check=True)""")
 if args.task=='WEB-108':
  program=program.replace("for command in commands:subprocess.run(command,cwd=source,check=True)","""commands=commands[:4]+[['node','--check','src/main/webapp/js/miniclient.js']]
for test in ['StockDvdReconfigureSmoke','StockClientPlaybackSmoke','StockClientInfoSmoke']:
 commands += [['javac','--release','8','-cp','build/manual/classes','-d','build/manual/test-classes','tests/'+test+'.java'],
 ['java','-cp','build/manual/classes:build/manual/test-classes','org.opensagetv.webplayer.'+test]]
for command in commands:subprocess.run(command,cwd=source,check=True)""")
 if args.task=='WEB-104':
  program=program.replace("for command in commands:subprocess.run(command,cwd=source,check=True)","""commands=commands[:4]
for test in ['HlsControlProfileSmoke','HardwarePipelineSmoke']:
 commands += [['javac','--release','8','-cp','build/manual/classes:/usr/share/java/servlet-api.jar','-d','build/manual/test-classes','tests/'+test+'.java'],
 ['java','-cp','build/manual/classes:build/manual/test-classes:/usr/share/java/servlet-api.jar','org.opensagetv.webplayer.'+test]]
for command in commands:subprocess.run(command,cwd=source,check=True)""")
 if args.task in ('WEB-100','WEB-101'):
  program=program.replace("for command in commands:subprocess.run(command,cwd=source,check=True)","""commands += [
 ['javac','--release','8','-cp','build/manual/classes','-d','build/manual/test-classes','tests/DvbTransitionFixtureSmoke.java','tests/DvbPmtTimingSmoke.java'],
 ['java','-cp','build/manual/classes:build/manual/test-classes','org.opensagetv.webplayer.DvbTransitionFixtureSmoke'],
 ['java','-cp','build/manual/classes:build/manual/test-classes','org.opensagetv.webplayer.DvbPmtTimingSmoke']]
for command in commands:subprocess.run(command,cwd=source,check=True)""")
 if args.task=='WEB-097':
  program=program.replace("for command in commands:subprocess.run(command,cwd=source,check=True)","""commands=commands[:4]+[['node','tests/test-miniclient-playback.js'],
 ['javac','--release','8','-cp','build/manual/classes','-d','build/manual/absent-provider','tests/OwnedProcessCapabilityAbsentSmoke.java'],
 ['java','-cp','build/manual/classes:build/manual/absent-provider','org.opensagetv.webplayer.OwnedProcessCapabilityAbsentSmoke'],
 ['bash','-c','SAGETV_FFMPEG_PLUGIN_JAR=test-dependencies/SageTVFFmpegPlugin.jar bash scripts/prepare-process-control-tests.sh']]
for test in ['OwnedProcessControlSmoke','HlsProcessStopSmoke']:
 commands += [['javac','--release','8','-cp','build/manual/classes:build/manual/test-classes','-d','build/manual/test-classes','tests/'+test+'.java'],
 ['java','-cp','build/manual/classes:build/manual/test-classes','org.opensagetv.webplayer.'+test]]
for command in commands:subprocess.run(command,cwd=source,check=True)""")
 transcript=docker('exec','opensagetv-vibe-dev','/opt/opensagetv-vibe/web-python/bin/python3','-c',program,temporary)
 result=json.loads(transcript.strip().splitlines()[-1])
 expected=hashlib.sha256((ROOT/'dist/SageTVWebPlayer.war').read_bytes()).hexdigest()
 if result['warSha256']!=expected:raise RuntimeError('Git-less build differs from commissioned WAR')
 report.update(result,passed=True,exactCommissionedWar=True,affectedTests='playback92/hardware-command40/package72+216/metadata3' if args.task=='WEB-099' else 'playback87/service16/TT5/DVB3/PMT4/package72+216/metadata3')
 if args.task=='WEB-097':report['affectedTests']='playback92/shared-provider-absent/blocked-duplex/retained-owner/admission/package+metadata'
 if args.task in ('WEB-100','WEB-101'):report['affectedTests']='playback/service18/TT5/DVB3/PMT4/generated-real-decoder4/timed-PMT/Java8-package+metadata'
 if args.task=='WEB-104':report['affectedTests']='public-HLS-profile12/hardware-command46/Java8-package+metadata'
 if args.task=='WEB-108':report['affectedTests']='stock-DVD-profile/native-clock/paused-intent/ownership/unknown-receipt/public-Watch-Info/Java8-package+metadata'
 if args.task=='WEB-112':report['affectedTests']='portable-input18groups/defaults/context/repeat/touch/DVD/cancellation/Java8-package+metadata'
 if args.task=='WEB-113':report['affectedTests']='portable-input21groups/DVD-Time-Scroll/batch-ownership/source-retirement/Java8-package+metadata'
 if args.task=='WEB-116':report['affectedTests']='playback99/passive-element-bounded-ranges/unavailable-APIs/no-media-URL/no-playback-mutation/Java8-package+metadata'
 if args.task=='WEB-117':report['affectedTests']='portable-input23/current-DVD-OSD-stale-preview-bounds/native-viewport-popup-stale-menu-negative/Java8-package+metadata'
 if args.task=='WP15-001':report['affectedTests']='stock-extension-contract17/real-TCP-GET-SET/companion11/audio-rate8/DVD-native-protocol/Java8-package+metadata'
except Exception as error:report.update(errorType=type(error).__name__,error=str(error)[:4000])
finally:
 if temporary and re.fullmatch(temp_pattern,temporary):
  try:
   resolved=docker('exec','opensagetv-vibe-dev','realpath','--',temporary).strip()
   if resolved!=temporary:raise RuntimeError('DEV staging resolved differently')
   docker('exec','opensagetv-vibe-dev','rm','-r','--',temporary)
   report['ownedDevTempRemoved']=True
  except Exception:report.update(passed=False,ownedDevTempRemovalUnverified=True)
 if archive.is_file():
  try:
   guard(archive);guard(retired)
   if retired.exists():raise RuntimeError('Preserve existing retirement target')
   digest=hashlib.sha256(archive.read_bytes()).hexdigest()
   retired.parent.mkdir(parents=True,exist_ok=True);archive.rename(retired)
   if hashlib.sha256(retired.read_bytes()).hexdigest()!=digest:raise RuntimeError('Retirement hash mismatch')
   report.update(archiveRetiredRecoverably=True,retiredRelativePath=str(Path('deleteme')/relative),archiveBytes=retired.stat().st_size)
  except Exception:report.update(passed=False,archiveRetirementUnverified=True)
 output.parent.mkdir(parents=True,exist_ok=True)
 with output.open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2)
print(json.dumps(report));raise SystemExit(0 if report['passed'] else 1)
