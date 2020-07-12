"""Test the utils.run_tidy function.

This doesn't test to see if tidy was actually run; all it does is make sure
that the function runs without error...
"""

from twill import utils
from twill.commands import config


bad_html = """<a href="test">you</a> <b>hello."""


def setup_module():
    config('require_tidy', 1)


def teardown_module():
    config('require_tidy', 0)


def test_bad_html():
    (output, errors) = utils.run_tidy(bad_html)
    assert errors
    (output, errors) = utils.run_tidy(output)
    assert not errors


def test_no_tidylib():
    tidylib, utils.tidylib = utils.tidylib, None
    try:
        try:
            utils.run_tidy(bad_html)
        except Exception:
            pass
        else:
            assert False, 'bad HTML should raise error'
    finally:
        utils.tidylib = tidylib


def test_no_tidylib_but_not_required():
    config('require_tidy', 0)
    tidylib, utils.tidylib = utils.tidylib, None
    try:
        output, errors = utils.run_tidy(bad_html)
    finally:
        utils.tidylib = tidylib

    assert output is None
    assert errors is None
    config('require_tidy', 1)


def test_tidy_options():
    good_content = '<h1>Hello, World!</h1>'
    (output, errors) = utils.run_tidy(good_content)
    assert errors
    config('tidy_show_body_only', 1)
    (output, errors) = utils.run_tidy(good_content)
    assert not errors
    config('tidy_show_body_only', 0)
    (output, errors) = utils.run_tidy(good_content)
    assert errors


if __name__ == '__main__':
    setup_module()
    test_bad_html()
    teardown_module()
