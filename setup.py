#!/usr/bin/env python3

import re
import sys

from setuptools import setup

python_version = sys.version_info[:2]
if python_version < (3, 6):
    sys.exit("Python {}.{} is not supported by twill.".format(*python_version))

with open("twill/__init__.py") as init_file:
    init = init_file.read()
    description = re.search('"""(.*)', init).group(1)
    version = re.search("__version__ = '(.*)'", init).group(1)
    url = re.search("__url__ = '(.*)'", init).group(1)
    download_url = re.search("__download_url__ = '(.*)'", init).group(1)

with open("README.md") as readme_file:
    readme = readme_file.read()

require_twill = ['lxml>=4.6,<5', 'requests>=2.25,<3', 'pyparsing>=2.4,<3']
require_docs = ['sphinx>=3.4,<4', 'sphinx_rtd_theme>=0.5,<1']
require_tidy = ['pytidylib>=0.3,<0.4']
require_quixote = ['quixote>=3.3,<4']
require_wsgi_intercept = ['wsgi_intercept>=1.9,<2']
require_tests = [
    'pytest>=6.2,<7'] + require_tidy + require_quixote + require_wsgi_intercept


def main():

    setup(
        name='twill',

        version=version,
        url=url,
        download_url=download_url,
        description=description,

        author='C. Titus Brown, Ben R. Taylor et al.',
        author_email='titus@idyll.org',

        license='MIT',

        packages=['twill', 'twill.extensions'],

        entry_points=dict(console_scripts=[
            'twill=twill.shell:main', 'twill-fork=twill.fork:main']),

        maintainer='C. Titus Brown',
        maintainer_email='titus@idyll.org',

        long_description=readme,
        long_description_content_type='text/markdown',

        project_urls={
            'Source': 'https://github.com/twill-tools/twill',
            'Issues': 'https://github.com/twill-tools/twill/issues',
            'Documentation': 'https://twill-tools.github.io/twill/',
            'ChangeLog': 'https://twill-tools.github.io/twill/changelog.html'
        },

        classifiers=[
            'Development Status :: 6 - Mature',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Other Scripting Engines',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Software Development :: Testing'
        ],

        install_requires=require_twill,
        extras_require={
            'docs': require_docs,
            'tidy': require_tidy,
            'tests': require_tests
        },
    )


if __name__ == '__main__':
    main()
