#!/usr/bin/env python

import os
import re
import sys

python_version = sys.version_info[:2]
if not (2, 6) <= python_version <= (2, 7) and not python_version >= (3, 3):
    sys.exit("Python %s.%s is not supported by twill." % python_version)

from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):

    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


def extract_desc(content):
    d = re.search('"""(.*?)"""', content, re.S).group(1)
    d = d.split('\n', 1)
    d = (d[0].strip(), d[1].strip())
    return d


def extract_var(content, what):
    return re.search("__%s__ = '(.*?)'" % (what,), content).group(1)


with open(os.path.join(os.path.dirname(__file__),
                       'twill', '__init__.py')) as initfile:
    content = initfile.read()
    description = extract_desc(content)
    version = extract_var(content, 'version')
    url = extract_var(content, 'url')
    download_url = extract_var(content, 'download_url')


def main():

    setup(
        name='twill',

        version=version,
        url=url,
        download_url=download_url,
        description=description[0],

        author='C. Titus Brown and Ben R. Taylor',
        author_email='titus@idyll.org',

        license='MIT',

        packages=['twill', 'twill.extensions'],

        entry_points=dict(console_scripts=[
            'twill=twill.shell:main', 'twill-fork=twill.fork:main']),

        maintainer='C. Titus Brown',
        maintainer_email='titus@idyll.org',

        long_description=description[1],

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
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Other Scripting Engines',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Software Development :: Testing'
        ],

        install_requires=['lxml>=3.0', 'requests>=2.0', 'pyparsing>=2.0'],
        extras_require={'tidy': ['pytidylib']},
        tests_require=['pytest', 'quixote', 'pytidylib'],
        cmdclass={'test': PyTest}
    )


if __name__ == '__main__':
    main()
