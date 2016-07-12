"""Test the WSGI intercept code."""

import pytest

from twill import commands

from wsgi_intercept import (
    requests_intercept, add_wsgi_intercept, remove_wsgi_intercept)


def setup_module():
    requests_intercept.install()


def teardown_module():
    requests_intercept.uninstall()


_app_was_hit = False


def success():
    return _app_was_hit


def simple_app(environ, start_response):
    """Simplest possible application object"""
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)

    global _app_was_hit
    _app_was_hit = True
    
    return [b'WSGI intercept successful!\n']


def test_intercept():
    global _app_was_hit
    _app_was_hit = False

    add_wsgi_intercept('localhost', 80, lambda: simple_app)
    assert not _app_was_hit
    commands.go('http://localhost:80/')
    commands.show()
    commands.find("WSGI intercept successful")
    assert _app_was_hit
    remove_wsgi_intercept('localhost', 80)


def write_app(environ, start_response):
    """Test the 'write_fn' legacy stuff."""
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    write_fn = start_response(status, response_headers)

    global _app_was_hit
    _app_was_hit = True
    
    write_fn('WSGI intercept successful!\n')
    return []


class WrapperApp:
    """Test some tricky generator stuff in wsgi_intercept."""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        generator = self.app(environ, start_response)
        
        for i in generator:
            yield i


@pytest.mark.skip("broken since wsgi_intercept 0.10.1")
def test_wrapper_intercept():
    """Test a tricky wsgi_intercept interaction.

    This tests a tricky wsgi_intercept interaction between the 'write' fn
    passed back from the start_response function in WSGI, and the generator
    data yielded from the initial app call.  See wsgi_intercept.py, section
    containing 'generator_data', for more info.

    This test had worked in all wsgi_intercept versions before 0.10.1.
    In later versions, this seems to be broken again.
    This should be fixed in wsgi_intercept, if it is a real problem.
    """
    global _app_was_hit
    _app_was_hit = False

    wrap_app = WrapperApp(write_app)

    add_wsgi_intercept('localhost', 80, lambda: wrap_app)
    assert not _app_was_hit
    commands.go('http://localhost:80/')
    commands.find("WSGI intercept successful")
    assert _app_was_hit
    remove_wsgi_intercept('localhost', 80)


class IteratorApp:
    """Test some tricky iterator stuff in wsgi_intercept."""

    content = [b'Hello, world']

    def __call__(self, environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return self

    def __iter__(self):
        self._iter = iter(self.content)
        return self

    def __next__(self):
        return next(self._iter)

    next = __next__  # for Python 2


def test_iter_stuff():
    add_wsgi_intercept('localhost', 80, IteratorApp)
    commands.go('http://localhost:80/')
    commands.show()
    commands.find("Hello, world")
    commands.notfind("Hello, worldHello, world")
    remove_wsgi_intercept('localhost', 80)
