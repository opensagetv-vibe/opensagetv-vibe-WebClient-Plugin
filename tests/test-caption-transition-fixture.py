"""Generated-fixture integrity and field ownership; not physical acceptance."""
import ast
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'caption_fixture', ROOT / 'scripts/create-caption-transition-fixture.py')
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


def inspect_tables(data):
    rows = {}
    if len(data) % 188:
        raise RuntimeError('Invalid transport length')
    for offset in range(0, len(data), 188):
        packet = data[offset:offset+188]
        payload = fixture.payload_start(packet)
        if ((packet[1] & 31) << 8) | packet[2] != 4096 or not packet[1] & 0x40:
            continue
        start = payload + 1 + packet[payload]
        section = packet[start:]
        length = 3 + (((section[1] & 15) << 8) | section[2])
        section = section[:length]
        if len(section) != length or fixture.V.crc32_mpeg(section) != b'\0\0\0\0':
            raise RuntimeError('PMT CRC/length mismatch')
        version = (section[5] >> 1) & 31
        cursor = 12 + (((section[10] & 15) << 8) | section[11])
        streams = []
        while cursor < len(section)-4:
            size = ((section[cursor+3] & 15) << 8) | section[cursor+4]
            streams.append(dict(pid=((section[cursor+1] & 31) << 8) | section[cursor+2],
                                descriptors=section[cursor+5:cursor+5+size].hex()))
            cursor += 5+size
        old = rows.setdefault(version, dict(firstByte=offset, streams=streams))
        if old['streams'] != streams:
            raise RuntimeError('Inventory changed without a PMT version change')
    return rows


class CaptionTransition(unittest.TestCase):
    def test_real_transport_has_crc_checked_service_removal_and_return(self):
        folder = ROOT / 'artifacts/test-media/VIBE_CAPTION_PMT'
        if not folder.exists():
            self.skipTest('Explicit canonical fixture generation required')
        meta = json.loads((folder / 'fixture.json').read_text(encoding='utf-8'))
        data = (folder / meta['name']).read_bytes()
        self.assertTrue(meta['generated'])
        self.assertFalse(meta['originalBroadcast'])
        self.assertEqual(hashlib.sha256(data).hexdigest(), meta['sha256'])
        inventory = inspect_tables(data)
        self.assertEqual(list(inventory), [0, 1, 2, 3])
        for phase, pids in enumerate(([336, 337], [337], [], [336, 337])):
            streams = inventory[phase]['streams']
            self.assertEqual([s['pid'] for s in streams], [256, 257] + pids)
            for stream in streams[2:]:
                descriptor = bytes.fromhex(stream['descriptors'])
                self.assertEqual(descriptor[:2], b'\x59\x08')
                self.assertEqual(descriptor[2:5], b'eng' if stream['pid'] == 336 else b'spa')
        corrupted = bytearray(data)
        offset = inventory[1]['firstByte']
        packet = data[offset:offset+188]
        payload = fixture.payload_start(packet)
        corrupted[offset + payload + 1 + packet[payload] + 8] ^= 1
        with self.assertRaises(RuntimeError):
            inspect_tables(corrupted)

    def test_staging_refuses_overwrite_and_verifies_bytes_before_public_scan(self):
        source = (ROOT / 'scripts/stage-caption-transition-fixture.py').read_text()
        ast.parse(source)
        for token in ('--verify-existing', 'no overwrite/replay', 'Readback hash mismatch',
                      'library.scan', 'media.resolve_exact_path', 'Another producer active'):
            self.assertIn(token, source)
        self.assertNotIn('library.add_import_path', source)
        self.assertNotIn('Sage.properties', source)

    def test_phone_observes_real_pixels_and_restores_only_borrowed_profiles(self):
        source = (ROOT / 'scripts/iphone-caption-pmt-field.py').read_text()
        ast.parse(source)
        for token in ('requestVideoFrameCallback', 'getImageData', 'x.clone().json()',
                      'Preserve changed profile', "await save_form(True)",
                      "report['profilesRestored']", "report['observerRestored']",
                      'before PMT source time16s', 'before PMT source time32s'):
            self.assertIn(token, source)
        self.assertEqual(source.count("mcp,'media.watch'"), 2)
        self.assertEqual(source.count("operation='stop'"), 2)
        for token in ('--lifecycle', 'reopenWatchIntent', 'preReconnectStopIntent',
                      'if not stopped and', 'old[\'source\']', 'actual native generated-source EOF',
                      'No new reopened pictures; no Watch replay'):
            self.assertIn(token, source)
        self.assertIn("ready['connected'] and contexts==[identity]", source)
        self.assertIn('actual new tail pictures and visible Spanish bitmap', source)
        self.assertNotIn('currentTime=', source)


if __name__ == '__main__':
    unittest.main()
