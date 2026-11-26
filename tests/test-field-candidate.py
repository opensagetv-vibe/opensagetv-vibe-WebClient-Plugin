"""Offline candidate-guard regressions; no phone/server imports."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('candidate',ROOT/'scripts/field_candidate.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)

class CandidateTests(unittest.TestCase):
    def check(self,metadata,html):
        with tempfile.TemporaryDirectory(prefix='vibe-field-candidate-') as directory:
            root=Path(directory);(root/'src/main/webapp').mkdir(parents=True)
            (root/'BUILD_INFO.json').write_text(json.dumps(metadata),encoding='utf-8')
            (root/'src/main/webapp/miniclient.html').write_text(html,encoding='utf-8')
            return C.playback_revision(root)
    def test_current_source(self):
        info=json.loads((ROOT/'BUILD_INFO.json').read_text(encoding='utf-8'))
        self.assertEqual(C.playback_revision(ROOT),'v='+info['version']+'-'+info['asset_versions']['playback'])
    def test_future_metadata_without_hardcoded_runner(self):
        self.assertEqual(self.check({'version':'4.2.1','asset_versions':{'playback':'web123.4'}},
            '<script src="js/miniclient-playback.js?v=4.2.1-web123.4"></script>'),'v=4.2.1-web123.4')
    def test_stale_source_refused(self):
        with self.assertRaises(ValueError):self.check({'version':'4.2.1','asset_versions':{'playback':'web123.4'}},
            '<script src="js/miniclient-playback.js?v=4.2.1-web122.1"></script>')
    def test_missing_metadata_refused(self):
        with self.assertRaises(ValueError):self.check({'version':'4.2.1'},'')
    def test_duplicate_script_refused(self):
        with self.assertRaises(ValueError):self.check({'version':'4.2.1','asset_versions':{'playback':'web123.4'}},
            '<script src="js/miniclient-playback.js?v=4.2.1-web123.4"></script>'*2)
if __name__=='__main__':unittest.main()
