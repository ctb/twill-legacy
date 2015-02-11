"""
An extension to set a script-wide timeout.

Commands:

   set_timeout: sets the script-wide (integer) timeout setting
"""

__all__ = ['set_timeout']

def _timeout_handler(signum, frame):
    from twill.errors import TwillTimeoutError
    raise TwillTimeoutError('Script timed out.')

def set_timeout(timeout):
    import signal
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(int(timeout))