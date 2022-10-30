from pytest import raises

from twill import commands
from twill.errors import TwillException

from .utils import execute_script


def test(url):
    commands.show()
    commands.show('html')
    commands.show('links')
    with raises(TwillException, match='Cannot show "nonsense".'):
        commands.show('nonsense')

    execute_script('test_show.twill', initial_url=url)
