from .utils import execute_script


def test(url):
    execute_script('test_back.twill', initial_url=url)
