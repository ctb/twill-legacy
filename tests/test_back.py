from .utils import execute_script


def test(url: str):
    execute_script("test_back.twill", initial_url=url)
