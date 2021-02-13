"""Test the WSGI intercept code."""

from twill import commands

from wsgi_intercept import (
    requests_intercept, add_wsgi_intercept, remove_wsgi_intercept)


def setup_module():
    requests_intercept.install()


def teardown_module():
    requests_intercept.uninstall()


app_was_hit = set()


def simple_app(_environ, start_response):
    """Simplest possible application object"""
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    app_was_hit.add('simple_app')
    return [b'WSGI intercept successful!\n']


def write_app(_environ, start_response):
    """Test the 'write_fn' legacy stuff."""
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    write_fn = start_response(status, response_headers)
    app_was_hit.add('write_app')
    write_fn(b'WSGI intercept successful!\n')
    return []


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


def test_intercept():
    app_was_hit.clear()
    add_wsgi_intercept('localhost', 8080, lambda: simple_app)
    assert not app_was_hit
    commands.go('http://localhost:8080/')
    commands.show()
    commands.find("WSGI intercept successful")
    assert 'simple_app' in app_was_hit
    remove_wsgi_intercept('localhost', 8080)


def test_write_intercept():
    app_was_hit.clear()
    add_wsgi_intercept('localhost', 8080, lambda: write_app)
    assert not app_was_hit
    commands.go('http://localhost:8080/')
    commands.show()
    commands.find("WSGI intercept successful")
    assert 'write_app' in app_was_hit
    remove_wsgi_intercept('localhost', 8080)


def test_iter_stuff():
    add_wsgi_intercept('localhost', 80, IteratorApp)
    commands.go('http://localhost:80/')
    commands.show()
    commands.find("Hello, world")
    commands.notfind("Hello, worldHello, world")
    remove_wsgi_intercept('localhost', 80)
