from .utils import execute_script


def test(url: str):
    execute_script("test_headers.twill", initial_url=url)
