from .utils import execute_script


def test(url: str):
    execute_script("test_equiv_refresh.twill", initial_url=url)
