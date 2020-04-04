.. _testing:

============================
Testing Web sites with twill
============================

twill was initially designed for testing web sites, although since then
people have also figured out that it's good for :ref:`browsing <browsing>`
unsuspecting web sites.

Using the twill command
~~~~~~~~~~~~~~~~~~~~~~~

The simplest way to test Web sites is to write one or more twill scripts
and then simply run ::

    twill [ -u initial_url ] script(s)

either from the command-line (for development purposes), via a cron job
(to check to see if sites are up and responding), or from your functional
or unit tests (see below).

twill will try to run each script given to it on the command line
once, and will report the number of scripts that failed. The exit value
of the script will be 0 if there are no failures, so you can use it in
a shell script easily enough.

twill will gather scripts from directories, so you can create a whole
directory hierarchy containing your scripts and they will all be gathered
and run, in standard lexical order.

twill scripts are assumed to have the '.twill' extensions; you don't
need to specify it explicitly.

The ``-u`` flag can be used to give twill an initial URL; this is
equivalent to placing a "go (initial_url)" command at the top of the
script, but is particularly handy for test frameworks where the URL
might change depending on the developer.

Stress testing
~~~~~~~~~~~~~~

You can use the `twill-fork` script to do some stress testing.
The syntax is ::

   twill-fork -n <number to execute> -p <number of processes> script [ scripts... ]

For example, ::

   twill-fork -n 500 -p 10 test-script

will fork 10 times and run `test-script` 50 times in each process.
`twill-fork` will record the time it takes to run all of the scripts specified
on the command and print a summary at the end.

The time recorded is *not* the CPU time used. (This would lead to an
inaccurate estimate because the client code uses blocking calls to
retrieve Web pages.)  Rather, the time recorded is the clock time
measured between the start and end of script execution.

Try `twill-fork -h` to get a list of other command line arguments.

Note that twill-fork runs only under Unix and still needs a lot of work...


Unit testing
~~~~~~~~~~~~

twill can be used in unit testing, and it contains some Python support
infrastructure for this purpose.

As an example, here's the code from twill's own unit test, testing the
unit-test support code::

    import os
    import twill
    from quixote.server.simple_server import run as quixote_run

    PORT=8090  # port to run the server on

    def run_server():
        """Function to run the server"""
        quixote_run(twill.tests.server.create_publisher, port=PORT)

    def test():
        """The unit test"""
        test_dir = twill.tests.utils.testdir
        script = os.path.join(test_dir, 'test_unit_support.twill')

        # create test_info object
        test_info = twill.unit.TestInfo(script, run_server, PORT)

        # run tests!
        twill.unit.run_test(test_info)

Here, I'm unit testing the Quixote application ``twill.tests.server``, which
is run by ``quixote_run`` (a.k.a. ``quixote.server.simple_server.run``) on
port ``PORT``, using the twill script ``test_unit_support.twill``. That
script contains this code::

   # starting URL is provided to it by the unit test support framework.

   go ./multisubmitform
   code 200

A few things to note:

 * the initial URL is set based on the URL reported by ``TestInfo``,
   which calculates it based on the ``PORT`` argument.
   (This can be overridden by subclasses.)

 * ``TestInfo`` contains code to (a) run the server function in a new
   process, and (b) run the twill script against that server. It then
   kills the server after script completion.

 * You can also pass a 'sleep' argument to the ``TestInfo`` constructor that
   specifies how many seconds to wait for the server to start before
   executing the script.

Testing WSGI applications "in-process"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use `wsgi_intercept`_ for testing `WSGI applications`_.

It provides two functions, `add_wsgi_intercept` and `remove_wsgi_intercept`,
that allow Python applications to redirect HTTP calls into a WSGI application
"in-process", without going via an external Internet call. This is
particularly useful for unit tests, where setting up an externally
available Web server can be inconvenient.

For example, the following code redirects all ``localhost:80`` calls to
the given WSGI app: ::

    def create_app():
        return wsgi_app

    import wsgi_intercept

    wsgi_intercept.requests_intercept.install()
    wsgi_intercept.add_wsgi_intercept('localhost', 80, create_app)
    # your twill tests go here...
    wsgi_intercept.remove_wsgi_intercept('localhost', 80)
    wsgi_intercept.requests_intercept.uninstall()

See the ``tests/test_wsgi_intercept.py`` unit test for more examples.

.. _wsgi_intercept: https://pypi.python.org/pypi/wsgi_intercept
.. _WSGI applications: https://www.python.org/dev/peps/pep-0333/
