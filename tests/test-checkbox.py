import twilltestlib
import twill
from twill import namespaces, commands
from twill.errors import TwillAssertionError
from _mechanize_dist import BrowserStateError, ClientForm

def setup_module():
    global url
    url = twilltestlib.get_url()

def test_select_multiple():
    namespaces.new_local_dict()
    twill.commands.reset_browser()
    browser = twill.get_browser()
    try:
        browser.get_title()
        assert 0, "should never get here"
    except BrowserStateError:
        pass

    commands.go(url)
    commands.go('/test_checkboxes')

    commands.fv('1', 'checkboxtest', 'one')
    commands.fv('1', 'checkboxtest', 'two')
    commands.fv('1', 'checkboxtest', 'three')

    commands.fv('1', 'checkboxtest', '-one')
    commands.fv('1', 'checkboxtest', '-two')
    commands.fv('1', 'checkboxtest', '-three')

    commands.submit()
    assert not 'CHECKBOXTEST' in browser.get_html()

    commands.fv('1', 'checkboxtest', '+one')
    commands.fv('1', 'checkboxtest', '+two')
    commands.fv('1', 'checkboxtest', '+three')
    
    commands.submit()
    assert 'CHECKBOXTEST: ==one,two,three==' in browser.get_html()

    commands.fv('1', 'checkboxtest', '-one')
    commands.fv('1', 'checkboxtest', '-two')
    commands.fv('1', 'checkboxtest', '-three')

    commands.submit()
    assert not 'CHECKBOXTEST' in browser.get_html()

def test_select_single():
    namespaces.new_local_dict()
    twill.commands.reset_browser()
    browser = twill.get_browser()
    try:
        browser.get_title()
        assert 0, "should never get here"
    except BrowserStateError:
        pass

    commands.go(url)
    commands.go('/test_checkboxes')

    for x in ('1', '0', 'True', 'False'):
        try:
            commands.fv('1', 'checkboxtest', x)
            assert False, ("Should not be able to use a bool style for when "
                    "there are multiple checkboxes")
        except:
            pass


