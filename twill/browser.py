"""
Implements TwillBrowser
"""

OUT=None

# Python imports
import pickle
import re
import urlparse

# Dependencies
import requests
from lxml import html
from requests.exceptions import InvalidSchema, ConnectionError
from utils import print_form, unique_match, _follow_equiv_refresh, ResultWrapper
from errors import TwillException

class TwillBrowser(object):
    """A simple, stateful browser"""
    def __init__(self):
        #
        # create special link/forms parsing code to run tidy on HTML first.
        #

        # WSGI Intercept
        # Taken from
        # https://code.google.com/p/wsgi-intercept/issues/detail?id=23
        # with slight modification
        import wsgi_intercept
        from requests.packages.urllib3 import connectionpool as cpl
        cpl.HTTPConnectionPool.old_http = cpl.HTTPConnectionPool.ConnectionCls
        cpl.HTTPConnectionPool.ConnectionCls = wsgi_intercept.WSGI_HTTPConnection
        wsgi_intercept.wsgi_fake_socket.settimeout = lambda self, timeout: None

        self.result = None
        self.last_submit_button = None

        # Session stores cookies
        self._session = requests.Session()
        self._session.headers.update({"Accept" : "text/html; */*"})

        # An lxml FormElement, none until a form is selected
        # replaces self._browser.form from mechanize
        self._form = None
        self._formFiles = {}

        # A dict of HTTPBasicAuth from requests, keyed off URL
        self._auth = {}

        # callables to be called after each page load.
        self._post_load_hooks = []

        self._history = []

    def _set_creds(self, creds):
        self._auth[creds[0]] = requests.auth.HTTPBasicAuth(*creds[1])

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

        # if this is a '?' or '/' URL, then assume that we want to tack it onto
        # the end of the current URL.
        try_urls.append(urlparse.urljoin(self.get_url(), url))
        
        success = False
        for u in try_urls:
            try:
                self._journey('open', u)
                success = True
                break

            except (IOError, ConnectionError, InvalidSchema):  # @CTB test this!
                pass

        if success:
            print>>OUT, '==> at', self.get_url()
        else:
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
        try:
            self._journey('back')
            print>>OUT, '==> back to', self.get_url()
        except TwillException:
            print>>OUT, '==> back at empty page.'

    def get_code(self):
        """
        Get the HTTP status code received for the current page.
        """
        if self.result is not None:
            return self.result.get_http_code()
        return None

    def get_html(self):
        """
        Get the HTML for the current page.
        """
        if self.result is not None:
            return self.result.get_page()
        return None

    def get_title(self):
        if self.result is not None:
            return self.result.get_title()
        raise TwillException("Error: Getting title with no page")

    def get_url(self):
        """
        Get the URL of the current page.
        """
        if self.result is not None:
            return self.result.get_url()
        return None

    def find_link(self, pattern):
        """
        Find the first link with a URL, link text, or name matching the
        given pattern.
        """
        if self.result is not None:
            return self.result.find_link(pattern)
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
        self._session.headers.update({'User-agent' : agent})
        return

    def showforms(self):
        """
        Pretty-print all of the forms.  Include the global form (form
        elements outside of <form> pairs) as forms[0] iff present.
        """
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
            print>>OUT, "\t%d. %s" % (n, page.get_url())
            n += 1
        print>>OUT, ''

    def get_all_links(self):
        """
        Return a list of all of the links on the page
        """
        if self.result is not None:
            return self.result.get_links()
        return []

    def get_all_forms(self):
        """
        Return a list of all of the forms, with global_form at index 0
        iff present.
        """
        if self.result is not None:
            return self.result.get_forms()
        return []

    def get_form(self, formname):
        """
        Return the first form that matches 'formname'.
        """
        if self.result is not None:
            return self.result.get_form(formname)
        return None


    def get_form_field(self, form, fieldname):
        """
        Return the control that matches 'fieldname'.  Must be
        a *unique* regexp/exact string match.
        """
        if fieldname in form.fields.keys():
            controls = [f for f in form.inputs if f.get("name") == fieldname \
                        and hasattr(f, 'type') and f.type == 'checkbox']
            if len(controls) > 1:
                return html.CheckboxGroup(controls)

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
        
        matches = [ c for c in form.inputs if str(c.name) == fieldname ]

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
                        if regexp.search(str(ctl.get("name"))) ]

            if matches:
                if unique_match(matches):
                    found = matches[0]
                else:
                    found_multiple = True # record for error

        if found is None:
            clickies = [ c for c in form.inputs if c.value == fieldname]
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
        if self._form != form:
            # construct a function to choose a particular form; select_form
            # can use this to pick out a precise form.

            self._form = form
            self.last_submit_button = None
        # record the last submit button clicked.
        if hasattr(control, 'type') and \
            (control.type == 'submit' or control.type == 'image'):
            self.last_submit_button = control

    def submit(self, fieldname=None):
        """
        Submit the currently clicked form using the given field.
        """
        if fieldname is not None:
            fieldname = str(fieldname)
        
        if len(self.get_all_forms()) == 0:
            raise TwillException("no forms on this page!")
        
        ctl = None
        
        form = self._form
        if form is None:
            forms = [ i for i in self.get_all_forms() ]
            if len(forms) == 1:
                form = forms[0]
            else:
                raise TwillException("""\
more than one form; you must select one (use 'fv') before submitting\
""")
        if form.action is None:
            form.action = self.get_url()

        # no fieldname?  see if we can use the last submit button clicked...
        if fieldname is None:
            if self.last_submit_button is not None:
                ctl = self.last_submit_button
            else:
                # get first submit button in form.
                submits = [ c for c in form.inputs 
                            if hasattr(c, 'type') and (c.type == 'submit' 
                            or c.type == 'image')]
                if len(submits) != 0:
                    ctl = submits[0]             
        else:
            # fieldname given; find it.
            ctl = self.get_form_field(form, fieldname)

        #
        # now set up the submission by building the request object that
        # will be sent in the form submission.
        #
        if ctl is not None:
            # submit w/button
            print>>OUT, """\
Note: submit is using submit button: name="%s", value="%s"
""" % (ctl.get("name"), ctl.value)
            
            if hasattr(ctl, 'type') and ctl.type == 'image':
                pass
            
                
        else:
            # submit w/o submit button.
            pass

        # @BRT: For now, the referrer is always the current page
        # @CTB this seems like an issue for further work.
        headers = {'referer' : self.get_url()}

        #
        # add referer information.  this may require upgrading the
        # request object to have an 'add_unredirected_header' function.
        #

        #
        # now actually GO.
        #
        payload = list(form.form_values())
        if ctl is not None and ctl.get("name") is not None:
            payload.append( (ctl.get("name"), ctl.value) )
        if form.method == 'POST':
            if len(self._formFiles) != 0:
                r = self._session.post(
                                        form.action, 
                                        data=payload, 
                                        files=self._formFiles, 
                                        headers=headers
                                      )
            else:
                r = self._session.post(
                                        form.action, 
                                        data=payload, 
                                        headers=headers
                                      )
        else:
            r = self._session.get(form.action, data=payload, headers=headers)

        self._formFiles.clear()
        self._history.append(self.result)
        self.result = ResultWrapper(r)

    def save_cookies(self, filename):
        """
        Save cookies into the given file.
        """
        with open(filename, 'wb') as f:
            pickle.dump(self._session.cookies, f)

    def load_cookies(self, filename):
        """
        Load cookies from the given file.
        """
        with open(filename, 'rb') as f:
            self._session.cookies = pickle.load(f)

    def clear_cookies(self):
        """
        Delete all of the cookies.
        """
        self._session.cookies.clear()

    def show_cookies(self):
        """
        Pretty-print all of the cookies.
        """
        c = requests.utils.dict_from_cookiejar(self._session.cookies)
        print>>OUT, 'There are %d cookie(s) in the cookiejar.\n' % (len(c))
        
        if len(self._session.cookies):
            for cookie in self._session.cookies:
                print>>OUT, '\t', cookie

            print>>OUT, ''

    # BRT: Added to test for meta redirection
    #       Shamelessly stolen from 
    #       http://stackoverflow.com/questions/2318446/how-to-follow-meta-refreshes-in-python
    #       Took some modification to get it working, though
    #       Original post notes that this doesn't check circular redirect
    #       Is this something we're concerned with?
    def _test_for_meta_redirections(self, r):
        """
        Checks a document for meta redirection
        """
        html_tree = html.fromstring(r.text)
        attr = html_tree.xpath(
        "//meta[translate(@http-equiv, 'REFSH', 'refsh') = 'refresh']/@content"
                )
        if len(attr) > 0:
            wait, text = attr[0].split(";")
            # @BRT: Strip surrounding quotes and ws; less brute force method?
            #       Other chars that need to be dealt with?
            text = text.strip()
            text = text.strip('\'"')
            if text.lower().startswith("url="):
                url = text[4:]
                if not url.startswith('http'):
                    # Relative URL, adapt
                    url = urlparse.urljoin(r.url, url)
                    return True, url
        return False, None

    # BRT: Added to test for meta redirection
    # Shamelessly stolen from the same link as _test_for_meta_redirections
    def _follow_redirections(self, r, s):
        """
        Recursive function that follows meta refresh redirections if they exist.
        """
        redirected, url = self._test_for_meta_redirections(r)
        if redirected:
            r = self._follow_redirections(s.get(url), s)
        return r

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
            url = args[0]

        elif func_name == 'follow_link':
            # Try to find the link first
            url = self.find_link(args[0])
            if url.find('://') == -1:
                url = urlparse.urljoin(self.get_url(), url)

        elif func_name == 'reload':
            url = self.get_url()

        elif func_name == 'back':
            try:
                self.result = self._history.pop()
                return
            except IndexError:
                raise TwillException

        if url in self._auth.keys():
            auth = self._auth[url]
        else:
            auth = None

        r = self._session.get(url, auth = auth)

        if _follow_equiv_refresh():
            r = self._follow_redirections(r, self._session)

        if func_name in ['follow_link', 'open']:
            # If we're really reloading and just didn't say so, don't store
            if self.result is not None and self.result.get_url() != r.url:
                self._history.append(self.result)

        self.result = ResultWrapper(r)
