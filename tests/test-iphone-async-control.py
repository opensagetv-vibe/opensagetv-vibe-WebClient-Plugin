"""Paired inspector's asyncio pump must stay alive during public HTTP controls."""
import ast,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class AsyncControlTests(unittest.TestCase):
 def test_no_blocking_public_controls_inside_async_observer(self):
  for name in ('iphone-uk-caption-life.py','iphone-long-source-field.py','iphone-real-dvd-gate.py','iphone-experience-field.py'):
   with self.subTest(script=name):
    tree=ast.parse((ROOT/'scripts'/name).read_text(encoding='utf-8'))
    bad=[]
    for function in ast.walk(tree):
     if not isinstance(function,ast.AsyncFunctionDef):continue
     for call in ast.walk(function):
      if isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and call.func.id in ('mcp','guard','api'):
       bad.append(call.lineno)
    self.assertEqual([],bad,'Use await asyncio.to_thread; never stall paired inspector transport')
if __name__=='__main__':unittest.main()
