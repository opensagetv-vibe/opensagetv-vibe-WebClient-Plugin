#!/usr/bin/env python3
"""Stage reviewed shared dependencies for stock232's NORMAL plugin manager.

Never writes installed JARs, registry properties, Core or runtime files.
The fixed component catalog is input to SageTV, not an alternate installer.
"""
import argparse
import hashlib
import io
import importlib.util
import json
import posixpath
import re
import shlex
import stat
import uuid
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)

def component(name):
    projects=ROOT.parent
    if name=='ffmpeg':
        owner=projects/'opensagetv-vibe-FFmpeg-Plugin'
        version=(owner/'VERSION').read_text().strip()
        descriptor=owner/'output/packages/SageTVFFmpegPluginLinux.xml'
        identifier='SageTVFFmpegPluginLinux'
        runtime_project=projects/'opensagetv-vibe-ffmpeg-mim'
        runtime=runtime_project/'output/plugin'
        properties=dict(line.split('=',1) for line in (runtime_project/'release.properties').read_text(encoding='utf-8').splitlines() if '=' in line)
        mim_version=properties['VERSION']
        if not re.fullmatch(r'\d+\.\d+\.\d+',mim_version):raise ValueError('Invalid runtime version')
        files={f'SageTVFFmpegPlugin-jar-{version}.zip':owner/f'output/packages/SageTVFFmpegPlugin-jar-{version}.zip',
               f'SageTVFFmpegPlugin-system-linux-{version}.zip':owner/f'output/packages/SageTVFFmpegPlugin-system-linux-{version}.zip',
               f'OpenSageTVVibeMIMRuntimeLinux-{mim_version}.zip':runtime/f'OpenSageTVVibeMIMRuntimeLinux-{mim_version}.zip'}
    elif name=='client-extension':
        owner=projects/'opensagetv-vibe-client-extension-Plugin'
        version=(owner/'VERSION').read_text().strip()
        descriptor=owner/'output/packages/VibeClientExtensionPlugin-dev.xml'
        identifier='OpenSageTVVibeClientExtensionPlugin'
        filename=f'VibeClientExtensionPlugin-jar-{version}.zip'
        files={filename:owner/'output/packages'/filename}
    elif name=='core-mcp':
        owner=projects/'opensagetv-vibe-core-MCP-Plugin'
        if not owner.is_dir():owner=projects/'core-mcp-plugin'
        version=dict(line.split('=',1) for line in (owner/'release.properties').read_text().splitlines() if '=' in line)['VERSION']
        descriptor=owner/'output/packages/OpenSageTVVibeCoreMCPPlugin-dev.xml'
        identifier='OpenSageTVVibeCoreMCPPlugin'
        filename=f'OpenSageTVVibeCoreMCPPlugin-jar-{version}.zip'
        files={filename:owner/'output/packages'/filename}
    elif name=='sagemc':
        owner=projects/'opensagetv-vibe-sagemc-Plugin'
        version=(owner/'VERSION').read_text().strip()
        descriptor=owner/'output/opensagetv-vibe-sagemc.xml'
        identifier='opensagetv-vibe-sagemc'
        files={f'OpenSageTV-Vibe-SageMC-v{version}-{kind}.zip':owner/f'output/OpenSageTV-Vibe-SageMC-v{version}-{kind}.zip' for kind in ('plugin','defaults')}
    else:raise ValueError('Unreviewed component')
    node=ET.fromstring(descriptor.read_bytes())
    if node.findtext('Identifier')!=identifier or node.findtext('Version')!=version or node.findtext('PluginType')!=('STV' if name=='sagemc' else 'Standard'):
        raise ValueError('Component identity/type/version mismatch')
    packages=node.findall('Package')
    if len(packages)!=len(files):raise ValueError('Unexpected dependency package count')
    used=set();digests={}
    for package in packages:
        filename=posixpath.basename(urlparse(package.findtext('Location','')).path)
        if filename not in files or filename in used:raise ValueError('Unreviewed/duplicate package')
        used.add(filename);source=files[filename]
        if not source.resolve().is_relative_to(projects.resolve()):raise ValueError('Package outside active projects')
        data=source.read_bytes()
        if hashlib.md5(data).hexdigest()!=package.findtext('MD5'):raise ValueError('Package MD5 mismatch: '+filename)
        digests[filename]=hashlib.sha256(data).hexdigest()
        with zipfile.ZipFile(source) as archive:
            seen=set()
            kind=package.findtext('PackageType')
            jar={'ffmpeg':'SageTVFFmpegPlugin.jar','client-extension':'VibeClientExtensionPlugin.jar','core-mcp':'OpenSageTVVibeCoreMCPPlugin.jar'}.get(name)
            # This narrowly reviewed dependency update may change only the STV
            # call names and its first-party presentation adapter. Theme/vendor
            # files/defaults must remain byte-identical to the installed baseline.
            baseline=None
            if name=='sagemc':
                suffix='defaults' if filename.endswith('-defaults.zip') else 'plugin'
                baseline=zipfile.ZipFile(owner/f'output/OpenSageTV-Vibe-SageMC-v0.1.0-{suffix}.zip')
                if set(archive.namelist())!=set(baseline.namelist()):raise ValueError('SageMC package inventory changed')
            for entry in archive.infolist():
                path=entry.filename
                if path in seen or '\\' in path or path.startswith('/') or '..' in path.split('/') or ':' in path:
                    raise ValueError('Unsafe/duplicate ZIP member')
                seen.add(path)
                mode=(entry.external_attr>>16)&0xffff
                if stat.S_ISLNK(mode):raise ValueError('Symlink in package')
                if name=='sagemc':
                    if kind!='System':raise ValueError('Unexpected SageMC package type')
                    if path not in ('STVs/SageTV3/SageMC_Vibe.xml','JARs/OpenSageTVVibeSageMcTmdbAdapter.jar') and archive.read(entry)!=baseline.read(path):
                        raise ValueError('Unreviewed SageMC dependency change: '+path)
                    if path=='STVs/SageTV3/SageMC_Vibe.xml' and archive.read(entry)!=(owner/'source/dev/SageMC_169.xml').read_bytes():raise ValueError('Stale SageMC graph')
                    if path=='JARs/OpenSageTVVibeSageMcTmdbAdapter.jar':
                        with zipfile.ZipFile(io.BytesIO(archive.read(entry))) as nested:
                            if any(not p.startswith(('META-INF/','org/opensagetv/vibe/sagemc/tmdb/')) for p in nested.namelist()):raise ValueError('Unreviewed adapter classes')
                elif kind=='JAR':
                    # SageTV's JAR package type installs this root member in
                    # JARs itself. Never fabricate a server-relative JAR path.
                    if path!=jar:raise ValueError('Unexpected JAR package member')
                    with zipfile.ZipFile(io.BytesIO(archive.read(entry))) as nested:
                        if any(p.startswith('sage/') for p in nested.namelist()):
                            raise ValueError('Plugin must not shadow stock sage classes')
                elif kind=='System' and path=='SageTVTranscoder' and name=='ffmpeg':
                    if archive.read(entry)!=archive.read('plugins/SageTVFFmpegPlugin/launcher/SageTVTranscoder'):
                        raise ValueError('Plugin-owned launcher copies differ')
                elif kind!='System' or not path.startswith('plugins/SageTVFFmpegPlugin/'):
                    raise ValueError('Package would touch non-plugin install paths: '+path)
        package.find('Location').text='file:///opt/sagetv/server/SageTVPluginsDev.d/'+filename
    return identifier,version,node,files,digests

def regular(files,path,directory=False,missing=False):
    try:entry=files.lstat(path)
    except FileNotFoundError:
        if missing:return False
        raise
    if not (stat.S_ISDIR(entry.st_mode) if directory else stat.S_ISREG(entry.st_mode)):
        raise ValueError('Refuse non-ordinary staging path: '+path)
    return True

def stage(name,owned_ui=None):
    identifier,version,node,packages,digests=component(name)
    cfg=C.configuration()
    activity=C.activity(cfg)
    if not activity.get('safeToRestart'):
        # Staging is manager INPUT, not an installation/restart. Permit only
        # this explicitly commissioned gate's sole idle manager UI, so the
        # operator can refresh the catalog before its normal update action.
        if owned_ui!='da92a86446be' or activity.get('recordingCount')!=0 or activity.get('connectedClientCount')!=0 or activity.get('uiContextCount')!=1:
            raise RuntimeError('Shared staging requires independently idle232 or its exact owned manager UI')
        contexts=C.request(cfg,'/v1/control',{'action':'ui.list'},mcp=True).get('contexts')
        if contexts!=[owned_ui]:raise RuntimeError('Manager UI ownership changed')
    with C.ssh(cfg) as client:
        container=shlex.quote(cfg['unraid_container_name'])
        stock=C.remote(client,'docker exec -w /opt/sagetv/server '+container+' sha256sum -c /usr/local/share/sagetv-stock/protected.sha256')
        details=json.loads(C.remote(client,'docker inspect '+container))[0]
        mounts=[m['Source'] for m in details['Mounts'] if m['Destination']=='/opt/sagetv']
        if len(mounts)!=1 or not mounts[0].startswith('/mnt/user/appdata/') or posixpath.normpath(mounts[0])!=mounts[0]:
            raise RuntimeError('Unrecognized appdata mount')
        server=mounts[0]+'/server';target=server+'/SageTVPluginsDev.d'
        with client.open_sftp() as files:
            # Refuse link traversal through every appdata/staging component.
            current=''
            for part in server.strip('/').split('/'):
                current+='/'+part;regular(files,current,directory=True)
            if not regular(files,target,directory=True,missing=True):files.mkdir(target)
            for filename,source in packages.items():
                destination=target+'/'+filename
                regular(files,destination,missing=True)
                files.put(str(source),destination)
                with files.open(destination,'rb') as stream:
                    digest=hashlib.file_digest(stream,'sha256').hexdigest()
                if digest!=digests[filename]:raise RuntimeError('Staged package SHA256 mismatch')
            catalog=server+'/SageTVPluginsDev.xml';previous=None
            if regular(files,catalog,missing=True):
                with files.open(catalog,'rb') as stream:previous=stream.read()
            parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
            root=ET.fromstring(previous,parser=parser) if previous else ET.Element('SageTVPlugins')
            if root.tag=='SageTVPlugin':
                wrapper=ET.Element('SageTVPlugins');wrapper.append(root);root=wrapper
            if root.tag!='SageTVPlugins':raise RuntimeError('Unrecognized plugin catalog')
            for old in list(root):
                if old.tag=='SageTVPlugin' and old.findtext('Identifier')==identifier:root.remove(old)
            root.append(node)
            backup=target+'/vibe-shared-'+name+'.catalog-original.bak'
            if not regular(files,backup,missing=True) and previous is not None:
                with files.open(backup,'wb') as stream:stream.write(previous)
            temporary=target+'/vibe-shared-'+uuid.uuid4().hex+'.tmp'
            with files.open(temporary,'wb') as stream:stream.write(ET.tostring(root,encoding='utf-8',xml_declaration=True))
            if previous is not None:
                with files.open(catalog,'rb') as stream:
                    if stream.read()!=previous:raise RuntimeError('Catalog changed; refusing overwrite; exact staged temporary: '+temporary)
            elif regular(files,catalog,missing=True):raise RuntimeError('Catalog appeared during staging')
            files.posix_rename(temporary,catalog)
    return {'component':name,'id':identifier,'version':version,'packagesSha256':digests,
            'protectedStockFilesVerified':stock.count(': OK'),'installation':'PENDING_NORMAL_SAGETV_PLUGIN_MANAGER'}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('component',choices=['ffmpeg','client-extension','core-mcp','sagemc'])
    parser.add_argument('--verify-only',action='store_true')
    parser.add_argument('--owned-ui',choices=['da92a86446be'])
    args=parser.parse_args()
    if args.verify_only:
        identifier,version,_,_,digests=component(args.component)
        result={'id':identifier,'version':version,'packagesSha256':digests,'serverTouched':False}
    else:result=stage(args.component,args.owned_ui)
    print(json.dumps(result,indent=2))
