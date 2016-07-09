"""This module implements the TwillBrowser."""

import pickle
import re

from urlparse import urljoin

import requests
from lxml import html
from requests.exceptions import InvalidSchema, ConnectionError
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from . import log, __version__
from .utils import (
    print_form, trunc, unique_match, ResultWrapper, _follow_equiv_refresh)
from .errors import TwillException

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class TwillBrowser(object):
    """A simple, stateful browser"""

    user_agent = 'TwillBrowser/%s' % (__version__,)

    def __init__(self):
        # create special link/forms parsing code to run tidy on HTML first.
        self.result = None
        self.last_submit_button = None

        # whether the SSL cert will be verified, or can be a ca bundle path
        self.verify = False

        # Session stores cookies
        self._session = requests.Session()

        # An lxml FormElement, none until a form is selected
        # replaces self._browser.form from mechanize
        self._form = None
        self._formFiles = {}

        # A dict of HTTPBasicAuth from requests, keyed off URL
        self._auth = {}

        # callables to be called after each page load.
        self._post_load_hooks = []

        self._history = []

        # set default headers
        self.reset_headers()

    def reset(self):
        """Reset the browser"""
        self.__init__()

    @property
    def creds(self):
        """Get the credentials for basic authentication."""
        return self._auth

    @creds.setter
    def creds(self, creds):
        """Set the credentials for basic authentication."""
        self._auth[creds[0]] = requests.auth.HTTPBasicAuth(*creds[1])

    def go(self, url):
        """Visit given URL."""
        try_urls = []
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
                try_urls.append('http://%s' % (url,))
                try_urls.append('https://%s' % (url,))
        for try_url in try_urls:
            try:
                self._journey('open', try_url)
            except (IOError, ConnectionError, InvalidSchema) as error:
                log.info("cannot go to '%s': %s" % (try_url, error))
            else:
                break
        else:
            raise TwillException("cannot go to '%s'" % (url,))
        log.info('==> at %s', self.url)

    def reload(self):
        """Tell the browser to reload the current page."""
        self._journey('reload')
        log.info('==> reloaded')

    def back(self):
        """Return to previous page, if possible."""
        try:
            self._journey('back')
            log.info('==> back to %s', self.url)
        except TwillException:
            log.warning('==> back at empty page')

    @property
    def code(self):
        """Get the HTTP status code received for the current page."""
        return self.result.http_code if self.result else None

    @property
    def html(self):
        """Get the HTML for the current page."""
        return self.result.text if self.result else None

    @property
    def dump(self):
        """Get the binary content of the current page."""
        return self.result.content if self.result else None

    @property
    def title(self):
        if self.result is None:
            raise TwillException("Error: Getting title with no page")
        return self.result.title

    @property
    def url(self):
        """Get the URL of the current page."""
        return self.result.url if self.result else None

    def find_link(self, pattern):
        """Find the first link matching the given pattern.

        The pattern is searched in the URL, link text, or name.
        """
        return self.result.find_link(pattern) if self.result else None

    def follow_link(self, link):
        """Follow the given link."""
        self._journey('follow_link', link)
        log.info('==> at %s', self.url)

    @property
    def headers(self):
        return self._session.headers

    def reset_headers(self):
        self.headers.clear()
        self.headers.update({
            'Accept': 'text/html; */*',
            'User-Agent': self.user_agent})

    @property
    def agent_string(self):
        """Get the agent string."""
        return self.headers.get('User-Agent')

    @agent_string.setter
    def agent_string(self, agent):
        """Set the agent string to the given value."""
        self.headers['User-agent'] = agent

    def showforms(self):
        """Pretty-print all of the forms.

        Include the global form (form elements outside of <form> pairs)
        as forms[0] if present.
        """
        for n, form in enumerate(self.forms):
            print_form(form, n)

    def showlinks(self):
        """Pretty-print all of the links."""
        info = log.info
        links = self.links
        if links:
            info('\nLinks (%d links total):\n', len(links))
            for n, link in enumerate(links):
                info('\t%d. %s ==> %s', n + 1, trunc(link.text, 40), link.url)
            info('')
        else:
            info('\n** no links **\n')

    def showhistory(self):
        """Pretty-print the history of links visited."""
        info = log.info
        history = self._history
        if history:
            info('\nHistory (%d pages total):\n', len(history))
            for n, page in enumerate(history):
                info('\t%d. %s', n + 1, page.url)
            info('')
        else:
            info('\n** no history **\n')

    @property
    def links(self):
        """Return a list of all of the links on the page."""
        return [] if self.result is None else self.result.links

    @property
    def forms(self):
        """Return a list of all of the forms.

        Include the global form at index 0 if present.
        """
        return [] if self.result is None else self.result.forms

    def form(self, formname=1):
        """Return the first form that matches the given form name."""
        return None if self.result is None else self.result.form(formname)

    def form_field(self, form, fieldname=1):
        """Return the control that matches the given field name.

        Must be a *unique* regex/exact string match.
        """
        inputs = form.inputs

        if fieldname in form.fields:
            controls = [f for f in inputs
                        if f.get('name') == fieldname and
                        hasattr(f, 'type') and f.type == 'checkbox']
            if len(controls) > 1:
                return html.CheckboxGroup(controls)

        found = None
        found_multiple = False

        if not isinstance(fieldname, int):

            # test exact match to id
            matches = [c for c in inputs if c.get('id') == fieldname]
            if matches:
                if unique_match(matches):
                    found = matches[0]
                else:
                    found_multiple = True

            if found is None:
                # test exact match to name
                matches = [c for c in inputs if c.name == fieldname]
                if matches:
                    if unique_match(matches):
                        found = matches[0]
                    else:
                        found_multiple = True

        # test field index
        if found is None:
            if fieldname == '3':
                pass
            try:
                found = list(inputs)[int(fieldname) - 1]
            except (IndexError, ValueError):
                pass

        if not isinstance(fieldname, int):

            if found is None:
                # test regex match
                regex = re.compile(fieldname)
                matches = [c for c in inputs
                           if c.name and regex.search(c.name)]
                if matches:
                    if unique_match(matches):
                        found = matches[0]
                    else:
                        found_multiple = True

            if found is None:
                # test field values
                matches = [c for c in inputs if c.value == fieldname]
                if matches:
                    if len(matches) == 1:
                        found = matches[0]
                    else:
                        found_multiple = True

        # error out?
        if found is None:
            if found_multiple:
                raise TwillException('multiple matches to "%s"' % (fieldname,))
            raise TwillException('no field matches "%s"' % (fieldname,))

        return found

    def clicked(self, form, control):
        """Record a 'click' in a specific form."""
        if self._form != form:
            # construct a function to choose a particular form;
            # select_form can use this to pick out a precise form.
            self._form = form
            self.last_submit_button = None
        # record the last submit button clicked.
        if hasattr(control, 'type') and control.type in ('submit', 'image'):
            self.last_submit_button = control

    def submit(self, fieldname=None):
        """Submit the currently clicked form using the given field."""
        if fieldname is not None:
            fieldname = str(fieldname)

        forms = self.forms
        if not forms:
            raise TwillException("no forms on this page!")
        
        ctl = None

        form = self._form
        if form is None:
            if len(forms) == 1:
                form = forms[0]
            else:
                raise TwillException(
                    "more than one form;"
                    " you must select one (use 'fv') before submitting")

        action = form.action or ''
        if '://' not in action:
             form.action = urljoin(self.url, action)

        # no fieldname?  see if we can use the last submit button clicked...
        if fieldname is None:
            if self.last_submit_button is None:
                # get first submit button in form.
                submits = [c for c in form.inputs
                           if hasattr(c, 'type') and
                           c.type in ('submit', 'image')]
                if submits:
                    ctl = submits[0]
            else:
                ctl = self.last_submit_button
        else:
            # fieldname given; find it.
            ctl = self.form_field(form, fieldname)

        # now set up the submission by building the request object that
        # will be sent in the form submission.
        if ctl is None:
            log.debug('Note: submit without using a submit button')
        else:
            log.info(
                "Note: submit is using submit button:"
                " name='%s', value='%s'", ctl.get('name'), ctl.value)
            if hasattr(ctl, 'type') and ctl.type == 'image':
                pass

        # add referer information.  this may require upgrading the
        # request object to have an 'add_unredirected_header' function.
        # @BRT: For now, the referrer is always the current page
        # @CTB this seems like an issue for further work.
        headers = {'referer': self.url}

        # now actually GO.
        payload = list(form.form_values())
        if ctl is not None and ctl.get('name') is not None:
            payload.append((ctl.get('name'), ctl.value))
        if form.method == 'POST':
            if self._formFiles:
                r = self._session.post(
                    form.action,
                    data=payload, files=self._formFiles, headers=headers)
            else:
                r = self._session.post(
                    form.action,
                    data=payload, headers=headers)
        else:
            r = self._session.get(form.action, data=payload, headers=headers)

        self._formFiles.clear()
        self._history.append(self.result)
        self.result = ResultWrapper(r)

    def save_cookies(self, filename):
        """Save cookies into the given file."""
        with open(filename, 'wb') as f:
            pickle.dump(self._session.cookies, f)

    def load_cookies(self, filename):
        """Load cookies from the given file."""
        with open(filename, 'rb') as f:
            self._session.cookies = pickle.load(f)

    def clear_cookies(self):
        """Delete all of the cookies."""
        self._session.cookies.clear()

    def show_cookies(self):
        """Pretty-print all of the cookies."""
        info = log.info
        cookies = self._session.cookies
        n = len(cookies)
        if n:
            log.info('\nThere are %d cookie(s) in the cookie jar.\n', n)
            for n, cookie in enumerate(cookies):
                info('\t%d. %s', n + 1, cookie)
            info('')
        else:
            log.info('\nThere are no cookies in the cookie jar.\n', n)

    def _test_for_meta_redirections(self, r):
        """Checks a document for meta redirection."""
        # @BRT: Added to test for meta redirection
        # Shamelessly stolen from
        # http://stackoverflow.com/questions/2318446/how-to-follow-meta-refreshes-in-python
        # Took some modification to get it working, though.
        # Original post notes that this doesn't check circular redirect.
        # Is this something we're concerned with?
        html_tree = html.fromstring(r.text)
        attr = html_tree.xpath(
            "//meta[translate(@http-equiv, 'REFSH', 'refsh')"
            " = 'refresh']/@content")
        if attr:
            wait, text = attr[0].split(';')
            # @BRT: Strip surrounding quotes and ws; less brute force method?
            # Other chars that need to be dealt with?
            text = text.strip().strip('\'"')
            if text.lower().startswith("url="):
                url = text[4:]
                if not url.startswith('http'):
                    # Relative URL, adapt
                    url = urljoin(r.url, url)
                    return True, url
        return False, None

    def _follow_redirections(self, r, s):
        """Follows a meta refresh redirections if it exists.

        Note: This is a recursive function.
        """
        # @BRT: Added to test for meta redirection
        # Shamelessly stolen from the same link as _test_for_meta_redirections
        redirected, url = self._test_for_meta_redirections(r)
        if redirected:
            r = self._follow_redirections(s.get(url), s)
        return r

    _re_basic_auth = re.compile('Basic realm="(.*)"', re.I)

    def _journey(self, func_name, *args, **kwargs):
        """Execute the function with the given name and arguments.

        The name should be one of 'open', 'reload', 'back', or 'follow_link'.
        This method then runs that function with the given arguments and turns
        the results into a nice friendly standard ResultWrapper object, which
        is stored as self.result.

        (Idea stolen from Python Browsing Probe (PBP).)
        """
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

        r = self._session.get(url, verify=self.verify)
        if r.status_code == 401:
            header = r.headers.get('WWW-Authenticate')
            realm = self._re_basic_auth.match(header)
            if realm:
                realm = realm.group(1)
                auth = self._auth.get((url, realm)) or self._auth.get(url)
                if auth:
                    r = self._session.get(url, auth=auth, verify=self.verify)

        if _follow_equiv_refresh():
            r = self._follow_redirections(r, self._session)

        if func_name in ('follow_link', 'open'):
            # If we're really reloading and just didn't say so, don't store
            if self.result is not None and self.result.url != r.url:
                self._history.append(self.result)

        self.result = ResultWrapper(r)


browser = TwillBrowser()  # the global twill browser instance
