from pytest import raises

import twill
from twill import namespaces, commands
from twill.errors import TwillAssertionError, TwillException

from .utils import execute_script


def test(url):
    # test empty page title
    namespaces.new_local_dict()
    twill.commands.reset_browser()
    browser = twill.browser
    with raises(TwillException):
        browser.title

    # now test a few special cases
    commands.go(url)
    assert browser.title == 'Hello, world!'

    commands.go('/login')
    assert browser.title is None

    # test no matching forms
    with raises(TwillAssertionError):
        commands.fv('2', 'submit', '1')

    # test regex match
    commands.fv('1', '.*you', '1')

    # test ambiguous match to value
    commands.go('/testform')
    commands.fv('1', 'selecttest', 'val')
    commands.fv('1', 'selecttest', 'value1')
    commands.fv('1', 'selecttest', 'selvalue1')
    commands.formclear('1')
    commands.showforms()
    with raises(TwillException):
        commands.fv('1', 'selecttest', 'value')
    # test ambiguous match to name
    commands.go('/testform')
    with raises(TwillException):
        commands.fv('1', 'item_', 'value')

    with raises(TwillException):
        commands.formfile('1', 'selecttest', 'null')

    # test the twill script.
    execute_script('test_form.twill', initial_url=url)
