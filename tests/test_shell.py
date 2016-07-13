"""Same as test_basic, but using the command interpreter."""

import os

from pytest import raises

from twill.errors import TwillNameError
from .utils import execute_shell, test_dir


def test_shell_specific(url):
    execute_shell('test_shell.twill', initial_url=url, fail_on_unknown=True)


def test_shell_fail(url):
    with raises(TwillNameError):
        execute_shell('test_shell_fail.twill', initial_url=url,
                      fail_on_unknown=True)


def test_most_commands(url):
    inp = "unique1\nunique2\n"
    execute_shell('test_basic.twill', inp, initial_url=url)


def teardown_module():
    for filename in 'test_basic.cookies', 'test_basic.out', 'test_shell.out':
        try:
            os.unlink(os.path.join(test_dir, filename))
        except OSError:
            pass
