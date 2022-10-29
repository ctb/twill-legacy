"""
Various ugly utility functions for twill.

Apart from various simple utility functions, twill's robust parsing
code is implemented in the ConfigurableParsingFactory class.
"""

import os
import re

from typing import Any, List, NamedTuple, Optional, Union, Sequence, Tuple

from requests import Response
from requests.structures import CaseInsensitiveDict
from lxml.html import (
    fromstring as html_to_tree, tostring as tree_to_html,
    CheckboxGroup, FormElement, HtmlElement, InputElement,
    MultipleSelectOptions, RadioGroup, SelectElement, TextareaElement)

try:
    import tidylib  # type: ignore
except (ImportError, OSError):
    # ImportError can be raised when PyTidyLib package is not installed
    # OSError can be raised when the HTML Tidy shared library is not installed
    tidylib = None

from . import log, twill_ext
from .errors import TwillException

__all__ = [
    'gather_filenames', 'get_equiv_refresh_interval', 'html_to_tree',
    'is_hidden_filename', 'is_twill_filename', 'print_form',
    'make_boolean', 'make_int', 'make_twill_filename',
    'run_tidy', 'tree_to_html',  'trunc', 'unique_match',
    'CheckboxGroup', 'FieldElement', 'FormElement',
    'HtmlElement', 'InputElement', 'Link', 'RadioGroup',
    'ResultWrapper', 'SelectElement', 'Singleton', 'TextareaElement',
    'UrlWithRealm', 'Response']


FieldElement = Union[
    CheckboxGroup, InputElement, RadioGroup, SelectElement, TextareaElement]


class Link(NamedTuple):
    text: str
    url: str


# Depending on the configuration, realms can be ignored
UrlWithRealm = Union[str, Tuple[str, str]]


class Singleton:
    """A mixin class to create singleton objects."""

    def __new__(cls, *args, **kwargs):
        it = cls.__dict__.get('__it__')
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        return it

    @classmethod
    def reset(cls):
        cls.__it__ = None


class ResultWrapper:
    """Deal with request results, and present them in a unified form.

    These objects are returned by browser._journey()-wrapped functions.
    """
    def __init__(self, response: Response) -> None:
        self.response = response
        self.encoding = response.encoding
        try:
            self.tree = html_to_tree(self.text)
        except ValueError:
            # may happen when there is an XML encoding declaration
            self.tree = html_to_tree(self.content)
        self.xpath = self.tree.xpath
        self._fix_forms()

    @property
    def url(self) -> str:
        """"Get the url of the result page."""
        return self.response.url

    @property
    def http_code(self) -> int:
        """Get the http status code of the result page."""
        return self.response.status_code

    @property
    def text(self) -> str:
        """Get the text of the result page."""
        return self.response.text

    @property
    def content(self) -> bytes:
        """Get the binary content of the result page."""
        return self.response.content

    @property
    def headers(self) -> CaseInsensitiveDict:
        """Get the headers of the result page."""
        return self.response.headers

    @property
    def title(self) -> Optional[str]:
        """Get the title of the result page."""
        try:
            return self.xpath('//title[1]/text()')[0]
        except IndexError:
            return None

    @property
    def links(self) -> List[Link]:
        """Get all links in the result page."""
        return [Link(a.text_content(), a.get('href'))
                for a in self.xpath('//a[@href]')]

    def find_link(self, pattern: str) -> Optional[Link]:
        """Find a link with a given pattern on the result page."""
        regex = re.compile(pattern)
        for link in self.links:
            if regex.search(link.text) or regex.search(link.url):
                return link
        return None

    def form(self, name_or_num: Union[str, int] = 1) -> Optional[FormElement]:
        """Get the form with the given name or number on the result page.

        Returns None if no such form can be found on the result page.
        """
        forms = self.forms

        if isinstance(name_or_num, str):

            # first, try ID
            for form in forms:
                form_id = form.get('id')
                if form_id and form_id == name_or_num:
                    return form

            # next, try regex with name
            regex = re.compile(name_or_num)
            for form in forms:
                name = form.get('name')
                if name and regex.search(name):
                    return form

        # last, try number
        try:
            num = int(name_or_num) - 1
            if not 0 <= num < len(forms):
                raise IndexError
        except (ValueError, IndexError):
            return None
        else:
            return forms[num]

    def _fix_forms(self) -> None:
        """Fix forms on the page for use with twill."""
        # put all stray fields into a form
        orphans = self.xpath('//input[not(ancestor::form)]')
        if orphans:
            form_parts = [b'<form>'] + [
                tree_to_html(orphan) for orphan in orphans] + [b'</form>']
            self.forms = html_to_tree(b''.join(form_parts)).forms
            self.forms.extend(self.tree.forms)
        else:
            self.forms = self.tree.forms
        # convert all submit button elements to input elements, since
        # otherwise lxml will not recognize them as form input fields
        for form in self.forms:
            for button in form.xpath("//button[@type='submit']"):
                button.tag = 'input'


def trunc(s: Optional[str], length: int) -> str:
    """Truncate a string to a given length.

    The string is truncated by cutting off the last (length-4) characters
    and replacing them with ' ...'
    """
    if s and len(s) > length:
        return s[:length - 4] + ' ...'
    return s or ''


def print_form(form: FormElement, n: int) -> None:
    """Pretty-print the given form, with the assigned number."""
    info = log.info
    name = form.get('name')
    info('\nForm name=%s (#%d)', name, n) if name else info('\nForm #%d', n)

    if form.inputs is not None:
        info('## __Name__________________'
             ' __Type___ __ID________ __Value__________________')

        for n, field in enumerate(form.inputs, 1):
            value = field.value
            value_options = getattr(field, 'value_options', None)
            if value_options:
                items = ', '.join(
                    f"'{getattr(opt, 'name', opt)}'"
                    for opt in value_options)
                value_displayed = f'{value} of {items}'
            else:
                value_displayed = f'{value}'
            field_name = field.name
            field_type = getattr(field, 'type', 'select')
            field_id = field.get('id')
            strings = (
                f'{n:2}',
                f'{trunc(field_name, 24):24}',
                f'{trunc(field_type, 9):9}',
                f'{trunc(field_id, 12):12}',
                trunc(value_displayed, 40))
            info(' '.join(strings))
    info('')


def make_boolean(value: Any) -> bool:
    """Convert the input value into a boolean."""
    value = str(value).lower().strip()

    # true/false
    if value in ('true', 'false'):
        return value == 'true'

    # 0/nonzero
    try:
        ival = int(value)
    except ValueError:
        pass
    else:
        return bool(ival)

    # +/-
    if value in ('+', '-'):
        return value == '+'

    # on/off
    if value in ('on', 'off'):
        return value == 'on'

    raise TwillException(f"unable to convert '{value}' into true/false")


def make_int(value: Any) -> int:
    """Convert the input value into an int."""
    try:
        ival = int(value)
    except Exception:
        pass
    else:
        return ival

    raise TwillException(f"unable to convert '{value}' into an int")


def set_form_control_value(control: FieldElement, value: str) -> None:
    """Set the given control to the given value

    The controls can be checkboxes, select elements etc.
    """
    if isinstance(control, InputElement):
        if control.checkable:
            try:
                boolean_value = make_boolean(value)
            except TwillException:
                # if there's more than one checkbox,
                # it should be a CheckboxGroup, see below.
                pass
            else:
                control.checked = boolean_value
        elif control.type not in ('submit', 'image'):
            control.value = value

    elif isinstance(control, (TextareaElement, RadioGroup)):
        control.value = value

    elif isinstance(control, CheckboxGroup):
        if value.startswith('-'):
            value = value[1:]
            try:
                control.value.remove(value)
            except KeyError:
                pass
        else:
            if value.startswith('+'):
                value = value[1:]
            control.value.add(value)

    elif isinstance(control, SelectElement):
        # for ListControls we need to find the right *value*,
        # and figure out if we want to *select* or *deselect*
        if value.startswith('-'):
            add = False
            value = value[1:]
        else:
            add = True
            if value.startswith('+'):
                value = value[1:]

        # now, select the value.
        option_values = [val.strip() for val in control.value_options]
        options = control.getchildren()  # type: ignore
        option_names = [(c.text or '').strip() for c in options]
        for name, opt in zip(option_names, option_values):
            if value not in (name, opt):
                continue
            if isinstance(control.value, MultipleSelectOptions):
                if add:
                    control.value.add(opt)
                elif opt in control.value:
                    control.value.remove(opt)
            else:
                control.value = opt if add else ""
            break
        else:
            raise TwillException('Attempt to set an invalid value')

    else:
        raise TwillException('Attempt to set value on invalid control')


def _all_the_same_submit(matches: Sequence[FieldElement]) -> bool:
    """Check if a list of controls all belong to the same control.

    For use with checkboxes, hidden, and submit buttons.
    """
    name = value = None
    for match in matches:
        if not isinstance(match, InputElement):
            return False
        if match.type not in ('submit', 'hidden'):
            return False
        if name is None:
            name = match.name
            value = match.value
        elif match.name != name or match.value != value:
            return False
    return True


def _all_the_same_checkbox(matches: Sequence[FieldElement]) -> bool:
    """Check if a list of controls all belong to the same checkbox.

    Hidden controls can combine with checkboxes, to allow form
    processors to ensure a False value is returned even if user
    does not check the checkbox. Without the hidden control, no
    value would be returned.
    """
    name = None
    for match in matches:
        if not isinstance(match, InputElement):
            return False
        if match.type not in ('checkbox', 'hidden'):
            return False
        if name is None:
            name = match.name
        else:
            if match.name != name:
                return False
    return True


def unique_match(matches: Sequence[FieldElement]) -> bool:
    """Check whether a match is unique"""
    return (len(matches) == 1 or
            _all_the_same_checkbox(matches) or _all_the_same_submit(matches))


def run_tidy(html: str) -> Tuple[Optional[str], Optional[str]]:
    """Run HTML Tidy on the given HTML string.

    Return a 2-tuple (output, errors).  (None, None) will be returned if
    PyTidyLib (or the required shared library for tidy) isn't installed.
    """
    from .commands import options
    require_tidy = options.get('require_tidy')

    if not tidylib:
        if require_tidy:
            raise TwillException(
                'Option require_tidy is set, but PyTidyLib is not installed')
        return None, None

    opts = {key[5:].replace('_', '-'): value
            for key, value in options.items() if key.startswith('tidy_')}
    clean_html, errors = tidylib.tidy_document(html, opts)
    return clean_html, errors


def get_equiv_refresh_interval() -> Optional[int]:
    """Get the smallest interval for which the browser should follow redirects.

    Redirection happens if the given interval is smaller than this.
    """
    from .commands import options
    return options.get('equiv_refresh_interval')


def is_hidden_filename(filename: str) -> bool:
    """Check if this is a hidden file (starting with a dot)."""
    return filename not in (
        '.', '..') and os.path.basename(filename).startswith('.')


def is_twill_filename(filename: str) -> bool:
    """Check if the given filename has the twill file extension."""
    return filename.endswith(twill_ext) and not is_hidden_filename(filename)


def make_twill_filename(name: str) -> str:
    """Add the twill extension to the name of a script if necessary."""
    if name not in ('.', '..'):
        twill_name, ext = os.path.splitext(name)
        if not ext:
            twill_name += twill_ext
            if os.path.exists(twill_name):
                name = twill_name
    return name


def gather_filenames(args: Sequence[str]) -> List[str]:
    """Collect script files from within directories."""
    names: List[str] = []
    for arg in args:
        name = make_twill_filename(arg)
        if os.path.isdir(name):
            for dir_path, dir_names, filenames in os.walk(arg):
                dir_names[:] = [
                    d for d in dir_names if not is_hidden_filename(d)]
                for filename in filenames:
                    if not is_twill_filename(filename):
                        continue
                    filename = os.path.join(dir_path, filename)
                    names.append(filename)
        else:
            names.append(name)
    return names
