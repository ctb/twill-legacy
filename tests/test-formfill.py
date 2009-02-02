import twilltestlib

def test():
    """
    Test the 'formfill' extension stuff.
    """
    url = twilltestlib.get_url()
    twilltestlib.execute_twill_script('test-formfill.twill', initial_url=url)
