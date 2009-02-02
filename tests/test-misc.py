"""
Test a boatload of miscellaneous functionality.
"""

import sys
import twilltestlib
import twill, twill.browser, twill.commands
from cStringIO import StringIO
from twill.errors import TwillAssertionError
import urllib2

def setup_module():
    pass

def ensure_fail_on_gopher_import():
    try:
        from mechanize import GopherError
        assert 0, "GopherError and gopherlib are no longer in python 2.6"
    except ImportError:
        pass

def test():
    # reset
    twill.commands.reset_browser()

    # get the current browser obj.
    browser = twill.get_browser()
    assert browser is twill.commands.browser

    # check the 'None' value of return code
    assert browser.get_code() is None

    # no forms, right?
    try:
        browser.submit()
    except Exception:
        pass

    try:
        import warnings
        warnings.filterwarnings('ignore')
        assert browser is twill.get_browser_state() # deprecated
        warnings.resetwarnings()
    except DeprecationWarning:
        pass

    old_err, sys.stderr = sys.stderr, StringIO()
    try:
        try:
            browser.go('http://') # what's a good "nowhere"?!?
            assert 0, "shouldn't get here"
        except:
            pass
    finally:
        sys.stderr = old_err

    try:
        twill.commands.exit()
        assert 0, "shouldn't get here"
    except SystemExit:
        pass

    try:
        twill.commands.reset_browser()
        twill.commands.showhistory()
        twill.commands.tidy_ok()
        twill.commands.show()
        assert 0, "shouldn't get here!" # no page!
    except TwillAssertionError:
        pass

    twill.commands.debug('http', '1')
    twill.commands.debug('http', '0')
    twill.commands.debug('http', '+')
    twill.commands.debug('http', '-')
    
    twill.commands.debug('commands', '0')
    twill.commands.debug('commands', '1')
    try:
        twill.commands.debug('nada', '1')
        assert 0
    except:
        pass

    twill.commands.config()
    twill.commands.config('readonly_controls_writeable')
    twill.commands.config('use_tidy')
    twill.commands.config('require_tidy')
    
    twill.commands.config('readonly_controls_writeable', 1)
    twill.commands.config('use_tidy', 1)
    twill.commands.config('require_tidy', 0)
    
    twill.commands.config('require_tidy', "on")

    twill.commands.run("print 'hello'")

def teardown_module():
    pass
