"""Simple mock implementation of dnspython to test the twill DNS extension."""

import enum
import sys
from typing import Any, Dict, List, Optional


class RdataType(enum.IntEnum):
    """DNS Rdata Type."""

    A = 1
    NS = 2
    CNAME = 5
    MX = 15


mock_records: Dict[RdataType, Dict[str, str]] = {
    RdataType.A: {
        "twill-test-1.ignore.idyll.org": "192.168.1.1",
        "twill-test-2.ignore.idyll.org": "192.168.1.2",
        "twill-test-3.ignore.idyll.org": "192.168.1.1",
    },
    RdataType.CNAME: {
        "twill-test-3.ignore.idyll.org": "twill-test-1.ignore.idyll.org.",
    },
    RdataType.MX: {
        "twill-test-4.ignore.idyll.org": "twill-test-2.ignore.idyll.org.",
    },
    RdataType.NS: {
        "idyll.org": "nsa.idyll.org.",
    },
}


def activate() -> None:
    """Activate the mock dns module."""
    package = sys.modules[__name__]
    sys.modules["dns"] = package
    for module in "ipv4 name rdatatype resolver".split():
        sys.modules[f"dns.{module}"] = package
        setattr(package, module, package)


def inet_aton(text: str) -> str:
    """Convert IPv4 address in text form to network form."""
    try:
        net = "".join(chr(int(x)) for x in text.split("."))
        if len(net) != 4:  # noqa: PLR2004
            raise ValueError
    except (TypeError, ValueError) as error:
        raise OSError(f"invalid ip address {text}") from error
    return net


def from_text(text: str) -> str:
    """Convert text into a Name object."""
    if not text.endswith("."):
        text += "."
    return text


class Result:
    """DNS query result."""

    def __init__(self, qtype: RdataType, value: Any) -> None:
        """Initialize the result."""
        self.value = value
        if qtype == RdataType.A:
            self.address = value
        elif qtype in (RdataType.CNAME, RdataType.NS):
            self.target = value
        elif qtype == RdataType.MX:
            self.exchange = value
        else:
            raise ValueError(f"unknown query type: {qtype}")

    def __str__(self) -> str:
        """Get a string representation of the result."""
        return str(self.value)


Answer = List[Result]


class Resolver:
    """DNS stub resolver."""

    def __init__(self) -> None:
        """Initialize the resolver."""
        self.nameservers: Optional[List] = None

    def resolve(self, qname: str, qtype: RdataType = RdataType.A) -> Answer:
        """Query nameservers to find the answer to the question."""
        if self.nameservers:
            raise ValueError(f"unknown name servers: {self.nameservers}")
        try:
            records = mock_records[qtype]
        except KeyError as error:
            raise ValueError(f"unknown query type: {qtype}") from error
        if qname.endswith("."):
            qname = qname[:-1]
        try:
            results = records[qname]
        except KeyError as error:
            raise ValueError(
                f"unknown query result: {qname} {qtype}"
            ) from error
        if not isinstance(results, list):
            results = [results]  # type: ignore[assignment]
        return [Result(qtype, result) for result in results]
