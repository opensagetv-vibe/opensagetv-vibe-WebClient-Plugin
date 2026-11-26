#!/usr/bin/env python3
"""Stage this task's verified MIM dependency for the normal stock plugin manager.

No plugin registry edit, Core replacement or installed binary copy. Preserve
other catalog entries and authoritative INI; compare-and-set catalog update.
"""
import hashlib,importlib.util,json,shlex,stat,uuid,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)

def stage():
    cfg=C.configuration()
    if not C.activity(cfg).get('safeToRestart'):raise RuntimeError('Independent idle server required')
    plugin=ROOT.parent/'opensagetv-vibe-FFmpeg-Plugin'
    runtime=ROOT.parent/'opensagetv-vibe-ffmpeg-mim'
    descriptor=ET.parse(plugin/'output/packages/SageTVFFmpegPluginLinux.xml').getroot()
    if descriptor.findtext('Identifier')!='SageTVFFmpegPluginLinux' or descriptor.findtext('Version')!='0.1.25':raise RuntimeError('Exact dependency candidate required')
    sources={p.name:p for p in (plugin/'output/packages').glob('*.zip')}
    sources['OpenSageTVVibeMIMRuntimeLinux-0.4.13.zip']=runtime/'output/plugin/OpenSageTVVibeMIMRuntimeLinux-0.4.13.zip'
    packages=descriptor.findall('Package')
    if len(packages)!=3:raise RuntimeError('Exact three-package installation contract required')
    selected=[]
    for package in packages:
        name=package.findtext('Location').rsplit('/',1)[-1]
        path=sources.get(name)
        if path is None or not path.is_file() or path.is_symlink() or hashlib.md5(path.read_bytes()).hexdigest()!=package.findtext('MD5'):raise RuntimeError('Verified manager package required')
        selected.append(path)
        package.find('Location').text='file:///opt/sagetv/server/SageTVPluginsDev.d/'+name
    with C.ssh(cfg) as client:
        container=shlex.quote(cfg['unraid_container_name'])
        info=json.loads(C.remote(client,'docker inspect '+container))[0]
        mounts=[m['Source'] for m in info['Mounts'] if m['Destination']=='/opt/sagetv']
        if len(mounts)!=1 or not mounts[0].startswith('/mnt/user/appdata/'):raise RuntimeError('Exact stock appdata mount required')
        protected=C.remote(client,'docker exec -w /opt/sagetv/server '+container+' sha256sum -c /usr/local/share/sagetv-stock/protected.sha256')
        baseline=C.remote(client,'docker exec '+container+' sha256sum /opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffmpeg.real.ini /opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffmpeg.real /opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffprobe')
        target=mounts[0]+'/server/SageTVPluginsDev.d';catalog=mounts[0]+'/server/SageTVPluginsDev.xml'
        with client.open_sftp() as ftp:
            for parent in (mounts[0],mounts[0]+'/server',target):
                if not stat.S_ISDIR(ftp.lstat(parent).st_mode):raise RuntimeError('Ordinary manager staging directory required')
            for path in selected:
                destination=target+'/'+path.name
                try:entry=ftp.lstat(destination)
                except FileNotFoundError:entry=None
                if entry is not None:raise RuntimeError('Preserve existing staged candidate; do not overwrite/replay')
                ftp.put(str(path),destination)
                if not stat.S_ISREG(ftp.lstat(destination).st_mode):raise RuntimeError('Staged package not regular')
                with ftp.open(destination,'rb') as f:digest=hashlib.sha256(f.read()).hexdigest()
                if digest!=hashlib.sha256(path.read_bytes()).hexdigest():raise RuntimeError('Staged package hash mismatch')
            if not stat.S_ISREG(ftp.lstat(catalog).st_mode):raise RuntimeError('Ordinary existing catalog required')
            with ftp.open(catalog,'rb') as f:previous=f.read()
            root=ET.fromstring(previous,parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))
            if root.tag!='SageTVPlugins':raise RuntimeError('Preserve unknown catalog format')
            for old in list(root):
                if old.tag=='SageTVPlugin' and old.findtext('Identifier')=='SageTVFFmpegPluginLinux':root.remove(old)
            root.append(descriptor)
            backup=target+'/vibe-stdin-001.catalog-original.bak'
            try:ftp.lstat(backup)
            except FileNotFoundError:
                with ftp.open(backup,'wb') as f:f.write(previous)
            temporary=target+'/vibe-stdin-001-'+uuid.uuid4().hex+'.tmp'
            with ftp.open(temporary,'wb') as f:f.write(ET.tostring(root,encoding='utf-8',xml_declaration=True))
            with ftp.open(catalog,'rb') as f:
                if f.read()!=previous:raise RuntimeError('Concurrent catalog change; preserve pending file')
            ftp.posix_rename(temporary,catalog)
    report=dict(pluginVersion='0.1.25',mimVersion='0.4.13',packages=3,hashesVerified=True,
        protectedStockFiles=protected.count(': OK'),beforeIniAndEngines=baseline.splitlines(),installation='PENDING_NORMAL_PLUGIN_MANAGER')
    out=ROOT/'artifacts/results/WP08-006/MIM_DEPENDENCY_STAGE.json';out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
    print(json.dumps(dict(pluginVersion='0.1.25',mimVersion='0.4.13',packages=3,protectedStockFiles=report['protectedStockFiles'],installation=report['installation'])))
if __name__=='__main__':stage()
