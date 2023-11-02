.. _python-api:

==================
twill's Python API
==================

twill is essentially a web browsing and testing tool based on the
`httpx`_ and `lxml`_ packages. All twill commands are implemented in
the ``commands.py`` file, and pyparsing_ does the work of parsing the
input and converting it into Python commands (see ``parse.py``).
Interactive shell work and readline support is implemented via the `cmd`_
module (from the standard Python library).

.. _httpx: https://www.python-httpx.org/
.. _lxml: https://lxml.de/
.. _pyparsing: https://github.com/pyparsing/pyparsing
.. _cmd: https://docs.python.org/3/library/cmd.html

Using twill from Python
~~~~~~~~~~~~~~~~~~~~~~~

There are two fairly simple ways to use twill from Python. (They are
compatible with each other, so you don't need to choose between them;
just use whichever is appropriate.)

The first is to simply import all of the commands in ``commands.py`` and
use them directly from Python. For example, ::

   from twill.commands import *
   go("http://www.python.org/")
   showforms()

This has the advantage of being very simple, as well as being tied
directly to the documented set of commands in
:ref:`the commands reference <commands>`.

However, the functions in ``commands.py`` are too simple for some situations.
In particular, most of them do not have any return values, so in order to
e.g. get the HTML for a particular page, you will need to ask the actual
"Web browser" object that twill uses.

To make use of to the Web browser directly, import the ``browser`` object::

   from twill import browser

   browser.go("https://www.python.org/")
   assert 'Python' in browser.html
   browser.showforms()

This is the second way to use twill from Python, and it is much more flexible.
All of the functions in ``commands.py`` use this same browser object, so
you can mix and match: ::

   from twill import browser

   from twill.commands import *
   go("https://www.python.org/")
   assert 'Python' in browser.html
   find("Documentation")
   browser.showforms()

The basic difference is that functions available through the browser object
are intended for use from Python, while ``commands.py`` functions define
the twill *language*. In fact, all of the functions in ``commands.py``
are small snippets of code wrapped around the browser object.

Most importantly, the browser object also provides several properties that
can be used to introspect the current state of the browser and evaluated
programmatically in Python, such as ``url``, ``code``, ``html``, ``title``,
``links``, ``forms``, ``cookies``, ``response_headers`` or ``history``.

For more information on the functions exposed by the browser object,
see the code of the **TwillBrowser** class in twill.browser.

Extending twill
~~~~~~~~~~~~~~~

Right now twill is very easy to extend: just build a Python module
that exports the functions you want to call, place it in the
PYTHONPATH, and run ``extend_with <modulename>``. See
``extensions/mailman_sf.py`` for an extension that helps deal
with mailman lists on SourceForge; this extension is used by
``examples/discard-sf-mailman-msgs``.

Notes:

  * If your extension raises ``SystemExit``, twill will stop processing
    the script. This is a useful way to build in conditionals, e.g.
    see the ``discard-sf-mailman-msgs`` example script.

Passing variables from Python into twill
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Suppose you write an extension function, and you want to return some
values from that extension function for later use in filling out forms.
How do you do this?

The simplest way is to simply insert them into the global or local
dictionary, like so: ::

  from twill.namespaces import get_twill_glocals
  global_dict, local_dict = get_twill_glocals()

  global_dict['varname'] = value

You can then use the usual variable access methods to substitute for
varname, e.g. ::

  formvalue 1 field $varname

Using twill in other Python programs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All of the commands available in twill are implemented as top-level functions
in the `twill.commands` module. For example, to use twill functionality from
another Python program, you can do::

   from twill.commands import go, showforms, formclear, fv, submit

   go('http://localhost:8080/')
   go('./widgets')
   showforms()

   formclear('1')
   fv('1', 'name', 'test')
   fv('1', 'password', 'testpass')
   fv('1', 'confirm', 'yes')
   showforms()

   submit('0')

Note that all arguments need to be strings, at least for the moment.

You can capture command output by passing any write-enabled file handle
to twill.set_output, e.g. ::

   twill.set_output(StringIO())

will send all non-error output into a StringIO() object.
