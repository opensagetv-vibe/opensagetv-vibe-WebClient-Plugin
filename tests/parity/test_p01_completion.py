import hashlib, json, pathlib, unittest

ROOT=pathlib.Path(__file__).resolve().parents[2]

class P01CompletionTest(unittest.TestCase):
    def test_literal_and_test_census(self):
        lit=json.loads((ROOT/'docs/parity/p01/LITERAL_CHANGELOG_RECONCILIATION.json').read_text())
        self.assertEqual(1066,lit['literal_top_level_bullets'])
        self.assertEqual(0,lit['unclassified_literal_bullets'])
        tests=json.loads((ROOT/'docs/parity/p01/UPSTREAM_RELEVANT_TESTS.json').read_text())
        self.assertEqual(162,tests['all_test_files_in_tree'])
        self.assertEqual(102,tests['relevant_test_files'])
        self.assertEqual(0,tests['unclassified_relevant_test_files'])
    def test_task_index_and_external_boundary(self):
        idx=json.loads((ROOT/'docs/parity/TASK_INDEX.json').read_text(encoding='utf-8'))
        p1=next(p for p in idx['phases'] if p['id']=='P01')
        by={t['id']:t for t in p1['tasks']}
        self.assertEqual('DONE',by['WP01-001']['status'])
        self.assertEqual('COMPLETE_REAL_PINNED_VENDOR_MSE_STOCK_20261117',by['WP01-004']['status'])
        self.assertEqual('DONE',by['WP01-006']['status'])
        self.assertEqual('COMPLETE_CANONICAL_SCOPE',p1['status'])
        self.assertIn('docs/parity/2026-11-17-ACCEPTANCE.md',by['WP01-004']['evidence'])
    def test_frozen_runtime_record_unchanged(self):
        # The historical baseline remains immutable; the current development
        # WAR is intentionally rebuilt and independently package-verified.
        record=json.loads((ROOT/'docs/parity/p01/PACKAGE_VERIFICATION.json').read_text(encoding='utf-8'))
        self.assertEqual('3.2.4',record['runtime_version'])
        self.assertEqual('069ec4cd1b080f896311e98a63a6c9168bdc9091039f4326e1506f54f965742d',record['runtime_war_sha256'])
        self.assertTrue(record['runtime_war_matches_expected'])
    def test_server_identity_redacted(self):
        d=json.loads((ROOT/'docs/parity/p01/SERVER_IDENTITY.json').read_text())
        self.assertEqual('9.2.10.1054',d['observed_server']['sagetv_version'])
        self.assertTrue(d['observed_server']['active_stv'].endswith('/STVs/SageTV7/SageTV7.xml'))
        self.assertFalse(d['sensitive_data_copied'])

if __name__=='__main__': unittest.main()
