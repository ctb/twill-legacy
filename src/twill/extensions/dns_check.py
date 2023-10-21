"""
Extension functions to help query/assert name service information.

Functions:

  * dns_resolves -- assert that a host resolves to a specific IP address.
  * dns_a -- assert that a host directly resolves to a specific IP address
  * dns_cname -- assert that a host is an alias for another hostname.
  * dnx_mx -- assert that a given host is a mail exchanger for the given name.
  * dns_ns -- assert that a given hostname is a name server for the given name.
"""

import socket
from twill.errors import TwillAssertionError

try:
    from dns.ipv4 import inet_aton
    from dns.name import from_text
    from dns.resolver import Resolver
except ImportError:
    raise Exception(
        "ERROR: must have dnspython installed to use the DNS extension module")


def dns_a(host, ipaddress, server=None):
    """>> dns_a <name> <ipaddress> [<name server>]

    Assert that <name> resolves to <ipaddress> (and is an A record).
    Optionally use the given name server.
    """
    if not is_ip_addr(ipaddress):
        raise Exception(
            "<ipaddress> parameter must be an IP address, not a hostname")

    for answer in _resolve(host, 'A', server):
        if ipaddress == answer.address:
            return True

    raise TwillAssertionError


def dns_cname(host, cname, server=None):
    """>> dns_cname <name> <alias_for> [<name server>]

    Assert that <name> is a CNAME alias for <alias_for>  Optionally use
    <name server>.
    """
    if is_ip_addr(cname):
        raise Exception(
            "<alias_for> parameter must be a hostname, not an IP address")

    cname = from_text(cname)

    for answer in _resolve(host, 'CNAME', server):
        if cname == answer.target:
            return True

    raise TwillAssertionError


def dns_resolves(host, ipaddress, server=None):
    """>> dns_resolves <name> <name2/ipaddress> [<name server>]

    Assert that <name> ultimately resolves to the given IP address (or
    the same IP address that 'name2' resolves to).  Optionally use the
    given name server.
    """
    if not is_ip_addr(ipaddress):
        ipaddress = _resolve_name(ipaddress, server)

    for answer in _resolve(host, 1, server):
        if ipaddress == answer.address:
            return True

    raise TwillAssertionError


def dns_mx(host, mailserver, server=None):
    """>> dns_mx <name> <mailserver> [<name server>]

    Assert that <mailserver> is a mailserver for <name>.
    """
    mailserver = from_text(mailserver)

    for rdata in _resolve(host, 'MX', server):
        if mailserver == rdata.exchange:
            return True

    raise TwillAssertionError


def dns_ns(host, query_ns, server=None):
    """>> dns_ns <domain> <nameserver> [<name server to use>]

    Assert that <nameserver> is a mailserver for <domain>.
    """
    query_ns = from_text(query_ns)

    for answer in _resolve(host, 'NS', server):
        if query_ns == answer.target:
            return True

    raise TwillAssertionError


def is_ip_addr(text):
    """Check the 'name' to see if it's just an IP address."""
    try:
        inet_aton(text)
        return True
    except socket.error:
        return False


def _resolve_name(name, server):
    """Resolve the given name to an IP address."""
    if is_ip_addr(name):
        return name

    resolver = Resolver()
    if server:
        resolver.nameservers = [_resolve_name(server, None)]

    answers = resolver.resolve(name)

    return str(answers[0])


def _resolve(query, query_type, server):
    """Resolve, perhaps via the given name server (None to use default)."""
    resolver = Resolver()
    if server:
        resolver.nameservers = [_resolve_name(server, None)]

    return resolver.resolve(query, query_type)
