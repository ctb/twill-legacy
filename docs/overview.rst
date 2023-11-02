.. _overview:

==============
twill Overview
==============

**twill** is a simple language that allows users to browse the Web from
a command-line interface. With twill, you can navigate through web
sites that use forms, cookies, and most standard Web features.

twill supports automated web testing and has a simple Python interface.
Check out the :ref:`examples`!

twill is open source and written in Python.

Downloading twill
-----------------

The latest release of twill is twill version 3.2.
It is available for `download`_ from the Python Package Index,
and you can use Python's `pip`_ tool to install or upgrade twill.
Please see the :ref:`changelog` for what's new in this version.

twill 3.2 works with Python 3.8 and newer.

To start using twill, install it and then type ``twill``.
At the prompt, type::

   go https://www.slashdot.org/
   show
   showforms
   showhistory

Documentation
-------------

The documentation for the latest release is published online at
https://twill-tools.github.io/twill/ and https://twill.readthedocs.io/.

Documentation is available for the following topics:

 * :ref:`examples` -- some short examples.

 * :ref:`browsing` -- General introduction to twill.

 * :ref:`commands` -- the twill scripting language.

 * :ref:`testing` -- how to use twill to test Web sites.

 * :ref:`extensions` -- extension modules that come with twill.

 * :ref:`python-api` -- for programmers interested in using twill from
   Python.

 * :ref:`developer` -- for developers interested in extending
   or fixing twill.

 * :ref:`other` -- projects relevant to, or based upon, twill.

Contributing
------------

Issues including bug reports, fixes or extensions and pull requests
can be submitted on the `GitHub project page`_.

When reporting bugs, please be sure to use the ``-f -l debug`` options
with ``twill`` so that we can see the full traceback.

Authors and License
-------------------

The original author of twill is C. Titus Brown, titus@idyll.org.
A number of people have contributed bug reports and code since the first
release; they are acknowledged below.

The original twill source code is Copyright (C) 2005, 2006, 2007
C. Titus Brown. twill is available under the `MIT license`_.

Acknowledgements and History
----------------------------

In May 2004, Cory Dodt had a great idea with "Python Browser Poseur"
(PBP), his insights helped C. Titus Brown. creating twill. Ian Bicking
had the idea of reimplementing PBP on top of IPython (since abandoned in
favor of cmd_), and suggested the "in-process" hack. Grig Gheorghiu was
strangely enthusiastic about a simple demo shown by Titus and promoted
twill since then. John J. Lee has promptly and enthusiastically checked
in various patches to mechanize created by Titus. Michele Simionato is
an early adopter who has also helped quite a bit.

Bug reports have come in from the following fine people: Chris Miles,
Matsuno Tokuhiro, Elvelind Grandin, Mike Rovner, sureshvv, Terry Peppers,
Kieran Holland, Alexander Shvedunov, Norman Khine, Leonardo Santagada,
Sebastien Pierre, Herve Cauwelier, aledain, Uy Do, David Hancock,
and Tomi Hautakoski.

Patches have been submitted by Joeri van Ruth, Paul McGuire, Ed Rahn,
Nic Ferrier, Robert Leftwich, James Cameron, William Volkman,
Tommi Virtanen, Simon Buenzli, sureshvv, Jeff Martin, Stephen
Thorne, and Bob Halley.

Features were proposed by Ben Bangert, and Tristan De Buysscher.

In April 2014, Ben Talyor created version 1.8 using requests and
lxml instead of mechanize.

In July 2016, Christoph Zwerschke created version 2.0 which also
integrates ideas and code from Flunc_ which was created by Luke Tucker
and Robert Marianski in 2006-2007, and from ReTwill_ which was created
in April 2012 as a fork from twill 0.9 by Adam Victor Brandizzi.

The official relaunch of twill on its current `GitHub project page`_
and the release of version 2.0 happened in April 2020 with the approval
of its original author C. Titus Brown, and Christoph Zwerschke acting
as new maintainer of the project.

In February 2021, twill 3.0 was released, followed by twill 3.1 in
October 2022, and twill 3.2 in October 2023. These versions do not
support Python 2 and more, adding type hints and more modernizations.

Thanks, all!

.. _GitHub project page: https://github.com/twill-tools/twill
.. _MIT license: https://opensource.org/licenses/MIT
.. _pip: https://pypi.python.org/pypi/pip
.. _download: https://pypi.org/project/twill/#files
.. _cmd: https://docs.python.org/3/library/cmd.html
.. _lxml: http://lxml.de/
.. _requests: http://docs.python-requests.org/
.. _Flunc: https://www.coactivate.org/projects/flunc/project-home
.. _Retwill: https://bitbucket.org/brandizzi/retwill/
