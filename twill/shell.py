"""
A command-line interpreter for twill.

This is an implementation of a command-line interpreter based on the
'Cmd' class in the 'cmd' package of the default Python distribution.
"""

import os
import sys
import traceback

from cmd import Cmd
from io import TextIOWrapper
from optparse import OptionParser
from typing import Any, Callable, List, Optional

try:
    from readline import read_history_file, write_history_file  # type: ignore
except ImportError:
    read_history_file = write_history_file = None  # type: ignore
# noinspection PyCompatibility
from . import (
    commands, execute_file,
    log, log_levels, set_log_level, set_output,
    namespaces, parse, shutdown, __url__, __version__)
from .browser import browser
from .utils import gather_filenames, Singleton

__all__ = ['main']

python_version = sys.version.split(None, 1)[0]

version_info = f"""
twill version: {__version__}
Python Version: {python_version}

See {__url__} for more info.
"""


def make_cmd_fn(cmd: str) -> Callable[[str], None]:
    """Make a command function.

    Dynamically define a twill shell command function based on an imported
    function name.  (This is where the twill.commands functions actually
    get executed.)
    """

    def do_cmd(rest_of_line: str, cmd: str = cmd) -> None:
        global_dict, local_dict = namespaces.get_twill_glocals()

        args = []
        if rest_of_line.strip():
            try:
                args = parse.arguments.parseString(rest_of_line)[0]
                args = parse.process_args(args, global_dict, local_dict)
            except Exception as e:
                log.error('\nINPUT ERROR: %s\n', e)
                return

        try:
            parse.execute_command(
                cmd, args, global_dict, local_dict, '<shell>')
        except SystemExit:
            raise
        except Exception as e:
            log.error('\nERROR: %s\n', e)
            log.debug(traceback.format_exc())

    return do_cmd


def make_help_cmd(cmd: str, docstring: str) -> Callable[[str], None]:
    """Make a help command function.

    Dynamically define a twill shell help function for the given
    command/docstring.
    """
    def help_cmd(message: str = docstring, cmd: str = cmd) -> None:
        message = message.strip()
        width = 7 + len(cmd)
        for line in message.splitlines():
            w = len(line.rstrip())
            if w > width:
                width = w
        info = log.info
        info('\n%s' % ('=' * width,))
        info('\nHelp for command %s:\n', cmd)
        info(message)
        info('\n%s\n' % ('=' * width,))

    return help_cmd


def add_command(cmd: str, docstring: str) -> None:
    """Add a command with given docstring to the shell."""
    shell = get_command_shell()
    if shell:
        shell.add_command(cmd, docstring)


class TwillCommandLoop(Singleton, Cmd):
    """The command-line interpreter for twill commands.

    This is a Singleton object: you can't create more than one
    of shell at a time.

    Note: most of the do_ and help_ functions are dynamically created
    by the metaclass.
    """

    def __init__(
            self,  stdin: Optional[TextIOWrapper] = None,
            initial_url: Optional[str] = None,
            fail_on_unknown: bool = False) -> None:
        Cmd.__init__(self, stdin=stdin)

        self.use_rawinput = stdin is None

        # initialize a new local namespace.
        namespaces.new_local_dict()

        # import readline history, if available/possible.
        if read_history_file:
            try:
                read_history_file('.twill-history')
            except IOError:
                pass

        # fail on unknown commands? for test-shell, primarily.
        self.fail_on_unknown = fail_on_unknown

        # handle initial URL argument
        if initial_url:
            commands.go(initial_url)

        self._set_prompt()

        self.names: List[str] = []

        global_dict, local_dict = namespaces.get_twill_glocals()

        # add all of the commands from twill
        for command in parse.command_list:
            fn = global_dict.get(command)
            self.add_command(command, fn.__doc__)

    def add_command(self, command: str, docstring: str) -> None:
        """Add the given command into the lexicon of all commands."""
        do_name = f'do_{command}'
        do_cmd = make_cmd_fn(command)
        setattr(self, do_name, do_cmd)

        if docstring:
            help_cmd = make_help_cmd(command, docstring)
            help_name = f'help_{command}'
            setattr(self, help_name, help_cmd)

        self.names.append(do_name)

    def get_names(self) -> List[str]:
        """Return the list of commands."""
        return self.names

    def complete_form_value(
            self, text: str, line: str, _begin: int, _end: int) -> List[str]:
        """Command arg completion for the form_value command.

        The twill command has the following syntax:

        form_value <form_name> <field_name> <value>
        """
        cmd, args = parse.parse_command(line + '.', {}, {})
        place = len(args)
        if place == 1:
            return self.provide_form_name(text)
        if place == 2:
            form_name = args[0]
            return self.provide_field_name(form_name, text)
        return []

    complete_fv = complete_form_value  # alias

    @staticmethod
    def provide_form_name(prefix: str) -> List[str]:
        """Provide the list of form names on the given page."""
        names = []
        forms = browser.forms
        for form in forms:
            form_id = form.attrib.get('id')
            if form_id and form_id.startswith(prefix):
                names.append(form_id)
                continue
            name = form.attrib.get('name')
            if name and name.startswith(prefix):
                names.append(name)
        return names

    @staticmethod
    def provide_field_name(form_name: str, prefix: str) -> List[str]:
        """Provide the list of fields for the given form_name or number."""
        names = []
        form = browser.form(form_name)
        if form is not None:
            for field in form.inputs:
                field_id = field.attrib.get('id')
                if field_id and field_id.startswith(prefix):
                    names.append(field_id)
                    continue
                name = field.name
                if name and name.startswith(prefix):
                    names.append(name)
        return names

    def _set_prompt(self) -> None:
        """"Set the prompt to the current page."""
        url = browser.url
        if url is None:
            url = " *empty page* "
        self.prompt = f"current page: {url}\n>> "

    def precmd(self, line: str) -> str:
        """Run before each command; save."""
        return line

    def postcmd(self, stop: bool, line: str) -> bool:
        """"Run after each command; set prompt."""
        self._set_prompt()
        return stop

    def default(self, line: str) -> None:
        """"Called when an unknown command is executed."""

        # empty lines ==> emptyline(); here we just want to remove
        # leading whitespace.
        line = line.strip()

        # look for command
        global_dict, local_dict = namespaces.get_twill_glocals()
        cmd, args = parse.parse_command(line, global_dict, local_dict)

        # ignore comments & empty stuff
        if cmd is None:
            return

        try:
            parse.execute_command(
                cmd, args, global_dict, local_dict, '<shell>')
        except SystemExit:
            raise
        except Exception as e:
            log.error('\nERROR: %s\n', e)
            if self.fail_on_unknown:
                raise

    def emptyline(self) -> Any:
        """Handle empty lines (by ignoring them)."""
        pass

    @staticmethod
    def do_EOF(*_args: str) -> None:
        """Exit on CTRL-D"""
        if write_history_file:
            write_history_file('.twill-history')
        raise SystemExit()

    @staticmethod
    def help_help() -> None:
        """Show help for the help command."""
        log.info("\nWhat do YOU think the command 'help' does?!?\n")

    @staticmethod
    def do_version(*_args: str) -> None:
        """Show the version number of twill."""
        log.info(version_info)

    @staticmethod
    def help_version() -> None:
        """Show help for the version command."""
        log.info("\nPrint version information.\n")

    def do_exit(self, *_args: str) -> None:
        """Exit the twill shell."""
        raise SystemExit()

    @staticmethod
    def help_exit() -> None:
        """Show help for the exit command."""
        log.info("\nExit twill.\n")

    do_quit = do_exit
    help_quit = help_exit


def get_command_shell() -> Optional[TwillCommandLoop]:
    """Get the command shell."""
    return getattr(TwillCommandLoop, '__it__', None)


twill_args: List[str] = []  # contains sys.argv *after* last '--'
interactive = False  # 'True' if interacting with user


def main():
    global twill_args, interactive

    # show the shorthand name for usage
    if sys.argv[0].endswith('-script.py'):
        sys.argv[0] = sys.argv[0].rsplit('-', 1)[0]

    # make sure that the current working directory is in the path
    if '' not in sys.path:
        sys.path.append('')

    parser = OptionParser()
    add = parser.add_option

    add('-d', '--dump-html', action='store', dest='dumpfile',
        help="dump HTML to this file on error")
    add('-f', '--fail', action='store_true', dest='fail',
        help='fail exit on first file to fail')
    add('-i', '--interactive', action='store_true', dest='interactive',
        help='drop into an interactive shell (after running files)')
    add('-l', '--loglevel', nargs=1, action='store', dest='loglevel',
        help='set the logging level')
    add('-n', '--never-fail', action='store_true', dest='never_fail',
        help='continue executing scripts past errors')
    add('-o', '--output', nargs=1, action='store', dest='outfile',
        help="print log to output file")
    add('-q', '--quiet', action='store_true', dest='quiet',
        help='do not show normal output')
    add('-u', '--url', nargs=1, action='store', dest='url',
        help='start at the given URL before each script')
    add('-v', '--version', action='store_true', dest='show_version',
        help='show version information and exit')
    add('-w', '--show-error-in-browser', action='store_true',
        dest='show_browser', help="show dumped HTML in a web browser ")

    # parse arguments
    sys_args = sys.argv[1:]
    if '--' in sys_args:
        for last in range(len(sys_args) - 1, -1, -1):
            if sys_args[last] == '--':
                twill_args = sys_args[last + 1:]
                sys_args = sys_args[:last]
                break

    options, args = parser.parse_args(sys_args)

    if options.show_version:
        log.info(version_info)
        sys.exit(0)

    quiet = options.quiet
    show_browser = options.show_browser
    dump_file = options.dumpfile
    out_file = options.outfile
    log_level = options.loglevel
    interactive = options.interactive or not args

    if out_file:
        out_file = out_file.lstrip('=').lstrip() or None
        if out_file == '-':
            out_file = None

    if interactive and (quiet or out_file or dump_file or show_browser):
        sys.exit("Interactive mode is incompatible with -q, -o, -d and -w")

    if options.show_browser and (not dump_file or dump_file == '-'):
        sys.exit("Please also specify a dump file with -d")

    if out_file:
        try:
            out_file = open(out_file, 'w')
        except IOError as e:
            sys.exit(f"Invalid output file '{out_file}': {e}")

    if log_level:
        log_level = log_level.lstrip('=').lstrip() or None
        if log_level.upper() not in log_levels:
            log_level_names = ', '.join(sorted(log_levels))
            sys.exit(f"Valid log levels are: {log_level_names}")
        set_log_level(log_level)

    if quiet:
        out_file = open(os.devnull, 'w')

    set_output(out_file)

    # first find and run any scripts put on the command line

    failed = False
    if args:
        success = []
        failure = []

        filenames = gather_filenames(args)
        dump = None

        for filename in filenames:
            try:
                interactive = False
                execute_file(filename, initial_url=options.url,
                             never_fail=options.never_fail)
                success.append(filename)
            except Exception as e:
                if dump_file:
                    dump = browser.dump
                if options.fail:
                    raise
                else:
                    if browser.first_error:
                        log.error('\nFirst error: %s', browser.first_error)
                    log.error('\n*** ERROR: %s', e)
                    log.debug(traceback.format_exc())
                    failure.append(filename)

        log.info('--')
        if dump:
            if dump_file == '-':
                log.info('HTML when error was encountered:\n\n%s\n--',
                         dump.strip())
            else:
                try:
                    with open(dump_file, 'wb') as f:
                        f.write(dump)
                except IOError as e:
                    log.error('Could not dump to %s: %s\n', dump_file, e)
                else:
                    log.info('HTML has been dumped to %s\n', dump_file)

        log.info('%d of %d files SUCCEEDED.',
                 len(success), len(success) + len(failure))
        if len(failure):
            log.error('Failed:\n\t%s', '\n\t'.join(failure))
            failed = True

        if dump and show_browser:
            import webbrowser

            url = 'file:///' + os.path.abspath(dump_file).replace(os.sep, '/')
            log.debug('Running web browser on %s', url)
            webbrowser.open(url)

    # if no scripts to run or -i is set, drop into an interactive shell

    if interactive:
        welcome_msg = "" if args else "\n -= Welcome to twill =-\n"

        shell = TwillCommandLoop(initial_url=options.url)

        while True:
            try:
                shell.cmdloop(welcome_msg)
            except KeyboardInterrupt:
                print()
                break
            except SystemExit:
                raise

            welcome_msg = ""

    shutdown()

    if failed:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
