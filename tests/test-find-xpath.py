import os
import twilltestlib

def test():
    url = twilltestlib.get_url()
        
    twilltestlib.execute_twill_script('test-find-xpath.twill', initial_url=url)
