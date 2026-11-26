#!/usr/bin/env python3
"""OWN-01 actual stock232 two-browser source/caption/seek/Stop isolation.

Only generated canonical fixtures reset; no household media or profiles.
One QSV transcode and one H264 Copy, not two quality renditions of one client.
"""
import argparse,importlib.util,json,subprocess,sys,time
from pathlib import Path
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright
from bounded_browser_rpc import bounded
from playback_activity import observe_activity
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(s);s.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--coexistence-check',action='store_true',help='Short public-HLS admission while native clients keep playing')
p.add_argument('--source-changes',action='store_true',help='Focused generated recording changes; no multi-client matrix replay')
p.add_argument('--engine',choices=('chromium','webkit'),default='chromium')
a_args=p.parse_args()
if a_args.coexistence_check and a_args.source_changes:p.error('Select one focused gate')
out=ROOT/'artifacts/active'/('WEB-106' if a_args.coexistence_check else 'WP11-008' if a_args.source_changes else 'WP16-006');out.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
report=dict(passed=False,physicalPhone=False,realStock232=True,engine=a_args.engine,rows=[],cleanup=[])
clients=[];browser=pw=None
ids={'da92a86446be','da92a86446bf'}

def mcp(action,**kw):return C.request(cfg,'/v1/control',dict(action=action,**kw),mcp=True,timeout=60 if action=='media.seek' else 30)
def guard():
    # All controls address exact owned ephemeral UIs/canonical generated media.
    # Other clients/recordings are not a reason to abandon owned retirement.
    observe_activity(C.activity(cfg))

class Client:
    def __init__(self,identity,media_id,profile,authority):
        self.identity=identity;self.media_id=media_id;self.owned=None;self.context=None;self.page=None;self.activated=False
        self.native_stop_intent=False;self.session_stop_intent=False
        clients.append(self)
        self.context=browser.new_context(viewport={'width':852,'height':393},service_workers='block',http_credentials={'username':cfg['web_username'],'password':cfg['web_password']})
        self.context.add_init_script("localStorage.setItem('sagetvWebMiniClientId',"+json.dumps(identity.upper())+");localStorage.setItem('sagetvWebStreaming.v1',"+json.dumps(json.dumps(profile))+");localStorage.setItem('sagetvWebCaptionAuthority.v1',"+json.dumps(json.dumps(authority))+");")
        self.page=self.context.new_page();original=self.page.evaluate
        self.page.evaluate=lambda *args,**kwargs:bounded(original,*args,**kwargs)
        self.page.on('response',self.observed)
        self.page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
        self.wait(lambda:self.owned and self.api('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'),'native first frame')
        self.configured=self.api('streamSettings').get('configured')
        self.saved=self.page.evaluate("['sagetvWebMiniClientSettings.v1','sagetvWebStreaming.v1','sagetvWebCaptionAuthority.v1'].map(k=>localStorage.getItem(k))")
        self.page.evaluate("()=>{const s=window.__isolation={frames:0,source:'',done:false,player:null};const original=SageMiniPlayback.prototype.start;SageMiniPlayback.prototype.start=function(...args){s.player=this;return original.apply(this,args)};function f(){const source=videoPlane.currentSrc;videoPlane.requestVideoFrameCallback(()=>{if(s.done)return;if(source&&source===videoPlane.currentSrc){s.frames++;s.source=source}f()})}f();return true}")
    def observed(self,response):
        if '/api/miniclient' not in response.url or response.request.method!='POST':return
        try:
            r=response.json()
            if r.get('clientId','').replace(':','').lower()==self.identity and r.get('session'):self.owned=r['session']
        except Exception:pass
    def api(self,action):return C.request(cfg,'/SageTVWebPlayer/api/miniclient?'+urlencode(dict(action=action,session=self.owned)))
    def sample(self):return self.page.evaluate("()=>{const s=__isolation,v=videoPlane,clock=s.player?.snapshot();const c=fileSubtitleCanvas,p=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let pixels=0;for(let i=3;i<p.length;i+=4)if(p[i])pixels++;return{time:v.currentTime,frames:s.frames,current:s.source===v.currentSrc,ready:v.readyState,paused:v.paused,error:v.error?.code||null,prompt:!autoplayBtn.hidden,textLength:localCaptions.textContent.trim().length,fileBitmapPixels:pixels,absoluteTimeMs:clock?.timeMs,recoveries:clock?.recoveries,clockRegressions:clock?.clockRegressions}}")
    def wait(self,check,label,seconds=45):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            if check():return
            self.page.wait_for_timeout(120)
        raise RuntimeError('Timed out '+label+'; no replay')
    def moving(self):
        before=self.sample()
        def check():
            value=self.sample()
            if value['error']:raise RuntimeError('Actual browser media error')
            if value['prompt'] and not self.activated:self.page.locator('#autoplayBtn').click();self.activated=True
            return value['current'] and value['frames']>before['frames']+8 and not value['paused'] and value['ready']>=2
        self.wait(check,'new decoded frames',60)
    def watch(self):
        guard()
        if not mcp('media.clear_watched',media_id=self.media_id,confirm='true').get('ok'):raise RuntimeError('Generated fixture reset rejected')
        if not mcp('media.watch',context=self.identity,media_id=self.media_id,wait_ms=0).get('accepted'):raise RuntimeError('One Watch rejected')
        self.moving()
    def seek(self,target):
        guard();old=self.api('streamSettings').get('session')
        if not mcp('media.seek',context=self.identity,target_ms=target).get('accepted'):raise RuntimeError('One Seek rejected')
        self.wait(lambda:self.api('streamSettings').get('session')!=old,'owned replacement')
        self.moving()
    def profiles(self):
        return self.configured==self.api('streamSettings').get('configured') and self.saved==self.page.evaluate("['sagetvWebMiniClientSettings.v1','sagetvWebStreaming.v1','sagetvWebCaptionAuthority.v1'].map(k=>localStorage.getItem(k))")
    def retire(self):
        if not self.owned:return
        guard()
        if mcp('ui.state',context=self.identity).get('fullyLoaded'):
            if self.native_stop_intent:raise RuntimeError('Owned native Stop receipt unknown; do not replay')
            self.native_stop_intent=True
            if not mcp('media.control',context=self.identity,operation='stop').get('accepted'):raise RuntimeError('Owned native Stop rejected')
        if self.session_stop_intent:raise RuntimeError('Owned UI Stop receipt unknown; do not replay')
        self.session_stop_intent=True
        if not C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action='stop',session=self.owned)).get('ok'):raise RuntimeError('Owned UI Stop rejected')
        self.owned=None
        if self.context:self.context.close();self.context=None

try:
    guard()
    existing=mcp('ui.list')
    if existing.get('ok') is not True or not isinstance(existing.get('contexts'),list):raise RuntimeError('Existing UI identities unknown')
    if ids.intersection(existing['contexts']):raise RuntimeError('Exact field client identity already in use; do not take it over')
    for path,expected in [('/var/media/OpenSageTV_Vibe_Tests/VibeCaptionTest-1080i-CEA608-90s-2s.ts',20905),('/var/media/OpenSageTV_Vibe_Tests/WP06-VobSub/VibeVobSubExternal-P06.ts',78951)]:
        if mcp('media.resolve_exact_path',path=path).get('mediaFileId')!=expected:raise RuntimeError('Generated canonical fixture changed')
    if a_args.source_changes:
        if mcp('media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/WP12-Audio-PMT/VibeAudio-PMT-Mono-to-51.ts').get('mediaFileId')!=84231:raise RuntimeError('Generated PMT fixture changed')
    pw=sync_playwright().start()
    if a_args.engine=='webkit':subprocess.run(['bash','/workspace/release-manifest/scripts/prepare-headless-audio.sh'],check=True,timeout=15)
    browser=pw.webkit.launch(headless=True) if a_args.engine=='webkit' else pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
    a=Client('da92a86446be',20905,dict(player='hls',videoMode='transcode',encoder='qsv',resolution='480',videoKbps=1000,captions='608',audioCodec='aac'),dict(mode='cc1',cc1Type='cea608',cc1Language='eng'))
    a.watch();a.wait(lambda:a.sample()['textLength']>0,'actual local CEA')
    if a_args.source_changes:
        for mid in (84231,20905):
            previous=a.api('streamSettings').get('session');a.media_id=mid;a.watch()
            first=a.sample();a.page.wait_for_timeout(5000);last=a.sample()
            native=mcp('ui.state',context=a.identity)
            if a.api('streamSettings').get('session')==previous or (native.get('media') or {}).get('mediaFileId')!=mid or last['frames']<=first['frames']+20 or last['time']<=first['time']+2 or last['error']:
                raise RuntimeError('Source change did not present new owned output')
            raw=native.get('rawMediaTimeMs');absolute=last.get('absoluteTimeMs')
            if type(raw) not in (int,float) or type(absolute) not in (int,float) or abs(raw-absolute)>2000 or last.get('recoveries')!=0 or last.get('clockRegressions')!=0:
                raise RuntimeError('New source presentation/native clock or recovery differs')
            try:
                old=C.request(cfg,'/SageTVWebPlayer/api/hls?'+urlencode(dict(session=previous)))
                if old.get('running'):raise RuntimeError('Old source retained its encoder')
            except RuntimeError as error:
                if not str(error).startswith('HTTP 404: HLS session not found'):raise
            if mid==20905:a.wait(lambda:a.sample()['textLength']>0,'new source CEA returns')
            elif a.sample()['textLength']:raise RuntimeError('Old source captions survived onto uncaptained source')
            if not a.profiles():raise RuntimeError('Source change mutated saved profiles')
            report['rows'].append(dict(gate='recording-change-new-producer-frames-caption-owner-and-profiles',passed=True,mediaId=mid,first=first,last=last,nativeFileTimeMs=raw,clockDifferenceMs=raw-absolute))
    else:
        b=Client('da92a86446bf',78951,dict(player='hls',videoMode='copy',encoder='software',resolution='source',deinterlace='off',allowFallback=False,audioCodec='aac',subtitleMode='track',subtitleTrack=128,subtitleLanguage='eng'),dict(mode='off'))
        b.watch();baseline=b.sample();b_producer=b.api('streamSettings').get('session')
        if a_args.coexistence_check:
            first=a.sample();producer=a.api('streamSettings').get('session')
            child=subprocess.run([sys.executable,str(ROOT/'tests/stock-long-recording-field.py'),'--engine',a_args.engine,'--profile-smoke','--require-other-client'],capture_output=True,text=True,timeout=120)
            summary=json.loads(child.stdout.strip().splitlines()[-1])
            if child.returncode or not summary.get('passed') or not summary.get('coTenancyObserved') or summary.get('resourceScope')!='shared-server':raise RuntimeError('Short public-HLS coexistence admission failed')
            a.moving();b.moving()
            if a.api('streamSettings').get('session')!=producer or b.api('streamSettings').get('session')!=b_producer or not a.profiles() or not b.profiles():raise RuntimeError('Coexisting playback disturbed existing sources/profiles')
            report['rows'].append(dict(gate='public-HLS-short-consumer-admits-active-native-clients-and-retires-only-itself',passed=True,child=summary,first=first,last=a.sample()))
        else:
            a.seek(30000)
            b.wait(lambda:b.sample()['frames']>baseline['frames']+8 and b.sample()['time']>baseline['time']+.3,'other client survives seek',15)
            if b.api('streamSettings').get('session')!=b_producer:raise RuntimeError('Other producer replaced by first seek')
            report['rows'].append(dict(gate='client-A-seek-keeps-B-producer-and-new-pictures',passed=True))
            b.seek(100000);b.wait(lambda:b.sample()['fileBitmapPixels']>100,'actual file bitmap',15)
            aa=a.sample();bb=b.sample()
            if aa['textLength']<=0 or aa['fileBitmapPixels'] or bb['textLength'] or bb['fileBitmapPixels']<=100:raise RuntimeError('Visible caption ownership crossed clients')
            report['rows'].append(dict(gate='simultaneous-distinct-CEA-and-genuine-VobSub-surfaces',passed=True,cea=aa,fileBitmap=bb))
            if not a.profiles() or not b.profiles():raise RuntimeError('Saved/configured profile changed')
            report['rows'].append(dict(gate='both-independent-saved-and-configured-profiles',passed=True))
            b_producer=b.api('streamSettings').get('session');baseline=b.sample();a.retire()
            b.wait(lambda:b.sample()['frames']>baseline['frames']+10 and b.sample()['time']>baseline['time']+.4,'other client survives Stop',10)
            if b.api('streamSettings').get('session')!=b_producer or mcp('ui.state',context=b.identity).get('media',{}).get('mediaFileId')!=78951:raise RuntimeError('First Stop retired second source')
            report['rows'].append(dict(gate='client-A-Stop-keeps-B-source-producer-and-new-pictures',passed=True))
    report['passed']=True
except Exception as e:
    report['failure']=dict(type=type(e).__name__,message=str(e)[:200] if isinstance(e,RuntimeError) else 'Bounded field observation failed')
finally:
    for c in reversed(clients):
        try:c.retire()
        except Exception:report['cleanup'].append('Exact owned client retirement unknown: '+c.identity)
    if browser:
        try:bounded(browser.close)
        except Exception:report['cleanup'].append('Browser cleanup unknown')
    if pw:
        try:bounded(pw.stop)
        except Exception:report['cleanup'].append('Driver cleanup unknown')
    end=time.monotonic()+95
    while time.monotonic()<end:
        if not ids.intersection(mcp('ui.list').get('contexts',[])):break
        time.sleep(.3)
    else:report['cleanup'].append('Owned UI retirement not independently confirmed')
    report['passed']=report['passed'] and not report['cleanup']
    path=out/(stamp+('-source-changeover' if a_args.source_changes else '-two-client-captions')+'.json');path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=report['passed'],rows=len(report['rows']),path=str(path),failure=report.get('failure'),cleanup=report['cleanup'])),flush=True)
raise SystemExit(0 if report['passed'] else 1)
