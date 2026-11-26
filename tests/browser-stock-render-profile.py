#!/usr/bin/env python3
"""WEB-037 opt-in stock232 STV graphics profile, NOT physical iPhone evidence.

Uses only the existing dedicated web-test identity when absent. No media/tuner,
recording controls, restart, plugin installation, or other client's input.
Four Down focus moves are allowed only with no loaded media; own session is
retired in finally. Browser timing instrumentation lives in this context only.
"""
import importlib.util
import argparse
import json
import os
from pathlib import Path
import time
from playwright.sync_api import sync_playwright

if os.environ.get('SAGETV_RUN_STV_RENDER_PROFILE') != '1':
    raise SystemExit('Opt in with SAGETV_RUN_STV_RENDER_PROFILE=1')
ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ['SAGETV_ARTIFACT_DIR']).resolve()
if not OUT.is_relative_to((ROOT/'artifacts/active/WEB-037').resolve()):
    raise SystemExit('Require WEB-037 output directory')
OUT.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location('commission', ROOT/'scripts/commission-mobile.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
cfg = C.configuration()
parser = argparse.ArgumentParser()
parser.add_argument('--engine', choices=['chromium', 'webkit', 'both'], default='both')
parser.add_argument('--remote-touch',action='store_true',help='Navigate with production long-press remote arrow touch buttons')
parser.add_argument('--ios-policy',action='store_true',help='Emulate iPhone user agent for finite STV event delivery; still not physical Safari')
args = parser.parse_args()

def contexts():
    value = C.request(cfg, '/v1/control', {'action': 'ui.list'}, mcp=True)
    if not value.get('ok'):
        raise RuntimeError('Context ownership unavailable')
    return value.get('contexts', [])

INIT = r"""(()=>{
 const s=window.RENDER_PROFILE={decodes:[],copies:[],flips:[],inputs:[],chunks:[]};
 const image=window.createImageBitmap;
 if(image)window.createImageBitmap=async function(...a){const t=performance.now();try{return await image.apply(window,a)}finally{s.decodes.push({ms:performance.now()-t,bytes:a[0]?.size||0})}};
 const draw=CanvasRenderingContext2D.prototype.drawImage;
 CanvasRenderingContext2D.prototype.drawImage=function(...a){const t=performance.now();try{return draw.apply(this,a)}finally{const end=performance.now();if(this.canvas.id==='gfxCanvas')s.flips.push(end);if(s.copies.length<20000)s.copies.push(end-t)}};
 const fetch=window.fetch.bind(window);
 window.fetch=async(...a)=>{const t=performance.now(),r=await fetch(...a),u=new URL(a[0],location.href);if(u.pathname.endsWith('/api/miniclient')&&u.searchParams.get('action')==='command')s.inputs.push({start:t,ack:performance.now()});return r};
 const read=ReadableStreamDefaultReader.prototype.read;
 ReadableStreamDefaultReader.prototype.read=async function(...a){const r=await read.apply(this,a);if(r.value&&s.chunks.length<20000)s.chunks.push({at:performance.now(),bytes:r.value.byteLength});return r};
})()"""

with sync_playwright() as pw:
    for engine in (('chromium','webkit') if args.engine=='both' else (args.engine,)):
        # Each engine gets a distinct diagnostic identity. SageTV may retain an
        # idle UI context after its socket closes; never replace that context
        # merely to force the next profile to run.
        identity = 'da92a86446be' if engine=='chromium' else 'da92a86446bf'
        if any(x.replace(':', '').lower() == identity for x in contexts()):
            raise RuntimeError('Dedicated test identity already in use; do not replace')
        owned = None
        browser = None
        report = {'engine': engine, 'scope': 'real stock232, host browser, not iPhone', 'rows': []}
        def observe(response):
            global owned
            if '/api/miniclient' not in response.url or response.request.method != 'POST':
                return
            try:
                value = response.json()
                if value.get('session') and value.get('clientId', '').replace(':', '').lower() == identity:
                    owned = value['session']
            except Exception:
                pass
        try:
            options = {'headless': True}
            if engine == 'chromium':
                options.update(executable_path='/usr/local/bin/vibe-chromium', args=['--no-sandbox'])
            browser = getattr(pw, engine).launch(**options)
            context = browser.new_context(viewport={'width': 852, 'height': 393}, device_scale_factor=3,has_touch=args.remote_touch,is_mobile=args.remote_touch,
                http_credentials={'username': cfg['web_username'], 'password': cfg['web_password']}, service_workers='block')
            if args.ios_policy:context.add_init_script("Object.defineProperty(navigator,'userAgent',{value:'iPhone AppleWebKit Safari',configurable:true});")
            context.add_init_script("localStorage.setItem('sagetvWebMiniClientId',"+json.dumps(identity.upper())+");")
            context.add_init_script(INIT)
            page = context.new_page()
            errors = []
            page.on('response', observe)
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(cfg['web_base_url'].rstrip('/')+'/SageTVWebPlayer/miniclient.html', wait_until='domcontentloaded')
            page.wait_for_function('RENDER_PROFILE.flips.length>0', timeout=60000)
            page.wait_for_timeout(2000)
            if args.remote_touch:page.locator('#remoteToggle').click()
            for _ in range(4):
                state = C.request(cfg, '/v1/control', {'action':'ui.state', 'context':identity}, mcp=True)
                if not state.get('ok') or state.get('media'):
                    raise RuntimeError('Refuse navigation without verified media-idle own UI')
                start = page.evaluate('performance.now()')
                if args.remote_touch:page.locator('#nav_down img').tap()
                else:
                    page.locator('#stage').focus()
                    page.keyboard.press('ArrowDown')
                page.wait_for_timeout(1400)
                report['rows'].append(page.evaluate("""t=>{const s=RENDER_PROFILE,f=s.flips.filter(v=>v>=t),i=s.inputs.filter(v=>v.start>=t);return{firstFlipMs:f.length?f[0]-t:null,flips:f.length,inputAckMs:i.map(v=>v.ack-v.start)}}""", start))
            report.update(page.evaluate("""()=>{let s=RENDER_PROFILE;return{mainRevision:[...document.scripts].filter(s=>new URL(s.src).pathname.endsWith('/miniclient.js')).map(s=>new URL(s.src).searchParams.get('v')),stats:document.getElementById('stats').textContent,canvas:[gfxCanvas.width,gfxCanvas.height],imageDecodes:s.decodes,drawCount:s.copies.length,drawMs:s.copies.reduce((a,b)=>a+b,0),maxDrawMs:Math.max(0,...s.copies),frames:s.flips.length,chunks:s.chunks.length,chunkBytes:s.chunks.reduce((a,b)=>a+b.bytes,0)}}"""))
            native = C.request(cfg, '/SageTVWebPlayer/api/miniclient?action=status&session='+owned)
            report['native'] = {k:native.get(k) for k in ['queuedEvents', 'peakQueuedEvents', 'width', 'height', 'error']}
            report['gfxPackets'] = native.get('connection', {}).get('gfxPackets')
            report['framePacing'] = native.get('connection',{}).get('browserFrames')
            report['inputMethod'] = 'remote touch arrows' if args.remote_touch else 'keyboard arrows'
            report['iosPolicyEmulated'] = args.ios_policy
            report['errors'] = errors
            print(json.dumps(report), flush=True)
        finally:
            if owned:
                C.request(cfg, '/SageTVWebPlayer/api/miniclient', {'action':'stop', 'session':owned})
            if browser:
                browser.close()
            path = OUT/(time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-'+engine+'-stock-profile.json')
            with path.open('x',encoding='utf-8') as f:
                json.dump(report, f, indent=2)
