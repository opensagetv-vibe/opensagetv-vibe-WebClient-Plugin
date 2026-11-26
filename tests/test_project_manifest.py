"""Do not omit newly implemented modules from the pre-commit source manifest."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase,main
from unittest.mock import patch

root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('project_manifest',root/'scripts/project_manifest.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class ManifestInventoryTest(TestCase):
    def test_new_untracked_source_is_included_without_staging_or_global_trust(self):
        with patch.object(module.subprocess,'run',return_value=SimpleNamespace(stdout=b'old.java\0new.java\0PROJECT_MANIFEST.sha256\0old.java\0')) as run:
            self.assertEqual(['new.java','old.java'],module.tracked(root))
        argv=run.call_args.args[0]
        for value in ('--cached','--others','--exclude-standard',f'safe.directory={root}'):
            self.assertIn(value,argv)

if __name__=='__main__':main()
