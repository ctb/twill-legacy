import pytest

from . import util


@pytest.fixture(scope='session')
def url(request):
    util.cd_test_dir()
    util.start_server()

    url = util.get_url()

    from twill import set_output
    from twill.commands import go, find
    set_output()
    try:
        go(url)
        find("These are the twill tests")
    except Exception:
        raise RuntimeError("""
***
Hello! The twill test server is not running or cannot be reached;
please free port 8080 (or set TWILL_TEST_PORT to something else),
and clear your proxy settings too!
***
""")

    def stop():
        util.stop_server()
        util.pop_test_dir()

    request.addfinalizer(stop)

    return url