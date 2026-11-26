"""WEB-120 installed stock232 regression; actual browser/FFmpeg, not physical phone.

Explicit opt-in uses the user-reported existing multi-segment recording. No
Record reservation, deletion, watched-state clearing or server setting change.
Stock Watch of a currently airing TV file may resume its live capture; the exact
owned UI is stopped at teardown, never a scheduled recording cancellation.
"""
import argparse,importlib.util,json,os,time
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',root/'scripts/commission-mobile.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);cfg=c.configuration()
p=argparse.ArgumentParser();p.add_argument('--run-stock232',action='store_true');p.add_argument('--media-id',type=int,required=True);p.add_argument('--health-seconds',type=int,default=0);p.add_argument('--recovery-probe',action='store_true');args=p.parse_args()
if not 0<=args.health_seconds<=180:raise SystemExit('Health observation must be bounded to180 seconds')
if not args.run_stock232:raise SystemExit('Explicit installed-server opt-in required')
identity='da92a86446be';owned=None;report={'passed':False,'physicalPhone':False,'rows':[]};page=None
engine=os.environ.get('SAGETV_BROWSER_ENGINE','chromium')
if engine not in ('chromium','webkit'):raise SystemExit('Unsupported browser engine')
report['engine']=engine
recovery_requests=[]
out=root/('artifacts/active/WEB-121' if args.health_seconds else 'artifacts/active/WEB-120');out.mkdir(parents=True,exist_ok=True)
path=out/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-stock-rollover.json')
def api(action,**v):return c.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action=action,session=owned,**v))
def mcp(action,**v):return c.request(cfg,'/v1/control',dict(action=action,**v),mcp=True)
def state():return c.request(cfg,'/SageTVWebPlayer/api/miniclient?action=playbackState&session='+owned)
def producer():
    sid=state().get('producer')
    if not sid:return {}
    try:return c.request(cfg,'/SageTVWebPlayer/api/hls?session='+sid)
    except RuntimeError as error:
        if str(error).startswith('HTTP 404:'):return {} # read-only replacement gap; never replay input
        raise
def observe(response):
    global owned
    if '/api/miniclient' in response.url and response.request.method=='POST':
        try:
            v=response.json()
            if 'action=recover' in response.url:recovery_requests.append({'accepted':v.get('ok'),'at':time.monotonic()})
            if v.get('session') and v.get('clientId','').replace(':','').lower()==identity:owned=v['session']
        except Exception:pass
def wait(test,seconds=60):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        result=test()
        if result:return result
        page.wait_for_timeout(200)
    raise RuntimeError('Bounded installed observation timed out; inputs were not replayed')
try:
    activity=c.activity(cfg);contexts=mcp('ui.list').get('contexts')
    if activity['recordingCount'] or activity['connectedClientCount'] or contexts not in ([],[identity]):
        raise RuntimeError('Unrelated recording/client; preserve it')
    if contexts and mcp('ui.state',context=identity).get('fullyLoaded'):
        raise RuntimeError('Existing test playback still active; preserve it')
    media=c.request(cfg,'/SageTVWebPlayer/api/media?id='+str(args.media_id))
    if media['recording'] or media['segments']<2:raise RuntimeError('Require existing completed multi-segment source; never create recording')
    with sync_playwright() as pw:
        launch={'headless':True}
        if engine=='chromium':launch.update(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
        browser=getattr(pw,engine).launch(**launch)
        context=browser.new_context(http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block')
        page=context.new_page();page.on('response',observe)
        page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify({player:'hls',allowFallback:true}));")
        page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html?ui=1280x720')
        wait(lambda:owned and page.locator('#connectionStatus').inner_text().lower().startswith('connected'))
        page.wait_for_timeout(2000)
        if not api('watchContent',mediaId=args.media_id).get('accepted'):raise RuntimeError('Single Watch rejected')
        wait(lambda:state().get('producer'))
        initial=producer();report['initialProducer']=initial
        if initial.get('transport')!='hls':raise RuntimeError('This HLS gate negotiated another transport; do not relabel it')
        if initial.get('nativeSegment') is not True:raise RuntimeError('Loaded application is not WEB-120; no seek attempted')
        mcp('media.seek',context=identity,target_ms=0)
        first=wait(lambda:(lambda s:s if s.get('nativeSegment') is True and s.get('sourceSegment')==0 else None)(producer()))
        duration=first['durationMs'];print(json.dumps({'selectedSegment':first['sourceSegment'],'durationMs':duration}),flush=True)
        if duration<10000:raise RuntimeError('First native segment too short for independent tail test')
        recoveries_before_tail=len(recovery_requests)
        mcp('media.seek',context=identity,target_ms=duration-6000)
        tail=wait(lambda:(lambda s:s if s.get('nativeSegment') and s.get('sourceSegment')==0 and s.get('startSeconds',0)>=(duration-6500)/1000 else None)(producer()))
        wait(lambda:page.locator('#videoPlane').evaluate('v=>v.readyState>=2&&!v.paused&&v.currentTime>0'),90)
        next_piece=wait(lambda:(lambda s:s if s.get('nativeSegment') and s.get('sourceSegment')==1 else None)(producer()),60)
        wait(lambda:page.locator('#videoPlane').evaluate('v=>v.readyState>=2&&!v.paused&&v.currentTime>1'),60)
        if len(recovery_requests)!=recoveries_before_tail:raise RuntimeError('Completed physical tail replayed recovery instead of advancing cleanly')
        report['rows'].append({'gate':'native-segment-zero-actual-tail-to-segment-one','passed':True,'before':tail,'after':next_piece})
        frames=page.locator('#videoPlane').evaluate('v=>v.getVideoPlaybackQuality().totalVideoFrames');page.wait_for_timeout(3000)
        after=producer();after_frames=page.locator('#videoPlane').evaluate('v=>v.getVideoPlaybackQuality().totalVideoFrames')
        if after['sourceSegment']!=1 or after_frames<=frames:raise RuntimeError('Next segment replayed zero or did not advance pictures')
        report['rows'].append({'gate':'segment-one-sustains-pictures-no-zero-replay','passed':True,'frames':after_frames-frames})
        if args.recovery_probe:
            # Explicit single production recovery intent on this disposable UI.
            # Tests real request/event/decoder flow, not a simulated VPN failure.
            previous=state()['producer'];prior=producer()
            target=round((prior['startSeconds']+page.locator('#videoPlane').evaluate('v=>v.currentTime'))*1000)
            began=time.monotonic();receipt=api('recover',expectedHlsSession=previous,timeMs=target);latency=round((time.monotonic()-began)*1000)
            if not receipt.get('ok') or receipt.get('pending') is not True or latency>2000:
                raise RuntimeError('Recovery did not return bounded asynchronous acceptance')
            replacement=wait(lambda:(lambda s:s if s.get('session') and s['session']!=previous else None)(producer()))
            wait(lambda:page.locator('#videoPlane').evaluate('v=>v.readyState>=2&&!v.paused&&v.currentTime>.5'),90)
            first_frames=page.locator('#videoPlane').evaluate('v=>v.getVideoPlaybackQuality().totalVideoFrames');page.wait_for_timeout(3000)
            last_frames=page.locator('#videoPlane').evaluate('v=>v.getVideoPlaybackQuality().totalVideoFrames');current_producer=producer()
            if last_frames<=first_frames or current_producer.get('streamHealth',{}).get('browserRevision')!='web121.4':
                raise RuntimeError('Replacement lacks real decoded progress or exact loaded revision')
            report['rows'].append({'gate':'single-async-recovery-real-decoded-output','passed':True,'acceptanceMs':latency,
                'targetMs':target,'frames':last_frames-first_frames,'before':previous,'after':current_producer})
        current=c.request(cfg,'/SageTVWebPlayer/api/media?id='+str(args.media_id))
        if current['recording']:
            previous=state()['producer']
            page.locator('#remoteToggle').click()
            with page.expect_response(lambda r:'action=goLive' in r.url,timeout=20000) as response:
                page.locator('#remoteLive').click()
            if not response.value.json().get('accepted'):raise RuntimeError('Production Watch live rejected')
            live=wait(lambda:(lambda s:s if s.get('session') and s['session']!=previous and s.get('activeRecording') and s.get('sourceSegment',-1)>=current['segments']-1 else None)(producer()),90)
            wait(lambda:page.locator('#videoPlane').evaluate('v=>v.readyState>=2&&!v.paused&&v.currentTime>.5'),60)
            report['rows'].append({'gate':'actual-DOM-Watch-live-to-current-growing-segment','passed':True,'after':live})
        if args.health_seconds:
            deadline=time.monotonic()+args.health_seconds
            observed=[]
            while time.monotonic()<deadline:
                page.wait_for_timeout(2000)
                item=producer()
                if item:observed.append({'producer':item['session'],'health':item.get('streamHealth'),'time':page.locator('#videoPlane').evaluate('v=>v.currentTime'),'frames':page.locator('#videoPlane').evaluate('v=>v.getVideoPlaybackQuality().totalVideoFrames')})
            if not observed or not any(r.get('health',{}).get('browserSeen') and r['health']['requests']>0 for r in observed):
                raise RuntimeError('Installed server recorder has no actual browser/delivery feedback')
            report['rows'].append({'gate':'installed-passive-health-observation','passed':True,'seconds':args.health_seconds,'samples':observed})
            # A recorder that sampled a frozen browser is not playback PASS.
            progressed=sum(1 for a,b in zip(observed,observed[1:]) if a['producer']==b['producer'] and b['frames']>a['frames'] and b['time']>a['time'])
            if progressed<3:raise RuntimeError('Health recorder works but actual pictures did not sustain; preserve the captured source/producer evidence')
            recent=observed[-10:]
            if len(recent)>=3 and not any(a['producer']==b['producer'] and b['frames']>a['frames'] and b['time']>a['time'] for a,b in zip(recent,recent[1:])):
                raise RuntimeError('No actual picture progress in final observation window; recorder acceptance is not playback acceptance')
            report['rows'].append({'gate':'actual-picture-progress-during-health-observation','passed':True,'progressedSamples':progressed})
            history=c.request(cfg,'/SageTVWebPlayer/api/support?action=streamHealth')
            if history.get('storageState')!='written' or not history.get('sessions'):raise RuntimeError('Server journal not written')
            report['healthBeforeClose']=history
        report['passed']=True
        report['recoveryRequests']=recovery_requests
        context.close();browser.close()
except Exception as error:
    report['error']=str(error)[:400]
    if owned:
        try:report['failureProducer']=producer();report['failureNative']=mcp('ui.state',context=identity)
        except Exception:pass
    if page and not page.is_closed():
        try:report['failureVideo']=page.locator('#videoPlane').evaluate('v=>({time:v.currentTime,ready:v.readyState,paused:v.paused,ended:v.ended,error:v.error?.code,frames:v.getVideoPlaybackQuality().totalVideoFrames})')
        except Exception:pass
    raise
finally:
    report['recoveryRequests']=recovery_requests
    if owned:
        try:api('stop')
        except RuntimeError:pass
    if args.health_seconds:
        try:report['healthAfterClose']=c.request(cfg,'/SageTVWebPlayer/api/support?action=streamHealth')
        except Exception as error:report['healthAfterCloseError']=str(error)[:200]
    path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':report['passed'],'report':str(path)}))
