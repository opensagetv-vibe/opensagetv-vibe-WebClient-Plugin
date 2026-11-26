import runpy,unittest
from pathlib import Path
c=runpy.run_path(str(Path(__file__).resolve().parents[1]/'scripts/commission-mobile.py'),run_name='test')
class Timestamp(unittest.TestCase):
    def test_changed_requires_strictly_newer_package_timestamp(self):
        for stamp in ((2026,11,20,12,0,0),(2026,11,19,12,0,0)):
            with self.assertRaises(RuntimeError):c['require_new_war_timestamp'](stamp,(2026,11,20,12,0,0),True)
    def test_newer_and_unchanged_are_safe(self):
        c['require_new_war_timestamp']((2026,11,22,12,0,0),(2026,11,20,12,0,0),True)
        c['require_new_war_timestamp']((2026,11,20,12,0,0),(2026,11,20,12,0,0),False)
if __name__=='__main__':unittest.main()
