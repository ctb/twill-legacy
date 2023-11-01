from .utils import execute_script


def test(url: str):
    execute_script("test_info.twill", initial_url=url)
