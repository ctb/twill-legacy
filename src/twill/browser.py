"""Implementation of the TwillBrowser."""

import pickle
import re
from contextlib import suppress
from http import HTTPStatus
from typing import (
    IO,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
    cast,
)
from urllib.parse import urljoin

from httpx import (
    BasicAuth,
    Client,
    ConnectError,
    Cookies,
    Headers,
    InvalidURL,
    Timeout,
)

from . import __version__, log
from .errors import TwillException
from .utils import (
    CheckboxGroup,
    FieldElement,
    FormElement,
    HtmlElement,
    InputElement,
    Link,
    RadioGroup,
    Response,
    ResultWrapper,
    UrlWithRealm,
    get_equiv_refresh_interval,
    html_to_tree,
    print_form,
    trunc,
    unique_match,
)

__all__ = ["browser"]


def _set_http_connection_debuglevel(level: int) -> None:
    """Set the debug level for the connection pool."""
    from http.client import HTTPConnection

    HTTPConnection.debuglevel = level


class TwillBrowser:
    """A simple, stateful browser."""

    user_agent = f"TwillBrowser/{__version__}"

    def __init__(
        self,
        base_url: str = "",
        app: Optional[Callable[..., Any]] = None,
        follow_redirects: bool = True,  # noqa: FBT001, FBT002
        verify: Union[bool, str] = False,  # noqa: FBT002
        timeout: Union[None, float, Timeout] = 10,
    ) -> None:
        """Initialize the twill browser.

        Optionally, you can send requests to a WSGI app instead over the
        network, and you can specify a base URL for all requests.
        The "follow_redirects" parameter has the default value True so that
        the browser by default automatically follows all redirects.
        The "verify" argument can be used to specify whether or how server
        certificates shall be verified; this can also be a CA bundle path.
        In the "timeout" argument you can specify the timeout in seconds.
        """
        self.reset(
            app=app,
            base_url=base_url,
            follow_redirects=follow_redirects,
            verify=verify,
            timeout=timeout,
        )

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

    def close(self) -> None:
        try:
            client = self._client
        except AttributeError:
            pass
        else:
            client.close()
            del self.result
            del self.last_submit_button
            del self.first_error
            del self._client
            del self._form
            del self._form_files
            del self._auth
            del self._post_load_hooks
            del self._history

    def reset(
        self,
        base_url: str = "",
        app: Optional[Callable[..., Any]] = None,
        follow_redirects: bool = True,  # noqa: FBT001, FBT002
        verify: Union[bool, str] = False,  # noqa: FBT002
        timeout: Union[None, float, Timeout] = 10,
    ) -> None:
        """Reset the browser.

        Optionally, you can send requests to a WSGI app instead over the
        network, and you can specify a base URL for all requests.
        The "follow_redirects" parameter has the default value True so that
        the browser by default automatically follows all redirects.
        The "verify" argument can be used to specify whether or how server
        certificates shall be verified; this can also be a CA bundle path.
        In the "timeout" argument you can specify the timeout in seconds.
        """
        self.close()

        self.result: Optional[ResultWrapper] = None
        self.last_submit_button: Optional[InputElement] = None
        self.first_error: Optional[str] = None

        # whether meta refresh will be displayed
        self.show_refresh = False

        # debug level to be used for the connection pool
        self._debug_level = 0

        # Client stores cookies
        self._client = Client(
            app=app,
            base_url=base_url,
            follow_redirects=follow_redirects,
            verify=verify,
            timeout=timeout,
        )

        # A lxml FormElement, None until a form is selected
        # replaces self._browser.form from mechanize
        self._form: Optional[FormElement] = None
        self._form_files: Dict[str, IO] = {}

        # A dict of BasicAuth from httpx, keyed off URL
        self._auth: Dict[UrlWithRealm, BasicAuth] = {}

        # callables to be called after each page load.
        self._post_load_hooks: List[Callable] = []

        self._history: List[ResultWrapper] = []

        # set default headers
        self.reset_headers()

    @property
    def creds(self) -> Dict[UrlWithRealm, BasicAuth]:
        """Get the credentials for basic authentication."""
        return self._auth

    def add_creds(self, url: UrlWithRealm, user: str, password: str) -> None:
        """Set the credentials for basic authentication."""
        self._auth[url] = BasicAuth(user, password)

    def go(self, url: str) -> None:
        """Visit given URL."""
        try_urls: List[str] = []
        if "://" in url:
            try_urls.append(url)
        else:  # URL does not have a schema
            # if this is a relative URL, then assume that we want to tack it
            # onto the end of the current URL
            current_url = self.url
            if current_url:
                try_urls.append(urljoin(current_url, url))
            # if this is an absolute URL, it may be just missing the 'http://'
            # at the beginning, try fixing that (mimic browser behavior)
            if not url.startswith((".", "/", "?")):
                # noinspection HttpUrlsUsage
                try_urls.append(f"http://{url}")
                try_urls.append(f"https://{url}")
        for try_url in try_urls:
            try:
                self._journey("open", try_url)
            except (
                OSError,
                ConnectError,
                InvalidURL,
                UnicodeError,
            ) as error:
                log.info("cannot go to '%s': %s", try_url, error)
            else:
                break
        else:
            raise TwillException(f"cannot go to '{url}'")
        log.info("==> at %s", self.url)

    def reload(self) -> None:
        """Tell the browser to reload the current page."""
        self._journey("reload")
        log.info("==> reloaded")

    def back(self) -> None:
        """Return to previous page, if possible."""
        try:
            self._journey("back")
            log.info("==> back to %s", self.url)
        except TwillException:
            log.warning("==> back at empty page")

    @property
    def code(self) -> int:
        """Get the HTTP status code received for the current page."""
        return self._assert_result_for("status code").http_code

    @property
    def encoding(self) -> Optional[str]:
        """Get the encoding used by the server for the current page."""
        return None if self.result is None else self.result.encoding

    @property
    def html(self) -> str:
        """Get the HTML for the current page."""
        return self._assert_result_for("HTML").text

    @property
    def dump(self) -> bytes:
        """Get the binary content of the current page."""
        return self._assert_result_for("content dump").content

    @property
    def title(self) -> Optional[str]:
        return self._assert_result_for("title").title

    @property
    def url(self) -> Optional[str]:
        """Get the URL of the current page."""
        return self.result.url if self.result else None

    def find_link(self, pattern: str) -> Optional[Link]:
        """Find the first link matching the given regular expression pattern.

        The pattern is searched in the URL and in the link text.
        """
        return self._assert_result_for("links").find_link(pattern)

    def find_links(self, pattern: str) -> Optional[List[Link]]:
        """Find all links matching the given regular expression pattern.

        The pattern is searched in the URL and in the link text.
        """
        return self._assert_result_for("links").find_links(pattern)

    def follow_link(self, link: Union[str, Link]) -> None:
        """Follow the given link."""
        self._journey("follow_link", link)
        log.info("==> at %s", self.url)

    @property
    def headers(self) -> Headers:
        """Return the request headers currently used by the browser."""
        return self._client.headers

    def reset_headers(self) -> None:
        """Reset the request headers currently used by the browser."""
        self.headers.clear()
        self.headers.update(
            {"Accept": "text/html; */*", "User-Agent": self.user_agent}
        )

    @property
    def response_headers(self) -> Headers:
        """Get the headers returned with the current page."""
        return self._assert_result_for("headers").headers

    @property
    def agent_string(self) -> Optional[str]:
        """Get the user agent string."""
        agent = self.headers.get("User-Agent")
        if isinstance(agent, bytes):
            agent = agent.decode()
        return agent

    @agent_string.setter
    def agent_string(self, agent: str) -> None:
        """Set the user agent string to the given value."""
        self.headers["User-Agent"] = agent

    @property
    def timeout(self) -> Union[None, float, Timeout]:
        """Get the request timeout in seconds."""
        timeout = self._client.timeout
        if timeout.connect == timeout.read == timeout.write == timeout.pool:
            return timeout.connect or None
        return timeout

    @timeout.setter
    def timeout(self, timeout: Union[None, float, Timeout]) -> None:
        """Set the request timeout in seconds."""
        self._client.timeout = timeout  # type: ignore[assignment]

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
            info("\nLinks (%d links total):\n", len(links))
            for n, link in enumerate(links, 1):
                info("\t%d. %s ==> %s", n, trunc(link.text, 40), link.url)
            info("")
        else:
            info("\n** no links **\n")

    def show_history(self) -> None:
        """Pretty-print the history of links visited."""
        info = log.info
        history = self._history
        if history:
            info("\nHistory (%d pages total):\n", len(history))
            for n, page in enumerate(history, 1):
                info("\t%d. %s", n, page.url)
            info("")
        else:
            info("\n** no history **\n")

    @property
    def links(self) -> List[Link]:
        """Return a list of all links on the page."""
        return self._assert_result_for("links").links

    @property
    def history(self) -> List[ResultWrapper]:
        """Return a list of all pages visited by the browser."""
        return self._history

    @property
    def forms(self) -> List[FormElement]:
        """Return a list of forms on the page.

        This includes the global form at index 0 if present.
        """
        return self._assert_result_for("forms").forms

    def form(self, name: Union[str, int] = 1) -> Optional[FormElement]:
        """Return the first form that matches the given form name."""
        return self._assert_result_for("form").form(name)

    def form_field(
        self,
        form: Optional[FormElement] = None,
        name_or_num: Union[str, int] = 1,
    ) -> FieldElement:
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
                    if all(
                        getattr(c, "type", None) == "checkbox"
                        for c in match_name
                    ):
                        return CheckboxGroup(
                            cast(List[InputElement], match_name)
                        )
                    if all(
                        getattr(c, "type", None) == "radio" for c in match_name
                    ):
                        return RadioGroup(cast(List[InputElement], match_name))
            else:
                match_name = None

            # test exact match to id
            match_id = [c for c in inputs if c.get("id") == name]
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
            with suppress(ValueError):
                num = int(name)

        # test field index
        if num is not None:
            with suppress(IndexError):
                return list(inputs)[num - 1]

        if name:
            # test regex match
            regex = re.compile(name)
            match_name = [c for c in inputs if c.name and regex.search(c.name)]
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
        if getattr(control, "type", None) in ("submit", "image"):
            self.last_submit_button = cast(InputElement, control)

    def submit(
        self,
        field_name: Optional[Union[str, int]] = None,
        form_name: Optional[Union[str, int]] = None,
    ) -> None:
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
                    " or select one (use 'fv') before submitting."
                )
            form = forms[0]

        action = form.action or ""
        if "://" not in action:
            form.action = urljoin(self.url, action)

        # no field name?  see if we can use the last submit button clicked...
        if field_name is None:
            if form is not self._form or self.last_submit_button is None:
                # get first submit button in form.
                submits = [
                    c
                    for c in form.inputs
                    if getattr(c, "type", None) in ("submit", "image")
                ]
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
            log.debug("Note: submit without using a submit button")
        else:
            log.info(
                "Note: submit is using submit button:"
                " name='%s', value='%s'",
                ctl.get("name"),
                ctl.value,
            )

        # Add referer information.  This may require upgrading the
        # request object to have an 'add_unredirected_header' function.
        # @BRT: For now, the referrer is always the current page
        # @CTB: this seems like an issue for further work.
        # Note: We do not set Content-Type from form.attrib.get('enctype'),
        # since httpx does a much better job at setting the proper one.
        headers = {"Referer": self.url}

        payload = form.form_values()
        if ctl is not None:
            name = ctl.get("name")
            if name:
                payload.append((name, ctl.value or ""))
        payload_dict = self._make_payload_dict(payload)

        # now actually GO
        if form.method == "POST":
            if self._form_files:
                log.debug("Submitting files: %r", self._form_files)
                result = self._client.post(
                    form.action,
                    data=payload_dict,
                    headers=headers,
                    files=self._form_files,
                )
            else:
                result = self._client.post(
                    form.action, data=payload_dict, headers=headers
                )
        else:
            result = self._client.get(
                form.action, params=payload_dict, headers=headers
            )

        self._form = None
        self._form_files.clear()
        self.last_submit_button = None
        if self.result is not None:
            self._history.append(self.result)
        self.result = ResultWrapper(result)

    def cookies(self) -> Cookies:
        """Get all cookies from the current client session."""
        return self._client.cookies

    def save_cookies(self, filename: str) -> None:
        """Save cookies into the given file."""
        with open(filename, "wb") as f:
            pickle.dump(dict(self._client.cookies), f)

    def load_cookies(self, filename: str) -> None:
        """Load cookies from the given file."""
        with open(filename, "rb") as f:
            self._client.cookies = pickle.load(f)  # noqa: S301

    def clear_cookies(self) -> None:
        """Delete all the cookies."""
        self._client.cookies.clear()

    def show_cookies(self) -> None:
        """Pretty-print all the cookies."""
        info = log.info
        cookies = self._client.cookies
        n = len(cookies)
        if n:
            log.info("\nThere are %d cookie(s) in the cookie jar.\n", n)
            for n, cookie in enumerate(cookies, 1):
                info("\t%d. %s", n, cookie)
            info("")
        else:
            log.info("\nThere are no cookies in the cookie jar.\n", n)

    def decode(self, value: Union[bytes, str]) -> str:
        """Decode a value using the current encoding."""
        if isinstance(value, bytes):
            value = value.decode(self.encoding or "utf-8")
        return value

    def xpath(self, path: str) -> List[HtmlElement]:
        """Evaluate an xpath expression."""
        return self._assert_result_for("xpath").xpath(path)

    def _make_payload_dict(
        self,
        payload: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Dict[str, Union[str, List[Union[str]]]]:
        """Prepare a payload by decoding bytes and converting to a dict."""
        encoding = self.encoding or "utf-8"
        data: Dict[str, Union[str, List[Union[str]]]] = {}
        for key, value in payload:
            new_value = (
                value if isinstance(value, str) else value.decode(encoding)
            )
            try:
                existing_value = data[key]
            except KeyError:
                data[key] = new_value
            else:
                if isinstance(existing_value, list):
                    existing_value.append(new_value)
                else:
                    data[key] = [existing_value, new_value]
        return data

    @staticmethod
    def _get_meta_refresh(
        response: Response,
    ) -> Tuple[Optional[int], Optional[str]]:
        """Get meta refresh interval and url from a response."""
        try:
            tree = html_to_tree(response.text)
        except ValueError:
            # may happen when there is an XML encoding declaration
            tree = html_to_tree(response.content)
        try:
            content = tree.xpath(  # "refresh" is case-insensitive
                "//meta[translate(@http-equiv,'REFSH','refsh')="
                "'refresh'][1]/@content"
            )[0]
            interval, url = content.split(";", 1)
            interval = int(interval)
            if interval < 0:
                raise ValueError
            url = url.strip().strip('"').strip().strip("'").strip()
            url = url.split("=", 1)
            if url[0].strip().lower() != "url":
                raise IndexError
            url = url[1].strip().strip('"').strip().strip("'").strip()
        except (IndexError, ValueError):
            interval = url = None
        else:
            if "://" not in url:  # relative URL, adapt
                url = str(response.url.join(url))
        return interval, url

    _re_basic_auth = re.compile('Basic realm="(.*)"', re.I)

    def _journey(self, func_name: str, *args, **_kwargs) -> None:
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

        if func_name == "open":
            url = args[0]

        elif func_name == "follow_link":
            url = args[0]
            with suppress(AttributeError):  # may be already a url
                url = url.url
            if "://" not in url and self.url:
                url = urljoin(self.url, url)

        elif func_name == "reload":
            url = self.url

        elif func_name == "back":
            try:
                self.result = self._history.pop()
            except IndexError as error:
                raise TwillException("Cannot go further back") from error
            return
        else:
            raise TwillException(f"Unknown function {func_name!r}")

        result = self._client.get(url)
        if result.status_code == HTTPStatus.UNAUTHORIZED:
            header = result.headers.get("WWW-Authenticate")
            match_realm = self._re_basic_auth.match(header)
            if match_realm:
                realm = match_realm.group(1)
                auth = self._auth.get((url, realm)) or self._auth.get(url)
                if auth:
                    result = self._client.get(url, auth=auth)

        # handle redirection via meta refresh (not handled in requests)
        refresh_interval = get_equiv_refresh_interval()
        if refresh_interval:
            visited = set()  # break circular refresh chains
            while True:
                interval, url = self._get_meta_refresh(result)
                if not url:
                    break
                if interval >= refresh_interval:
                    (log.info if self.show_refresh else log.debug)(
                        "Meta refresh interval too long: %d", interval
                    )
                    break
                if url in visited:
                    log.warning("Circular meta refresh detected!")
                    break
                (log.info if self.show_refresh else log.debug)(
                    "Meta refresh to new URL: %s", url
                )
                result = self._client.get(url)
                visited.add(url)

        if func_name in ("follow_link", "open") and (
            # if we're really reloading and just didn't say so, don't store
            self.result is not None
            and self.result.url != result.url
        ):
            self._history.append(self.result)

        self.result = ResultWrapper(result)


browser = TwillBrowser()  # the global twill browser instance
