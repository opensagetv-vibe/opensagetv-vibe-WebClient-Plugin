#!/usr/bin/env python3
"""Interactive stock232 Web Client commissioning through its real browser UI.

No Core changes, private controls, arbitrary API/eval or credential logging.
Commands on stdin are JSON: key, command, click, text, wait, shot, quit.
The exact owned MiniClient is retired in finally, including failed gates.
"""
import importlib.util,json,sys,time,os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('commission',ROOT/'scripts/commission-mobile.py')
commission=importlib.util.module_from_spec(spec);spec.loader.exec_module(commission)
cfg=commission.configuration()
engine=os.environ.get('SAGETV_BROWSER_ENGINE','chromium')
if engine not in ('chromium','webkit'):raise SystemExit('Unsupported test browser')
viewport=os.environ.get('SAGETV_BROWSER_VIEWPORT','1280x800')
if viewport not in ('1280x800','852x393','393x852','320x568'):raise SystemExit('Unsupported test viewport')
vw,vh=map(int,viewport.split('x'))
auto_ui=os.environ.get('SAGETV_BROWSER_AUTO_UI')=='1'
trace_gfx=os.environ.get('SAGETV_BROWSER_GFX_TRACE')=='1'
trace_timeline=os.environ.get('SAGETV_BROWSER_TIMELINE_TRACE')=='1'
before=commission.activity(cfg)
if not before.get('safeToRestart'):
    contexts=commission.request(cfg,'/v1/control',{'action':'ui.list'},mcp=True).get('contexts')
    if before.get('recordingCount')!=0 or before.get('connectedClientCount')!=0 or contexts!=['da92a86446be']:
        raise SystemExit('Commissioning requires idle server or only its exact owned test UI')
OUT=Path(os.environ.get('SAGETV_ARTIFACT_DIR',ROOT/'artifacts/active/WEB-019')).resolve()
if not OUT.is_relative_to((ROOT/'artifacts/active').resolve()):
    raise SystemExit('Commissioning captures must remain in project artifacts/active/<task>')
OUT.mkdir(parents=True,exist_ok=True)
owned=None;browser=None;counter=0
def respond(value):print(json.dumps(value),flush=True)
def observed(response):
    global owned
    if '/api/miniclient' not in response.url or response.request.method!='POST':return
    try:
        data=response.json()
        if data.get('session') and data.get('clientId','').replace(':','').lower()=='da92a86446be':owned=data['session']
    except Exception:pass
try:
  with sync_playwright() as pw:
    options={'headless':True}
    if engine=='chromium':options.update(executable_path='/usr/local/bin/vibe-chromium',args=['--no-sandbox'])
    browser=getattr(pw,engine).launch(**options)
    context=browser.new_context(viewport={'width':vw,'height':vh},device_scale_factor=3 if auto_ui else 1,http_credentials={'username':cfg['web_username'],'password':cfg['web_password']},service_workers='block')
    page=context.new_page();page.on('response',observed);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    if os.environ.get('SAGETV_BROWSER_SOURCE_JS')=='1':
        # Opt-in same-origin test context only, never a deployed-file edit.
        page.route(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/js/miniclient.js*',lambda route:route.fulfill(path=str(ROOT/'src/main/webapp/js/miniclient.js'),content_type='application/javascript'))
    page.add_init_script("localStorage.setItem('sagetvWebMiniClientId','DA92A86446BE');")
    if trace_timeline:
        # Isolated browser storage only. Exercise the phone's HLS production
        # path; do not silently benchmark the Auto continuous-TS choice.
        page.add_init_script("localStorage.setItem('sagetvWebStreaming.v1',JSON.stringify({player:'hls',videoMode:'transcode',videoKbps:1000,resolution:'480',deinterlace:'on'}));localStorage.setItem('sagetvWebMiniClientSettings.v1',JSON.stringify({mute:true}));")
        page.add_init_script("""(()=>{window.TIMELINE_TRACE=[];const original=window.fetch;
          window.fetch=async function(input,init){const u=String(input),body=String(init&&init.body||''),t=performance.now();
            const action=new URL(u,location.href).searchParams.get('action');
            if(u.includes('api/miniclient')&&['click','mouse','seek'].includes(action)){
              const row={action,start:t,body};TIMELINE_TRACE.push(row);
              try{const r=await original.apply(this,arguments);row.ack=performance.now();row.status=r.status;return r;}
              catch(e){row.failed=performance.now();throw e;}}
            const r=await original.apply(this,arguments);
            if(u.includes('api/hls?')&&TIMELINE_TRACE.length<128)r.clone().json().then(s=>TIMELINE_TRACE.push({action:'hls-status',start:t,ack:performance.now(),producerAgeMs:s.producerAgeMs,firstSegmentMs:s.firstSegmentMs,segments:s.segments,sourceProbeMs:s.sourceProbeMs})).catch(()=>{});
            return r;};
          const read=ReadableStreamDefaultReader.prototype.read,decoder=new TextDecoder();let pending='';
          ReadableStreamDefaultReader.prototype.read=async function(...a){const r=await read.apply(this,a);
            if(r.value){pending+=decoder.decode(r.value,{stream:true});if(pending.length>16*1024*1024)pending='';let i;
              while((i=pending.indexOf('\\n'))>=0){const line=pending.slice(0,i);pending=pending.slice(i+1);try{const e=JSON.parse(line);if(['videoStart','videoStop','media'].includes(e.type)&&TIMELINE_TRACE.length<128)TIMELINE_TRACE.push({action:'event-'+e.type,start:performance.now(),target:e.startSeconds,media:e.action});}catch(_){}}}
            return r;};})()""")
    if trace_gfx:
        # Count only this owned browser's incoming GFX; bounded header samples,
        # no image payloads, credentials or changes to the ordered event stream.
        page.add_init_script(r"""(()=>{const t=window.GFX_TRACE={commands:{},blend:{},samples:[],pending:'',seen:0};
          const decoder=new TextDecoder(),read=ReadableStreamDefaultReader.prototype.read;
          ReadableStreamDefaultReader.prototype.read=async function(...a){const r=await read.apply(this,a);
            if(r.value&&r.value.byteLength&&t.seen<20000){t.pending+=decoder.decode(r.value,{stream:true});
              if(t.pending.length>16*1024*1024){t.pending='';return r}let i;
              while((i=t.pending.indexOf('\n'))>=0){let line=t.pending.slice(0,i);t.pending=t.pending.slice(i+1);
                try{let e=JSON.parse(line);if(e.type!=='gfx')continue;t.seen++;t.commands[e.cmd]=(t.commands[e.cmd]||0)+1;
                  if(e.cmd===24){let b=Uint8Array.from(atob(e.payload),c=>c.charCodeAt(0)),v=new DataView(b.buffer),n=[];
                    for(let k=4;k<44&&k+4<=b.length;k+=4)n.push(v.getInt32(k));let color=(n[9]>>>0).toString(16);
                    if(Object.keys(t.blend).length<64||t.blend[color])t.blend[color]=(t.blend[color]||0)+1;
                    if(t.samples.length<128)t.samples.push(n)}
                }catch(_){}}
            }return r};})()""")
    page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html'+('' if auto_ui else '?ui=1280x720'),wait_until='domcontentloaded')
    page.wait_for_timeout(3000)
    respond({'ready':True,'version':commission.request(cfg,'/SageTVWebPlayer/api/health').get('version')})
    for line in sys.stdin:
      try:
        item=json.loads(line);action=item.get('action')
        if action=='quit':break
        if action=='key':
            key=item.get('key','')
            if key not in ['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Enter','Escape','Home','PageUp','PageDown','i','o','g','r']:raise ValueError('Unknown remote key')
            page.locator('#stage').focus();page.keyboard.press(key)
        elif action=='command':
            command=int(item['command'])
            if command not in [2,3,4,5,6,7,8,9,10,15,18,20,24,27,28,29,41,55,56,60,61,62,65,66,67,75,86,89]:raise ValueError('Unknown stock command')
            if not owned:raise ValueError('No owned native client')
            commission.request(cfg,'/SageTVWebPlayer/api/miniclient',{'action':'command','session':owned,'command':command})
        elif action=='click':
            target=page.locator(item['selector']);position=item.get('position')
            if position is not None:
                if not isinstance(position,dict) or set(position)!=set(('x','y')):raise ValueError('Explicit x/y point required')
                bounds=target.bounding_box()
                if not bounds or any(type(position[k]) not in (int,float) or not 0<=position[k]<bounds['width' if k=='x' else 'height'] for k in ('x','y')):raise ValueError('Point outside visible target')
                target.click(position=position,timeout=5000)
            else:target.click(timeout=5000)
        elif action=='watch-fixture':
            if not trace_timeline or not owned:raise ValueError('Explicit timeline trace required')
            media=commission.request(cfg,'/v1/control',{'action':'media.resolve_exact_path','path':'/var/media/OpenSageTV_Vibe_Tests/VibeCaptionTest-1080i-CEA608-90s-2s.ts'},mcp=True)
            if not media.get('mediaFileId'):raise ValueError('Canonical fixture missing')
            commission.request(cfg,'/v1/control',{'action':'media.clear_watched','media_id':media['mediaFileId'],'confirm':'true'},mcp=True)
            commission.request(cfg,'/v1/control',{'action':'media.watch','context':'da92a86446be','media_id':media['mediaFileId'],'wait_ms':0},mcp=True)
            commission.request(cfg,'/v1/control',{'action':'media.seek','context':'da92a86446be','target_ms':0},mcp=True)
            page.wait_for_function('videoPlane.videoWidth>0&&videoPlane.currentTime>.3&&!videoPlane.paused',timeout=90000)
        elif action in ('stage-click','timeline-click'):
            x=max(0,min(1279,float(item['x'])));y=max(0,min(719,float(item['y'])))
            if action=='timeline-click':
                if not trace_timeline:raise ValueError('Explicit timeline trace required')
                page.evaluate("()=>{TIMELINE_TRACE.length=0;window.TIMELINE_SAMPLES=[];window.TIMELINE_T0=performance.now();window.TIMELINE_TIMER=setInterval(()=>{const v=videoPlane;TIMELINE_SAMPLES.push({ms:performance.now()-TIMELINE_T0,time:v.currentTime,src:v.currentSrc,ready:v.readyState,paused:v.paused,frames:v.getVideoPlaybackQuality?v.getVideoPlaybackQuality().totalVideoFrames:null});},25)}")
            page.locator('#gfxCanvas').click(position={'x':x,'y':y},timeout=5000)
            if action=='timeline-click':
                page.wait_for_timeout(12000)
                trace=page.evaluate("()=>{clearInterval(TIMELINE_TIMER);return{inputs:TIMELINE_TRACE.map(r=>({...r,start:r.start-TIMELINE_T0,ack:r.ack==null?null:r.ack-TIMELINE_T0})),samples:TIMELINE_SAMPLES,stats:document.getElementById('stats').textContent}}")
                trace_path=OUT/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-timeline.json')
                trace_path.write_text(json.dumps(trace,indent=2)+'\n',encoding='utf-8')
                respond({'timelineTrace':str(trace_path.relative_to(ROOT)),'inputs':trace['inputs']})
        elif action=='text':page.locator(item['selector']).fill(str(item['text']),timeout=5000)
        elif action=='wait':page.wait_for_timeout(max(0,min(10,float(item.get('seconds',1))))*1000)
        elif action=='viewport':
            size=item.get('size')
            if size not in ('1280x800','852x393','393x852','320x568'):raise ValueError('Unsupported test viewport')
            vw,vh=map(int,size.split('x'));page.set_viewport_size({'width':vw,'height':vh})
        elif action not in ['shot','status','render-info']:raise ValueError('Unknown commissioning action')
        page.wait_for_timeout(700);counter+=1
        path=OUT/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-field-'+str(counter)+'.png')
        page.screenshot(path=str(path))
        uis=commission.request(cfg,'/v1/control',{'action':'ui.list'},mcp=True)
        states=[commission.request(cfg,'/v1/control',{'action':'ui.state','context':name},mcp=True) for name in uis.get('contexts',[]) if name.replace(':','').lower()=='da92a86446be']
        state=commission.request(cfg,'/SageTVWebPlayer/api/miniclient?action=status&session='+owned) if action=='status' and owned else None
        result={'capture':str(path.relative_to(ROOT)),'ui':states,'ownedSession':bool(owned),'errors':errors[-5:],'nativeState':state}
        if action=='render-info':
            result['render']=page.evaluate("""()=>({viewport:[innerWidth,innerHeight,devicePixelRatio],canvas:[gfxCanvas.width,gfxCanvas.height],trace:window.GFX_TRACE?{commands:GFX_TRACE.commands,blend:GFX_TRACE.blend,samples:GFX_TRACE.samples,seen:GFX_TRACE.seen}:null,stats:document.getElementById('stats').textContent})""")
            result['browserMedia']=page.evaluate("""()=>({hlsVersion:window.Hls&&Hls.version,hlsSupported:!!(window.Hls&&Hls.isSupported()),mse:!!window.MediaSource,
                nativeHls:videoPlane.canPlayType('application/vnd.apple.mpegurl'),avc:videoPlane.canPlayType('video/mp4;codecs="avc1.42E01E"'),
                error:videoPlane.error?{code:videoPlane.error.code,message:videoPlane.error.message}:null,
                revision:[...document.scripts].map(s=>new URL(s.src).pathname).filter(s=>s.includes('hls'))})""")
            result['stv']=commission.request(cfg,'/v1/control',{'action':'captions.get','context':'da92a86446be'},mcp=True)
            path.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        respond(result)
      except Exception as error:respond({'error':str(error)[:500]})
    context.close();browser.close();browser=None
finally:
    if owned:
        try:commission.request(cfg,'/SageTVWebPlayer/api/miniclient',{'action':'stop','session':owned})
        except Exception:pass
