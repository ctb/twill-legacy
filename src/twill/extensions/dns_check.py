"""Extension functions to help query/assert name service information.

Functions:

  * dns_resolves -- assert that a host resolves to a specific IP address.
  * dns_a -- assert that a host directly resolves to a specific IP address
  * dns_cname -- assert that a host is an alias for another hostname.
  * dnx_mx -- assert that a given host is a mail exchanger for the given name.
  * dns_ns -- assert that a given hostname is a name server for the given name.
"""

from typing import Optional

from twill.errors import TwillAssertionError

try:
    from dns.ipv4 import inet_aton
    from dns.name import from_text
    from dns.rdatatype import RdataType
    from dns.resolver import Answer, Resolver
except ImportError as error:
    msg = str(error)
    msg += "\nMust have dnspython installed to use the DNS extension module."
    raise ImportError(msg) from error


def dns_a(host: str, ipaddress: str, server: Optional[str] = None) -> None:
    """>> dns_a <name> <ipaddress> [<name server>]

    Assert that <name> resolves to <ipaddress> (and is an A record).
    Optionally use the given name server.
    """
    if not is_ip_addr(ipaddress):
        raise ValueError(
            "<ipaddress> parameter must be an IP address, not a hostname"
        )

    for answer in _resolve(host, RdataType.A, server):
        if answer.address == ipaddress:
            return

    raise TwillAssertionError


def dns_cname(host: str, cname: str, server: Optional[str] = None) -> None:
    """>> dns_cname <name> <alias_for> [<name server>]

    Assert that <name> is a CNAME alias for <alias_for>.
    Optionally use the given <name server>.
    """
    if is_ip_addr(cname):
        raise ValueError(
            "<alias_for> parameter must be a hostname, not an IP address"
        )

    cname_name = from_text(cname)

    for answer in _resolve(host, RdataType.CNAME, server):
        if answer.target == cname_name:
            return

    raise TwillAssertionError


def dns_resolves(
    host: str, ipaddress: str, server: Optional[str] = None
) -> None:
    """>> dns_resolves <name> <name2/ipaddress> [<name server>]

    Assert that <name> ultimately resolves to the given IP address (or
    the same IP address that 'name2' resolves to).
    Optionally use the given name server.
    """
    if not is_ip_addr(ipaddress):
        ipaddress = _resolve_name(ipaddress, server)

    for answer in _resolve(host, RdataType.A, server):
        if answer.address == ipaddress:
            return

    raise TwillAssertionError


def dns_mx(host: str, mailserver: str, server: Optional[str] = None) -> None:
    """>> dns_mx <name> <mailserver> [<name server>]

    Assert that <mailserver> is a mailserver for <name>.
    """
    mailserver_name = from_text(mailserver)

    for rdata in _resolve(host, RdataType.MX, server):
        if rdata.exchange == mailserver_name:
            return

    raise TwillAssertionError


def dns_ns(host: str, query_ns: str, server: Optional[str] = None) -> None:
    """>> dns_ns <domain> <nameserver> [<name server to use>]

    Assert that <nameserver> is a mailserver for <domain>.
    """
    query_ns_name = from_text(query_ns)

    for answer in _resolve(host, RdataType.NS, server):
        if answer.target == query_ns_name:
            return

    raise TwillAssertionError


def is_ip_addr(text: str) -> bool:
    """Check the 'name' to see if it's just an IP address."""
    try:
        inet_aton(text)
    except OSError:
        return False
    return True


def _resolve_name(name: str, server: Optional[str] = None) -> str:
    """Resolve the given name to an IP address."""
    if is_ip_addr(name):
        return name

    resolver = Resolver()
    if server:
        resolver.nameservers = [_resolve_name(server, None)]

    answers = resolver.resolve(name)

    return str(answers[0])


def _resolve(
    query: str, query_type: RdataType, server: Optional[str] = None
) -> Answer:
    """Resolve, perhaps via the given name server."""
    resolver = Resolver()
    if server:
        resolver.nameservers = [_resolve_name(server, None)]

    return resolver.resolve(query, query_type)
