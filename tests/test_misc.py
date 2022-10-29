"""Test a boatload of miscellaneous functionality."""

import sys

from io import StringIO

from pytest import raises

from twill import browser, commands
from twill.errors import TwillException


def test():
    assert browser is not None
    for attr in ('go', 'reset', 'submit'):
        assert hasattr(browser, attr)

    # reset
    commands.reset_browser()
    assert browser is not None
    for attr in ('go', 'reset', 'submit'):
        assert hasattr(browser, attr)

    with raises(TwillException):  # no page and thus no status code yet
        assert browser.code

    with raises(TwillException):  # no page and thus no form yet
        browser.submit()

    stderr, sys.stderr = sys.stderr, StringIO()
    try:
        with raises(TwillException):
            browser.go('http://0.0.0.0')  # URL parses, but is invalid
    finally:
        sys.stderr = stderr

    with raises(SystemExit):
        commands.exit()

    commands.reset_browser()
    commands.showhistory()

    with raises(TwillException):   # no page, cannot tidy yet
        commands.tidy_ok()

    with raises(TwillException):  # no page, cannot show yet
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
