"""Explicit idle co-tenancy never grants restart or other-client controls."""
import unittest
from playback_activity import observe_idle_phone_field


class IdlePhoneTests(unittest.TestCase):
    def activity(self, **changes):
        return dict(ok=True, recordingCount=0, connectedClientCount=0, uiContextCount=1, **changes)

    def state(self, name):
        return dict(ok=True, context=name, fullyLoaded=False, loading=False)

    def test_idle_phone_requires_explicit_flag(self):
        with self.assertRaises(RuntimeError):
            observe_idle_phone_field(self.activity(), ['123c8282e1ee'], self.state)

    def test_exact_unloaded_phone_is_not_restart_proof(self):
        result = observe_idle_phone_field(self.activity(), ['123c8282e1ee'], self.state, True)
        self.assertTrue(result['idlePhoneObserved'])
        self.assertFalse(result['safeToRestart'])

    def test_foreign_disposable_or_duplicate_ui_refuses_without_state_query(self):
        def forbidden(name):
            raise AssertionError('No foreign observation/control')
        for contexts in (['other'], ['da92a86446be'], ['123c8282e1ee', '123c8282e1ee']):
            value = self.activity(); value['uiContextCount'] = len(contexts)
            with self.assertRaises(RuntimeError):
                observe_idle_phone_field(value, contexts, forbidden, True)

    def test_active_or_unknown_phone_refuses(self):
        for changes in ({'fullyLoaded': True}, {'loading': True}, {'fullyLoaded': None},
                        {'loading': None}, {'ok': False}, {'context': 'other'}):
            def state(name):
                return {**self.state(name), **changes}
            with self.assertRaises(RuntimeError):
                observe_idle_phone_field(self.activity(), ['123c8282e1ee'], state, True)

    def test_recording_native_client_and_unknown_counts_refuse(self):
        for change in ({'recordingCount': 1}, {'connectedClientCount': 1},
                       {'uiContextCount': 0}, {'uiContextCount': None}, {'recordingCount': False}):
            value = {**self.activity(), **change}
            with self.assertRaises(RuntimeError):
                observe_idle_phone_field(value, ['123c8282e1ee'], self.state, True)

    def test_empty_slot_needs_no_phone_override(self):
        value = self.activity(); value['uiContextCount'] = 0
        result = observe_idle_phone_field(value, [], self.state)
        self.assertFalse(result['idlePhoneObserved'])
        self.assertFalse(result['safeToRestart'])


if __name__ == '__main__':
    unittest.main()
