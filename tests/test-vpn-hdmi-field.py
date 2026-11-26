"""Offline guards for physical cellular/VPN capture; no live imports or input."""
import ast,unittest
from pathlib import Path
SOURCE=(Path(__file__).resolve().parents[1]/'scripts/iphone-remote-hdmi.py').read_text(encoding='utf-8')
class VpnCaptureTests(unittest.TestCase):
    def test_script_syntax_and_owning_task(self):
        ast.parse(SOURCE)
        self.assertIn("choices=('WEB-023','WEB-037'),default='WEB-023'",SOURCE)
        self.assertIn("ROOT/'artifacts/active'/args.task",SOURCE)
    def test_capture_and_input_are_bounded(self):
        for token in ('choices=range(8,31)','1<=len(args.keys)<=12',
                      'len(args.keys)*args.interval+4>args.seconds',"not .3<=args.interval<=2"):
            self.assertIn(token,SOURCE)
    def test_exact_phone_media_and_recording_guards(self):
        for token in ("contexts!=['123c8282e1ee']","activity.get('recordingCount')!=0",
                      "activity.get('connectedClientCount')!=0",'mediaFileId'):
            self.assertIn(token,SOURCE)
        self.assertNotIn("'media.watch'",SOURCE)
        self.assertNotIn("'media.seek'",SOURCE)
    def test_unknown_input_is_not_replayed_and_owner_is_closed(self):
        self.assertIn('Unknown key receipt; do not replay',SOURCE)
        self.assertIn('finally:\n    box.close()',SOURCE)
        self.assertEqual(SOURCE.count("'action':'key'"),1)
        self.assertIn('AWAITING_VISUAL_REVIEW_NOT_AUTOMATIC_PASS',SOURCE)
    def test_audio_requires_explicit_commissioned_hdmi_not_microphone(self):
        self.assertIn("audio=args.audio_device or capture.get('audio_device')",SOURCE)
        self.assertIn("audio!='Digital Audio Interface (USB Digital Audio)'",SOURCE)
        self.assertIn('Explicit audio input requires --audio',SOURCE)
        self.assertNotIn('Webcam',SOURCE)
if __name__=='__main__':unittest.main()
