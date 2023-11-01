"""Test the unit-test support framework using (naturally) a unit test."""

from pathlib import Path

import twill.unit
from quixote.server.simple_server import (  # type: ignore[import-untyped]
    run as quixote_run,
)

from .server import create_publisher
from .utils import test_dir

PORT = 8081  # default port to run the server on
SLEEP = 0.5  # time to wait for the server to start


def run_server(port: int = PORT) -> None:
    """Function to run the server"""
    quixote_run(create_publisher, port=port)


def test():
    """The unit test"""
    # abspath to the script
    script = str(Path(test_dir, "test_unit_support.twill"))

    # create test_info object
    test_info = twill.unit.TestInfo(script, run_server, PORT, SLEEP)

    # run tests!
    twill.unit.run_test(test_info)


if __name__ == "__main__":
    test()
