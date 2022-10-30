# This file is part of the twill source distribution.
#
# twill is an extensible scriptlet language for testing Web apps,
# available at https://github.com/twill-tools/twill.
#
# Copyright (c) 2005-2022
# by C. Titus Brown, Ben R. Taylor, Christoph Zwerschke et al.
#
# This program and all associated source code files are released under the
# terms of the MIT license; please see the included LICENSE file for more
# information, or go to https://opensource.org/licenses/mit-license.php.

"""twill web browsing and testing language and associated utilities.

A scripting system for automating web browsing.  Useful for testing
web pages or grabbing data from password-protected sites automatically.
"""

import logging
import sys
import os.path

__version__ = '3.1'

__url__ = 'https://github.com/twill-tools/twill'
__download_url__ = 'https://pypi.org/project/twill/'

__all__ = [
    'browser', 'execute_file', 'execute_string',
    'log', 'set_log_level', 'set_output', 'set_err_out',
    'twill_ext', 'TwillCommandLoop']


this_dir = os.path.dirname(__file__)
# Add extensions directory at the *end* of sys.path.
# This means that user extensions will take priority over twill extensions.
extensions = os.path.join(this_dir, 'extensions')
sys.path.append(extensions)

twill_ext = '.twill'  # file extension for twill scripts


log_levels = dict(
    CRITICAL=logging.CRITICAL,
    ERROR=logging.ERROR,
    WARNING=logging.WARNING,
    INFO=logging.INFO,
    DEBUG=logging.DEBUG,
    NOTSET=logging.NOTSET)

log = logging.getLogger(__name__)
handler = None

stdout, stderr = sys.stdout, sys.stderr


def set_log_level(level=None):
    """Set the logging level.

    If no level is passed, use INFO as logging level.
    """
    if level is None:
        level = logging.INFO
    if isinstance(level, str):
        level = log_levels[level.upper()]
    log.setLevel(level)


def set_output(stream=None):
    """Set the standard output.

    If no stream is passed, use standard output.
    """
    global handler
    if stream is None:
        stream = stdout
    if handler:
        log.removeHandler(handler)
    handler = logging.StreamHandler(stream)
    log.addHandler(handler)
    sys.stdout = stream


def set_err_out(stream=None):
    """Set the error output.

    If no stream is passed, use standard error.
    """
    if stream is None:
        stream = stderr
    sys.stderr = stream


def shutdown():
    """Shut down and flush the logging system."""
    sys.stdout.flush()
    sys.stderr.flush()
    logging.shutdown()


set_log_level()
set_output()


# a convenience function:
from .browser import browser  # noqa: ignore=E402

# the two core components of twill:
from .parse import execute_file, execute_string  # noqa: ignore=E402
from .shell import TwillCommandLoop  # noqa: ignore=E402

# initialize global dict
from . import namespaces  # noqa: ignore=E402
namespaces.init_global_dict()
