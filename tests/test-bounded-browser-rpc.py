import signal,time,unittest
from bounded_browser_rpc import bounded

class BoundedBrowserTests(unittest.TestCase):
    def test_result_and_timer_restored(self):
        prior=signal.getsignal(signal.SIGALRM)
        self.assertEqual(17,bounded(lambda:17))
        self.assertEqual(prior,signal.getsignal(signal.SIGALRM))
        self.assertEqual((0.0,0.0),signal.getitimer(signal.ITIMER_REAL))

    def test_timeout_no_replay(self):
        calls=[]
        def hung():
            calls.append('one observation');time.sleep(.2)
        with self.assertRaises(TimeoutError):bounded(hung,seconds=.01)
        self.assertEqual(['one observation'],calls)
        self.assertEqual((0.0,0.0),signal.getitimer(signal.ITIMER_REAL))

    def test_original_exception_propagated(self):
        def failed():raise ValueError('original')
        with self.assertRaisesRegex(ValueError,'original'):bounded(failed)
        self.assertEqual((0.0,0.0),signal.getitimer(signal.ITIMER_REAL))

if __name__=='__main__':unittest.main()
