import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from playback_activity import observe_activity


class PlaybackActivity(unittest.TestCase):
    def value(self, **changes):
        return dict(ok=True, recordingCount=0, uiContextCount=0,
                    connectedClientCount=0, safeToRestart=False, **changes)

    def test_known_multiple_clients_are_not_restart_requests(self):
        value=self.value();value.update(uiContextCount=2,connectedClientCount=3)
        result=observe_activity(value,require_other_client=True)
        self.assertTrue(result['coTenancyObserved'])
        self.assertEqual(result['resourceScope'],'shared-server')
        self.assertFalse(value['safeToRestart'])

    def test_existing_recordings_are_preserved_as_shared_load(self):
        value=self.value();value['recordingCount']=1
        self.assertTrue(observe_activity(value)['coTenancyObserved'])

    def test_explicit_isolation_stays_strict(self):
        for key in ('recordingCount','uiContextCount','connectedClientCount'):
            value=self.value();value[key]=1
            with self.assertRaises(RuntimeError):observe_activity(value,require_isolation=True)
        self.assertFalse(observe_activity(self.value(),require_isolation=True)['coTenancyObserved'])

    def test_unknown_counts_never_mean_idle(self):
        for bad in (None,-1,False,True,'0'):
            for key in ('recordingCount','uiContextCount','connectedClientCount'):
                value=self.value();value[key]=bad
                with self.assertRaises(RuntimeError):observe_activity(value)
        for value in ({},None,dict(self.value(),ok=False)):
            with self.assertRaises(RuntimeError):observe_activity(value)

    def test_concurrency_requirement_is_not_fabricated(self):
        with self.assertRaises(RuntimeError):observe_activity(self.value(),require_other_client=True)

    def test_elapsed_requests_are_rejected_before_any_playback(self):
        source=Path(__file__).with_name('stock-long-recording-field.py').read_text(encoding='utf-8')
        tree=ast.parse(source)
        guard=next(node for node in tree.body if isinstance(node,ast.If)
                   and ast.unparse(node.test)=='a.elapsed_soak_seconds')
        class Parser:
            def error(self,message):raise ValueError(message)
        for duration in (7200,10800):
            with self.assertRaisesRegex(ValueError,'Multi-hour testing removed'):
                exec(compile(ast.Module(body=[guard],type_ignores=[]),'<actual elapsed guard>','exec'),
                     dict(a=SimpleNamespace(elapsed_soak_seconds=duration),p=Parser()))

    def test_owned_field_controls_do_not_require_restart_idle(self):
        source=Path(__file__).with_name('stock-multiclient-captions.py').read_text(encoding='utf-8')
        ast.parse(source)
        self.assertNotIn('safeToRestart',source)
        for token in ('ids.intersection(existing[\'contexts\'])','observe_activity(C.activity(cfg))',
                      '--coexistence-check','--source-changes','--require-other-client',
                      "if a.api('streamSettings').get('session')!=producer"):
            self.assertIn(token,source)
        self.assertLess(source.index('self.native_stop_intent=True'),source.index("if not mcp('media.control'"))
        self.assertLess(source.index('self.session_stop_intent=True'),source.index("if not C.request(cfg,'/SageTVWebPlayer/api/miniclient',dict(action='stop'"))

    def test_unknown_stop_receipts_are_not_replayed_by_cleanup(self):
        source=Path(__file__).with_name('stock-multiclient-captions.py').read_text(encoding='utf-8')
        cls=next(n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name=='Client')
        method=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='retire')
        for native in (True,False):
            calls=[]
            def mcp(action,**values):
                if action=='ui.state':return dict(fullyLoaded=native)
                calls.append('native-stop');raise TimeoutError('unknown native receipt')
            def request(*args,**kwargs):
                calls.append('ui-stop');raise TimeoutError('unknown UI receipt')
            ns=dict(guard=lambda:None,mcp=mcp,C=SimpleNamespace(request=request),cfg={})
            exec(compile(ast.Module(body=[method],type_ignores=[]),'<actual retirement>','exec'),ns)
            client=SimpleNamespace(owned='test-owned',identity='test-id',context=None,
                                   native_stop_intent=False,session_stop_intent=False)
            with self.assertRaises(TimeoutError):ns['retire'](client)
            with self.assertRaisesRegex(RuntimeError,'do not replay'):ns['retire'](client)
            self.assertEqual(calls,['native-stop' if native else 'ui-stop'])


if __name__=='__main__':unittest.main()
