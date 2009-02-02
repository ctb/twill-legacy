import os
import twilltestlib

def test():
    url = twilltestlib.get_url()

    twilltestlib.execute_twill_script('test-http-codes.twill', initial_url=url)
