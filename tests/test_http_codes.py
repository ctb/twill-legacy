from .utils import execute_script


def test(url: str):
    execute_script("test_http_codes.twill", initial_url=url)
