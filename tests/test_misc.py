"""Test a boatload of miscellaneous functionality."""

import sys

from cStringIO import StringIO

from pytest import raises, deprecated_call

import twill

from twill import commands
from twill.errors import TwillAssertionError, TwillException


def test():
    # reset
    commands.reset_browser()

    # get the current browser obj.
    browser = twill.get_browser()
    assert browser is commands.browser

    # check the 'None' value of return code
    assert browser.get_code() is None

    # no forms, right?
    with raises(TwillException):
        browser.submit()

    assert browser is deprecated_call(twill.get_browser_state)

    old_err, sys.stderr = sys.stderr, StringIO()
    try:
        with raises(TwillException):
            browser.go('http://...')  # what's a good "nowhere"?!?
    finally:
        sys.stderr = old_err

    with raises(SystemExit):
        commands.exit()

    with raises(TwillAssertionError):
        commands.reset_browser()
        commands.showhistory()
        commands.tidy_ok()
        commands.show()

    commands.debug('http', '1')
    commands.debug('http', '0')
    commands.debug('http', '+')
    commands.debug('http', '-')
    
    commands.debug('commands', '0')
    commands.debug('commands', '1')
    with raises(TwillException):
        commands.debug('nada', '1')

    commands.config()

    commands.config('readonly_controls_writeable')

    commands.config('readonly_controls_writeable', 1)
    commands.config('readonly_controls_writeable', 'on')
    with raises(TwillException):
        commands.config('readonly_controls_writeable', 'nada')

    commands.run("print 'hello'")

