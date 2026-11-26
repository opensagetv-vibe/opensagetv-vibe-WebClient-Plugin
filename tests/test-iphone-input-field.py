"""Offline ownership/no-replay/privacy checks of the physical input runner."""
import ast,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=(ROOT/'scripts/iphone-input-field.py').read_text(encoding='utf-8');TREE=ast.parse(SOURCE)
class InputField(unittest.TestCase):
 def test_literal_probes_are_valid_and_within_inspector_bound(self):
  codes=[n.args[0].value for n in ast.walk(TREE) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='ev' and n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str)]
  self.assertGreaterEqual(len(codes),10)
  for code in codes:
   self.assertLessEqual(len(code.encode()),2048)
   result=subprocess.run(['node','--check'],input=code,text=True,capture_output=True,timeout=5)
   self.assertEqual(result.returncode,0,result.stderr)
 def test_harmless_mapping_and_preserved_draft(self):
  self.assertIn("await edit('24');await key('delete')",SOURCE)
  self.assertIn("await edit('none');await key('delete')",SOURCE)
  self.assertNotIn("await edit('83')",SOURCE)
  self.assertIn('keyboardInput.value)',SOURCE)
  self.assertNotIn("key('enter')",SOURCE)
 def test_checkpoint_precedes_edits_and_cas_restore(self):
  self.assertLess(SOURCE.index('input-checkpoint.private.json'),SOURCE.index("await edit('24')"))
  self.assertIn('Preserve changed mapping',SOURCE)
  self.assertIn("localStorage.removeItem('sagetvWebInput.v1')",SOURCE)
  self.assertIn("report['exactProfilesRestored']",SOURCE)
  self.assertIn('Observer owner changed',SOURCE)
 def test_idle_observes_existing_firmware_worker_without_rearm(self):
  self.assertIn("before.get('firmwareKeepAwakeEnabled')",SOURCE)
  self.assertIn("status.get('activeInputSessions')==0",SOURCE)
  self.assertIn("view['moves']>moves",SOURCE)
  self.assertNotIn("'firmware_keep_awake'",SOURCE)
  self.assertNotIn('unlock',SOURCE.replace('no rearm/unlock',''))
if __name__=='__main__':unittest.main()
