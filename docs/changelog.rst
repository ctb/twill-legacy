.. _changelog:

=========
ChangeLog
=========

2.0.2 (released 2021-02-13)
---------------------------

* Also support Python 3.9
* 'tidy_should_exist' has been renamed ot 'require_tidy'.
* Support for setting options to be used with HTML Tidy.
* Cleanup scripts are now also read as UTF-8 in Python 3.


2.0.1 (released 2020-07-12)
---------------------------

* Fixes an issue with encoding declarations (#5).

2.0 (released 2020-04-04)
-------------------------

This version is based on twill 1.8, which was a refactoring
of version 0.9 that used requests_ and lxml_ instead of mechanize_,
done by Ben Taylor in April 2014. It also integrates ideas and
code from Flunc_ which was created by Luke Tucker and Robert Marianski
in 2006-2007, and from ReTwill_ which was created in April 2012
as a fork from twill 0.9 by Adam Victor Brandizzi.
The following improvements and changes were made in this version:

* Larger refactoring, clean-up and modernization efforts to support
  Python 2.7, 3.5 and higher.
* The console script has been renamed from 'twill-sh' to just 'twill'.
* We assume the default file extension '.twill' for twill scripts now.
* Uses lxml_ and requests_ instead of mechanize_ (like in version 1.8),
  but doesn't need cssselect_ and `Beautiful Soup`_ any more (unlike 1.8).
* Removed bundled packages which have become unnecessary (mechanize)
  or are available in newer versions on PyPI (pyparsing, wsgi_intercept)
  or in the standard library (subprocess).
* Removed parsing options (use_tidy, use_BeautifulSoup, allow_parse_errors)
  which have become insignificant due to the use of lxml.html.
* We use pytest_ instead of nose_ for testing twill now.
* A tox_ configuration file for running tests with different Python versions
  has been added.
* Optimized the order of the URLs that are tried out by the twill browser.
* Added an option '-d' to dump the last HTML to a file or standard output
  and an option '-w' to show the HTML directly in the web browser (this
  feature was taken over from Flunc).
* Added alias 'rf' for 'runfiles' and made runfiles run directories of
  scripts as well. This helps writing test suites for twill scripts.
* Added command 'add_cleanup' to unconditionally run cleanup scripts after
  the current script finished. This allows resetting the state of the
  tested server, so that tests will always re-run on a clean state.
  Together with a small init.twill script, this creates a test fixture.
  (This idea was taken from Flunc, which supports cleanup scripts for
  test suites, although in a somewhat different way.)
* Non string values are now accepted in variable substitution (this feature
  has been backported from ReTwill).
* XPath expressions are now supported in find/notfind commands (this feature
  has been backported from ReTwill).
* Made output better controllable by using log levels (this feature has
  been backported from ReTwill). See options '-l' and '-o'.
* Updated the map of predefined user agent strings.
* Basic authentication with realm is now supported again
  (the 'with_default_realm' option, which was broken in version 1.8,
  has been switched off).
* Server certificates are not verified by default any more, since they are
  usually not valid on test and staging servers.
* Improved handling of meta refresh. Circular redirects are detected and
  'debug equiv-refresh' is functional again. A limit for the refresh time
  interval can be set with the 'equiv_refresh_interval' option. By default
  this is set to 2, so refresh intervals of 2 or more seconds are ignored.
* Moved the  examples and additional stuff into an 'extras' directory.
* The documentation in the 'docs' directory has been updated and is now
  created with Sphinx_.
* Made sure everything (except twill-forks) also works on Windows.
* Fixed a lot of smaller and larger bugs and problems.

.. _lxml: https://lxml.de/
.. _requests: https://2.python-requests.org/
.. _mechanize: https://mechanize.readthedocs.io/
.. _cssselect: https://github.com/scrapy/cssselect
.. _Beautiful Soup: https://www.crummy.com/software/BeautifulSoup/
.. _Flunc: https://www.coactivate.org/projects/flunc/project-home
.. _Retwill: https://bitbucket.org/brandizzi/retwill/
.. _Sphinx: https://www.sphinx-doc.org/
.. _pytest: https://pytest.org/
.. _nose: https://nose.readthedocs.io/
.. _tox: https://tox.readthedocs.io/
