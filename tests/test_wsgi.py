"""Test the WSGI support."""

from typing import Callable, Dict, Generator, List, Sequence, Tuple

from twill import browser, commands

"""Intercept HTTP connections that use
`requests <http://docs.python-requests.org/en/latest/>`_.
"""

app_was_hit = set()

Environ = Dict[str, str]
WriteCallable = Callable[[bytes], None]
Headers = List[Tuple[str, str]]
StartResponse = Callable[[str, Headers], WriteCallable]


def simple_app(
    _environ: Environ,
    start_response: StartResponse,
) -> Sequence[bytes]:
    """Simplest possible application object."""
    status = "200 OK"
    response_headers = [("Content-type", "text/plain")]
    start_response(status, response_headers)
    app_was_hit.add("simple_app")
    return (b"Hello, World!",)


def write_app(
    _environ: Environ,
    start_response: StartResponse,
) -> Sequence[bytes]:
    """Simple application using a legacy write callable.

    See https://peps.python.org/pep-3333/#the-write-callable.
    """
    status = "200 OK"
    response_headers = [("Content-type", "text/plain")]
    write = start_response(status, response_headers)
    app_was_hit.add("write_app")
    write(b"Hello, ")
    return (b"World!",)


class IteratorApp:
    """Simple application using a custom iterator."""

    content = (b"Hello, world!",)

    def __init__(
        self,
        environ: Environ,
        start_response: StartResponse,
    ) -> None:
        """Create this application."""
        self.environ = environ
        self.start_response = start_response

    def __iter__(self) -> Generator[bytes, None, None]:
        status = "200 OK"
        response_headers = [("Content-type", "text/plain")]
        self.start_response(status, response_headers)
        app_was_hit.add(self.__class__.__name__)
        yield from self.content


def test_simple_app():
    app_was_hit.clear()
    browser.reset(app=simple_app)
    try:
        assert not app_was_hit
        commands.go("http://localhost:8080/")
        commands.show()
        commands.find("Hello, World!")
        assert "simple_app" in app_was_hit
    finally:
        browser.reset()


def test_write_app():
    app_was_hit.clear()
    browser.reset(app=write_app)
    try:
        assert not app_was_hit
        commands.go("http://localhost:8080/")
        commands.show()
        # next line may be added again once this has been merged:
        # https://github.com/encode/httpx/pull/2920
        # commands.find("Hello, World!")  # noqa: ERA001
        assert "write_app" in app_was_hit
    finally:
        browser.reset()


def test_iterator_app():
    browser.reset(app=IteratorApp)
    try:
        commands.go("http://localhost:80/")
        commands.show()
        commands.find("Hello, world!")
        commands.notfind("!Hello")
        assert "IteratorApp" in app_was_hit
    finally:
        browser.reset()
