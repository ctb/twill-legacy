import twilltestlib

def test():
    url = twilltestlib.get_url()
        
    twilltestlib.execute_twill_script('test-back.twill', initial_url=url)
    
