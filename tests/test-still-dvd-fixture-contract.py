from pathlib import Path
import unittest,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
class FixtureContract(unittest.TestCase):
    def test_nonfirst_has_explicit_authored_main_and_three_chapters(self):
        xml=ET.parse(ROOT/'tests/fixtures/dvd-nonfirst-author.xml').getroot()
        self.assertEqual(xml.find('./titleset/menus/pgc/button').text,'jump title 2;')
        titles=xml.findall('./titleset/titles/pgc/vob')
        self.assertEqual([x.attrib['file'] for x in titles],['extra.vob','main.vob'])
        self.assertEqual(titles[1].attrib['chapters'],'0,4,8')
        s=(ROOT/'scripts/create-multititle-dvd-fixture.py').read_text(encoding='utf-8')
        self.assertIn("Path('/vibe-task-temp')",s)
        self.assertIn('no overwrite or alternate staging',s)
    def test_single_explicit_button_no_inferred_extra_buttons(self):
        spu=ET.parse(ROOT/'tests/fixtures/dvd-still-menu.xml').getroot().find('./stream/spu')
        self.assertNotIn('autooutline',spu.attrib)
        self.assertEqual([v.attrib['name'] for v in spu.findall('button')],['play'])
    def test_infinite_still_and_explicit_vmgm_format(self):
        xml=ET.parse(ROOT/'tests/fixtures/dvd-still-author.xml').getroot()
        self.assertEqual(xml.find('./vmgm/menus/video').attrib['format'],'ntsc')
        self.assertEqual(xml.find('./titleset/menus/pgc/vob').attrib['pause'],'inf')
    def test_staging_never_overwrites_or_stops_playback(self):
        s=(ROOT/'scripts/stage-still-dvd-fixture.py').read_text(encoding='utf-8')
        self.assertNotIn("'media.watch'",s);self.assertNotIn("'media.control'",s)
        self.assertIn("Preserve existing fixture; no overwrite/staging replay",s)
        self.assertIn('Remote fixture hash mismatch',s)
    def test_first_observer_guard_checks_window_before_declaring_global(self):
        s=(ROOT/'scripts/iphone-one-picture-dvd-gate.py').read_text(encoding='utf-8')
        self.assertIn('!window.__iphoneGate?.api||window.__onePictureField',s)
        self.assertIn('!videoPlane.paused||videoPlane.readyState!==0',s)
        self.assertIn("report['watchSubmitted']=True",s)
        self.assertIn("'held10s-without-audio'",s)
        self.assertIn('await owner.send(\'key\',key=\'enter\')',s)
    def test_failure_export_is_bounded_exact_owned_one_segment_only(self):
        s=(ROOT/'scripts/iphone-one-picture-dvd-gate.py').read_text(encoding='utf-8')
        self.assertIn("if not report.get('passed') and installed:",s)
        self.assertIn('await asyncio.to_thread(guard,True)',s)
        self.assertIn("if len(entries)!=1",s)
        self.assertIn('1024*1024',s)
        self.assertIn("with segment.open('xb')",s)
        self.assertNotIn('verify=False',s)
    def test_phone_acceptance_separates_selected_engine_and_actual_teardown(self):
        s=(ROOT/'scripts/iphone-one-picture-dvd-gate.py').read_text(encoding='utf-8')
        self.assertIn('selectedPlayer:p?.streamSettings?.requested?.player',s)
        self.assertIn('engine:p?.snapshot().browserEngine',s)
        self.assertIn("report['stopState']=stopped",s)
        self.assertIn("stopped['remotePlaybackDisabled']!=report['pagePreflight']['remotePlaybackDisabled']",s)
        self.assertNotIn("v.currentSrc=''",s)
if __name__=='__main__':unittest.main()
