"""Offline validation of the actual phone field helper; no phone I/O."""
import ast,importlib.util,json,subprocess,unittest
from contextlib import nullcontext
from types import SimpleNamespace
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=(ROOT/'scripts/iphone-dvd-portable-field.py').read_text(encoding='utf-8')
TREE=ast.parse(SOURCE)
LITERALS=[n.args[0].value for n in ast.walk(TREE) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='ev' and n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str)]
class PhoneDvdField(unittest.TestCase):
 def test_all_literal_expressions_are_bounded_valid_javascript(self):
  self.assertGreaterEqual(len(LITERALS),12)
  for code in LITERALS:
   self.assertLessEqual(len(code.encode()),2048)
   r=subprocess.run(['node','--check'],input=code,text=True,capture_output=True,timeout=5)
   self.assertEqual(r.returncode,0,r.stderr)
 def test_actual_observer_discovers_body_state_without_waiting_for_new_event_stream(self):
  code=next(s for s in LITERALS if 's.fetch=function' in s)
  js="""const vm=require('node:vm'),assert=require('node:assert/strict');let calls=0;
const c={URL,URLSearchParams,location:{origin:'http://test',href:'http://test/SageTVWebPlayer/miniclient.html'},document:{visibilityState:'visible',addEventListener(){}},videoPlane:{getAttribute(){return null},readyState:0,requestVideoFrameCallback(){return 1}},localStorage:{getItem(){return null}},SageMiniStreaming:{normalize:v=>v},fetch(){calls++;return 'unchanged'}};c.window=c;vm.createContext(c);vm.runInContext(CODE,c);
const s=c.__dvdPortable,id='1'.repeat(32),other='2'.repeat(32);
assert.equal(c.fetch('http://foreign/api/miniclient?action=state',{body:new URLSearchParams({session:other})}),'unchanged');assert.equal(s.session,undefined);
c.fetch('http://test/SageTVWebPlayer/api/miniclient?action=state',{body:new URLSearchParams({session:id})});assert.equal(s.session,id);
c.fetch(new URL('http://test/SageTVWebPlayer/api/miniclient?action=events&session='+other));assert.equal(s.session,other);
c.fetch('http://test/SageTVWebPlayer/api/miniclient?action=command',{body:new URLSearchParams({session:id,command:'8'})});assert.equal(s.commands.join(','),'8');assert.equal(s.session,other);assert.equal(calls,4);
""".replace('CODE',json.dumps(code))
  r=subprocess.run(['node','-e',js],text=True,capture_output=True,timeout=5)
  self.assertEqual(r.returncode,0,r.stderr)
 def test_observer_cleanup_is_not_skipped_if_profile_observation_fails(self):
  self.assertIn("except Exception:report['cleanup'].append('Profile comparison unavailable')\n   try:",SOURCE)
  self.assertIn('configured is not None and',SOURCE)
  self.assertIn("if(window.fetch===s.fetch)window.fetch=s.realFetch",SOURCE)
 def test_private_originals_precede_the_single_apply_action(self):
  self.assertLess(SOURCE.index("dvd-apply-checkpoint.private.json"),SOURCE.index("await button('applyStreaming')"))
  self.assertIn('Preserve changed profile',SOURCE)
  self.assertIn("report['exactProfilesRestored']",SOURCE)
 def test_only_public_canonical_source_and_guarded_stop(self):
  self.assertIn("identity='123c8282e1ee';fixture=20819",SOURCE)
  self.assertEqual(SOURCE.count("api,'watchContent'"),1)
  self.assertEqual(SOURCE.count("mcp,'media.control',context=identity,operation='stop'"),1)
  self.assertNotIn('media.seek',SOURCE)
  self.assertNotIn('clear_watched',SOURCE)
  close_at=SOURCE.index("mcp,'media.control',context=identity,operation='stop'")
  self.assertGreater(SOURCE.rfind('await asyncio.to_thread(guard,True)',0,close_at),0)
  self.assertIn("view.get('layout')=='fullscreen' and actual.get('presentation',{}).get('kind')=='fullscreen'",SOURCE)
 def test_real_ble_and_actual_picture_native_clock_proof(self):
  for token in ("await owner.send('key',key='enter')","v['epoch']>before['epoch']","v['frames']>15",'[7,10,8,8,9]',"['session']!=producer",'approximateLanding=True'):
   self.assertIn(token,SOURCE)
 def test_apply_uses_real_encoder_and_settled_pictures_not_missing_dvd_metadata(self):
  self.assertNotIn("eff=(st.get('streamSettings')",SOURCE)
  for token in ("encoder_target,profile['session']","target['videoTarget']!='700k'","target['encodedHeight']!=480","time.monotonic()-began>=8","v['frameTime']>=after['frameTime']+5"):
   self.assertIn(token,SOURCE)
 def test_encoder_observer_is_exact_owned_child_and_actual_raster(self):
  spec=importlib.util.spec_from_file_location('dvd_observations',ROOT/'scripts/dvd-field-observations.py')
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  identity='a'*32;calls=[]
  def remote(client,command):
   calls.append(command)
   if 'ps -eww -o args' in command:
    return '/p/mim -c:v h264_qsv -b:v 700k /h/'+identity+'/stream.m3u8\n/p/ffmpeg.real -c:v h264_qsv -b:v 700k /h/'+identity+'/stream.m3u8'
   return json.dumps({'streams':[{'width':720,'height':480}]})
  c=SimpleNamespace(ssh=lambda cfg:nullcontext(None),remote=remote)
  target=module.encoder_target(c,{'unraid_container_name':'test'},identity)
  self.assertEqual(target,dict(videoTarget='700k',encoder='h264_qsv',encodedWidth=720,encodedHeight=480))
  self.assertIn('/'+identity+'/seg_00002.ts',calls[1])
  for invalid in ('','../../other','a'*31,'A'*32):
   with self.assertRaises(RuntimeError):module.encoder_target(c,{},invalid)
  self.assertEqual(len(calls),2)
if __name__=='__main__':unittest.main()
