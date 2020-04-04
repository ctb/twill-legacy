from pytest import raises

import twill
from twill import browser, commands, namespaces
from twill.errors import TwillException


def test_select_multiple(url):
    namespaces.new_local_dict()
    twill.commands.reset_browser()

    with raises(TwillException):
        browser.title

    commands.go(url)
    commands.go('/test_checkboxes')

    commands.fv('1', 'checkboxtest', 'one')
    commands.fv('1', 'checkboxtest', 'two')
    commands.fv('1', 'checkboxtest', 'three')

    commands.fv('1', 'checkboxtest', '-one')
    commands.fv('1', 'checkboxtest', '-two')
    commands.fv('1', 'checkboxtest', '-three')

    commands.submit()
    assert 'CHECKBOXTEST' not in browser.html

    commands.fv('1', 'checkboxtest', '+one')
    commands.fv('1', 'checkboxtest', '+two')
    commands.fv('1', 'checkboxtest', '+three')

    commands.submit()
    assert 'CHECKBOXTEST: ==one,two,three==' in browser.html

    commands.fv('1', 'checkboxtest', '-one')
    commands.fv('1', 'checkboxtest', '-two')
    commands.fv('1', 'checkboxtest', '-three')

    commands.submit()
    assert 'CHECKBOXTEST' not in browser.html


def test_select_single(url):
    namespaces.new_local_dict()
    twill.commands.reset_browser()
    browser = twill.browser
    with raises(TwillException):
        browser.title

    commands.go(url)
    commands.go('/test_checkboxes')

    # Should not be able to use a bool style for when
    # there are multiple checkboxes
    for x in ('1', '0', 'True', 'False'):
        with raises(KeyError):
            commands.fv('1', 'checkboxtest', x)
