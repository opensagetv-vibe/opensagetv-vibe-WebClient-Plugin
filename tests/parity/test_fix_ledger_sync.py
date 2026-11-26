"""Current checklist resolution must never rewrite historical proof or scope."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('ledger_sync', ROOT / 'scripts/reconcile-fix-ledger.py')
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)


class LedgerTests(unittest.TestCase):
    def fixture(self, category='required', targets=None):
        return {'entries': [{'id': 'UP-0001', 'category': category,
                'target_task_ids': targets or ['WP01-001'],
                'implementation_status': 'NOT_PORTED', 'reason': 'Pinned reason',
                'evidence': ['original.json']}]}

    def test_checked_is_scoped_not_field_pass(self):
        original = self.fixture()
        result = S.reconcile('- [x] **WP01-001**\n', original)
        row = result['entries'][0]
        self.assertEqual(row['current_resolution']['state'], 'TARGET_TASKS_COMPLETE_SCOPED')
        self.assertIn('No inferred physical', row['current_resolution']['boundary'])
        for field in ('implementation_status', 'reason', 'evidence'):
            self.assertEqual(row[field], original['entries'][0][field])
        self.assertNotIn('current_resolution', original['entries'][0])

    def test_mixed_targets_remain_partial(self):
        result = S.reconcile('- [x] **WP01-001**\n- [ ] **WP01-002**\n',
                             self.fixture(targets=['WP01-001', 'WP01-002']))
        current = result['entries'][0]['current_resolution']
        self.assertEqual(current['state'], 'TARGET_TASKS_PARTIAL')
        self.assertEqual(current['open_targets'], ['WP01-002'])

    def test_open_target_does_not_complete_from_implementation_label(self):
        result = S.reconcile('- [ ] **WP01-001**\n **Status:** PASS_LOCAL\n', self.fixture())
        self.assertEqual(result['entries'][0]['current_resolution']['state'], 'TARGET_TASKS_OPEN')

    def test_reference_categories_retain_boundary(self):
        for category, expected in [('not_applicable', 'NOT_APPLICABLE_RETAIN_REASON'),
                                   ('superseded', 'SUPERSEDED_RETAIN_REASON'),
                                   ('optional_core', 'OPTIONAL_NOT_AUTHORIZED')]:
            result = S.reconcile('- [x] **WP01-001**\n', self.fixture(category))
            self.assertEqual(result['entries'][0]['current_resolution']['state'], expected)

    def test_invalid_mapping_or_duplicates_refuse(self):
        for source in ('- [x] **WP01-002**\n', '- [x] **WP01-001**\n- [ ] **WP01-001**\n'):
            with self.assertRaises(ValueError):
                S.reconcile(source, self.fixture())
        fixture = self.fixture()
        fixture['entries'].append(dict(fixture['entries'][0]))
        with self.assertRaises(ValueError):
            S.reconcile('- [x] **WP01-001**\n', fixture)

    def test_current_ledger_matches_canonical(self):
        current = json.loads((ROOT / 'docs/parity/UPSTREAM_FIX_LEDGER.json').read_text(encoding='utf-8'))
        self.assertEqual(S.reconcile((ROOT / 'TASKS.md').read_text(encoding='utf-8'), current), current)

    def test_removed_target_is_not_open_or_pass(self):
        result = S.reconcile('- [-] **WP01-001**\n', self.fixture())
        current = result['entries'][0]['current_resolution']
        self.assertEqual(current['state'], 'TARGET_TASKS_CLOSED_WITH_USER_WAIVERS')
        self.assertEqual(current['completed_targets'], [])
        self.assertEqual(current['open_targets'], [])
        self.assertEqual(current['removed_targets'], ['WP01-001'])

    def test_removed_target_does_not_hide_unrelated_open_target(self):
        result = S.reconcile('- [-] **WP01-001**\n- [ ] **WP01-002**\n',
                             self.fixture(targets=['WP01-001', 'WP01-002']))
        current = result['entries'][0]['current_resolution']
        self.assertEqual(current['state'], 'TARGET_TASKS_PARTIAL')
        self.assertEqual(current['open_targets'], ['WP01-002'])
        self.assertEqual(current['completed_targets'], [])
    def test_starred_observation_is_not_open_complete_or_waived(self):
        original=self.fixture()
        result=S.reconcile('- [*] **WP01-001**\n',original)
        current=result['entries'][0]['current_resolution']
        self.assertEqual(current['state'],'TARGET_TASKS_WITH_FLAGGED_OBSERVATIONS')
        self.assertEqual(current['completed_targets'],[])
        self.assertEqual(current['open_targets'],[])
        self.assertEqual(current['flagged_targets'],['WP01-001'])
        self.assertNotIn('removed_targets',current)
        self.assertIn('not a proven correction',current['boundary'])
        self.assertEqual(result['entries'][0]['implementation_status'],original['entries'][0]['implementation_status'])
    def test_star_does_not_hide_other_active_work(self):
        result=S.reconcile('- [*] **WP01-001**\n- [ ] **WP01-002**\n',self.fixture(targets=['WP01-001','WP01-002']))
        current=result['entries'][0]['current_resolution']
        self.assertEqual(current['state'],'TARGET_TASKS_PARTIAL')
        self.assertEqual(current['open_targets'],['WP01-002'])
        self.assertEqual(current['flagged_targets'],['WP01-001'])


if __name__ == '__main__':
    unittest.main()
