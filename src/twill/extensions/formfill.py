"""
Extension functions for easier form filling.

(This module is a dumping ground for features that may ultimately get
added into the main twill command set.)

Commands:

 * fv_match -- fill in *all* fields that match a regex (unlike 'form_value'
        which will complain about multiple matches).  Useful for forms
        with lots of repeated field names -- 'field-1', 'field-2', etc.

 * fv_multi -- fill in multiple form fields at once, e.g.

          fv_multi <form_name> field1=value1 field2=value2 field3=value3

 * fv_multi_sub -- same as 'fv_multi', followed by a 'submit'.
"""

import re

from twill import browser, commands, log, utils

__all__ = ['fv_match', 'fv_multi_match', 'fv_multi', 'fv_multi_sub']


def fv_match(form_name: str, field_pattern: str, value: str) -> None:
    """>> fv_match <form_name> <field_pattern> <value>

    Set value of *all* form fields with a name that matches the given
    regular expression pattern.

    (Unlike 'form_value' or 'fv', this will not complain about multiple
    matches!)
    """
    form = browser.form(form_name)
    if form is None:
        log.error("no such form '%s'", form_name)
        return

    regex = re.compile(field_pattern)

    matches = [ctl for ctl in form.inputs
               if regex.search(str(ctl.get('name')))]

    if matches:
        log.info('-- matches %d', len(matches))

        n = 0
        for control in matches:
            browser.clicked(form, control)
            if 'readonly' in control.attrib:
                continue

            n += 1
            utils.set_form_control_value(control, value)

        log.info('set %d values total', n)


def fv_multi_match(form_name: str, field_pattern: str, *values: str) -> None:
    """>> fv_multi_match <form_name> <field_pattern> <value>...

    Set value of each consecutive form field matching the given pattern with
    the next specified value.  If there are no more values, use the last for
    all remaining form fields.
    """
    form = browser.form(form_name)
    if form is None:
        log.error("no such form '%s'", form_name)
        return

    regex = re.compile(field_pattern)

    matches = [
        ctl for ctl in form.inputs if regex.search(str(ctl.get('name')))]

    if matches:
        log.info('-- matches %d, values %d', len(matches), len(values))

        for n, control in enumerate(matches):
            browser.clicked(form, control)
            if 'readonly' in control.attrib:
                continue
            try:
                utils.set_form_control_value(control, values[n])
            except IndexError:
                utils.set_form_control_value(control, values[-1])

        log.info('set %d values total', n)


def fv_multi(form_name: str, *pairs: str) -> None:
    """>> fv_multi <form_name> <pair>...

    Set multiple form fields; each pair should be of the form

        field_name=value

    The pair will be split around the first '=', and
    'fv <form_name> field_name value' will be executed in the order the
    pairs are given.
    """
    for pair in pairs:
        field_name, value = pair.split('=', 1)
        commands.fv(form_name, field_name, value)


def fv_multi_sub(form_name: str, *pairs: str) -> None:
    """>> fv_multi_sub <form_name> <pair>...

    Set multiple form fields (as with 'fv_multi') and then submit().
    """
    for pair in pairs:
        field_name, value = pair.split('=', 1)
        commands.fv(form_name, field_name, value)

    commands.submit()
