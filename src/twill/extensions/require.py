"""A simple set of extensions to manage post-load requirements for pages.

Commands:

   require       -- turn on post-load requirements; either 'success' or
                    'links_ok'.

   no_require    -- turn off requirements.

   skip_require  -- for the next page visit, skip requirements processing.

   flush_visited -- flush the list of already visited pages
                    (for links checking)
"""

from twill import browser, commands, log

__all__ = ["require", "skip_require", "flush_visited", "no_require"]

_requirements = []  # what requirements to satisfy


class Ignore:
    once: bool = False  # reset after each hook call
    always: bool = False  # never reset


def skip_require() -> None:
    """>> skip_require

    Skip the post-page-load requirements.
    """
    Ignore.once = True


def require(what: str) -> None:
    """>> require <what>

    After each page is loaded, require that 'what' be satisfied.  'what'
    can be:
      * 'success' -- HTTP return code is 200
      * 'links_ok' -- all the links on the page load OK (see 'check_links'
                      extension module)
    """
    # install the post-load hook function.
    # noinspection PyProtectedMember
    hooks = browser._post_load_hooks  # noqa: SLF001
    if _require_post_load_hook not in hooks:
        log.debug("INSTALLING POST-LOAD HOOK")
        hooks.append(_require_post_load_hook)

    # add the requirement.
    if what not in _requirements:
        log.debug("Adding requirement: %s", what)
        _requirements.append(what)


def no_require() -> None:
    """>> no_require

    Remove all post-load requirements.
    """
    # noinspection PyProtectedMember
    hooks = browser._post_load_hooks  # noqa: SLF001
    hooks = [fn for fn in hooks if fn != _require_post_load_hook]
    browser._post_load_hooks = hooks  # noqa: SLF001

    _requirements.clear()


def flush_visited() -> None:
    """>> flush_visited

    Flush the list of pages successfully visited already.
    """
    from .check_links import good_urls

    good_urls.clear()


def _require_post_load_hook(action: str, *_args, **_kwargs) -> None:
    """Post load hook function to be called after each page is loaded.

    See TwillBrowser._journey() for more information.
    """
    if action == "back":  # do nothing on a 'back'
        return

    if Ignore.once or Ignore.always:
        Ignore.once = False
        return

    for what in _requirements:
        if what == "success":
            log.debug("REQUIRING success")
            commands.code(200)

        elif what == "links_ok":
            from .check_links import check_links, good_urls

            Ignore.always = True
            log.debug("REQUIRING functioning links")
            log.debug("(already visited:)")
            log.debug("\n\t".join(sorted(good_urls)))

            try:
                check_links()
            finally:
                Ignore.always = False
