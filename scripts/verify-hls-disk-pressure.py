#!/usr/bin/env python3
"""Isolated real192MiB tmpfs guard test; never fills a server/host filesystem.

Reuse the exact local DEV image, read-only project mount, no network/privileges,
bounded CPU/RAM/processes/time. No image build/pull or server connection.
"""
import json,re,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
name='vibe-web102-'+stamp.lower();label='org.opensagetv.vibe.task=WEB-102'
out=ROOT/'artifacts/active/WEB-102';out.mkdir(parents=True,exist_ok=True)
path=out/(stamp+'-isolated-disk-pressure.json')
report=dict(passed=False,serverMutation=False,physicalBrowser=False,network=False,
            privateTmpfsBytes=192*1024*1024,containerName=name)
def docker(*args,timeout=20):
 return subprocess.run(['docker',*args],capture_output=True,text=True,timeout=timeout)
try:
 image=docker('inspect','--format','{{.Image}}','opensagetv-vibe-dev')
 if image.returncode or not re.fullmatch(r'sha256:[a-f0-9]{64}',image.stdout.strip()):raise RuntimeError('Exact reusable local DEV image unavailable')
 if docker('container','inspect',name).returncode==0:raise RuntimeError('Preserve preexisting container')
 image_id=image.stdout.strip();report['devImage']=image_id
 command=['run','--rm','--pull','never','--name',name,'--label',label,
          '--network','none','--user','65534:65534','--read-only','--cap-drop','ALL',
          '--security-opt','no-new-privileges','--cpus','1','--memory','512m','--pids-limit','128',
          '--tmpfs','/scratch:rw,nosuid,nodev,noexec,size=192m',
          '--tmpfs','/tmp:rw,nosuid,nodev,noexec,size=32m',
          '--mount','type=bind,source='+str(ROOT)+',target=/suite,readonly',
          '--entrypoint','/usr/bin/timeout',image_id,'65s','/usr/bin/java',
          '-XX:ActiveProcessorCount=1','-cp','/suite/build/manual/classes:/suite/build/manual/test-classes:/usr/share/java/servlet-api.jar',
          'org.opensagetv.webplayer.HlsDiskPressureSmoke','/scratch']
 result=docker(*command,timeout=75)
 report['exitCode']=result.returncode
 report['stdout']=result.stdout[-8000:];report['stderr']=result.stderr[-4000:]
 if result.returncode:raise RuntimeError('Isolated production-monitor pressure gate failed')
 observation=json.loads(result.stdout.strip().splitlines()[-1])
 report.update(observation=observation,passed=observation.get('passed') is True)
except Exception as failure:report.update(errorType=type(failure).__name__,error=str(failure)[:350])
finally:
 current=docker('container','inspect',name)
 if current.returncode==0:
  data=json.loads(current.stdout)[0]
  if data['Config']['Labels'].get('org.opensagetv.vibe.task')!='WEB-102' or data['Image']!=report.get('devImage'):
   report.update(passed=False,cleanup='Identity mismatch; preserved container')
  else:
   # Only this generated networkless sandbox, never the reusable DEV/server.
   stopped=docker('stop','--time','3',name)
   if stopped.returncode:report.update(passed=False,cleanup='Owned sandbox stop unverified')
 report['ownedSandboxRetired']=docker('container','inspect',name).returncode!=0
 if not report['ownedSandboxRetired']:report['passed']=False
 path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2));print('Report: '+str(path))
raise SystemExit(0 if report['passed'] else 1)
