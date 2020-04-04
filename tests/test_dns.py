from . import mock_dns

from .utils import execute_script


def setup_module():
    mock_dns.activate()


def test(url):
    execute_script('test_dns.twill', initial_url=url)
