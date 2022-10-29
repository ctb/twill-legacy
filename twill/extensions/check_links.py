"""
Extension functions to check all of the links on a page.

Usage:

   check_links [ <pattern> ]

Make sure that all the HTTP links on the current page can be visited
successfully.  If 'pattern' is given, check only URLs that match that
regular expression.

If option 'check_links.only_collect_bad_links' is on, then all bad
links are silently collected across all calls to check_links.  The
function 'report_bad_links' can then be used to report all the links,
together with their referring pages.
"""

import re

from typing import Dict, List, Set

from twill import browser, commands, log, utils
from twill.errors import TwillAssertionError

__all__ = ['check_links', 'report_bad_links', 'good_urls', 'bad_urls']

# first, set up config options & persistent 'bad links' memory...
if commands.options.get('check_links.only_collection_bad_links') is None:
    commands.options['check_links.only_collect_bad_links'] = False

good_urls: Set[str] = set()
bad_urls: Dict[str, Set[str]] = dict()


def check_links(pattern=''):
    """>> check_links [<pattern>]

    Make sure that all the HTTP links on the current page can be visited
    with an HTTP response 200 (success).  If 'pattern' is given, interpret
    it as a regular expression that link URLs must contain in order to be
    tested, e.g.

        check_links https://.*\\.google\\.com

    would check only links to google URLs.  Note that because 'follow'
    is used to visit the pages, the referrer URL is properly set on the
    visit.
    """
    debug, info = log.debug, log.info

    debug('in check_links')

    # compile the regex
    regex = re.compile(pattern) if pattern else None

    # iterate over all links, collecting those that match
    #
    # note that in the case of duplicate URLs, only one of the
    # links is actually followed!

    collected_urls: Set[str] = set()

    links = browser.links
    if not links:
        debug("no links to check!?")
        return

    for link in links:
        url = link.url
        url = url.split('#', 1)[0]  # get rid of subpage pointers

        # noinspection HttpUrlsUsage
        if not url.startswith(('http://', 'https://')):
            debug("url '%s' is not an HTTP link; ignoring", url)
            continue

        if regex:
            if regex.search(url):
                collected_urls.add(url)
                debug("Gathered URL %s -- matched pattern", url)
            else:
                debug("URL %s doesn't match pattern", url)
        else:
            collected_urls.add(url)
            debug("Gathered URL %s.", url)

    # now, for each unique and unchecked URL, follow the link

    failed: List[str] = []
    for url in sorted(collected_urls):
        debug("Checking %s", url)
        if url in good_urls:
            debug('... already known as good')
        elif url in bad_urls:
            debug('... already collected as broken')
        else:
            try:
                browser.follow_link(url)
            except Exception:  # count as failure
                code = 404
            else:
                code = browser.code
                browser.back()
            if code == 200:
                debug('...success!')
                good_urls.add(url)
            else:
                debug('...failure!')
                failed.append(url)

    if commands.options['check_links.only_collect_bad_links']:
        for url in failed:
            referrers = bad_urls.setdefault(url, set())
            info('*** %s', browser.url)
            referrers.add(browser.url)
    elif failed:
        info('\nCould not follow %d links:\n', len(failed))
        for url in failed:
            info('* %s', url)
        raise TwillAssertionError("broken links on page")
    else:
        info('\nNo broken links were detected.\n')


def report_bad_links(fail_if_exist='true', flush_bad_links='true'):
    """>> report_bad_links [<fail-if-exist> [<flush-bad-links>]]

    Report all the links collected across check_links runs (collected
    if and only if the config option check_links.only_collect_bad_links
    is set).

    If <fail-if-exist> is false (true by default) then the command will
    fail after reporting any bad links.

    If <flush-bad-links> is false (true by default) then the list of
    bad links will be retained across the function call.
    """
    fail_if_exist = utils.make_boolean(fail_if_exist)
    flush_bad_links = utils.make_boolean(flush_bad_links)

    info = log.info
    if not bad_urls:
        info('\nNo bad links to report.\n')
        return

    info('\nCould not follow %d links', len(bad_urls))
    for url in sorted(bad_urls):
        referrers = sorted(bad_urls[url])
        info("\tlink '%s' (occurs on: %s)", url, ','.join(referrers))

    if flush_bad_links:
        bad_urls.clear()

    if fail_if_exist:
        raise TwillAssertionError("broken links encountered")
