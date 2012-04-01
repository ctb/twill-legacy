"""
Extension functions to discard all moderated messages in a SourceForge-based
mailman queue.

(Currently there is no way to do this without manually selecting 'discard'
for each and every message.)
"""

import twill, twill.utils
import re
from twill import logconfig

logger = logconfig.logger

# export:
__all__ = ['discard_all_messages',
           'exit_if_empty'
           ]

def exit_if_empty():
    """
    >> exit_if_empty

    Exit the script currently running, if there are no deferred messages
    on the current page.
    """
    state = twill.get_browser()
    form = state.get_form("1")
    if not form:
        logger.error("No messages; exiting.")
        raise SystemExit
    
def discard_all_messages():
    """
    >> discard_all_messages

    Set all buttons to "discard".
    """
    _formvalue_by_regexp_setall("1", "^\d+$", "3")

### utility functions

def _formvalue_by_regexp_setall(formname, fieldname, value):
    state = twill.get_browser()
    
    form = state.get_form(formname)
    if not form:
        logger.error('no such form %s', formname)
        return

    regexp = re.compile(fieldname)

    matches = [ ctl for ctl in form.controls if regexp.search(str(ctl.name)) ]

    if matches:
        logger.error('-- matches %d', len(matches))

        n = 0
        for control in matches:
            state.clicked(form, control)
            if control.readonly:
                continue

            n += 1
            twill.utils.set_form_control_value(control, value)

        logger.error('set %d values total', n)
