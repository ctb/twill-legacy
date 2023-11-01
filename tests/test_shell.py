"""Same as test_basic, but using the command interpreter."""

import sys
from pathlib import Path

import pytest
from twill import __url__ as twill_url
from twill import __version__ as twill_version
from twill.errors import TwillNameError

from .utils import execute_shell, test_dir

python_version = sys.version.split(None, 1)[0]


def test_shell_specific(url: str):
    execute_shell("test_shell.twill", initial_url=url, fail_on_unknown=True)
    text = Path(test_dir, "test_shell.out").read_text()
    lines = [line for line in text.splitlines() if line and "===" not in line]
    expected_lines = [
        f"twill version: {twill_version}",
        f"Python Version: {python_version}",
        f"See {twill_url} for more info.",
        "What do YOU think the command 'help' does?!?",
        "Help for command exit:",
        ">> exit [<code>]",
        '    Exit twill with given exit code (default 0, "no error").',
        "Print version information.",
        "Imported extension module 'shell_test'.",
        "testing extension",
        "raising errors",
        "ERROR: The flag has not been set",
        "ERROR: The flag has been set",
    ]

    assert lines == expected_lines


def test_shell_fail(url: str):
    with pytest.raises(TwillNameError):
        execute_shell(
            "test_shell_fail.twill",
            initial_url=url,
            fail_on_unknown=True,
        )


def test_most_commands(url: str):
    inp = "unique1\nunique2\n"
    execute_shell("test_basic.twill", inp, initial_url=url)


def teardown_module():
    for filename in "test_basic.cookies", "test_basic.out", "test_shell.out":
        Path(test_dir, filename).unlink(missing_ok=True)
