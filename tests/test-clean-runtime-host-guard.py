"""The staging orchestrator must reject a DEV alias before creating files."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class HostStagingGuard(unittest.TestCase):
 def test_real_workspace_guard_precedes_staging(self):
  source=(ROOT/'scripts/verify-clean-runtime.py').read_text(encoding='utf-8')
  guard=source.index("if ROOT.parent.name!='projects'")
  self.assertIn("not (WORKSPACE/'AGENTS.md').is_file()",source)
  self.assertLess(guard,source.index("relative=Path('artifacts/temp')"))
  self.assertLess(guard,source.index('archive.parent.mkdir'))
  self.assertIn('Run this staging orchestrator from the native workspace host',source)
if __name__=='__main__':unittest.main()
