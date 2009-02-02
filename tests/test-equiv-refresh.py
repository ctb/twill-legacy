import os
import twilltestlib

def test():
    url = twilltestlib.get_url()
        
    twilltestlib.execute_twill_script('test-equiv-refresh.twill',
                                      initial_url=url)
