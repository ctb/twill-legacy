import sys, os
import twilltestlib
from twill import commands
from twill import namespaces
from twill.errors import TwillAssertionError, TwillNameError
import twill.parse
from cStringIO import StringIO

def setup_module():
    global _save_print
    _save_print = twill.parse._print_commands
    twill.parse.debug_print_commands(True)

def test():
    url = twilltestlib.get_url()

    # capture output
    fp = StringIO()
    twill.set_output(fp)

    twill.parse.execute_string('code 200', initial_url=url)

    # from file
    twilltestlib.execute_twill_script('test-go.twill', initial_url=url)

    twill.set_output(None)
    assert fp.getvalue()

    ###

    # from stdin
    filename = os.path.join(twilltestlib.testdir, 'test-go.twill')
    old_in, sys.stdin = sys.stdin, open(filename)
    try:
        twilltestlib.execute_twill_script('-', initial_url=url)
    finally:
        sys.stdin = old_in

    # from parse.execute_file
    twill.parse.execute_file('test-go-exit.twill', initial_url=url)
    
    # also test some failures.

    old_err, sys.stderr = sys.stderr, StringIO()
    try:
        twill.set_errout(sys.stderr)
        #
        # failed assert in a script
        #
        try:
            twill.parse.execute_file('test-go-fail.twill', initial_url=url)
            assert 0
        except TwillAssertionError:
            pass

        commands.go(url)
        try:
            commands.code(400)
            assert 0
        except TwillAssertionError:
            pass

        #
        # no such command (NameError)
        #

        try:
            twill.parse.execute_file('test-go-fail2.twill', initial_url=url)
            assert 0
        except TwillNameError, e:
            pass
    finally:
        sys.stderr = old_err

    namespaces.new_local_dict()
    gd, ld = namespaces.get_twill_glocals()

    commands.go(url)
    try:
        twill.parse.execute_command('url', ('not this',), gd, ld, "anony")
        assert 0, "shouldn't get here"
    except TwillAssertionError:
        pass

    try:
        commands.follow('no such link')
        assert 0, "shouldn't get here"
    except TwillAssertionError:
        pass

    try:
        commands.find('no such link')
        assert 0, "shouldn't get here"
    except TwillAssertionError:
        pass

    try:
        commands.notfind('Hello')
        assert 0, "shouldn't get here"
    except TwillAssertionError:
        pass

    try:
        twill.parse.execute_command('exit', ('0',), gd, ld, "anony")
        assert 0, "shouldn't get here"
    except SystemExit:
        pass

    
def teardown_module():
    twill.parse.debug_print_commands(_save_print)
