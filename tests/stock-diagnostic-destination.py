#!/usr/bin/env python3
"""WP14-006 approved real destination/spool/retry with actual browser playback.

Only the dedicated user-approved folder and our two hash-proven ZIPs move.
No recording, household setting, Core or unrelated diagnostic report is edited.
"""
import hashlib,importlib.util,io,json,re,stat,time,zipfile
from pathlib import Path
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
identity='da92a86446be';owned=None;context=None;browser=None;pw=None
client=None;files=None;held=False;obstruction=False;rows=[];cleanup=[];failure=None
out=ROOT/'artifacts/active/WP14-006';out.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());passed=False
directory='/mnt/user/appdata/sagetv-stock-u26-gpu-j11/server/VibeWebDiagnosticTest'
holding=directory+'-WP14-006-held';marker=b'WP14-006 owned unavailable-destination fixture\n'
known={};pattern=re.compile(r'^SageTV-WebPlayer-diagnostics-\d{8}-\d{6}-\d{3}\.zip$')
def mcp(action,**kw):return C.request(cfg,'/v1/control',dict(action=action,**kw),mcp=True)
def api(action,**kw):return C.request(cfg,'/SageTVWebPlayer/api/miniclient?'+urlencode(dict(action=action,session=owned,**kw)))
def support():return C.request(cfg,'/SageTVWebPlayer/api/support')
def observed(response):
    global owned
    if '/api/miniclient' not in response.url or response.request.method!='POST':return
    try:
        value=response.json()
        if value.get('clientId','').replace(':','').lower()==identity:owned=value['session']
    except Exception:pass
def wait(test,label,seconds=35):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        if test():return
        page.wait_for_timeout(100)
    raise RuntimeError('Timed out '+label+'; no ordered input replay')
def decoded():return page.evaluate('({frames:DEST.frames,time:videoPlane.currentTime,paused:videoPlane.paused,error:videoPlane.error?.code||null})')
def bundle(data):
    if len(data)>2*1024*1024:raise RuntimeError('Unexpected diagnostic bundle size')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if set(archive.namelist())!={'report.json','hashes.sha256','README.txt'}:raise RuntimeError('Unexpected ZIP entries')
        payload=archive.read('report.json');report=json.loads(payload)
        if hashlib.sha256(payload).hexdigest()+'  report.json' not in archive.read('hashes.sha256').decode():raise RuntimeError('Report hash mismatch')
        if report.get('miniClient',{}).get('connection',{}).get('crypto')!='[redacted]':raise RuntimeError('Native crypto was not wholly redacted')
    return hashlib.sha256(data).hexdigest()
def send(label,expected):
    with page.expect_response(lambda r:'/api/support' in r.url and 'action=report' in r.url and r.request.method=='POST',timeout=30000) as response:
        page.locator('#sendReportServer').click()
    reply=response.value;headers=reply.all_headers()
    # Chromium CDP response.body may UTF-8 transcode an attachment response.
    # Observe the same real fetch's binary ArrayBuffer inside the browser.
    wait(lambda:page.evaluate('DEST.reportBytes!==null'),'browser report bytes')
    data=bytes(page.evaluate('DEST.reportBytes'));page.evaluate('DEST.reportBytes=null')
    if headers.get('x-sagetv-report-save')!=expected:raise RuntimeError('Unexpected real server-save disposition')
    detail=headers.get('x-sagetv-report-detail','')
    if '/opt/sagetv/' in detail or '/mnt/user/' in detail:raise RuntimeError('Failure detail leaked server path')
    digest=bundle(data);(out/(stamp+'-'+label+'.zip')).write_bytes(data)
    rows.append({'gate':label,'passed':True,'saveState':expected,'zipSha256':digest,'cryptoRedacted':True})
    return digest
def listing():
    names=files.listdir(directory)
    if any(not pattern.fullmatch(n) for n in names):raise RuntimeError('Unexpected destination entry; preserve it')
    return names
def remote_hash(name):
    entry=files.lstat(directory+'/'+name)
    if not stat.S_ISREG(entry.st_mode) or entry.st_size>2*1024*1024:raise RuntimeError('Unexpected destination file')
    with files.open(directory+'/'+name,'rb') as stream:return hashlib.sha256(stream.read()).hexdigest()
def restore_directory():
    global obstruction,held
    if obstruction:
        with files.open(directory,'rb') as stream:data=stream.read(256)
        if data!=marker or not stat.S_ISREG(files.lstat(directory).st_mode):raise RuntimeError('Do not remove altered obstruction')
        files.remove(directory);obstruction=False
    if held:files.rename(holding,directory);held=False
try:
    initial=C.activity(cfg)
    if not initial.get('safeToRestart') or mcp('ui.list').get('contexts'):raise RuntimeError('Require independently idle stock232')
    status=support()
    if not(status.get('configured') and status.get('writesEnabled') and status.get('destinationName')=='VibeWebDiagnosticTest' and status.get('spoolFiles')==0):
        raise RuntimeError('Require approved configured destination and empty spool')
    client=C.ssh(cfg);files=client.open_sftp()
    for path in ('/mnt/user/appdata/sagetv-stock-u26-gpu-j11','/mnt/user/appdata/sagetv-stock-u26-gpu-j11/server'):
        if not stat.S_ISDIR(files.lstat(path).st_mode):raise RuntimeError('Reject destination ancestor symlink')
    for path in (directory,holding):
        try:files.lstat(path)
        except FileNotFoundError:pass
        else:raise RuntimeError('Test path already exists; preserve its work')
    pw=sync_playwright().start();browser=pw.chromium.launch(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
    context=browser.new_context(http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block')
    page=context.new_page();page.on('response',observed)
    page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify({player:'hls',videoMode:'transcode',encoder:'qsv',videoKbps:1000,resolution:'480',deinterlace:'on',allowFallback:false}));")
    page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
    wait(lambda:owned and api('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'),'native first UI')
    page.evaluate("window.DEST={frames:0,done:false,reportBytes:null};const original=window.fetch;window.fetch=async(...a)=>{const r=await original(...a);if(r.url.includes('/api/support?action=report'))DEST.reportBytes=Array.from(new Uint8Array(await r.clone().arrayBuffer()));return r};const f=()=>{if(!DEST.done){DEST.frames++;videoPlane.requestVideoFrameCallback(f)}};videoPlane.requestVideoFrameCallback(f)")
    if not mcp('media.watch',context=identity,media_id=20905,wait_ms=0).get('accepted'):raise RuntimeError('One Watch rejected')
    clicked=False
    def moving():
        global clicked
        if page.locator('#autoplayBtn').is_visible() and not clicked:clicked=True;page.locator('#autoplayBtn').click()
        s=decoded();return s['frames']>12 and s['time']>.4 and not s['paused'] and not s['error']
    wait(moving,'actual playback',65)
    page.locator('#settingsToggle').click();page.locator('#settings-tab-diagnostics').click()
    wait(lambda:not page.locator('#sendReportServer').is_disabled(),'enabled destination control')
    profile=page.evaluate("[localStorage.getItem('sagetvWebMiniClientSettings.v1'),localStorage.getItem('sagetvWebStreaming.v1')]")
    configured=api('streamSettings').get('configured')
    with page.expect_response(lambda r:'/api/support' in r.url and 'action=testDestination' in r.url) as response:
        page.locator('#testDiagnosticDestination').click()
    test=response.value.json()
    if not test.get('ok') or test.get('stage')!='complete' or files.listdir(directory):raise RuntimeError('Real bounded test failed or left its temporary probe')
    rows.append({'gate':'real-write-read-hash-delete','passed':True,'temporaryProbeRemoved':True})
    first=send('external-save','external');names=listing()
    if len(names)!=1 or remote_hash(names[0])!=first:raise RuntimeError('Saved ZIP differs from real response')
    known[names[0]]=first
    files.rename(directory,holding);held=True
    with files.open(directory,'wx') as stream:stream.write(marker)
    obstruction=True
    before=decoded();second=send('unavailable-destination-spooled','spooled')
    state=support()
    if state.get('spoolFiles')!=1 or not 0<state.get('spoolBytes',0)<=10*1024*1024:raise RuntimeError('Expected exactly one bounded spool item')
    spooled=[second]
    for index in range(11):
        spooled.append(send('spool-capacity-'+str(index+2),'spooled'))
        state=support()
        if state.get('spoolFiles')!=min(len(spooled),10) or not 0<state.get('spoolBytes',0)<=10*1024*1024:
            raise RuntimeError('Actual spool exceeded its bounded policy')
    rows.append({'gate':'real-spool-prunes-oldest-at-ten','passed':True,'failedWrites':12,'retained':10,'maxBytes':10*1024*1024})
    wait(lambda:decoded()['frames']>before['frames']+8 and decoded()['time']>before['time']+.3 and not decoded()['error'],'playback despite failed destination',12)
    rows.append({'gate':'destination-failure-does-not-stop-playback','passed':True,'before':before,'after':decoded()})
    restore_directory()
    with page.expect_response(lambda r:'/api/support' in r.url and 'action=retrySpool' in r.url) as response:
        page.locator('#retryDiagnosticSpool').click()
    result=response.value.json()
    if result.get('state')!='retried' or 'Moved 10 ' not in result.get('detail','') or support().get('spoolFiles')!=0:raise RuntimeError('Spool retry did not move exactly the owned items')
    names=listing();fresh=[n for n in names if n not in known]
    if len(names)!=11 or len(fresh)!=10 or sorted(remote_hash(n) for n in fresh)!=sorted(spooled[-10:]):raise RuntimeError('Retried ZIP hash mismatch or oldest reports not pruned')
    known.update({n:remote_hash(n) for n in fresh})
    if any(remote_hash(n)!=digest for n,digest in known.items()):raise RuntimeError('External report changed')
    rows.append({'gate':'recover-retry-hash-and-empty-spool','passed':True,'ownedReports':11,'leftoverTemporaryFiles':False})
    if profile!=page.evaluate("[localStorage.getItem('sagetvWebMiniClientSettings.v1'),localStorage.getItem('sagetvWebStreaming.v1')]") or configured!=api('streamSettings').get('configured'):
        raise RuntimeError('Saved browser/native profiles changed')
    rows.append({'gate':'exact-profile-preservation','passed':True});passed=True
except Exception as error:
    failure={'type':type(error).__name__}
    if isinstance(error,RuntimeError):failure['message']=str(error)
finally:
    if files:
        try:restore_directory()
        except Exception:cleanup.append('Approved destination restoration unverified');passed=False
    if owned:
        try:C.request(cfg,'/SageTVWebPlayer/api/miniclient',{'action':'stop','session':owned})
        except Exception:cleanup.append('Exact test UI stop outcome unknown');passed=False
    if context:context.close()
    if browser:browser.close()
    if pw:pw.stop()
    end=time.monotonic()+95
    while identity in mcp('ui.list').get('contexts',[]):
        if time.monotonic()>end:cleanup.append('Owned native UI retirement unverified');passed=False;break
        time.sleep(.3)
    if files and passed:
        try:
            if set(listing())!=set(known):raise RuntimeError('Preserve unexpected destination work')
            for name,digest in known.items():
                if remote_hash(name)!=digest:raise RuntimeError('Preserve changed report')
                files.remove(directory+'/'+name)
            files.rmdir(directory)
            rows.append({'gate':'remove-only-hash-proven-test-reports','passed':True,'reportsRemoved':len(known)})
        except Exception:cleanup.append('Approved test-report cleanup incomplete');passed=False
    if files:files.close()
    if client:client.close()
    path=out/(stamp+'-real-destination.json');path.write_text(json.dumps({'passed':passed,'realStock232':True,'physicalPhone':False,'rows':rows,'failure':failure,'cleanup':cleanup},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':passed,'rows':len(rows),'failure':failure,'cleanup':cleanup,'report':str(path)}))
raise SystemExit(0 if passed else 1)
