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

    if len(shell.twillargs) < require:
        from twill.errors import TwillAssertionError
        given = len(shell.twillargs)
        raise TwillAssertionError(
            f"too few arguments; {given} rather than {require}")

    if shell.twillargs:
        for n, arg in enumerate(shell.twillargs, 1):
            global_dict[f"arg{n}"] = arg
        n = len(shell.twillargs)
        log.info("get_args: loaded %d args as $arg1..$arg%d.", n, n)
    else:
        log.info("no arguments to parse!")
