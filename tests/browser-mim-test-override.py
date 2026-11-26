#!/usr/bin/env python3
"""MCP-ADAPT-TEST-001 / WEB-127: real MIM override through an owned browser.

No simulated policy/responses, global bitrate edits, phone or network shaping.
Only the pre-existing runtime opt-in is checkpointed/restored through MCP CAS.
"""
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import time
from urllib.parse import parse_qs, urlparse
from urllib.error import HTTPError, URLError
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('commission', ROOT/'scripts/commission-mobile.py')
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
cfg = C.configuration()
engine = os.environ.get('SAGETV_BROWSER_ENGINE', 'chromium')
if engine not in ('chromium', 'webkit'):
    raise SystemExit('Supported browser required')
OUT = ROOT/'artifacts/active/WEB-127'
OUT.mkdir(parents=True, exist_ok=True)
identity = 'da92a86446be'
owned = None
handle = None
site_original = None
changed = False
rows = []
receipts = []
passed = False
restored = False
page = None

def mcp(action, **values):
    return C.request(cfg, '/v1/control', dict(action=action, **values), mcp=True)

def api(action):
    return C.request(cfg, '/SageTVWebPlayer/api/miniclient', dict(action=action, session=owned))

def sessions():
    return json.loads(read_only('/v1/control',{'action':'plugin.adaptive_test','plugin_id':'sagetvffmpegpluginlinux','operation':'status'},True)['sessions'])

def read_only(path, values=None, mcp=False):
    # Retry transport failures ONLY on these fixed observational calls. Never
    # replay an override/rate/install/stop mutation after an uncertain response.
    for attempt in range(3):
        try:
            return C.request(cfg,path,values,mcp=mcp,timeout=5)
        except HTTPError:
            raise
        except (URLError, TimeoutError):
            if attempt==2:
                raise
            time.sleep(.25)

def selected():
    return next((s for s in sessions() if s['sessionId'] == handle), None)

def override(target):
    current = selected()
    assert current, 'Owned controller disappeared'
    return mcp('plugin.adaptive_test', plugin_id='sagetvffmpegpluginlinux',
               operation='override' if target else 'clear', session_id=handle,
               expected_revision=current['revision'], target_kbps=target,
               lease_seconds=120 if target else 0, confirm='true')

def wait(predicate, label, seconds=45):
    deadline = time.monotonic()+seconds
    while time.monotonic()<deadline:
        result = predicate()
        if result:
            return result
        page.wait_for_timeout(250)
    raise AssertionError('Timed out: '+label)

def observe(response):
    global owned, handle
    if '/api/miniclient' not in response.url or response.request.method != 'POST':
        return
    action = parse_qs(urlparse(response.url).query).get('action', [''])[0]
    try:
        data = response.json()
        if action == 'start' and data.get('clientId', '').replace(':', '').lower() == identity:
            owned = data['session']
        if action == 'bufferReport' and data.get('testSessionId'):
            # Exact response of this browser, never the first unrelated list row.
            handle = data['testSessionId']
            receipts.append({k:data.get(k) for k in ('reason','reserveMs','targetKbps','samples','testSessionId')})
            del receipts[:-20]
    except Exception:
        pass

def output(producer, target):
    assert re.fullmatch('[a-f0-9]{32}', producer)
    def status():
        return read_only('/SageTVWebPlayer/api/hls?session='+producer)
    initial = int(status().get('segments', 0))-1
    wait(lambda: int(status().get('segments', 0)) >= initial+5, 'fresh output after rate ACK', 20)
    number = int(status()['segments'])-1
    packets = []
    with C.ssh(cfg) as ssh:
        processes = C.remote(ssh, 'docker exec '+shlex.quote(cfg['unraid_container_name'])+' ps -eo pid,lstart,comm,args')
        matches = [line.split()[:6] for line in processes.splitlines()
                   if producer in line and len(line.split())>6 and line.split()[6]=='ffmpeg.real']
        assert len(matches)==1, 'Owned encoder not unique/alive'
        for index in range(number-2, number+1):
            path='/tmp/sagetv-webplayer-hls/'+producer+'/seg_'+str(index).zfill(5)+'.ts'
            command=['docker','exec',cfg['unraid_container_name'],
                     '/opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffprobe',
                     '-v','error','-select_streams','v:0','-show_packets',
                     '-show_entries','packet=pts_time,duration_time,size','-of','json',path]
            packets.extend(json.loads(C.remote(ssh,' '.join(shlex.quote(s) for s in command)))['packets'])
    duration=max(float(p['pts_time'])+float(p.get('duration_time',0)) for p in packets)-min(float(p['pts_time']) for p in packets)
    measured=sum(int(p['size']) for p in packets)*8/1000/duration
    assert duration>2.5 and target*.55 < measured < target*1.55, (target, measured)
    return {'targetKbps':target,'measuredVideoKbps':round(measured,3),'durationSeconds':duration,
            'encoderIdentity':' '.join(matches[0])}

try:
    assert C.activity(cfg).get('safeToRestart') and not mcp('ui.list').get('contexts')
    site_original=mcp('plugin.config_get',plugin_id='sagetvffmpegpluginlinux',setting='stdinctrl.runtime_bitrate_control')['value']
    assert site_original in ('true','false')
    if site_original=='false':
        mcp('plugin.config_set',plugin_id='sagetvffmpegpluginlinux',setting='stdinctrl.runtime_bitrate_control',expected='false',value='true',confirm='true')
        changed=True
    media=mcp('media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/VibeSeekTest-1080i-MPEG2-AC3-CC.ts')
    with sync_playwright() as pw:
        options={'headless':True}
        if engine=='chromium':
            options.update(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
        browser=getattr(pw,engine).launch(**options)
        context=browser.new_context(viewport={'width':1280,'height':800},service_workers='block',
                                   http_credentials={'username':cfg['web_username'],'password':cfg['web_password']})
        page=context.new_page(); page.on('response',observe)
        page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify({player:'hls',videoMode:'transcode',videoKbps:4000,resolution:'720',encoder:'qsv',deinterlace:'off',runtimeBitrateControl:true}));localStorage.setItem('sagetvWebMiniClientSettings.v1',JSON.stringify({adaptiveQuality:true,adaptiveMinimumKbps:1000,maxBufferSeconds:30,mute:true}));")
        page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
        wait(lambda: owned and identity in mcp('ui.list').get('contexts',[]),'owned UI',30)
        wait(lambda:api('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'),'native frame',30)
        print('READY owned native UI',flush=True)
        mcp('media.clear_watched',media_id=media['mediaFileId'],confirm='true')
        mcp('media.watch',context=identity,media_id=media['mediaFileId'],wait_ms=0)
        mcp('media.seek',context=identity,target_ms=0)
        wait(lambda:page.locator('#videoPlane').evaluate('v=>v.videoWidth>0&&v.currentTime>.3&&!v.paused'),'real video',60)
        def eligible():
            current=selected() if handle else None
            return current and current['eligible']
        try:
            wait(eligible,'exact eligible MIM handle')
        except Exception:
            state=api('playbackState')
            print(json.dumps({'controller':selected(),'receipts':receipts,
                              'runtime':state.get('runtimeBitrateControl'),
                              'browser':page.locator('#videoPlane').evaluate('v=>({time:v.currentTime,paused:v.paused,seeking:v.seeking,ready:v.readyState})')}),flush=True)
            raise
        print('READY real video and exact eligible shared controller',flush=True)
        state=api('playbackState'); producer=state['producer']
        assert state['bufferAdaptationRevision']==1
        assert selected()['minimumKbps']==1000 and selected()['maximumKbps']==4000
        checkpoint=selected()['revision']
        for target,revision,confirm in ((500,checkpoint,'true'),(2000,checkpoint+1,'true'),(2000,checkpoint,'false')):
            try:
                mcp('plugin.adaptive_test',plugin_id='sagetvffmpegpluginlinux',operation='override',session_id=handle,
                    expected_revision=revision,target_kbps=target,lease_seconds=120,confirm=confirm)
            except Exception:
                assert selected()['revision']==checkpoint
            else:
                raise AssertionError('Invalid live test control accepted')
        rows.append({'actualRangeRevisionConfirmationRefusal':True})
        previous=output(producer,4000)
        rows.append({'baselineOutput':previous})
        for target in (2000,2500):
            if target>2000:
                # Existing encoder protocol retains its real 15s cooldown and
                # maximum 25% recovery step; test control must not bypass it.
                page.wait_for_timeout(15000)
            override(target)
            wait(lambda:selected()['observedKbps']==target,'observed target '+str(target),20)
            assert api('playbackState')['producer']==producer, 'In-place update replaced stream'
            measured=output(producer,target)
            assert measured['encoderIdentity']==previous['encoderIdentity'], 'Encoder replaced'
            rows.append(measured)
            print(json.dumps({'passedTarget':target,'output':measured}),flush=True)
        override(0)
        assert selected()['overrideKbps']==0
        assert page.locator('#videoPlane').evaluate('v=>v.videoWidth>0&&!v.paused&&v.readyState>=2')
        rows.append({'clear':True,'playbackAdvancing':True,'producerUnchanged':True})
        passed=True
        C.request(cfg,'/SageTVWebPlayer/api/miniclient',{'action':'stop','session':owned})
        owned=None
        context.close();browser.close()
finally:
    cleanup_errors=[]
    try:
        if handle and selected() and selected()['overrideKbps']:
            override(0)
    except Exception as error:
        cleanup_errors.append('clear:'+type(error).__name__)
    try:
        if owned:
            C.request(cfg,'/SageTVWebPlayer/api/miniclient',{'action':'stop','session':owned})
    except Exception as error:
        # Browser shutdown can already have retired the exact owned session.
        # A refused duplicate stop is acceptable ONLY with independent absence.
        try:
            if identity in mcp('ui.list').get('contexts',[]):
                cleanup_errors.append('stop:'+type(error).__name__)
        except Exception:
            cleanup_errors.append('stopUnverified:'+type(error).__name__)
    try:
        if changed:
            mcp('plugin.config_set',plugin_id='sagetvffmpegpluginlinux',setting='stdinctrl.runtime_bitrate_control',expected='true',value=site_original,confirm='true')
        restored=not changed or mcp('plugin.config_get',plugin_id='sagetvffmpegpluginlinux',setting='stdinctrl.runtime_bitrate_control')['value']==site_original
    except Exception as error:
        cleanup_errors.append('siteRestore:'+type(error).__name__)
    finally:
        report={'task':'MCP-ADAPT-TEST-001 / WEB-127','browser':engine,'passed':passed and not cleanup_errors,
                'cleanupErrors':cleanup_errors,
                'restored':restored,'rows':rows,'receipts':receipts,'physicalPhone':False,'stockCoreModified':False}
        path=OUT/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-'+engine+'-mim-override.json')
        path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(report),flush=True)
if not passed or not restored or cleanup_errors:
    raise SystemExit('MIM override gate or cleanup failed')
