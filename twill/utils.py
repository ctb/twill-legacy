"""
Various ugly utility functions for twill.

Apart from various simple utility functions, twill's robust parsing
code is implemented in the ConfigurableParsingFactory class.
"""

import os
import base64

import subprocess

from lxml import etree, html, cssselect
import re

from errors import TwillException

class ResultWrapper(object):
    """
    Deal with mechanize/urllib2/whatever results, and present them in a
    unified form.  Returned by 'journey'-wrapped functions.
    """
    def __init__(self, req):
        self.req = req
        self.lxml = html.fromstring(self.req.text)
        gfEntry = html.FormElement
        orphans = self.lxml.xpath('//input[not(ancestor::form)]')
        if len(orphans) > 0:
            gloFo = "<form>"
            for o in orphans:
                gloFo += etree.tostring(o)
            gloFo += "</form>"
            self.forms = html.fromstring(gloFo).forms
            self.forms.extend(self.lxml.forms)
        else:
            self.forms = self.lxml.forms

    def get_url(self):
        return self.req.url

    def get_http_code(self):
        return self.req.status_code

    def get_page(self):
        return self.req.text

    def get_headers(self):
        return self.req.headers

    def get_forms(self):
        return self.forms

    def get_title(self):
        selector = cssselect.CSSSelector("title")
        return selector(self.lxml)[0].text

    def get_links(self):
        selector = cssselect.CSSSelector("a")
        return [
                 # (stringify_children(l) or '', l.get("href")) 
                 (l.text or '', l.get("href"))
                 for l in selector(self.lxml)
               ]
    def find_link(self, pattern):
        selector = cssselect.CSSSelector("a")

        links = [
                 # (stringify_children(l) or '', l.get("href")) 
                 (l.text or '', l.get("href"))
                 for l in selector(self.lxml)
                ]
        for link in links:
            if re.search(pattern, link[0]) or re.search(pattern, link[1]):
                return link[1]
        return ''

    def get_form(self, formname):
        forms = self.get_forms()

        # first try ID
        for f in forms:
            id = f.get("id")
            if id and str(id) == formname:
                return f
        
        # next try regexps
        regexp = re.compile(formname)
        for f in forms:
            if f.get("name") and regexp.search(f.get("name")):
                return f

        # ok, try number
        try:
            formnum = int(formname)
            if formnum >= 0 and formnum <= len(forms):
                return forms[formnum - 1]
        except (ValueError, IndexError):              # int() failed
            return None

def trunc(s, length):
    """
    Truncate a string s to length length, by cutting off the last 
    (length-4) characters and replacing them with ' ...'
    """
    if not s:
        return ''
    
    if len(s) > length:
        return s[:length-4] + ' ...'
    
    return s

def print_form(n, f, OUT):
    """
    Pretty-print the given form, assigned # n.
    """
    if f.get('name'):
         print>>OUT, '\nForm name=%s (#%d)' % (f.get('name'), n + 1)
    else:
        print>>OUT, '\nForm #%d' % (n + 1,)

    if f.inputs is not None:
        print>>OUT, "## ## __Name__________________ __Type___ __ID________ __Value__________________"

    for n, field in enumerate(f.inputs):
        if hasattr(field, 'value_options'):
            items = [ i.name if hasattr(i, 'name') else i 
                        for i in field.value_options ]
            value_displayed = "%s of %s" % ([i for i in field.value], items)
        else:
            value_displayed = "%s" % (field.value,)

        submit_index = "  "
        strings = ("%-2s" % (n + 1,),
                   submit_index,
                   "%-24s %-9s" % (trunc(str(field.name), 24),
                                   trunc(field.type 
                                   if hasattr(field, 'type') else 'select', 9)),
                    "%-12s" % (trunc(field.get("id") or "(None)", 12),),
                   trunc(value_displayed, 40),
                   )
        for s in strings:
            print>>OUT, s,
        print>>OUT, ''

    print ''

def make_boolean(value):
    """
    Convert the input value into a boolean like so:
    
    >> make_boolean('true')
    True
    >> make_boolean('false')
    False
    >> make_boolean('1')
    True
    >> make_boolean('0')
    False
    >> make_boolean('+')
    True
    >> make_boolean('-')
    False
    """
    value = str(value)
    value = value.lower().strip()

    # true/false
    if value in ('true', 'false'):
        if value == 'true':
            return True
        return False

    # 0/nonzero
    try:
        ival = int(value)
        return bool(ival)
    except ValueError:
        pass

    # +/-
    if value in ('+', '-'):
        if value == '+':
            return True
        return False

    # on/off
    if value in ('on', 'off'):
        if value == 'on':
            return True
        return False

    raise TwillException("unable to convert '%s' into true/false" % (value,))

def set_form_control_value(control, val):
    """
    Helper function to deal with setting form values on checkboxes, lists etc.
    """
    if hasattr(control, 'type') and control.type == 'checkbox':
        try:
            # checkbox = control.get()
            val = make_boolean(val)
            control.checked = val
            return
        except TwillException:
            # if there's more than one checkbox, use the behaviour for
            # ClientForm.ListControl, below.
            pass
            
    elif isinstance(control, html.CheckboxGroup):
        if val.startswith('-'):
            val = val[1:]
            flag = False
        else:
            flag = True
            if val.startswith('+'):
                val = val[1:]
        if flag:
            control.value.add(val)
        else:
            try:
                control.value.remove(val)
            except KeyError:
                pass

    elif isinstance(control, html.SelectElement):
        #
        # for ListControls (checkboxes, multiselect, etc.) we first need
        # to find the right *value*.  Then we need to set it +/-.
        #

        # figure out if we want to *select* it, or if we want to *deselect*
        # it (flag T/F).  By default (no +/-) select...
        if val.startswith('-'):
            val = val[1:]
            flag = False
        else:
            flag = True
            if val.startswith('+'):
                val = val[1:]

        # now, select the value.

        options = [i.strip() for i in control.value_options]
        optionNames = [i.text.strip() for i in control.getchildren()]
        fullOptions = dict(zip(optionNames, options))
        for k,v in fullOptions.iteritems():
            if (val == k or val == v) and flag:
                if hasattr(control, 'checkable') and control.checkable:
                    control.checked = flag
                else:
                    control.value.add(v)
                return
            elif (val == k or val == v) and not flag:
                try:
                    control.value.remove(v)
                except ValueError:
                    pass
                return
        raise(TwillException("Attempt to set invalid value"))
        
    else:
        if(hasattr(control, 'type') and control.type != 'submit'):
            control.value = val
        #else:
            #raise(TwillException("Attempt to set value on invalid control"))

def _all_the_same_submit(matches):
    """
    Utility function to check to see if a list of controls all really
    belong to the same control: for use with checkboxes, hidden, and
    submit buttons.
    """
    name = None
    value = None
    for match in matches:
        if match.type not in ['submit', 'hidden']:
            return False
        if name is None:
            name = match.name
            value = match.value
        else:
            if match.name != name or match.value!= value:
                return False
    return True

def _all_the_same_checkbox(matches):
    """
    Check whether all these controls are actually the the same
    checkbox.

    Hidden controls can combine with checkboxes, to allow form
    processors to ensure a False value is returned even if user
    does not check the checkbox. Without the hidden control, no
    value would be returned.
    """
    name = None
    for match in matches:
        if match.type not in ['checkbox', 'hidden']:
            return False
        if name is None:
            name = match.name
        else:
            if match.name != name:
                return False
    return True

def unique_match(matches):
    return len(matches) == 1 or \
           _all_the_same_checkbox(matches) or \
           _all_the_same_submit(matches)

#
# stuff to run 'tidy'...
#

_tidy_cmd = ["tidy", "-q", "-ashtml"]
_tidy_exists = True

def run_tidy(html):
    """
    Run the 'tidy' command-line program on the given HTML string.

    Return a 2-tuple (output, errors).  (None, None) will be returned if
    'tidy' doesn't exist or otherwise fails.
    """
    global _tidy_cmd, _tidy_exists

    from commands import _options
    require_tidy = _options.get('require_tidy')

    if not _tidy_exists:
        if require_tidy:
            raise TwillException("tidy does not exist and require_tidy is set")
        return (None, None)
    
    #
    # run the command, if we think it exists
    #
    
    clean_html = None
    if _tidy_exists:
        try:
            process = subprocess.Popen(_tidy_cmd, stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, bufsize=0,
                                       shell=False)
        
            (stdout, stderr) = process.communicate(html)

            clean_html = stdout
            errors = stderr
        except OSError:
            _tidy_exists = False

    errors = None
    if require_tidy and clean_html is None:
        raise TwillException("tidy does not exist and require_tidy is set")

    return (clean_html, errors)


def _is_valid_filename(f):
    return not (f.endswith('~') or f.endswith('.bak') or f.endswith('.old'))

# Added so browser can ask whether to follow meta redirects
def _follow_equiv_refresh():
    from twill.commands import _options
    return _options.get('acknowledge_equiv_refresh')

def gather_filenames(arglist):
    """
    Collect script files from within directories.
    """
    l = []

    for filename in arglist:
        if os.path.isdir(filename):
            thislist = []
            for (dirpath, dirnames, filenames) in os.walk(filename):
                if '.svn' in dirpath:   # ignore subversion files
                    continue
                for f in filenames:
                    if _is_valid_filename(f):
                        f = os.path.join(dirpath, f)
                        thislist.append(f)
                        
            thislist.sort()
            l.extend(thislist)
        else:
            l.append(filename)

    return l
