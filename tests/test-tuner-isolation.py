"""Synthetic observer guard tests, not real phone/tuner acceptance."""
import importlib.util,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('tuner_isolation',ROOT/'scripts/verify-tuner-isolation.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class IsolationTest(unittest.TestCase):
    def exercise(self,mutate=None,channels=('2.1','5.1'),fail=None):
        now=[0.0];producer='a'*32
        def request(cfg,path):
            self.assertEqual(path,'/SageTVWebPlayer/api/support?action=streamHealth')
            s=dict(atMs=1000000+now[0]*1000,mediaId=12,browserRevision='web121.4',
                processAlive=True,recording=True,browserEnded=False,intentPaused=False,
                browserFeedbackAgeMs=50,nativeTransportError='none',inputError='none',
                inputBytes=100+int(now[0]*100000),browserTimeMs=2000+int(now[0]*1000),
                bufferAheadMs=2000,browserRecoveryAttempts=0)
            if mutate:mutate(s,now[0])
            return {'sessions':[{'session':producer,'samples':[s]}]}
        class Reply:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self):return json.dumps([{'Resource':'tuner0','VctNumber':channels[0]},
                {'Resource':'tuner3','VctNumber':channels[1]}]).encode()
        def sleep(seconds):now[0]+=seconds
        with tempfile.TemporaryDirectory() as tmp,patch.object(m,'ROOT',Path(tmp)),\
            patch.object(m.runpy,'run_path',return_value={'configuration':lambda:{},'request':request}),\
            patch.object(m,'urlopen',return_value=Reply()),\
            patch.object(m.time,'monotonic',side_effect=lambda:now[0]),\
            patch.object(m.time,'time',side_effect=lambda:1000+now[0]),\
            patch.object(m.time,'sleep',side_effect=sleep),\
            patch.object(sys,'argv',['observer','--producer',producer,'--media-id','12']),\
            patch('builtins.print'):
            if fail:
                with self.assertRaisesRegex(RuntimeError,fail):m.main()
            else:m.main()
            reports=list(Path(tmp).rglob('*-isolated-live.json'));self.assertEqual(len(reports),1)
            report=json.loads(reports[0].read_text());self.assertEqual(report['passed'],not bool(fail))
            return report

    def test_actual_progress_required(self):
        self.assertEqual(len(self.exercise()['samples']),11)
    def test_changed_owner_state_preserved(self):
        self.exercise(lambda s,t:s.update(processAlive=False),fail='state changed')
    def test_tuner_theft_detected(self):
        self.exercise(channels=('5.1','5.1'),fail='channels changed')
    def test_stale_browser_rejected(self):
        self.exercise(lambda s,t:s.update(browserFeedbackAgeMs=6000),fail='fresh phone')
    def test_frozen_source_rejected(self):
        self.exercise(lambda s,t:s.update(inputBytes=10),fail='did not advance')
    def test_recovery_is_not_continuity(self):
        self.exercise(lambda s,t:s.update(browserRecoveryAttempts=int(t>30)),fail='Recovery count increased')
    def test_wrong_revision_rejected(self):
        self.exercise(lambda s,t:s.update(browserRevision='unknown'),fail='revision changed')

if __name__=='__main__':unittest.main()
