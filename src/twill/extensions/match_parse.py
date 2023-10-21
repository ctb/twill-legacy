"""
Suresh's extension for slicing and dicing variables with regular expressions.
"""

import re

from twill import browser, log
from twill.namespaces import get_twill_glocals


def showvar(which):
    """>> showvar var

    Shows the value of the variable 'var'.
    """
    global_dict, local_dict = get_twill_glocals()

    d = global_dict.copy()
    d.update(local_dict)

    log.info(d.get(str(which)))


def split(what):
    """>> split <regex>

    Sets __matchlist__ to re.split(regex, page).
    """
    page = browser.html

    m = re.split(what, page)

    global_dict, local_dict = get_twill_glocals()
    local_dict['__matchlist__'] = m


def findall(what):
    """>> findall <regex>

    Sets __matchlist__ to re.findall(regex, page).
    """
    page = browser.html

    regex = re.compile(what, re.DOTALL)
    m = regex.findall(page)

    global_dict, local_dict = get_twill_glocals()
    local_dict['__matchlist__'] = m


def getmatch(where, what):
    """>> getmatch into_var expression

    Evaluates an expression against __match__ and puts it into 'into_var'.
    """
    global_dict, local_dict = get_twill_glocals()
    match = local_dict['__match__']
    local_dict[where] = _do_eval(match, what)


def setmatch(what):
    """>> setmatch expression

    Sets each element __matchlist__ to eval(expression); 'm' is set
    to each element of __matchlist__ prior to processing.
    """
    global_dict, local_dict = get_twill_glocals()

    match = local_dict['__matchlist__']
    if isinstance(match, str):
        match = [match]

    new_match = [_do_eval(m, what) for m in match]
    local_dict['__matchlist__'] = new_match


def _do_eval(match, exp):
    """Used internally to evaluate an expression."""
    return eval(exp, globals(), {'m': match})


def popmatch(which):
    """>> popmatch index

    Pops __matchlist__[i] into __match__.
    """
    global_dict, local_dict = get_twill_glocals()

    matchlist = local_dict['__matchlist__']
    match = matchlist.pop(int(which))
    local_dict['__match__'] = match
