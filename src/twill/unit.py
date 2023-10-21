"""Support functionality for using twill in unit tests."""

import sys
import time

from io import StringIO
from multiprocessing import Process

from .parse import execute_file

HOST = '127.0.0.1'  # interface to run the server on
PORT = 8080  # default port to run the server on
SLEEP = 0  # time to wait for the server to start


class TestInfo:
    """Test info container.

    Object containing info for a test: script to run, server function to
    run, and port to run it on.  Note that information about server port
    *must* be decided by the end of the __init__ function.

    The optional sleep argument specifies how many seconds to wait for the
    server to set itself up.  Default is 0.
    """

    def __init__(self, script, server_fn, port=PORT, sleep=SLEEP):
        self.script = script
        self.server_fn = server_fn
        self.port = port
        self.stdout = None
        self.stderr = None
        self.sleep = sleep

    def start_server(self):
        # save old stdout/stderr
        stdout, stderr = sys.stdout, sys.stderr

        # create new stdout/stderr
        self.stdout = sys.stdout = StringIO()
        self.stderr = sys.stderr = StringIO()

        try:
            self.server_fn()
        finally:
            # restore stdout/stderr
            sys.stdout, sys.stderr = stdout, stderr

    def run_script(self):
        """Run the given twill script on the given server."""
        time.sleep(self.sleep)
        url = self.url
        execute_file(self.script, initial_url=url)

    @property
    def url(self):
        """"Get the test server URL."""
        # noinspection HttpUrlsUsage
        return f"http://{HOST}:{self.port}/"


def run_test(test_info):
    """Run test on a web site where the site is running in a sub process."""
    # run server
    server_process = Process(target=test_info.start_server)
    server_process.start()
    # wait for server process to spin up
    timeout = max(1, test_info.sleep)
    wait = min(0.125, 0.125 * timeout)
    waited = 0
    while not server_process.is_alive() and waited < timeout:
        time.sleep(wait)
        waited += wait
    # run twill test script
    try:
        test_info.run_script()
    finally:
        server_process.terminate()
