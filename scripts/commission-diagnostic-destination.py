#!/usr/bin/env python3
"""Explicit WP14-006 approved stock232 test-only JVM destination commissioning.

Uses the container project's guarded recreation, same pinned stock image and
appdata. Private original environment/inspect remains server-side, never logs.
No Core, plugin registration, recording or installed settings file is edited.
"""
import argparse,hashlib,importlib.util,json,shlex,stat,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('configure','restore'));a=p.parse_args()
helper=ROOT.parent/'opensagetv-vibe-container/scripts/recreate-unraid-test-container.py'
out=ROOT/'artifacts/active/WP14-006';out.mkdir(parents=True,exist_ok=True)
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
report={'action':a.action,'restartSubmitted':False,'passed':False,'stockCoreUnchanged':False}
name=cfg['unraid_container_name'];appdata='/mnt/user/appdata/sagetv-stock-u26-gpu-j11'
backup=appdata+'/.vibe-commissioning/WP14-006';baseline=backup+'/environment-before.private.json'
def idle():
    state=C.activity(cfg)
    if not state.get('safeToRestart') or any(state.get(k)!=0 for k in ('recordingCount','uiContextCount','connectedClientCount')):
        raise RuntimeError('Independent zero recordings/UI/clients required')
    return state
try:
    report['activityBefore']=idle()
    with C.ssh(cfg) as client:
        container=json.loads(C.remote(client,'docker inspect '+shlex.quote(name)))[0]
        if (container['Config'].get('Labels') or {}).get('org.opensagetv.vibe.core.flavor')!='stock':
            raise RuntimeError('Require commissioned stock container')
        if [m['Source'] for m in container['Mounts'] if m['Destination']=='/opt/sagetv']!=[appdata]:
            raise RuntimeError('Appdata identity changed')
        protected=C.remote(client,'docker exec -w /opt/sagetv/server '+shlex.quote(name)+' sha256sum -c /usr/local/share/sagetv-stock/protected.sha256')
        if protected.count(': OK')!=20:raise RuntimeError('Protected stock preflight mismatch')
        commands=C.remote(client,'docker exec '+shlex.quote(name)+' ps -eo comm').splitlines()
        if any(v.strip() in ('ffmpeg','ffmpeg.real','SageTVTranscoder','ffmpeg_MIM') for v in commands):
            raise RuntimeError('Active producer; do not interrupt')
        environment=container['Config'].get('Env',[])
        with client.open_sftp() as files:
            for directory in (appdata,appdata+'/.vibe-commissioning',backup):
                try:entry=files.lstat(directory)
                except FileNotFoundError:files.mkdir(directory,mode=0o700);entry=files.lstat(directory)
                if not stat.S_ISDIR(entry.st_mode):raise RuntimeError('Private backup ancestor not ordinary directory')
            if a.action=='configure':
                status=C.request(cfg,'/SageTVWebPlayer/api/support')
                if status.get('configured') or status.get('writesEnabled') or status.get('spoolFiles')!=0:
                    raise RuntimeError('Preserve existing diagnostic configuration/spool')
                try:files.lstat(baseline)
                except FileNotFoundError:pass
                else:raise RuntimeError('Private original checkpoint already exists; inspect before any repeat')
                try:files.lstat(appdata+'/server/VibeWebDiagnosticTest')
                except FileNotFoundError:pass
                else:raise RuntimeError('Approved test destination already exists; preserve its work')
                original={'environment':environment,'image':container['Image'],'containerId':container['Id']}
                with files.open(baseline,'wx') as stream:stream.write(json.dumps(original))
                files.chmod(baseline,0o600)
                before=dict(v.split('=',1) for v in environment)
                options=before.get('JAVAOPTS','')
                if 'sagetv.webplayer.diagnostics.' in options:raise RuntimeError('Preserve preexisting JVM diagnostic options')
                changed=options+' -Dsagetv.webplayer.diagnostics.dir=/opt/sagetv/server/VibeWebDiagnosticTest -Dsagetv.webplayer.diagnostics.writeEnabled=true'
                desired=[v for v in environment if not v.startswith('JAVAOPTS=')]+['JAVAOPTS='+changed.strip()]
                unset=[]
            else:
                with files.open(baseline,'r') as stream:original=json.load(stream)
                if original['image']!=container['Image']:raise RuntimeError('Image changed since checkpoint')
                desired=original['environment'];unset=[] if any(v.startswith('JAVAOPTS=') for v in desired) else ['JAVAOPTS']
            temporary=C.remote(client,'mktemp /tmp/vibe-wp14-recreate.XXXXXX.py').strip()
            if not temporary.startswith('/tmp/vibe-wp14-recreate.') or '/' in temporary[len('/tmp/'):]:raise RuntimeError('Unexpected temporary helper path')
            try:
                files.put(str(helper),temporary)
                with files.open(temporary,'rb') as stream:remote_hash=hashlib.sha256(stream.read()).hexdigest()
                if remote_hash!=hashlib.sha256(helper.read_bytes()).hexdigest():raise RuntimeError('Guarded helper upload hash mismatch')
                arguments=['python3',temporary,'--container',name,'--image',container['Image'],'--expected-ip','192.168.10.232',
                    '--backup-dir',backup,'--stock-appdata',appdata,'--resume-stock-appdata','--health-timeout','240','--verification-soak-seconds','30']
                for value in desired:arguments+=['--set-env',value]
                for key in unset:arguments+=['--unset-env',key]
                report['activityImmediatelyBefore']=idle()
                report['restartSubmitted']=True
                _,stdout,stderr=client.exec_command(' '.join(shlex.quote(v) for v in arguments),timeout=360)
                output=stdout.read();error=stderr.read();code=stdout.channel.recv_exit_status()
                # Helper output/inspect can contain private Docker configuration.
                # Retain privately on the server, never export it into a report.
                private_log=backup+'/'+stamp+'-'+a.action+'.private.log'
                with files.open(private_log,'wx') as stream:stream.write(output+error)
                files.chmod(private_log,0o600)
                report['guardedHelperExitCode']=code
                if code:raise RuntimeError('Guarded recreation did not pass; private server-side log retained, no retry')
                current=json.loads(C.remote(client,'docker inspect '+shlex.quote(name)))[0]
                actual=dict(v.split('=',1) for v in current['Config'].get('Env',[]))
                expected=dict(v.split('=',1) for v in desired)
                if actual!=expected:raise RuntimeError('Post-recreate environment differs from exact intended values')
                if current['Image']!=original['image']:raise RuntimeError('Unexpected image replacement')
                verified=C.remote(client,'docker exec -w /opt/sagetv/server '+shlex.quote(name)+' sha256sum -c /usr/local/share/sagetv-stock/protected.sha256')
                report.update(passed=verified.count(': OK')==20,stockCoreUnchanged=verified.count(': OK')==20,
                    exactEnvironmentPreserved=True,imageUnchanged=True,privateOriginalCheckpointOnServer=True)
            finally:files.remove(temporary)
except Exception as error:
    report['errorType']=type(error).__name__
    if isinstance(error,RuntimeError):report['error']=str(error)
finally:
    path=out/(stamp+'-'+a.action+'-destination.json');path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':report['passed'],'restartSubmitted':report['restartSubmitted'],'error':report.get('error'),'report':str(path)}))
raise SystemExit(0 if report['passed'] else 1)
