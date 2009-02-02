"""
Run through the test-basic script.

This should really be broken out into multiple sub scripts...
"""

import os
import twilltestlib

def setup_module():
    global url
    url = twilltestlib.get_url()

def test():
    inp = "unique1\nunique2\n"
    
    twilltestlib.execute_twill_script('test-basic.twill', inp, initial_url=url)
    
def teardown_module():
    try:
        os.unlink(os.path.join(twilltestlib.testdir, 'test-basic.cookies'))
    except OSError:
        pass
