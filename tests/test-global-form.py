import twill, twilltestlib

def test():
    url = twilltestlib.get_url()

    twilltestlib.execute_twill_script('test-global-form.twill',
                                      initial_url=url)
