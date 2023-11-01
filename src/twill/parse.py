"""Code parsing and evaluation for the twill mini-language."""

import re
import sys
from contextlib import nullcontext
from io import StringIO
from typing import Any, Callable, Dict, List, Optional, Sequence, TextIO, Tuple

from pyparsing import (
    CharsNotIn,
    Combine,
    Group,
    Literal,
    Opt,
    ParseException,
    ParseResults,
    Word,
    ZeroOrMore,
    pyparsing_unicode,
    remove_quotes,
    rest_of_line,
)

# noinspection PyCompatibility
from . import commands, log, namespaces
from .browser import browser
from .errors import TwillNameError

# pyparsing stuff

# allow characters in full 8-bit range
char_range = pyparsing_unicode.Latin1
alphas, alphanums = char_range.alphas, char_range.alphanums
printables = char_range.printables

# basically, a valid Python identifier:
command_word = Word(alphas + "_", alphanums + "_")
command = command_word.set_results_name("command")
command.set_name("command")

# arguments to it.

# we need to reimplement all this junk from pyparsing because pcre's
# idea of escapable characters contains a lot more than the C-like
# thing pyparsing implements
_bslash = "\\"
_sgl_quote = Literal("'")
_dbl_quote = Literal('"')
_escapables = printables
_escaped_char = Word(_bslash, _escapables, exact=2)
dbl_quoted_string = (
    Combine(
        _dbl_quote
        + ZeroOrMore(CharsNotIn('\\"\n\r') | _escaped_char | '""')
        + _dbl_quote
    )
    .streamline()
    .set_name("string enclosed in double quotes")
)
sgl_quoted_string = (
    Combine(
        _sgl_quote
        + ZeroOrMore(CharsNotIn("\\'\n\r") | _escaped_char | "''")
        + _sgl_quote
    )
    .streamline()
    .set_name("string enclosed in single quotes")
)
quoted_arg = dbl_quoted_string | sgl_quoted_string
quoted_arg.set_parse_action(remove_quotes)
quoted_arg.set_name("quoted_arg")

plain_arg_chars = printables.replace("#", "").replace('"', "").replace("'", "")
plain_arg = Word(plain_arg_chars)
plain_arg.set_name("plain_arg")

arguments_group = Group(ZeroOrMore(quoted_arg | plain_arg))
arguments = arguments_group.set_results_name("arguments")
arguments.set_name("arguments")

# comment line.
comment = Literal("#") + rest_of_line
comment = comment.suppress()
comment.set_name("comment")

full_command = comment | (command + arguments + Opt(comment))
full_command.set_name("full_command")


command_list: List[str] = []  # filled in by namespaces.init_global_dict().


def process_args(
    args: Sequence[str],
    globals_dict: Dict[str, Any],
    locals_dict: Dict[str, Any],
) -> List[str]:
    """Process string arguments.

    Take a list of string arguments parsed via pyparsing and evaluate
    the special variables ('__*').

    Return a new list.
    """
    new_args: List[str] = []
    for arg in args:
        # __variable substitution
        if arg.startswith("__"):
            try:
                val = eval(arg, globals_dict, locals_dict)
            except NameError:  # not in dictionary; don't interpret
                val = arg

            log.info("VAL IS %s FOR %s", val, arg)

            if isinstance(val, str):
                new_args.append(val)
            else:
                new_args.extend(val)

        # $variable substitution
        elif arg.startswith("$") and not arg.startswith("${"):
            try:
                val = str(eval(arg[1:], globals_dict, locals_dict))
            except NameError:  # not in dictionary; don't interpret
                val = arg
            new_args.append(val)
        else:
            new_args.append(
                variable_substitution(arg, globals_dict, locals_dict)
            )

    return [arg.replace("\\n", "\n") for arg in new_args]


def execute_command(
    cmd: str,
    args: Sequence[str],
    globals_dict: Dict[str, Any],
    locals_dict: Dict[str, Any],
    cmd_info: str,
) -> None:
    """Actually execute the command.

    Side effects:
     - __args__ is set to the arguments
     - __cmd__ is set to the command, and
     - __url__ is set to the browser URL.
    """
    # execute command
    locals_dict["__cmd__"] = cmd
    locals_dict["__args__"] = args
    if cmd not in command_list:
        raise TwillNameError(f"unknown twill command: '{cmd}'")

    eval_str = f"{cmd}(*__args__)"

    # compile the code object so that we can get 'cmd_info' into the
    # error tracebacks
    code_obj = compile(eval_str, cmd_info, "eval")

    # evaluate the code object in the appropriate dictionary
    result = eval(code_obj, globals_dict, locals_dict)

    # set __url__
    locals_dict["__url__"] = browser.url

    return result


_log_commands: Callable = log.debug  # type: ignore[has-type]


def parse_command(
    line: str,
    globals_dict: Dict[str, Any],
    locals_dict: Dict[str, Any],
) -> Tuple[Optional[str], Optional[List[str]]]:
    """Parse command.

    Returns a tuple with the command and its arguments.
    """
    try:
        results: Optional[ParseResults] = full_command.parse_string(line)
    except ParseException as e:
        log.error("PARSE ERROR: %s", e)
        results = None
    if results:
        _log_commands("twill: executing cmd '%s'", line.strip())
        args = process_args(
            results.arguments.as_list(), globals_dict, locals_dict
        )
        return results.command, args
    return None, None  # e.g. a comment


def execute_string(buf: str, **kw) -> None:
    """Execute commands from a string buffer."""
    fp = StringIO(buf)

    kw["source"] = ["<string buffer>"]
    if "no_reset" not in kw:
        kw["no_reset"] = True

    _execute_script(fp, **kw)


def execute_file(filename: str, **kw) -> None:
    """Execute commands from a file."""
    with (
        nullcontext(sys.stdin)  # type: ignore[attr-defined]
        if filename == "-"
        else open(filename, encoding="utf-8")
    ) as inp:
        log.info("\n>> Running twill file %s", filename)

        kw["source"] = filename
        _execute_script(inp, **kw)


def _execute_script(inp: TextIO, **kw) -> None:
    """Execute lines taken from a file-like iterator."""
    # initialize new local dictionary and get global and current local
    namespaces.new_local_dict()
    globals_dict, locals_dict = namespaces.get_twill_glocals()

    locals_dict["__url__"] = browser.url

    # reset browser
    if not kw.get("no_reset"):
        commands.reset_browser()

    # go to a specific URL?
    init_url = kw.get("initial_url")
    if init_url:
        commands.go(init_url)
        locals_dict["__url__"] = browser.url

    # should we catch exceptions on failure?
    catch_errors = kw.get("never_fail")

    # source_info stuff
    source_info = kw.get("source", "<input>")

    try:
        for line_no, line_raw in enumerate(inp, 1):
            line = line_raw.strip()
            if not line:  # skip empty lines
                continue

            cmd_info = f"{source_info}:{line_no}"
            log.info("AT LINE: %s", cmd_info)

            cmd, args = parse_command(line, globals_dict, locals_dict)
            if cmd is None:
                continue

            try:
                execute_command(cmd, args, globals_dict, locals_dict, cmd_info)
            except SystemExit:
                # abort script execution if a SystemExit is raised
                return
            except Exception as error:  # noqa: BLE001
                error_type = error.__class__.__name__ or "Error"
                error_context = (
                    f"{error_type} raised on line {line_no}"
                    f"of '{source_info}'"
                )
                if line:
                    error_context += f" while executing\n>> {line}"
                if not browser.first_error:
                    browser.first_error = error_context
                log.error("\nOops! %s", error_context)
                error_msg = str(error).strip()
                log.error("\nError: %s", error_msg)
                if not catch_errors:
                    raise

    finally:
        cleanups = locals_dict.get("__cleanups__")
        if cleanups:
            first_error, result = browser.first_error, browser.result
            for filename in reversed(cleanups):
                log.info("\n>> Running twill cleanup file %s", filename)
                try:
                    with open(filename, encoding="utf-8") as inp:
                        _execute_script(inp, source=filename, no_reset=True)
                except Exception as error:  # noqa: BLE001
                    log.error(
                        ">> Cannot run cleanup file %s: %s", filename, error
                    )
            browser.reset()
            browser.first_error, browser.result = first_error, result
        namespaces.pop_local_dict()


def log_commands(flag: bool) -> bool:  # noqa: FBT001
    """Turn printing of commands as they are executed on or off."""
    global _log_commands  # noqa: PLW0603
    old_flag = _log_commands is log.info
    _log_commands = log.info if flag else log.debug
    return old_flag


_re_variable = re.compile(r"\${(.*?)}")


def variable_substitution(
    raw_str: str, globals_dict: Dict[str, Any], locals_dict: Dict[str, Any]
) -> str:
    """Substitute the variables in the given string."""
    parts: List[str] = []
    append = parts.append
    position = 0
    for match in _re_variable.finditer(raw_str):
        append(raw_str[position : match.start()])
        try:
            variable = match.group(1)
            value = eval(variable, globals_dict, locals_dict)
            append(str(value))
        except NameError:
            append(match.group())
        position = match.end()
    append(raw_str[position:])
    return "".join(parts)
