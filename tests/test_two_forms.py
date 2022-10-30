from pytest import raises

from twill import commands
from twill.errors import TwillException


def test(url):
    commands.go('/two_forms')
    commands.find(' NO FORM ')

    with raises(TwillException):
        commands.submit()
    with raises(TwillException):
        commands.submit('1')

    commands.fv('1', 'item', 'foo')
    commands.submit()
    commands.find(' FORM=1 ITEM=foo ')

    commands.fv('2', 'item', 'bar')
    commands.submit()
    commands.find(' FORM=2 ITEM=bar ')

    with raises(TwillException):
        commands.submit()

    commands.submit('1', '1')
    commands.find(' FORM=1 ITEM= ')

    commands.submit('1', '2')
    commands.find(' FORM=2 ITEM= ')

    with raises(TwillException):
        commands.submit('1', '3')

    commands.fv('1', 'item', 'foo')
    commands.fv('2', 'item', 'bar')
    commands.submit()
    commands.find(' FORM=2 ITEM=bar ')

    commands.fv('2', 'item', 'bar')
    commands.fv('1', 'item', 'foo')
    commands.submit()
    commands.find(' FORM=1 ITEM=foo ')
