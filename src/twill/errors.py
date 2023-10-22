"""The twill exceptions."""


class TwillException(Exception):  # noqa: N818
    """General twill exception."""


class TwillAssertionError(TwillException):
    """AssertionError to raise upon failure of some twill command."""


class TwillNameError(TwillException):
    """Error to raise when an unknown command is called."""
