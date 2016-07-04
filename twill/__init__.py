"""twill Web testing language and associated utilities."""

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

__version__ = "1.8.0"

__all__ = [
    "TwillCommandLoop",
    "execute_file", "execute_string",
    "get_browser", "set_loglevel", "set_output", "set_errout"]


this_dir = os.path.dirname(__file__)
# Add extensions directory at the *end* of sys.path.
# This means that user extensions will take priority over twill extensions.
extensions = os.path.join(this_dir, 'extensions')
sys.path.append(extensions)


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
        level = loglevels[level]
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


set_loglevel()
set_output()


# convenience function or two...
from .commands import get_browser


def get_browser_state():
    import warnings
    warnings.warn(
        "get_browser_state is deprecated;"
        " use get_browser() instead.", DeprecationWarning)
    return get_browser()


# the two core components of twill:
from .shell import TwillCommandLoop
from .parse import execute_file, execute_string


# initialize global dict
from . import namespaces
namespaces.init_global_dict()
