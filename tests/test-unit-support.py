"""
Test the unit-test support framework using (naturally) a unit test...
"""

import os
import twilltestlib
import twill.unit
import twilltestserver
from quixote.server.simple_server import run as quixote_run

def test():
    return 1

    # port to run the server on
    PORT=8090
    
    # create a function to run the server
    def run_server_fn():
        quixote_run(twilltestserver.create_publisher, port=PORT)

    # abspath to the script
    script = os.path.join(twilltestlib.testdir, 'test-unit-support.twill')

    # create test_info object
    test_info = twill.unit.TestInfo(script, run_server_fn, PORT)

    # run tests!
    twill.unit.run_test(test_info)

if __name__ == '__main__':
    test()
