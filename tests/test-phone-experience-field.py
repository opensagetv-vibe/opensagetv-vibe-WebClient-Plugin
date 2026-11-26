"""Offline guards for actual-phone shared-experience commissioning."""
import ast,asyncio,json,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=(ROOT/'scripts/iphone-experience-field.py').read_text(encoding='utf-8')
class ExperienceFieldGuards(unittest.TestCase):
 def test_actual_cancel_handler_sets_flag_without_remote_input(self):
  handler=next(n for n in ast.parse(SOURCE).body if isinstance(n,ast.FunctionDef) and n.name=='request_cancel')
  ns={'cancel_requested':False}
  exec(compile(ast.Module(body=[handler],type_ignores=[]),'<actual-cancel-handler>','exec'),ns)
  ns['request_cancel'](None,None)
  self.assertTrue(ns['cancel_requested'])
 def test_actual_expression_guard_cancels_work_but_allows_finally(self):
  ev=next(n for n in ast.walk(ast.parse(SOURCE)) if isinstance(n,ast.AsyncFunctionDef) and n.name=='ev')
  calls=[]
  async def remote(_session,_code):calls.append(True);return {'fieldOk':True,'value':'cleanup-only'}
  ns={'cleaning':False,'cancel_requested':True,'report':{},'original':remote,'session':object(),'json':json}
  exec(compile(ast.Module(body=[ev],type_ignores=[]),'<actual-expression-guard>','exec'),ns)
  with self.assertRaisesRegex(RuntimeError,'Operator cancelled'):asyncio.run(ns['ev']('true'))
  self.assertEqual(calls,[])
  self.assertTrue(ns['report']['cancelledByOperator'])
  ns['cleaning']=True
  self.assertEqual(asyncio.run(ns['ev']('true')),'cleanup-only')
  self.assertEqual(calls,[True])
 def test_operator_cancel_preserves_finally_and_original_checkpoint(self):
  ast.parse(SOURCE)
  for token in ('signal.signal(signal.SIGINT,request_cancel)',
                'if not cleaning and (cancel_requested or cancel_path.exists())',
                'cleaning=True',"checkpoint_path.open('x'",'profile-checkpoint.private.json'):
   self.assertIn(token,SOURCE)
  self.assertLess(SOURCE.index("checkpoint_path.open('x'"),SOURCE.index('borrowed=True;await profile()'))
  self.assertNotIn("report['checkpoint']=checkpoint",SOURCE)
 def test_literal_phone_expressions_are_bounded_and_valid_javascript(self):
  tree=ast.parse(SOURCE);count=0
  for n in ast.walk(tree):
   if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='ev' and n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str):
    script=n.args[0].value;self.assertLessEqual(len(script.encode()),2048)
    result=subprocess.run(['node','--check'],input=script,capture_output=True,text=True,timeout=5)
    self.assertEqual(result.returncode,0,result.stderr);count+=1
  self.assertGreaterEqual(count,15)
 def test_only_canonical_fixture_watch_and_reset(self):
  self.assertIn("fixture=20905",SOURCE)
  self.assertIn("info.get('mediaFileId')!=fixture",SOURCE)
  self.assertEqual(SOURCE.count("mcp,'media.watch'"),1)
  self.assertEqual(SOURCE.count("mcp,'media.clear_watched'"),1)
  self.assertIn("(n.get('media') or {}).get('mediaFileId')!=fixture",SOURCE)
  self.assertNotIn('channel.tune',SOURCE)
 def test_presentation_and_counter_not_receipt_or_saved_rewrite(self):
  self.assertIn("if not a.abort:\n            while state.get('qualityHandoff')!='presented'",SOURCE)
  self.assertIn("actualPresentedAck=state.get('qualityHandoff')=='presented'",SOURCE)
  self.assertIn('#settingsCategories [data-settings-page=transcoding]',SOURCE)
  for token in ("if(e.isTrusted)s.trustedClicks++","state.get('qualityHandoff')!='presented'",
                "v['frames']>current['frames']+12","effective.get('videoTargetKbps')!=rate",
                'time.monotonic()-began<61','s.realObserve.call(this,v)',
                "SageMiniExperience.QualityAdvisor.prototype.observe=s.realObserve"):
   self.assertIn(token,SOURCE)
 def test_preview_does_not_commit_timeline_or_duplicate_producer(self):
  self.assertIn("input instanceof URL?input.href:input.url",SOURCE)
  self.assertIn('!seekRange.disabled&&Number(seekRange.max)>=45',SOURCE)
  self.assertIn("seekRange.dispatchEvent(new Event('input'",SOURCE)
  self.assertNotIn("seekRange.dispatchEvent(new Event('change'",SOURCE)
  for token in ("('producer','source','requestedPositionMs')","'activePreviewLeases':1",'<=32768',"result['height']!=108"):
   self.assertIn(token,SOURCE)
 def test_explicit_abort_and_profile_restoration_remain_guarded(self):
  for token in ("body.delete('presentedTimeMs')","expectedHlsSession=candidate",
                "restored.get('producer')!=baseline['producer']",'Preserve changed profile',
                'Preserve changed client settings',"report['profilesRestored']",'measuredWan=False'):
   self.assertIn(token,SOURCE)
if __name__=='__main__':unittest.main()
