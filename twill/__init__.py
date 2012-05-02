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

"""
twill Web testing language & associated utilities.
"""

__version__ = "1.0.0b1"

#import warnings
#warnings.defaultaction = "error"

#import pychecker.checker

__all__ = [ "TwillCommandLoop",
            "execute_file",
            "execute_string",
            "get_browser",
            "add_wsgi_intercept",
            "remove_wsgi_intercept",
            "set_output",
            "set_errout"]

#
# add extensions (twill/extensions) and the the wwwsearch & pyparsing
# stuff from twill/included-packages/.  NOTE: this works with eggs! hooray!
#

import sys, os.path
thisdir = os.path.dirname(__file__)

# add extensions directory at the *end* of sys.path.  This means that
# user extensions will take priority over twill extensions.
extensions = os.path.join(thisdir, 'extensions')
sys.path.append(extensions)

# add other_packages in at the *beginning*, so that the correct
# (patched) versions of pyparsing and mechanize get imported.
wwwsearchlib = os.path.join(thisdir, 'other_packages')
sys.path.insert(0, wwwsearchlib)

# the two core components of twill:
from shell import TwillCommandLoop
from parse import execute_file, execute_string

# convenience function or two...
from commands import get_browser

def get_browser_state():
    import warnings
    warnings.warn("""\
get_browser_state is deprecated; use 'twill.get_browser() instead.
""", DeprecationWarning)
    return get_browser()

# initialize global dict
import namespaces
namespaces.init_global_dict()

from wsgi_intercept import add_wsgi_intercept, remove_wsgi_intercept

def set_output(fp):
    """
    Changes stdout.
    """
    sys.stdout = fp if fp else sys.stdout

def set_errout(fp):
    """
    Changes stderr
    """
    sys.stderr = fp if fp else sys.stderr
