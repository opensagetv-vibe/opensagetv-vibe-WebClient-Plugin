#!/usr/bin/env python3
"""Genuine IDX/SUB/IFO over an owned generated A/V fixture, stock232.

Actual production extraction/canvas/frames; no physical-phone/audio claim.
One Watch, one Seek, no replay, exact owned retirement and saved profile checks.
"""
import argparse,hashlib,importlib.util,json,time,stat
from pathlib import Path
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C);cfg=C.configuration()
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--engine',choices=('webkit','chromium'),default='webkit');p.add_argument('--case',choices=('normal','forced','missing'),default='normal');a=p.parse_args()
OUT=ROOT/'artifacts/active/WP06-004';OUT.mkdir(parents=True,exist_ok=True)
stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());identity='da92a86446be';owned=None;browser=context=page=pw=None;renamed=False
passed=False;rows=[];errors=[];cleanup=[];observed=[];failure=None;palette_restored=False
base='/mnt/user/sagemedia/OpenSageTV_Vibe_Tests/WP06-VobSub/VibeVobSubExternal-P06';ifo=base+'.ifo';held=ifo+'.palette-disabled'
def guard_fixture_ancestors(ftp):
 for parent in ('/mnt','/mnt/user','/mnt/user/sagemedia','/mnt/user/sagemedia/OpenSageTV_Vibe_Tests','/mnt/user/sagemedia/OpenSageTV_Vibe_Tests/WP06-VobSub'):
  if not stat.S_ISDIR(ftp.lstat(parent).st_mode):raise RuntimeError('Refuse test-fixture symlink traversal')
def mcp(action,**v):return C.request(cfg,'/v1/control',dict(action=action,**v),mcp=True,timeout=60 if action=='media.seek' else 20)
def api(action,**v):return C.request(cfg,'/SageTVWebPlayer/api/miniclient'+('?' +urlencode(dict(action=action,session=owned,**v))),timeout=20)
def wait(test,label,seconds=45):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  if test():return
  page.wait_for_timeout(100)
 raise RuntimeError('Timed out: '+label)
def observe(response):
 global owned
 try:
  if '/api/miniclient' in response.url and response.request.method=='POST':
   data=response.json()
   if data.get('session') and data.get('clientId','').replace(':','').lower()==identity:owned=data['session']
  elif '/api/subtitles' in response.url:
   data=response.json()
   if data.get('scope')=='file':
    ordinary=data.get('ordinary');cues=data.get('cues',[])
    observed.append(dict(ordinary=ordinary,cues=[dict(ptsMs=q.get('ptsMs'),clear=q.get('clear'),bytes=len(q.get('data','')),owner=q.get('owner')) for q in cues[:8]]));del observed[:-100]
 except Exception:pass
def picture():return page.evaluate("()=>{const v=videoPlane,c=fileSubtitleCanvas,p=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let visible=0;for(let i=3;i<p.length;i+=4)if(p[i])visible++;return{time:v.currentTime,frames:P06.frames,last:P06.last,current:P06.source===v.currentSrc,paused:v.paused,width:v.videoWidth,error:v.error?.code||null,prompt:!autoplayBtn.hidden,pixels:visible}}")
def moving(label):
 activated=False;before=picture();end=time.monotonic()+45
 while time.monotonic()<end:
  v=picture()
  if v['error']:raise RuntimeError('Browser decoder error')
  if v['prompt'] and not activated:page.locator('#autoplayBtn').click();activated=True
  if v['current'] and not v['paused'] and v['frames']>=before['frames']+8 and v['last']>before['last']+.1:rows.append(dict(gate=label,passed=True,video=v));return
  page.wait_for_timeout(100)
 raise RuntimeError('No fresh moving pictures: '+label)
try:
 idle_deadline=time.monotonic()+30
 while True:
  activity=C.activity(cfg);uis=mcp('ui.list').get('contexts',[])
  if activity.get('recordingCount')!=0 or activity.get('connectedClientCount')!=0 or uis not in ([],[identity]):raise RuntimeError('Independent idle required; unrelated activity preserved')
  if not uis:break
  if time.monotonic()>=idle_deadline:raise RuntimeError('Previous exact test UI has not retired; no takeover')
  time.sleep(.4)
 source=mcp('media.resolve_exact_path',path='/var/media/OpenSageTV_Vibe_Tests/WP06-VobSub/VibeVobSubExternal-P06.ts')
 if source.get('mediaFileId')!=78951:raise RuntimeError('Exact owned fixture changed')
 if a.case=='missing':
  with C.ssh(cfg) as client:
   with client.open_sftp() as ftp:
    guard_fixture_ancestors(ftp)
    if not stat.S_ISREG(ftp.lstat(ifo).st_mode):raise RuntimeError('Exact fixture IFO required')
    with ftp.open(ifo,'rb') as stream:digest=hashlib.sha256(stream.read()).hexdigest()
    if digest!='1575c66c281bee964c039380f5851473f215672889bb51fafa085a80cd2ba75f':raise RuntimeError('Canonical IFO hash changed')
    try:ftp.lstat(held)
    except FileNotFoundError:pass
    else:raise RuntimeError('Previous test palette move unresolved')
    ftp.rename(ifo,held);renamed=True
 pw=sync_playwright().start();browser=pw.webkit.launch(headless=True) if a.engine=='webkit' else pw.chromium.launch(headless=True,executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
 context=browser.new_context(viewport={'width':852,'height':393},http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block')
 profile=dict(player='hls',videoMode='copy',encoder='software',resolution='source',deinterlace='off',allowFallback=False,audioCodec='aac',subtitleMode='track' if a.case=='normal' else 'auto',subtitleTrack=128,subtitleLanguage='eng',subtitleForcedOnly=a.case=='forced')
 context.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');localStorage.setItem('sagetvWebStreaming.v1',"+json.dumps(json.dumps(profile))+");")
 page=context.new_page();page.on('response',observe);page.on('pageerror',lambda e:errors.append(type(e).__name__))
 page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html',wait_until='domcontentloaded')
 wait(lambda:owned and api('status').get('connection',{}).get('startupEvents',{}).get('firstFrameCompleted'),'owned first frame')
 native_before=api('streamSettings').get('configured');saved_before=page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')")
 page.evaluate("()=>{const s=window.P06={frames:0,last:0,source:''};function arm(){const source=videoPlane.currentSrc;videoPlane.requestVideoFrameCallback((n,m)=>{if(source&&source===videoPlane.currentSrc){s.frames++;s.last=m.mediaTime;s.source=source}arm()})}arm()}")
 if not mcp('media.watch',context=identity,media_id=78951,wait_ms=0).get('accepted'):raise RuntimeError('One Watch rejected')
 moving('original-owned-fixture-playback')
 layout=api('contentState',mediaId=78951).get('layout')
 if layout=='preview':
  if not C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action='showContent',session=owned,mediaId=78951)).get('ok'):raise RuntimeError('One qualified fullscreen action rejected')
 elif layout!='fullscreen':raise RuntimeError('Unknown native layout; no guessed TV toggle')
 wait(lambda:api('contentState',mediaId=78951).get('layout')=='fullscreen','qualified native fullscreen')
 rows.append(dict(gate='qualified-fullscreen-no-Watch-replay',passed=True))
 old=api('streamSettings').get('session')
 page.evaluate('()=>{P06.frames=0;P06.last=0;P06.source=""}')
 if not mcp('media.seek',context=identity,target_ms=100000).get('accepted'):raise RuntimeError('One Seek rejected')
 wait(lambda:api('streamSettings').get('session')!=old,'new producer');moving('new-seek-source-pictures')
 if a.case=='normal':
  wait(lambda:picture()['pixels']>100,'genuine visible VobSub',20);rows.append(dict(gate='genuine-palette-visible',passed=True,video=picture()))
  page.screenshot(path=str(OUT/(stamp+'-'+a.engine+'-genuine-visible.png')))
  wait(lambda:picture()['pixels']==0,'authored natural clear',5);rows.append(dict(gate='authored-natural-clear',passed=True,video=picture()))
  cue_times=[q['ptsMs'] for item in observed for q in item['cues'] if q['bytes']>0]
  if not any(abs(t-103603)<=1 for t in cue_times if isinstance(t,int)):raise RuntimeError('Genuine original file cue time missing')
 elif a.case=='forced':
  start=picture()['last'];wait(lambda:picture()['last']>start+5,'forced-only advancing pictures',15)
  states=[r['ordinary'] for r in observed if r['ordinary']]
  if not states or not any(r.get('complete') and r.get('cues')==0 and not r.get('error') for r in states) or picture()['pixels']!=0:raise RuntimeError('Forced-only did not filter unforced sample')
  rows.append(dict(gate='actual-unforced-sample-filtered-with-moving-AV',passed=True))
 else:
  start=picture()['last'];wait(lambda:picture()['last']>start+5,'missing-palette moving AV',15)
  settings=api('streamSettings');text=json.dumps(settings)
  if 'VobSub unavailable' not in text or 'palette unavailable' not in text or picture()['pixels']!=0:raise RuntimeError('Missing palette did not remain explicit/AV-safe')
  rows.append(dict(gate='missing-palette-explicit-no-working-track-AV-preserved',passed=True))
 if api('streamSettings').get('configured')!=native_before or page.evaluate("localStorage.getItem('sagetvWebStreaming.v1')")!=saved_before:raise RuntimeError('Saved/native profile changed')
 if errors:raise RuntimeError('Browser script error')
 rows.append(dict(gate='saved-native-profiles-preserved',passed=True));passed=True
except Exception as e:
 failure=dict(type=type(e).__name__,message=str(e)[:220] if isinstance(e,RuntimeError) else 'Bounded field observation failed')
 if page:
  try:
   failure['video']=picture();settings=api('streamSettings');active=settings.get('active') or {}
   failure['effective']=active.get('effective');failure['source']=active.get('source');failure['filePolls']=len(observed)
   failure['ordinary']=[dict((k,(r['ordinary'] or {}).get(k)) for k in ('active','complete','mode','trackIndex','cues','bytes','error','decoder')) for r in observed[-3:]]
   producer=settings.get('session')
   if producer:
    hls=C.request(cfg,'/SageTVWebPlayer/api/hls?'+urlencode(dict(action='status',session=producer)))
    failure['subtitleQueues']=hls.get('subtitleQueues');failure['playbackToken']=hls.get('playbackToken')
   failure['cueTimes']=[q for r in observed for q in r['cues']][-12:]
  except Exception:failure['diagnosticUnavailable']=True
  try:page.screenshot(path=str(OUT/(stamp+'-'+a.engine+'-'+a.case+'-failure.png')))
  except Exception:pass
finally:
 if owned:
  try:
   if not C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action='stop',session=owned)).get('ok'):cleanup.append('Exact Stop not acknowledged')
  except Exception:cleanup.append('Stop unknown, not replayed')
 if context:context.close()
 if browser:browser.close()
 if pw:pw.stop()
 end=time.monotonic()+90
 while time.monotonic()<end:
  try:
   if identity not in mcp('ui.list').get('contexts',[]):break
  except Exception:
   cleanup.append('Native UI retirement query unavailable; not idle proof');break
  time.sleep(.3)
 else:cleanup.append('Native UI not retired')
 if renamed:
  try:
   with C.ssh(cfg) as client:
    with client.open_sftp() as ftp:
     guard_fixture_ancestors(ftp)
     try:ftp.lstat(ifo)
     except FileNotFoundError:pass
     else:raise RuntimeError('Refuse overwriting a concurrent IFO')
     with ftp.open(held,'rb') as stream:digest=hashlib.sha256(stream.read()).hexdigest()
     if digest!='1575c66c281bee964c039380f5851473f215672889bb51fafa085a80cd2ba75f':raise RuntimeError('Held IFO changed')
     ftp.rename(held,ifo)
     with ftp.open(ifo,'rb') as stream:restored_hash=hashlib.sha256(stream.read()).hexdigest()
     if restored_hash!=digest:raise RuntimeError('Restored IFO readback mismatch')
     palette_restored=True
  except Exception:cleanup.append('Exact canonical IFO restoration unverified; inspect held path')
 result=dict(passed=passed and not cleanup,engine=a.engine,case=a.case,realStock232=True,physicalIPhone=False,genuineExternalSubtitle=True,generatedAVFixture=True,fixturePaletteRestored=palette_restored if renamed else None,rows=rows,errors=errors,cleanup=cleanup,failure=failure)
 with (OUT/(stamp+'-'+a.engine+'-'+a.case+'-stock-vobsub.json')).open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
 print(json.dumps(result),flush=True)
raise SystemExit(0 if result['passed'] else 1)
