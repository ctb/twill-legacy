import os
import twilltestlib

def test():
    url = twilltestlib.get_url()
        
    twilltestlib.execute_twill_script('test-find.twill', initial_url=url)
