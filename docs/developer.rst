.. _developer:

================
Developing twill
================

twill is entirely written in Python. You will need Python 2.7, 3.5
or newer to use and develop it.

Package tests
~~~~~~~~~~~~~

twill comes with several unit tests. They depend on `pytest`_,
`wsgi_intercept`_ and `Quixote`_. To run them, type 'pytest'
in the top level directory. To run an individual test, you can use
the command 'pytest tests/test_something.py'.

.. _pytest: https://pytest.org/
.. _wsgi_intercept: https://pypi.org/project/wsgi-intercept/
.. _Quixote: http://quixote.ca/

Licensing
~~~~~~~~~

twill 0.8 and above are licensed under the `MIT license`_.
All code taken from twill 0.8 is Copyright (C) 2005, 2006, 2007
C. Titus Brown <titus@idyll.org>.

In plain English: C. Titus Brown owns the original code, but you're
welcome to use it, update it, subsume it into other projects, and
distribute it freely. However, you must retain copyright attribution.

.. _MIT license: http://www.opensource.org/licenses/mit-license.php

Developer releases
~~~~~~~~~~~~~~~~~~

"Developer releases" incorporating all recent significant changes are
made available at https://github.com/twill-tools/twill.
