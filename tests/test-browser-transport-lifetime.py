from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
JAVA=ROOT/'src/main/java/org/opensagetv/webplayer'
class LifetimeContracts(unittest.TestCase):
    def test_stream_detach_is_finally_and_generation_scoped(self):
        s=(JAVA/'MiniClientServlet.java').read_text(encoding='utf-8')
        self.assertIn('long browserTicket=s.openBrowserStream()',s)
        self.assertIn('finally{s.detachBrowserStream(browserTicket);}',s)
    def test_status_is_not_a_heartbeat(self):
        s=(JAVA/'MiniClientServlet.java').read_text(encoding='utf-8')
        self.assertIn('if("state".equals(action))s.browserActivity();',s)
        self.assertIn('if("status".equals(action)){json(resp,s.json());return;}',s)
        self.assertNotIn('s.browserActivity();json(resp,s.json())',s)
    def test_cleanup_and_background_delivery_hooks_are_present(self):
        s=(JAVA/'MiniClientSessionManager.java').read_text(encoding='utf-8')
        self.assertIn('REAPER.shutdownNow()',s)
        self.assertIn('SESSIONS.remove(entry.getKey(),session)',s)
        self.assertIn('out.flush();\n            httpStatus=200;delivered=data.length;\n            HlsSessionManager.browserMediaRead(sessionId);',(JAVA/'HlsFileServlet.java').read_text(encoding='utf-8'))
        self.assertIn('s.lastBrowserMediaReadNs=System.nanoTime()', (JAVA/'ContinuousStreamServlet.java').read_text(encoding='utf-8'))
    def test_field_gate_observes_real_resources_before_and_after(self):
        s=(ROOT/'tests/stock-dvd-lifecycle.py').read_text(encoding='utf-8')
        self.assertIn("('explicit-exit','reload','page-close')",s)
        self.assertIn("live_spools!=['present']*len(producers)",s)
        self.assertIn('Require active encoder before disconnect',s)
        self.assertNotIn('kill',s.replace('forced process kills','').replace('kill an encoder',''))
        self.assertNotIn('media.seek',s)
        self.assertIn("body.get('session')===id",s)
        self.assertIn('Lost-beacon fault did not execute; no expiry PASS',s)
        self.assertIn('page.close(run_before_unload=True)',s)
if __name__=='__main__':unittest.main()
