"""
Implements TwillBrowser
"""

OUT=None

# Python imports
import re

# Dependencies
import requests
import lxml

# Will need at least some of these
from utils import print_form, ConfigurableParsingFactory, \
     ResultWrapper, unique_match, HistoryStack
from errors import TwillException

class TwillBrowser(object):
    """A simple, stateful browser"""
    def __init__(self):
        #
        # create special link/forms parsing code to run tidy on HTML first.
        #
        
        # --BRT-- Incomplete

        factory = ConfigurableParsingFactory()

        self.result = None
        self.last_submit_button = None

        # callables to be called after each page load.
        self._post_load_hooks = []

        ## Placeholder
        self._browser = None
        ## Quick fix
        self.history = []

    def _set_creds(self, creds):
        # --BRT-- Incomplete
        return

    def _get_creds(self):
        # --BRT-- Incomplete
        return

    def go(self, url):
        """
        Visit given URL.
        """
        # --BRT-- Incomplete

        try_urls = [url, ]

        # if this is an absolute URL that is just missing the 'http://' at
        # the beginning, try fixing that.
        
        if url.find('://') == -1:
            full_url = 'http://%s' % (url,)  # mimic browser behavior
            try_urls.append(full_url)

        # if this is a '?' URL, then assume that we want to tack it onto
        # the end of the current URL.

        if url.startswith('?'):
            current_url = self.get_url()
            current_url = current_url.split('?')[0]
            try_urls = [ current_url + url, ]

        success = False

        for u in try_urls:
            try:
                self._journey('open', u)
                success = True
                break
            except IOError:             # @CTB test this!
                pass

        if success:
            print>>OUT, '==> at', self.get_url()
        else:
            # Modified to use TwillException in place of BrowserStateError
            raise TwillException("cannot go to '%s'" % (url,))

    def reload(self):
        """
        Tell the browser to reload the current page.
        """
        self._journey('reload')
        print>>OUT, '==> reloaded'

    def back(self):
        """
        Return to previous page, if possible.
        """
        # --BRT-- Incomplete
        # Modified to use TwillException in place of BrowserStateError
        try:
            self._journey('back')
            print>>OUT, '==> back to', self.get_url()
        except TwillException:
            print>>OUT, '==> back at empty page.'

    def get_code(self):
        """
        Get the HTTP status code received for the current page.
        """
        if self.result:
            return self.result.get_http_code()
        return None

    def get_html(self):
        """
        Get the HTML for the current page.
        """
        if self.result:
            return self.result.get_page()
        return None

    def get_title(self):
        # --BRT-- Incomplete
        return

    def get_url(self):
        """
        Get the URL of the current page.
        """
        if self.result:
            return self.result.get_url()
        return None

    def find_link(self, pattern):
        """
        Find the first link with a URL, link text, or name matching the
        given pattern.
        """
        # --BRT-- Incomplete
        return None

    def follow_link(self, link):
        """
        Follow the given link.
        """
        self._journey('follow_link', link)
        print>>OUT, '==> at', self.get_url()

    def set_agent_string(self, agent):
        """
        Set the agent string to the given value.
        """
        # --BRT-- Incomplete
        return

    def showforms(self):
        """
        Pretty-print all of the forms.  Include the global form (form
        elements outside of <form> pairs) as forms[0] iff present.
        """
        # --BRT-- Incomplete
        return

    def showlinks(self):
        """
        Pretty-print all of the links.
        """
        # --BRT-- Incomplete
        return ''

    def showhistory(self):
        """
        Pretty-print the history of links visited.
        """
        # --BRT-- Incomplete
        return

    def get_all_forms(self):
        """
        Return a list of all of the forms, with global_form at index 0
        iff present.
        """
        # --BRT-- Incomplete
        return

    def get_form(self, formname):
        """
        Return the first form that matches 'formname'.
        """
        # --BRT-- Incomplete
        return

    def get_form_field(self, form, fieldname):
        """
        Return the control that matches 'fieldname'.  Must be
        a *unique* regexp/exact string match.
        """
        # --BRT-- Incomplete
        return

    def clicked(self, form, control):
        """
        Record a 'click' in a specific form.
        """
        # --BRT-- Incomplete
        return

    def submit(self, fieldname=None):
        """
        Submit the currently clicked form using the given field.
        """
        # --BRT-- Incomplete
        return

    def save_cookies(self, filename):
        """
        Save cookies into the given file.
        """
        # --BRT-- Incomplete
        return

    def load_cookies(self, filename):
        """
        Load cookies from the given file.
        """
        # --BRT-- Incomplete
        return

    def clear_cookies(self):
        """
        Delete all of the cookies.
        """
        # --BRT-- Incomplete

    def show_cookies(self):
        """
        Pretty-print all of the cookies.
        """
        # --BRT-- Incomplete
        return

    def _journey(self, func_name, *args, **kwargs):
        """
        'func_name' should be one of 'open', 'reload', 'back', or 'follow_link'.

        journey then runs that function with the given arguments and turns
        the results into a nice friendly standard ResultWrapper object, which
        is stored as 'self.result'.

        All exceptions other than HTTPError are unhandled.
        
        (Idea stolen straight from PBP.)
        """
        # --BRT-- Incomplete
        self.last_submit_button = None

        if func_name == 'open':
            r = requests.get(*args)
            url = args[0] # r.get_url()
            self.result = ResultWrapper(r.status_code, url, r.text)
            self.history.append(url)

        elif func_name == 'follow_link':
            r = requests.get(*args)
            # url = r.get_url()
            url = args[0]
            self.result = ResultWrapper(r.status_code, url, r.text)
            self.history.append(self.result.get_url())

        elif func_name == 'reload':
            r = requests.get(self.history[-1])
            url = self.result.get_url()
            self.result = ResultWrapper(r.status_code, url, r.text)

        elif func_name == 'back':
            try:
                url = self.history.pop()
                r = requests.get(self.history.pop())
                self.result = ResultWrapper(r.status_code, url, r.text)
            except IndexError:
                pass

        else:
            self.result = None
