import socket
import unittest
from urllib import urlopen

from socketwhitelist.plugins import (LOCALHOST_IPV4, LOCALHOST_IPV6, SocketError,
    ErroringSocketWhitelistPlugin, LoggingSocketWhitelistPlugin)


class ErroringSocketWhitelistPluginTestCase(unittest.TestCase):
    def setUp(self):
        self.plugin = ErroringSocketWhitelistPlugin()
        self.plugin.begin()

    def tearDown(self):
        self.plugin.finalize(None)

    def test_allows_locally(self):
        for address in LOCALHOST_IPV4 + LOCALHOST_IPV6:
            socket.getaddrinfo(address, '80')

    def test_errors_on_remote(self):
        self.assertRaises(SocketError, lambda: urlopen('http://www.disqus.com'))


class Options(object):
    socket_trace = True


class LoggingSocketWhitelistPluginTestCase(unittest.TestCase):

    def setUp(self):
        self.plugin = LoggingSocketWhitelistPlugin()
        self.plugin.configure(Options(), None)
        self.plugin.begin()

    def tearDown(self):
        self.plugin.finalize(None)

    def test_allows_locally(self):
        for address in LOCALHOST_IPV4 + LOCALHOST_IPV6:
            socket.getaddrinfo(address, '80')

    def test_report(self):
        urlopen('http://www.disqus.com')
        self.plugin.report()
