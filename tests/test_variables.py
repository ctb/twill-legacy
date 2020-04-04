from pytest import raises

from twill import parse

from .utils import execute_script


def test_variable_substitution():
    fut = parse.variable_substitution
    args = (dict(foo=7), dict(bar=13, baz='wall'))
    assert fut("${foo} * ${bar} bottles on the ${baz}!",
               *args) == "7 * 13 bottles on the wall!"
    assert fut("${foo * bar}", *args) == str(7 * 13)
    with raises(ZeroDivisionError):
        fut("${1/0}", {}, {})


def test_variables_script(url):
    execute_script('test_variables.twill', initial_url=url)
