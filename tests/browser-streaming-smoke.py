#!/usr/bin/env python3
"""Production DOM/profile/CC integration, with mock SageTV and mock mpegts.js.
This deliberately does NOT claim end-to-end vendor/video/GPU validation.
"""
from pathlib import Path
import json, os, re, time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];WEB=ROOT/'src/main/webapp'
count=0

def passed(s):
    global count
    count+=1;print('PASS '+s,flush=True)

with sync_playwright() as p:
    engine=os.environ.get('SAGETV_BROWSER_ENGINE','chromium')
    if engine not in ('chromium','webkit'):raise ValueError('Unsupported test engine')
    browser=p.webkit.launch(headless=True) if engine=='webkit' else p.chromium.launch(executable_path=os.getenv('CHROMIUM_PATH','/usr/local/bin/vibe-chromium'),headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    html=re.sub(r'<script[^>]*>.*?</script>','',(WEB/'miniclient.html').read_text(),flags=re.S)
    html=re.sub(r'<link[^>]*>','',html);page.set_content(html)
    page.add_style_tag(content=(WEB/'css/miniclient.css').read_text())
    page.evaluate(r"""(()=>{
      const T=window.TEST={requests:[],storage:{},pending:[],owners:[],stream:null,active:null,cursor:0,timeJump:0};
      const realNow=performance.now.bind(performance);performance.now=()=>realNow()+T.timeJump;
      T.emit=e=>T.stream?T.stream.enqueue(new TextEncoder().encode(JSON.stringify(e)+'\n')):T.pending.push(e);
      T.source={tracks:[{index:0,type:'video',codec:'mpeg2video',width:1920,height:1080},
        {index:1,type:'audio',codec:'ac3',language:'eng',channels:6,title:'Main'},
        {index:2,type:'audio',codec:'ac3',language:'spa',channels:2,title:'Spanish'}]};
      T.active={requested:{captions:'608',captionService:'1',captionOffsetMs:'0'},
        effective:{video:'h264',audio:'aac',videoTargetKbps:4500,audioTargetKbps:128,audioStreamIndex:2,reason:'requested transcode'},source:T.source};
      window.mpegts={version:'1.8.0-MOCK',Events:{ERROR:'error',MEDIA_INFO:'info',STATISTICS_INFO:'stats'},
        getFeatureList:()=>({mseLivePlayback:true}),createPlayer:(source,config)=>{
          const o={source,config,handlers:{},on(k,f){this.handlers[k]=f;},attachMediaElement(v){this.video=v;},
            load(){},destroy(){this.destroyed=true;},play(){return this.video.play();},pause(){return this.video.pause();}};
          T.owners.push(o);return o;
        }};
      const v=document.querySelector('#videoPlane');v._paused=true;v._time=0;v._ahead=20;
      Object.defineProperties(v,{
        currentTime:{get:()=>v._time,set:x=>v._time=x},paused:{get:()=>v._paused},readyState:{get:()=>4},
        videoWidth:{get:()=>1280},videoHeight:{get:()=>720},
        buffered:{get:()=>({length:1,start:()=>0,end:()=>v._time+v._ahead})}
      });
      v.play=()=>{v._paused=false;v.dispatchEvent(new Event('playing'));return Promise.resolve();};
      v.pause=()=>{v._paused=true;};v.load=()=>{v._time=0;};
      window.fetch=async(url,options={})=>{
        const u=new URL(url),q=new URLSearchParams(u.search);if(options.body)new URLSearchParams(options.body).forEach((v,k)=>q.set(k,v));
        const d=Object.fromEntries(q),a=d.action;T.requests.push({path:u.pathname,method:options.method||'GET',data:d});
        const json=(x,status=200)=>new Response(JSON.stringify(x),{status});
        if(a==='stream')return new Response(new ReadableStream({start(c){T.stream=c;for(const item of T.pending)T.emit(item);T.pending=[];}}));
        if(a==='start')return json({session:'settings-test',clientId:'020000000abc'});
        if(u.pathname.endsWith('/api/assets'))return json({streamingReady:true,errors:[]});
        if(u.pathname.endsWith('/api/captions')){
          if(Number(d.cursor)>0)return json({cursor:1,packets:[]});
          return json({cursor:1,packets:[[0,'fc142efc1420fc4849fc142f']]});
        }
        if(a==='streamSettings'){
          if(T.holdApply&&options.method==='POST'&&d.applyNow==='true')
            return new Promise(resolve=>(T.held||(T.held=[])).push(()=>resolve(json({ok:true,session:d.expectedHlsSession,active:T.active}))));
          return json({ok:true,active:T.active});
        }
        if(a==='status')return json({session:d.session,transport:'mpegts',running:true,hlsSeconds:120,durationMs:300000,encoder:'libx264',streamSettings:T.active});
        return json({ok:true});
      };
    })();""")
    for fn in ['miniclient-core.js','miniclient-input.js','miniclient-streaming.js','miniclient-caption-authority.js','atsc-captions.js','miniclient-captions.js','miniclient-subtitles.js','miniclient-dvd-spu.js','miniclient-support.js','miniclient-experience.js','miniclient-playback.js']:
        page.evaluate((WEB/'js'/fn).read_text())
    page.evaluate("(function(location,localStorage){\n"+(WEB/'js/miniclient.js').read_text()+"\n})({href:'https://fixture.test/miniclient.html',origin:'https://fixture.test',search:''},{getItem:k=>TEST.storage[k]||null,setItem:(k,v)=>TEST.storage[k]=v})")
    page.wait_for_function("document.querySelector('#connectionStatus').textContent.startsWith('Connected')")
    start=page.evaluate("TEST.requests.find(x=>x.data.action==='start').data")
    assert start['stream_player']=='auto' and start['stream_videoMode']=='auto' and start['stream_videoKbps']=='8000',start
    passed('native connect sends explicit browser streaming profile and capabilities')
    page.evaluate("TEST.timeJump=16000;TEST.emit({type:'keepalive'})")
    page.wait_for_function("TEST.requests.some(x=>x.data.action==='state'&&x.data.expectedHlsSession==='__browser_transport_only__')",timeout=4000)
    receipt=page.evaluate("TEST.requests.filter(x=>x.data.action==='state'&&x.data.expectedHlsSession==='__browser_transport_only__')")
    assert len(receipt)==1 and receipt[0]['method']=='POST' and receipt[0]['data']['timeMs']=='-1',receipt
    page.evaluate("TEST.emit({type:'keepalive'});TEST.emit({type:'keepalive'})");page.wait_for_timeout(100)
    assert page.evaluate("TEST.requests.filter(x=>x.data.expectedHlsSession==='__browser_transport_only__').length")==1
    passed('idle browser acknowledges received event bytes with bounded producer-mismatched receipt, not a clock/control or diagnostic heartbeat')
    assert page.locator('#browserPlaybackRate').is_disabled()
    page.locator('#settingsToggle').click();page.wait_for_function("document.querySelector('#stream_audioTrack').options.length===3")
    page.locator('#settings-tab-transcoding').click()
    page.locator('#stream_videoMode').select_option('copy');page.wait_for_function("TEST.storage['sagetvWebStreaming.v1']&&JSON.parse(TEST.storage['sagetvWebStreaming.v1']).videoMode==='copy'")
    assert page.evaluate("JSON.parse(TEST.storage['sagetvWebStreaming.v1']).videoMode")=='copy'
    page.locator('#closeSettings').click();page.locator('#settingsToggle').click();page.locator('#settings-tab-transcoding').click();page.wait_for_function("document.querySelector('#stream_videoMode').value==='copy'")
    passed('Copy video-processing selection persists immediately across settings close/reopen')
    assert page.locator('#stream_audioTrack option').nth(2).get_attribute('value')=='2'
    assert 'Spanish' in page.locator('#stream_audioTrack option').nth(2).inner_text()
    assert '4500 kbps' in page.locator('#streamingActual').inner_text()
    passed('source-derived language/codec/channel tracks and effective transcode values displayed')
    page.locator('#stream_player').select_option('mpegts');page.locator('#stream_videoMode').select_option('transcode');page.wait_for_function("JSON.parse(TEST.storage['sagetvWebStreaming.v1']).videoMode==='transcode'")
    page.locator('#stream_encoder').select_option('nvenc');page.locator('#stream_videoKbps').fill('4500')
    page.locator('#stream_resolution').select_option('720');page.locator('#stream_fps').select_option('29.97')
    page.locator('#stream_audioCodec').select_option('aac')
    page.locator('#stream_audioKbps').select_option('128');page.locator('#stream_audioChannels').select_option('2')
    page.locator('#settings-tab-playback').click()
    page.locator('#stream_audioTrack').select_option('2');page.locator('#stream_audioLanguage').fill('es');page.locator('#stream_audioOffsetMs').fill('250')
    page.locator('#captionAuthorityMode').select_option('cc1');page.locator('#cc1Type').select_option('cea608');page.locator('#cc1Service').fill('2')
    page.locator('#saveStreaming').click();page.wait_for_function("JSON.parse(TEST.storage['sagetvWebStreaming.v1']).audioLanguage==='es'&&JSON.parse(TEST.storage['sagetvWebStreaming.v1']).audioTrack===-1")
    request=page.evaluate("TEST.requests.filter(x=>x.data.action==='streamSettings'&&x.method==='POST').at(-1).data")
    for k,v in {'videoKbps':'4500','resolution':'720','fps':'29.97','encoder':'nvenc','audioTrack':'2','audioCodec':'aac','audioKbps':'128','audioOffsetMs':'250','captions':'608','captionService':'2'}.items():
        assert request['stream_'+k]==v,(k,request)
    assert request['applyNow']=='false'
    saved=page.evaluate("JSON.parse(TEST.storage['sagetvWebStreaming.v1'])")
    assert saved['audioTrack']==-1 and saved['audioLanguage']=='es'
    passed('Save wires all video/audio/CC options; explicit track is not persisted for other recordings')
    page.locator('#settings-tab-transcoding').click();page.locator('#resetStreaming').click()
    assert page.locator('#stream_videoKbps').input_value()=='8000'
    assert page.evaluate("JSON.parse(TEST.storage['sagetvWebStreaming.v1']).videoKbps")==4500
    passed('Load defaults edits draft only, without overwriting saved profile')
    page.locator('#preparePlayerAssets').click();page.wait_for_function("document.querySelector('#streamingResult').textContent.startsWith('Player assets cached')")
    asset=page.evaluate("TEST.requests.filter(x=>x.path.endsWith('/api/assets')).at(-1)")
    assert asset['method']=='POST' and asset['data']['family']=='streaming'
    passed('Prepare assets requests only version-pinned streaming library family')
    page.locator('#closeSettings').click()
    page.evaluate("TEST.emit({type:'videoStart',mediaId:100,hlsSession:'11111111111111111111111111111111',transport:'mpegts',streamUrl:'continuous/11111111111111111111111111111111/stream.ts',durationMs:300000,streamSettings:TEST.active})")
    page.wait_for_function('TEST.owners.length===1')
    owner=page.evaluate('({source:TEST.owners[0].source,config:TEST.owners[0].config})')
    assert owner['config']['lazyLoadMaxDuration']==180 and not owner['source']['isLive'] and owner['config']['enableWorker'] and not owner['config']['enableWorkerForMSE']
    assert '/continuous/' in owner['source']['url'] and owner['config']['seekParamStart']=='bstart'
    passed('production playback adapter starts continuous TS with 180-second lazy reserve and byte resume')
    page.wait_for_function("document.querySelector('#localCaptions').textContent.includes('HI')")
    assert page.locator('#localCaptions .caption-608').count()==1
    passed('real production CEA decoder and video-clock controller display side-channel CC')
    page.wait_for_function('!browserPlaybackRate.disabled')
    before=page.evaluate("TEST.requests.filter(r=>r.method==='POST'&&['streamSettings','seek','command','qualityPrepare'].includes(r.data.action)).length")
    for rate in ('0.5','1.5','2','1'):
        page.evaluate("r=>{browserPlaybackRate.value=r;browserPlaybackRate.dispatchEvent(new Event('change',{bubbles:true}))}",rate)
        assert page.evaluate('videoPlane.playbackRate')==float(rate)
    assert page.evaluate("TEST.requests.filter(r=>r.method==='POST'&&['streamSettings','seek','command','qualityPrepare'].includes(r.data.action)).length")==before
    passed('explicit browser-local speed changes effective rate without native rate/seek/transcode requests')
    page.locator('#settingsToggle').click();page.locator('#settings-tab-transcoding').click();page.locator('#stream_videoKbps').fill('5000');page.locator('#settings-tab-playback').click();page.locator('#stream_audioTrack').select_option('2')
    page.evaluate("TEST.emit({type:'media',action:'pause'});document.querySelector('#videoPlane')._time=42;")
    page.wait_for_function('videoPlane.paused')
    page.locator('#applyStreaming').click();page.wait_for_function("document.querySelector('#streamingResult').textContent.startsWith('Applied')")
    request=page.evaluate("TEST.requests.filter(x=>x.data.action==='streamSettings'&&x.method==='POST').at(-1).data")
    assert request['applyNow']=='true' and request['timeMs']=='42000' and request['expectedHlsSession']=='1'*32 and request['stream_videoKbps']=='5000'
    passed('Apply now carries selected quality/track, current timestamp and stale-session guard')
    page.locator('#captionAuthorityMode').select_option('cc1');page.locator('#cc1Type').select_option('cea608');page.locator('#cc1Service').fill('5');page.locator('#saveStreaming').click()
    # Explicit manual CEA selection is intentionally clamped by the current
    # caption authority policy; it does not reject the whole streaming form.
    page.wait_for_function("document.querySelector('#streamingResult').textContent.startsWith('Saved')")
    request=page.evaluate("TEST.requests.filter(x=>x.data.action==='streamSettings'&&x.method==='POST').at(-1).data")
    assert request['stream_captions']=='608' and request['stream_captionService']=='4',request
    passed('manual CEA-608 service is bounded to a valid channel instead of submitting service5')
    page.locator('#cc1Service').fill('1')
    # Production450ms debounce and one-in-flight/latest-successor behavior,
    # not a test reimplementation of the controller. Vendor/server are mocks.
    page.evaluate("""()=>{TEST.requests=[];for(const n of [800,750,700]){stream_videoKbps.value=String(n);stream_videoKbps.dispatchEvent(new Event('input',{bubbles:true}));}for(const n of [100,200,250]){stream_audioOffsetMs.value=String(n);stream_audioOffsetMs.dispatchEvent(new Event('input',{bubbles:true}));}}""")
    page.wait_for_function("TEST.requests.filter(r=>r.method==='POST'&&r.data.action==='streamSettings').length===1")
    page.wait_for_function("JSON.parse(TEST.storage['sagetvWebStreaming.v1']).videoKbps===700")
    page.wait_for_timeout(550)
    changes=page.evaluate("TEST.requests.filter(r=>r.method==='POST'&&r.data.action==='streamSettings').map(r=>r.data)")
    assert len(changes)==1 and changes[0]['stream_videoKbps']=='700' and changes[0]['stream_audioOffsetMs']=='250',changes
    assert changes[0]['timeMs']=='42000' and changes[0]['expectedHlsSession']=='1'*32 and changes[0]['session']=='settings-test',changes
    assert changes[0]['stream_captions']=='608' and changes[0]['stream_captionService']=='1' and page.evaluate('videoPlane.paused'),(changes,page.evaluate('videoPlane.paused'))
    passed('six rapid production inputs produce one settled Apply preserving position/Pause/caption/native owner')
    page.evaluate("""()=>{TEST.requests=[];TEST.holdApply=true;TEST.held=[];stream_videoKbps.value='800';stream_videoKbps.dispatchEvent(new Event('input',{bubbles:true}));}""")
    page.wait_for_function('TEST.held.length===1')
    page.evaluate("""()=>{for(const n of [850,875,900]){stream_videoKbps.value=String(n);stream_videoKbps.dispatchEvent(new Event('input',{bubbles:true}));}stream_audioOffsetMs.value='200';stream_audioOffsetMs.dispatchEvent(new Event('input',{bubbles:true}));}""")
    page.wait_for_timeout(600)
    assert page.evaluate('TEST.held.length')==1
    assert page.evaluate("JSON.parse(TEST.storage['sagetvWebStreaming.v1']).videoKbps")==700
    page.evaluate('TEST.held.shift()()');page.wait_for_function('TEST.held.length===1')
    assert page.evaluate("JSON.parse(TEST.storage['sagetvWebStreaming.v1']).videoKbps")==700
    page.evaluate('TEST.holdApply=false;TEST.held.shift()()')
    page.wait_for_function("JSON.parse(TEST.storage['sagetvWebStreaming.v1']).videoKbps===900")
    changes=page.evaluate("TEST.requests.filter(r=>r.method==='POST'&&r.data.action==='streamSettings').map(r=>r.data)")
    assert len(changes)==2 and [r['stream_videoKbps'] for r in changes]==['800','900'],changes
    assert changes[-1]['stream_audioOffsetMs']=='200' and page.evaluate('videoPlane.paused')
    passed('one delayed Apply retains only latest successor and never persists superseded slider values')
    page.evaluate("""()=>{TEST.requests=[];TEST.holdApply=true;TEST.held=[];TEST.beforeStale=TEST.storage['sagetvWebStreaming.v1'];stream_videoKbps.value='950';stream_videoKbps.dispatchEvent(new Event('input',{bubbles:true}));}""")
    page.wait_for_function('TEST.held.length===1')
    page.evaluate("""()=>{TEST.emit({type:'videoStart',mediaId:200,hlsSession:'22222222222222222222222222222222',transport:'mpegts',streamUrl:'continuous/22222222222222222222222222222222/stream.ts',durationMs:300000,streamSettings:TEST.active});}""")
    page.wait_for_function('TEST.owners.length===2')
    page.evaluate('TEST.holdApply=false;TEST.held.shift()()');page.wait_for_timeout(650)
    assert page.evaluate("TEST.storage['sagetvWebStreaming.v1']===TEST.beforeStale")
    assert page.evaluate("TEST.requests.filter(r=>r.method==='POST'&&r.data.action==='streamSettings').length")==1
    passed('late Apply response cannot persist an old profile or replay configuration on a different source')
    # The video is a real HTMLMediaElement: playbackRate is not mocked above.
    # Exercise the production control branch without inventing a server event.
    observed=page.evaluate("""()=>{const v=videoPlane,before={source:v.getAttribute('src'),paused:v.paused,volume:v.volume,muted:v.muted};const rates=[];for(const rate of [.5,1,1.5,2,1]){SageMiniPlayback.prototype.control.call({video:v},'rate',rate);rates.push(v.playbackRate)}return{rates,preserved:JSON.stringify(before)===JSON.stringify({source:v.getAttribute('src'),paused:v.paused,volume:v.volume,muted:v.muted})}}""")
    assert observed['rates']==[.5,1,1.5,2,1] and observed['preserved'],observed
    passed('production rate-control branch sets real browser playbackRate0.5..2/reset without altering source/Pause/audio state')
    page.evaluate("""()=>{TEST.rateStorage=TEST.storage['sagetvWebStreaming.v1'];TEST.emit({type:'media',action:'pause'});browserPlaybackRate.value='1.5';browserPlaybackRate.dispatchEvent(new Event('change',{bubbles:true}));}""")
    page.wait_for_function('videoPlane.paused&&videoPlane.playbackRate===1.5')
    page.evaluate("""()=>{TEST.emit({type:'videoStart',mediaId:200,seek:true,hlsSession:'33333333333333333333333333333333',transport:'mpegts',streamUrl:'continuous/33333333333333333333333333333333/stream.ts',durationMs:300000,streamSettings:TEST.active});}""")
    page.wait_for_function('TEST.owners.length===3&&videoPlane.paused&&videoPlane.playbackRate===1.5')
    passed('same-recording seek retains browser speed and Pause without persisting a speed preference')
    page.evaluate("""()=>{TEST.emit({type:'videoStart',mediaId:300,hlsSession:'44444444444444444444444444444444',transport:'mpegts',streamUrl:'continuous/44444444444444444444444444444444/stream.ts',durationMs:300000,streamSettings:TEST.active});}""")
    page.wait_for_function('TEST.owners.length===4&&videoPlane.playbackRate===1&&!browserPlaybackRate.disabled')
    assert page.evaluate("TEST.storage['sagetvWebStreaming.v1']===TEST.rateStorage")
    passed('different recording resets speed to normal and preserves saved streaming settings')
    observed=page.evaluate("""()=>{const v=videoPlane,before=v.playbackRate;Object.defineProperty(v,'playbackRate',{configurable:true,get:()=>before,set:()=>{throw Error('Deliberate unsupported rate')}});try{browserPlaybackRate.value='1.5';browserPlaybackRate.dispatchEvent(new Event('change',{bubbles:true}));return{unchanged:v.playbackRate===before,reported:browserPlaybackRateStatus.textContent.includes('unavailable')}}finally{delete v.playbackRate}}""")
    assert observed['unchanged'] and observed['reported'],observed
    passed('browser rate rejection is reported without decoder restart or an implicit retry')
    page.evaluate("""()=>{browserPlaybackRate.value='2';browserPlaybackRate.dispatchEvent(new Event('change',{bubbles:true}));TEST.emit({type:'videoStart',mediaId:400,dvd:true,hlsSession:'55555555555555555555555555555555',transport:'mpegts',streamUrl:'continuous/55555555555555555555555555555555/stream.ts',durationMs:300000,streamSettings:TEST.active});}""")
    page.wait_for_function('TEST.owners.length===5&&videoPlane.playbackRate===1&&browserPlaybackRate.disabled')
    passed('DVD generation resets local speed and disables it so native DVD controls retain ownership (mock media)')
    page.locator('#settings-tab-transcoding').click();page.locator('#stream_videoKbps').fill('700')
    page.locator('#applyStreaming').click()
    page.wait_for_function("streamingResult.textContent.startsWith('DVD settings submitted')")
    request=page.evaluate("TEST.requests.filter(x=>x.data.action==='streamSettings'&&x.method==='POST'&&x.data.applyNow==='true').at(-1).data")
    assert request['expectedHlsSession']=='5'*32 and request['stream_videoKbps']=='700'
    assert 'Resume' in page.locator('#streamingResult').inner_text()
    passed('explicit DVD Apply uses existing profile endpoint/exact producer and reports submission, not presented video or forced Play')
    out=Path(os.environ.get('SAGETV_ARTIFACT_DIR',ROOT/'build/test-results'));out.mkdir(parents=True,exist_ok=True)
    stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
    page.locator('#streamingPreferences').scroll_into_view_if_needed();page.screenshot(path=str(out/(stamp+'-streaming-settings-desktop.png')))
    page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(100)
    assert page.evaluate('document.documentElement.scrollWidth')<=391
    for selector in ['#streamingPreferences','#stream_videoKbps','#stream_audioCodec']:
        b=page.locator(selector).bounding_box();assert b['x']>=-1 and b['x']+b['width']<=391,(selector,b)
    page.locator('#applyStreaming').scroll_into_view_if_needed();assert page.locator('#applyStreaming').is_visible()
    page.screenshot(path=str(out/(stamp+'-streaming-settings-mobile.png')))
    passed('streaming form and long track descriptions fit mobile viewport; all controls scroll into view')
    assert page.locator('label',has=page.locator('#stream_encoder')).inner_text().startswith('Hardware Encoder')
    for encoder in ('auto','qsv','nvenc','vaapi','amf','videotoolbox','software'):
        assert page.evaluate('(encoder)=>SageMiniStreaming.toParams(SageMiniStreaming.normalize({encoder,player:"hls"})).stream_encoder',encoder)==encoder
    passed('Hardware Encoder names and all shared accelerator/software profile choices survive normalization')
    page.locator('#closeSettings').click();page.evaluate("TEST.emit({type:'videoStop'});")
    page.wait_for_function("TEST.owners.every(o=>o.destroyed)&&document.querySelector('#localCaptions').textContent===''")
    assert page.evaluate('videoPlane.playbackRate===1&&browserPlaybackRate.disabled')
    passed('stop destroys TS owner and clears caption output')
    assert not errors,errors;passed('no uncaught JavaScript errors in production settings, playback adapter and caption UI')
    browser.close()
print(f'{engine} streaming settings: {count} tests PASS (mock vendor/SageTV, real DOM/CC decoder)')
