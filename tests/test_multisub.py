from .utils import execute_script


def test(url: str):
    execute_script("test_multisub.twill", initial_url=url)
