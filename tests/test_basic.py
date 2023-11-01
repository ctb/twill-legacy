"""
Run through the test-basic script.

This should really be broken out into multiple sub scripts...
"""

from pathlib import Path

from .utils import execute_script, test_dir


def test(url: str):
    inp = "unique1\nunique2\n"

    execute_script("test_basic.twill", inp, initial_url=url)


def teardown_module():
    for filename in "test_basic.cookies", "test_basic.out":
        Path(test_dir, filename).unlink(missing_ok=True)
