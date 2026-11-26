#!/usr/bin/env python3
"""WEB-043: opt-in real stock232/WebKit startup, not physical iPhone evidence.

Canonical fixture and one absent owned identity only. Production assets/settings
are unchanged; every run owns its browser storage and native session. Other UIs
are never sent controls. Measurements are observations, not hard speed gates.
"""
import importlib.util,json,os,time,re,shlex,base64
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
if os.environ.get('SAGETV_ALLOW_STOCK_STARTUP')!='1':
    raise SystemExit('Explicit SAGETV_ALLOW_STOCK_STARTUP=1 required')
OUT=Path(os.environ['SAGETV_ARTIFACT_DIR']).resolve()
if OUT not in [(ROOT/'artifacts/active'/task).resolve() for task in ('WEB-043','WEB-044')]:raise SystemExit('Use the exact owned startup artifact directory')
OUT.mkdir(parents=True,exist_ok=True)
cfg=C.configuration();identity='da92a86446be'
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
if os.environ.get('SAGETV_STARTUP_PROBE_STAMP'):
    stamp=os.environ['SAGETV_STARTUP_PROBE_STAMP']
    if not re.fullmatch('[0-9]{8}T[0-9]{4,6}Z',stamp):raise SystemExit('Invalid probe stamp')
def mcp(action,**values):return C.request(cfg,'/v1/control',dict(action=action,**values),mcp=True)
def retire_owned_fixture_ui():
    """One bounded exact-identity cleanup, never another UI or a user source."""
    if identity not in mcp('ui.list').get('contexts',[]):return
    state=mcp('ui.state',context=identity)
    if (state.get('media') or {}).get('paths')!=[fixture_path]:
        raise RuntimeError('Refuse cleanup of unexpected media in test identity')
    if C.activity(cfg).get('recordingCount')!=0:raise RuntimeError('Recording activity changed')
    replacement=C.request(cfg,'/SageTVWebPlayer/api/miniclient',
        {'action':'start','clientId':identity,'width':1280,'height':720,'stream_captions':'off'})
    if replacement.get('clientId','').replace(':','').lower()!=identity or not replacement.get('session'):
        raise RuntimeError('Exact owned cleanup identity mismatch')
    C.request(cfg,'/SageTVWebPlayer/api/miniclient',{'action':'stop','session':replacement['session']})
    deadline=time.monotonic()+10
    while identity in mcp('ui.list').get('contexts',[]) and time.monotonic()<deadline:time.sleep(.5)

before=C.activity(cfg);prior_contexts=mcp('ui.list').get('contexts')
if not isinstance(prior_contexts,list):raise SystemExit('UI listing unavailable')
if before.get('recordingCount')!=0:raise SystemExit('Defer profiling while recordings are active')
fixture_path='/var/media/OpenSageTV_Vibe_Tests/VibeCaptionTest-1080i-CEA608-90s-2s.ts'
fixture=mcp('media.resolve_exact_path',path=fixture_path);media_id=fixture.get('mediaFileId')
if not media_id:raise SystemExit('Canonical completed fixture unavailable')
if identity in prior_contexts:
    if os.environ.get('SAGETV_STARTUP_RETIRE_OWN_FIXTURE')!='1':raise SystemExit('Owned test identity present')
    retire_owned_fixture_ui()
    if identity in mcp('ui.list').get('contexts',[]):raise SystemExit('Exact test cleanup did not settle')
    prior_contexts=mcp('ui.list').get('contexts',[])
rows=[];browser=None;context=None;owned=None;page=None;complete=False;failure=None
# Linux WebKit lacks the native HLS media backend present on iPhone. Measure
# its supported hls.js/MSE path; report that limit, never relabel it Safari HLS.
cases=[('hlsjs-fast-first','hls','auto'),('hlsjs-fast-repeat','hls','auto'),
       ('hlsjs-stable','hls','stable')]
if os.environ.get('SAGETV_STARTUP_CASES')=='followup':cases=cases[1:]
if os.environ.get('SAGETV_STARTUP_CASES')=='inspect':cases=cases[:1]
if os.environ.get('SAGETV_STARTUP_CASES')=='wan':cases=cases[:1]
try:
  with sync_playwright() as pw:
    for label,player,buffer_profile in cases:
      if identity in mcp('ui.list').get('contexts',[]):raise RuntimeError('Previous owned UI not retired')
      # Reset only our canonical synthetic fixture, never user recordings.
      # Otherwise SageTV's saved resume seek creates a second converter and
      # confounds the fresh-start comparison on subsequent runs.
      mcp('media.clear_watched',media_id=media_id,confirm='true')
      browser=pw.webkit.launch(headless=True)
      context=browser.new_context(viewport={'width':852,'height':393},device_scale_factor=3,
          http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block')
      page=context.new_page();owned=None;states=[];errors=[];request_errors=[];generations={};delivery=[]
      if os.environ.get('SAGETV_STARTUP_CASES')=='wan':
        # Synthetic segment delivery only:160ms added round-trip and4Mbps
        # per response. Not a measurement of the user's cellular/VPN route.
        def delayed_segment(route):
          target=urlparse(route.request.url);authorized=urlparse(cfg['web_base_url'])
          if (target.scheme,target.hostname,target.port)!=(authorized.scheme,authorized.hostname,authorized.port):
            raise RuntimeError('Refuse segment interception outside authorized server')
          # WebKit's browser HTTP-auth cache is not inherited by route.fetch's
          # API client. Preserve the commissioned auth only for this exact
          # origin; forbid redirects, never disable SageTV authentication.
          headers=dict(route.request.headers)
          headers['Authorization']='Basic '+base64.b64encode((cfg['web_username']+':'+cfg['web_password']).encode()).decode()
          response=route.fetch(headers=headers,max_redirects=0);body=response.body()
          delivery.append({'status':response.status,'bytes':len(body),'type':response.headers.get('content-type')})
          if response.status!=200 or not body or body[0]!=0x47:
            raise RuntimeError('Constrained-delivery helper did not fetch authenticated MPEG-TS')
          time.sleep(.160+len(body)/500000.0)
          route.fulfill(response=response,body=body)
        page.route('**/hls/**/seg_*.ts*',delayed_segment)
      def observed(response):
        global owned
        try:
          if '/api/miniclient' in response.url and response.request.method=='POST':
            data=response.json()
            if data.get('session') and data.get('clientId','').replace(':','').lower()==identity:owned=data['session']
          elif '/api/hls?' in response.url and len(states)<256:
            data=response.json()
            session_key=data.get('session','')
            if session_key not in generations:generations[session_key]=len(generations)+1
            if os.environ.get('SAGETV_STARTUP_CASES')=='inspect' and owned and re.fullmatch('[a-f0-9]{32}',session_key):
              marker=OUT/(stamp+'-probe-request.json')
              if not marker.exists():
                marker.write_text(json.dumps({'client':identity,'nativeSession':owned,'hlsSession':session_key,
                  'fixture':fixture_path,'expiresAt':time.time()+45}),encoding='utf-8')
            states.append({'generation':generations[session_key],'observedElapsedMs':page.evaluate('performance.now()-STARTUP.t0'),
              **{k:data.get(k) for k in ['segments','playlistReady','firstSegmentMs','producerAgeMs',
                'hlsSeconds','hardware','hardwareDecode','hardwareFilters','encoder','fallbackStage','error',
                'sourceProbeMs','sourceProbeCacheHit']}})
        except Exception:pass
      page.on('response',observed);page.on('pageerror',lambda e:errors.append(str(e)))
      page.on('requestfailed',lambda r:request_errors.append({'path':urlparse(r.url).path,'failure':r.failure}))
      page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');")
      page.add_init_script("localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify("+json.dumps(
        {'player':player,'videoMode':'transcode','videoKbps':1000,'resolution':'480','deinterlace':'on',
         'deinterlaceFilter':'auto','encoder':'auto','keyFrameSeconds':1,'bFrames':0})+"));")
      page.add_init_script("localStorage.setItem('sagetvWebMiniClientSettings.v1',JSON.stringify("+json.dumps(
        {'bufferPreset':buffer_profile,'startSegments':0,'mute':True})+"));")
      page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
      try:
        page.wait_for_function("document.querySelector('#connectionStatus').textContent.toLowerCase().startsWith('connected')",timeout=20000)
      except Exception:
        failure={'stage':'native-connect','pageErrors':errors,'requestErrors':request_errors,
          'ui':page.evaluate("()=>({status:document.getElementById('connectionStatus').textContent,message:document.getElementById('osdMessage').textContent})")}
        page.screenshot(path=str(OUT/(stamp+'-connect-failure.png')))
        raise
      for _ in range(90):
        if owned:
          native=C.request(cfg,'/SageTVWebPlayer/api/miniclient?action=status&session='+owned)
          if native.get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'):break
        page.wait_for_timeout(300)
      else:raise AssertionError('Owned native UI not ready')
      page.evaluate("""()=>{const v=document.getElementById('videoPlane');window.STARTUP={t0:performance.now(),events:[],frame:null};
        for(const name of ['loadstart','loadedmetadata','loadeddata','canplay','play','playing','waiting','stalled','error'])
          v.addEventListener(name,()=>{if(STARTUP.events.length<128)STARTUP.events.push({event:name,ms:performance.now()-STARTUP.t0,time:v.currentTime,ready:v.readyState,network:v.networkState})});
        if(v.requestVideoFrameCallback)v.requestVideoFrameCallback((now,m)=>{STARTUP.frame={ms:performance.now()-STARTUP.t0,mediaTime:m.mediaTime,presentedFrames:m.presentedFrames}});
      }""")
      started=time.monotonic();reply=mcp('media.watch',context=identity,media_id=media_id,wait_ms=0)
      watch_ack_ms=round((time.monotonic()-started)*1000,1)
      if not reply.get('ok'):raise RuntimeError('Canonical Watch rejected')
      try:
        page.wait_for_function("(()=>{let v=document.getElementById('videoPlane');return v.videoWidth>0&&v.currentTime>.2&&!v.paused})()",timeout=45000 if os.environ.get('SAGETV_STARTUP_CASES')=='wan' else 90000)
      except Exception:
        failure={'stage':'first-video','delivery':delivery[-30:],'serverSamples':states,'pageErrors':errors,'requestErrors':request_errors,
          'browser':page.evaluate("()=>({message:document.getElementById('osdMessage').textContent,stats:document.getElementById('stats').textContent,video:{time:videoPlane.currentTime,ready:videoPlane.readyState,width:videoPlane.videoWidth,paused:videoPlane.paused,error:videoPlane.error&&videoPlane.error.message}})")}
        page.screenshot(path=str(OUT/(stamp+'-first-video-failure.png')))
        raise
      first=page.evaluate("""()=>{const v=videoPlane;return{elapsedMs:performance.now()-STARTUP.t0,time:v.currentTime,width:v.videoWidth,height:v.videoHeight,quality:v.getVideoPlaybackQuality?{frames:v.getVideoPlaybackQuality().totalVideoFrames,dropped:v.getVideoPlaybackQuality().droppedVideoFrames}:null}}""")
      observation_ms=30000 if os.environ.get('SAGETV_STARTUP_CASES')=='wan' else 8000
      page.wait_for_timeout(observation_ms)
      result=page.evaluate("""()=>{let v=videoPlane;return{events:STARTUP.events,firstFrame:STARTUP.frame,
        time:v.currentTime,width:v.videoWidth,height:v.videoHeight,paused:v.paused,ready:v.readyState,
        quality:v.getVideoPlaybackQuality?{frames:v.getVideoPlaybackQuality().totalVideoFrames,dropped:v.getVideoPlaybackQuality().droppedVideoFrames}:null,
        buffered:Array.from({length:v.buffered.length},(_,i)=>[v.buffered.start(i),v.buffered.end(i)]),
        stats:document.getElementById('stats').textContent,revision:[...document.scripts].map(s=>s.src).filter(s=>/miniclient\\.js/.test(s)),
        nativeHls:v.canPlayType('application/vnd.apple.mpegurl'),mse:!!window.MediaSource,
        resources:performance.getEntriesByType('resource').filter(r=>/\\.m3u8|\\.ts(?:\\?|$)/.test(r.name)).slice(0,20).map(r=>({kind:r.name.includes('.m3u8')?'playlist':'segment',startMs:r.startTime-STARTUP.t0,durationMs:r.duration,bytes:r.transferSize}))}}""")
      assert result['time']>first['time']+observation_ms/1000*.75,'Decoded playback did not sustain the observation window'
      result['observationMs']=observation_ms
      result['syntheticNetwork']=('160ms additional segment RTT/4Mbps per response' if os.environ.get('SAGETV_STARTUP_CASES')=='wan' else None)
      assert not errors,errors
      hardware=next((s for s in reversed(states) if s.get('encoder')),None)
      assert hardware and hardware['hardware'],('Expected GPU transcoding',hardware)
      result.update(label=label,requestedPlayer=player,bufferProfile=buffer_profile,watchAckMs=watch_ack_ms,
                    firstObservedAdvancing=first,serverSamples=states,pageErrors=errors,requestErrors=request_errors)
      # Read the existing user's Video information action, not a new production
      # test hook or an always-running timing poll. Inspect only after sampling.
      result['startupTiming']=page.evaluate("()=>{document.getElementById('videoInfoBtn').click();const r=JSON.parse(document.getElementById('videoInfoText').textContent).playback.startupTiming;document.getElementById('closeVideoInfo').click();return r}")
      if os.environ.get('SAGETV_STARTUP_CASES')=='inspect':
        active=C.request(cfg,'/SageTVWebPlayer/api/miniclient?action=streamSettings&session='+owned)
        hls=active.get('session','')
        if not re.fullmatch('[a-f0-9]{32}',hls):raise RuntimeError('Expected exact owned HLS generation')
        # SSH identity/known_hosts belong to Windows. A separate read-only host
        # inspector reads this exact short-lived owner marker, verifies current
        # HLS ownership, and returns bounded segment metadata while we hold it.
        marker=OUT/(stamp+'-probe-request.json');reply_path=OUT/(stamp+'-probe-result.json')
        if not marker.exists():raise RuntimeError('Early owner marker not created')
        deadline=time.monotonic()+40
        while not reply_path.exists() and time.monotonic()<deadline:page.wait_for_timeout(250)
        if not reply_path.exists():raise RuntimeError('Host segment inspector did not complete')
        result['segmentInspection']=json.loads(reply_path.read_text(encoding='utf-8'))
      rows.append(result)
      page.screenshot(path=str(OUT/(stamp+'-'+label+'.png')))
      print(json.dumps({'case':label,'watchAckMs':watch_ack_ms,'firstFrame':result['firstFrame'],
         'firstAdvancingMs':round(first['elapsedMs'],1),'firstSegmentMs':next((s['firstSegmentMs'] for s in states if s.get('firstSegmentMs') is not None),None),
         'encoder':hardware['encoder'],'GPUDecode':hardware['hardwareDecode'],'GPUFilters':hardware['hardwareFilters'],
         'nativeHls':result['nativeHls'],'mse':result['mse'],'observationMs':observation_ms,'timeAfterObservation':result['time']}),flush=True)
      # Retire through the client's explicit Exit path before closing the
      # browser, so a foreground/recovery callback cannot recreate the UI.
      page.locator('#remoteToggle').click()
      page.locator('#closeRemote').click()
      page.locator('#confirmClientExit').click()
      page.wait_for_function("!document.getElementById('clientExited').hidden",timeout=10000)
      # The browser beacon is best-effort during context teardown; complete
      # that same exact owned stop independently if it has not arrived yet.
      try:C.request(cfg,'/SageTVWebPlayer/api/miniclient',{'action':'stop','session':owned})
      except RuntimeError as error:
        if 'HTTP 404' not in str(error):raise
      owned=None
      context.close();context=None;page=None
      browser.close();browser=None
      # Native sockets close asynchronously after the HTTP stop acknowledges.
      # Wait for removal; never replace a still-present UI to accelerate a run.
      deadline=time.monotonic()+25
      while identity in mcp('ui.list').get('contexts',[]) and time.monotonic()<deadline:time.sleep(.5)
      if identity in mcp('ui.list').get('contexts',[]):retire_owned_fixture_ui()
      if identity in mcp('ui.list').get('contexts',[]):raise RuntimeError('Owned UI close did not settle')
    complete=True
finally:
    if page and not complete:
        try:page.screenshot(path=str(OUT/(stamp+'-failure.png')))
        except Exception:pass
    if owned:
        try:C.request(cfg,'/SageTVWebPlayer/api/miniclient',{'action':'stop','session':owned})
        except Exception:pass
    if context:
        try:context.close()
        except Exception:pass
    if browser:
        try:browser.close()
        except Exception:pass
    if identity in mcp('ui.list').get('contexts',[]):
        try:retire_owned_fixture_ui()
        except Exception as error:failure={'cleanupError':str(error)[:300],'priorFailure':failure}
    after=C.activity(cfg);after_contexts=mcp('ui.list').get('contexts',[])
    report={'completed':complete,'server':'.232 stock','engine':'host WebKit','physicalIPhone':False,
      'fixture':fixture_path,'otherContextsBefore':len(prior_contexts),'otherContextsAfter':len(after_contexts),
      'ownedRetired':identity not in after_contexts,'recordingsBefore':before.get('recordingCount'),
      'recordingsAfter':after.get('recordingCount'),'cases':rows,'failure':failure}
    (OUT/(stamp+'-startup.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'complete':complete,'cases':len(rows),'ownedRetired':identity not in after_contexts}),flush=True)
