"""This module implements the TwillBrowser."""

import pickle
import re
from typing import (
    cast, Callable, Dict, IO, List, Optional, Sequence, Tuple, Union)
from urllib.parse import urljoin

from requests import Session
from requests.auth import HTTPBasicAuth
from requests.cookies import RequestsCookieJar
from requests.exceptions import InvalidSchema, ConnectionError
from requests.structures import CaseInsensitiveDict

from . import log, __version__
from .utils import (
    get_equiv_refresh_interval, html_to_tree, print_form, trunc, unique_match,
    CheckboxGroup, FieldElement, FormElement, HtmlElement,
    InputElement, Link, UrlWithRealm, RadioGroup, Response, ResultWrapper)
from .errors import TwillException

__all__ = ['browser']


def _disable_insecure_request_warnings() -> None:
    """Disable insecure request warnings."""
    try:
        from requests.packages import urllib3  # type: ignore
    except ImportError:
        import urllib3  # type: ignore
    # noinspection PyUnresolvedReferences
    insecure_request_warning = urllib3.exceptions.InsecureRequestWarning
    urllib3.disable_warnings(insecure_request_warning)


def _set_http_connection_debuglevel(level: int) -> None:
    """Set the debug level for the connection pool."""
    from http.client import HTTPConnection
    HTTPConnection.debuglevel = level


class TwillBrowser:
    """A simple, stateful browser"""

    user_agent = f'TwillBrowser/{__version__}'

    def __init__(self):
        self.result: Optional[ResultWrapper] = None
        self.last_submit_button: Optional[InputElement] = None
        self.first_error: Optional[str] = None

        # whether meta refresh will be displayed
        self.show_refresh = False

        # debug level to be used for the connection pool
        self._debug_level = 0

        # whether the SSL cert will be verified, or can be a ca bundle path
        self.verify = False

        # Session stores cookies
        self._session = Session()

        # A lxml FormElement, None until a form is selected
        # replaces self._browser.form from mechanize
        self._form: Optional[FormElement] = None
        self._form_files: Dict[str, IO] = {}

        # A dict of HTTPBasicAuth from requests, keyed off URL
        self._auth: Dict[UrlWithRealm, HTTPBasicAuth] = {}

        # callables to be called after each page load.
        self._post_load_hooks: List[Callable] = []

        self._history: List[ResultWrapper] = []

        # set default headers
        self.reset_headers()

    def _assert_result_for(self, what: str) -> ResultWrapper:
        if not self.result:
            raise TwillException(f"Cannot get {what} since there is no page.")
        return self.result

    @property
    def debug_level(self) -> int:
        return self._debug_level

    @debug_level.setter
    def debug_level(self, level: int) -> None:
        _set_http_connection_debuglevel(level)
        self._debug_level = level

    def reset(self):
        """Reset the browser"""
        self.__init__()

    @property
    def creds(self) -> Dict[UrlWithRealm, HTTPBasicAuth]:
        """Get the credentials for basic authentication."""
        return self._auth

    def add_creds(self, url: UrlWithRealm, user: str, password: str) -> None:
        """Set the credentials for basic authentication."""
        self._auth[url] = HTTPBasicAuth(user, password)

    def go(self, url: str) -> None:
        """Visit given URL."""
        try_urls: List[str] = []
        if '://' in url:
            try_urls.append(url)
        else:  # URL does not have a schema
            # if this is a relative URL, then assume that we want to tack it
            # onto the end of the current URL
            current_url = self.url
            if current_url:
                try_urls.append(urljoin(current_url, url))
            # if this is an absolute URL, it may be just missing the 'http://'
            # at the beginning, try fixing that (mimic browser behavior)
            if not url.startswith(('.', '/', '?')):
                # noinspection HttpUrlsUsage
                try_urls.append(f'http://{url}')
                try_urls.append(f'https://{url}')
        for try_url in try_urls:
            try:
                self._journey('open', try_url)
            except (IOError,
                    ConnectionError, InvalidSchema, UnicodeError) as error:
                log.info("cannot go to '%s': %s", try_url, error)
            else:
                break
        else:
            raise TwillException(f"cannot go to '{url}'")
        log.info('==> at %s', self.url)

    def reload(self) -> None:
        """Tell the browser to reload the current page."""
        self._journey('reload')
        log.info('==> reloaded')

    def back(self) -> None:
        """Return to previous page, if possible."""
        try:
            self._journey('back')
            log.info('==> back to %s', self.url)
        except TwillException:
            log.warning('==> back at empty page')

    @property
    def code(self) -> int:
        """Get the HTTP status code received for the current page."""
        return self._assert_result_for('status code').http_code

    @property
    def encoding(self) -> Optional[str]:
        """Get the encoding used by the server for the current page."""
        return None if self.result is None else self.result.encoding

    @property
    def html(self) -> str:
        """Get the HTML for the current page."""
        return self._assert_result_for('HTML').text

    @property
    def dump(self) -> bytes:
        """Get the binary content of the current page."""
        return self._assert_result_for('content dump').content

    @property
    def title(self) -> Optional[str]:
        return self._assert_result_for('title').title

    @property
    def url(self):
        """Get the URL of the current page."""
        return self.result.url if self.result else None

    def find_link(self, pattern: str) -> Optional[Link]:
        """Find the first link matching the given regular expression pattern.

        The pattern is searched in the URL and in the link text.
        """
        return self._assert_result_for('links').find_link(pattern)

    def follow_link(self, link: Union[str, Link]) -> None:
        """Follow the given link."""
        self._journey('follow_link', link)
        log.info('==> at %s', self.url)

    @property
    def headers(self) -> CaseInsensitiveDict:
        """Return the request headers currently used by the browser."""
        return self._session.headers

    def reset_headers(self):
        """Reset the request headers currently used by the browser."""
        self.headers.clear()
        self.headers.update({
            'Accept': 'text/html; */*',
            'User-Agent': self.user_agent})

    @property
    def response_headers(self):
        """Get the headers returned with the current page."""
        return self._assert_result_for('headers').headers

    @property
    def agent_string(self) -> Optional[str]:
        """Get the user agent string."""
        return self.headers.get('User-Agent')

    @agent_string.setter
    def agent_string(self, agent: str) -> None:
        """Set the user agent string to the given value."""
        self.headers['User-Agent'] = agent

    def show_forms(self) -> None:
        """Pretty-print all forms on the page.

        Include the global form (form elements outside <form> pairs)
        as forms[0] if present.
        """
        for n, form in enumerate(self.forms, 1):
            print_form(form, n)

    def show_links(self) -> None:
        """Pretty-print all links on the page."""
        info = log.info
        links = self.links
        if links:
            info('\nLinks (%d links total):\n', len(links))
            for n, link in enumerate(links, 1):
                info('\t%d. %s ==> %s', n, trunc(link.text, 40), link.url)
            info('')
        else:
            info('\n** no links **\n')

    def show_history(self) -> None:
        """Pretty-print the history of links visited."""
        info = log.info
        history = self._history
        if history:
            info('\nHistory (%d pages total):\n', len(history))
            for n, page in enumerate(history, 1):
                info('\t%d. %s', n, page.url)
            info('')
        else:
            info('\n** no history **\n')

    @property
    def links(self) -> List[Link]:
        """Return a list of all links on the page."""
        return self._assert_result_for('links').links

    @property
    def history(self) -> List[ResultWrapper]:
        """Return a list of all pages visited by the browser."""
        return self._history

    @property
    def forms(self) -> List[FormElement]:
        """Return a list of forms on the page.

        This includes the global form at index 0 if present.
        """
        return self._assert_result_for('forms').forms

    def form(self, name: Union[str, int] = 1) -> Optional[FormElement]:
        """Return the first form that matches the given form name."""
        return self._assert_result_for('form').form(name)

    def form_field(self, form: FormElement = None,
                   name_or_num: Union[str, int] = 1) -> FieldElement:
        """Return the control that matches the given field name.

        Must be a *unique* regex/exact string match, but the returned
        control can also be a CheckboxGroup or RadioGroup list.

        Raises a TwillException if no such field or multiple fields are found.
        """
        if form is None:
            form = self._form
            if form is None:
                raise TwillException("Must specify a form for the field")
        inputs = form.inputs
        found_multiple = False

        name = name_or_num if isinstance(name_or_num, str) else None

        if name:

            if name in form.fields:
                match_name = [c for c in inputs if c.name == name]
                if len(match_name) > 1:
                    if all(getattr(c, 'type', None) == 'checkbox'
                            for c in match_name):
                        return CheckboxGroup(
                            cast(List[InputElement], match_name))
                    if all(getattr(c, 'type', None) == 'radio'
                            for c in match_name):
                        return RadioGroup(cast(List[InputElement], match_name))
            else:
                match_name = None

            # test exact match to id
            match_id = [c for c in inputs if c.get('id') == name]
            if match_id:
                if unique_match(match_id):
                    return match_id[0]
                found_multiple = True

            # test exact match to name
            if match_name:
                if unique_match(match_name):
                    return match_name[0]
                found_multiple = True

        num = name_or_num if isinstance(name_or_num, int) else None
        if num is None and name and name.isdigit():
            try:
                num = int(name)
            except ValueError:
                pass

        # test field index
        if num is not None:
            try:
                return list(inputs)[num - 1]
            except IndexError:
                pass

        if name:

            # test regex match
            regex = re.compile(name)
            match_name = [c for c in inputs
                          if c.name and regex.search(c.name)]
            if match_name:
                if unique_match(match_name):
                    return match_name[0]
                found_multiple = True

            # test field values
            match_value = [c for c in inputs if c.value == name]
            if match_value:
                if len(match_value) == 1:
                    return match_value[0]
                found_multiple = True

        # error out
        if found_multiple:
            raise TwillException(f'multiple matches to "{name_or_num}"')
        raise TwillException(f'no field matches "{name_or_num}"')

    def add_form_file(self, field_name: str, fp: IO) -> None:
        self._form_files[field_name] = fp

    def clicked(self, form: FormElement, control: FieldElement) -> None:
        """Record a 'click' in a specific form."""
        if self._form != form:
            # construct a function to choose a particular form;
            # select_form can use this to pick out a precise form.
            self._form = form
            self.last_submit_button = None
        # record the last submit button clicked.
        if getattr(control, 'type', None) in ('submit', 'image'):
            self.last_submit_button = cast(InputElement, control)

    def submit(self, field_name: Optional[Union[str, int]] = None,
               form_name: Optional[Union[str, int]] = None) -> None:
        """Submit the last or specified form using the given field."""
        forms = self.forms
        if not forms:
            raise TwillException("There are no forms on this page.")

        ctl: Optional[InputElement] = None

        form = self._form if form_name is None else self.form(form_name)
        if form is None:
            if len(forms) > 1:
                raise TwillException(
                    "There is more than one form on this page;"
                    " therefore you must specify a form explicitly"
                    " or select one (use 'fv') before submitting.")
            form = forms[0]

        action = form.action or ''
        if '://' not in action:
            form.action = urljoin(self.url, action)

        # no field name?  see if we can use the last submit button clicked...
        if field_name is None:
            if form is not self._form or self.last_submit_button is None:
                # get first submit button in form.
                submits = [c for c in form.inputs
                           if getattr(c, 'type', None) in ('submit', 'image')]
                if submits:
                    ctl = cast(InputElement, submits[0])
            else:
                ctl = self.last_submit_button
        else:
            # field name given; find it
            ctl = cast(InputElement, self.form_field(form, field_name))

        # now set up the submission by building the request object that
        # will be sent in the form submission.
        if ctl is None:
            log.debug('Note: submit without using a submit button')
        else:
            log.info(
                "Note: submit is using submit button:"
                " name='%s', value='%s'", ctl.get('name'), ctl.value)

        # Add referer information.  This may require upgrading the
        # request object to have an 'add_unredirected_header' function.
        # @BRT: For now, the referrer is always the current page
        # @CTB: this seems like an issue for further work.
        # Note: We do not set Content-Type from form.attrib.get('enctype'),
        # since Requests does a much better job at setting the proper one.
        headers = {'Referer': self.url}

        payload = form.form_values()
        if ctl is not None:
            name = ctl.get('name')
            if name:
                payload.append((name, ctl.value or ''))
        encoded_payload = self._encode_payload(payload)

        # now actually GO
        if form.method == 'POST':
            if self._form_files:
                r = self._session.post(
                    form.action, data=encoded_payload, headers=headers,
                    files=self._form_files)
            else:
                r = self._session.post(
                    form.action, data=encoded_payload, headers=headers)
        else:
            r = self._session.get(
                form.action, params=encoded_payload, headers=headers)

        self._form = None
        self._form_files.clear()
        self.last_submit_button = None
        if self.result is not None:
            self._history.append(self.result)
        self.result = ResultWrapper(r)

    def cookies(self) -> RequestsCookieJar:
        """Get all cookies from the current session."""
        return self._session.cookies

    def save_cookies(self, filename: str) -> None:
        """Save cookies into the given file."""
        with open(filename, 'wb') as f:
            pickle.dump(self._session.cookies, f)

    def load_cookies(self, filename: str) -> None:
        """Load cookies from the given file."""
        with open(filename, 'rb') as f:
            self._session.cookies = pickle.load(f)

    def clear_cookies(self) -> None:
        """Delete all the cookies."""
        self._session.cookies.clear()

    def show_cookies(self) -> None:
        """Pretty-print all the cookies."""
        info = log.info
        cookies = self._session.cookies
        n = len(cookies)
        if n:
            log.info('\nThere are %d cookie(s) in the cookie jar.\n', n)
            for n, cookie in enumerate(cookies, 1):
                info('\t%d. %s', n, cookie)
            info('')
        else:
            log.info('\nThere are no cookies in the cookie jar.\n', n)

    def decode(self, value: Union[bytes, str]):
        """Decode a value using the current encoding."""
        if isinstance(value, bytes) and self.encoding:
            value = value.decode(self.encoding)
        return value

    def xpath(self, path: str) -> List[HtmlElement]:
        """Evaluate an xpath expression."""
        return self._assert_result_for('xpath').xpath(path)

    def _encode_payload(
            self, payload: Sequence[Tuple[str, Union[str, bytes]]]
            ) -> List[Tuple[str, Union[str, bytes]]]:
        """Encode a payload with the current encoding if not utf-8."""
        encoding = self.encoding
        if not encoding or encoding.lower() in ('utf8', 'utf-8'):
            return list(payload)
        return [(name, val if isinstance(val, bytes) else val.encode(encoding))
                for name, val in payload]

    @staticmethod
    def _get_meta_refresh(
            response: Response) -> Tuple[Optional[int], Optional[str]]:
        """Get meta refresh interval and url from a response."""
        try:
            tree = html_to_tree(response.text)
        except ValueError:
            # may happen when there is an XML encoding declaration
            tree = html_to_tree(response.content)
        try:
            content = tree.xpath(  # "refresh" is case insensitive
                "//meta[translate(@http-equiv,'REFSH','refsh')="
                "'refresh'][1]/@content")[0]
            interval, url = content.split(';', 1)
            interval = int(interval)
            if interval < 0:
                raise ValueError
            url = url.strip().strip('"').strip().strip("'").strip()
            url = url.split('=', 1)
            if url[0].strip().lower() != 'url':
                raise IndexError
            url = url[1].strip().strip('"').strip().strip("'").strip()
        except (IndexError, ValueError):
            interval = url = None
        else:
            if '://' not in url:  # relative URL, adapt
                url = urljoin(response.url, url)
        return interval, url

    _re_basic_auth = re.compile('Basic realm="(.*)"', re.I)

    def _journey(self, func_name, *args, **_kwargs):
        """Execute the function with the given name and arguments.

        The name should be one of 'open', 'reload', 'back', or 'follow_link'.
        This method then runs that function with the given arguments and turns
        the results into a nice friendly standard ResultWrapper object, which
        is stored as self.result.

        (Idea stolen from Python Browsing Probe (PBP).)
        """
        self._form = None
        self._form_files.clear()
        self.last_submit_button = None

        if func_name == 'open':
            url = args[0]

        elif func_name == 'follow_link':
            url = args[0]
            try:
                url = url.url
            except AttributeError:
                pass  # this is already a url
            if '://' not in url and self.url:
                url = urljoin(self.url, url)

        elif func_name == 'reload':
            url = self.url

        elif func_name == 'back':
            try:
                self.result = self._history.pop()
                return
            except IndexError:
                raise TwillException
        else:
            raise TwillException(f"Unknown function {func_name!r}")

        r = self._session.get(url, verify=self.verify)
        if r.status_code == 401:
            header = r.headers.get('WWW-Authenticate')
            realm = self._re_basic_auth.match(header)
            if realm:
                realm = realm.group(1)
                auth = self._auth.get((url, realm)) or self._auth.get(url)
                if auth:
                    r = self._session.get(url, auth=auth, verify=self.verify)

        # handle redirection via meta refresh (not handled in requests)
        refresh_interval = get_equiv_refresh_interval()
        if refresh_interval:
            visited = set()  # break circular refresh chains
            while True:
                interval, url = self._get_meta_refresh(r)
                if not url:
                    break
                if interval >= refresh_interval:
                    (log.info if self.show_refresh else log.debug)(
                        'Meta refresh interval too long: %d', interval)
                    break
                if url in visited:
                    log.warning('Circular meta refresh detected!')
                    break
                (log.info if self.show_refresh else log.debug)(
                    'Meta refresh to new URL: %s', url)
                r = self._session.get(url)
                visited.add(url)

        if func_name in ('follow_link', 'open'):
            # If we're really reloading and just didn't say so, don't store
            if self.result is not None and self.result.url != r.url:
                self._history.append(self.result)

        self.result = ResultWrapper(r)


browser = TwillBrowser()  # the global twill browser instance

_disable_insecure_request_warnings()  # should not warn for HTTP requests
