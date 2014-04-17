"""
Test the WSGI intercept code.
"""

try:
    from paste.lint import middleware as wsgi_lint
except ImportError:
    wsgi_lint = lambda x: x             # ignore lack of paste.lint ;)
    
import twill

_app_was_hit = False

def success():
    return _app_was_hit

def simple_app(environ, start_response):
    """Simplest possible application object"""
    status = '200 OK'
    response_headers = [('Content-type','text/plain')]
    start_response(status, response_headers)

    global _app_was_hit
    _app_was_hit = True
    
    return ['WSGI intercept successful!\n']

def write_app(environ, start_response):
    """Test the 'write_fn' legacy stuff."""
    status = '200 OK'
    response_headers = [('Content-type','text/plain')]
    write_fn = start_response(status, response_headers)

    global _app_was_hit
    _app_was_hit = True
    
    write_fn('WSGI intercept successful!\n')
    return []

class wrapper_app:
    """
    Test some tricky generator stuff in wsgi_intercept.
    """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        generator = self.app(environ, start_response)
        
        for i in generator:
            yield i

def test_intercept():
    global _app_was_hit
    _app_was_hit = False

    twill.add_wsgi_intercept('localhost', 80, lambda: wsgi_lint(simple_app))
    assert not _app_was_hit
    print 'go'
    twill.commands.go('http://localhost:80/')
    twill.commands.show()
    print 'find'
    twill.commands.find("WSGI intercept successful")
    assert _app_was_hit
    print 'remove'
    twill.remove_wsgi_intercept('localhost', 80)

def test_wrapper_intercept():
    """
    This tests a tricky wsgi_intercept interaction between the 'write' fn
    passed back from the start_response function in WSGI, and the generator
    data yielded from the initial app call.

    See wsgi_intercept.py, section containing 'generator_data', for more
    info.
    """
    global _app_was_hit
    _app_was_hit = False

    wrap_app = wrapper_app(write_app)

    twill.add_wsgi_intercept('localhost', 80, lambda: wsgi_lint(wrap_app))
    assert not _app_was_hit
    print 'go'
    twill.commands.go('http://localhost:80/')
    print 'find'
    twill.commands.find("WSGI intercept successful")
    assert _app_was_hit
    print 'remove'
    twill.remove_wsgi_intercept('localhost', 80)

####

class iterator_app:
    """
    Test some tricky iterator stuff in wsgi_intercept.
    """

    content = ['Hello, world']

    def __call__(self, environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type','text/plain')]
        start_response(status, response_headers)
        return self

    def __iter__(self):
        self._iter = iter(self.content)
        return self

    def next(self):
        return self._iter.next()

def test_iter_stuff():
    twill.add_wsgi_intercept('localhost', 80, iterator_app)
    print 'go'
    twill.commands.go('http://localhost:80/')
    print 'find'
    twill.commands.show()
    twill.commands.find("Hello, world")
    twill.commands.notfind("Hello, worldHello, world")
    print 'remove'
    twill.remove_wsgi_intercept('localhost', 80)
