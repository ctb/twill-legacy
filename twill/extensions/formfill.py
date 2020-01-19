"""
Extension functions for easier form filling.

(This module is a dumping ground for features that may ultimately get
added into the main twill command set.)

Commands:

 * fv_match -- fill in *all* fields that match a regex (unlike 'formvalue'
        which will complain about multiple matches).  Useful for forms
        with lots of repeated fieldnames -- 'field-1', 'field-2', etc.

 * fv_multi -- fill in multiple form fields at once, e.g.

          fv_multi <formname> field1=value1 field2=value2 field3=value3

 * fv_multi_sub -- same as 'fv_multi', followed by a 'submit'.
"""

import re

from twill import browser, commands, log, utils

__all__ = ['fv_match', 'fv_multi_match', 'fv_multi', 'fv_multi_sub']


def fv_match(formname, regex, value):
    """>> fv_match <formname> <field regex> <value>

    Set value of *all* form fields with a name that matches the given
    regular expression.

    (Unlike 'formvalue' or 'fv', this will not complain about multiple
    matches!)
    """
    form = browser.form(formname)
    if form is None:
        log.error("no such form '%s'", formname)
        return

    regex = re.compile(regex)

    matches = [
        ctl for ctl in form.inputs if regex.search(str(ctl.get('name')))]

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


def fv_multi_match(formname, regex, *values):
    """>> fv_multi_match <formname> <field regex> <value> [<value> [<value>..]]

    Set value of each consecutive matching form field with the next specified
    value.  If there are no more values, use the last for all remaining form
    fields
    """
    form = browser.form(formname)
    if form is None:
        log.error("no such form '%s'", formname)
        return

    regex = re.compile(regex)

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


def fv_multi(formname, *pairs):
    """>> fv_multi <formname> [<pair1> [<pair2> [<pair3>]]]

    Set multiple form fields; each pair should be of the form

        fieldname=value

    The pair will be split around the first '=', and
    'fv <formname> fieldname value' will be executed in the order the
    pairs are given.
    """
    for p in pairs:
        fieldname, value = p.split('=', 1)
        commands.fv(formname, fieldname, value)


def fv_multi_sub(formname, *pairs):
    """>> fv_multi_sub <formname> [<pair1> [<pair2> [<pair3>]]]

    Set multiple form fields (as with 'fv_multi') and then submit().
    """
    for p in pairs:
        fieldname, value = p.split('=', 1)
        commands.fv(formname, fieldname, value)

    commands.submit()
