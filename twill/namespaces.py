"""Global and local dictionaries, and initialization/utility functions."""

global_dict = {}  # the global dictionary


def init_global_dict():
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


def new_local_dict():
    """Initialize a new local dictionary & push it onto the stack."""
    d = {}
    _local_dict_stack.append(d)
    return d


def pop_local_dict():
    """Get rid of the current local dictionary."""
    return _local_dict_stack.pop()


def get_twill_glocals():
    """Return both global and current local dictionary."""
    global global_dict, _local_dict_stack
    assert global_dict is not None, "must initialize global namespace first!"
    if not _local_dict_stack:
        new_local_dict()
    return global_dict, _local_dict_stack[-1]
