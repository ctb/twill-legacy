from .utils import execute_script


def test(url):
    execute_script('test_variables.twill', initial_url=url)
