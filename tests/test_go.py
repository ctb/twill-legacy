import os
import sys

from io import StringIO

from pytest import raises

from twill import commands
from twill import namespaces
from twill.errors import TwillAssertionError, TwillNameError
import twill.parse

from .utils import execute_script, test_dir

_log_commands = None


def setup_module():
    global _log_commands
    _log_commands = twill.parse.log_commands(True)


def teardown_module():
    twill.parse.log_commands(_log_commands)


def test(url):
    # capture output
    fp = StringIO()
    twill.set_output(fp)

    twill.parse.execute_string('code 200', initial_url=url)

    # from file
    execute_script('test_go.twill', initial_url=url)

    twill.set_output(None)
    assert fp.getvalue()

    # from stdin
    filename = os.path.join(test_dir, 'test_go.twill')
    stdin, sys.stdin = sys.stdin, open(filename)
    try:
        execute_script('-', initial_url=url)
    finally:
        sys.stdin = stdin

    # from parse.execute_file
    twill.parse.execute_file('test_go_exit.twill', initial_url=url)

    # also test some failures

    stderr, sys.stderr = sys.stderr, StringIO()
    try:
        twill.set_err_out(sys.stderr)
        # failed assert in a script
        with raises(TwillAssertionError):
            twill.parse.execute_file('test_go_fail.twill', initial_url=url)

        commands.go(url)
        with raises(TwillAssertionError):
            commands.code(400)

        # no such command (NameError)
        with raises(TwillNameError):
            twill.parse.execute_file('test_go_fail2.twill', initial_url=url)
    finally:
        sys.stderr = stderr

    namespaces.new_local_dict()
    gd, ld = namespaces.get_twill_glocals()

    commands.go(url)

    with raises(TwillAssertionError):
        twill.parse.execute_command('url', ('not this',), gd, ld, "anony")

    with raises(TwillAssertionError):
        commands.follow('no such link')

    with raises(TwillAssertionError):
        commands.find('no such link')

    with raises(TwillAssertionError):
        commands.notfind('Hello')

    with raises(SystemExit):
        twill.parse.execute_command('exit', ('0',), gd, ld, "anony")
