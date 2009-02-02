import twilltestlib
import twill
from twill import namespaces, commands
from twill.errors import TwillAssertionError
from _mechanize_dist import BrowserStateError, ClientForm

def test():
    url = twilltestlib.get_url()
            
    # test empty page get_title
    namespaces.new_local_dict()
    twill.commands.reset_browser()
    browser = twill.get_browser()
    try:
        browser.get_title()
        assert 0, "should never get here"
    except BrowserStateError:
        pass

    ### now test a few special cases
    
    commands.go(url)
    commands.go('/login')
    commands.showforms()

    # test no matching forms
    try:
        commands.fv('2', 'submit', '1')
        assert 0
    except TwillAssertionError:
        pass

    # test regexp match
    commands.fv('1', '.*you', '1')


    # test ambiguous match to value
    commands.go('/testform')
    commands.fv('1', 'selecttest', 'val')
    commands.fv('1', 'selecttest', 'value1')
    commands.fv('1', 'selecttest', 'selvalue1')
    commands.formclear('1')
    try:
        commands.fv('1', 'selecttest', 'value')
        assert 0
    except ClientForm.ItemNotFoundError:
        pass

    # test ambiguous match to name
    commands.go('/testform')
    try:
        commands.fv('1', 'item_', 'value')
        assert 0
    except Exception:
        pass

    try:
        commands.formfile('1', 'selecttest', 'null')
        assert 0
    except Exception:
        pass

    commands.go('http://www.google.com/')
    browser.get_title()

    # test the twill script.
    twilltestlib.execute_twill_script('test-form.twill', initial_url=url)
