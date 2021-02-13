from pytest import raises

import twill
from twill import browser, commands, namespaces
from twill.errors import TwillException


def test_switch_buttons(url):
    namespaces.new_local_dict()
    twill.commands.reset_browser()

    with raises(TwillException):
        browser.title

    commands.go(url)
    commands.go('/test_radiobuttons')

    commands.submit()
    assert 'RADIOBUTTONTEST' not in browser.html

    for x in ('one', 'two', 'three'):
        commands.fv('1', 'radiobuttontest', x)
        commands.submit()
        assert f'RADIOBUTTONTEST: =={x}==' in browser.html
