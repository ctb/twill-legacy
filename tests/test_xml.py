from .utils import execute_script


def test(url):
    execute_script('test_xml.twill', initial_url=url)
