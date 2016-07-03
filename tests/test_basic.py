"""
Run through the test-basic script.

This should really be broken out into multiple sub scripts...
"""

import os

from twilltestlib import execute_script, testdir


def test(url):
    inp = "unique1\nunique2\n"
    
    execute_script('test_basic.twill', inp, initial_url=url)


def teardown_module():
    for filename in 'test_basic.cookies', 'test_basic.out':
        try:
            os.unlink(os.path.join(testdir, filename))
        except OSError:
            pass

