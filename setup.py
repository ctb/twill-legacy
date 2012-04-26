#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    print('importing distutils, not setuptools')
    from distutils.core import setup

#### retwill info.

setup(name = 'retwill',
      version = '1.0.0',
      download_url = 'https://bitbucket.org/brandizzi/retwill/downloads/retwill-1.0.0.tar.gz',
      description = "retwill - fork of C. Titus Brown's twill Web browsing language",
      author = 'C. Titus Brown',
      author_email = 'titus@idyll.org',
      packages = ['twill',
                  'twill.extensions',
                  'twill.extensions.match_parse'],
      # allow both
      entry_points = dict(console_scripts=['twill-sh = twill.shell:main'],),
      scripts = ['twill-fork'],
      maintainer = 'Adam Victor Nazareth Brandizzi ',
      maintainer_email = 'brandizzi@gmail.com',
      url = 'http://bitbucket.org/brandizzi/retwill/',
      long_description = """\
retwill is a fork of the acclaimed but apparently abandoned twill Web browsing
language.

Twill is a scripting system for automating Web browsing.  Useful for testing
Web pages or grabbing data from password-protected sites automatically.
""",
      classifiers = ['Development Status :: 4 - Beta',
                     'Environment :: Console',
                     'Intended Audience :: Developers',
                     'Intended Audience :: System Administrators',
                     'License :: OSI Approved :: MIT License',
                     'Natural Language :: English',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Programming Language :: Other Scripting Engines',
                     'Topic :: Internet :: WWW/HTTP',
                     'Topic :: Software Development :: Testing',
                     ],

      obsoletes = 'twill',
      test_suite = 'nose.collector',
      install_requires = [
                'lxml', 'nose', 'pyparsing',
                'beautifulsoup', 'wsgi_intercept'],
      tests_require =  ['quixote'],
      )
