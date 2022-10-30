"""
Implementation of all the individual 'twill' commands available
through twill-sh.
"""

import getpass
import re
import time
import sys
from typing import Any, Dict, Optional

from os.path import sep

from . import log, set_output, set_err_out, utils
from .agents import agents
from .browser import browser
from .errors import TwillException, TwillAssertionError
from .namespaces import get_twill_glocals

# noinspection SpellCheckingInspection
__all__ = [
    'add_auth', 'add_cleanup', 'add_extra_header', 'agent',
    'back', 'browser',
    'clear_cookies', 'clear_extra_headers',
    'code', 'config',
    'debug', 'echo', 'exit', 'extend_with',
    'find', 'follow',
    'form_action', 'formaction', 'fa',
    'form_clear', 'formclear', 'form_file', 'formfile',
    'form_value', 'formvalue', 'fv',
    'get_input', 'getinput', 'get_password', 'getpassword',
    'go', 'info', 'load_cookies', 'not_find', 'notfind', 'options',
    'redirect_error', 'redirect_output',
    'reload', 'reset_browser', 'reset_error', 'reset_output',
    'run', 'run_file', 'runfile', 'rf',
    'save_cookies', 'save_html',
    'setglobal', 'set_global', 'setlocal', 'set_local',
    'show', 'showcookies', 'show_cookies', 'show_extra_headers',
    'showforms', 'show_forms', 'showhistory', 'show_history',
    'showhtml', 'show_html', 'showlinks', 'show_links',
    'sleep', 'submit',
    'tidy_ok', 'title', 'url']


def reset_browser():
    """>> reset_browser

    Reset the browser completely.
    """
    browser.reset()
    options.clear()
    options.update(default_options)


# noinspection PyShadowingBuiltins
def exit(code: str = '0') -> None:
    """twill command: exit [<code>]

    Exit twill, with the given exit code (defaults to 0, "no error").
    """
    raise SystemExit(int(code))


def go(url: str) -> None:
    """>> go <url>

    Visit the URL given.
    """
    browser.go(url)


def reload() -> None:
    """>> reload

    Reload the current URL.
    """
    browser.reload()


def code(should_be: str) -> None:
    """>> code <int>

    Check to make sure the response code for the last page is as given.
    """
    if browser.code != int(should_be):
        raise TwillAssertionError(f"code is {browser.code} != {should_be}")


def tidy_ok() -> None:
    """>> tidy_ok

    Assert that 'tidy' does not produce any warnings or errors when run on
    the current page.

    If 'tidy' cannot be run, will fail silently (unless 'require_tidy' option
    is true; see 'config' command).
    """
    page = browser.html
    if page is None:
        raise TwillAssertionError("not viewing HTML!")

    clean_page, errors = utils.run_tidy(page)
    if clean_page is None:  # tidy doesn't exist...
        if options.get('require_tidy'):
            raise TwillAssertionError("cannot run 'tidy'")
    elif errors:
        raise TwillAssertionError(f"tidy errors:\n====\n{errors}\n====\n")


def url(should_be: str) -> str:
    """>> url <pattern>

    Check to make sure that the current URL matches the regex pattern.
    The local variable __match__ is set to the matching part of the URL.
    """
    regex = re.compile(should_be)
    current_url = browser.url

    if current_url is None:
        current_url = ''
        m = None
    else:
        m = regex.search(current_url)

    if not m:
        raise TwillAssertionError(
            f"current url is '{current_url}';\n"
            f"does not match '{should_be}'\n")

    match_str = m.group(1 if m.groups() else 0)
    global_dict, local_dict = get_twill_glocals()
    local_dict['__match__'] = match_str
    return match_str


def follow(what: str) -> str:
    """>> follow <pattern>

    Find the first link on the page matching the given regex pattern and
    then visit it.
    """
    link = browser.find_link(what)
    if link:
        browser.follow_link(link)
        return browser.url

    raise TwillAssertionError(f"no links match to '{what}'")


_find_flags = dict(i=re.IGNORECASE, m=re.MULTILINE, s=re.DOTALL)


def _parse_find_flags(flags: str) -> int:
    """Helper function to parse the find flags."""
    re_flags = 0
    for char in flags:
        try:
            re_flags |= _find_flags[char]
        except IndexError:
            raise TwillAssertionError(f"unknown 'find' flag {char!r}")
    return re_flags


def find(what: str, flags='') -> str:
    """>> find <pattern> [<flags>]

    Succeed if the regular expression pattern can be found on the page.
    Sets the local variable __match__ to the matching text.

    Flags is a string consisting of the following characters:

    * i: ignore case
    * m: multi-line
    * s: dot matches all
    * x: use XPath expressions instead of regular expression

    For explanations of regular expressions, please see the Python re module
    documentation.
    """
    page = browser.html
    local_dict = get_twill_glocals()[1]
    if 'x' in flags:
        elements = browser.xpath(what)
        if not elements:
            raise TwillAssertionError(f"no element to path '{what}'")
        match_str = elements[0].text or ''
    else:
        match = re.search(what, page, flags=_parse_find_flags(flags))
        if not match:
            raise TwillAssertionError(f"no match to '{what}'")
        match_str = match.group(1 if match.groups() else 0)
    local_dict['__match__'] = match_str
    return match_str


def not_find(what: str, flags='') -> None:
    """>> not_find <pattern> [<flags>]

    Fail if the regular expression pattern can be found on the page.
    """
    try:
        find(what, flags)
    except TwillAssertionError:
        pass
    else:
        raise TwillAssertionError(f"match to '{what}'")


# noinspection SpellCheckingInspection
notfind = not_find  # backward compatibility and convenience


def back() -> None:
    """>> back

    Return to the previous page.
    """
    browser.back()


def show(what: Optional[str] = None) -> None:
    """>> show [<objects>]

    Show the specified objects (html, cookies, forms, links, history).
    """
    if not what:
        what = 'html'
    command = None
    if what.isalpha():
        command_name = f'show_{what}'
        if command_name in __all__:
            command = globals().get(command_name)
    if not command:
        raise TwillException(f'Cannot show "{what}".')
    command()


def show_html() -> None:
    """>> show_html

    Show the HTML for the current page or show the specified objects
    (which can be cookies, forms, history or links).

    Note: Use browser.html to get the HTML programmatically.
    """
    html = browser.html.strip()
    log.info('')
    log.info(html)
    log.info('')


# noinspection SpellCheckingInspection
showhtml = show_html  # backward compatibility and consistency


def echo(*strs: str) -> None:
    """>> echo <list> <of> <strings>

    Echo the arguments to the screen.
    """
    log.info(' '.join(map(str, strs)))


def save_html(filename: Optional[str] = None) -> None:
    """>> save_html [<filename>]

    Save the HTML for the current page into <filename>.
    If no filename given, construct the filename from the URL.
    """
    html = browser.html
    if html is None:
        log.warning("No page to save.")
        return

    if filename is None:
        url = browser.url
        url = url.split('?', 1)[0]
        filename = url.rsplit('/', 1)[-1]
        if not filename:
            filename = 'index.html'
        log.info("Using filename '%s'.", filename)

    encoding = browser.encoding or 'utf-8'
    try:
        with open(filename, 'w', encoding=encoding) as f:
            f.write(html)
    except UnicodeEncodeError:
        if encoding == 'utf-8':
            raise
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)


def sleep(interval: str = "1") -> None:
    """>> sleep [<interval>]

    Sleep for the specified amount of time.
    If no interval is given, sleep for 1 second.
    """
    time.sleep(float(interval))


def agent(what: str) -> None:
    """>> agent <agent>

    Set the agent string (identifying the browser brand).

    Some convenient shortcuts:
    chrome_107, firefox_106, safari_605, edge_107, ie_11.

    See twill.agents for a list of all available shortcuts.
    """
    what = what.strip()
    agent = agents.get(what, what)
    browser.agent_string = agent


def submit(submit_button: Optional[str] = None,
           form_name: Optional[str] = None) -> None:
    """>> submit [<submit_button> [<form_name>]]

    Submit the current form (the one last clicked on) by clicking on the
    given submission button.  If no 'submit_button' is given, submit the
    current form by using the last clicked submit button.

    The form to submit is the last form clicked on with a 'form_value' command
    unless explicitly specified given the

    The button used to submit is chosen based on 'submit_button'.
    If 'submit_button' is given, it's matched against buttons using
    the same rules that 'form_value' uses.  If 'button_name' is not given,
    this function uses the last submit button clicked on by 'form_value'.
    If none can be found, it submits the form with no submit button clicked.
    """
    browser.submit(submit_button, form_name)


def show_forms() -> None:
    """>> show_forms

    Show all the forms on the current page.

    Note: Use browser.forms to get the forms programmatically.
    """
    browser.show_forms()


# noinspection SpellCheckingInspection
showforms = show_forms  # backward compatibility and convenience


def show_links() -> None:
    """>> show_links

    Show all the links on the current page.

    Note: Use browser.links to get the links programmatically.
    """
    browser.show_links()


# noinspection SpellCheckingInspection
showlinks = show_links  # backward compatibility and convenience


def show_history() -> None:
    """>> show_history

    Show the browser history (what URLs were visited).

    Note: Use browser.history to get the history programmatically.
    """
    browser.show_history()


# noinspection SpellCheckingInspection
showhistory = show_history  # backward compatibility and convenience


def form_clear(form_name: str) -> None:
    """>> form_clear <form_name>

    Run 'clear' on all the controls in this form.
    """
    form = browser.form(form_name)
    if form is None:
        raise TwillAssertionError("Form not found")
    for control in form.inputs:
        if not ('readonly' in control.attrib
                or 'disabled' in control.attrib
                or getattr(control, 'type', None)
                in ('submit', 'image', 'hidden')):
            del control.value
    browser.last_submit_button = None


# noinspection SpellCheckingInspection
formclear = form_clear  # backward compatibility and convenience


def form_value(form_name: str, field_name: str, value: str) -> None:
    """>> form_value <form_name> <field_name> <value>

    Set value of a form field.

    There are some ambiguities in the way 'form_value' deals with lists:
    'form_value' will *add* the given value to a list of multiple selection,
    for lists that allow it.

    Forms are matched against 'form_name' as follows:
      1. regex match to actual form name;
      2. if 'form_name' is an integer, it's tried as an index.

    Form controls are matched against 'field_name' as follows:
      1. unique exact match to control name;
      2. unique regex match to control name;
      3. if field_name is an integer, it's tried as an index;
      4. unique & exact match to submit-button values.

    'form_value' ignores read-only fields completely; if they're readonly,
    nothing is done, unless the config options ('config' command) are
    changed.

    'form_value' is available as 'fv' as well.
    """
    form = browser.form(form_name)
    if form is None:
        raise TwillAssertionError("Form not found")

    control = browser.form_field(form, field_name)

    browser.clicked(form, control)

    attrib = getattr(control, 'attrib', {})
    if 'readonly' in attrib:
        if options['readonly_controls_writeable']:
            log.info('Forcing read-only form field to writeable.')
            del attrib['readonly']
        else:
            log.info('Form field is read-only or ignorable; nothing done.')
            return

    if getattr(control, 'type', None) == 'file':
        raise TwillException(
            'form field is for file upload; use "form_file" instead')

    value = browser.decode(value)
    utils.set_form_control_value(control, value)


# noinspection SpellCheckingInspection
fv = formvalue = form_value  # backward compatibility and convenience


def form_action(form_name: str, action_url: str) -> None:
    """>> form_action <form_name> <action_url>

    Sets action parameter on form to action_url.

    'form_action' is available as 'fa' as well.
    """
    form = browser.form(form_name)
    if form is None:
        raise TwillAssertionError("Form not found")
    log.info("Setting action for form %s to %s.", form, action_url)
    form.action = action_url


# noinspection SpellCheckingInspection
fa = formaction = form_action  # backward compatibility and convenience


def form_file(form_name: str, field_name: str, filename: str,
              content_type: Optional[str] = None) -> None:
    """>> form_file <form_name> <field_name> <filename> [<content_type>]

    Upload a file via an "upload file" form field.
    """
    filename = filename.replace('/', sep)

    form = browser.form(form_name)
    if form is None:
        raise TwillAssertionError("Form not found")
    control = browser.form_field(form, field_name)

    if getattr(control, 'type', None) != 'file':
        raise TwillException('ERROR: field is not a file upload field!')

    browser.clicked(form, control)
    plain = content_type and content_type.startswith(('plain/', 'html/'))
    fp = open(filename, 'r' if plain else 'rb')
    browser.add_form_file(field_name, fp)

    log.info(
        'Added file "%s" to file upload field "%s".', filename, field_name)


# noinspection SpellCheckingInspection
formfile = form_file  # backward compatibility and convenience


def extend_with(module_name: str) -> None:
    """>> extend_with <module_name>

    Import contents of given module.
    """
    global_dict, local_dict = get_twill_glocals()

    exec(f"from {module_name} import *", global_dict)

    # now add the commands into the commands available for the shell,
    # and print out some nice stuff about what the extension module does.

    mod = sys.modules[module_name]

    from . import parse, shell

    fn_list = getattr(mod, '__all__', None)
    if fn_list is None:
        fn_list = [fn for fn in dir(mod) if callable(getattr(mod, fn))]

    for command in fn_list:
        fn = getattr(mod, command)
        shell.add_command(command, fn.__doc__)
        parse.command_list.append(command)

    info, debug = log.info, log.debug
    info("Imported extension module '%s'.", module_name)
    debug("(at %s)", mod.__file__)

    if shell.interactive:
        if mod.__doc__:
            info("\nDescription:\n\n%s\n", mod.__doc__.strip())
        else:
            if fn_list:
                info('New commands:\n')
                for name in fn_list:
                    info('\t%s', name)
                info('')


def get_input(prompt: str) -> str:
    """>> get_input <prompt>

    Get input, store it in '__input__'.
    """
    local_dict = get_twill_glocals()[1]

    inp = input(prompt)

    local_dict['__input__'] = inp
    return inp


# noinspection SpellCheckingInspection
getinput = get_input  # backward compatibility and convenience


def get_password(prompt: str) -> str:
    """>> get_password <prompt>

    Get a password ("invisible input"), store it in '__password__'.
    """
    local_dict = get_twill_glocals()[1]

    # we use sys.stdin here in order to get the same behaviour on Unix
    # as on other platforms and for better testability of this function
    inp = getpass.getpass(prompt, sys.stdin)

    local_dict['__password__'] = inp
    return inp


# noinspection SpellCheckingInspection
getpassword = get_password  # backward compatibility and convenience


def save_cookies(filename: str) -> None:
    """>> save_cookies <filename>

    Save all the current cookies to the given file.
    """
    browser.save_cookies(filename)


def load_cookies(filename: str) -> None:
    """>> load_cookies <filename>

    Clear the cookie jar and load cookies from the given file.
    """
    browser.load_cookies(filename)


def clear_cookies() -> None:
    """>> clear_cookies

    Clear the cookie jar.
    """
    browser.clear_cookies()


def show_cookies() -> None:
    """>> show_cookies

    Show all the cookies in the cookie jar.

    Note: Use browser.cookies to get the cookies programmatically.
    """
    browser.show_cookies()


# noinspection SpellCheckingInspection
showcookies = show_cookies  # backward compatibility and convenience


def add_auth(realm: str, uri: str, user: str, passwd: str) -> None:
    """>> add_auth <realm> <uri> <user> <passwd>

    Add HTTP Basic Authentication information for the given realm/uri.
    """
    if realm is not None:
        browser.add_creds((uri, realm), user, passwd)
        log.info(
            "Added auth info: realm '%s' / URI '%s' / user '%s'.",
            realm, uri, user)
    if realm is None or options['with_default_realm']:
        browser.add_creds(uri, user, passwd)
        if realm is None:
            log.info("Added auth info: URI '%s' / user '%s'.", uri, user)


def debug(what: str, level: str) -> None:
    """>> debug <what> <level>

    <what> can be:
       * http (any level >= 1), to display the HTTP transactions.
       * commands (any level >= 1), to display the commands being executed.
       * equiv-refresh (any level >= 1) to display HTTP-EQUIV refresh handling.
    """
    from . import parse

    try:
        num_level = int(level)
    except ValueError:
        num_level = 1 if utils.make_boolean(level) else 0

    log.info('DEBUG: Setting %s debugging to level %d.', what, num_level)

    if what == 'http':
        browser.debug_level = num_level
    elif what == 'equiv-refresh':
        browser.show_refresh = num_level > 0
    elif what == 'commands':
        parse.log_commands(num_level > 0)
    else:
        raise TwillException(f'Unknown debugging type: "{what}"')


def run(cmd: str) -> None:
    """>> run <command>

    <command> can be any valid Python command; 'exec' is used to run it.
    """
    # @CTB: use pyparsing to grok the command?  make sure that quoting works...

    # execute command.
    global_dict, local_dict = get_twill_glocals()

    # set __url__
    local_dict['__cmd__'] = cmd
    local_dict['__url__'] = browser.url

    exec(cmd, global_dict, local_dict)


def run_file(*args: str) -> None:
    """>> run_file <file1> [<file2> ...]

    Execute the given twill scripts or directories of twill scripts.

    'run_file' is available as 'rf' as well.
    """
    from . import parse

    filenames = utils.gather_filenames(args)
    for filename in filenames:
        parse.execute_file(filename, no_reset=True)


# noinspection SpellCheckingInspection
rf = runfile = run_file  # backward compatibility and convenience


def add_cleanup(*args: str) -> None:
    """>> add_cleanup <file1> [<file2> ...]

    Execute the given twill scripts after the current twill script.
    """

    local_dict = get_twill_glocals()[1]
    cleanups = local_dict.setdefault('__cleanups__', [])
    filenames = utils.gather_filenames(args)
    log.debug('Adding cleanup scripts: %s', ', '.join(filenames))
    cleanups.extend(reversed(filenames))


def set_global(name: str, value: str) -> None:
    """set_global <name> <value>

    Sets the variable <name> to the value <value> in the global namespace.
    """
    global_dict, local_dict = get_twill_glocals()
    global_dict[name] = value


# noinspection SpellCheckingInspection
setglobal = set_global  # backward compatibility and convenience


def set_local(name: str, value: str) -> None:
    """set_local <name> <value>

    Sets the variable <name> to the value <value> in the local namespace.
    """
    global_dict, local_dict = get_twill_glocals()
    local_dict[name] = value


# noinspection SpellCheckingInspection
setlocal = set_local  # backward compatibility and convenience


def title(what: str) -> str:
    """>> title <pattern>

    Succeed if the regular expression pattern is in the page title.
    """
    regex = re.compile(what)
    title = browser.title

    if title is None:
        log.info("The page has no title.")
    else:
        log.info("The title is '%s'.", title)

    m = regex.search(title) if title else None
    if m is None:
        raise TwillAssertionError(f"The title does not contain '{what}'.")

    if m.groups():
        match_str = m.group(1)
    else:
        match_str = m.group(0)

    global_dict, local_dict = get_twill_glocals()
    local_dict['__match__'] = match_str
    return match_str


def redirect_output(filename: str) -> None:
    """>> redirect_output <filename>

    Append all twill output to the given file.
    """
    fp = open(filename, 'a')
    set_output(fp)


def reset_output() -> None:
    """>> reset_output

    Reset twill output to go to the screen.
    """
    set_output(None)


def redirect_error(filename: str) -> None:
    """>> redirect_error <filename>

    Append all twill error output to the given file.
    """
    fp = open(filename, 'a')
    set_err_out(fp)


def reset_error() -> None:
    """>> reset_error

    Reset twill error output to go to the screen.
    """
    set_err_out(None)


def add_extra_header(header_key: str, header_value: str) -> None:
    """>> add_header <name> <value>

    Add an HTTP header to each HTTP request.  See 'show_extra_headers' and
    'clear_extra_headers'.
    """
    browser.headers[header_key] = header_value


def show_extra_headers() -> None:
    """>> show_extra_headers

    Show any extra headers being added to each HTTP request.
    """
    info = log.info
    headers = browser.headers
    if headers:
        info('\nThe following HTTP headers are added to each request:\n')
        for key, value in headers.items():
            info('\t"%s" = "%s"', key, value)
        info('')
    else:
        info('** no extra HTTP headers **')


def clear_extra_headers() -> None:
    """>> clear_extra_headers

    Remove all user-defined HTTP headers.  See 'add_extra_header' and
    'show_extra_headers'.
    """
    browser.reset_headers()


default_options: Dict[str, Any] = dict(
    equiv_refresh_interval=2,
    readonly_controls_writeable=False,
    require_tidy=False,
    with_default_realm=False)

options = default_options.copy()  # the global options dictionary


def config(key: Optional[str] = None, value: Any = None) -> None:
    """>> config [<key> [<int value>]]

    Configure/report various options.  If no <value> is given, report
    the current key value; if no <key> given, report current settings.

    Options starting with "tidy_" will be used to configure HTML tidy.

    So far:

     * 'equiv_refresh_interval', default 2 -- time limit for HTTP-EQUIV=REFRESH
     * 'readonly_controls_writeable', default False -- all controls writeable
     * 'require_tidy', default False -- *require* that tidy be installed
     * 'with_default_realm', default False -- use a default realm for HTTP AUTH
    """
    info = log.info
    if key is None:
        keys = sorted(options)
        info('\nCurrent configuration:\n')
        for k in keys:
            info('\t%s : %s', k, options[k])
        info('')
    else:
        v = options.get(key)
        if v is None and not key.startswith('tidy_'):
            log.error("no such configuration key '%s'", key)
            info("valid keys are: %s", ', '.join(sorted(options)))
            raise TwillException("no such configuration key: '%s'" % (key,))
        elif value is None:
            info('\nkey %s: value %s\n', key, v)
        else:
            if isinstance(v, bool):
                value = utils.make_boolean(value)
            elif isinstance(v, int):
                value = utils.make_int(value)
            options[key] = value


def info() -> None:
    """>> info

    Report information on current page.
    """
    current_url = browser.url
    if current_url is None:
        log.warning("We're not on a page!")
        return

    content_type = browser.response_headers['content-type']
    is_html = content_type and content_type.split(';', 1)[0] == 'text/html'
    code = browser.code

    info = log.info
    info('\tURL: %s', current_url)
    info('\tHTTP code: %s', code)
    info('\tContent type: %s%s', content_type, ' (HTML)' if is_html else '')
    if is_html:
        title = browser.title
        info('\tPage title: %s', title)
        forms = browser.forms
        if len(forms):
            info('\tThis page contains %d form(s)', len(forms))
    info('')
