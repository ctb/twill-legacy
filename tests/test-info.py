import twilltestlib

def test():
    url = twilltestlib.get_url()
    twilltestlib.execute_twill_script('test-info.twill', initial_url=url)
