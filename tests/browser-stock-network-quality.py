#!/usr/bin/env python3
"""WEB-127 real bounded media-body delivery, shared MIM buffer-only policy.

Only this owned browser's generated HLS segment requests pass a local paced
forwarder. No server/network configuration, policy class or clock is patched.
"""
import base64,importlib.util,json,os,re,shlex,threading,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs,urlparse
from urllib.request import Request,urlopen
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
inplace=os.environ.get('SAGETV_INPLACE_TEST')=='1'
task='WEB-127'
OUT=Path(os.environ.get('SAGETV_ARTIFACT_DIR',ROOT/'artifacts/active'/task)).resolve()
if OUT!=(ROOT/'artifacts/active'/task).resolve():raise SystemExit('Use '+task+' active output')
OUT.mkdir(parents=True,exist_ok=True)
engine=os.environ.get('SAGETV_BROWSER_ENGINE','chromium')
if engine not in ('chromium','webkit'):raise SystemExit('Unsupported browser')
player=os.environ.get('SAGETV_HLS_PLAYER','hls')
if player not in ('hls','native') or player=='native' and engine!='webkit':raise SystemExit('Native-HLS row requires host WebKit')
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());identity='da92a86446be'
owned=None;page=None;browser=None;context=None;passed=False;rows=[];errors=[];transfers=[];changes=[];samples=[];reports=[]
site_original=None;site_changed=False;initial_contexts=[];skip_reason=None;native_supported=None
profile=os.environ.get('SAGETV_NETWORK_CASE','adaptive')
if profile not in ('adaptive','default-off','healthy','transient','native-baseline'):raise SystemExit('Unsupported case')
if profile=='native-baseline' and player!='native':raise SystemExit('Native baseline requires actual native decoder')
initial_rate=int(os.environ.get('SAGETV_BODY_LIMIT_KBPS','1000' if profile=='default-off' else '8000'))
if not 250<=initial_rate<=10000:raise SystemExit('Unsupported bounded body limit')
stop=threading.Event();pace={'kbps':initial_rate};segments=re.compile(r'^/SageTVWebPlayer/hls/[a-f0-9]{32}/seg_[0-9]{5,}\.ts$')
auth='Basic '+base64.b64encode((cfg['web_username']+':'+cfg['web_password']).encode()).decode()

class BodyDelivery(BaseHTTPRequestHandler):
    protocol_version='HTTP/1.1'
    def log_message(self,*args):pass
    def do_GET(self):
        path=urlparse(self.path).path
        if not segments.fullmatch(path) or self.headers.get('X-Vibe-Test-Owner')!=stamp:
            self.send_error(404);return
        began=time.monotonic();sent=0;rate=pace['kbps']
        try:
            with urlopen(Request(cfg['web_base_url'].rstrip('/')+path,headers={'Authorization':auth}),timeout=10) as upstream:
                size=int(upstream.headers['Content-Length'])
                if not 0<size<=8*1024*1024:raise ValueError('Unexpected segment size')
                self.send_response(200);self.send_header('Content-Type','video/mp2t')
                self.send_header('Content-Length',str(size));self.send_header('Cache-Control','no-store')
                self.send_header('Access-Control-Allow-Origin','*');self.end_headers()
                # First byte is immediate; body pacing is deliberately AFTER
                # it so production hls.js excludes encoder/header wait itself.
                first=upstream.read(1);self.wfile.write(first);self.wfile.flush();sent=len(first)
                clock=time.monotonic()
                while not stop.is_set():
                    data=upstream.read(4096)
                    if not data:break
                    if stop.wait(max(0,(sent+len(data))*8/(rate*1000)-(time.monotonic()-clock))):break
                    self.wfile.write(data);self.wfile.flush();sent+=len(data)
                transfers.append({'bytes':sent,'bodyMs':round((time.monotonic()-clock)*1000,1),'limitKbps':rate,'complete':sent==size})
                if profile=='transient' and rate==1000:pace['kbps']=8000
        except (BrokenPipeError,ConnectionResetError):pass
        except Exception as error:
            errors.append('forwarder:'+type(error).__name__)
            self.close_connection=True

server=ThreadingHTTPServer(('127.0.0.1',0),BodyDelivery);server.daemon_threads=True
threading.Thread(target=server.serve_forever,daemon=True).start()
def mcp(action,**values):return C.request(cfg,'/v1/control',dict(action=action,**values),mcp=True)
def api(action,**values):return C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action=action,session=owned,**values))

def encoded_sample(producer_id,target):
    """Independent completed video packets and actual GPU-process witness."""
    if not re.fullmatch('[a-f0-9]{32}',producer_id):raise AssertionError('Invalid owned producer')
    status=C.request(cfg,'/SageTVWebPlayer/api/hls?session='+producer_id)
    initial_number=int(status.get('segments',0))-1
    if initial_number<0:raise AssertionError('No published segment')
    # A command ACK and progress do not ensure the latest completed segment
    # contains only the new rate. Measure three fresh full segments, excluding
    # the boundary segment, instead of accepting a one-second transient.
    deadline=time.monotonic()+15
    while time.monotonic()<deadline:
        number=int(C.request(cfg,'/SageTVWebPlayer/api/hls?session='+producer_id).get('segments',0))-1
        if number>=initial_number+4:break
        page.wait_for_timeout(200)
    else:raise AssertionError('No fresh completed output measurement window')
    with C.ssh(cfg) as ssh:
        commands=C.remote(ssh,'docker exec '+shlex.quote(cfg['unraid_container_name'])+' ps -eo pid,lstart,comm,args')
        matches=[line.split()[:6] for line in commands.splitlines() if producer_id in line and 'ffmpeg.real' in line and line.split()[6]=='ffmpeg.real']
        if len(matches)!=1:raise AssertionError('Actual encoder process is not unique/alive')
        witness=' '.join(matches[0]);pid=matches[0][0]
        # The container root lacks CAP_SYS_PTRACE for Java's uid99 children.
        # Read as the commissioned SageTV uid, not via a privileged container
        # or a proc-glob readlink whose transient closed fd makes exit1.
        fds=C.remote(ssh,'docker exec -u 99:100 '+shlex.quote(cfg['unraid_container_name'])+' find /proc/'+pid+'/fd -maxdepth 1 -type l -lname '+shlex.quote('/dev/dri/*')+' -printf '+shlex.quote('%l\n'))
        if '/dev/dri/renderD128' not in fds:raise AssertionError('Actual encoder lacks GPU render device')
        packets=[]
        for index in range(number-2,number+1):
            path='/tmp/sagetv-webplayer-hls/'+producer_id+'/seg_'+str(index).zfill(5)+'.ts'
            command=['docker','exec',cfg['unraid_container_name'],'/opt/sagetv/server/plugins/SageTVFFmpegPlugin/runtime/ffprobe',
                '-v','error','-select_streams','v:0','-show_packets','-show_streams','-show_entries','packet=pts_time,dts_time,duration_time,size:stream=codec_name,width,height','-of','json',path]
            data=json.loads(C.remote(ssh,' '.join(shlex.quote(s) for s in command)))
            packets.extend(data['packets'])
    times=[float(v['pts_time']) for v in packets];dts=[float(v['dts_time']) for v in packets]
    duration=max(float(v['pts_time'])+float(v.get('duration_time',0)) for v in packets)-min(times)
    kbps=sum(int(v['size']) for v in packets)*8/1000/duration
    if not duration>2.5 or not all(b>a for a,b in zip(dts,dts[1:])):raise AssertionError('Bad segment clock')
    if not target*.55<kbps<target*1.55:raise AssertionError('Output packets do not follow target: '+str(round(kbps,2))+' vs '+str(target))
    return {'targetKbps':target,'measuredVideoKbps':round(kbps,3),'seconds':round(duration,6),'packets':len(packets),
        'encoderPidStart':witness,'gpuRenderDevice':True,'streams':data['streams']}
def observe(response):
    global owned
    if '/api/miniclient' not in response.url:return
    action=parse_qs(urlparse(response.url).query).get('action',[''])[0]
    if action not in ('start','qualityPrepare','runtimeRate','bufferReport'):return
    try:
        data=response.json()
        if action=='start' and data.get('clientId','').replace(':','').lower()==identity:owned=data['session']
        if action=='qualityPrepare':changes.append(data)
        if inplace and action=='runtimeRate' and response.request.method=='POST':changes.append(data)
        if action=='bufferReport':
            reports.append({k:data.get(k) for k in ('reportId','reason','reserveMs','targetKbps','samples','attempts','minimumKbps','maximumKbps')})
            del reports[:-100]
    except Exception:pass
def waiting(predicate,label,seconds):
    deadline=time.monotonic()+seconds;next_sample=0
    while time.monotonic()<deadline:
        if predicate():return
        if label.startswith('automatic') and time.monotonic()>=next_sample:
            page.locator('#videoInfoBtn').evaluate('el=>el.click()')
            snapshot=json.loads(page.locator('#videoInfoText').text_content())['playback']
            sample={k:snapshot.get(k) for k in ('timeMs','paused','rebuffering','starting','firstFrameMs','ahead','network','error')}
            sample['videoPaused']=page.locator('#videoPlane').evaluate('v=>v.paused')
            sample['qualityText']=page.locator('#qualityRecommendation').text_content()
            samples.append(sample);print(json.dumps({'observed':sample}),flush=True)
            page.locator('#closeVideoInfo').evaluate('el=>el.click()')
            next_sample=time.monotonic()+10
        page.wait_for_timeout(250)
    raise AssertionError('Timed out: '+label+'; transfers='+str(len(transfers))+'; changes='+str(len(changes)))
try:
    activity=C.activity(cfg)
    initial_contexts=mcp('ui.list').get('contexts',[])
    assert activity.get('recordingCount')==0 and identity not in initial_contexts,activity
    # Handoff tests own only this new UI/media delivery. Preserve unrelated
    # viewers. In-place opt-in is a site mutation and still requires full idle.
    if inplace:assert activity.get('safeToRestart') is True and not initial_contexts,activity
    if inplace:
        if profile!='adaptive':raise RuntimeError('In-place gate currently requires adaptive profile')
        site_original=mcp('plugin.config_get',plugin_id='sagetvffmpegpluginlinux',setting='stdinctrl.runtime_bitrate_control')['value']
        if site_original not in ('true','false'):raise RuntimeError('Unknown site opt-in')
        if site_original=='false':
            changed=mcp('plugin.config_set',plugin_id='sagetvffmpegpluginlinux',setting='stdinctrl.runtime_bitrate_control',expected='false',value='true',confirm='true')
            assert changed.get('value')=='true';site_changed=True
    media=mcp('media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/VibeSeekTest-1080i-MPEG2-AC3-CC.ts')
    assert media.get('mediaFileId')
    with sync_playwright() as pw:
        browser=(pw.webkit.launch(headless=True) if engine=='webkit' else pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox']))
        context=browser.new_context(viewport={'width':852,'height':393},service_workers='block',http_credentials={'username':cfg['web_username'],'password':cfg['web_password']})
        page=context.new_page();page.on('response',observe);page.on('pageerror',lambda e:errors.append('page:'+str(e)))
        native_supported=page.evaluate("()=>!!document.createElement('video').canPlayType('application/vnd.apple.mpegurl')")
        if player=='native' and not native_supported:
            skip_reason='host-webkit-native-hls-unavailable'
            print('SKIPPED native HLS: actual host WebKit capability is unavailable; not a Safari PASS',flush=True)
            raise SystemExit(77)
        def route_segment(route):
            path=urlparse(route.request.url).path
            if not owned or not segments.fullmatch(path):route.abort();return
            headers={k:v for k,v in route.request.headers.items() if k.lower() not in ('authorization','host')}
            headers['X-Vibe-Test-Owner']=stamp
            route.continue_(url='http://127.0.0.1:'+str(server.server_port)+path,headers=headers)
        page.route('**/hls/*/seg_*.ts',route_segment)
        streaming={'player':player,'videoMode':'transcode','videoKbps':4000,'resolution':'720','deinterlace':'on'}
        if inplace:streaming.update(encoder='qsv',deinterlace='off',runtimeBitrateControl=True)
        page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebCaptionAuthority.v1',JSON.stringify({mode:'cc1',cc1Type:'cea608',cc1Language:'eng',cc1Service:1}));localStorage.setItem('sagetvWebStreaming.v1',"+json.dumps(json.dumps(streaming))+");")
        settings={'maxBufferSeconds':30}
        settings['adaptiveMinimumKbps']=1000
        if profile not in ('default-off','native-baseline'):settings['adaptiveQuality']=True
        page.add_init_script('localStorage.setItem("sagetvWebMiniClientSettings.v1",'+json.dumps(json.dumps(settings))+');')
        page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
        waiting(lambda:owned is not None and identity in mcp('ui.list').get('contexts',[]),'owned native registration',30)
        waiting(lambda:api('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'),'first native frame',30)
        saved=page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')")
        mcp('media.clear_watched',media_id=media['mediaFileId'],confirm='true')
        mcp('media.watch',context=identity,media_id=media['mediaFileId'],wait_ms=0)
        mcp('media.seek',context=identity,target_ms=0)
        deadline=time.monotonic()+45;clicked=False
        while time.monotonic()<deadline:
            state=page.locator('#videoPlane').evaluate('v=>({time:v.currentTime,width:v.videoWidth,paused:v.paused})')
            if state['width'] and state['time']>.3 and not state['paused']:break
            if page.locator('#autoplayBtn').is_visible() and not clicked:
                page.locator('#autoplayBtn').click();clicked=True
            page.wait_for_timeout(100)
        else:raise AssertionError('Actual video did not start: '+json.dumps(state))
        if player=='native':
            assert page.locator('#videoPlane').evaluate("v=>!!v.canPlayType('application/vnd.apple.mpegurl')&&!v.currentSrc.startsWith('blob:')&&v.currentSrc.includes('.m3u8')"),'Native-HLS selected but actual decoder is not native'
        if profile=='native-baseline':
            first=page.locator('#videoPlane').evaluate('v=>v.currentTime')
            page.wait_for_timeout(12000)
            last=page.locator('#videoPlane').evaluate('v=>({time:v.currentTime,ready:v.readyState,paused:v.paused,buffered:v.buffered.length,error:v.error&&v.error.code})')
            rows.append({'gate':'native-with-adjustment-disabled-unconstrained-progress','firstSeconds':first,'last':last,'passed':last['time']-first>=8})
            assert last['time']-first>=8,rows[-1]
            passed=True;raise SystemExit(0)
        print('READY actual paced video; shared MIM buffer-only policy, no target injection',flush=True)
        if inplace:
            initial=api('playbackState');producer_id=initial['producer']
            waiting(lambda:api('playbackState').get('runtimeBitrateControl',{}).get('available') is True,'runtime controller ready',15)
            source=page.locator('#videoPlane').evaluate('v=>v.currentSrc')
            initial_sample=encoded_sample(producer_id,4000)
            waiting(lambda:len(reports)>=2,'healthy shared-controller reports',15)
            assert not changes,changes
            pace['kbps']=1000
            print('SHAPED actual HLS body delivery 1000kbps',flush=True)
            def applied_change():
                state=api('playbackState');rate=state.get('runtimeBitrateControl') or {}
                if state.get('producer')!=producer_id:raise AssertionError('In-place control replaced producer')
                return rate if rate.get('state')=='applied' and rate.get('appliedKbps',4000)<4000 else None
            waiting(lambda:len(changes)>=1 and applied_change(),'automatic in-place downshift',100)
            reduced=applied_change();assert reduced and reduced.get('sameProcess') is True
            pace['kbps']=8000
            down_sample=encoded_sample(producer_id,reduced['appliedKbps'])
            assert down_sample['encoderPidStart']==initial_sample['encoderPidStart']
            assert page.locator('#videoPlane').evaluate('v=>v.currentSrc')==source
            rows.append({'gate':'buffer-only-automatic-inplace-downshift','passed':True,'rate':reduced,'producerUnchanged':True,'policyUnmodified':True,'baselineOutput':initial_sample,'output':down_sample})
            print('PASS actual automatic same-producer downshift '+str(reduced['appliedKbps']),flush=True)
            pace['kbps']=8000
            def recovered():
                state=api('playbackState');rate=state.get('runtimeBitrateControl') or {}
                if state.get('producer')!=producer_id:raise AssertionError('Recovery replaced producer')
                return rate if rate.get('state')=='applied' and reduced['appliedKbps']<rate.get('appliedKbps',0)<=4000 else None
            waiting(lambda:len(changes)>=2 and recovered(),'automatic in-place recovery',120)
            raised=recovered();assert raised and raised.get('sameProcess') is True
            up_sample=encoded_sample(producer_id,raised['appliedKbps'])
            assert up_sample['encoderPidStart']==initial_sample['encoderPidStart']
            assert up_sample['measuredVideoKbps']>down_sample['measuredVideoKbps']*1.03,'Measured recovery must rise, not merely fit a broad target tolerance'
            first=page.locator('#videoPlane').evaluate('v=>({time:v.currentTime,frames:v.getVideoPlaybackQuality().totalVideoFrames})')
            page.wait_for_timeout(3000)
            last=page.locator('#videoPlane').evaluate('v=>({time:v.currentTime,frames:v.getVideoPlaybackQuality().totalVideoFrames})')
            assert last['time']>first['time'] and last['frames']>first['frames']
            assert page.locator('#videoPlane').evaluate('v=>v.currentSrc')==source
            assert page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')")==saved
            rows.append({'gate':'buffer-only-automatic-inplace-recovery','passed':True,'rate':raised,'producerUnchanged':True,'newFrames':last['frames']-first['frames'],'policyUnmodified':True,'savedProfileUnchanged':True,'output':up_sample})
            print('PASS actual automatic same-producer recovery '+str(raised['appliedKbps']),flush=True)
            passed=True;raise SystemExit(0)
        if profile!='adaptive':
            if profile=='transient':
                pace['kbps']=1000
                waiting(lambda:any(r['complete'] and r['limitKbps']==1000 for r in transfers),'automatic transient-body completion observation',25)
            else:
                waiting(lambda:sum(r['complete'] and r['bytes']>=16384 and r['bodyMs']>=100 for r in transfers)>=4,'automatic negative measured samples observation',35)
            # No injected recommendation, early policy reset or cooldown skip.
            # Observe normal playback for longer than three3s policy samples.
            for _ in range(12):
                page.wait_for_timeout(1000);assert not changes,'Unexpected quality mutation in '+profile
            active=api('streamSettings');actual=C.request(cfg,'/SageTVWebPlayer/api/hls?session='+active['session'])
            assert actual['streamSettings']['effective']['videoTargetKbps']==4000
            assert page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')")==saved
            rows.append({'gate':'buffer-only-'+profile+'-does-not-change-quality','passed':True,'effectiveKbps':4000,'policyUnmodified':True,'defaultOff':profile=='default-off','actualCompleteTransfers':len([r for r in transfers if r['complete']]),'savedProfileUnchanged':True})
            print('PASS buffer-only '+profile+' keeps original quality/settings',flush=True)
            passed=True
            raise SystemExit(0)
        waiting(lambda:len(reports)>=2,'healthy shared-controller reports',15)
        assert not changes,changes
        pace['kbps']=1000
        waiting(lambda:len(changes)>=1,'automatic buffer-only downshift',100)
        reduction=changes[0];assert reduction.get('session'),reduction
        waiting(lambda:api('playbackState').get('producer')==reduction['session'] and api('playbackState').get('qualityHandoff')=='presented','actual downshift presentation',30)
        reduced=C.request(cfg,'/SageTVWebPlayer/api/hls?session='+reduction['session'])
        assert reduced['streamSettings']['effective']['videoTargetKbps']<4000
        assert all(reduced.get(k) for k in ('hardware','hardwareDecode','hardwareFilters')),reduced.get('encoder')
        measured=[r for r in transfers if r['complete'] and r['bytes']>=16384 and r['bodyMs']>=100]
        assert len(measured)>=3,measured
        assert page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')")==saved
        rows.append({'gate':'actual-buffer-only-automatic-downshift','passed':True,'effectiveKbps':reduced['streamSettings']['effective']['videoTargetKbps'],'bodyLimitKbps':1000,'completeMeasuredTransfers':len(measured),'policyUnmodified':True,'actualPresentedAck':True,'fullGpu':True,'savedProfileUnchanged':True})
        print('PASS real body-limited automatic downshift and actual presentation',flush=True)
        # Keep finite positive transfer time (not synthetic sample injection)
        # to qualify recovery headroom after the actual production cooldown.
        pace['kbps']=8000
        waiting(lambda:len(changes)>=2,'automatic buffer-only recovery after cooldown',120)
        recovery=changes[1]
        waiting(lambda:api('playbackState').get('producer')==recovery.get('session') and api('playbackState').get('qualityHandoff')=='presented','actual recovery presentation',30)
        raised=C.request(cfg,'/SageTVWebPlayer/api/hls?session='+recovery['session'])
        if player=='native':
            assert page.locator('#videoPlane').evaluate("v=>!v.currentSrc.startsWith('blob:')&&v.currentSrc.includes('.m3u8')"),'Native-HLS recovery fell back to MSE'
        assert reduced['streamSettings']['effective']['videoTargetKbps']<raised['streamSettings']['effective']['videoTargetKbps']<=4000
        assert all(raised.get(k) for k in ('hardware','hardwareDecode','hardwareFilters'))
        assert page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')")==saved
        rows.append({'gate':'actual-buffer-only-automatic-recovery','passed':True,'effectiveKbps':raised['streamSettings']['effective']['videoTargetKbps'],'bodyLimitKbps':8000,'policyUnmodified':True,'actualPresentedAck':True,'fullGpu':True,'savedProfileUnchanged':True})
        page.screenshot(path=str(OUT/(stamp+'-'+engine+'-buffer-quality.png')))
        print('PASS real buffer-only automatic recovery inside saved ceiling',flush=True)
        passed=True
finally:
    stop.set()
    if owned:
        try:api('stop')
        except Exception:pass
    if context:
        try:context.close()
        except Exception:pass
    if browser:
        try:browser.close()
        except Exception:pass
    server.shutdown();server.server_close()
    if site_changed:
        restored=mcp('plugin.config_set',plugin_id='sagetvffmpegpluginlinux',setting='stdinctrl.runtime_bitrate_control',expected='true',value=site_original,confirm='true')
        if restored.get('value')!=site_original:raise RuntimeError('Original site opt-in not restored')
    deadline=time.monotonic()+90
    while True:
        try:
            final=C.activity(cfg)
            if identity not in mcp('ui.list').get('contexts',[]):break
        except Exception:final=None
        if time.monotonic()>=deadline:passed=False;break
        time.sleep(.5)
    (OUT/(stamp+'-'+engine+'-'+player+'-'+('inplace-' if inplace else '')+profile+'-buffer-quality.json')).write_text(json.dumps({'passed':passed,'skipReason':skip_reason,'nativeHlsSupported':native_supported,'profile':profile,'player':player,'inPlace':inplace,'stockServer':'.232','engine':engine,'physicalPhone':False,'measuredPhysicalWan':False,'method':'shared-mim-buffer-only','reports':reports,'rows':rows,'transfers':transfers[-200:],'samples':samples,'errors':errors,'initialOtherContexts':initial_contexts,'finalActivity':final},indent=2)+'\n')
    if not final or identity in mcp('ui.list').get('contexts',[]):raise RuntimeError('Independent owned-UI retirement unavailable')
