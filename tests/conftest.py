import pytest

import twilltestlib
import twilltestserver


@pytest.fixture
def url(request, scope='session'):
    twilltestlib.cd_testdir()
    twilltestlib.run_server(twilltestserver.create_publisher)

    url = twilltestlib.get_url()

    from twill.commands import go, find
    try:
        go(url)
        find("These are the twill tests")
    except:
        raise Exception("""
***
Hello! The twill test server is not running or cannot be reached;
please free port 8080 (or set TWILL_TEST_PORT to something else),
and clear your proxy settings too!
***
""")

    def stop():
        twilltestlib.kill_server()
        twilltestlib.pop_testdir()

    request.addfinalizer(stop)

    return url