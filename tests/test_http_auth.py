from .utils import execute_script


def test(url: str):
    execute_script("test_http_auth.twill", initial_url=url)
