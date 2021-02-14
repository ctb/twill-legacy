"""Test a boatload of miscellaneous functionality."""

import sys

from io import StringIO

from pytest import raises

from twill import browser, commands
from twill.browser import TwillBrowser
from twill.errors import TwillAssertionError, TwillException


def test():
    assert isinstance(browser, TwillBrowser)

    # reset
    commands.reset_browser()
    assert isinstance(browser, TwillBrowser)

    # check the 'None' value of return code
    assert browser.code is None

    # no forms, right?
    with raises(TwillException):
        browser.submit()

    stderr, sys.stderr = sys.stderr, StringIO()
    try:
        with raises(TwillException):
            browser.go('http://0.0.0.0')  # URL parses, but is invalid
    finally:
        sys.stderr = stderr

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

    commands.run("print('Hello!')")
