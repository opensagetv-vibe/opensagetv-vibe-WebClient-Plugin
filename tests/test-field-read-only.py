#!/usr/bin/env python3
"""No live imports/server access: field observers must use GET for settings."""
import ast,unittest
from pathlib import Path
from urllib.parse import urlencode,urlparse,parse_qs
ROOT=Path(__file__).resolve().parents[1]
class Recorder:
    def __init__(self):self.calls=[]
    def request(self,*args,**kwargs):self.calls.append((args,kwargs));return {}
class FieldReadOnly(unittest.TestCase):
    def test_observer_methods(self):
        for file in ('stock-copy-recovery-field.py','stock-uk-caption-field.py','stock-current-video-field.py','stock-legacy-caption-field.py'):
            with self.subTest(file=file):
                tree=ast.parse((ROOT/'tests'/file).read_text(encoding='utf-8'))
                helper=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='api')
                recorder=Recorder();ns={'C':recorder,'cfg':{},'owned':'synthetic-owned-id','urlencode':urlencode}
                exec(compile(ast.Module(body=[helper],type_ignores=[]),file,'exec'),ns)
                for action in ('status','streamSettings'):
                    ns['api'](action)
                    args,kwargs=recorder.calls[-1]
                    self.assertEqual(len(args),2,'Read-only observation must not include a POST body')
                    query=parse_qs(urlparse(args[1]).query)
                    self.assertEqual(query['action'],[action]);self.assertEqual(query['session'],['synthetic-owned-id'])
                ns['api']('stop');args,kwargs=recorder.calls[-1]
                self.assertEqual(args[2],{'action':'stop','session':'synthetic-owned-id'})
if __name__=='__main__':unittest.main()
