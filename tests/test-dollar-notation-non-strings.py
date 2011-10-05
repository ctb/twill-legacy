import os
import twilltestlib

def test():
    url = twilltestlib.get_url()
        
    twilltestlib.execute_twill_script('test-dollar-notation-non-strings.twill', initial_url=url)
