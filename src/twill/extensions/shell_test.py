"""Used in test_shell, to test default command execution and extensions."""

from twill.errors import TwillAssertionError

__all__ = ["set_flag", "unset_flag", "assert_flag_set", "assert_flag_unset"]


class Flag:
    """Global flag value."""

    value: bool = False


def set_flag() -> None:
    """Set the flag."""
    Flag.value = True


def unset_flag() -> None:
    """Unset the flag."""
    Flag.value = False


def assert_flag_set() -> None:
    """Assert that the flag has been set."""
    if not Flag.value:
        raise TwillAssertionError("The flag has not been set")


def assert_flag_unset() -> None:
    """Assert that the flag has not been set."""
    if Flag.value:
        raise TwillAssertionError("The flag has been set")
