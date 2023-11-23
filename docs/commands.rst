.. _commands:

========================
twill language reference
========================

The following commands are built into twill. Note that all text after
a '#' is ignored as a comment, unless it's in a quoted string.

Browsing
========

**go** *<url>* -- visit the given URL.

**back** -- return to the previous URL.

**reload** -- reload the current URL.

**follow** *<link name>* -- follow the given link.

Note: When used from Python, you get the new URL after executing
these commands (after possible redirects) with ``browser.url``.

Assertions
==========

**code** *<code>* -- assert that the last page loaded had this HTTP status,
e.g. ``code 200`` asserts that the page loaded fine.

**find** *<pattern>* [*<flags>*] -- assert that the page contains the
specified regular expression pattern. The variable ``__match__`` is set to
the first matching subgroup (or the entire matching string, if no subgroups
are specified). When called from Python, the matching string is also returned.

Fhe command also accepts some flags: **i**, for case-insensitive matching,
**m** for multi-line mode and **s** for dotall matching. The flag **x** uses
XPath expressions instead of regular expressions (see below).

**find** *<xpath>* **x** -- assert that the page contains the element
matched by the XPath expression. The variable ``__match__`` is set to
the first matching element's text content. When called from Python, the
matching text is also returned.

**not_find** *<pattern>* [*<flags>*] -- assert that the page *does not*
contain the specified regular expression pattern. This command accepts the
same flags as **find**.

Alternative spelling: "notfind"

**not_find** *<xpath>* **x** -- assert that the page *does not* contain the
element pointed by the XPath expression.

**url** *<pattern>* -- assert that the current URL matches the given regex
pattern. The variable ``__match__`` is set to the first matching subgroup
(or the entire matching string, if no subgroups are specified).
When called from Python, the matching string is returned.

**title** *<pattern>* -- assert that the title of this page matches this
regular expression. The variable ``__match__`` is set to the first matching
subgroup (or the entire matching string, if no subgroups are specified).
When called from Python, the matching string is returned.

Display
=======

**echo** *<string>* -- echo the string to the screen.

**info** -- display information about the current page.

**redirect_output** *<filename>* -- append all twill output to the given file.

**reset_output** -- display all output to the screen.

**save_html** *[<filename>]* -- save the current page's HTML into a file.
If no filename is given, derive the filename from the URL.

**show** -- show the current page's HTML.

Alternative spelling: "showhtml" or "show html"

**show_links** -- show all of the links on the current page.

Alternative spellings: "showlinks" or "show links"

**show_forms** -- show all of the forms on the current page.

Alternative spellings: "showforms" or "show forms"

**show_history** -- show the browser history.

Alternative spellings: "showhistory" or "show history"

**show_cookies** -- show the current cookies.

Alternative spellings: "showcookies" or "show cookies"

Note: When used from Python, you get these objects using the properties
of the browser with the same names, e.g. ``browser.html``, ``browser.links``,
``browser.forms``, ``browser.history`` and ``browser.cookies``.

Forms
=====

**submit** *[<button_name>]* -- click the submit button with the given name.
Instead of the name of the button you can also specify the number of the form
element that shall be used as the submit button. If you do not specify a
button name or number, the form is submitted via the last submission button
clicked; if nothing had been clicked, use the first submit button on the form.
See `details on form handling`_ for more information. In rare cases you may
need to specify the form explicitly, you can do so by adding the form name
or number as an additional parameter to the button name or number.

**form_value** *<form_name> <field_name> <value>* --- set the given field
in the given form to the given value. For read-only form controls,
the click may be recorded for use by **submit**, but the value is not
changed unless the 'config' command has changed the default behavior.
See 'config' and `details on form handling`_ for more information on
the 'form_value' command.

For list controls, you can use 'form_value <form_name> <field_name> +value'
or 'form_value <form_name> <field_name> -value' to select or deselect a
particular value.

Alternative spellings: "formvalue" or "fv"

**fv** -- abbreviation for 'form_value'.

**form_action** *<form_name> <action>* -- change the form action URL to the
given URL.

Alternative spellings: "formaction" or "fa"

**fa** -- abbreviation for 'form_action'.

**form_clear** -- clear all values in the form.

Alternative spelling: "formclear"

**form_file** *<form_name> <field_name> <filename> [ <content_type> ]* --
attach a file to a file upload button by filename.

Alternative spelling: 'formfile'.

**show_forms** -- show all of the forms on the current page.

Alternative spellings: "showforms" or "show forms"

Cookies
=======

**save_cookies** *<filename>* -- save current cookie jar into a file.

**load_cookies** *<filename>* -- replace current cookie jar
with file contents.

**clear_cookies** -- clear all of the current cookies.

**show_cookies** -- show all of the current cookies.

Alternative spellings: "showcookies" or "show cookies"

Debugging
=========

**debug** *<what>* *<level>* -- turn on or off debugging/tracing for
various functions. The first argument is either 'http' to show HTTP
headers, 'equiv-refresh' to show "meta refresh" redirects, or 'commands'
to show twill commands. The second argument is '0' for off, '1' for on.

Variable handling
=================

**set_global** *<name> <value>* -- set variable <name> to value <value> in
global dictionary. The value can be retrieved with '$value'.

Alternative spelling: "setglobal"

**set_local** *<name> <value>* -- set variable <name> to value <value> in
local dictionary. The value can be retrieved with '$value'.

Alternative spelling: "setlocal"

The local dictionary is file-specific, while the global module is general
to all the commands. Local variables will override global variables if
they exist.

Note that you can do variable interpolation in strings with ${var}, e.g. ::

   setglobal a 1
   setglobal b 2

   fv thisform thatfield "${a}${b}"

Other commands
==============

**tidy_ok** -- check to see if HTML Tidy runs on this page without any
errors or warnings. This check is very stringent, but you can relax the
default configuration by setting ``tidy_*`` configuration options.

**exit** *[<code>]* -- exit with the given integer code, if specified.
'code' defaults to 0.

**run** *<command>* -- execute the given Python command.

**run_file** *<file1> [ <file2> ... ]* -- execute the given file(s).

Alternative spellings: "runfile" or "rf"

**rf** -- abbreviation for 'run_file'.

**add_cleanup** *<file1> [ <file2> ... ]* -- add the given cleanup file(s).
These will be run after the current file has executed (successfully or not).

**agent** -- set the browser's "User-agent" string.

**timeout** *[<seconds>]* -- set browser timeout to given number of seconds.
Defaults to 10 seconds.  Set to 0 for no timeout.

**sleep** *[<seconds>]* -- sleep the given number of seconds.
Defaults to 1 second.

**reset_browser** -- reset the browser.

**extend_with** *<module>* -- import commands from Python module. This acts
like ``from <module> import *`` does in Python, so e.g. a function
``fn`` in ``extmodule`` would be available as ``fn``.
See *extras/examples/extend_example.py* for an example.

**get_input** *<prompt>* -- get keyboard input and store it in ``__input__``.
When called from Python, this function returns the input value.

Alternative spelling: "getinput"

**get_password** *<prompt>* -- get *silent* keyboard input and store
it in ``__password__``. When called from Python, this function returns
the input value.

Alternative spelling: "getpassword"

**add_auth** *<realm> <uri> <user> <password>* -- add HTTP Basic
Authentication information for the given realm/URI combination.
For example, ::

   add_auth IdyllStuff http://www.idyll.org/ titus test

tells twill that a request from the authentication realm
"IdyllStuff" under ``http://www.idyll.org/`` should be answered with
username 'titus', password 'test'. If the 'with_default_realm' option
is set to True, ignore 'realm'.

**config** [*<key>* [*<value>*]] -- show/set configuration options.

Configuration options starting with ``tidy_`` will be used when checking
documents with HTML Tidy. For example, ::

    config tidy_drop_empty_elements no

**add_extra_headers** *<name>* *<value>* -- add an extra HTTP header to
each HTTP request.

**show_extra_headers** -- show the headers being added to each HTTP request.

**clear_extra_headers** -- clear the headers being added to each HTTP request.

Special variables
=================

**__input__** -- result of last **getinput**.

**__match__** -- matched text from last **find**, **title**, or **url**.

**__password__** -- result of last **getpassword**.

**__url__** -- current URL.

Details on form handling
========================

.. _details on form handling:

Both the `form_value` (or `fv`) and `submit` commands rely on a certain
amount of implicit cleverness to do their work. In odd situations, it
can be annoying to determine exactly what form field `form_value` is
going to pick based on your field name, or what form and field `submit`
is going to "click" on.

Here is the pseudocode for how `form_value` and `submit` figure out
what form to use (function `twill.browser.form`)::

   for each form on page:
       if supplied regex pattern matches the form name, select

   if no form name, try converting to an integer N & using N-1 as
   an index into the list or forms on the page (i.e. form 1 is the
   first form on the page).

Here is the pseudocode for how `form_value` and `submit` figure out
what form field to use (function `twill.browser.form_field`)::

   search current form for control name with exact match to field_name;
   if single (unique) match, select.

   if no match, convert field_name into a number and use as an index, if
   possible.

   if no match, search current form for control name with regex match to
   field_name; if single (unique) match, select.

   if *still* no match, look for exact matches to submit-button values.
   if single (unique) match, select.

Here is the pseudocode for `submit`::

   if a form was _not_ previously selected by form_value:
      if there's only one form on the page, select it.
      otherwise, fail.

   if a field is not explicitly named:
      if a submit button was "clicked" with form_value, use it.
      otherwise, use the first submit button on the form, if any.
   otherwise:
      find the field using the same rules as form_value

   finally, if a button has been picked, submit using it;
   otherwise, submit without using a button

