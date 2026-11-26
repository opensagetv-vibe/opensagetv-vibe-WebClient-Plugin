#!/usr/bin/env python3
"""Explicitly authorized short real recording -> growth -> completion -> cleanup.

Existing production Record/Cancel/Library interfaces only, no new MCP control,
synthetic EPG, Core patch, tuner/config setting or household-media deletion.
Durable exact ownership before Watch. On failure preserve media for diagnosis,
cancel only our capture and retire only our UI; never replay unknown controls.
"""
import argparse,importlib.util,json,time
from pathlib import Path
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright
from bounded_browser_rpc import bounded
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--engine',choices=('chromium','webkit'),required=True)
a=p.parse_args();identity='da92a86446be';airing_id=36124
out=ROOT/'artifacts/active/WP11-008';out.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());path=out/(stamp+'-'+a.engine+'-growing-recording.json')
report=dict(passed=False,realStock232=True,physicalPhone=False,engine=a.engine,
    userAuthorizedTestRecording=True,airingId=airing_id,rows=[],cleanup=[],retirementReadFailures=[])
owned=producer=media_id=None;source_path=None;page=context=browser=pw=None
record_attempted=cancel_attempted=False;baseline=None

def save():path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
def mcp(action,**kw):return C.request(cfg,'/v1/control',dict(action=action,**kw),mcp=True,timeout=15)
def mini(action,**kw):return C.request(cfg,'/SageTVWebPlayer/api/miniclient?'+urlencode(dict(action=action,session=owned,**kw)))
def guide():return C.request(cfg,'/SageTVWebPlayer/api/guide?hours=1')
def source():
    rows=[x for x in guide()['airings'] if x['airingId']==airing_id]
    if len(rows)!=1:raise RuntimeError('Exact test airing unavailable')
    return rows[0]
def media():return C.request(cfg,'/SageTVWebPlayer/api/media?'+urlencode(dict(id=media_id)))
def schedule():return C.request(cfg,'/SageTVWebPlayer/api/dvr')['scheduled']
def active():return C.request(cfg,'/SageTVWebPlayer/api/recordings?active=true&limit=500')['recordings']
def hls():return C.request(cfg,'/SageTVWebPlayer/api/hls?'+urlencode(dict(session=producer)))
def guard(initial=False):
    state=C.activity(cfg);contexts=mcp('ui.list').get('contexts')
    expected=[] if initial else [identity]
    if state.get('connectedClientCount')!=0 or contexts!=expected:raise RuntimeError('Unrelated client/UI; preserve it')
    records=active()
    if initial and (records or state.get('recordingCount')!=0):raise RuntimeError('Require independently idle initial server')
    if not initial and any(x['id']!=media_id for x in records):raise RuntimeError('Unrelated recording appeared')
def wait(test,label,seconds=45):
    deadline=time.monotonic()+seconds
    while time.monotonic()<deadline:
        if test():return
        page.wait_for_timeout(200)
    raise RuntimeError('Timed out '+label+'; ordered command not replayed')
def observed(response):
    global owned
    if '/api/miniclient' not in response.url or response.request.method!='POST':return
    try:
        d=response.json()
        if d.get('clientId','').replace(':','').lower()==identity and d.get('session'):owned=d['session']
    except Exception:pass
def sample():
    return page.evaluate("()=>{const v=videoPlane,s=__growing;return{time:v.currentTime,frames:s.frames,current:s.source===v.currentSrc,paused:v.paused,ended:v.ended,endedEvents:s.ended,ready:v.readyState,width:v.videoWidth,error:v.error?.code||null,prompt:!autoplayBtn.hidden,message:osdMessage.textContent,player:s.player?.snapshot()||null}}")
def moving():
    first=sample();activated=False;deadline=time.monotonic()+70
    while time.monotonic()<deadline:
        v=sample()
        if v['error']:raise RuntimeError('Actual browser decoder error')
        if v['prompt'] and not activated:page.locator('#autoplayBtn').click(timeout=3000);activated=True
        if v['current'] and v['frames']>first['frames']+8 and not v['paused'] and v['time']>.2:return v
        page.wait_for_timeout(150)
    report['last']=v;raise RuntimeError('No new decoded pictures')
def owned_cancel():
    global cancel_attempted
    if cancel_attempted:raise RuntimeError('Cancellation already attempted; no replay')
    current=source();mine=[x for x in schedule() if x['airingId']==airing_id]
    if not record_attempted or not current.get('manualRecord') or (media_id and current.get('mediaId')!=media_id) or len(mine)!=1:
        raise RuntimeError('Exact new manual reservation ownership missing')
    cancel_attempted=True;report['cancelIntent']=True;save()
    if not C.request(cfg,'/SageTVWebPlayer/api/dvr',dict(action='cancel',airingId=airing_id)).get('ok'):
        raise RuntimeError('Owned cancellation unacknowledged')

try:
    guard(True);baseline=schedule();current=source();now=int(time.time()*1000)
    if current['title']!='NBC 5 News Today at 5:30 AM' or current['channelNumber']!='5.1' or not current['currentlyAiring'] or current['end']<now+240000:
        raise RuntimeError('Exact current source/time changed')
    if current.get('mediaId') or current.get('manualRecord') or current.get('watched') or any(x['airingId']==airing_id for x in baseline):
        raise RuntimeError('Existing user media/schedule/watch state; no test takeover')
    tuners=C.request(cfg,'/SageTVWebPlayer/api/tuners')['devices']
    if not any(x.get('functioning') and 'HDHomeRun' in x['name'] and not x.get('liveClient') and not x.get('currentMediaId') for x in tuners):
        raise RuntimeError('No free functioning HDHR tuner')
    report['baseline']=dict(source=current,schedule=baseline);save()
    pw=sync_playwright().start()
    browser=pw.webkit.launch(headless=True) if a.engine=='webkit' else pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':852,'height':393},service_workers='block',http_credentials={'username':cfg['web_username'],'password':cfg['web_password']})
    profile=dict(player='hls',videoMode='transcode',encoder='qsv',videoKbps=1000,resolution='480',deinterlace='on',audioCodec='aac',allowFallback=False)
    context.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebStreaming.v1',"+json.dumps(json.dumps(profile))+");")
    page=context.new_page();original=page.evaluate;page.evaluate=lambda *args,**kw:bounded(original,*args,**kw)
    page.on('response',observed);page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
    wait(lambda:owned and mini('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'),'native first frame')
    guard();profiles=page.evaluate("['sagetvWebMiniClientSettings.v1','sagetvWebStreaming.v1','sagetvWebCaptionAuthority.v1'].map(k=>localStorage.getItem(k))");configured=mini('streamSettings')['configured']
    page.evaluate("()=>{const s=window.__growing={frames:0,source:'',ended:0,player:null};videoPlane.addEventListener('ended',()=>s.ended++);const original=SageMiniPlayback.prototype.start;SageMiniPlayback.prototype.start=function(...args){s.player=this;return original.apply(this,args)};function f(){const source=videoPlane.currentSrc;videoPlane.requestVideoFrameCallback(()=>{if(source&&source===videoPlane.currentSrc){s.frames++;s.source=source}f()})}f()}")
    if schedule()!=baseline or source().get('mediaId'):raise RuntimeError('Source changed before record dispatch')
    record_attempted=True;report['recordIntent']=True;save()
    receipt=C.request(cfg,'/SageTVWebPlayer/api/guide',dict(action='record',airingId=airing_id))
    if not receipt.get('accepted'):raise RuntimeError('Record dispatch rejected')
    wait(lambda:source().get('manualRecord') and source().get('mediaId') and len(active())==1,'new actual recording',45)
    current=source();media_id=current['mediaId'];owned_media=media()
    if owned_media['id']!=media_id or owned_media['channelNumber']!='5.1' or not owned_media['recording'] or len(owned_media['files'])!=1:
        raise RuntimeError('New recording identity mismatch')
    if [x['id'] for x in active()]!=[media_id]:raise RuntimeError('Unrelated capture; no ownership assumption')
    source_path=owned_media['files'][0]['path'];report['ownership']=dict(mediaId=media_id,path=source_path,initial=owned_media);save()
    wait(lambda:media()['files'][0]['streamSize']>188*200,'real new recording bytes',30)
    if not C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action='watchContent',session=owned,mediaId=media_id)).get('accepted'):
        raise RuntimeError('One owned Watch rejected')
    first=moving();producer=mini('streamSettings')['session'];state=hls()
    if state.get('mediaId')!=media_id or state.get('activeRecording') is not True or state.get('endList'):
        raise RuntimeError('Not following exact growing recording')
    report['rows'].append(dict(gate='real-new-HDHR-capture-and-native-QSV-playback',passed=True,first=first,inputMode=state.get('inputMode'),producer=producer));save()
    samples=[]
    for _ in range(5):
        page.wait_for_timeout(5000);v=sample();state=hls();info=media()
        samples.append(dict(video=v,bytes=info['files'][0]['streamSize'],inputBytes=state.get('bytesInput'),outputSeconds=state.get('hlsSeconds')))
        if not info['recording'] or not state.get('activeRecording') or state.get('endList') or v['endedEvents'] or v['error'] or mini('streamSettings')['session']!=producer:
            raise RuntimeError('Growing source ended/replaced/failed prematurely')
        if v['player'] and (v['player']['recoveries'] or v['player']['clockRegressions']):raise RuntimeError('Growing source recovery/clock loop')
    if samples[-1]['bytes']<=samples[0]['bytes'] or samples[-1]['video']['frames']<=samples[0]['video']['frames']+20:
        raise RuntimeError('Source bytes or decoded pictures did not grow')
    report['rows'].append(dict(gate='same-producer-live-file-grows-and-continues-through-input-EOF',passed=True,samples=samples));save()
    guard();owned_cancel()
    wait(lambda:not media()['recording'] and not source().get('manualRecord') and not active(),'owned recording completion flag',30)
    wait(lambda:hls().get('activeRecording') is False and hls().get('endList') is True,'same producer completed ENDLIST',40)
    final=hls()
    if final.get('exitCode')!=0 or final.get('running') or final.get('session')!=producer:raise RuntimeError('Producer did not finish cleanly')
    report['rows'].append(dict(gate='real-capture-stop-to-finite-same-producer-ENDLIST',passed=True,final={k:final.get(k) for k in ('durationMs','hlsSeconds','bytesInput','bytesProduced','exitCode','activeRecording','endList','hardware','hardwareDecode','hardwareFilters')}));save()
    wait(lambda:sample()['endedEvents']>0,'actual browser completed EOF',100)
    last=sample()
    if last['error'] or (last['player'] and last['player']['recoveries']) or 'Buffering' in last['message']:
        raise RuntimeError('Completion stuck in buffering/recovery')
    report['rows'].append(dict(gate='actual-browser-ended-without-infinite-refill-or-restart',passed=True,last=last))
    if profiles!=page.evaluate("['sagetvWebMiniClientSettings.v1','sagetvWebStreaming.v1','sagetvWebCaptionAuthority.v1'].map(k=>localStorage.getItem(k))") or mini('streamSettings')['configured']!=configured:
        raise RuntimeError('Saved/configured profiles changed')
    report['rows'].append(dict(gate='exact-client-profiles-preserved',passed=True));report['passed']=True;save()
except Exception as e:
    report['failure']=dict(type=type(e).__name__,message=str(e)[:220] if isinstance(e,RuntimeError) else 'Bounded field observation unavailable')
    if page:
        try:report['last']=sample();page.screenshot(path=str(path.with_suffix('.png')))
        except Exception:pass
    if producer:
        try:report['lastProducer']=hls()
        except Exception:pass
finally:
    if record_attempted and not cancel_attempted:
        try:
            if source().get('manualRecord'):owned_cancel()
        except Exception:report['cleanup'].append('Owned capture cancellation unconfirmed; do not replay')
    if owned:
        try:
            if mcp('ui.state',context=identity).get('fullyLoaded'):
                if not mcp('media.control',context=identity,operation='stop').get('accepted'):raise RuntimeError('Native Stop rejected')
            if not C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action='stop',session=owned)).get('ok'):raise RuntimeError('UI Stop rejected')
        except Exception:report['cleanup'].append('Owned Stop unknown; no replay')
    for resource in (context,browser,pw):
        if resource:
            try:bounded(resource.stop if resource is pw else resource.close)
            except Exception:report['cleanup'].append('Browser shutdown unknown')
    if owned:
        deadline=time.monotonic()+90
        while time.monotonic()<deadline:
            try:
                reply=C.request(cfg,'/v1/control',dict(action='ui.list'),mcp=True,timeout=5)
                if reply.get('ok') is not True or not isinstance(reply.get('contexts'),list):raise RuntimeError('Invalid retirement reply')
                if identity not in reply['contexts']:break
            except Exception as e:report['retirementReadFailures'].append(type(e).__name__)
            time.sleep(.5)
        else:report['cleanup'].append('Native retirement unknown')
    # Successful test only: remove exactly the newly recorded, now inactive ID.
    # Failures retain their media and ownership for investigation.
    if report['passed'] and not report['cleanup'] and media_id:
        try:
            if not C.activity(cfg).get('safeToRestart') or schedule()!=baseline:raise RuntimeError('Not independently idle/restored')
            current=media()
            if current['recording'] or len(current['files'])!=1 or current['files'][0]['path']!=source_path or source().get('mediaId')!=media_id:
                raise RuntimeError('Exact owned media deletion check failed')
            if not C.request(cfg,'/SageTVWebPlayer/api/library',dict(action='unwatched',id=media_id)).get('ok'):raise RuntimeError('Original unwatched restoration rejected')
            report['deleteOwnedMediaIntent']=media_id;save()
            if not C.request(cfg,'/SageTVWebPlayer/api/library',dict(action='deleteWithoutPrejudice',id=media_id,confirm='DELETE')).get('ok'):
                raise RuntimeError('Owned test-media deletion unacknowledged')
            if source().get('mediaId') or source().get('manualRecord') or source().get('watched'):raise RuntimeError('Original source state not restored')
            report['rows'].append(dict(gate='owned-test-recording-only-removed-original-schedule-and-airing-state-restored',passed=True))
            report['testRecordingDeleted']=True
        except Exception:report['cleanup'].append('Owned test-media cleanup incomplete; preserve exact manifest/no deletion replay')
    report['passed']=report['passed'] and not report['cleanup'];save()
    print(json.dumps(dict(passed=report['passed'],rows=len(report['rows']),report=str(path),failure=report.get('failure'),cleanup=report['cleanup'])),flush=True)
raise SystemExit(0 if report['passed'] else 1)
