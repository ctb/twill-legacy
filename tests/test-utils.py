import nose.tools

from twill import utils
from twill.errors import TwillException


class TestMakeBoolean:

    @nose.tools.raises(TwillException)
    def test_twill_exception(self):
        utils.make_boolean('no')
