#!/usr/bin/env python

import os
import re
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

python_version = sys.version_info[:2]
if not (2, 6) <= python_version <= (2, 7):
    sys.exit("Python %s.%s is not supported by twill." % python_version)


class PyTest(TestCommand):

    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

with open(os.path.join(os.path.dirname(__file__),
                       'twill', '__init__.py')) as initfile:
    VERSION = re.compile(r".*__version__ = '(.*?)'",
                         re.S).match(initfile.read()).group(1)

setup(
    name='twill',
    version=VERSION,
    download_url='https://pypi.python.org/pypi/twill',

    description='twill Web browsing language',
    author='C. Titus Brown and Ben R. Taylor',
    author_email='titus@idyll.org',
    license='MIT',

    packages=['twill', 'twill.extensions'],

    # allow both
    entry_points=dict(console_scripts=['twill=twill.shell:main']),
    scripts=['twill-fork'],

    maintainer='C. Titus Brown',
    maintainer_email='titus@idyll.org',

    url='http://twill.idyll.org/',
    long_description="""\
A scripting system for automating Web browsing.  Useful for testing
Web pages or grabbing data from password-protected sites automatically.""",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Other Scripting Engines',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Testing'
    ],

    install_requires=['lxml', 'cssselect', 'requests', 'pyparsing'],
    extras_require={'tidy': ['pytidylib'], 'xpath': ['beautifulsoup4']},
    tests_require=['pytest', 'quixote', 'pytidylib', 'beautifulsoup4'],
    cmdclass={'test': PyTest}
)
