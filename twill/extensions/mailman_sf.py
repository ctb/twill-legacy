"""
Extension functions to discard all moderated messages in a SourceForge-based
mailman queue.

(Currently there is no way to do this without manually selecting 'discard'
for each and every message.)
"""

import re

from twill import browser, log, utils

__all__ = ['discard_all_messages', 'exit_if_empty']


def exit_if_empty():
    """>> exit_if_empty

    Exit the script currently running, if there are no deferred messages
    on the current page.
    """
    form = browser.form()
    if not form:
        log.error("No messages; exiting.")
        raise SystemExit


def discard_all_messages():
    """>> discard_all_messages

    Set all buttons to "discard".
    """
    _form_value_by_regex_setall('1', '^\\d+$', '3')


def _form_value_by_regex_setall(form_name, field_name, value):
    form = browser.form(form_name)
    if not form:
        log.error("no such form '%s'", form_name)
        return

    regex = re.compile(field_name)

    matches = [ctl for ctl in form.controls if regex.search(str(ctl.name))]

    if matches:
        log.info('-- matches %d', len(matches))

        n = 0
        for control in matches:
            browser.clicked(form, control)
            if not control.readonly:
                utils.set_form_control_value(control, value)
                n += 1

        log.info('set %d values total', n)
