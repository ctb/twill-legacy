"""
Extension functions to check all of the links on a page.

Usage:

   check_links [ <pattern> ]

Make sure that all of the HTTP links on the current page can be visited
successfully.  If 'pattern' is given, check only URLs that match that
regular expression.

If option 'check_links.only_collect_bad_links' is on, then all bad
links are silently collected across all calls to check_links.  The
function 'report_bad_links' can then be used to report all of the links,
together with their referring pages.
"""

import re

from twill import commands, log
from twill.errors import TwillAssertionError

__all__ = ['check_links', 'report_bad_links']

### first, set up config options & persistent 'bad links' memory...

if commands._options.get('check_links.only_collection_bad_links') is None:
    commands._options['check_links.only_collect_bad_links'] = False

bad_links_dict = {}

#
# main function: 'check_links'
#

def check_links(pattern = '', visited={}):
    """
    >> check_links [ <pattern> ]

    Make sure that all of the HTTP links on the current page can be visited
    with an HTTP response 200 (success).  If 'pattern' is given, interpret
    it as a regular expression that link URLs must contain in order to be
    tested, e.g.

        check_links http://.*\.google\.com

    would check only links to google URLs.  Note that because 'follow'
    is used to visit the pages, the referrer URL is properly set on the
    visit.
    """
    log.debug('in check_links')
    
    browser = commands.browser

    #
    # compile the regexp
    #
    
    regexp = None
    if pattern:
        regexp = re.compile(pattern)

    #
    # iterate over all links, collecting those that match.
    #
    # note that in the case of duplicate URLs, only one of the
    # links is actually followed!
    #

    collected_urls = {}

    links = list(browser._browser.links())
    if not links:
        log.debug("no links to check!?")
        return
        
    for link in links:
        url = link.absolute_url
        url = url.split('#', 1)[0]      # get rid of subpage pointers

        if not (url.startswith('http://') or url.startswith('https://')):
            log.debug("url '%s' is not an HTTP link; ignoring", url)
            continue

        if regexp:
            if regexp.search(url):
                collected_urls[url] = link
                log.debug("Gathered URL %s -- matched regexp", url)
            else:
                log.debug("URL %s doesn't match regexp", url)
        else:
            collected_urls[url] = link
            log.debug("Gathered URL %s.", url)

    #
    # now, for each unique URL, follow the link. Trap ALL exceptions
    # as failures.
    #

    failed = []
    for link in collected_urls.values():
        went = False
        try:
            log.debug("Trying %s", link.absolute_url)
                
            if link.absolute_url not in visited:
                went = True
                browser.follow_link(link)
                
                code = browser.get_code()
                assert code == 200

                visited[link.absolute_url] = 1
                
                log.debug('...success!')
            else:
                log.debug('(already visited successfully)')
        except Exception:
            failed.append(link.absolute_url)
            log.debug('...failure!')

        if went:
            browser.back()

    info = log.info
    if failed:
        if commands._options['check_links.only_collect_bad_links']:
            for l in failed:
                refering_pages = bad_links_dict.get(l, [])
                info('*** %s', browser.get_url())
                refering_pages.append(browser.get_url())
                bad_links_dict[l] = refering_pages
        else:
            info('\nCould not follow %d links', len(failed))
            info('\t%s\n', '\n\t'.join(failed))
            raise TwillAssertionError("broken links on page")


def report_bad_links(fail_if_exist='+', flush_bad_links='+'):
    """
    >> report_bad_links [<fail-if-exist> [<flush-bad-links>]]

    Report all of the links collected across check_links runs (collected
    if and only if the config option check_links.only_collect_bad_links
    is set).

    If <fail-if-exist> is false (true by default) then the command will
    fail after reporting any bad links.

    If <flush-bad-links> is false (true by default) then the list of
    bad links will be retained across the function call.
    """
    global bad_links_dict
    
    from twill import utils
    fail_if_exist = utils.make_boolean(fail_if_exist)
    flush_bad_links = utils.make_boolean(flush_bad_links)

    info = log.info
    if not bad_links_dict:
        info('\nNo bad links to report.\n')
    else:
        info('\nCould not follow %d links', len(bad_links_dict))
        for page, referers in bad_links_dict.items():
            info("\tlink '%s' (occurs on: %s)", page, ','.join(referers))

        if flush_bad_links:
            bad_links_dict = {}

        if fail_if_exist:
            raise TwillAssertionError("broken links encountered")
