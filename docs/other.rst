.. _other:

==============================
Propaganda, tools and packages
==============================

Other opinions
~~~~~~~~~~~~~~

Grig Gheorgiu has written a blog entry on `Web app testing using twill`_.
Michele Simionato wrote a nice long article on `Testing Web Apps`_, and
Nitesh Djanjani `tried it out`_ as well.

.. _Web app testing using twill: http://agiletesting.blogspot.com/2005/09/web-app-testing-with-python-part-3.html
.. _Testing Web Apps: http://www.onlamp.com/pub/a/python/2005/11/03/twill.html
.. _tried it out: http://archive.oreilly.com/pub/wlg/8201

Offshoots from the twill project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

C. Titus Brown wrote a simple `wsgi_intercept`_ standalone package based
on the WSGI interception stuff for in-process testing of WSGI apps by twill.
This is for people who want to talk directly to their Web apps without going
through a network connection.

.. _wsgi_intercept: https://pypi.python.org/pypi/wsgi_intercept

Other Python-based Web testing and browsing tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For those who want to use Python-based toolkits to test their Web
apps, there are many great options. Here are some of them:

PBP_ was very similar to twill -- twill was initially based on it --
but the project seems to be defunct now.
Like PBP, twill was based on mechanize_ in the past,
unfortunately development of that project also stalled.
The current version is based on requests_ and lxml_ instead.

funkload_ is a nifty looking tool that does functional load testing.
It is built on webunit_.

webtest_ is an extension to ``unittest`` for testing `WSGI applications`_,
without starting up an HTTP server.

zope.testbrowser_ provides an easy-to-use programmable web browser with
special focus on testing.

mechanoid_ is a fork of mechanize_ that claims many bug fixes and a
different programming style. It's primarily used for scripting Web
sites, not for testing, but it can easily be used for testing.

PAMIE_ and PyXPCOM_ provide a Python interface for interacting with IE
and Mozilla-based browsers, respectively.

Finally, Selenium_ is an in-browser testing system that several people
have given rave reviews. Note that it's not written in Python...

You might also consider checking out Ian Bicking's proto-implementation
of `twill in Javascript`_.

As twill was based upon mechanize, so is Perl's `WWW::Mechanize::Shell`_
based upon `WWW::Mechanize`_. There's even an `HTTP::Recorder`_.
WebTst_ also looks interesting.

.. _funkload: http://funkload.nuxeo.org/
.. _`HTTP::Recorder`: http://www.perl.com/pub/a/2004/06/04/recorder.html
.. _lxml: http://lxml.de/
.. _maxq: http://maxq.tigris.org/
.. _mechanize: http://wwwsearch.sf.net/
.. _mechanoid: https://pypi.python.org/pypi/mechanoid
.. _PAMIE: http://sourceforge.net/projects/pamie/files/
.. _PBP: http://pbp.berlios.de/
.. _pyparsing: http://pyparsing.sourceforge.net/
.. _PyXPCOM: https://developer.mozilla.org/en-US/docs/Mozilla/Tech/XPCOM/Language_bindings/PyXPCOM
.. _Quixote: http://www.mems-exchange.org/software/quixote/
.. _requests: http://docs.python-requests.org/
.. _Selenium: http://www.seleniumhq.org/
.. _twill in Javascript: http://blog.ianbicking.org/twill-in-javascript.html
.. _webtest: https://pypi.python.org/pypi/WebTest
.. _WebTst: http://webtst.sourceforge.net/
.. _webunit: http://mechanicalcat.net/tech/webunit/
.. _WSGI:  http://www.python.org/peps/pep-0333.html
.. _WSGI applications: http://www.python.org/peps/pep-0333.html
.. _`WWW::Mechanize`: http://search.cpan.org/perldoc?WWW::Mechanize::Shell
.. _`WWW::Mechanize::Shell`: http://search.cpan.org/perldoc?WWW::Mechanize::Shell
.. _zope.testbrowser: https://pypi.python.org/pypi/zope.testbrowser

