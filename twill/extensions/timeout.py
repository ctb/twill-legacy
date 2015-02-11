"""
An extension to set a script-wide timeout.

Commands:

   set_timeout: Sets the script-wide (integer) timeout setting
   cancel_timeout: Cancels the current timeout timer.
                   Useful for setting timeouts on a step-by-step basis.

"""

__all__ = ['set_timeout', 'cancel_timeout']

def _timeout_handler(signum, frame):
    from twill.errors import TwillTimeoutError
    raise TwillTimeoutError('Script timed out.')

def set_timeout(timeout):
    import signal
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(int(timeout))

def cancel_timeout():
    import signal
    signal.alarm(0)