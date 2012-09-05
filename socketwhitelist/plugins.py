__license__ = """
Copyright 2012 DISQUS

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import socket
import sys
import traceback

from collections import defaultdict
from nose.plugins.base import Plugin


LOCALHOST_IPV4 = ('127.0.0.1',)
LOCALHOST_IPV6 = ('::1',)


# This class extends BaseException to decrease the likelihood that is able to
# be suppressed by application code. If you're ever blindly supressing
# BaseException, you're doing it even more wrong than supressing Exception.
class SocketError(BaseException):
    pass


class Counter(defaultdict):
    def __init__(self):
        super(Counter, self).__init__(lambda: 0)

    def increment(self, key, step=1):
        """
        Increments the value at ``key``.
        """
        self[key] += step
        return self[key]

    def rollup(self, values):
        """
        Takes a sequence of ``values``, and rolls them up into the counter, for
        example: ('a', 'a', 'a', 'b') -> {'a': 3, 'b': 1}
        """
        for value in values:
            self.increment(value)
        return self


class SocketWhitelistPlugin(Plugin):
    enabled = True
    score = sys.maxint  # execute as soon as possible
    socket_address_whitelist = LOCALHOST_IPV4 + LOCALHOST_IPV6

    # If `configure` and `options` are not set on the class, nose assumes this
    # isn't a plugin and ignores without warning or a runtime error.
    configure = options = lambda self, *a, **k: None

    def begin(self):
        self.test = None

        self._getaddrinfo = socket.getaddrinfo

        def getwhitelistedaddrinfo(host, port, *args, **kwargs):
            """
            Wraps ``socket.getaddrinfo``, adding a filter for connections that
            are opened to non-whitelisted sockets.
            """
            results = self._getaddrinfo(host, port, *args, **kwargs)
            if not any((self.is_whitelisted(addrinfo) for addrinfo in results)):
                self.handle_nonwhitelisted_socket_connection(host, port)
            return results

        socket.getaddrinfo = getwhitelistedaddrinfo

    def beforeTest(self, test):
        # This has to be here so that we can get the test name in
        # our patched `getwhitelistedaddrinfo`.
        self.test = test

    def finalize(self, result):
        # Replace ``getaddrinfo`` with the original.
        socket.getaddrinfo = self._getaddrinfo

    def is_whitelisted(self, addrinfo):
        """
        Returns if a result of ``socket.getaddrinfo`` is in the socket address whitelist.
        """
        # For details about the ``getaddrinfo`` struct, see the Python docs:
        # http://docs.python.org/library/socket.html#socket.getaddrinfo
        family, socktype, proto, canonname, sockaddr = addrinfo
        address, port = sockaddr[:2]
        return address in self.socket_address_whitelist

    def handle_nonwhitelisted_socket_connection(self, host, port):
        raise NotImplementedError  # Should be implemented by subclasses.


class LoggingSocketWhitelistPlugin(SocketWhitelistPlugin):
    """
    Patches ``socket.getaddrinfo`` to log when a socket is attempted to be
    opened to a destination that is not on the socket address whitelist.
    """
    stream = sys.stderr

    def begin(self):
        self.socket_warnings = defaultdict(list)
        super(LoggingSocketWhitelistPlugin, self).begin()

    def options(self, parser, env):
        parser.add_option('--socket-trace', type=int, default=False,
            metavar='NUM_FRAMES', help='number of stack frames to print to '
                'stderr when an invalid socket connection is encountered')

    def configure(self, options, conf):
        self.trace = options.socket_trace

    def handle_nonwhitelisted_socket_connection(self, host, port):
        address = '%s:%s' % (host, port)
        self.socket_warnings[str(self.test)].append(address)
        if self.trace:
            print >> self.stream, '\n', 'NON-WHITELISTED SOCKET OPENED: %s' % address
            print >> self.stream, 'in test: %s' % str(self.test)
            print >> self.stream, ''.join(traceback.format_list(traceback.extract_stack(limit=self.trace)))

    def report(self):
        """
        Performs rollups, prints report of sockets opened.
        """
        aggregations = dict((test, Counter().rollup(values))
            for test, values in self.socket_warnings.iteritems())
        total = sum((len(warnings) for warnings
            in self.socket_warnings.itervalues()))

        def format_test_statistics(test, counter):
            return "%s:\n%s" % (test, '\n'.join('  - %s: %s' % (socket, count) for socket, count in counter.iteritems()))

        def format_statistics(aggregations):
            return '\n'.join(format_test_statistics(test, counter)
                for test, counter in aggregations.iteritems())

        # Only print the report if there are actually things to report.
        if aggregations:
            print >> self.stream, '=' * 70
            print >> self.stream, 'NON-WHITELISTED SOCKETS OPENED: %s' % total
            print >> self.stream, '-' * 70
            print >> self.stream, format_statistics(aggregations)


class ErroringSocketWhitelistPlugin(SocketWhitelistPlugin):
    """
    Patches ``socket.getaddrinfo`` and fails any test that attempts to open a
    socket to a destination that is not on the socket address whitelist.
    """
    def handle_nonwhitelisted_socket_connection(self, host, port):
        raise SocketError('Invalid attempt to access non-whitelisted socket: %s:%s' % (host, port))
