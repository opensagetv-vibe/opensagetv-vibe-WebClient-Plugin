import importlib.util,ast
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('clock',Path(__file__).resolve().parents[1]/'scripts/dvd-field-clock.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)

class ClockChecks(unittest.TestCase):
    def test_fixture_replacements_do_not_confuse_reader_with_presentation(self):
        for chapter,command in [(1,65),(2,66),(3,66),(4,66)]:
            self.assertEqual(C.fixture_replacement_command(dict(dvdMenu=False,dvdTitle=1,dvdChapter=chapter)),command)
        for change in [dict(dvdMenu=True),dict(dvdMenu=None),dict(dvdTitle=2),dict(dvdChapter=0),dict(dvdChapter=5),dict(dvdChapter=True),dict(dvdChapter='2')]:
            self.assertIsNone(C.fixture_replacement_command(dict(dict(dvdMenu=False,dvdTitle=1,dvdChapter=1),**change)))
    def test_field_observations_never_post_settings_defaults(self):
        source=(Path(__file__).parent/'stock-dvd-clock-field.py').read_text(encoding='utf-8')
        tree=ast.parse(source)
        function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='api')
        from urllib.parse import urlencode,parse_qs,urlsplit
        class Transport:
            calls=[]
            @classmethod
            def request(cls,*args):cls.calls.append(args);return {}
        scope=dict(C=Transport,cfg={},owned='owned-test',urlencode=urlencode)
        exec(compile(ast.Module(body=[function],type_ignores=[]),'<actual field API>','exec'),scope)
        for action,values in [('status',{}),('contentState',{'mediaId':20819}),('streamSettings',{})]:
            scope['api'](action,**values)
            args=Transport.calls[-1]
            self.assertEqual(len(args),2)
            self.assertEqual(parse_qs(urlsplit(args[1]).query)['action'],[action])
        scope['api']('streamSettings',applyNow='false',stream_videoKbps='700')
        self.assertEqual(Transport.calls[-1][2]['stream_videoKbps'],'700')
        scope['api']('stop')
        self.assertEqual(Transport.calls[-1][2]['action'],'stop')
    def sample(self, **changes):
        return dict(dict(nativeMenu=False,title=1,chapter=2,lastPresented=5.5,
            rawMs=25500,sourceChanged=True,frames=40,ready=4,paused=False),**changes)
    def test_reader_can_advance_without_falsifying_presented_clock(self):
        self.assertTrue(C.chapter_two_picture_clock(self.sample(chapter=3)))
    def test_stale_before_fix_clock_fails(self):
        self.assertFalse(C.chapter_two_picture_clock(self.sample(rawMs=5500)))
    def test_presentation_speed_uses_real_frames_and_monotonic_elapsed(self):
        before=dict(epoch=2,frames=10,frameTime=1,paused=False)
        after=dict(epoch=2,frames=160,frameTime=6,paused=False)
        self.assertEqual(C.presentation_speed(before,after,5),1)
        self.assertEqual(C.presentation_speed(before,dict(after,frameTime=3),5),.4)
        for changes in ({'epoch':3},{'frames':10},{'paused':True},{'frameTime':None}):
            self.assertIsNone(C.presentation_speed(before,dict(after,**changes),5))
        self.assertIsNone(C.presentation_speed(before,after,0))
    def test_old_picture_menu_wrong_title_and_missing_clocks_fail(self):
        for changes in ({'sourceChanged':False},{'frames':0},{'nativeMenu':True},
                {'title':2},{'lastPresented':None},{'lastPresented':float('nan')},
                {'rawMs':True},{'rawMs':41000},{'paused':True}):
            self.assertFalse(C.chapter_two_picture_clock(self.sample(**changes)),changes)
if __name__=='__main__':unittest.main()
