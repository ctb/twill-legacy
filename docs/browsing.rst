.. _browsing:

=======================
Web browsing with twill
=======================

twill strives to be a complete implementation of a web browser,
omitting only JavaScript support. It includes support for cookies,
basic authentication, and trickery such as "meta refresh" redirects.

twill implements a variety of :ref:`commands <commands>`.
With the built-in language, you can do things like go to a specific URL;
follow links; fill out forms and submit them; save, load,
and delete cookies; and change the user agent string. You can also
easily extend twill with new and specialized commands using Python.

.. _commands: commands.html

Using twill interactively
~~~~~~~~~~~~~~~~~~~~~~~~~

The twill command line script lets you interactively browse the Web.
It features built-in help, e.g. "help go" will describe the command 'go'
to you; command-line completion with the TAB key; and history browsing
with the UP/DOWN arrow keys.

Proxy servers
~~~~~~~~~~~~~

twill understands the ``http_proxy`` environment variable generically
used to set proxy server information. To use a proxy in UNIX or
Windows, just set the ``http_proxy`` environment variable, e.g.::

   % export http_proxy="http://www.someproxy.com:3128"

or::

   % setenv http_proxy="http://www.someotherproxy.com:3148"

Recording scripts
~~~~~~~~~~~~~~~~~

Writing twill scripts is boring. One simple way to get at least a
rough initial script is to use the MaxQ_ recorder to generate a twill
script. MaxQ_ acts as an HTTP proxy and records all HTTP traffic; I
have written a simple twill script generator for it. The script
generator and installation docs are included in the twill distribution
under the directory ``extras/maxq``.

.. _MaxQ: http://maxq.tigris.org/

Miscellaneous implementation details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 * twill ignores robots.txt.

 * http-equiv=refresh headers are handled immediately, independent of the
   'pause' component of the 'content' attribute.

 * twill ignores JavaScript.

Using HTML Tidy to check for broken HTML
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `HTML Tidy`_ tool can be used to check and clean up broken HTML
pages. You can use it with the 'tidy_ok' command to assert that it
reports no warnings or errors. In order to use this command in twill,
you need to install the `PyTidyLib`_ package. If it is not installed,
twill will silently ignore it. It may be desirable to *require* a
functioning ``PyTidyLib`` installation; so, to fail when it *isn't*
installed, set ``config require_tidy 1``.

.. _HTML Tidy: http://www.html-tidy.org/
.. _PyTidyLib: https://pythonhosted.org/pytidylib/
