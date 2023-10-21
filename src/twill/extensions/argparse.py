"""
Extension functions for parsing sys.argv.

Commands:

   get_args -- load all command-line arguments after the last --
      into $arg1...$argN.
"""

from twill import log, namespaces, shell

__all__ = ['get_args']


def get_args(require=0):
    """>> get_args [<require>]

    Load the command line arguments after the last '--' into $arg1...$argN,
    optionally requiring at least 'require' such arguments.
    """
    global_dict, local_dict = namespaces.get_twill_glocals()

    require = int(require)

    if len(shell.twill_args) < require:
        from twill.errors import TwillAssertionError
        given = len(shell.twill_args)
        raise TwillAssertionError(
            f"too few arguments; {given} rather than {require}")

    if shell.twill_args:
        for n, arg in enumerate(shell.twill_args, 1):
            global_dict[f"arg{n}"] = arg
        n = len(shell.twill_args)
        log.info("get_args: loaded %d args as $arg1..$arg%d.", n, n)
    else:
        log.info("no arguments to parse!")
