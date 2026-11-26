"""Canonical checklist status is not inferred physical acceptance."""
import importlib.util,json,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('sync',ROOT/'scripts/reconcile-task-index.py')
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)
class SyncTests(unittest.TestCase):
    def fixture(self):return {'phases':[{'id':'P01','scope':'required','status':'NOT_STARTED','tasks':[{'id':'WP01-001','status':'PLANNED','acceptance':'keep criteria','evidence':[]}]}]}
    def test_local_unchecked_never_becomes_complete(self):
        for label in ['PASS_LOCAL','COMPLETE_LOCAL']:
            result,_=S.reconcile('- [ ] **WP01-001 — test**\n **Status:** '+label+'.\n',self.fixture())
            self.assertEqual(result['phases'][0]['tasks'][0]['status'],'PASS_LOCAL')
    def test_optional_approval_is_not_advanced(self):
        fixture=self.fixture();fixture['phases'][0]['scope']='optional';fixture['phases'][0]['tasks'][0]['status']='AWAITING_SEPARATE_APPROVAL'
        result,_=S.reconcile('- [ ] **WP01-001 — test**\n **Status:** PASS_LOCAL.\n',fixture)
        self.assertEqual(result,fixture)
    def test_explicitly_completed_stock_alternative_can_advance_without_core_approval(self):
        fixture=self.fixture();fixture['phases'][0]['scope']='optional';fixture['phases'][0]['tasks'][0]['status']='AWAITING_SEPARATE_APPROVAL'
        result,_=S.reconcile('- [x] **WP01-001**\n **Status:** COMPLETE_STOCK_ALTERNATIVE.\n',fixture)
        self.assertEqual(result['phases'][0]['tasks'][0]['status'],'COMPLETE_STOCK_ALTERNATIVE')
        self.assertEqual(result['phases'][0]['tasks'][0]['acceptance'],'keep criteria')
    def test_verified_correction_can_complete_a_formerly_starred_phase(self):
        fixture=self.fixture();fixture['phases'][0]['status']='QUALIFIED_SCOPE_WITH_FLAGGED_OBSERVATIONS'
        result,_=S.reconcile('- [x] **WP01-001**\n',fixture)
        self.assertEqual(result['phases'][0]['status'],'COMPLETE_CANONICAL_SCOPE')
    def test_unavailable_stock_contract_is_not_pass_or_an_approval_claim(self):
        fixture=self.fixture();fixture['phases'][0]['scope']='optional';fixture['phases'][0]['tasks'][0]['status']='AWAITING_SEPARATE_APPROVAL'
        result,_=S.reconcile('- [ ] **WP01-001**\n **Status:** UNAVAILABLE_STOCK_CONTRACT.\n',fixture)
        self.assertEqual(result['phases'][0]['tasks'][0]['status'],'UNAVAILABLE_STOCK_CONTRACT')
        self.assertEqual(result['phases'][0]['tasks'][0]['acceptance'],'keep criteria')
    def test_checked_preserves_scope_and_acceptance(self):
        for phase_status in ('NOT_STARTED','IMPLEMENTED_LOCAL_AWAITING_FIELD','IN_PROGRESS_FIELD_ACCEPTANCE'):
            fixture=self.fixture();fixture['phases'][0]['status']=phase_status
            result,changes=S.reconcile('- [x] **WP01-001 — test**\n',fixture)
            self.assertEqual(result['phases'][0]['tasks'][0]['status'],'COMPLETE_LOCAL')
            self.assertEqual(result['phases'][0]['tasks'][0]['acceptance'],'keep criteria')
            self.assertEqual(result['phases'][0]['status'],'COMPLETE_CANONICAL_SCOPE')
            self.assertEqual(fixture['phases'][0]['tasks'][0]['status'],'PLANNED')
            self.assertTrue(changes)
    def test_duplicate_or_missing_id_refuses(self):
        for source in ['- [x] **WP01-001**\n- [ ] **WP01-001**','- [ ] **WP01-002**']:
            with self.assertRaises(ValueError):S.reconcile(source,self.fixture())
    def test_current_mirror_matches_canonical(self):
        _,changes=S.reconcile((ROOT/'TASKS.md').read_text(encoding='utf-8'),json.loads((ROOT/'docs/parity/TASK_INDEX.json').read_text(encoding='utf-8')))
        self.assertEqual(changes,[])
    def test_counts_and_next_task_follow_canonical_not_old_chat(self):
        fixture=self.fixture();fixture['progress']={'completed':99,'total':99};fixture['next_task']='WP99-999'
        result,_=S.reconcile('- [ ] **WP01-001**\n',fixture)
        self.assertEqual(result['progress'],{'completed':0,'total':1})
        self.assertEqual(result['next_task'],'WP01-001')
        result,_=S.reconcile('- [x] **WP01-001**\n',fixture)
        self.assertEqual(result['progress'],{'completed':1,'total':1})
        self.assertIsNone(result['next_task'])
    def test_dated_partial_or_blocked_status_does_not_become_complete(self):
        for label in ['PARTIAL_AVAILABLE_FIELD','BLOCKED_BASELINE_ARTIFACT','AWAITING_PUBLICATION_APPROVAL']:
            result,_=S.reconcile('- [ ] **WP01-001**\n **Current2026-11-19:** '+label+'.\n',self.fixture())
            self.assertEqual(result['phases'][0]['tasks'][0]['status'],label)
    def test_user_removed_is_not_pass_or_next_task(self):
        fixture=self.fixture();fixture['progress']={'completed':0,'total':1};fixture['next_task']='WP01-001'
        result,_=S.reconcile('- [-] **WP01-001**\n **Status:** REMOVED_USER_REQUEST.\n',fixture)
        self.assertEqual(result['phases'][0]['tasks'][0]['status'],'REMOVED_USER_REQUEST')
        self.assertEqual(result['phases'][0]['status'],'CLOSED_WITH_USER_WAIVERS')
        self.assertEqual(result['progress'],{'completed':0,'total':1,'removed':1})
        self.assertIsNone(result['next_task'])
        self.assertEqual(result['phases'][0]['tasks'][0]['acceptance'],'keep criteria')
    def test_removed_requires_explicit_user_status(self):
        with self.assertRaises(ValueError):S.reconcile('- [-] **WP01-001**\n',self.fixture())
    def test_star_is_not_complete_removed_or_next_retest(self):
        fixture=self.fixture();fixture.update(progress={'completed':0,'total':1},next_task='WP01-001')
        result,_=S.reconcile('- [*] **WP01-001**\n **Status:** POSSIBLY_FIXED_NOT_REPEATABLE.\n',fixture)
        self.assertEqual(result['phases'][0]['tasks'][0]['status'],'POSSIBLY_FIXED_NOT_REPEATABLE')
        self.assertEqual(result['phases'][0]['status'],'QUALIFIED_SCOPE_WITH_FLAGGED_OBSERVATIONS')
        self.assertEqual(result['progress'],{'completed':0,'total':1,'flagged':1})
        self.assertIsNone(result['next_task'])
        self.assertEqual(result['phases'][0]['tasks'][0]['acceptance'],'keep criteria')
    def test_star_requires_explicit_non_repeatable_status(self):
        for source in ('- [*] **WP01-001**\n','- [*] **WP01-001**\n **Status:** COMPLETE_LOCAL.\n'):
            with self.assertRaises(ValueError):S.reconcile(source,self.fixture())
    def test_real_recurrence_reopens_flagged_phase(self):
        fixture=self.fixture();fixture['phases'][0]['status']='QUALIFIED_SCOPE_WITH_FLAGGED_OBSERVATIONS'
        fixture['phases'][0]['tasks'][0]['status']='POSSIBLY_FIXED_NOT_REPEATABLE'
        result,_=S.reconcile('- [ ] **WP01-001**\n **Status:** PARTIAL_AVAILABLE_FIELD.\n',fixture)
        self.assertEqual(result['phases'][0]['status'],'IMPLEMENTED_LOCAL_AWAITING_FIELD')
        self.assertEqual(result['phases'][0]['tasks'][0]['status'],'PARTIAL_AVAILABLE_FIELD')
    def test_publication_hold_is_not_phase_completion(self):
        fixture=self.fixture();fixture['phases'][0]['status']='COMPLETE_CANONICAL_SCOPE'
        result,_=S.reconcile('- [ ] **WP01-001**\n **Status:** AWAITING_PUBLICATION_APPROVAL.\n',fixture)
        self.assertEqual(result['phases'][0]['status'],'AWAITING_PUBLICATION_APPROVAL')
if __name__=='__main__':unittest.main()
