"""
Implements TwillBrowser
"""

OUT=None

# Python imports
import re

# Dependencies
import requests
from lxml import etree, html, cssselect

# Will need at least some of these
# from utils import print_form, ConfigurableParsingFactory, \
#     ResultWrapper, unique_match
from utils import print_form, ResultWrapper, unique_match
from errors import TwillException

class TwillBrowser(object):
    """A simple, stateful browser"""
    def __init__(self):
        #
        # create special link/forms parsing code to run tidy on HTML first.
        #

        # --BRT-- This is mechanize. Remove it? Or rewrite it?
        #factory = ConfigurableParsingFactory()

        self.result = None
        self.last_submit_button = None

        # --BRT-- I think this will handle cookies
        self._session = requests.Session()

        # --BRT-- Headers, this will handle user-agent
        self._headers = dict([("Accept", "text/html; */*")])

        # --BRT-- Creds... just an HTTPBasicAuth from requests, 
        # --BRT-- None until creds added
        self._auth = None

        # callables to be called after each page load.
        self._post_load_hooks = []

        ## Quick fix
        self._history = []

    def _set_creds(self, creds):
        self._auth = requests.auth.HTTPBasicAuth(creds)

    def _get_creds(self):
        return self._auth

    def go(self, url):
        """
        Visit given URL.
        """
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
        # --BRT-- Possibly broken? Seems to work better when else is commented
        # --BRT-- May be related to other not-yet-implemented functions
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
        if self.result:
            doc = html.fromstring(self.result.get_page())
            selector = cssselect.CSSSelector("title")
            return selector(doc)[0].text
        else:
            return ''

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
        doc = html.fromstring(self.result.get_page())
        selector = cssselect.CSSSelector("a")
        links = [(l.text or '', l.get("href")) for l in selector(doc)]
        for link in links:
            if re.search(pattern, link[0]) or re.search(pattern, link[1]):
                return link[1]
        return ''

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
        self._headers['User-agent'] = agent
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
        doc = html.fromstring(self.result.get_page())
        selector = cssselect.CSSSelector("a")
        links = iter([(l.text, l.get("href")) for l in selector(doc)])
        for n,link in enumerate(links):
            print>>OUT, "%d. %s ==> %s" % (n, link[0], link[1],)
        print>>OUT, ''

    def showhistory(self):
        """
        Pretty-print the history of links visited.
        """
        print>>OUT, ''
        print>>OUT, 'History: (%d pages total) ' % (len(self._history))
        n = 1
        for page in self._history:
            if page.get_http_code() == 200:
            # --BRT-- Not sure how to implement the below comment 
            # --BRT-- as back doesn't do that yet
            # --BRT-- this might be what it's after?

            # only print those that back() will go
                print>>OUT, "\t%d. %s" % (n, page.get_url())
                n += 1
            
        print>>OUT, ''

    def get_all_forms(self):
        """
        Return a list of all of the forms, with global_form at index 0
        iff present.
        """
        # --BRT-- Does lxml follow this behavior?
        if self.result:
            doc = html.fromstring(self.result.get_page())
            return doc.forms
        return []

    def get_form(self, formname):
        """
        Return the first form that matches 'formname'.
        """
        # --BRT-- Incomplete
        if self.result:
            doc = html.fromstring(self.result.get_page())
            for form in doc.forms:
                if re.search(form.name, formname):
                    return form
        return None

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
        with open(filename, 'w') as f:
            pickle.dump(
                requests.utils.dict_from_cookiejar(self._session.cookies),
                f
            )

    def load_cookies(self, filename):
        """
        Load cookies from the given file.
        """
        # --BRT-- Adds to rather than overwriting cookies - correct?
        with open('somefile') as f:
            c = requests.utils.add_dict_to_cookiejar(
                self._session.cookies, 
                pickle.load(f)
            )
        self._session.cookies = c

    def clear_cookies(self):
        """
        Delete all of the cookies.
        """
        self._session.cookies.clear()

    def show_cookies(self):
        """
        Pretty-print all of the cookies.
        """
        # --BRT-- show_cookies is the only show w/ underscore syntax - why?
        # --BRT-- Format is different, site names not associated w/ cookies
        c = requests.utils.dict_from_cookiejar(self._session.cookies)
        print>>OUT, 'There are %d cookie(s) in the cookiejar.' % (len(c))
        
        if len(c):
            for k,v in c.iteritems():
                print>>OUT, k, '\t', v
            print>>OUT, ''

    def _journey(self, func_name, *args, **kwargs):
        """
        'func_name' should be one of 'open', 'reload', 'back', or 'follow_link'.

        journey then runs that function with the given arguments and turns
        the results into a nice friendly standard ResultWrapper object, which
        is stored as 'self.result'.

        All exceptions other than HTTPError are unhandled.
        
        (Idea stolen straight from PBP.)
        """
        self.last_submit_button = None

        if func_name == 'open':
            if self.result:
                self._history.append(self.result)
            r = self._session.get(*args, headers=self._headers, auth=self._auth)
            url = args[0] # r.get_url()
            self.result = ResultWrapper(r.status_code, url, r.text)

        elif func_name == 'follow_link':
            if self.result:
                self._history.append(self.result)
            # --BRT-- Try to find the link first, appropriate method?
            url = self.find_link(args[0])
            if url.find('://') == -1:
                url = self.result.get_url() + url
            r = self._session.get(url, headers=self._headers)
            # url = r.get_url()
            url = args[0]
            self.result = ResultWrapper(r.status_code, url, r.text)

        elif func_name == 'reload':
            r = self._session.get(
                self.result.get_url(), 
                headers=self._headers,
                auth = self._auth
            )
            url = self.result.get_url()
            self.result = ResultWrapper(r.status_code, url, r.text)

        elif func_name == 'back':
            try:
                url = self._history.pop().get_url()
                r = self._session.get(
                    url, 
                    headers=self._headers, 
                    auth=self._auth
                )
                self.result = ResultWrapper(r.status_code, url, r.text)
            except IndexError:
                pass

        else:
            self.result = None
