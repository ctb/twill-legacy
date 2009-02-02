"""
Test the utils.run_tidy function.

This doesn't test to see if tidy was actually run; all it does is make sure
that the function runs without error...

(Yes, I know that some of the setup/teardown code is stupid.  Sorry.)
"""
import twilltestlib
from twill import utils
from twill.commands import config

bad_html = """<a href="test">you</a> <b>hello."""
    
def setup_module():
    config('require_tidy', 1)

def teardown_module():
    config('require_tidy', 0)

def test():
    (output, errors) = utils.run_tidy(bad_html)
    assert output != None

def test2():
    config('require_tidy', 0)
    _save, utils._tidy_cmd = utils._tidy_cmd, [""]
    
    try:
        (output, errors) = utils.run_tidy(bad_html)
        (output, errors) = utils.run_tidy(bad_html)
    finally:
        utils._tidy_cmd = _save

    assert output is None
    assert errors is None
    config('require_tidy', 1)

def test3():
    _save, utils._tidy_cmd = utils._tidy_cmd, [""]

    try:
        try:
            (output, errors) = utils.run_tidy(bad_html)
            assert 0
        except:
            pass
    finally:
        utils._tidy_cmd = _save

if __name__ == '__main__':
    setup_module()
    test()
    teardown_module()
