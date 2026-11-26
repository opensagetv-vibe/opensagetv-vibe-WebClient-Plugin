#!/usr/bin/env python3
"""Read-only stock commissioning preflight; credentials stay in ignored config.

Uses existing MCP/public web interfaces, never patches Core or installs a WAR
outside the SageTV plugin manager. No private config is included in reports.
"""
import argparse,base64,json,os,tomllib,shlex,hashlib,stat
from pathlib import Path
from urllib.parse import urlencode,urlparse
from urllib.request import Request,urlopen
from urllib.error import HTTPError

ROOT=Path(__file__).resolve().parents[1]

def require_new_war_timestamp(candidate,installed,different):
    if different and tuple(candidate)<=tuple(installed):
        raise RuntimeError('Changed WAR requires a newer SOURCE_DATE_EPOCH; Jetty may reuse old extracted classes')
def configuration():
    android=ROOT.parent/'opensagetv-vibe-android-client'
    if not android.is_dir():android=ROOT.parent/'android-client'
    path=Path(os.environ.get('SAGETV_TEST_CONFIG',str(android/'config/firetv.toml')))
    value=tomllib.loads(path.read_text(encoding='utf-8'))['servers']['vibe']
    if not str(value['address']).endswith('.232'):raise RuntimeError('This task is restricted to the commissioned232 test server')
    web=urlparse(value['web_base_url'])
    if web.hostname!=value['address'] or web.scheme not in ['http','https']:raise RuntimeError('Configured web target mismatch')
    if web.username or web.password:raise RuntimeError('Keep credentials in their separate ignored configuration fields, not the URL')
    return value
def request(cfg,path,values=None,mcp=False,timeout=20):
    base=cfg['core_mcp_base_url'] if mcp else cfg['web_base_url']
    headers={'Accept':'application/json'}
    headers['Authorization']='Bearer '+cfg['core_mcp_token'] if mcp else 'Basic '+base64.b64encode((cfg['web_username']+':'+cfg['web_password']).encode()).decode()
    data=urlencode(values).encode() if values is not None else None
    if data is not None:headers['Content-Type']='application/x-www-form-urlencoded; charset=utf-8'
    try:
        with urlopen(Request(base.rstrip('/')+path,data=data,headers=headers),timeout=timeout) as response:return json.load(response)
    except HTTPError as failure:
        try:detail=json.loads(failure.read(4096)).get('error','Request rejected')
        except Exception:detail='Request rejected'
        raise RuntimeError('HTTP '+str(failure.code)+': '+str(detail)[:500]) from None
def activity(cfg):
    reply=request(cfg,'/v1/control',{'action':'server.activity'},mcp=True)
    if not reply.get('ok'):raise RuntimeError('MCP activity unavailable; not idle proof')
    return reply
def ssh(cfg):
    import paramiko
    client=paramiko.SSHClient();client.load_system_host_keys()
    known=Path.home()/'.ssh/known_hosts'
    if known.is_file():client.load_host_keys(str(known))
    shared_known=ROOT/'config/ssh_known_hosts.local'
    if shared_known.is_symlink():raise RuntimeError('Refuse SSH trust-file symlink')
    if shared_known.is_file():client.load_host_keys(str(shared_known))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect(cfg['unraid_host'],port=int(cfg.get('unraid_ssh_port',22)),username=cfg['unraid_ssh_username'],password=cfg['unraid_ssh_password'],look_for_keys=False,allow_agent=False,timeout=15)
    return client
def remote(client,command):
    _,stdout,stderr=client.exec_command(command,timeout=30);out=stdout.read().decode();error=stderr.read().decode();code=stdout.channel.recv_exit_status()
    if code:raise RuntimeError('Remote diagnostic failed: '+error[:500])
    return out
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['status','caption-sources','verify-stock','media-status','inspect-container','catalog-status','stage','stop-approved-web-session','clear-owned-startup-fixture']);parser.add_argument('--client-id');args=parser.parse_args();cfg=configuration()
    if args.action=='clear-owned-startup-fixture':
        if not activity(cfg).get('safeToRestart'):raise RuntimeError('Fixture cleanup requires independently idle server')
        path='/var/media/OpenSageTV_Vibe_Tests/VibeCaptionTest-1080i-CEA608-90s-2s.ts'
        media=request(cfg,'/v1/control',{'action':'media.resolve_exact_path','path':path},mcp=True)
        if not media.get('mediaFileId'):raise RuntimeError('Canonical fixture unavailable')
        cleared=request(cfg,'/v1/control',{'action':'media.clear_watched','media_id':media['mediaFileId'],'confirm':'true'},mcp=True)
        print(json.dumps({'canonicalFixtureId':media['mediaFileId'],'cleared':cleared.get('ok')},indent=2));raise SystemExit()
    if args.action=='caption-sources':
        with ssh(cfg) as client:
            name=shlex.quote(cfg['unraid_container_name'])
            for filename in ['Breakfast-26711345-0.ts','ClassicHolbyCity-SinsoftheFather-26696712-0.ts','Taskmaster-ThisIsFoodGlue-26714235-0.ts','TheChase-26742651-0.ts']:
                command='docker exec '+name+' /opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffprobe -v error -analyzeduration 2000000 -probesize 4000000 -show_entries stream=index,codec_type,codec_name,id:stream_tags=language -of json '+shlex.quote('/var/media/videos/USER_TEST/'+filename)
                result=json.loads(remote(client,command));print(json.dumps({'fixture':filename,'subtitles':[s for s in result.get('streams',[]) if s.get('codec_type')=='subtitle']}))
        raise SystemExit()
    if args.action=='verify-stock':
        with ssh(cfg) as client:
            name=shlex.quote(cfg['unraid_container_name'])
            checked=remote(client,'docker exec -w /opt/sagetv/server '+name+' sha256sum -c /usr/local/share/sagetv-stock/protected.sha256')
            processes=remote(client,'docker exec '+name+' ps -eo pid,comm')
            encoders=[line.strip() for line in processes.splitlines() if line.split() and line.split()[-1] in ['ffmpeg','ffmpeg.real','SageTVTranscoder','ffmpeg-mim']]
        print(json.dumps({'protectedStockFilesVerified':checked.count(': OK'),'encoderProcesses':encoders,'activity':activity(cfg)},indent=2));raise SystemExit()
    if args.action=='media-status':
        print(json.dumps({'recordings':[{k:v for k,v in row.items() if k in ['id','title','format']} for row in request(cfg,'/SageTVWebPlayer/api/recordings?limit=12').get('recordings',[])]},indent=2))
        with ssh(cfg) as client:
            print(remote(client,'docker exec '+shlex.quote(cfg['unraid_container_name'])+' ls -1 /var/media/OpenSageTV_Vibe_Tests'))
            print(remote(client,'docker exec '+shlex.quote(cfg['unraid_container_name'])+' ls -1 /var/media'))
            print(remote(client,'docker exec '+shlex.quote(cfg['unraid_container_name'])+' ls -1 /var/media/videos/USER_TEST'))
        raise SystemExit()
    if args.action=='catalog-status':
        import xml.etree.ElementTree as ET
        with ssh(cfg) as client:
            data=json.loads(remote(client,'docker inspect '+shlex.quote(cfg['unraid_container_name'])))[0]
            mounts=[m['Source'] for m in data['Mounts'] if m['Destination']=='/opt/sagetv']
            if len(mounts)!=1:raise RuntimeError('Ambiguous appdata')
            with client.open_sftp() as files:
                with files.open(mounts[0]+'/server/Sage.properties','rb') as f:
                    lines=f.read().decode('utf-8',errors='replace').splitlines()
                    dev=[line for line in lines if line.startswith('devmode=')]
                try:
                    with files.open(mounts[0]+'/server/SageTVPluginsDev.xml','rb') as f:root=ET.fromstring(f.read())
                    plugins=[root] if root.tag=='SageTVPlugin' else root.findall('SageTVPlugin')
                    catalog=[{'id':p.findtext('Identifier'),'version':p.findtext('Version')} for p in plugins]
                except FileNotFoundError:catalog=[]
            print(json.dumps({'developerMode':dev,'catalog':catalog,'workingDirectory':data['Config'].get('WorkingDir')},indent=2))
        raise SystemExit()
    if args.action=='inspect-container':
        with ssh(cfg) as client:
            name=shlex.quote(cfg['unraid_container_name'])
            data=json.loads(remote(client,'docker inspect '+name))[0]
            print(json.dumps({'name':data['Name'],'running':data['State']['Running'],'image':data['Config']['Image'],'mounts':[{'source':v['Source'],'destination':v['Destination']} for v in data['Mounts']]},indent=2))
        raise SystemExit()
    if args.action=='stage':
        if not activity(cfg).get('safeToRestart'):raise RuntimeError('Test install requires independently idle server')
        version=(ROOT/'VERSION').read_text().strip();package=ROOT/'dist/local-install/SageTVPluginsDev.d'/('sagetv-webplayer-'+version+'.zip')
        xml=ROOT/'dist/local-install/SageTVPluginsDev.d/sagetv-webplayer.xml'
        import xml.etree.ElementTree as ET
        descriptor=ET.fromstring(xml.read_bytes())
        if descriptor.findtext('Identifier')!='sagetvwebplayer' or descriptor.findtext('Version')!=version:raise RuntimeError('Package identity mismatch')
        md5=hashlib.md5(package.read_bytes()).hexdigest()
        if descriptor.findtext('Package/MD5')!=md5:raise RuntimeError('Package digest mismatch')
        with ssh(cfg) as client:
            name=shlex.quote(cfg['unraid_container_name']);data=json.loads(remote(client,'docker inspect '+name))[0]
            appdata=[m['Source'] for m in data['Mounts'] if m['Destination']=='/opt/sagetv']
            if len(appdata)!=1 or not appdata[0].startswith('/mnt/user/appdata/'):raise RuntimeError('Unrecognized stock appdata mount')
            result=remote(client,'docker exec -w /opt/sagetv/server '+name+' sha256sum -c /usr/local/share/sagetv-stock/protected.sha256')
            target=appdata[0]+'/server/SageTVPluginsDev.d'
            with client.open_sftp() as files:
                parent=files.lstat(appdata[0]+'/server')
                if not stat.S_ISDIR(parent.st_mode):raise RuntimeError('Server appdata must be an ordinary directory')
                import zipfile
                installed_war=appdata[0]+'/server/jetty/webapps/SageTVWebPlayer.war'
                try:installed_info=files.lstat(installed_war)
                except FileNotFoundError:installed_info=None
                if installed_info:
                    if not stat.S_ISREG(installed_info.st_mode):raise RuntimeError('Refuse non-regular installed WAR')
                    with files.open(installed_war,'rb') as stream,zipfile.ZipFile(stream) as archive:
                        installed_stamp=archive.getinfo('miniclient.html').date_time
                    with zipfile.ZipFile(package) as archive:
                        candidate_stamp=archive.getinfo('jetty/webapps/SageTVWebPlayer.war').date_time
                    installed_hash=remote(client,'docker exec '+name+' sha256sum /opt/sagetv/server/jetty/webapps/SageTVWebPlayer.war').split()[0]
                    candidate_hash=hashlib.sha256((ROOT/'dist/SageTVWebPlayer.war').read_bytes()).hexdigest()
                    require_new_war_timestamp(candidate_stamp,installed_stamp,candidate_hash!=installed_hash)
                try:entry=files.lstat(target)
                except FileNotFoundError:files.mkdir(target);entry=files.lstat(target)
                if not stat.S_ISDIR(entry.st_mode):raise RuntimeError('Refuse developer staging through a symlink')
                # This is a developer catalog/package, not a WAR replacement or
                # registry edit. SageTV's manager remains the installer/owner.
                catalog=target+'/vibe-web-mobile.xml'
                for source,destination in [(package,target+'/'+package.name),(xml,catalog)]:
                    try:info=files.lstat(destination)
                    except FileNotFoundError:info=None
                    if info and not stat.S_ISREG(info.st_mode):raise RuntimeError('Refuse non-regular staging destination')
                    files.put(str(source),destination)
                with files.open(target+'/'+package.name,'rb') as f:staged=hashlib.sha256(f.read()).hexdigest()
                if staged!=hashlib.sha256(package.read_bytes()).hexdigest():raise RuntimeError('Staged digest mismatch')
                # Stock devmode=false ignores Dev.d. Its ordinary local catalog
                # is still supported: merge ONLY this plugin's descriptor and
                # leave every unrelated entry intact. This is manager input,
                # not a registry edit, Core patch or direct WAR installation.
                local_catalog=appdata[0]+'/server/SageTVPluginsDev.xml'
                previous=None
                try:
                    entry=files.lstat(local_catalog)
                    if not stat.S_ISREG(entry.st_mode):raise RuntimeError('Refuse non-regular local catalog')
                    with files.open(local_catalog,'rb') as f:previous=f.read()
                except FileNotFoundError:pass
                parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
                root=ET.fromstring(previous,parser=parser) if previous else ET.Element('SageTVPlugins')
                if root.tag=='SageTVPlugin':
                    wrapper=ET.Element('SageTVPlugins');wrapper.append(root);root=wrapper
                if root.tag!='SageTVPlugins':raise RuntimeError('Unrecognized local plugin catalog')
                for old in list(root):
                    if old.tag=='SageTVPlugin' and old.findtext('Identifier')=='sagetvwebplayer':root.remove(old)
                local_plugin=ET.fromstring(xml.read_bytes())
                # Like stock DevRepoSAXHandler, give this DEVELOPMENT catalog
                # entry a monotonically newer snapshot version. Runtime/base
                # version and package digest remain separately reported; this
                # is never a public release or an installed-registry edit.
                import time
                # compareVersions parses EACH dot-separated component as int;
                # one14-digit date would overflow stock Core's parser.
                snapshot_version=version+'.'+time.strftime('%Y%m%d.%H%M%S',time.gmtime())
                local_plugin.find('Version').text=snapshot_version
                local_plugin.find('Package/Location').text='file:///opt/sagetv/server/SageTVPluginsDev.d/'+package.name
                root.append(local_plugin)
                backup=target+'/vibe-web-mobile.catalog-original.bak'
                try:files.lstat(backup)
                except FileNotFoundError:
                    if previous is not None:
                        with files.open(backup,'wb') as f:f.write(previous)
                import uuid
                temporary=target+'/vibe-web-mobile-'+uuid.uuid4().hex+'.tmp'
                with files.open(temporary,'wb') as f:f.write(ET.tostring(root,encoding='utf-8',xml_declaration=True))
                if previous is not None:
                    with files.open(local_catalog,'rb') as f:
                        if f.read()!=previous:raise RuntimeError('Catalog changed during staging; refusing overwrite, staged temporary retained')
                files.posix_rename(temporary,local_catalog)
            print(json.dumps({'runtimeVersion':version,'developmentCatalogVersion':snapshot_version,'packageSha256':staged,'protectedStockFilesVerified':result.count(': OK'),'installation':'PENDING_SAGETV_PLUGIN_MANAGER'},indent=2))
        raise SystemExit()
    if args.action=='stop-approved-web-session':
        # Existing exact-identity MiniClient replacement closes the superseded
        # browser session. No private reflection or unrelated client shutdown.
        import re,time
        if not args.client_id or not re.fullmatch('[0-9a-f]{12}',args.client_id):raise RuntimeError('Exact approved12-hex Web Client required')
        before=activity(cfg);uis=request(cfg,'/v1/control',{'action':'ui.list'},mcp=True)
        if before['recordingCount'] or before['connectedClientCount'] or uis.get('contexts')!=[args.client_id]:raise RuntimeError('Activity changed; refusing takeover')
        created=request(cfg,'/SageTVWebPlayer/api/miniclient',{'action':'start','clientId':args.client_id,'width':1280,'height':720,'stream_captions':'off'})
        try:
            if created.get('clientId','').replace(':','').lower()!=args.client_id or not created.get('session'):raise RuntimeError('Replacement identity mismatch')
        finally:
            if created.get('session'):request(cfg,'/SageTVWebPlayer/api/miniclient',{'action':'stop','session':created['session']})
        time.sleep(2);print(json.dumps({'afterApprovedSessionStop':activity(cfg)},indent=2));raise SystemExit()
    uis=request(cfg,'/v1/control',{'action':'ui.list'},mcp=True)
    states=[request(cfg,'/v1/control',{'action':'ui.state','context':name},mcp=True) for name in uis.get('contexts',[])[:8]]
    print(json.dumps({'webClientUrl':cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html','webHealth':request(cfg,'/SageTVWebPlayer/api/health'),'activity':activity(cfg),'uiStates':states},indent=2))
