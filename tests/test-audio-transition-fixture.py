"""Offline CRC/PID/version and field safety contracts; no network or mutations."""
import importlib.util, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('audio_fixture',ROOT/'scripts/create-audio-transition-fixture.py')
G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)

class AudioTransition(unittest.TestCase):
    def test_generated_actual_transport_has_both_versions_and_late_nar(self):
        folder=ROOT/'artifacts/test-media/VIBE_AUDIO_PMT'
        if not folder.exists():self.skipTest('Explicit canonical fixture generation required')
        meta=json.loads((folder/'fixture.json').read_text(encoding='utf-8'))
        data=(folder/meta['name']).read_bytes();tables=G.inspect_tables(data)
        self.assertEqual([s['pid'] for s in tables[0]['streams']],[256,257])
        self.assertEqual([s['pid'] for s in tables[1]['streams']],[256,257,258])
        self.assertIn(b'eng',bytes.fromhex(tables[0]['streams'][1]['descriptors']))
        self.assertIn(b'nar',bytes.fromhex(tables[1]['streams'][2]['descriptors']))
        self.assertEqual(meta['phases'][0]['probe']['streams'][1]['channels'],1)
        self.assertEqual(meta['phases'][1]['probe']['streams'][1]['channels'],6)
        self.assertEqual(G.hashlib.sha256(data).hexdigest(),meta['sha256'])
        broken=bytearray(data);broken[tables[1]['firstByte']+20]^=1
        with self.assertRaises(RuntimeError):G.inspect_tables(broken)
    def test_field_requires_same_producer_identity_and_actual_audio(self):
        source=(ROOT/'tests/stock-audio-transition-field.py').read_text(encoding='utf-8')
        self.assertIn("current.get('session') != producer",source)
        self.assertIn("effective.get('audioStreamIndex') != expected_index",source)
        self.assertIn('selectedToOtherPower',source)
        self.assertIn("'/SageTVWebPlayer/',status['playlistUrl']",source)
        self.assertIn("wait(lambda:video()['ended']",source)
        self.assertNotIn('context.route(',source)
        self.assertNotIn("mcp('media.seek'",source)
        self.assertIn("observed.get('ok') is not True",source)
        self.assertIn('Read-only native retirement observation unavailable; no control replay',source)
    def test_staging_is_idle_new_only_readback_and_public_library(self):
        source=(ROOT/'scripts/stage-audio-transition-fixture.py').read_text(encoding='utf-8')
        for phrase in ('safeToRestart','no overwrite/replay','Readback hash mismatch','library.scan','media.resolve_exact_path'):
            self.assertIn(phrase,source)
        self.assertNotIn('library.add_import_path',source)
        self.assertNotIn('Sage.properties',source)

if __name__=='__main__':unittest.main()
