from pathlib import Path
import unittest

class FieldContract(unittest.TestCase):
    def test_menu_receipt_is_not_old_menu_picture_acceptance(self):
        s=(Path(__file__).resolve().parents[1]/'scripts/iphone-dvd-audio-title-gate.py').read_text(encoding='utf-8')
        helper=s.split('async def menu_transition(',1)[1].split('async def authored_audio(',1)[0]
        self.assertIn("await checkpoint();await native(command)",helper)
        for guard in ("r['sourceChanged']","r['presented']>=1","r['pixels']>100","n.get('dvdMenu')"):
            self.assertIn(guard,helper)
        for label in ('languages','audio tracks','languages after audio selection','special features'):
            self.assertIn("await menu_transition('Select','"+label+"')",s)
    def test_representative_root_waits_actual_replacement_not_fixed_sleep(self):
        s=(Path(__file__).resolve().parents[1]/'scripts/iphone-real-dvd-gate.py').read_text(encoding='utf-8')
        block=s.split("'authored root domain')",1)[1].split('if options.companion:',1)[0]
        self.assertIn("geometry['epoch']!=baseline['epoch']",block)
        self.assertIn("geometry['frames']>=1",block)
        self.assertIn("row['rootHighlightLast']=geometry",block)
        self.assertIn('time.monotonic()+20',block)
        self.assertNotIn('await asyncio.sleep(2)',block)
    def test_explicit_soak_has_bounded_real_source_and_same_epoch_oracle(self):
        s=(Path(__file__).resolve().parents[1]/'scripts/iphone-real-dvd-gate.py').read_text(encoding='utf-8')
        for token in ("options.source!='aladdin'",'20<=options.soak_seconds<=600','300+options.soak_seconds',"b['epoch']!=a['epoch']",'presentation_speed(a,b,wall_seconds)',"n.get('mediaTimeMs',0)>500"):
            self.assertIn(token,s)
if __name__=='__main__':unittest.main()
