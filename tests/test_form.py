import pytest
import twill
from twill import commands, namespaces
from twill.errors import TwillAssertionError, TwillException

from .utils import execute_script


def test(url: str):
    # test empty page title
    namespaces.new_local_dict()
    commands.reset_browser()
    browser = twill.browser
    with pytest.raises(TwillException):
        browser.title  # noqa: B018

    # now test a few special cases
    commands.go(url)
    assert browser.title == "Hello, world!"

    commands.go("/login")
    assert browser.title is None

    # test no matching forms
    with pytest.raises(TwillAssertionError):
        commands.fv("2", "submit", "1")

    # test regex match
    commands.fv("1", ".*you", "1")

    # test ambiguous match to value
    commands.go("/testform")
    commands.fv("1", "selecttest", "val")
    commands.fv("1", "selecttest", "value1")
    commands.fv("1", "selecttest", "selvalue1")
    commands.formclear("1")
    commands.showforms()
    with pytest.raises(TwillException):
        commands.fv("1", "selecttest", "value")
    # test ambiguous match to name
    commands.go("/testform")
    with pytest.raises(TwillException):
        commands.fv("1", "item_", "value")

    with pytest.raises(TwillException):
        commands.formfile("1", "selecttest", "null")

    # test the twill script.
    execute_script("test_form.twill", initial_url=url)
