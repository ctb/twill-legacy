"""twill web browsing and testing language and associated utilities.

A scripting system for automating web browsing.  Useful for testing
web pages or grabbing data from password-protected sites automatically.
"""

# This file is part of the twill source distribution.
#
# twill is a extensible scriptlet language for testing Web apps,
# available at http://twill.idyll.org/.
#
# Contact author: C. Titus Brown, titus@idyll.org.
#
# This program and all associated source code files are Copyright (C)
# 2005-2007 by C. Titus Brown.  It is released under the MIT license;
# please see the included LICENSE.txt file for more information, or
# go to http://www.opensource.org/licenses/mit-license.php.

import logging
import sys
import os.path

__version__ = '2.0.2'

__url__ = 'https://github.com/twill-tools/twill'
__download_url__ = 'https://pypi.org/project/twill/'

__all__ = [
    'browser', 'execute_file', 'execute_string',
    'set_loglevel', 'set_output', 'set_errout',
    'twill_ext', 'TwillCommandLoop']


this_dir = os.path.dirname(__file__)
# Add extensions directory at the *end* of sys.path.
# This means that user extensions will take priority over twill extensions.
extensions = os.path.join(this_dir, 'extensions')
sys.path.append(extensions)

twill_ext = '.twill'  # file extension for twill scripts


loglevels = dict(
    CRITICAL=logging.CRITICAL,
    ERROR=logging.ERROR,
    WARNING=logging.WARNING,
    INFO=logging.INFO,
    DEBUG=logging.DEBUG,
    NOTSET=logging.NOTSET)

log = logging.getLogger()
handler = None


def set_loglevel(level=None):
    """Set the logging level.

    If no level is passed, use INFO as loging level.
    """
    if level is None:
        level = logging.INFO
    if isinstance(level, str):
        level = loglevels[level.upper()]
    log.setLevel(level)


def set_output(stream=None):
    """Set the standard output.

    If no stream is passed, use standard output.
    """
    global handler
    if stream is None:
        stream = sys.__stdout__
    if handler:
        log.removeHandler(handler)
    handler = logging.StreamHandler(stream)
    log.addHandler(handler)
    sys.stdout = stream


def set_errout(stream=None):
    """Set the error output.

    If no stream is passed, use standard error.
    """
    if stream is None:
        stream = sys.__stderr__
    sys.stderr = stream


def shutdown():
    """Shut down and flush the logging sytem."""
    sys.stdout.flush()
    sys.stderr.flush()
    logging.shutdown()


set_loglevel()
set_output()


# a convenience function:
from .browser import browser  # noqa: ignore=E402

# the two core components of twill:
from .parse import execute_file, execute_string  # noqa: ignore=E402
from .shell import TwillCommandLoop  # noqa: ignore=E402

# initialize global dict
from . import namespaces  # noqa: ignore=E402
namespaces.init_global_dict()
