"""Utility functions for testing twill."""

import getpass
import os
import subprocess
import sys
import time
from io import StringIO
from pathlib import Path
from typing import Optional, TextIO

import httpx
import twill

test_dir = Path(__file__).parent  # test directory
current_dir = Path.cwd()  # current working directory

HOST = "127.0.0.1"  # interface to run the server on
PORT = 8080  # default port to run the server on
SLEEP = 0.5  # time to wait for the server to start

START = True  # whether to automatically start the quixote server
LOG = None  # name of the server log file or None

_url = None  # current server url


def get_url() -> str:
    """Get the current server URL."""
    if _url is None:
        raise RuntimeError("Server has not yet been started!")
    return _url


def cd_test_dir() -> None:
    """Make the test directory the current directory."""
    os.chdir(test_dir)


def pop_test_dir() -> None:
    """Restore the current directory before running the tests."""
    os.chdir(current_dir)


def mock_getpass(
    prompt: str = "Password: ",  # noqa: ARG001
    stream: Optional[TextIO] = None,  # noqa: ARG001
) -> str:
    """Mock getpass function."""
    return "pass"


def execute_script(
    filename: str, inp: Optional[str] = None, initial_url: Optional[str] = None
) -> None:
    """Execute twill script with the given filename."""
    if filename != "-":
        filename = str(Path(test_dir, filename))

    if inp:
        # use inp as the stdin for the actual script commands
        stdin, sys.stdin = sys.stdin, StringIO(inp)
        real_getpass, getpass.getpass = getpass.getpass, mock_getpass
    try:
        twill.execute_file(filename, initial_url=initial_url)
    finally:
        if inp:
            sys.stdin = stdin
            getpass.getpass = real_getpass


def execute_shell(
    filename: str,
    inp: Optional[str] = None,
    initial_url: Optional[str] = None,
    *,
    fail_on_unknown: bool = False,
) -> None:
    """Execute twill script with the given filename using the shell."""
    # use filename as the stdin *for the shell object only*
    if filename != "-":
        filename = str(Path(test_dir, filename))

    with open(filename, encoding="utf-8") as cmd_file:
        cmd_content = cmd_file.read()
    cmd_content += "\nquit\n"
    cmd_inp = StringIO(cmd_content)

    if inp:
        # use inp as the std input for the actual script commands
        stdin, sys.stdin = sys.stdin, StringIO(inp)
        real_getpass, getpass.getpass = getpass.getpass, mock_getpass
    try:
        loop = twill.shell.TwillCommandLoop(
            initial_url=initial_url,
            stdin=cmd_inp,
            fail_on_unknown=fail_on_unknown,
        )
        loop.cmdloop()
    except SystemExit:
        pass
    finally:
        if inp:
            sys.stdin = stdin
            getpass.getpass = real_getpass
        loop.reset()  # reset the singleton


def start_server(port: Optional[int] = None) -> None:
    """Start a simple test web server.

    Run a Quixote simple_server on HOST:PORT with subprocess.
    All output is captured and thrown away.

    The parent process returns the URL on which the server is running.
    """
    global _url  # noqa: PLW0603

    if port is None:
        port = int(os.environ.get("TWILL_TEST_PORT", PORT))

    if START:
        out = open(LOG or os.devnull, "w", buffering=1)  # noqa: SIM115
        print(  # noqa: T201
            "Starting:", sys.executable, "tests/server.py", Path.cwd()
        )
        subprocess.Popen(
            [sys.executable, "-u", "server.py"],  # noqa: S603
            stderr=subprocess.STDOUT,
            stdout=out,
        )
        time.sleep(SLEEP)  # wait until the server is up and running
        print("The server has been started.")  # noqa: T201

    # noinspection HttpUrlsUsage
    _url = f"http://{HOST}:{port}/"


def stop_server() -> None:
    """Stop a previously started test web server."""
    global _url  # noqa: PLW0603

    if _url:
        if START:
            try:
                httpx.get(f"{_url}exit", timeout=10)
            except Exception as error:  # noqa: BLE001
                print("ERROR:", error)  # noqa: T201
                print("Could not stop the server.")  # noqa: T201
        _url = None
