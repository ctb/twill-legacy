.. _developer:

================
Developing twill
================

twill is entirely written in Python. You will need Python 3.8
or newer to use and develop it.

Package tests
~~~~~~~~~~~~~

twill comes with several unit tests. They depend on `pytest`_ and
`Quixote`_. To run them, type 'pytest' in the top level directory.
To run an individual test, you can use the command
``pytest tests/test_something.py``.

.. _pytest: https://pytest.org/
.. _Quixote: http://quixote.ca/

Licensing
~~~~~~~~~

twill 0.8 and above are licensed under the `MIT license`_.
All code taken from twill 0.x is Copyright (C) 2005-2007
C. Titus Brown <titus@idyll.org>.

In plain English: C. Titus Brown owns the original code, but you're
welcome to use it, update it, subsume it into other projects, and
distribute it freely. However, you must retain copyright attribution.

Newer versions 1.x, 2.x and 3.x are also Copyright (C) 2007-2023
Ben R. Taylor, Adam V. Brandizzi, Christoph Zwerschke et al.

The newer versions are released under the same `MIT license`_.

.. _MIT license: http://www.opensource.org/licenses/mit-license.php

Developer releases
~~~~~~~~~~~~~~~~~~

"Developer releases" incorporating all recent significant changes are
made available at https://github.com/twill-tools/twill.
