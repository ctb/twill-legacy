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

        # @BRT: This is mechanize. Remove it? Or rewrite it?
        #factory = ConfigurableParsingFactory()

        self.result = None
        self.last_submit_button = None

        # Session stores cookies
        self._session = requests.Session()

        self._headers = dict([("Accept", "text/html; */*")])

        # An HTTPBasicAuth from requests, None until creds added
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

        # @BRT urls beginning with / need to be special-cased now
        # @BRT This seems to be causing a hang in the tests
        if(url.startswith('/')):
            u = self.get_url()
            prefix = u[:u.find('://')+3]
            base_url = u.split('/')[2]
            try_urls.append(prefix+base_url+url)
        
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
        # @BRT: Possibly broken? Seems to work better when else is commented
        #      May be related to other not-yet-implemented functions
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
        # @BRT: Modified to use TwillException in place of BrowserStateError
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
        # @BRT: Does lxml follow golbal_form @ index 0 behavior from docstring?
        forms = self.get_all_forms()
        for n, f in enumerate(forms):
            print_form(n, f, OUT)

    def showlinks(self):
        """
        Pretty-print all of the links.
        """
        links = self.get_all_links()
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
            # @BRT: confirm that this is the intended logic of below comment
            if page.get_http_code() == 200:
            # only print those that back() will go
                print>>OUT, "\t%d. %s" % (n, page.get_url())
                n += 1
        print>>OUT, ''

    def get_all_links(self):
        """
        Return a list of all of the links on the page
        """
        # @BRT: New function for use in commands, showlinks function
        doc = html.fromstring(self.result.get_page())
        selector = cssselect.CSSSelector("a")
        return iter([(l.text, l.get("href")) for l in selector(doc)])

    def get_all_forms(self):
        """
        Return a list of all of the forms, with global_form at index 0
        iff present.
        """
        # @BRT: Does lxml follow golbal_form @ index 0 behavior from docstring?
        if self.result:
            doc = html.fromstring(self.result.get_page())
            return doc.forms
        return []

    def get_form(self, formname):
        """
        Return the first form that matches 'formname'.
        """
        # @BRT: Returns an lxml FormElement where old code may expect mechanize
        forms = self.get_all_forms()

        # first try ID
        for f in forms:
            id = f.get("id")
            if id and str(id) == formname:
                return f
        
        # next try regexps
        regexp = re.compile(formname)
        for f in forms:
            if f.get("name") and regexp.search(f.name):
                return f

        # ok, try number
        try:
            formnum = int(formname)
            # @BRT: Does lxml follow golbal_form @ index 0 behavior?
            #      Otherwise, change conditional to >= 0
            if formnum >= 1 and formnum <= len(forms):
                return forms[formnum - 1]
        except ValueError:              # int() failed
            pass
        except IndexError:              # formnum was incorrect
            pass
        return None


    def get_form_field(self, form, fieldname):
        """
        Return the control that matches 'fieldname'.  Must be
        a *unique* regexp/exact string match.
        """
        fieldname = str(fieldname)
        
        found = None
        found_multiple = False

        matches = [ c for c in form.inputs if c.get("id") == fieldname ]

        # test exact match.
        if matches:
            if unique_match(matches):
                found = matches[0]
            else:
                found_multiple = True   # record for error reporting.
        
        matches = [ c for c in form.controls if str(c.name) == fieldname ]

        # test exact match.
        if matches:
            if unique_match(matches):
                found = matches[0]
            else:
                found_multiple = True   # record for error reporting.

        # test index.
        if found is None:
            # try num
            clickies = [c for c in form.inputs]
            try:
                fieldnum = int(fieldname) - 1
                found = clickies[fieldnum]
            except ValueError:          # int() failed
                pass
            except IndexError:          # fieldnum was incorrect
                pass

        # test regexp match
        if found is None:
            regexp = re.compile(fieldname)

            matches = [ ctl for ctl in form.inputs \
                        if regexp.search(ctl.get("name")) ]

            if matches:
                if unique_match(matches):
                    found = matches[0]
                else:
                    found_multiple = True # record for error

        if found is None:
            # @BRT: better way to check for readonly?
            # try value, for readonly controls like submit keys
            clickies = [ c for c in form.inputs if c.value == fieldname
                         and 'readonly' in c.attrib.keys()]
            if clickies:
                if len(clickies) == 1:
                    found = clickies[0]
                else:
                    found_multiple = True   # record for error

        # error out?
        if found is None:
            if not found_multiple:
                raise TwillException('no field matches "%s"' % (fieldname,))
            else:
                raise TwillException('multiple matches to "%s"' % (fieldname,))

        return found

    def clicked(self, form, control):
        """
        Record a 'click' in a specific form.
        """
        # @BRT: Incomplete: clicked()
        return

    def submit(self, fieldname=None):
        """
        Submit the currently clicked form using the given field.
        """
        # @BRT: Incomplete: submit()
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
        # @BRT: Adds to rather than overwriting cookies - correct?
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
        # @BRT: show_cookies is the only show w/ underscore syntax - why?
        c = requests.utils.dict_from_cookiejar(self._session.cookies)
        print>>OUT, 'There are %d cookie(s) in the cookiejar.\n' % (len(c))
        
        if len(self._session.cookies):
            for cookie in self._session.cookies:
                print>>OUT, '\t', cookie

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
            # @BRT: Try to find the link first, same as mechanize behavior?
            url = self.find_link(args[0])
            if url.find('://') == -1:
                if url[-1] != '/':
                    url = self.result.get_url() + '/' + url
                else:
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
