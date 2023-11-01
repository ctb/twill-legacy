import pytest
from twill import utils
from twill.errors import TwillException


def test_make_boolean():
    make_boolean = utils.make_boolean
    assert make_boolean(True)  # noqa: FBT003
    assert not make_boolean(False)  # noqa: FBT003
    assert make_boolean("true")
    assert not make_boolean("false")
    assert make_boolean(1)
    assert not make_boolean(0)
    assert make_boolean("1")
    assert not make_boolean("0")
    assert make_boolean("+")
    assert not make_boolean("-")
    with pytest.raises(TwillException):
        make_boolean("no")


def test_trunc():
    trunc = utils.trunc
    assert trunc("hello, world!", 12) == "hello, w ..."
    assert trunc("hello, world!", 13) == "hello, world!"
