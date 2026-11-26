"""Linux field-runner RPC timeout; never retries browser inputs or observations."""
import signal

def bounded(call,*args,seconds=12,**kwargs):
    def expired(_number,_frame):
        raise TimeoutError('Browser RPC exceeded bounded field observation')
    prior=signal.signal(signal.SIGALRM,expired)
    timer=signal.setitimer(signal.ITIMER_REAL,seconds)
    try:
        return call(*args,**kwargs)
    finally:
        signal.setitimer(signal.ITIMER_REAL,*timer)
        signal.signal(signal.SIGALRM,prior)
