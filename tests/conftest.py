"""Shared test configuration for pytest."""

from io import StringIO
from typing import Generator

import pytest

from . import utils


@pytest.fixture(scope="session")
def url() -> Generator[str, None, None]:
    """Start a server and returns its URL."""
    utils.cd_test_dir()
    utils.start_server()

    url = utils.get_url()

    from twill import set_output
    from twill.commands import find, go

    set_output()
    try:
        go(url)
        find("These are the twill tests")
    except Exception as error:  # noqa: BLE001
        raise RuntimeError(
            """
***
Hello! The twill test server is not running or cannot be reached;
please free port 8080 (or set TWILL_TEST_PORT to something else),
and clear your proxy settings too!
***
"""
        ) from error

    yield url

    utils.stop_server()
    utils.pop_test_dir()


@pytest.fixture()
def output() -> Generator[StringIO, None, None]:
    """Get output from the test."""
    from twill import set_output

    with StringIO() as output:
        set_output(output)
        yield output
    set_output()
