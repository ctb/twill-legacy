"""Global and local dictionaries, and initialization/utility functions."""

from typing import Any, Dict, Tuple

from . import errors

global_dict: Dict[str, Any] = {}  # the global dictionary


def init_global_dict() -> None:
    """Initialize the global dictionary with twill commands.

    This must be done after all the other modules are loaded, so that all
    the commands are already defined.
    """
    # noinspection PyCompatibility
    from . import commands, parse

    cmd_list = commands.__all__
    global_dict.update((cmd, getattr(commands, cmd)) for cmd in cmd_list)
    parse.command_list.extend(cmd_list)


_local_dict_stack = []  # local dictionaries


def new_local_dict() -> Dict[str, Any]:
    """Initialize a new local dictionary and push it onto the stack."""
    local_dict: Dict[str, Any] = {}
    _local_dict_stack.append(local_dict)
    return local_dict


def pop_local_dict() -> Dict[str, Any]:
    """Get rid of the current local dictionary."""
    return _local_dict_stack.pop()


def get_twill_glocals() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Return both global and current local dictionary."""
    if global_dict is None:
        raise errors.TwillException("Must initialize global namespace first!")
    if not _local_dict_stack:
        new_local_dict()
    return global_dict, _local_dict_stack[-1]
