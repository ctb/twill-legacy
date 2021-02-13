"""Simple mock implementation of dnspython to test the twill dns extension"""

import socket
import sys


mock_records = {
    'A': {
        'twill-test-1.ignore.idyll.org': '192.168.1.1',
        'twill-test-2.ignore.idyll.org': '192.168.1.2',
        'twill-test-3.ignore.idyll.org': '192.168.1.1',
    },
    'CNAME': {
        'twill-test-3.ignore.idyll.org': 'twill-test-1.ignore.idyll.org.',
    },
    'MX': {
        'twill-test-4.ignore.idyll.org': 'twill-test-2.ignore.idyll.org.',
    },
    'NS': {
        'idyll.org': 'nsa.idyll.org.',
    }
}


def activate():
    """Activate the mock dns module"""
    package = sys.modules[__name__]
    sys.modules['dns'] = package
    for module in 'ipv4 name resolver'.split():
        sys.modules[f'dns.{module}'] = package
        setattr(package, module, package)


def inet_aton(text):
    """Convert IPv4 address in text form to network form."""
    try:
        net = ''.join(chr(int(x)) for x in text.split('.'))
        if len(net) != 4:
            raise ValueError
        return net
    except (TypeError, ValueError):
        raise socket.error('invalid ip address %s' % text)


def from_text(text):
    """Convert text into a Name object"""
    if not text.endswith('.'):
        text += '.'
    return text


class Answer:
    """"DNS query result"""

    def __init__(self, qtype, result):
        self.result = result
        if qtype == 'A':
            self.address = result
        elif qtype in ('CNAME', 'NS'):
            self.target = result
        elif qtype == 'MX':
            self.exchange = result
        else:
            raise ValueError(f'unknown query type: {qtype}')

    def __str__(self):
        return str(self.result)


class Resolver:
    """DNS stub resolver"""

    def __init__(self):
        self.nameservers = None

    def query(self, qname, qtype='A'):
        if self.nameservers:
            raise ValueError(f'unknown name servers: {self.nameservers}')
        if qtype == 1:
            qtype = 'A'
        try:
            records = mock_records[qtype]
        except KeyError:
            raise ValueError(f'unknown query type: {qtype}')
        if qname.endswith('.'):
            qname = qname[:-1]
        try:
            results = records[qname]
        except KeyError:
            raise ValueError(f'unknown query result: {qname} {qtype}')
        if not isinstance(results, list):
            results = [results]
        return [Answer(qtype, result) for result in results]
