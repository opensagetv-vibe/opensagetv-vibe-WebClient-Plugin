#!/usr/bin/env python3
"""Authorized real mobile Guide Record/status/cancel, on a new owned reservation.

Uses existing production/public APIs, never synthetic EPG or arbitrary server
controls. No tuner is allocated: the selected airing must remain future and
have no manual reservation or media. Cancel ONLY this test's new reservation.
"""
import argparse,importlib.util,json,time
from pathlib import Path
from urllib.parse import parse_qs,urlencode,urlparse
from playwright.sync_api import sync_playwright
from bounded_browser_rpc import bounded
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--engine',choices=('chromium','webkit'),required=True)
a=p.parse_args();identity='da92a86446be';airing_id=32620
out=ROOT/'artifacts/active/WEB-080';out.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());path=out/(stamp+'-'+a.engine+'-future-record.json')
report=dict(passed=False,engine=a.engine,physicalPhone=False,realStock232=True,airingId=airing_id,
    userAuthorizedTestRecording=True,rows=[],cleanup=[],retirementReadFailures=[])
owned=None;page=context=browser=pw=None;attempted=False;baseline=None

def save():path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
def mcp(action,**kw):return C.request(cfg,'/v1/control',dict(action=action,**kw),mcp=True,timeout=5)
def status():return C.request(cfg,'/SageTVWebPlayer/api/guide?'+urlencode(dict(action='recordStatus',airingId=airing_id)))
def schedule():return C.request(cfg,'/SageTVWebPlayer/api/dvr')['scheduled']
def mini(action):return C.request(cfg,'/SageTVWebPlayer/api/miniclient?'+urlencode(dict(action=action,session=owned)))
def guard(own=False):
    activity=C.activity(cfg)
    if activity.get('recordingCount')!=0 or activity.get('connectedClientCount')!=0:raise RuntimeError('Unexpected recording/client activity')
    if mcp('ui.list').get('contexts')!=([identity] if own else []):raise RuntimeError('Unexpected UI; no takeover')
def wait(test,label,seconds=30):
    deadline=time.monotonic()+seconds
    while time.monotonic()<deadline:
        if test():return
        page.wait_for_timeout(150)
    raise RuntimeError('Timed out '+label+'; ordered command not replayed')
def observed(response):
    global owned
    if '/api/miniclient' not in response.url or response.request.method!='POST':return
    try:
        d=response.json()
        if d.get('clientId','').replace(':','').lower()==identity and d.get('session'):owned=d['session']
    except Exception:pass

try:
    guard();baseline=schedule()
    guide=C.request(cfg,'/SageTVWebPlayer/api/guide?hours=2')
    source=[x for x in guide['airings'] if x['airingId']==airing_id]
    if len(source)!=1:raise RuntimeError('Exact future airing missing')
    source=source[0]
    if source['title']!='CBS News Chicago 6:00am' or source['channelNumber']!='2.1' or source['start']<guide['now']+300000:
        raise RuntimeError('Owned reservation requires the exact sufficiently future airing')
    if source.get('mediaId') or source.get('manualRecord') or status().get('scheduled') is not False or any(x['airingId']==airing_id for x in baseline):
        raise RuntimeError('Existing user reservation/media; do not modify')
    report['baseline']=dict(airing=source,schedule=baseline);save()
    pw=sync_playwright().start()
    browser=pw.webkit.launch(headless=True) if a.engine=='webkit' else pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':393,'height':852},has_touch=True,service_workers='block',
        http_credentials={'username':cfg['web_username'],'password':cfg['web_password']})
    context.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE')")
    page=context.new_page();original=page.evaluate;page.evaluate=lambda *args,**kw:bounded(original,*args,**kw)
    page.on('response',observed);page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
    wait(lambda:owned and mini('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'),'native UI')
    guard(True);profiles=page.evaluate("['sagetvWebMiniClientSettings.v1','sagetvWebStreaming.v1','sagetvWebCaptionAuthority.v1'].map(k=>localStorage.getItem(k))")
    configured=mini('streamSettings')['configured']
    page.locator('#mobileTab-guide').click()
    target=page.locator('.mc-mobile-program').filter(has=page.locator('strong',has_text='CBS News Chicago 6:00am'))
    wait(lambda:target.count()==1,'exact future Guide program')
    target.click();record=page.locator('.mc-mobile-guide-details [data-content-action]',has_text='Record')
    if not record.is_visible() or not record.is_enabled():raise RuntimeError('Production future Record unavailable')
    guard(True)
    if status().get('scheduled') is not False or schedule()!=baseline:raise RuntimeError('Schedule changed before dispatch')
    attempted=True;report['recordDispatchIntent']=True;save()
    with page.expect_response(lambda r:'/api/guide' in r.url and r.request.method=='POST') as response:
        record.click()
    req=parse_qs(urlparse(response.value.url).query)
    req.update(parse_qs(response.value.request.post_data or ''))
    report['recordTarget']={k:req.get(k) for k in ('action','airingId')};save()
    if req.get('airingId')!=[str(airing_id)] or req.get('action')!=['record']:raise RuntimeError('Wrong production Record target')
    reply=response.value.json()
    if not reply.get('accepted'):raise RuntimeError('Record dispatch rejected')
    wait(lambda:status().get('scheduled') is True,'actual new manual reservation')
    wait(lambda:page.locator('.mc-mobile-guide-details [data-content-action]',has_text='Scheduled').count()==1,'Scheduled confirmation')
    current=schedule();new=[x for x in current if x['airingId']==airing_id]
    if len(new)!=1 or not new[0]['manualRecord'] or new[0]['mediaId'] or [x for x in current if x['airingId']!=airing_id]!=baseline:
        raise RuntimeError('Unexpected reservation/media change')
    report['rows'].append(dict(gate='production-Guide-one-Record-actual-manual-schedule-and-label',passed=True,receipt=reply));save()
    page.screenshot(path=str(path.with_suffix('.png')))
    if profiles!=page.evaluate("['sagetvWebMiniClientSettings.v1','sagetvWebStreaming.v1','sagetvWebCaptionAuthority.v1'].map(k=>localStorage.getItem(k))") or mini('streamSettings')['configured']!=configured:
        raise RuntimeError('Client profiles changed')
    report['rows'].append(dict(gate='client-profiles-preserved',passed=True));report['passed']=True
except Exception as e:
    report['failure']=dict(type=type(e).__name__,message=str(e)[:200] if isinstance(e,RuntimeError) else 'Bounded field observation failed')
finally:
    if attempted:
        try:
            if status().get('scheduled') is True:
                current=schedule();mine=[x for x in current if x['airingId']==airing_id]
                if len(mine)!=1 or mine[0]['mediaId'] or mine[0]['start']<int(time.time()*1000)+60000:
                    raise RuntimeError('Cancellation ownership/future safety changed')
                if not C.request(cfg,'/SageTVWebPlayer/api/dvr',dict(action='cancel',airingId=airing_id)).get('ok'):
                    raise RuntimeError('Owned cancel unacknowledged')
                wait(lambda:status().get('scheduled') is False,'owned cancel observed')
            if schedule()!=baseline:raise RuntimeError('Original schedule not restored')
            report['rows'].append(dict(gate='owned-new-reservation-cancelled-original-schedule-exact',passed=True))
        except Exception:report['cleanup'].append('Owned reservation restoration unavailable; do not replay cancellation')
    if owned:
        try:
            if not C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action='stop',session=owned)).get('ok'):report['cleanup'].append('Owned UI Stop unacknowledged')
        except Exception:report['cleanup'].append('Owned UI Stop unknown; no replay')
    for resource in (context,browser,pw):
        if resource:
            try:bounded(resource.stop if resource is pw else resource.close)
            except Exception:report['cleanup'].append('Browser shutdown unknown')
    if owned:
        deadline=time.monotonic()+90
        while time.monotonic()<deadline:
            try:
                result=mcp('ui.list')
                if result.get('ok') is not True or not isinstance(result.get('contexts'),list):raise RuntimeError('Unproven retirement response')
                if identity not in result['contexts']:break
            except Exception as e:report['retirementReadFailures'].append(type(e).__name__)
            time.sleep(.5)
        else:report['cleanup'].append('Native retirement unverified')
    report['passed']=report['passed'] and not report['cleanup'];save()
    print(json.dumps(dict(passed=report['passed'],rows=len(report['rows']),report=str(path),failure=report.get('failure'),cleanup=report['cleanup'])),flush=True)
raise SystemExit(0 if report['passed'] else 1)
