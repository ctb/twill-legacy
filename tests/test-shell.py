"""
Run through the test-basic script, but this time from the command interpreter.
"""

import sys, os
import twilltestlib
from cStringIO import StringIO
import twill.shell

def setup_module():
    global url
    url = twilltestlib.get_url()

def test_shell_specific():    
    twilltestlib.execute_twill_shell('test-shell.twill', initial_url=url,
                                     fail_on_unknown=True)

    try:
        twilltestlib.execute_twill_shell('test-shell-fail.twill',
                                         initial_url=url,
                                         fail_on_unknown=True)
    except NameError:
        pass
    
def test_most_commands():
    inp = "unique1\nunique2\n"
    twilltestlib.execute_twill_shell('test-basic.twill', inp, initial_url=url)
    
def teardown_module():
    try:
        os.unlink(os.path.join(twilltestlib.testdir, 'test-basic.cookies'))
    except OSError:
        pass
