import twill.commands
import twilltestlib

def test():
    url = twilltestlib.get_url()

    twilltestlib.execute_twill_script('test-headers.twill', initial_url=url)
