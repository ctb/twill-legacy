from .utils import execute_script


def test(url):
    execute_script('test_global_form.twill', initial_url=url)
